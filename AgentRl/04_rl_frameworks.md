# 04. Agent RL 开源框架（对照 Survey §5.2 分类）

> 目标：理解三大框架的架构差异，并用 Landscape Survey §5.2 的**框架分类法**给它们定位。
> 读完应能回答："为什么多轮 Agent RL 更推荐 Slime？""HybridFlow 解决了什么？"

## 0. Survey §5.2 的框架三分类

```text
A. Agentic RL frameworks        —— 专为多步 Agent 训练设计（解耦环境交互与优化）
B. RLHF and LLM fine-tuning     —— 通用后训练框架（PPO/DPO/GRPO）
C. General-purpose RL frameworks—— 通用 RL 库（可改造用于 LLM）
```

下面三个主流框架，本质是 B 类向 A 类演进的代表。

---

## 1. RL Infra 标准范式（由 OpenRLHF 确立）

```text
┌─────────────────────────────────────────┐
│              Ray（调度层）               │
├─────────────────────────────────────────┤
│  推理引擎               训练引擎          │
│  ├─ vLLM                ├─ DeepSpeed     │
│  └─ SGLang              ├─ FSDP          │
│                          └─ Megatron      │
│  Actor ←→ Critic ←→ Reward 模型（PPO 时） │
└─────────────────────────────────────────┘
核心：推理引擎做 Rollout，训练引擎做更新，Ray 做分布式调度。
```

---

## 2. OpenRLHF（入门首选，B 类）

```text
定位：首个 Ray + vLLM 的高性能 RLHF 框架，工业级可用。
特点：
  - Ray 分布式调度 Actor/Critic/Reward 到不同 GPU
  - vLLM PagedAttention 加速推理
  - 支持 PPO / DPO / Rejection Sampling / GRPO
  - 最新版把 RLHF 组件统一成 Agent 架构

适用：7B–70B 中小规模、快速实验、教学。
学习建议：先跑通 PPO → 理解 RLHF 全流程 → 切 GRPO 对比稳定性。
```

---

## 3. veRL（Volcano Engine RL，字节，B→A 演进）

```text
定位：灵活、高效的大规模 RL 训练框架。
特点：
  - HybridFlow 混合控制器：推理和训练可独立扩缩容（vLLM/SGLang + Megatron/FSDP）
  - 已验证 70B+，千卡级
  - uni-agent 集成：内置统一 Agent 框架，可构建/运行/训练 LLM Agent
  - VeRL-Omni：多模态扩展

适用：大规模（70B+）、需推理/训练独立扩缩、多模态。
关键概念 HybridFlow：传统框架推理和训练耦合，扩缩容要一起动；
           HybridFlow 让两者各自弹性，训练卡等推理时不被拖死。
```

---

## 4. Slime（Agent RL 专精，A 类，GLM 系列引擎）

```text
定位：专为 Agent 时代设计的 RL 训练框架，GLM-4.5→GLM-5.2 的 RL 引擎。
核心创新｜解耦 Agent 与 RL 框架：
  Agent 框架负责：环境交互（调工具/读文件）、轨迹生成（记录 s/τ/a/r）、Rollout 管理
  RL 框架负责：策略优化（PPO/GRPO）、参数更新（Megatron）、模型管理

为什么解耦重要？
  传统（veRL/OpenRLHF）：Agent 逻辑与 RL 逻辑耦合 → 灵活差
  Slime：两者通过标准化接口通信 → 可独立升级、支持更复杂环境

RadixTree 技术：确保多轮对话中 logits 准确 → 直接解决 03 讲的 Re-tokenize 问题
Megatron 原生集成：参数透传不做中间转换 → 训练效率

适用：多轮 Agent RL（修 Bug/网页/OS）、需 Agent-RL 解耦、Megatron 分布式。
```

---

## 5. 三框架对比（含 Survey 分类）

| | OpenRLHF | veRL | Slime |
|---|---|---|---|
| Survey 分类 | B (RLHF/ft) | B→A | A (Agentic RL) |
| 调度 | Ray | HybridFlow | Ray + 自研 |
| 推理引擎 | vLLM | vLLM/SGLang | vLLM/SGLang |
| 训练引擎 | DeepSpeed/FSDP | Megatron/FSDP | Megatron |
| 多轮支持 | 基础 | 较好 | 专门优化 |
| Agent 解耦 | ❌ | 部分(uni-agent) | ✅ |
| Re-tokenize | 需自行处理 | 部分 | RadixTree 解决 |
| 验证规模 | 中小 | 大 | 百亿级 |
| 学习难度 | 低 | 中 | 高 |

---

## 6. 选型决策树

```text
你是入门/教学/小模型？
  → OpenRLHF + GRPO（最简单，文档最全）

你要 70B+ 大规模、推理训练独立扩缩？
  → veRL + HybridFlow

你做多轮 Agent（工具/网页/OS），要轨迹级 + 解耦 + Re-tokenize 稳定？
  → Slime

你想要"Agent 框架 + RL 训练"一体化？
  → veRL + uni-agent（折中方案）
```

---

## 7. 实践路线

```text
1. OpenRLHF 跑通 PPO → 看 loss/reward 曲线，理解 RLHF 流程
2. 切 GRPO → 体验"无 Critic"的简洁与稳定
3. veRL 或 Slime 试多轮任务 → 体验 Agent 解耦与环境交互
4. 自定义环境 → 给自己的任务写环境接口 + 奖励函数 → 跑通
```

---

## 8. 一句话总结

> 框架是算法落地的"基建"。OpenRLHF 适合入门，veRL 靠 HybridFlow 做大规模，
> Slime 用 Agent-RL 解耦 + RadixTree 专攻多轮 Agent——这正是 Survey §5.2 把
> "Agentic RL frameworks" 单列出来的原因：多步 POMDP 需要不同于单步 RLHF 的工程范式。
