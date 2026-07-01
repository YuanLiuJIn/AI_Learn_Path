# 参考资料（语言模型篇）

## 通用

- Stanford CS224n: NLP with Deep Learning；CS324: Large Language Models。
- 博客：Jay Alammar 的 Illustrated 系列（Word2Vec / BERT / GPT / Transformer）。
- GitHub: `huggingface/transformers`（统一跑遍本部分所有模型）。

## 01 十篇论文串烧（全部为必读经典）

- Mikolov et al., Word2Vec, 2013。
- Vaswani et al., "Attention Is All You Need", 2017。
- Devlin et al., "BERT", 2018。
- Radford et al., GPT-1/2/3, 2018–2020。
- Raffel et al., "T5", 2019。
- Kaplan et al., "Scaling Laws", 2020；Hoffmann et al., "Chinchilla", 2022。
- Ouyang et al., "InstructGPT / RLHF", 2022。
- Touvron et al., "LLaMA", 2023。

## 02 表征学习

- Mikolov et al., Word2Vec, 2013；Pennington et al., GloVe, 2014。
- Peters et al., "ELMo", 2018；Devlin et al., "BERT", 2018。
- GitHub: `google-research/bert`、`huggingface/transformers`。

## 03 手写 Agent

- Yao et al., "ReAct", 2022；Schick et al., "Toolformer", 2023；Shinn et al., "Reflexion", 2023。
- GitHub: `langchain-ai/langchain`、`microsoft/autogen`、`OpenHands/OpenHands`。
- 本仓库：`Harness_Engineering/`（理解 Agent 可靠性的工程方法）。

## 04 GPT

- Radford et al., GPT-1/2, 2018–2019；Brown et al., GPT-3, 2020。
- Wei et al., "Emergent Abilities", 2022。
- GitHub: `karpathy/nanoGPT`（从零实现，强烈推荐）、`openai/gpt-2`。

## 05 T5

- Raffel et al., "T5", 2019；Xue et al., "mT5", 2020；Chung et al., "Flan-T5", 2022。
- GitHub: `google-research/text-to-text-transfer-transformer`。

## 06 多模态

- Radford et al., "CLIP", 2021；Alayrac et al., "Flamingo", 2022。
- Li et al., "BLIP-2", 2023；Liu et al., "LLaVA", 2023。
- GitHub: `openai/CLIP`、`mlfoundations/open_clip`、`haotian-liu/LLaVA`。

## 学习建议

1. 先读 10 篇串烧建立地图，再深入 BERT / GPT / T5 三条主线。
2. 用 `transformers` 各跑一次 BERT（填空）、GPT-2（续写）、T5（翻译）、CLIP（零样本分类）。
3. 跟着 `karpathy/nanoGPT` 从零实现一个 GPT，串联 Part2 的 Transformer 知识。
4. 手写一个最小 Agent，体会其脆弱，再回到 `Harness_Engineering/`。
