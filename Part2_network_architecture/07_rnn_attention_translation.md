# 07 RNN + Attention 机器翻译模型

## 1. 本章目标

把第 6 章的 Attention 接到第 5 章的 Seq2Seq 上，得到带注意力的翻译模型——这正是 2014~2017 年神经机器翻译（NMT）的主流架构，也是理解 Transformer 前的最后一站。

```text
05 章 Seq2Seq：编码器把整句压成一个向量 c -> 信息瓶颈
06 章 Attention：解码每一步动态看输入
07 章（本章）：Seq2Seq + Attention -> 解决瓶颈，翻译质量大幅提升
```

## 2. 结构对比

### 没有 Attention（普通 Seq2Seq）

```text
编码器最后一个隐藏状态 c  ──>  解码器的唯一信息来源
                              （长句信息丢失）
```

### 有 Attention

```text
编码器保留每个时间步的隐藏状态  h_1, h_2, ..., h_T  （不再只用最后一个）
                │
解码器第 t 步：
   用当前解码状态 s_t 作为 Query
   对所有编码器状态 h_i 算注意力权重 α
   得到上下文向量 c_t = Σ α_i * h_i   （这一步专属的、动态的上下文）
   用 c_t + s_t 预测当前词
```

关键差异：上下文向量从“固定的 `c`”变成“每个解码步都不同的 `c_t`”。

## 3. 完整数据流图

```text
源句:  x1   x2   x3   x4
        │    │    │    │
      [Encoder GRU 双向/单向]
        │    │    │    │
        h1   h2   h3   h4     <- 编码器保留所有时间步状态
        └────┬────┴────┘
             │  解码第 t 步：
   s_t ───> 算 α (s_t 对每个 h_i 的注意力)
             │
             α = [0.1, 0.7, 0.1, 0.1]   <- 这步主要看 h2
             │
   c_t = Σ α_i h_i  ──> [拼接 s_t, c_t] ──> 预测 y_t
```

## 4. 关键实现（PyTorch）

下面给出带注意力的解码器核心（编码器与第 5 章类似，但要返回**所有**时间步输出）。

```python
import torch
from torch import nn
import torch.nn.functional as F

class Encoder(nn.Module):
    def __init__(self, vocab_size, embed=64, hidden=128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed)
        self.rnn = nn.GRU(embed, hidden, batch_first=True)

    def forward(self, src):
        x = self.embed(src)
        outputs, h = self.rnn(x)     # outputs: [B, T, hidden] 全部时间步
        return outputs, h            # 注意：保留 outputs，给注意力用


class Attention(nn.Module):
    """加性注意力 (Bahdanau)"""
    def __init__(self, hidden):
        super().__init__()
        self.W = nn.Linear(hidden * 2, hidden)
        self.v = nn.Linear(hidden, 1, bias=False)

    def forward(self, decoder_state, encoder_outputs):
        # decoder_state: [B, hidden]  encoder_outputs: [B, T, hidden]
        T = encoder_outputs.size(1)
        s = decoder_state.unsqueeze(1).repeat(1, T, 1)     # [B, T, hidden]
        energy = torch.tanh(self.W(torch.cat([s, encoder_outputs], dim=2)))
        scores = self.v(energy).squeeze(2)                 # [B, T] 每个位置分数
        alpha = F.softmax(scores, dim=1)                   # [B, T] 注意力权重
        context = torch.bmm(alpha.unsqueeze(1), encoder_outputs).squeeze(1)
        return context, alpha                              # context: [B, hidden]


class AttnDecoder(nn.Module):
    def __init__(self, vocab_size, embed=64, hidden=128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed)
        self.attn = Attention(hidden)
        self.rnn = nn.GRU(embed + hidden, hidden, batch_first=True)  # 输入拼了 context
        self.fc = nn.Linear(hidden * 2, vocab_size)

    def forward(self, token, hidden, encoder_outputs):
        x = self.embed(token)                              # [B, 1, embed]
        context, alpha = self.attn(hidden[-1], encoder_outputs)  # 算注意力
        rnn_in = torch.cat([x.squeeze(1), context], dim=1).unsqueeze(1)
        out, hidden = self.rnn(rnn_in, hidden)
        logits = self.fc(torch.cat([out.squeeze(1), context], dim=1))
        return logits, hidden, alpha                       # 返回 alpha 便于可视化
```

要点：
- 编码器返回**所有时间步** `outputs`，不再只用最后状态。
- 解码每步：先用 `Attention` 算出 `context` 和权重 `alpha`，再把 `context` 拼进 RNN 输入和输出层。
- 返回 `alpha`，用于画对齐热力图。

## 5. 可视化注意力对齐

收集每个解码步的 `alpha`，堆成矩阵画热力图：

```python
import matplotlib.pyplot as plt

# attn_matrix: [tgt_len, src_len]，每行是一个目标词对源句的注意力
def plot_attention(attn_matrix, src_tokens, tgt_tokens):
    fig, ax = plt.subplots()
    ax.imshow(attn_matrix, cmap="viridis")
    ax.set_xticks(range(len(src_tokens)))
    ax.set_yticks(range(len(tgt_tokens)))
    ax.set_xticklabels(src_tokens, rotation=90)
    ax.set_yticklabels(tgt_tokens)
    ax.set_xlabel("Source"); ax.set_ylabel("Target")
    plt.tight_layout(); plt.show()
```

典型的翻译对齐图会呈现近似对角线的亮带（语序相近的语言），语序差异大的地方会偏离对角线——这直观证明模型学会了“对齐”。

## 6. 这一步在历史上的意义

```text
2014 Seq2Seq：神经翻译可行，但长句差
2014 + Attention (Bahdanau)：长句翻译质量大幅提升，成为 NMT 标准
2016 Google GNMT：大规模工程化的 RNN+Attention 翻译系统上线
2017 Transformer："Attention Is All You Need"，干脆去掉 RNN，只留注意力
```

本章模型是承上启下的关键：它证明了 Attention 的威力，而 Transformer 则把这个思想推向极致——既然注意力这么有用，为什么还要 RNN？

## 7. RNN+Attention 的残留问题

```text
- 仍依赖 RNN，时间步必须串行计算，无法充分并行 -> 训练慢
- 长序列下 RNN 部分依然吃力
=> Transformer 用自注意力替换 RNN，彻底并行化（下一章）
```

## 8. 经典论文

- Bahdanau, Cho, Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", ICLR 2015（RNN+Attention 翻译奠基）。
- Luong et al., "Effective Approaches to Attention-based NMT", EMNLP 2015。
- Wu et al., "Google's Neural Machine Translation System", 2016（GNMT，工业级落地）。

## 本章小结

把 Attention 接入 Seq2Seq：编码器保留所有时间步状态，解码器每步用当前状态作 Query 动态计算上下文向量，解决了固定向量的信息瓶颈，并能可视化对齐。它是 NMT 的里程碑，也直接启发了 Transformer。

## 推荐阅读

- Bahdanau et al., 2015。
- Jay Alammar, "Visualizing A Neural Machine Translation Model (Seq2Seq with Attention)"。
- *Dive into Deep Learning*，注意力机制与机器翻译章节。
