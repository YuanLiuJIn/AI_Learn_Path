# Part6_building_llm：打造 LLM 篇

本部分是整个学习路线的工程收官：把前面所有知识（Transformer、生成、语言模型、RLHF）落到“**真正从头打造一个大语言模型**”的工程实践上。聚焦数据、架构、训练、推理四大工程支柱，以及在有限预算下的可行路径。

## 主线

```text
预算与工程基础（100 刀也能练一个小 LLM）
        │
现代 LLM 架构演进（RMSNorm、RoPE、GQA、MoE、SwiGLU ...）
        │
数据：数据集 -> 清洗 -> 去重 -> Tokenization
        │
训练：多 GPU 并行（DP / TP / PP / ZeRO）
        │
推理：高性能推理（KV Cache、量化、批处理、投机解码）
        │
        v
一个能跑、能用、可优化的 LLM
```

## 章节顺序

1. `01_build_llm_100usd.md`：100 刀预算打造 LLM（附 AI 工程基础）
2. `02_modern_llm_arch_1.md`：现代 LLM 架构演进及其创新（上）
3. `03_modern_llm_arch_2.md`：现代 LLM 架构演进及其创新（下）
4. `04_data_tokenization.md`：数据集、数据清洗与 Tokenization
5. `05_multi_gpu_training.md`：多 GPU 训练——DP、TP、PP 与 ZeRO
6. `06_llm_inference.md`：LLM 高性能推理——如何极致压榨 GPU
7. `references.md`：论文、开源项目与工具

## 前置要求

- Part2：Transformer 全部细节。
- Part4：GPT、预训练范式、RLHF。
- Part1：GPU/CUDA、混合精度、显存优化（本部分大量用到）。

## 学完后应达到

- 能在小规模上从零训练一个 GPT 并理解每个工程环节。
- 能讲清现代 LLM 相比原始 Transformer 的关键改进（RMSNorm、RoPE、GQA、MoE 等）。
- 能解释数据清洗、去重、Tokenization（BPE）为什么决定模型质量。
- 能区分 DP / TP / PP / ZeRO，知道何时用哪种并行。
- 能讲清 KV Cache、量化、连续批处理等推理优化的原理。
