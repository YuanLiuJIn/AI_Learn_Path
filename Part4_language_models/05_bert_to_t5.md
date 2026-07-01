# 05 BERT 的进化之路：T5 技术详解

## 1. 它解决什么问题

BERT 之后，NLP 模型五花八门，但每个任务的**输入输出格式都不一样**：分类输出标签、翻译输出句子、问答输出片段……每来一个任务都要设计专门的输出头和训练方式。

T5（Text-to-Text Transfer Transformer，Google 2019）提出一个极简且强大的统一思想：

> **把所有 NLP 任务都变成“文本输入 → 文本输出”。**

## 2. 一句话直觉

> T5 说：管你是翻译、分类、摘要还是问答，统统当成“给一段文字，吐一段文字”。用同一个模型、同一种格式、同一个损失搞定一切。

## 3. 一切皆“文本到文本”

通过给输入加**任务前缀**，把不同任务统一：

```text
翻译：  "translate English to German: That is good."  -> "Das ist gut."
分类：  "cola sentence: The course is jumping well."   -> "unacceptable"
相似度："stsb sentence1: ... sentence2: ..."           -> "3.8"
摘要：  "summarize: <长文>"                              -> "<摘要>"
```

连情感分类、打分都用“输出一个词/数字字符串”表示。这样：

```text
统一输入格式：带前缀的文本
统一输出格式：文本
统一损失：    文本的交叉熵
统一模型：    一个 encoder-decoder
```

## 4. 结构：Encoder-Decoder（与 BERT/GPT 都不同）

```text
BERT：只有 Encoder（擅长理解）
GPT： 只有 Decoder（擅长生成）
T5：  Encoder + Decoder（兼顾理解与生成，适合"输入→输出"型任务）
```

Encoder 读懂输入，Decoder 自回归生成输出，中间用交叉注意力连接（Part2 的标准 Transformer）。

## 5. 预训练任务：Span Corruption（片段掩码）

BERT 是遮单个 token，T5 改成**遮一段连续片段**，让模型生成被遮的部分：

```text
原文：   "Thank you for inviting me to your party last week."
输入：   "Thank you <X> me to your party <Y> week."
目标输出："<X> for inviting <Y> last <Z>"
```

用哨兵标记 `<X><Y>` 占位，模型要生成这些位置原本的内容。这比 BERT 的单 token 掩码更贴近“生成”，也适配 encoder-decoder。

## 6. T5 的另一大贡献：系统性消融实验

T5 论文（"Exploring the Limits of Transfer Learning"）像一份**大型实验报告**，系统比较了：

```text
- 架构：encoder-decoder vs decoder-only vs encoder-only
- 预训练目标：语言模型 vs 各种掩码策略
- 数据集大小与质量（提出了 C4 大规模清洗语料）
- 模型规模、训练步数的影响
```

结论指导了后续大量工作，比如“encoder-decoder + span corruption + 大规模干净数据”是当时很强的组合。C4 数据集也成为重要的公开预训练语料。

## 7. T5 家族与影响

```text
T5：         原版，多个尺寸（small ~ 11B）
mT5：        多语言版
Flan-T5：    指令微调版，零样本/少样本能力强
UL2 / T5X：  改进的预训练目标与训练框架
```

“文本到文本”的统一范式深刻影响了后续：今天很多模型（包括对话模型）本质都把任务当成文本到文本。

## 8. BERT vs GPT vs T5 一图总结

| 维度 | BERT | GPT | T5 |
|---|---|---|---|
| 结构 | Encoder | Decoder | Encoder-Decoder |
| 预训练 | MLM（遮单词）| 自回归（预测下一个）| Span corruption（遮片段）|
| 方向 | 双向 | 单向 | 编码双向 + 解码自回归 |
| 擅长 | 理解（分类/抽取）| 生成/续写 | 输入→输出转换（翻译/摘要/QA）|
| 使用 | 微调 | prompt/few-shot | 任务前缀 + 微调 |

## 9. 代码直觉

```python
from transformers import T5Tokenizer, T5ForConditionalGeneration

tok = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

ids = tok("translate English to German: That is good.", return_tensors="pt").input_ids
out = model.generate(ids, max_new_tokens=20)
print(tok.decode(out[0], skip_special_tokens=True))   # "Das ist gut."
```

## 经典论文与开源项目

- Raffel et al., "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), 2019（必读）。
- Xue et al., "mT5", 2020。
- Chung et al., "Scaling Instruction-Finetuned Language Models" (Flan-T5), 2022。
- GitHub: `google-research/text-to-text-transfer-transformer`、`huggingface/transformers`。

## 本章小结

T5 把所有 NLP 任务统一成“文本到文本”，用 encoder-decoder 架构 + span corruption 预训练 + 任务前缀实现一个模型通吃。它还通过大规模消融实验和 C4 语料为迁移学习提供了系统性指南。这种统一范式深刻影响了后续大模型的设计思路。
