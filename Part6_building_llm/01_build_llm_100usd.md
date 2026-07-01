# 01 100 刀预算打造 LLM（附 AI 工程基础）

## 1. 它解决什么问题

“训练大模型”听起来要烧几百万美元。但**学习目的**的 LLM，100 美元（甚至几美元租 GPU）就能从零训一个小型 GPT，完整走一遍数据→训练→生成的流程。本章先建立 AI 工程基础和可行预算路径。

> 目标不是造出 ChatGPT，而是亲手把“造一个能生成文本的 GPT”这件事跑通，理解每个工程环节。

## 2. 现实的预算与规模对照

```text
$0（本地 CPU/小 GPU）：字符级迷你 GPT（莎士比亚文本），几分钟出效果
$10~$100（租云 GPU 几小时~几天）：训练一个几千万~几亿参数的小 LLM
$1000~$1万：复现一个像样的小型语言模型（如 GPT-2 规模）
$百万+：前沿大模型（数千 GPU，数月）
```

参考：Karpathy 的 `nanoGPT` 项目，在单卡上几小时可训出能写莎士比亚风格文本的模型；其 `llm.c`、`nanochat` 等项目展示了低成本端到端流程。

## 3. AI 工程基础：训练一个 LLM 的完整流程

```text
1. 准备数据：收集文本 -> 清洗 -> 去重 -> Tokenize -> 打包成训练样本（第 4 章）
2. 定义模型：Transformer 解码器（GPT 架构，复用 Part2/Part4）
3. 训练：自回归预测下一个 token，交叉熵损失，AdamW + 学习率调度
4. 评估：用验证集 loss / perplexity 监控
5. 生成：自回归采样（temperature/top-k/top-p）
6. （可选）微调 + 对齐：指令微调 + RLHF/DPO（连接 Part5）
```

## 4. 最小可跑：迷你 GPT（结合 Part2/Part4）

核心就是把 Part2 的 TransformerBlock 堆起来，做自回归训练：

```python
import torch
from torch import nn

class MiniGPT(nn.Module):
    def __init__(self, vocab, n_layer=6, n_head=6, d_model=384, block=256):
        super().__init__()
        self.tok = nn.Embedding(vocab, d_model)        # token 嵌入
        self.pos = nn.Embedding(block, d_model)        # 位置嵌入
        self.blocks = nn.ModuleList([Block(d_model, n_head) for _ in range(n_layer)])
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab, bias=False)
        self.block = block

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        for blk in self.blocks:
            x = blk(x)                                  # 带因果掩码的自注意力
        logits = self.head(self.ln(x))
        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss
```

`Block` 即 Part2 的“因果自注意力 + FFN + 残差 + LayerNorm”。训练就是不断 `next token prediction`，与 Part4 的 GPT 一致。

## 5. 训练循环要点

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)
for step in range(max_steps):
    xb, yb = get_batch("train")                 # xb=输入序列, yb=右移一位的目标
    _, loss = model(xb, yb)
    optimizer.zero_grad(); loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # 梯度裁剪（防爆炸）
    optimizer.step()
```

关键工程点（很多来自 Part1）：

```text
- 混合精度(bf16/fp16)：省显存提速（Part1 第6章）
- 梯度裁剪：防梯度爆炸
- 学习率 warmup + cosine 衰减：训练更稳
- 梯度累积：单卡显存不够时模拟大 batch
- 定期存 checkpoint：防中断（呼应 Harness 的 checkpoint 思想）
```

## 6. 省钱省显存的实用技巧

```text
1. 先在小数据/小模型上验证流程，再放大（别一上来就大模型）
2. 用 bf16 混合精度
3. 用梯度累积 + gradient checkpointing 换显存
4. 租用 spot/抢占式实例（便宜但可能被中断 -> 配合 checkpoint）
5. 用现成 tokenizer（如 tiktoken），别自己从头训
6. 数据量按 Chinchilla 经验配比（参数与 token 数匹配，别浪费算力）
```

## 7. 从预训练到“能对话”

```text
预训练：学会"续写"（next token）
   ↓
指令微调(SFT)：用"指令-回答"数据，学会"听指令"
   ↓
对齐(RLHF/DPO)：用人类偏好，学会"答得有用、安全"（Part5 的 PPO）
```

100 刀预算通常只够走到预训练/小规模 SFT，但流程是完整的。

## 经典论文与开源项目

- GitHub: `karpathy/nanoGPT`（必学，几百行的 GPT 训练）、`karpathy/llm.c`（纯 C/CUDA 训 GPT-2）、`karpathy/nanochat`（端到端低成本对话模型）。
- Karpathy, "Let's build GPT from scratch"（视频，从零讲透）。
- Hoffmann et al., "Chinchilla", 2022（参数与数据配比）。

## 本章小结

学习目的的 LLM，百元预算即可从零跑通“数据→训练→生成”的完整流程。核心是把 Part2 的 Transformer 堆成 GPT，做自回归预训练，配合混合精度、梯度裁剪/累积、学习率调度、checkpoint 等工程手段。`nanoGPT` 是最佳起点。后续章节深入架构、数据、多卡训练与推理优化。
