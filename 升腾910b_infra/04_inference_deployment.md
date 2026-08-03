# 04 · 推理部署与集群

> 把训练好的模型部署成线上服务。重点：ATC 转 OM、MindIE 推理引擎、大模型在 910B 上的部署。
> 对标：TensorRT / vLLM / TRT-LLM。

## 1. 部署链路总览

```
训练好的权重 (.ckpt / .pt / HuggingFace)
        │
        ▼
[A] 导出中间格式 (ONNX / MindIR)        ← 框架导出
        │
        ▼
[B] ATC 转换 → OM 模型                   ← CANN 离线编译（见 02）
        │
        ▼
[C] 推理引擎加载 (MindIE / AscendCL)     ← 运行时
        │
        ▼
[D] 服务化 (MindIE Service / 自研 HTTP)  ← 上线
```

不同场景选择：
- **小模型 / 离线**：ATC→OM + AscendCL 直接推理（轻量）
- **大模型 (LLM)**：用 **MindIE**（华为对标 vLLM 的推理引擎），支持 PagedAttention、量化、连续批处理
- **集群批量**：MindCluster / ModelArts 调度

## 2. ATC 转 OM（复习 + 深入）

```bash
atc --model=model.onnx \
    --framework=5 \
    --output=model_om \
    --input_shape="input:1,3,224,224" \
    --soc_version=Ascend910B \
    --precision_mode=force_fp16 \
    --op_select_implmode=high_precision   # 算子精度模式
```

常用参数：
- `--input_format=NCHW/ND`：输入排布
- `--dynamic_batch_size`：动态 batch（对标动态 shape）
- `--enable_small_channel`：小通道优化
- `--fusion_switch_file`：融合策略开关文件（控制哪些算子融合）

**infra 要点**：ATC 的转换质量（融合策略、精度模式）直接影响推理时延。遇到精度问题先调 `--precision_mode` 和 `--op_select_implmode`。

## 3. MindIE：大模型推理引擎（重点）

MindIE（Mind Inference Engine）是华为面向 LLM 的推理引擎，能力对标 vLLM / TRT-LLM：

- PagedAttention（KV Cache 分页管理）
- 连续批处理（continuous batching）
- 权重量化（W8A8 / W4A16 等）
- 支持 DeepSeek / Qwen 等主流模型

最小启动（服务化）：

```bash
# 用 MindIE Service 拉起一个 OpenAI 兼容接口（示意）
vim /usr/local/Ascend/mindie/conf/config.json   # 配模型路径、卡号、端口
cd /usr/local/Ascend/mindie/latest/mindie-service
./bin/mindieservice_daemon                        # 启动服务

# 调用（OpenAI 兼容）
curl http://localhost:1025/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek","messages":[{"role":"user","content":"你好"}]}'
```

**infra 要点**：
- 大模型部署瓶颈通常在 **KV Cache 显存** 和 **decode 阶段的算子效率**（逐 token 生成是 memory-bound）。
- 910B 的 ~64GB HBM 能塞下多大模型？粗略：7B(BF16)≈14GB 权重 + KV Cache；70B 需多卡 TP/PP。
- 量化（W8A8）可大幅降显存、提吞吐，但要评估精度损失。

## 4. 实战：910B 部署 DeepSeek 满血版（671B）

搜索结果里有完整实战（百度云《910B 多机部署 DeepSeek-V3/R1》），关键链路：

```
1. 准备权重（HF 格式）→ 转 MindIE 支持的格式
2. 切分策略：671B 必须多机多卡，TP/PP 跨卡
3. 配置 MindIE：并行维度、KV Cache 大小、量化开关
4. 启动 MindIE Service，验证首 token 时延与吞吐
5. 压测：并发、batch、显存占用，调优
```

部署维度参考（示意，以实测为准）：

| 模型 | 显存(权重 BF16) | 典型部署 |
|---|---|---|
| 7B | ~14 GB | 单卡 910B |
| 70B | ~140 GB | 2~4 卡 TP |
| 671B | 数 TB | 多机多卡 TP+PP |

## 5. 集群与调度：MindCluster / ModelArts

| 组件 | 作用 | 对标 |
|---|---|---|
| MindCluster | 集群节点管理、任务调度、故障自愈 | Slurm / K8s |
| ModelArts | 云上训练/推理一站式平台 | SageMaker |
| Ascend Operator | K8s 上调度 NPU 资源 | NVIDIA Device Plugin |

infra 运维视角：
- NPU 资源以 `npu.ai` 资源类型在 K8s 中声明（对标 `nvidia.com/gpu`）
- 任务异常时看 MindCluster 的节点健康 + `npu-smi info -t ecc` 硬件健康
- 故障自愈：掉卡自动隔离、任务重调度

## 6. 部署排错清单

| 现象 | 原因 | 处理 |
|---|---|---|
| OM 转换失败 | `--soc_version` 不匹配 / 算子不支持 | 核对硬件型号；查 ATC 日志 |
| 推理结果异常 | 精度模式 | 调 `--precision_mode` / `--op_select_implmode` |
| 服务起不来 | 端口/卡号配置 | 查 config.json、npu-smi 卡在位 |
| 吞吐低 | KV Cache 小 / 未量化 | 调缓存、开 W8A8、continuous batching |
| 显存爆 | 模型过大未切分 | 加 TP/PP、量化 |

## 7. 本章验收

- [ ] 用 ATC 转换并部署一个小模型
- [ ] 用 MindIE 起一个 LLM 推理服务并成功调用
- [ ] 说清大模型在 910B 上的部署维度与显存估算
- [ ] 了解 MindCluster / ModelArts 在集群中的角色

## 参考

- 官方：MindIE 文档、ATC 工具指南、MindCluster 用户指南（见 [references.md](references.md)）
- 搜索结果：百度云《910B 多机部署 DeepSeek-V3/R1 满血版实战》（环境/转换/分布式/调优全链路）
