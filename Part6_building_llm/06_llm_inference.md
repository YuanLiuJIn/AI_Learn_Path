# 06 LLM 高性能推理：如何极致压榨 GPU 性能

## 1. 它解决什么问题

训练是一次性的，**推理是每天无数次的**。推理成本直接决定一个 LLM 服务能不能赚钱、能服务多少用户。本章讲如何让推理又快、又省、又能扛高并发。

## 2. 先理解：LLM 推理为什么慢

LLM 自回归生成——一个一个 token 蹦：

```text
生成 "今天天气真好"：
  先算"今"，再把"今"接上算"天"，再算"气"...
  每个新 token 都要把整个模型跑一遍前向
```

两个阶段，瓶颈不同：

```text
Prefill（预填充）：处理输入 prompt，一次性算完所有输入 token -> 计算密集
Decode（解码）：  逐个生成新 token，每次只算 1 个 -> 内存带宽密集(读权重的开销 >> 计算)
```

关键洞察：

> Decode 阶段，GPU 大部分时间在“搬运模型权重”，而不是“计算”。所以很多优化是为了**减少访存、提高 GPU 利用率**。

## 3. KV Cache：最重要的推理优化

### 问题

自回归生成时，每生成一个新 token 都要和前面所有 token 算注意力。如果每次都重算前面所有 token 的 Key/Value，重复计算量爆炸。

### 一句话直觉

> 把前面 token 已经算过的 Key、Value **缓存**起来，生成新 token 时直接复用，只算新 token 的 K/V。用空间换时间。

```text
不缓存：生成第 100 个 token 要重算前 99 个的 K/V
KV Cache：前 99 个的 K/V 存着，只算第 100 个的 -> 快得多
```

代价：KV Cache 占大量显存（呼应上一章 GQA/MQA 就是为了缩小它）。

```text
KV Cache 显存 ∝ 层数 × 头数 × 序列长度 × batch
长上下文 + 高并发时，KV Cache 是头号显存杀手。
```

## 4. 量化（Quantization）：用更低精度

### 一句话直觉

> 把模型权重从 fp16（16 位）压到 int8、int4（8/4 位），显存减半甚至四分之一，访存更快，质量损失可控。

```text
fp16：每个权重 2 字节   （训练精度）
int8：每个权重 1 字节   （省一半）
int4：每个权重 0.5 字节 （省四分之三）
```

```text
推理量化方法：GPTQ、AWQ（权重量化，几乎不掉点）
权衡：量化越激进越省，但质量可能下降，需测试
适用：让大模型能在小显存(甚至消费级显卡)上跑
```

## 5. 连续批处理（Continuous Batching）

### 问题

传统批处理：一批请求一起进、一起出。但 LLM 各请求生成长度不同，短的早就完了还得等长的，GPU 空转。

### 一句话直觉

> 不等整批结束——谁生成完了就让它走、立刻把新请求填进来，让 GPU 时刻满载。像餐厅拼桌，有人吃完就翻台，不等全桌一起走。

```text
静态批处理：8 个请求一起开始，等最慢的结束才能下一批 -> GPU 利用率低
连续批处理：每生成一步就动态调整 batch，完成的踢出、新来的加入 -> 利用率高
```

这是 vLLM、TGI 等推理框架吞吐量高的关键之一。

## 6. PagedAttention：像操作系统管内存一样管 KV Cache

vLLM 的招牌技术：

```text
问题：KV Cache 连续分配，但请求长度不定 -> 显存碎片化、浪费
PagedAttention：把 KV Cache 分成小"页"，按需分配(类比 OS 虚拟内存分页)
  -> 几乎零碎片，显存利用率大增，能支持更高并发
```

## 7. 投机解码（Speculative Decoding）

### 一句话直觉

> 用一个**小而快**的模型先“猜”出接下来几个 token，再用大模型**一次性验证**这几个。猜对了就白赚（一步顶多步），猜错了回退。

```text
小模型：快速草拟 5 个 token（便宜）
大模型：一次前向并行验证这 5 个，接受对的、拒绝错的
=> 大模型一次前向可能产出多个 token -> 加速，且结果与大模型单独生成一致
```

## 8. 其他优化

```text
FlashAttention：     注意力省显存提速（上一章，训练推理都用）
算子融合(fusion)：    把多个小算子合并，减少访存
张量并行推理：        大模型推理也可多卡切分
Prefix Caching：     相同前缀(如系统提示)的 KV 复用，省 prefill
```

## 9. 推理优化全景

| 优化 | 省什么 | 代价/适用 |
|---|---|---|
| KV Cache | 重复计算 | 占显存（必用）|
| GQA/MQA | KV Cache 显存 | 略掉点（架构层）|
| 量化(int8/4) | 显存、访存 | 可能掉点 |
| 连续批处理 | GPU 空转 | 高并发服务 |
| PagedAttention | 显存碎片 | 高并发（vLLM）|
| 投机解码 | 解码延迟 | 需小草稿模型 |
| FlashAttention | 注意力显存/时间 | 通用 |

## 10. 实用建议

```text
自己部署：直接用 vLLM / TGI / TensorRT-LLM（已集成上述大部分优化）
关注指标：吞吐量(tokens/s)、首 token 延迟(TTFT)、显存占用、并发数
权衡：    延迟敏感(对话) vs 吞吐优先(批量处理) 选不同策略
```

## 经典论文与开源项目

- Kwon et al., "Efficient Memory Management for LLM Serving with PagedAttention" (vLLM), 2023。
- Leviathan et al., "Speculative Decoding", 2023。
- Frantar et al., "GPTQ", 2022；Lin et al., "AWQ", 2023。
- Dao et al., "FlashAttention", 2022。
- GitHub: `vllm-project/vllm`（必学）、`huggingface/text-generation-inference`、`NVIDIA/TensorRT-LLM`。

## 本章小结（Part6 完结）

LLM 推理慢在自回归 + 访存瓶颈。核心优化：KV Cache（复用已算的 K/V，最重要）、量化（低精度省显存访存）、连续批处理 + PagedAttention（高并发满载 GPU）、投机解码（小模型猜大模型验证）、FlashAttention（注意力提速）。生产部署直接用 vLLM 等框架。至此打造 LLM 篇完结：数据、架构、训练、推理四大支柱齐备，你已具备从零理解和参与大模型工程的完整知识地图。
