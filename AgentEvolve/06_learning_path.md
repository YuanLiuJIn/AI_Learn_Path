# 06. 学习路线：从入门到前沿

## 四阶段渐进学习

```text
阶段 1：记忆驱动自进化（1-2 周）
  目标：理解 Agent 如何从经验中积累知识
  论文：Generative Agents (2023)
  要点：Memory Stream + Reflection + Planning
  动手：实现一个简单的"对话记忆 + 反思"模块

阶段 2：技能驱动自进化（2-3 周）
  目标：理解 Agent 如何自动发现和复用可执行技能
  论文：Voyager (2023)
  开源：github.com/MineDojo/Voyager
  要点：自动课程 + 技能库 + 迭代提示
  动手：实现一个简单技能库，让 Agent 记住并复用成功操作

阶段 3：RL 驱动自进化（3-4 周）
  目标：理解如何用 GRPO/RL 训练 Agent 的决策能力
  论文：SkillRL (2026)、SAGE (2025)
  要点：技能自动发现 + 递归进化 + 技能组合优化
  动手：基于 GRPO 训练 Agent 学会"选择合适的技能组合"

阶段 4：元认知自进化（2-3 周）
  目标：理解 Agent 如何学会"学习本身"
  论文：AgentEvolver (2025)、ADAS (2025)
  开源：github.com/alibaba/AgentEvolver
  要点：自我提问 + 自我导航 + 自我归因 + 架构自动搜索
  动手：运行 AgentEvolver，体验 Agent 自进化的完整流程
```

## 核心论文阅读顺序

```text
必读（4 篇）：
  1. Generative Agents (2023) — 自进化的经典范式
  2. Voyager (2023) — 技能库 + 终身学习
  3. AgentEvolver (2025) — 自我提问/导航/归因
  4. Self-Evolving Agents Survey (2025) — 全景综述

选读（3 篇）：
  5. SkillRL (2026) — 技能自动发现
  6. SAGE (2025) — 技能增强 GRPO
  7. ADAS (2025) — 架构自动搜索
```

## 动手实践顺序

```text
1. 跑通 AgentEvolver（最完整的自进化系统）
   github.com/alibaba/AgentEvolver

2. 玩 Voyager 的 Minecraft 世界
   github.com/MineDojo/Voyager
   （需要 Minecraft Java Edition）

3. 自己实现一个简化版：
   - 自进化课程生成（自我提问）
   - 经验检索（自我导航）
   - 细粒度奖励（自我归因）
   - 技能库自动构建
```

## 简历项目方向

```text
方向 1：AgentEvolver 改进
  "基于 AgentEvolver 框架，针对 xx 场景实现 Agent 自进化，
   任务完成率从 xx% 提升至 xx%"

方向 2：技能自动发现系统
  "基于 SkillRL 思路，设计 Agent 技能自动发现与递归进化系统"

方向 3：自进化课程生成
  "设计 Agent 自进化训练框架，包含自动课程生成、经验复用、
   细粒度归因，在 xx 任务上 14B 模型超越 32B 基线"

方向 4：Meta Agent 架构搜索
  "基于 ADAS 思路，实现 Agent 架构自动搜索与评估系统"
```
