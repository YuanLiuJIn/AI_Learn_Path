# 11. 结合 KM 实践补充：从 PPO/DPO/GRPO 到 Agentic-RL

> 本章把 KM 中关于 PPO、DPO、GRPO、Agentic-RL、Verl 框架等内容，整理为 Part5 的直接学习补充。

---

## 1. RLHF：让模型从“会答”变成“答得像人喜欢”

可以把大模型训练分成三步：

```text
预训练：模型学会语言和知识
SFT：模型学会按指令回答
RLHF：模型学会人类更喜欢什么样的回答
```

KM 中的偏好对齐文章用了“小狗抓球”类比：

```text
状态：小狗当前看到球和主人
动作：小狗选择去不去抓球
奖励：抓对了主人奖励，抓错了没有奖励
策略：小狗逐渐学会什么时候该抓球
```

对应到 LLM：

```text
状态：prompt + 上下文
动作：模型生成的回答
奖励：人类偏好 / 奖励模型 / 规则奖励
策略：模型参数
```

---

## 2. PPO、DPO、GRPO 的直觉对比

### 2.1 PPO：老师打分 + 小步更新

PPO 流程：

```text
模型生成回答
奖励模型打分
用策略梯度更新模型
用 KL 约束防止模型偏离太远
```

核心思想：

```text
更新可以，但不能一下子偏太远。
```

缺点：

```text
需要奖励模型
需要 Critic/Value 网络
训练复杂、显存开销大
```

### 2.2 DPO：两两偏好直接优化

DPO 不训练奖励模型，而是直接用偏好对：

```text
prompt
chosen answer
rejected answer
```

目标：

```text
提高 chosen 的概率
降低 rejected 的概率
```

优点：流程简单。

缺点：依赖高质量偏好数据，不适合需要在线探索的任务。

### 2.3 GRPO：组内比较，不要 Critic

GRPO 对同一个 prompt 生成多个候选：

```text
o1, o2, ..., oN
```

给每个候选打奖励：

```text
r1, r2, ..., rN
```

计算相对优势：

```text
A_i = (r_i - mean(r)) / std(r)
```

直觉：

```text
比组内平均好 → 强化
比组内平均差 → 弱化
```

优势：

```text
不需要 Critic
显存更省
适合规则奖励明确的任务
```

---

## 3. Agentic-RL：从“写说明书”到“让 Agent 练出来”

Prompt Engineering 像给 Agent 写说明书：

```text
遇到 A 做 B，遇到 C 做 D。
```

Agentic-RL 像让 Agent 反复实践：

```text
任务 → 尝试 → 工具调用 → 得到结果 → 奖励/惩罚 → 更新策略
```

### 3.1 为什么 Agent 任务更适合 RL？

Agent 任务天然有环境和反馈：

```text
写代码 → 跑测试 → 通过/失败
操作 GUI → 最终任务是否完成
查资料 → 答案是否命中事实
玩游戏 → 得分高低
```

这些反馈可以变成奖励函数。

### 3.2 两阶段训练范式

```text
阶段 1：SFT 冷启动
  - 学会基本格式
  - 学会工具调用语法
  - 学会基本任务模式

阶段 2：RL / GRPO
  - 用奖励信号优化策略
  - 超越 SFT 数据上限
  - 学会纠错、规划、探索
```

伪代码：

```python
# SFT: 模仿专家轨迹
model = sft_train(model, expert_trajectories)

# RL: 让模型自己实践
for task in tasks:
    trajectories = [rollout(model, task) for _ in range(G)]
    rewards = [reward_fn(traj) for traj in trajectories]
    advantages = normalize(rewards)
    model = grpo_update(model, trajectories, advantages)
```

---

## 4. 奖励函数设计原则

KM 中 Agentic-RL 文章强调：奖励函数是连接人类意图和模型行为的桥梁。

好的奖励函数应具备四点：

```text
1. 可验证性：能自动判断对错
2. 多维度覆盖：准确率、格式、效率、安全都要考虑
3. 稠密性：不要只在最后给一个 0/1，尽量给中间信号
4. 鲁棒性：防止奖励黑客（模型钻规则空子）
```

示例：代码 Agent 的奖励函数：

```python
def reward_code_agent(trajectory):
    reward = 0
    if tests_pass(trajectory.patch):
        reward += 1.0
    if lint_pass(trajectory.patch):
        reward += 0.2
    if patch_is_small(trajectory.patch):
        reward += 0.1
    if touches_forbidden_files(trajectory.patch):
        reward -= 2.0
    if introduces_security_risk(trajectory.patch):
        reward -= 3.0
    return reward
```

---

## 5. Verl 框架：GRPO 的工程落地

Verl 是大模型强化学习训练框架，适合做 RLHF / GRPO / RLVR。

GRPO 工程训练常见难点：

```text
多候选 rollout 成本高
奖励计算要并行
FSDP / ZeRO 要和 RL 采样配合
长上下文下 Attention Sink 等模型结构需要适配
```

工程经验：

```text
1. 先用小模型和小数据验证奖励函数
2. 再扩大 rollout 并行度
3. 训练时监控 KL、reward、response length
4. 防止 reward hacking 和过度思考
5. 保存每轮 rollout 轨迹，便于 debug
```

---

## 6. 学完 Part5 后应形成的现代 RL 认知

```text
1. 强化学习不是只用来玩游戏，也已经成为大模型后训练核心方法。
2. PPO 稳但重，DPO 简但依赖偏好数据，GRPO 省显存且适合可验证任务。
3. Agentic-RL 的关键不是算法名字，而是环境、奖励函数和 rollout 质量。
4. SFT 负责冷启动，RL 负责突破模仿数据上限。
5. 奖励函数设计不好，模型会学会“钻空子”而不是完成任务。
```

---

## 参考来源

本文综合整理自 KM 中 PPO/DPO/GRPO 偏好对齐科普、无需 RL 基础理解 PPO/GRPO、Agentic-RL 全面解析、GRPO+Verl 工程实践、Tree-GRPO、Attention Sink RL Recipe 等文章。
