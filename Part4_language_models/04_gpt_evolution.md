# 04 GPT 进化史：从 GPT-1 到 GPT-3

## 1. 主线

GPT（Generative Pre-trained Transformer）走的是与 BERT 不同的路线：**自回归生成**。三代演化的关键词是“**规模**”。

```text
GPT-1 (2018)：证明"预训练+微调"对生成式也有效（117M 参数）
GPT-2 (2019)：放大 + 零样本，"语言模型是无监督多任务学习者"（1.5B）
GPT-3 (2020)：再放大 + few-shot，in-context learning 涌现（175B）
```

## 2. GPT 的核心：自回归语言模型

GPT 只用 Transformer 的**解码器**，做一件事——预测下一个 token：

```text
给定 "今天天气真"，预测下一个字的概率分布 -> "好"
把"好"接上，继续预测 -> "今天天气真好，"...
```

训练目标就是 Part3 学的 MLE / 交叉熵（next token prediction）。用**因果掩码**保证只能看左边（不能偷看未来）。

### GPT vs BERT

```text
BERT：双向、做"填空"(MLM)、擅长理解类任务、需要微调
GPT： 单向(从左到右)、做"续写"、擅长生成、可不微调直接用
```

## 3. GPT-1：预训练 + 微调用于生成

GPT-1 先在大量文本上做自回归预训练，再在下游任务上微调。**贡献**：证明无监督预训练学到的语言知识可迁移到多种任务。

## 4. GPT-2：规模 + 零样本

GPT-2 把模型放大到 1.5B，并提出一个有冲击力的观点：

> 一个足够大的语言模型，不需要为每个任务专门训练，**仅靠预训练就能零样本（zero-shot）完成翻译、摘要、问答**——只要把任务用自然语言描述出来。

它还因“生成太逼真可能被滥用”而分批发布，引发广泛关注。

## 5. GPT-3：规模带来质变 —— in-context learning

GPT-3 放大到 175B 参数，发现了一个关键现象：

> **不更新任何参数**，只在 prompt 里给几个示范，模型就能学会任务。这叫 in-context learning（上下文学习）。

```text
zero-shot： 直接问            "翻译成英文：你好 ->"
one-shot：  给一个例子        "你好->Hello；谢谢->"
few-shot：  给几个例子        给 3~5 个翻译示范，再让它翻新句子
```

模型在“前向计算”中就完成了“临时学习”，无需梯度更新。这彻底改变了使用范式——从“微调模型”转向“写 prompt”。

## 6. 为什么“变大”会“变强”：涌现与 Scaling

```text
随着参数、数据、算力增大：
- 损失平滑下降（Scaling Laws 可预测）
- 但某些能力（多步推理、in-context learning）在规模到一定程度后"突然出现"
  -> 称为"涌现能力"(emergent abilities)
```

这解释了为什么大家拼命把模型做大（Part6 会讲怎么做大）。

## 7. GPT-3 之后（简述，承上启下）

```text
InstructGPT (2022)：用 RLHF 让 GPT-3 听指令、更有用 -> ChatGPT 的基础
（RLHF 的强化学习细节见 Part5）
GPT-4+：多模态、更强推理
```

## 8. 代码直觉（自回归生成）

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tok = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

ids = tok("The future of AI is", return_tensors="pt")
out = model.generate(**ids, max_new_tokens=20, do_sample=True, temperature=0.8)
print(tok.decode(out[0]))   # 自回归地逐 token 续写
```

`temperature`、`top_k`、`top_p` 控制采样的随机性（与 Part2 语言模型章一致）。

## 经典论文与开源项目

- Radford et al., "Improving Language Understanding by Generative Pre-Training" (GPT-1), 2018。
- Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2), 2019。
- Brown et al., "Language Models are Few-Shot Learners" (GPT-3), 2020（必读）。
- Wei et al., "Emergent Abilities of Large Language Models", 2022。
- GitHub: `openai/gpt-2`、`karpathy/nanoGPT`（从零实现 GPT，强烈推荐）。

## 本章小结

GPT 是自回归生成路线：用 Transformer 解码器预测下一个 token。GPT-1 证明预训练有效，GPT-2 展示零样本，GPT-3 用 175B 参数解锁 in-context learning，使“写 prompt”取代“微调”成为主流用法。规模带来涌现能力，这是大模型时代的核心信念。后续的“听话”由 RLHF 实现（Part5）。
