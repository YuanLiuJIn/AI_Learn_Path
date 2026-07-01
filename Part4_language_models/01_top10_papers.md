# 01 大语言模型最重要的 10 篇论文串烧

本章用一条时间线把现代大语言模型的关键论文串起来，建立全局地图。每篇只讲“它解决了什么、贡献是什么、为什么重要”，细节留给后续章节。

## 地图总览

```text
2013 Word2Vec ──> 2017 Transformer ──> 2018 BERT / GPT-1
        │                                    │
        │                              2019 GPT-2 / T5
        │                                    │
        └──> 表征学习线              2020 GPT-3 / Scaling Laws
                                             │
                                  2022 InstructGPT(RLHF) / Chinchilla
                                             │
                                  2022+ LLaMA / 开源浪潮
```

## 1. Word2Vec (2013) —— 词向量

Mikolov et al. 让词变成稠密向量，相近词向量相近，甚至能做“国王 - 男人 + 女人 ≈ 王后”的类比。**意义**：奠定“用向量表示语义”的基础。

## 2. Seq2Seq (2014) —— 编码器-解码器

Sutskever et al. 用 LSTM 做“输入序列→输出序列”，开启神经机器翻译（Part2 已讲）。**意义**：生成式 NLP 的框架雏形。

## 3. Attention / Transformer (2014–2017)

Bahdanau 的注意力 + Vaswani 的 "Attention Is All You Need"。**意义**：用自注意力替代 RNN，可并行、建模长程依赖，是后续一切大模型的骨架（Part2 已详讲）。

## 4. BERT (2018) —— 双向预训练

Devlin et al. 用掩码语言模型（MLM）做深度双向预训练，刷新一众理解类任务。**意义**：确立“预训练 + 微调”范式，理解型 NLP 的标杆。

## 5. GPT-1 / GPT-2 (2018–2019) —— 自回归生成

Radford et al. 用 Transformer 解码器做自回归语言模型，GPT-2 展示了强大的零样本生成。**意义**：生成型路线，规模化的起点。

## 6. T5 (2019) —— 文本到文本大一统

Raffel et al. 把翻译、摘要、分类等所有任务都表述成“输入文本→输出文本”。**意义**：统一任务格式，系统研究了预训练的各种选择。

## 7. GPT-3 (2020) —— 规模化与 in-context learning

Brown et al. 把模型放大到 175B 参数，发现**不微调、只给几个例子**（few-shot prompting）就能完成任务。**意义**：揭示“规模带来质变”，催生 prompt 范式。

## 8. Scaling Laws / Chinchilla (2020–2022)

Kaplan et al. 与 Hoffmann et al. 研究“模型大小、数据量、算力”如何影响效果。Chinchilla 指出很多大模型“训练数据喂不够”。**意义**：指导如何高效分配算力（Part6 会用到）。

## 9. InstructGPT / RLHF (2022) —— 对齐

Ouyang et al. 用人类反馈强化学习（RLHF）让模型“听话、有用、安全”，是 ChatGPT 的直接前身。**意义**：从“会生成”到“好用”，对齐成为关键（Part5 强化学习会接上）。

## 10. LLaMA / 开源浪潮 (2023)

Touvron et al. 的 LLaMA 用更优数据和训练，在更小参数下达到强性能，并推动开源生态爆发。**意义**：让研究与应用大众化，是当下大量开源模型的基础。

## 一句话把 10 篇串起来

```text
Word2Vec 给了词的向量；Transformer 给了高效的结构；
BERT 教会理解、GPT 教会生成；T5 统一了任务格式；
GPT-3 发现规模带来 in-context learning；Scaling Laws 教我们怎么花算力；
RLHF 让模型听话；LLaMA 让一切开源普及。
```

## 经典论文与开源项目

以上 10 篇均为必读。配套：

- GitHub: `huggingface/transformers`（用一套 API 跑遍上述模型）。
- 课程：Stanford CS224n、CS324（大模型）。
- 博客：Jay Alammar 的 Illustrated 系列（Word2Vec/BERT/GPT/Transformer 图解）。

## 本章小结

这 10 篇论文构成现代语言模型的主干：表征（Word2Vec）→ 结构（Transformer）→ 理解与生成（BERT/GPT）→ 统一（T5）→ 规模化（GPT-3/Scaling）→ 对齐（RLHF）→ 开源（LLaMA）。后续章节逐一展开其中最关键的几条线。
