# 01 · 升腾 910B 硬件与计算架构

> 这一章是后面所有调优的地基。看不懂 Da Vinci 和 HCCS，后面 msprof 的瓶颈分析就无从谈起。
> 对标对象：NVIDIA A100/H100 的 GPU + NVLink。

## 1. 一张全局图

```
┌──────────────── 单机 (如 Atlas 800T A2) ────────────────┐
│                                                         │
│   CPU (鲲鹏/ x86) ── PCIe ──┐                           │
│                            [Switch]── HCCS ──┐          │
│   NPU0 ──HCCS── NPU1 ──HCCS── NPU2 ... NPU7  │          │
│     │            │            │               │          │
│  [Da Vinci]  [Da Vinci]   [Da Vinci] ...  [Da Vinci]    │
│                                                         │
└─────────────────────────────────────────────────────────┘
         HCCS = 芯片间高速互联（对标 NVLink）
```

- 整机常见 **8 卡 910B**（部分机型 4 卡）。
- 卡间靠 **HCCS** 互联，CPU 与卡之间靠 PCIe（部分机型用自研总线）。
- 多机之间靠 **RoCE / 网卡**（对标 InfiniBand）。

## 2. Ascend 910B 关键规格（与 A100 对标）

| 指标 | Ascend 910B | NVIDIA A100 (80G) | 说明 |
|---|---|---|---|
| 制程 | 7nm 级 | 7nm (TSMC) | — |
| FP16 算力 | ~256–320 TFLOPS | 312 TFLOPS | 训练主力精度 |
| BF16 | 支持 | 支持 | 大模型训练常用 |
| INT8 | ~400–600 TOPS | 624 TOPS | 推理量化 |
| HBM 容量 | ~64 GB | 80 GB | 影响能塞多大模型 |
| HBM 带宽 | ~392 GB/s | 2039 GB/s? 实际 ~2TB/s | NPU 带宽相对低，注意访存瓶颈 |
| 互联 | HCCS | NVLink | 卡间通信 |
| TDP | ~310 W | 400 W | 功耗 |

> 注：不同批次（910B1/B2/B3、910C）规格有差异，以上为公开常见区间，实际以 `npu-smi info` 和官方文档为准。

**infra 要点**：910B 的算力接近 A100，但**单卡 HBM 带宽相对低**——这意味着**访存密集（memory-bound）算子**（如 LayerNorm、attention 的某些 stage）更容易成为瓶颈，调优时要优先看算子是否打满 Cube 还是卡在 Global Memory 搬运。

## 3. Da Vinci 计算架构（核心）

每个 910B 内含多个 **AI Core**，每个 AI Core 由三类执行单元组成：

```
┌─────────── AI Core ───────────┐
│  ┌────────┐ ┌────────┐ ┌─────┐ │
│  │ Cube   │ │ Vector │ │Scal.│ │  三类单元并行
│  │(矩阵乘)│ │(逐元素)│ │(控制)│ │
│  └───┬────┘ └───┬────┘ └──┬──┘ │
│      └─────┬─────┴───────┘     │
│        [ Unified Buffer (UB) ] │  ← 片上高速缓存（对标 shared memory）
│        [ L0/L1 Buffer ]        │
└───────────────────────────────┘
              │
        Global Memory (HBM)
```

| 单元 | 对标 GPU | 干什么 | 典型算子 |
|---|---|---|---|
| **Cube** | Tensor Core | 矩阵乘/卷积（计算密集） | GEMM、conv、attention 的 QK^T·V |
| **Vector** | CUDA Core (FP 部分) | 逐元素/激活/归一化（访存密集） | LayerNorm、Softmax、GeLU、elementwise |
| **Scalar** | CUDA Core (控制) | 地址计算、循环控制 | 调度逻辑 |

**关键洞察**：
- Cube 负责"重计算"，Vector 负责"轻计算+搬运"。一个算子往往要 Cube 和 Vector 配合。
- **UB（Unified Buffer）** 是片上共享缓存，TBE 算子开发时要把数据排布对齐到 UB，否则频繁 Global Memory 往返 → 性能骤降。这是升腾算子调优的第一课。

## 4. 内存层级（对标 GPU 内存层次）

```
Global Memory (HBM, ~几十 GB, 带宽 ~400GB/s)
        ▲ 搬运慢
        │
L1 Buffer (较大, 片上)
        ▲
L0 Buffer (小, 极快)
        ▲
UB (Unified Buffer, 算子内共享, 类比 shared memory)
```

调优原则（和 GPU 一致）：**让热点数据尽量留在 UB/L1，减少 Global Memory 往返**；算子分块（tiling）要匹配 UB 大小。

## 5. HCCS 互联与集群拓扑

- **HCCS（Huawei Cache Coherence System）**：芯片间高速直连，单机 8 卡通常全互连或环/树拓扑。
- 看拓扑：`npu-smi` 能看到链路，`npu-smi info -t topology` 类似 NVLink topology 查询。
- 多机：靠 RoCE 网卡 + HCCL 的通信组，对标 NCCL + InfiniBand。

```bash
# 看设备与链路
npu-smi info
npu-smi info -t usages -d 1     # 实时利用率
npu-smi info -t ecc             # 看 ECC 错误（硬件健康）
```

**infra 要点**：分布式训练时，**通信拓扑决定 HCCL 效率**。尽量让通信密集的并行（如张量并行）落在同一台机器的 HCCS 域内，跨机只放数据并行/流水并行，避免 HCCS 与 RoCE 混用导致带宽塌方。

## 6. 精度与混合精度

| 精度 | 算力 | 何时用 |
|---|---|---|
| FP32 | 低 | 数值敏感（如 loss 累加、某些 norm 的 master weight） |
| FP16 | 高 | 训练主力，但需要 loss scale 防溢出 |
| BF16 | 高 | 大模型训练首选（动态范围大，不易溢出） |
| INT8 | 最高 | 推理量化，需校准 |

torch_npu 的混合精度写法与 CUDA 几乎一致（见 [03](03_torch_npu_distributed.md)）。

## 7. 本章验收

- [ ] 能画"单卡 910B 计算/存储/互联"简图
- [ ] 说清 Cube / Vector / Scalar 各算什么，UB 是什么
- [ ] 说清 HCCS 对标 NVLink，以及为何跨机通信要分层
- [ ] 用 `npu-smi` 解释一台 8 卡机器的健康与利用率字段

## 参考

- 官方：昇腾 910B 产品文档、Da Vinci 架构白皮书（见 [references.md](references.md)）
- 博客：搜索结果中《910B 服务器深度解析》《达芬奇架构与国产化适配》适合打底
