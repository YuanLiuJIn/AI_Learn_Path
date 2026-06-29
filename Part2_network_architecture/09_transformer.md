# 09 Transformer 详解

> Vaswani et al., "Attention Is All You Need", NeurIPS 2017。
> 现代大模型（GPT、BERT、LLaMA、T5 ……）的共同基石。本章是 Part2 的终点，也是后续大模型阶段的起点。

## 1. 它解决什么问题

到第 7 章为止，最强的翻译模型是 RNN + Attention。但 RNN 有两个无法回避的硬伤：

```text
1. 无法并行：必须算完 h_{t-1} 才能算 h_t，时间步串行，训练慢
2. 长程依赖弱：信息要逐步传递，距离越远越容易衰减
```

Transformer 的革命性主张：

> 既然 Attention 这么有用，那就**完全去掉 RNN**，只用注意力。让序列里任意两个位置直接交互，并且可以一次性并行计算所有位置。

## 2. 一句话直觉

> Transformer 让句子里每个词都同时“看一遍所有词”（包括自己），按相关性收集信息来更新自己的表示。没有先后顺序的串行依赖，所以能大规模并行。

## 3. 整体架构

原始 Transformer 是 Encoder-Decoder 结构（用于翻译）：

```text
        输入序列                        输出序列(右移)
          │                                │
   [输入Embedding]                  [输出Embedding]
          │ + 位置编码                     │ + 位置编码
          v                                v
   ┌─────────────┐                 ┌─────────────────┐
   │  Encoder    │                 │   Decoder       │
   │  × N 层     │ ──────────────> │   × N 层        │
   │             │   (K,V 给解码器) │                 │
   └─────────────┘                 └─────────────────┘
                                            │
                                     [Linear + Softmax]
                                            │
                                       输出概率分布
```

每个 Encoder 层包含：

```text
1. Multi-Head Self-Attention（多头自注意力）
2. Feed-Forward Network（前馈网络）
每个子层都包 残差连接 + LayerNorm
```

每个 Decoder 层包含：

```text
1. Masked Multi-Head Self-Attention（带掩码，防止看到未来）
2. Encoder-Decoder Attention（关注编码器输出）
3. Feed-Forward Network
同样每个子层都有 残差 + LayerNorm
```

## 4. 核心模块逐个拆解

### 4.1 自注意力（Self-Attention）

第 6 章的注意力里，Query 来自解码器、K/V 来自编码器（跨序列）。**自注意力**则是 Q、K、V **都来自同一个序列**：

```text
句子 "The animal didn't cross the street because it was tired"
处理 "it" 时，自注意力让 "it" 去关注句中所有词，
学到 "it" 指代 "animal" -> 给 "animal" 高注意力权重
```

计算就是第 6 章的缩放点积注意力：

```text
Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V
```

其中 Q、K、V 由同一输入 X 分别乘以三个可学习矩阵得到：

```text
Q = X·W_Q,  K = X·W_K,  V = X·W_V
```

### 4.2 多头注意力（Multi-Head Attention）

只做一次注意力，模型只能学到一种“关注方式”。多头让模型**并行做多组注意力**，每组关注不同的子空间（如有的关注语法、有的关注指代）。

```text
把 Q/K/V 切成 h 份（h 个头），每个头独立做注意力，
再把 h 个头的结果拼接起来，过一个线性层融合。

MultiHead(Q,K,V) = Concat(head_1, ..., head_h) · W_O
```

直觉：像让多个专家从不同角度看同一句话，再综合意见。

### 4.3 位置编码（Positional Encoding）

自注意力本身**没有顺序概念**（它平等地看所有位置），但语言有语序。所以要显式注入位置信息：

```text
给每个位置加一个位置向量，原论文用正弦/余弦函数：
PE(pos, 2i)   = sin(pos / 10000^(2i/d))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d))

输入 = 词Embedding + 位置编码
```

现代大模型常用改进版（如 RoPE 旋转位置编码）。核心目的不变：让模型知道词的先后位置。

### 4.4 前馈网络（FFN）

每个位置独立过一个两层 MLP，增加非线性表达：

```text
FFN(x) = max(0, x·W1 + b1)·W2 + b2     （中间用 ReLU/GELU）
```

注意：FFN 对每个位置**独立且相同**地处理（position-wise）。

### 4.5 残差连接 + LayerNorm

每个子层都套：

```text
output = LayerNorm(x + Sublayer(x))
```

