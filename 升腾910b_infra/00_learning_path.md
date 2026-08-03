# 00 · 升腾 910B Infra 学习路径

> 一条 6~8 周、面向 infra 的路线。每个阶段都给出"学完能做什么"的验收标准。

## 阶段 0：环境即 infra（约 1 周）

**目标**：独立把一台 910B 点亮，会看设备状态。

1. 装驱动 + 固件 + CANN（注意**版本配套**，OS/内核版本要匹配）
2. 跑通 `npu-smi info`（升腾版 `nvidia-smi`）
3. 装 torch_npu，验证 `torch.randn(3,3).npu()` 能放到设备上

```bash
# 看设备与健康状态
npu-smi info
npu-smi info -l   # 看逻辑卡
# 监控（类似 watch nvidia-smi）
npu-smi info -t usages -d 1
```

**验收**：能独立装机、解释 `npu-smi` 里利用率/显存/HCCS 链路字段、处理最常见的驱动不匹配报错。

## 阶段 1：硬件与计算架构（1~2 周）→ [01](01_hardware_architecture.md)

**目标**：懂 910B 的算力/内存/互联，知道算子为什么这么设计。

- Da Vinci 架构：Cube（矩阵）/Vector（逐元素）/Scalar（控制）三类单元
- 内存层级：L0/L1、UB（Unified Buffer）、Global Memory
- HCCS 芯片间互联，对比 NVLink；整机的 8 卡 910B 服务器拓扑
- 精度：FP16/BF16/INT8 算力与适用场景

**验收**：能画一张"单卡 910B 计算/存储/互联"简图，说清 Cube 和 Vector 各算什么、HCCS 带宽大概量级。

## 阶段 2：CANN 与算子（2 周，infra 核心）→ [02](02_CANN_operators.md)

**目标**：理解图编译与算子执行链路，能做基础算子迁移。

- CANN 组成：GE（Graph Engine）图编译、算子库、Runtime、ATC
- AscendCL：C/Python 调用接口（对标 CUDA Runtime API）
- 自定义算子：TBE DSL / TIK（对标 Triton/CUDA C++）
- 性能：算子融合、流水、memory 对齐

**验收**：能写一段 AscendCL 的最小推理流程；能解释一个 PyTorch 模型怎么被 GE 切成 NPU 算子；知道算子缺失时怎么补。

## 阶段 3：框架对接 + 分布式（2 周，最实用）→ [03](03_torch_npu_distributed.md)

**目标**：把 GPU 训练脚本迁到 NPU，并跑通多卡分布式。

- torch_npu：`.to('npu')`、amp 混合精度、常见 API 差异
- **HCCL**：对标 NCCL 的集合通信（AllReduce/Broadcast/ReduceScatter）
- 分布式并行：数据/流水线/张量并行在 Ascend 上的落地
- 多机：HCCS + 网卡拓扑、rank/device 映射

**验收**：把一份 GPU 训练脚本改到 NPU 跑通；在 2~8 卡上用 HCCL 跑通 DDP/FSDP 类训练；说明 HCCL 和 NCCL 的差异。

## 阶段 4：推理部署与集群（1~2 周）→ [04](04_inference_deployment.md)

**目标**：把训练好的模型部署成线上推理服务。

- **ATC** 把模型转 OM 格式（对标 ONNX→TensorRT）
- **MindIE** 推理引擎（对标 vLLM/TensorRT-LLM）
- 实战：910B 上部署 DeepSeek 类大模型
- MindCluster / ModelArts 集群任务调度、故障自愈

**验收**：用 ATC 转一个模型、用 MindIE 起一个推理服务；能复述大模型在 910B 上的部署链路。

## 阶段 5：调优与排错（贯穿，约 2 周）→ [05](05_profiling_troubleshooting.md)

**目标**：定位性能瓶颈、处理生产故障。

- **msprof** 性能剖析（对标 Nsight）：算子耗时、流水气泡、HCCS 带宽利用率
- 精度问题：NPU 上 FP16/BF16 行为差异
- 故障：掉卡、HCCS 异常、`npu-smi` 报错码对照

**验收**：对一个慢训练任务用 msprof 找到瓶颈并给出优化方向；能根据报错码初步定位硬件/软件问题。

## 一张速查图

```
[PyTorch/torch_npu] ──图/算子──> [CANN: GE 图编译]
                                      │
                          ┌───────────┼────────────┐
                       [AscendCL]  [算子库/TBE]  [Runtime]
                                      │
                              ┌───────┴───────┐
                         [Da Vinci 910B]   [HCCS 互联]
                                      │
                            [msprof 剖析 / MindIE 部署]
```

## 下一步

从 [01_硬件架构](01_hardware_architecture.md) 开始。建议每章读完动手敲一遍命令，再回到这里对照验收标准。
