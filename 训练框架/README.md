# 大模型训练框架专题

> 本专题系统梳理当前主流的大模型训练 / 微调 / 强化学习 / 多模态训练框架，
> 每个框架都给出：**核心特点 + 安装命令 + 最小可运行示例**。
> 配套阅读：`AgentRl/`（强化学习原理）、`多模态检索/`（多模态原理）。

---

## 0. 最重要的事：先分清"训练"和"用 AI 生成"

很多人把这两件事混为一谈，先记住：

```text
训练框架 = 改模型权重的"工厂"
  → 输入：模型 + 数据 / 奖励
  → 输出：一个"不一样了"的新模型

用 AI 生成 = 调用现成模型的"产品"
  → 输入：模型 + prompt
  → 输出：一段文本 / JSON / 图片（权重不变）
```

你那个 UE5 测试项目其实横跨两层：

```text
SFT 微调 Qwen2.5-7B（2300 条数据）  → 训练层（用 LLaMA-Factory/Unsloth）
运行时 LLM 生成测试 JSON            → 推理层（用 vLLM / API）
```

---

## 1. 框架分层总览

按"是否改权重"从底到顶：

```text
第 0 层  预训练 Pre-training
        从零造模型，喂几万亿 token
        框架：Megatron-LM / DeepSpeed / FSDP
        场景：你基本用不到（太重）

第 1 层  强化学习 RLHF / GRPO / Agent RL
        用奖励信号改模型行为
        框架：veRL / OpenRLHF / Slime / AReaL / TRL
        场景：你 AgentRL 专题在学

第 2 层  微调 SFT / LoRA / DPO
        用小数据让模型擅长某任务
        框架：LLaMA-Factory / ms-swift / Axolotl / Unsloth / TRL
        场景：你已做过的 2300 条 SFT ✅

第 3 层  推理 Inference（用 AI 生成）
        调用现成模型产出内容
        框架：vLLM / SGLang / LMDeploy / 直接 API
        场景：你"LLM 生成测试 JSON" ✅
```

---

## 2. 框架速查表

| 框架 | 层 | 一句话特点 | 你用得到吗 |
|---|---|---|---|
| Megatron-LM | 0 | NVIDIA 3D 并行祖师爷 | 了解原理 |
| DeepSpeed | 0/2 | ZeRO 分片 + 卸载 | 后训练底层 |
| FSDP2 | 0 | PyTorch 原生并行 | 小团队首选 |
| LLaMA-Factory | 2 | 配置/UI 驱动，通吃 LLM+VLM | SFT 首选 |
| ms-swift | 2/4 | 训评部一体，多模态强 | VLM 首选 |
| Axolotl | 2 | YAML 配置驱动 | 灵活党 |
| Unsloth | 2 | 改 kernel 提速省显存 | 单卡神器 |
| TRL | 1/2 | HF 官方 SFT~GRPO 全有 | RL 入门 |
| veRL | 1 | 混合控制器，生成训练分离 | Agent/多模态 RL |
| OpenRLHF | 1 | Ray+vLLM，工程成熟 | 中大规模 RLHF |
| Slime | 1 | 极简单控制器 | 读源码学 RL |
| AReaL | 1 | 异步多轮 Agent RL | UE5 Agent 方向 |
| LLaVA | 4 | VLM 范式开创者 | 学术必读 |
| Qwen-VL | 4 | 官方强多模态 | 接 Qwen 经验 |
| InternVL | 4 | 强视觉编码器 | 多模态研究 |
| vLLM | 3 | PagedAttention 高吞吐 | 部署首选 |
| SGLang | 3 | 结构化/多轮快 | Agent 部署 |
| LMDeploy | 3 | 训推一体 | 配 ms-swift |

---

## 3. 推荐学习顺序（结合你的基础）

```text
① LLaMA-Factory   复现你的 SFT（巩固已有能力）
② Unsloth         单卡把 SFT 跑得更省更快
③ ms-swift        把 Qwen 接成 VLM（打通多模态检索）
④ TRL             跑通 GRPO（打通 AgentRL）
⑤ veRL / AReaL     进阶多轮 Agent RL（UE5 测试 Agent）
```

---

## 4. 目录

```text
训练框架/
├─ README.md                  ← 你在这
├─ 01_底座训练框架.md          预训练 / 大规模：Megatron / DeepSpeed / FSDP
├─ 02_微调框架.md             SFT/LoRA：LLaMA-Factory / ms-swift / Axolotl / Unsloth
├─ 03_RL框架.md               RLHF/GRPO/Agent：TRL / veRL / OpenRLHF / Slime / AReaL
├─ 04_多模态VLM框架.md        LLaVA / Qwen-VL / InternVL
├─ 05_推理部署框架.md         vLLM / SGLang / LMDeploy
├─ 06_选型指南.md             按场景 / 资源怎么选
└─ references.md              官方链接索引
```

> 说明：所有安装命令和示例均为"最小可运行"示意，真实环境请参考各框架
> 官方文档核对版本（PyTorch / CUDA / 模型权重路径会变）。
