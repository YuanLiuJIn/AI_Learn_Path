# Agent RL 学习专题（论文驱动版）

> 目标：用**论文原文 + 形式化推导 + 可运行思路**的方式，系统搞懂「如何用强化学习训练出能自主规划、调用工具、在多轮交互中完成复杂任务的 LLM Agent」。
>
> 本专题的「总纲」是这篇综述：**The Landscape of Agentic Reinforcement Learning for LLMs: A Survey**（Zhang et al., arXiv:2509.02547，已发表在 TMLR）。它把零散的 Agent RL 工作统一到 POMDP 框架和「能力 × 任务」双重分类法下，是入门最好的地图。建议先读 `01b_Landscape_Survey_详解.md`。

## 这个专题和旧版的区别

旧版内容「太提纲、学不到东西」。新版的补强：

```text
1. 以一篇权威 Survey 作为骨架
   → 所有概念都挂到 Landscape Survey 的分类法上，不再是孤立点

2. 每个概念都配「代表论文 + 它解决了什么」
   → 不只讲"是什么"，更讲"谁提出的、怎么做的、为什么有效"

3. 补上形式化与伪代码
   → MDP vs POMDP、PPO/DPO/GRPO 的目标函数、多轮优势估计

4. 强调"读论文"而不是"读二手总结"
   → 07 给出按能力/任务组织的论文清单，可直接作为精读路线
```

## 一句话定义（来自 Survey 的核心论点）

> **Agentic RL** 是一种范式转移：把 LLM 从"被动的序列生成器"重新定义为"嵌入复杂、动态世界中的自主决策 Agent"。其核心论点是——**强化学习是把规划、工具使用、记忆、推理、自我改进、感知这些能力，从"静态启发式模块"变成"自适应、鲁棒 Agent 行为"的关键机制。**

## 文件结构（建议阅读顺序）

| 顺序 | 文件 | 内容 | 关键论文 |
|---|---|---|---|
| 0 | `00_learning_path.md` | 学习路线、前置知识、怎么读论文 | — |
| 1 | `01_agent_rl_overview.md` | **概念基石：单步 MDP（LLM-RL） vs POMDP（Agentic RL）** | Landscape Survey §2 |
| 2 | `01b_Landscape_Survey_详解.md` | **逐章吃透这篇总纲综述** | Landscape Survey 全文 |
| 3 | `02_rl_foundations.md` | RL 算法全家桶：REINFORCE/PPO/DPO/GRPO + 各自变体族 | PPO, DPO, GRPO, DAPO… |
| 4 | `03_multi_turn_agent_rl.md` | 多轮 Agent RL 框架与代表论文 | AgentRL, RAGEN/StarPO, AgentGym-RL |
| 5 | `04_rl_frameworks.md` | 开源训练框架的分类与选型 | OpenRLHF, veRL, Slime |
| 6 | `05_reward_design.md` | 奖励设计的理论与方法族 | RLVR, EPO, ThinkRM, AgentPRM, ASPO |
| 7 | `06_environment_and_benchmark.md` | 环境/基准的分类（对照 Survey §5.1） | SWE-bench, WebArena, OSWorld |
| 8 | `07_papers_projects.md` | 按"能力 × 任务"组织的论文精读清单 | 500+ works 精选 |
| 9 | `references.md` | 参考资料索引（含论文链接） | — |

## 三条必须建立的核心直觉

```text
直觉 1：Agentic RL 的本质是 POMDP，不是单步 MDP
  传统 RLHF 是"生成一次 → 给一个分"（T=1）
  Agentic RL 是"多步交互 → 部分观测 → 长期回报"（T>1, POMDP）
  → 这带来信用分配、部分可观测、环境非平稳三大新难题

直觉 2：奖励信号决定 Agent 能学到什么
  RLVR（可验证奖励）是当前最可靠的燃料
  Process Reward 解决稀疏奖励，但引入 Reward Model
  → 奖励设计是 Agent RL 的"指挥棒"

直觉 3：框架工程决定能不能跑起来
  Agent RL = RL 算法 × 高并发沙箱环境 × 推理/训练解耦
  选 OpenRLHF（入门）/ veRL（大规模）/ Slime（多轮 Agent）
```

## 最小可行动建议

```text
Week 1：读 01 → 01b → 02，建立 POMDP + 算法家族认知
Week 2：读 03 → 04，理解多轮训练与框架，跑通一个 GRPO demo
Week 3：读 05 → 06，动手给自己的任务设计奖励和环境
Week 4：按 07 精读 5~10 篇代表论文，跟进最新工作
```
