# 参考资料（打造 LLM 篇）

## 必学开源项目

- GitHub: `karpathy/nanoGPT`（从零训 GPT，入门首选）。
- GitHub: `karpathy/llm.c`（纯 C/CUDA 训 GPT-2）、`karpathy/nanochat`（低成本端到端对话模型）。
- GitHub: `huggingface/transformers`、`huggingface/accelerate`。
- GitHub: `microsoft/DeepSpeed`、`NVIDIA/Megatron-LM`（大规模训练）。
- GitHub: `vllm-project/vllm`（高性能推理，必学）、`huggingface/text-generation-inference`、`NVIDIA/TensorRT-LLM`。

## 01 工程基础

- Karpathy, "Let's build GPT" / "Let's reproduce GPT-2"（视频）。
- Hoffmann et al., "Chinchilla", 2022（参数-数据配比）。

## 02–03 现代架构

- Zhang & Sennrich, "RMSNorm", 2019。
- Su et al., "RoFormer (RoPE)", 2021。
- Shazeer, "GLU Variants (SwiGLU)", 2020。
- Shazeer, "MQA", 2019；Ainslie et al., "GQA", 2023。
- Fedus et al., "Switch Transformer (MoE)", 2021；Jiang et al., "Mixtral", 2024。
- Dao et al., "FlashAttention" 1/2, 2022–2023。
- Touvron et al., "LLaMA" / "LLaMA 2", 2023。

## 04 数据与 Tokenization

- Raffel et al., "C4/T5", 2019。
- Penedo et al., "RefinedWeb / FineWeb", 2023–2024。
- Lee et al., "Deduplicating Training Data Makes LMs Better", 2021。
- Sennrich et al., "BPE", 2016；Kudo, "SentencePiece", 2018。
- GitHub: `huggingface/datatrove`、`huggingface/tokenizers`、`openai/tiktoken`、`google/sentencepiece`。

## 05 多 GPU 训练

- Shoeybi et al., "Megatron-LM", 2019。
- Huang et al., "GPipe", 2019。
- Rajbhandari et al., "ZeRO", 2020。
- 文档：DeepSpeed、PyTorch FSDP、HuggingFace Accelerate。

## 06 推理优化

- Kwon et al., "vLLM / PagedAttention", 2023。
- Leviathan et al., "Speculative Decoding", 2023。
- Frantar et al., "GPTQ", 2022；Lin et al., "AWQ", 2023。

## 学习建议

1. 先用 `nanoGPT` 在莎士比亚数据上训通一个迷你 GPT，串联 Part2 的 Transformer。
2. 读 LLaMA 论文，对照第 2–3 章逐个核对现代架构改进。
3. 自己写一遍 BPE 的合并逻辑，理解 tokenization。
4. 用 HuggingFace Accelerate / DeepSpeed 体验多卡训练配置。
5. 用 vLLM 部署一个开源模型，观察吞吐与延迟，理解推理优化。

## 全路线收官

至此 Part1–Part6 + Harness 专题构成完整学习地图：

```text
Part1 基础 -> Part2 网络结构 -> Part3 内容生成 -> Part4 语言模型
        -> Part5 强化学习 -> Part6 打造 LLM
专题：Harness Engineering（让模型能力变成可靠产品）
工具：glossary.md（全局术语表）
```

下一步可深入的方向：智能体系统、多模态大模型、模型对齐与安全、领域大模型应用。
