# 06 深入浅出 Attention 机制

## 1. 它解决什么问题

上一章 Seq2Seq 的痛点：编码器把**整个输入句子**压缩成**一个固定向量** `c`，长句信息装不下，形成“信息瓶颈”。

```text
"The agreement on the European Economic Area was signed in August 1992."
译成中文时，生成"1992"那个词，最该关注的是原文的"1992"，
而不是被迫从一个压扁了整句的向量里捞信息。
```

Attention 的想法：

> 不要只靠一个总结向量。解码器每生成一个词时，都回头看一遍输入的所有位置，并**动态决定该重点关注哪些位置**。

## 2. 一句话直觉

> Attention 就是“带着问题去原文里查资料，按相关程度加权地把信息取回来”。

生活类比：你做阅读理解题。每回答一道题（解码一步），你不会背下全文，而是带着这道题（query），扫一遍原文每句话（keys），找出最相关的句子，重点读它们的内容（values）作答。相关性高的多读，相关性低的略过——这个“按相关性加权”就是注意力。

## 3. 核心三件套：Query、Key、Value

Attention 把信息检索抽象成 Q、K、V：

```text
Query (Q)：查询，"我现在想找什么"      （解码器当前状态）
Key   (K)：索引，"每个位置的标签"      （输入每个位置的表示）
Value (V)：内容，"每个位置的实际信息"  （输入每个位置的表示）
```

类比图书馆：

```text
Query = 你的搜索词
Key   = 每本书的标题/标签（用来匹配）
Value = 每本书的实际内容（匹配上后要取的东西）
```

## 4. Attention 怎么计算（四步）

```text
第1步：算相关性分数   score(Q, K_i) = Q · K_i   （点积，越大越相关）
第2步：缩放 + softmax  α_i = softmax(scores)      （归一化成权重，和为1）
第3步：加权求和        context = Σ α_i * V_i       （按权重融合各位置内容）
第4步：用 context 帮助产生当前输出
```

### 一个手算小例子

假设输入 3 个位置，解码器当前 Query 与各 Key 点积得到分数：

```text
scores = [2.0, 1.0, 0.1]

softmax 后:
α = [0.66, 0.24, 0.10]   （第1个位置最相关）

context = 0.66*V1 + 0.24*V2 + 0.10*V3
```

解码器主要从第 1 个位置取信息，但也兼顾其他位置。权重 `α` 是**学出来的、随每一步动态变化的**。

## 5. 缩放点积注意力（Scaled Dot-Product Attention）

Transformer 用的标准形式：

```text
Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V
```

- `Q·Kᵀ`：所有 query 和所有 key 的相关性矩阵。
- `√d_k`：缩放因子。维度 `d_k` 大时点积值会很大，使 softmax 进入梯度极小的饱和区，除以 `√d_k` 稳定训练。
- `softmax(...)`：把相关性变成权重。
- `· V`：加权求和取出信息。

## 6. 注意力权重矩阵可以可视化

翻译时，注意力权重 `α` 形成一个**对齐矩阵**，能直观看到“目标词关注了源句哪些词”：

```text
            The   cat   sat
  那只        ■                  （"那只" 对齐 "The"）
  猫                 ■           （"猫"   对齐 "cat"）
  坐着                      ■    （"坐着" 对齐 "sat"）
```

颜色越深权重越大。这种热力图是 Attention 可解释性的经典展示（Bahdanau 2014 论文里就有）。

## 7. 几种常见 Attention

| 类型 | 说明 |
|---|---|
| 加性注意力 (Bahdanau) | 用一个小神经网络算分数，最早用于翻译 |
| 点积注意力 (Luong) | 直接点积算分数，更高效 |
| 缩放点积注意力 | Transformer 采用，加了 √d_k 缩放 |
| 自注意力 (Self-Attention) | Q、K、V 都来自同一序列，序列内部互相关注（见 09 章）|
| 多头注意力 (Multi-Head) | 多组 Q/K/V 并行，关注不同子空间（见 09 章）|

注意区分：

```text
（编码器-解码器）注意力：Query 来自解码器，K/V 来自编码器（跨序列对齐，本章+07 章）
自注意力：             Q/K/V 来自同一序列（序列内部，Transformer 核心）
```

## 8. 最小实现（PyTorch）

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    # Q: [B, Tq, d], K: [B, Tk, d], V: [B, Tk, d]
    d_k = Q.size(-1)
    scores = Q @ K.transpose(-2, -1) / (d_k ** 0.5)   # [B, Tq, Tk] 相关性
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    attn = F.softmax(scores, dim=-1)                  # [B, Tq, Tk] 权重
    context = attn @ V                                # [B, Tq, d] 加权求和
    return context, attn

B, Tq, Tk, d = 2, 3, 5, 8
Q = torch.randn(B, Tq, d)
K = torch.randn(B, Tk, d)
V = torch.randn(B, Tk, d)
context, attn = scaled_dot_product_attention(Q, K, V)
print(context.shape)   # [2, 3, 8]
print(attn.shape)      # [2, 3, 5]  每个 query 对每个 key 的权重
```

这段几行的函数，就是整个 Transformer 的计算核心。

## 9. 为什么 Attention 如此重要

```text
解决信息瓶颈：    不再把长句压成一个向量
建模长程依赖：    任意两个位置直接交互，距离不再是障碍
可并行：          自注意力一次性算所有位置，不像 RNN 串行
可解释：          注意力权重能看出模型在关注什么
```

最后一点最关键：自注意力可以并行 + 直接建模任意距离依赖，这正是 Transformer 抛弃 RNN 的底气。

## 10. 经典论文

- Bahdanau, Cho, Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", 2014：注意力机制的开创性工作。
- Luong et al., "Effective Approaches to Attention-based NMT", 2015：点积注意力。
- Vaswani et al., "Attention Is All You Need", 2017：缩放点积 + 自注意力 + 多头（见 09 章）。

## 本章小结

Attention 让模型在处理每个位置时，按相关性动态地从其他位置取信息，用 Q/K/V 抽象：算分数 → softmax 归一化 → 加权求和。它解决了 Seq2Seq 的信息瓶颈，能建模长程依赖、可并行、可解释，是通往 Transformer 的关键一步。

## 推荐阅读

- Bahdanau et al., 2014（attention 起源）。
- Vaswani et al., "Attention Is All You Need", 2017。
- Jay Alammar, "The Illustrated Transformer" / "Visualizing A Neural Machine Translation Model"（图解博客）。
