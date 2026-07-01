# Part4_language_models：语言模型篇

本部分讲清楚“机器如何理解和生成语言”，从词向量一路到大语言模型与多模态。Part2 学了 Transformer 这个结构，本部分聚焦它如何被用来做语言：表征、预训练、GPT/BERT/T5 路线，以及如何把语言能力扩展到图像（多模态）。

## 主线

```text
Word2Vec（词向量）──> BERT（双向理解）──> T5（统一为文本到文本）
       │
       └──> GPT 系列（自回归生成）──> 多模态（CLIP → Flamingo）
                                              │
                                              v
                                      现代大语言模型 / 多模态大模型
```

## 章节顺序

1. `01_top10_papers.md`：大语言模型最重要的 10 篇论文串烧
2. `02_representation_word2vec_to_bert.md`：表征学习——从 Word2Vec 到 BERT
3. `03_handwrite_agent.md`：手写 Agent 从入门到放弃（番外）
4. `04_gpt_evolution.md`：GPT 进化史——从 GPT-1 到 GPT-3
5. `05_bert_to_t5.md`：BERT 的进化之路——T5 技术详解
6. `06_multimodal_clip_to_flamingo.md`：从 CLIP 到 Flamingo，语言模型的多模态之路
7. `references.md`：论文与开源项目

## 前置要求

- Part2：Attention、Transformer、Encoder/Decoder。
- Part1：交叉熵、softmax、Embedding。
- 名词查 `glossary.md`。

## 学完后应达到

- 能解释词向量为什么能表示语义，以及它的局限。
- 能讲清 BERT（双向、MLM）和 GPT（自回归、单向）的根本区别与各自适用任务。
- 能说明 T5 如何把所有 NLP 任务统一成“文本到文本”。
- 能理解预训练 + 微调范式，以及 GPT-3 的 in-context learning。
- 能讲清 CLIP 如何对齐图文、Flamingo 如何让语言模型“看图说话”。
