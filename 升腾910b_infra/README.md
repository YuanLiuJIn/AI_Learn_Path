# 升腾 910B Infra 学习体系

> 面向 **infra / 平台 / 运维 / 性能调优** 视角，而非单纯"跑通一个模型"。
> 目标：能在升腾 910B 上**点亮环境、迁移训练、搭分布式、部署推理、定位瓶颈**。

## 这个文件夹在讲什么

升腾（Ascend）生态和 NVIDIA/CUDA 生态是**对位**关系。学的时候始终把"CUDA 里我熟悉的那个东西"映射到"升腾里对应的那一层"，会快很多。

| 层级 | CUDA 栈 | 升腾栈 | 本文件夹对应章节 |
|---|---|---|---|
| 芯片/硬件 | GPU (Ampere/Hopper) | Ascend 910B/910C/310 | [01_硬件架构](01_hardware_architecture.md) |
| 计算架构 | Tensor Core / SM | Da Vinci（Cube/Vector/Scalar） | [01_硬件架构](01_hardware_architecture.md) |
| 驱动/运行时 | Driver + CUDA Runtime | 驱动+固件 + Runtime | [02_CANN](02_CANN_operators.md) |
| 算子/编译 | cuDNN/cuBLAS/Triton | CANN（GE+算子库+ATC） | [02_CANN](02_CANN_operators.md) |
| 集合通信 | NCCL | **HCCL** | [03_分布式](03_torch_npu_distributed.md) |
| 框架对接 | PyTorch (CUDA) | **torch_npu** / MindSpore | [03_分布式](03_torch_npu_distributed.md) |
| 推理引擎 | TensorRT / vLLM | **MindIE** / ATC转OM | [04_推理部署](04_inference_deployment.md) |
| 集群调度 | Slurm / K8s | MindCluster / ModelArts | [04_推理部署](04_inference_deployment.md) |
| 性能剖析 | Nsight | **msprof** | [05_调优排错](05_profiling_troubleshooting.md) |

## 推荐学习顺序

```
00 学习路径（先读这个，建立全局）
   │
   ├─ 01 硬件架构      ← 懂算力/内存/互联，后面的调优才有抓手
   ├─ 02 CANN 与算子   ← infra 核心：图编译、算子、ATC
   ├─ 03 torch_npu+分布式 ← 最实用：把 GPU 代码跑在 NPU 上 + HCCL
   ├─ 04 推理部署      ← MindIE / ATC / 大模型部署实战
   └─ 05 调优与排错    ← msprof + 故障码，infra 吃饭本事
```

建议周期 **6~8 周**，每章标注了大致投入。不要跳着读——01 的 Da Vinci 和 HCCS 概念是后面所有调优的地基。

## 前置要求

- 一台可见的 910B 环境（物理机 / 云上 ModelArts / 远程集群均可）
- Linux 基础（你已具备 AI 训练框架基础）
- 有 PyTorch + CUDA 经验最好（用类比学最快），没有也能从 01 起步

## 文档约定

- 命令块均可在 910B 环境直接执行
- 代码以 PyTorch + torch_npu 为主（MindSpore 仅在分布式章节补充）
- 文档出处写在 [references.md](references.md)，论文/博客均给可回溯链接
