# 02 现代 LLM 架构演进及其创新（上）

## 1. 它解决什么问题

2017 年的原始 Transformer（Part2）很经典，但现代 LLM（LLaMA、GPT、Qwen 等）做了大量改进，让模型**训练更稳、更省、能扩到更大、上下文更长**。本章（上）讲归一化、位置编码、激活函数三大改进。

## 2. 原始 Transformer 回顾与改进总览

```text
原始 (2017)：           现代 LLM 常用：
- Post-LN（后归一化）  -> Pre-LN（前归一化，更稳）
- LayerNorm            -> RMSNorm（更省更快）
- 绝对位置编码(正弦)    -> RoPE（旋转位置编码，外推好）
- ReLU/GELU            -> SwiGLU（效果更好）
- MHA(多头注意力)       -> GQA/MQA（省推理显存，下篇讲）
- 稠密 FFN             -> MoE（稀疏专家，下篇讲）
```

## 3. Pre-LN vs Post-LN：归一化放哪

```text
Post-LN（原版）：x -> 子层 -> 残差相加 -> LayerNorm
Pre-LN（现代）： x -> LayerNorm -> 子层 -> 残差相加
```

为什么改成 Pre-LN：

> Post-LN 在深层网络里梯度不稳，训练大模型容易发散，要小心翼翼地 warmup。Pre-LN 把归一化放在子层之前，梯度更稳定，深层、大模型更容易训练。

```text
现代写法：x = x + Attention(LayerNorm(x))
         x = x + FFN(LayerNorm(x))
```

## 4. RMSNorm：更简单的归一化

LayerNorm 要算均值和方差再归一化。RMSNorm（Root Mean Square Norm）发现**去掉减均值这一步、只用均方根缩放**，效果几乎一样但更快更省。

```text
LayerNorm： (x - 均值) / 标准差 · γ + β
RMSNorm：   x / RMS(x) · γ       （RMS(x)=√(均值(x²))，无需减均值、无 β）
```

直觉：

> 大模型里那一点点“减均值”的收益不大，省掉它能减少计算和参数。LLaMA 等主流模型都用 RMSNorm。

## 5. RoPE：旋转位置编码

### 原始位置编码的问题

原始 Transformer 用固定的正弦位置编码**加**到词向量上。问题：对没见过的更长序列**外推差**（训练时见过 512 长度，推理 2048 就乱）。

### RoPE 的思想

> 不再“加”位置，而是把位置信息以**旋转**的方式注入到 Q、K 向量里——让两个 token 的注意力只依赖它们的**相对距离**。

```text
直觉：给每个位置的向量旋转一个角度，位置越远转得越多。
两个 token 算注意力(点积)时，结果自然只和"它们差了几个位置"有关。
=> 天然编码相对位置，且对更长序列外推更好。
```

RoPE 是现代 LLM（LLaMA、Qwen、GPT-NeoX 等）的标配，也是长上下文技术的基础（可通过插值扩展）。

## 6. SwiGLU：更好的前馈激活

原始 FFN 用 ReLU/GELU。现代 LLM 多用 **SwiGLU**（门控 + SiLU 激活）：

```text
普通 FFN： FFN(x) = W2 · GELU(W1·x)
SwiGLU：   FFN(x) = W2 · ( SiLU(W1·x) ⊙ (W3·x) )
                              └激活分支┘  └门控分支┘ ⊙是逐元素乘
```

直觉：

> 多一条“门控”分支，让网络能动态控制信息流过多少，表达力更强。代价是多一个权重矩阵（参数略增），但效果提升值得。LLaMA 系列采用。

## 7. 改进效果一句话总结

```text
Pre-LN：  深层大模型训练更稳，少炸
RMSNorm： 比 LayerNorm 更快更省，效果相当
RoPE：    相对位置 + 长序列外推好
SwiGLU：  比 ReLU/GELU 表达力更强、效果更好
```

这些改进单看都不大，叠加起来让现代 LLM 比原始 Transformer 更易训、更强、更能扩展。

## 8. 代码直觉（RMSNorm + SwiGLU）

```python
import torch
from torch import nn
import torch.nn.functional as F

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.g = nn.Parameter(torch.ones(dim))
        self.eps = eps
    def forward(self, x):
        rms = x.pow(2).mean(-1, keepdim=True).add(self.eps).rsqrt()
        return x * rms * self.g           # 只缩放，不减均值

class SwiGLU(nn.Module):
    def __init__(self, dim, hidden):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden, bias=False)   # 激活分支
        self.w3 = nn.Linear(dim, hidden, bias=False)   # 门控分支
        self.w2 = nn.Linear(hidden, dim, bias=False)
    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))
```

## 经典论文与开源项目

- Zhang & Sennrich, "Root Mean Square Layer Normalization" (RMSNorm), 2019。
- Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding" (RoPE), 2021。
- Shazeer, "GLU Variants Improve Transformer" (SwiGLU), 2020。
- Touvron et al., "LLaMA", 2023（综合采用上述改进）。
- GitHub: `meta-llama/llama`、`karpathy/nanoGPT`。

## 本章小结（上）

现代 LLM 在原始 Transformer 上做了关键改进：Pre-LN（训练更稳）、RMSNorm（更省更快）、RoPE（相对位置 + 长序列外推）、SwiGLU（更强的前馈）。这些是 LLaMA 等主流模型的标配。下篇继续讲注意力优化（GQA/MQA）与稀疏专家（MoE）等扩展性创新。
