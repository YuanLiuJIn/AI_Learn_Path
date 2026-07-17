# 02. RL 基础：RLHF、RLVR、PPO、GRPO

> 目标：理解大模型后训练中最核心的四种 RL 方法，以及它们的区别和适用场景。

## 1. 大模型后训练的 RL 全景

```text
后训练 = SFT + RL

SFT（监督微调）：
  教模型"怎么回答"
  用高质量"问-答"对训练

RL（强化学习）：
  让模型"越答越好"
  用奖励信号引导模型优化

当前趋势：SFT 越来越轻量，RL 越来越重要
```

## 2. RLHF（Reinforcement Learning from Human Feedback）

### 核心思想

用人类偏好训练一个 Reward Model，再用 RL 优化模型。

### 流程

```text
Step 1：收集偏好数据
  同一个 prompt，模型生成多个回答
  人类标注"哪个更好"
  例如：回答 A > 回答 B

Step 2：训练 Reward Model
  让一个模型学会给回答打分
  目标是让好回答分高、差回答分低

Step 3：PPO 优化
  用 PPO 算法优化主模型
  目标是让模型生成 Reward Model 打高分的回答
  同时加 KL 惩罚，防止偏离太远
```

### 优点

```text
灵活：可以捕捉人类复杂的偏好
成熟：InstructGPT/ChatGPT 验证
可迭代：收集新数据 → 更新 Reward Model → 继续训练
```

### 缺点

```text
训练复杂：需要维护 Reward Model + PPO
不稳定：PPO 训练容易崩溃
成本高：需要大量人类标注
Reward Hacking：模型可能找到 Reward Model 的漏洞
```

## 3. DPO（Direct Preference Optimization）

### 核心思想

跳过 Reward Model，直接用偏好数据优化模型。

### 核心公式直觉

```text
DPO 的 loss 本质上在做：
  让模型对"好回答"的概率更高
  让模型对"差回答"的概率更低
  同时不要偏离原始模型太远

数学上等价于隐式的 Reward Model
但不需要显式训练它
```

### 优点

```text
简单：不需要 Reward Model
稳定：不需要 PPO
高效：直接优化
```

### 缺点

```text
离线：只能在已有偏好数据上优化
分布偏移：数据分布变了可能失效
缺乏探索：不能在线收集新数据
```

## 4. RLVR（RL with Verifiable Rewards）

### 核心思想

对于有确定答案的任务（数学、代码），直接用答案正确性作为奖励。

### DeepSeek-R1 的突破

```text
核心创新：不需要人类标注的 Reward Model
只要任务有可验证的正确答案：
  数学题 → 答案对不对
  代码 → 测试过不过
  游戏 → 有没有通关

用规则判断代替 Reward Model
简单、可靠、可扩展
```

### 优点

```text
不需要人类标注：成本极低
无 Reward Hacking：规则无法被欺骗
可大规模扩展：自动生成海量训练数据
```

### 局限

```text
只适用于有明确答案的任务
开放式任务（写作、对话）不适用
```

## 5. GRPO（Group Relative Policy Optimization）

### 核心思想

DeepSeek-R1 使用的算法，PPO 的改进版。

### 和 PPO 的区别

```text
PPO：
  需要 Critic 模型（Value Function）
  需要 Reward Model
  训练复杂、不稳定

GRPO：
  不需要 Critic 模型
  对同一个 prompt 生成多个回答（Group）
  用组内相对分数作为优势估计
  更简单、更稳定
```

### 工作原理

```text
1. 对同一个 prompt 采样 N 个回答
2. 用规则/Reward Model 给每个回答打分
3. 计算组内均值和标准差
4. 回答分数高于均值 → 正优势 → 强化
5. 回答分数低于均值 → 负优势 → 抑制
6. 加上 KL 惩罚，防止偏离太远
```

### 优点

```text
不需要 Critic 模型：更简单
组内归一化：减少奖励尺度影响
稳定：比 PPO 更容易训练
```

## 6. 四种方法对比

| | RLHF | DPO | RLVR | GRPO |
|---|---|---|---|---|
| 需要 Reward Model | ✅ | ❌ | ❌ | 可选 |
| 需要 Critic | ✅ | ❌ | ❌ | ❌ |
| 需要人类标注 | ✅ | ✅ | ❌ | ❌ |
| 训练稳定性 | 低 | 高 | 高 | 较高 |
| 在线探索 | ✅ | ❌ | ✅ | ✅ |
| 适用任务 | 开放式 | 偏好数据 | 有正确答案 | 通用 |
| 代表模型 | InstructGPT | Zephyr | DeepSeek-R1 | DeepSeek-R1 |

## 7. 一句话总结

> 大模型 RL 正从"依赖人类标注的 RLHF"走向"依赖可验证奖励的 RLVR/GRPO"。GRPO 通过去掉 Critic 和组内归一化，让 RL 训练更简单、更稳定、更可扩展，是当前 Agent RL 的主流选择。