这里 `x + Sublayer(x)` 就是第 8 章的残差连接！没有它，深层 Transformer 也训不动。LayerNorm 稳定每层的数值分布。

### 4.6 掩码（Mask）

解码器生成时不能“偷看”未来的词（否则就作弊了）。**因果掩码 (causal mask)** 把当前位置之后的注意力分数设为 `-inf`：

```text
生成第 3 个词时，只能看第 1、2、3 个位置，看不到第 4 个之后。
```

这正是 GPT 这类自回归语言模型的关键。

## 5. 最小自注意力实现（PyTorch）

```python
import torch
from torch import nn
import torch.nn.functional as F

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.qkv = nn.Linear(d_model, d_model * 3)   # 一次算出 Q,K,V
        self.out = nn.Linear(d_model, d_model)

    def forward(self, x, mask=None):
        B, T, D = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.num_heads, self.d_k)
        qkv = qkv.permute(2, 0, 3, 1, 4)             # [3, B, heads, T, d_k]
        Q, K, V = qkv[0], qkv[1], qkv[2]

        scores = Q @ K.transpose(-2, -1) / (self.d_k ** 0.5)  # [B, heads, T, T]
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        attn = F.softmax(scores, dim=-1)
        context = attn @ V                           # [B, heads, T, d_k]

        context = context.transpose(1, 2).reshape(B, T, D)    # 合并多头
        return self.out(context)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff):
        super().__init__()
        self.attn = MultiHeadSelfAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        x = self.norm1(x + self.attn(x, mask))   # 残差 + LayerNorm
        x = self.norm2(x + self.ff(x))           # 残差 + LayerNorm
        return x

# 验证
x = torch.randn(2, 10, 64)   # [batch, seq_len, d_model]
block = TransformerBlock(d_model=64, num_heads=8, d_ff=256)
print(block(x).shape)        # [2, 10, 64]
```

这个 `TransformerBlock` 堆叠 N 次，就是 GPT/BERT 的主体。

## 6. Transformer vs RNN

| 维度 | RNN/LSTM | Transformer |
|---|---|---|
| 计算方式 | 串行（按时间步） | 并行（一次算所有位置） |
| 长程依赖 | 随距离衰减 | 任意两位置直接交互 |
| 训练速度 | 慢 | 快（适合 GPU 大规模并行） |
| 位置信息 | 天然有序 | 需位置编码显式注入 |
| 扩展性 | 难堆很大 | 极易 scale 到千亿参数 |

最后一行是关键：Transformer 的可并行 + 可扩展，直接催生了大模型时代。

## 7. 三大衍生范式

| 范式 | 代表 | 用法 |
|---|---|---|
| Encoder-only | BERT | 理解类任务（分类、抽取） |
| Decoder-only | GPT、LLaMA | 生成类任务（对话、写作），自回归 |
| Encoder-Decoder | T5、原始 Transformer | 序列转换（翻译、摘要） |

当下主流大语言模型多为 **Decoder-only**（GPT 路线）。

## 8. 为什么说"Attention Is All You Need"

```text
- 抛弃 RNN/CNN，只用注意力 + FFN，结构简洁
- 可并行 -> 能用海量数据 + 大算力训练
- 可扩展 -> 参数从亿到万亿，能力随规模持续增长（scaling law）
- 通用 -> 文本、图像(ViT)、语音、多模态都能用
```

这篇 2017 年的论文，奠定了之后所有大模型的技术路线。

## 9. 通往大模型

学完 Transformer，你已经站在大模型的门口。后续阶段会展开：

```text
- Tokenization 与 BPE
- 预训练（next token prediction，规模化）
- 微调与指令对齐、RLHF
- 推理加速、KV cache、量化
- 长上下文、MoE、多模态
```

这些都建立在本章的 Transformer 之上。

## 本章小结

Transformer 用自注意力替代循环：每个位置并行地关注序列中所有位置；多头让模型从多角度建模；位置编码补回顺序信息；残差 + LayerNorm 让深层可训练；掩码支撑自回归生成。它可并行、可扩展、通用，是现代所有大模型的共同基石。

## 推荐阅读

- Vaswani et al., "Attention Is All You Need", NeurIPS 2017。
- Jay Alammar, "The Illustrated Transformer"（最佳图解入门）。
- Andrej Karpathy, "Let's build GPT" / nanoGPT（从零实现，强烈推荐）。
- Devlin et al., "BERT", 2018；Radford et al., "GPT" 系列论文。
- Harvard NLP, "The Annotated Transformer"（逐行注释实现）。
