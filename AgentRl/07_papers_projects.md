# 07. 重要论文与开源项目清单

> 按学习阶段整理 Agent RL 最值得读的论文和项目。

## 阶段一：RL 基础

### 必读论文

| 论文 | 年份 | 为什么重要 |
|---|---|---|
| PPO: Proximal Policy Optimization | 2017 | RL 经典算法，RLHF 的基础 |
| Training Language Models to Follow Instructions (InstructGPT) | 2022 | RLHF 的开端 |
| DPO: Direct Preference Optimization | 2023 | 跳过 Reward Model 的替代方案 |
| DeepSeek-R1 | 2025 | GRPO + RLVR，纯 RL 训练出推理能力 |
| RLHF Survey / Post-Training Survey | 2024 | 后训练 RL 全景 |

### 推荐项目

```text
OpenRLHF：入门首选，跑通第一个 RLHF 训练
TRL (HuggingFace)：最简单，适合小规模实验
```

## 阶段二：多轮 Agent RL

### 必读论文

| 论文 | 年份 | 为什么重要 |
|---|---|---|
| AgentRL: Scaling Agentic RL | 2025 | 全异步多轮 Agent RL，超越 GPT-5 |
| A Practitioner's Guide to Multi-turn Agentic RL | 2025 | 多轮 RL 实践指南 |
| RAGEN + StarPO | 2025 | 轨迹级 Agent RL 框架 |
| AgentGym-RL | 2025 | 长程决策 Agent RL |
| MUA-RL | 2025 | 多轮用户交互 Agent RL |

### 推荐项目

```text
veRL + uni-agent：构建和训练 LLM Agent
Slime：GLM 系列的 RL 引擎，Agent 解耦设计
```

## 阶段三：奖励与环境

### 必读论文

| 论文 | 年份 | 为什么重要 |
|---|---|---|
| AgentPRM: Process Reward Models | 2025 | 过程奖励模型 |
| SWE-bench | 2023 | 代码 Agent 评测基准 |
| WebArena | 2024 | Web Agent 评测基准 |
| AgentBench | 2023 | 多维 Agent 评测 |

## 阶段四：前沿方向

### 关注方向

```text
1. 并行化 Agent RL
   让 Agent 学会并行思考、并行调用工具

2. 长程任务 RL
   从几十步到几百步的 Agent 训练

3. 多模态 Agent RL
   视觉 + 语言的 Agent RL 训练

4. Agent RL Scaling Law
   更多数据、更大模型、更复杂环境 → 更强 Agent？
```

## 推荐实践路线

```text
实践 1：用 OpenRLHF + GRPO 训练一个数学 Agent
  任务：解数学题
  奖励：答案正确性
  理解 RLVR 的工作方式

实践 2：用 veRL 训练一个代码 Agent
  任务：修 SWE-bench 的 Bug
  奖励：测试通过率
  理解多轮 RL 的挑战

实践 3：自定义环境
  设计自己的 Agent 任务
  定义奖励函数
  跑通训练

实践 4（进阶）：用 Slime 训练 UE5 测试 Agent
  任务：自动生成和执行测试用例
  奖励：测试通过率 + 性能表现
  理解 Agent 解耦的价值
```
