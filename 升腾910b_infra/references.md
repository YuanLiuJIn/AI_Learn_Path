# 参考资源索引 · 升腾 910B Infra

> 按章节归类。优先官方文档，其次精选实战博客。版本配套请以官网最新为准。

## 官方主入口

- **昇腾开发者社区 · 学习路径**：https://ascend.developer.huaweicloud.com/learningPath
- **CANN 学习中心（cann-learning-hub）**：系统化入门到算子开发
- **MindSpore 官网/教程**：https://www.mindspore.cn/ （含「分布式并行训练(Ascend)」）
- **torch_npu GitHub**：PyTorch 适配升腾的插件与示例
- **MindIE 文档**：大模型推理引擎
- **ModelArts / MindCluster**：云上训练推理与集群调度

## 按章节

### [01 硬件架构]
- Da Vinci 架构白皮书（官方）
- Ascend 910B 产品规格文档（官方，`npu-smi info` 以实测为准）
- 博客《Ascend 910B 服务器深度解析》（硬件规格、Da Vinci+HCCS、软件栈）
- 博客《华为昇腾 910B 国产化适配深度解析：从 CANN 算子到 vLLM 实践》

### [02 CANN 与算子]
- CANN 学习路线（CANN 学习中心，1-2 周入门 API，2-4 周算子与优化）
- AscendCL 开发指南（C/Python 调用接口）
- TBE 算子开发指南（DSL / TIK）
- ATC 工具指南（模型转 OM）
- 博客《手把手教你在昇腾平台上搭建 PyTorch 训练环境》（华为云社区）

### [03 torch_npu + 分布式]
- torch_npu GitHub 与 README（迁移指南）
- MindSpore「分布式并行训练(Ascend)」官方教程（含 HCCL 说明）
- 博客《910B 多机部署 DeepSeek-V3/R1 满血版实战》（环境/转换/分布式/调优）
- 博客《从零搭建昇腾 AI 开发环境：PyTorch 模型迁移全流程实战》

### [04 推理部署]
- MindIE 官方文档（推理引擎、服务化配置）
- ATC 工具指南（同 02）
- MindCluster / ModelArts 用户指南
- 博客《910B 多机部署 DeepSeek 满血版》（实战链路）

### [05 调优排错]
- msprof 用户指南（性能剖析）
- MindStudio 性能分析文档（时间轴可视化）
- `npu-smi` 命令参考（官方）

## CUDA → 升腾 术语速查

| NVIDIA/CUDA | 升腾 |
|---|---|
| GPU / SM / Tensor Core | Ascend 910B / AI Core / Cube |
| CUDA Driver + Runtime | 驱动+固件 + CANN Runtime |
| cuDNN / cuBLAS | CANN 算子库 |
| CUDA Runtime API | AscendCL |
| TensorRT | ATC + OM / MindIE |
| NCCL | HCCL |
| Nsight / DCGM | msprof / MindStudio |
| nvidia-smi | npu-smi |
| NVLink | HCCS |
| Triton (算子) | TBE (DSL/TIK) |
| vLLM / TRT-LLM | MindIE |
| Slurm / K8s GPU plugin | MindCluster / Ascend Operator |
