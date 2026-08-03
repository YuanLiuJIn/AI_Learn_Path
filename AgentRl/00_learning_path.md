# 00. Agent RL 学习路线（论文驱动版）

> 目标：从"读得懂论文"到"训得动 Agent"。本路线强调：**先建立统一的框架概念，再读代表论文，最后动手**。

## 1. 推荐学习顺序

```text
阶段 0｜建立统一语言（最重要，别跳过）
  → 01_agent_rl_overview.md（MDP vs POMDP 形式化）
  → 01b_Landscape_Survey_详解.md（总纲综述逐章讲解）
  目的：搞懂"Agentic RL 到底在解决什么"，以及 Survey 的
        "能力 × 任务"双重分类法，后面所有论文都挂在这张地图上

阶段 1｜夯实 RL 算法
  → 02_rl_foundations.md
  要求：能手写出 PPO / DPO / GRPO 的目标函数区别
        知道 DAPO/GSPO/Dr.GRPO 各自改了什么

阶段 2｜深入多轮训练
  → 03_multi_turn_agent_rl.md
  要求：说清 AgentRL / RAGEN / AgentGym-RL 解决的核心痛点
        理解 Re-tokenize、变长 episode、轨迹过滤

阶段 3｜跑通框架
  → 04_rl_frameworks.md → 选一个跑 demo

阶段 4｜奖励与环境
  → 05_reward_design.md → 06_environment_and_benchmark.md
  要求：能为一个真实任务设计 outcome + process 奖励

阶段 5｜读论文、跟前沿
  → 07_papers_projects.md（按分类选读）→ references.md（追新）
```

## 2. 前置知识自查

```text
❑ 强化学习基础：MDP、Policy、Value、Reward、Credit Assignment
   推荐：Part5_reinforcement_learning/ 或 Sutton & Barto 前 3 章

❑ 大模型后训练：SFT、RLHF、DPO 的基本流程
   推荐：Part6_building_llm/ 或 InstructGPT 论文

❑ Agent 基础：ReAct、Tool Calling、Agent Loop、MCP
   推荐：Agent系统设计/ 或 ReAct (Yao et al. 2022) 论文

❑ 一点工程常识：Ray / vLLM / 分布式训练的基本概念（读 04 时补充即可）
```

## 3. 怎么"读论文"才学得到东西（本专题的方法论）

不要只读摘要。按这个模板拆解每篇论文：

```text
读一篇 Agent RL 论文的 6 问：
1. 它把 Agent 建模成什么？单步 MDP 还是多步 POMDP？
2. 它的 Action Space 是什么？纯文本 / 工具调用 / GUI 操作？
3. Reward 从哪来？可验证规则 / Reward Model / 过程奖励？
4. 它用哪个算法？PPO / GRPO / DPO / 自研？
5. 它解决了哪个具体痛点？（稳定性？信用分配？环境？）
6. 在 Survey 的哪一类下？（能力视角？任务视角？）
```

## 4. 学习原则

```text
1. 先建框架，再塞细节
   Survey 的双重分类法就是你的"文件夹结构"，
   每读一篇论文就归到某个能力/任务下，知识才不会散。

2. 带着"对比"读书
   PPO vs GRPO、Outcome vs Process、单步 vs 多步、
   OpenRLHF vs veRL vs Slime ——对比让概念更锋利。

3. 读原文，不只读二手
   本专题给的讲解是"导读"，真正吸收要靠你点开 arxiv 链接读 §Method。

4. 先跑通小 demo，再钻理论
   用 OpenRLHF + GRPO 跑一个数学题 Agent，
   看到 reward 曲线涨起来，理论才有锚点。
```
