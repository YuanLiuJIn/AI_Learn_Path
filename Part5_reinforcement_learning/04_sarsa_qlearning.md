# 04 基础 RL（下）：SARSA 与 Q-Learning

## 1. 从“评估”到“控制”

上一章用 MC/TD 估计价值（预测）。本章要更进一步——**控制**：不仅评估，还要学出**最优策略**。两个经典算法：SARSA 和 Q-Learning，都基于 TD，但学的是动作价值 Q(s,a)。

为什么学 Q 而不是 V？因为有了 Q(s,a)，选动作很直接：选 Q 最大的那个动作即可，不需要知道环境模型。

## 2. SARSA：on-policy

名字来自更新用到的五元组：`(S, A, R, S', A')`。

```text
Q(s,a) ← Q(s,a) + α·[ r + γ·Q(s', a') - Q(s,a) ]
                              └ a' 是实际按当前策略选的下一个动作 ┘
```

关键：`a'` 是**智能体实际会执行的下一个动作**（按当前策略，比如 ε-greedy 选的）。

> SARSA 学的是“我实际在用的这套策略”的价值——所以叫 on-policy（同策略）。

## 3. Q-Learning：off-policy

```text
Q(s,a) ← Q(s,a) + α·[ r + γ·max_{a'} Q(s', a') - Q(s,a) ]
                              └ 直接取下一状态的最优动作 ┘
```

关键：用 `max` 取下一状态**最好**的动作价值，而不管实际会不会选它。

> Q-Learning 直接学“最优策略”的价值，即使行为上还在探索——所以叫 off-policy（异策略）。

## 4. 一字之差，性格不同

```text
SARSA：    r + γ·Q(s', a')        a' = 实际选的动作（含探索）
Q-Learning：r + γ·max_a' Q(s',a')  取最优动作（不含探索的影响）
```

经典对比例子——“悬崖行走”（Cliff Walking）：

```text
有一条最短路紧贴悬崖（走错一步掉下去，大负奖励）。
Q-Learning：学到贴着悬崖的最优最短路（但训练中因探索偶尔掉崖）—— 激进
SARSA：    学到离悬崖远一点的安全路（因为它把"探索可能掉崖"算进了价值）—— 保守
```

直觉：

```text
Q-Learning：理想主义者，学"最优路线"，不管自己手抖
SARSA：     现实主义者，考虑"我会探索/手抖"，学更安全的路线
```

## 5. on-policy vs off-policy（重要概念）

| | on-policy（SARSA）| off-policy（Q-Learning）|
|---|---|---|
| 学的策略 | 就是正在执行的策略 | 最优策略（与行为策略不同）|
| 能否复用旧数据 | 难 | 能（可用经验回放）|
| 风格 | 保守、考虑探索风险 | 激进、追求最优 |
| 后续影响 | 多数 on-policy 方法（如 PPO）| DQN 基于它（经验回放）|

off-policy 能复用历史数据，这正是后面 DQN 用“经验回放池”的前提。

## 6. Q-Learning 完整代码（表格版，可直接跑）

```python
import numpy as np, gymnasium as gym

env = gym.make("FrozenLake-v1", is_slippery=False)
Q = np.zeros((env.observation_space.n, env.action_space.n))
alpha, gamma, eps = 0.1, 0.99, 0.1

for episode in range(2000):
    s, _ = env.reset()
    done = False
    while not done:
        # ε-greedy：探索 vs 利用
        a = env.action_space.sample() if np.random.rand() < eps else np.argmax(Q[s])
        s2, r, term, trunc, _ = env.step(a)
        done = term or trunc
        # Q-Learning 更新（用 max）
        Q[s, a] += alpha * (r + gamma * np.max(Q[s2]) - Q[s, a])
        s = s2

# 用学到的 Q 贪心选动作即为最优策略
policy = np.argmax(Q, axis=1)
print(policy)
```

把 `np.max(Q[s2])` 换成 `Q[s2, a2]`（a2 用 ε-greedy 选）就变成 SARSA。

## 7. 表格法的局限 → 引出 DQN

```text
表格 Q 要为每个 (状态, 动作) 存一个值。
围棋状态约 10^170 种，Atari 画面是高维像素 —— 表格根本存不下。
解决：用神经网络来逼近 Q(s,a) —— 这就是下一章的 DQN（深度强化学习）。
```

## 经典教材与开源项目

- Watkins, "Q-Learning", 1992。
- Sutton & Barto, *RL: An Introduction*，第 6 章。
- GitHub: `Farama-Foundation/Gymnasium`（FrozenLake/CliffWalking 环境）。

## 本章小结

SARSA（on-policy）用“实际会执行的下一个动作”更新，学到考虑探索风险的保守策略；Q-Learning（off-policy）用“下一状态的最优动作”更新，直接学最优策略。一字之差（`Q(s',a')` vs `max Q(s',a')`）带来不同性格。表格法因状态爆炸无法扩展到复杂问题，由此引出用神经网络逼近的深度强化学习。
