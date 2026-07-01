# 03 现代 LLM 架构演进及其创新（下）

> 上篇讲了 Pre-LN、RMSNorm、RoPE、SwiGLU。本篇讲注意力优化（MQA/GQA）、稀疏专家（MoE）、长上下文与其他扩展性创新。

## 1. 注意力的显存瓶颈：KV Cache 太大

推理时为了加速，要缓存每个 token 的 Key 和 Value（KV Cache，见第 6 章）。问题：

```text
多头注意力(MHA)：每个头都有自己的 K、V -> KV Cache 巨大
长上下文 + 大 batch 时，KV Cache 占的显存甚至超过模型本身！
```

## 2. MQA 与 GQA：共享 K/V 省显存

### MQA（Multi-Query Attention）

```text
MHA：  每个 Query 头配自己的 K、V 头
MQA：  所有 Query 头共享同一组 K、V
=> KV Cache 缩小 N 倍（N=头数），推理快很多
代价：表达力略降，可能掉点
```

### GQA（Grouped-Query Attention）—— 折中方案

```text
GQA：把 Query 头分成几组，每组共享一组 K、V
     （介于 MHA 和 MQA 之间）
```

```text
MHA：  8 个 Q 头 -> 8 组 KV   （质量最好，KV最大）
GQA：  8 个 Q 头 -> 2 组 KV   （质量与省显存平衡）✓ 主流选择
MQA：  8 个 Q 头 -> 1 组 KV   （最省，质量略降）
```

直觉：

> GQA 找到了“省 KV Cache”和“保住质量”的甜点，被 LLaMA-2/3、Qwen 等广泛采用。

## 3. MoE：稀疏专家，参数多但算得少

### 一句话直觉

> 与其让一个巨大的 FFN 处理所有 token，不如准备很多个“专家”FFN，每个 token 只激活其中少数几个。这样**总参数量很大（知识多），但每次实际计算量很小**。

```text
稠密模型：每个 token 都过完整的大 FFN
MoE：    有 N 个专家 FFN + 一个"路由器"
         路由器给每个 token 选 top-k 个专家（如 8 选 2）
         只有被选中的专家参与计算
```

```text
       token
         │
    [路由器 Router] 决定用哪几个专家
         │
   ┌─────┼─────┬─────┐
专家1  专家2  专家3 ... 专家N    （只激活 2 个，其余不算）
   └─────┴─────┘
     加权合并 -> 输出
```

### 优缺点

```text
优点：参数量可以做到极大（万亿级），但每 token 计算量(FLOPs)只相当于小模型
     -> "用小算力跑大知识"
缺点：显存要装下所有专家；路由不均衡(有的专家过载)；训练更复杂
代表：Mixtral 8x7B、DeepSeek-MoE、GPT-4(传闻)等
```

## 4. 长上下文（Long Context）

让模型处理几万甚至上百万 token 的输入，是近年热点：

```text
1. RoPE 插值/外推：把训练时的位置编码"拉伸"到更长（NTK、YaRN 等）
2. 注意力优化：FlashAttention（省显存、不近似）让长序列可行
3. 稀疏/局部注意力：只关注部分位置，降低 O(n²) 开销
4. 滑动窗口注意力：每个 token 只看附近窗口（Mistral 用）
```

注意：注意力是 O(序列长度²)，长上下文的核心挑战就是这个平方复杂度。

## 5. FlashAttention：不改结果，只改算法

```text
问题：注意力中间的大矩阵(N×N)要写回显存，慢且费显存
FlashAttention：用分块 + 不存中间大矩阵的方式算注意力
  -> 数学结果完全一样，但更快、更省显存
  -> 几乎是现代训练/推理的标配
```

这是“算法层面”的优化（呼应 Part1 的计算/内存瓶颈），不改变模型，只改变怎么算。

## 6. 现代 LLM 架构改进全景

| 改进 | 解决什么 | 代表 |
|---|---|---|
| Pre-LN | 训练稳定 | 几乎所有现代 LLM |
| RMSNorm | 更省更快 | LLaMA、Qwen |
| RoPE | 相对位置、长序列外推 | LLaMA、Qwen、GPT-NeoX |
| SwiGLU | 更强前馈 | LLaMA |
| GQA/MQA | 省 KV Cache、推理快 | LLaMA-2/3、Qwen |
| MoE | 参数大、算力省 | Mixtral、DeepSeek |
| FlashAttention | 注意力省显存提速 | 训练/推理标配 |
| 长上下文(YaRN等) | 处理超长输入 | 长文模型 |

## 7. 一句话把上下两篇串起来

```text
现代 LLM = 原始 Transformer
  + Pre-LN/RMSNorm（训练稳、省）
  + RoPE（位置 + 长序列）
  + SwiGLU（强前馈）
  + GQA/MQA（推理省显存）
  + MoE（参数大算力省，可选）
  + FlashAttention（算得快省显存）
```

这些累积创新，是大模型能越做越大、上下文越来越长、推理越来越省的工程基础。

## 经典论文与开源项目

- Shazeer, "Fast Transformer Decoding (MQA)", 2019。
- Ainslie et al., "GQA", 2023。
- Shazeer et al., "Outrageously Large Neural Networks (MoE)", 2017；Fedus et al., "Switch Transformer", 2021。
- Jiang et al., "Mixtral of Experts", 2024。
- Dao et al., "FlashAttention", 2022；"FlashAttention-2", 2023。
- GitHub: `Dao-AILab/flash-attention`、`mistralai/mistral-src`、`meta-llama/llama`。

## 本章小结（下）

为了让模型更大、上下文更长、推理更省：GQA/MQA 通过共享 K/V 缩小 KV Cache；MoE 用稀疏专家实现“参数多但算力省”；FlashAttention 在算法层省显存提速；RoPE 插值与稀疏/窗口注意力支撑长上下文。结合上篇，现代 LLM 是在原始 Transformer 上叠加这一系列工程创新而成。
