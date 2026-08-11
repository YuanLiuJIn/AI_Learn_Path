# 05 · LLMs 主线（伴读）

> 对应原始库：`llms/`（83 文件）。
> LLM 是 Agent 的"身体"、是 RL 后训练的"底座"。这条主线让你理解 Transformer 架构本身，以及它如何支撑后面的 Agent / RL。

## 0. 学习动线

```
架构基础 → 注意力变体 → 训练 → 多模态 → 可解释性
```

## 1. 架构基础 → `llms/架构/`（45 文件，最大）

### 1.1 先读总览
- `transformer-auto-regressive.ipynb`：自回归生成原理（一个 token 一个 token 出）。
- `prefill-decode.ipynb` 与 `pd-分离.ipynb`：**Prefill（并行算 prompt 的 KV）** 与 **Decode（逐 token 生成）** 是两阶段；PD 分离是把它们放到不同硬件/进程，提升吞吐（推理部署核心概念，连回 `升腾910b_infra/04` 的 MindIE）。

### 1.2 注意力家族 → `llms/架构/attention/`（8 个 notebook，现代重点）
按这个顺序读：
```
qkv.ipynb          Q/K/V 是什么（基础）
  → gqa.ipynb      Grouped-Query Attention（KV 分组，省显存，Llama 系列用）
  → mla.ipynb      Multi-head Latent Attention（DeepSeek 用，极致压缩 KV Cache）
  → linear_attn.ipynb   线性注意力（跳出 softmax 的 O(n²)）
  → gated_deltanet.ipynb  门控 delta 网络（SSM 类新架构）
  → dsa.ipynb      Dynamic Sparse Attention（稀疏注意力）
  → attn_sink.ipynb  注意力 sink（streaming LLM 现象：首 token 被过度关注）
  → attention_pattern.ipynb  注意力模式汇总
```

### 1.3 其他架构主题
- `moe/`：混合专家（Mixtral/DeepSeek 用，稀疏激活省算力）。
- `optimizers/`：优化器（AdamW 等）。
- `pe/`：位置编码（RoPE 等，现代 LLM 标配）。
- `tokenizers/`：分词器（BPE/WordPiece，影响一切的上游）。
- `connection/`：层连接/归一化（Pre-LN 等）。
- `optimizers/`、`representation/`：表征相关。
- `dpsk/`、`kimi/`：具体模型（DeepSeek / Kimi）架构拆解。

## 2. 训练 → `llms/training/`
- 预训练 / 微调 / 对齐的整体流程。
- 与 `AgentRl/`、`03_AgenticRL主线.md` 的"后训练"衔接：SFT → RLHF → RLVR。

## 3. 多模态 → `llms/多模态/`（29 文件）
- 视觉-语言对齐（CLIP 思路）、图文生成、跨模态注意力。
- 体量较大，建议在主线走完后再深入。

## 4. 可解释性 → `llms/可解释性/`
-  mechanistic interpretability：找模型里的"电路"、特征方向。
- 偏研究，按需读。

## 5. 关键概念速记

| 概念 | 一句话 | 为什么重要 |
|---|---|---|
| Prefill / Decode | 生成的两阶段 | 推理优化、PD 分离的基础 |
| KV Cache | 缓存历史 K/V 避免重算 | 显存与吞吐的关键；MLA/GQA 都为压缩它 |
| GQA / MLA | KV 压缩的两种路线 | 长上下文、低显存部署 |
| RoPE | 旋转位置编码 | 现代 LLM 长上下文能力来源 |
| MoE | 稀疏专家 | 用更少激活参数换算力 |
| PD 分离 | prefill/decode 解耦部署 | 高吞吐推理架构 |

## 6. 和你其他文件夹的关系

- `Part2_network_architecture/`、`Part4_language_models/`、`Part6_building_llm/`：你自己的 LLM 体系笔记，可对照。
- `升腾910b_infra/04_推理部署.md`：PD 分离、KV Cache 在 910B 上的落地。
- `03_AgenticRL主线.md`：架构是 RL 后训练的底座。

## 7. 在原始库里的阅读落点（精确路径）

`llms/架构/transformer-auto-regressive` → `prefill-decode` / `pd-分离` → `attention/`（按 1.2 顺序）→ `moe/` / `optimizers/` / `pe/` / `tokenizers/` / `connection/` → `llms/training/` → `llms/多模态/` → `llms/可解释性/`

## 验收

- [ ] 能解释自回归生成的 prefill/decode 两阶段
- [ ] 能说清 GQA 与 MLA 都在解决"KV Cache 太大"的问题，路线差异
- [ ] 能解释 RoPE 的作用
- [ ] 理解 MoE 的"稀疏激活"思路
- [ ] 能把 PD 分离和推理部署（连回升腾/MindIE）联系起来
