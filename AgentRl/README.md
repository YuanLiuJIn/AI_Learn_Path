# Agent RL 学习专题

> 目标：系统学习如何用强化学习（RL）训练出能自主使用工具、完成多轮复杂任务的 AI Agent。

## 一句话定义

Agent RL 不是传统的"在固定环境里学走路"的强化学习，而是：

```text
用强化学习训练大语言模型，让它学会在多轮交互中
自主规划、调用工具、观察环境反馈、修正策略，
最终成长为能独立完成复杂任务的 Agent。
```

## 核心问题

```text
Chatbot 时代：模型只会"说话"，不会"做事"
SFT 时代：教模型模仿人类行为，但上限受限于数据质量
Agent RL 时代：让模型在真实环境中试错、获得奖励、自主进化

关键转变：
  从"模仿人类" → 到"超越人类"
  从"单轮问答" → 到"多轮工具调用"
  从"静态数据" → 到"动态环境交互"
```

## 文件结构

| 文件 | 内容 |
|---|---|
| `00_learning_path.md` | 学习路线与前置知识 |
| `01_agent_rl_overview.md` | Agent RL 概述：范式转移、核心概念 |
| `02_rl_foundations.md` | RL 基础：RLHF、RLVR、PPO、GRPO |
| `03_multi_turn_agent_rl.md` | 多轮 Agent RL：AgentRL、RAGEN、AgentGym-RL |
| `04_rl_frameworks.md` | 开源框架：OpenRLHF、veRL、Slime |
| `05_reward_design.md` | 奖励设计：Outcome Reward、Process Reward、Rule-based |
| `06_environment_and_benchmark.md` | 环境与评测：SWE-bench、WebArena、AgentBench |
| `07_papers_projects.md` | 重要论文、开源项目清单 |
| `references.md` | 参考资料索引 |
