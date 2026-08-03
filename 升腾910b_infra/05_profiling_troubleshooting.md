# 05 · 性能剖析与故障排查

> infra 的吃饭本事：定位瓶颈、处理生产故障。工具对标 Nsight / DCGM。
> 核心工具：**msprof**（升腾性能剖析器）。

## 1. msprof：升腾版 Nsight

`msprof` 采集训练/推理过程中的算子耗时、AI Core 占用、HCCS 带宽、流水气泡等。

```bash
# 基本剖析（包住你的训练命令）
msprof --application="python train.py" \
       --output=./prof_result

# 只看算子耗时（对标 kernel profile）
msprof --application="python train.py" --sys-performance=on

# 看 HCCS / 通信
msprof --application="python train.py" --hccs-profiler=on
```

产出（在 `prof_result/`）：
- `mindstudio_profiler_*.csv`：每个算子的起止时间、耗时、在哪个 AI Core
- 时间轴视图（用 MindStudio 打开）：看 Cube/Vector 占用、流水是否打满

**关键指标**：
| 指标 | 含义 | 健康线（参考） |
|---|---|---|
| AI Core 利用率 | Cube/Vector 忙的比例 | 越高越好，>70% 算健康 |
| 流水气泡 (bubble) | 单元空等比例 | 越低越好 |
| HCCS 带宽利用率 | 卡间通信打满程度 | 通信密集时该高 |
| 算子耗时 TopN | 最慢的算子 | 重点优化对象 |

## 2. 四类典型瓶颈与对策

### 2.1 计算未打满（AI Core 利用率低）

- 原因：算子太小/太多、融合不足、数据没喂上
- 对策：看 GE 融合是否开启；算子融合（`fusion_switch_file`）；增大 batch

### 2.2 访存瓶颈（memory-bound）

- 现象：Cube 用不满，频繁 Global Memory 搬运（连回 [01](01_hardware_architecture.md) UB 概念）
- 对策：算子 tiling 对齐 UB/L1；减少 elementwise 算子的往返；用融合

### 2.3 通信瓶颈（HCCS / RoCE）

- 现象：训练时 AI Core 在等通信（流水气泡大）
- 对策：计算/通信 overlap；TP 放单机 HCCS 内；调 HCCS 拓扑；减少跨机通信

### 2.4 算子 fallback

- 现象：某算子跑到 CPU（连回 [02](02_CANN_operators.md)）
- 对策：消灭 fallback（替换算子 / 自定义 TBE 算子）

## 3. 一个剖析实战流程

```bash
# 1. 采集
msprof --application="python train.py" --output=./prof

# 2. 看 AI Core 利用率
grep -i "aicore" ./prof/**/*.csv

# 3. 找最慢算子 Top10
# 在 MindStudio 时间轴里或导出的 csv 排序

# 4. 判断类型：
#    - 若是 GEMM 类 → 计算优化 / 增大 M,N,K
#    - 若是 LayerNorm/Softmax → 访存优化 / 融合
#    - 若整体慢但单算子快 → 通信/调度问题
```

## 4. 硬件健康与故障排查

### 4.1 npu-smi 健康检查

```bash
npu-smi info                 # 设备列表、利用率、显存、温度
npu-smi info -t usages -d 1  # 实时监控
npu-smi info -t ecc          # ECC 错误（硬件健康关键！）
npu-smi info -t power        # 功耗/降频
```

### 4.2 常见故障对照

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 设备不在位 (`npu-smi` 看不到) | 驱动/固件异常、PCIe 掉链 | 重装驱动、查 `dmesg`、查物理 |
| ECC 错误增长 | 显存硬件问题 | 隔离该卡，报修 |
| 训练中途掉卡 | 过热降频 / HCCS 异常 | 看 `-t power`、查拓扑、降温 |
| 利用率周期性掉底 | 数据加载瓶颈 | 优化 DataLoader、加大 prefetch |
| 通信 hang | HCCL/RoCE 不通 | 查网卡、MASTER 连通、防火墙 |
| 结果 NaN | 精度溢出 | BF16 替代 FP16、检查 loss scale |

### 4.3 日志去哪看

- 驱动/固件：`/var/log/npu/` 或 `dmesg | grep npu`
- CANN：ATC / GE 日志（按文档开 debug 级别）
- 训练：torch_npu 的告警（如 fallback 提示）

## 5. 一个排错决策树

```
训练慢 / 报错
   │
   ├─ 设备不可见？ ──> 驱动/固件/PCIe (npu-smi, dmesg)
   │
   ├─ 周期性掉底？ ──> 数据加载 (DataLoader/prefetch)
   │
   ├─ 利用率低？ ──> msprof 看是 计算/访存/通信 哪类瓶颈
   │       │
   │       ├─ 计算未打满 ──> 融合、增大 batch
   │       ├─ 访存瓶颈 ──> tiling/UB 对齐、融合
   │       └─ 通信瓶颈 ──> overlap、TP 单机内
   │
   ├─ 数值异常？ ──> 精度 (BF16/loss scale)、ECC
   │
   └─ 多卡 hang？ ──> HCCL/RoCE 连通、MASTER 配置
```

## 6. 本章验收

- [ ] 用 msprof 采集一次训练，能读取 AI Core 利用率和最慢算子
- [ ] 能区分 计算/访存/通信 三类瓶颈并给对策
- [ ] 能用 `npu-smi -t ecc` 做硬件健康巡检
- [ ] 面对"训练慢/掉卡/NaN"能用决策树初步定位

## 参考

- 官方：msprof 用户指南、MindStudio 性能分析文档（见 [references.md](references.md)）
- 类比学习：NVIDIA Nsight Systems / DCGM 的思路可直接迁移
