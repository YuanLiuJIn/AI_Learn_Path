# 00. Agent RL 学习路线

> 目标：从 RL 基础到多轮 Agent RL 训练，建立系统认知。

## 1. 推荐学习顺序

```text
第一阶段：理解"为什么需要 Agent RL"
  → 01_agent_rl_overview.md
  搞清楚 Chatbot → SFT Agent → RL Agent 的进化逻辑

第二阶段：掌握 RL 基础算法
  → 02_rl_foundations.md
  理解 PPO、RLHF、RLVR、GRPO 的核心区别

第三阶段：深入多轮 Agent RL
  → 03_multi_turn_agent_rl.md
  理解多轮任务中 RL 的特殊挑战和解决方案

第四阶段：动手实践
  → 04_rl_frameworks.md
  选一个开源框架跑通 RL 训练流程

第五阶段：奖励设计与环境
  → 05_reward_design.md
  → 06_environment_and_benchmark.md
  理解奖励设计哲学和评测体系

第六阶段：前沿论文
  → 07_papers_projects.md
  跟进最新 Agent RL 论文
```

## 2. 前置知识

建议先掌握：

```text
强化学习基础：MDP、Policy、Value Function、Reward
大模型训练基础：SFT、RLHF、DPO
Agent 基础：ReAct、工具调用、Agent Loop
```

如果还没学过，建议先看 `AI_Learn_Path/Part5_reinforcement_learning/` 和 `AI_Learn_Path/Agent/`。

## 3. 学习原则

```text
1. 先理解"为什么 RL 能突破 SFT 上限"，再学具体算法
   关键是理解"探索-验证-再探索"的飞轮机制

2. 带着对比思维学习
   RLHF vs DPO vs GRPO 各有什么优势和局限？
   单轮 RL vs 多轮 RL 有什么区别？

3. 关注工程实践
   Agent RL 不只是算法，更是 Infra 问题
   Ray、vLLM、Megatron 的协同至关重要

4. 先跑通一个小 demo，再深入理论
   用 OpenRLHF 跑一个简单的 RLHF 训练
   再尝试多轮任务
```
