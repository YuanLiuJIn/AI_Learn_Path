# 05 DeepRL：价值网络、策略网络与 Actor-Critic

## 1. 它解决什么问题

表格 Q-Learning 在状态爆炸时失效（围棋、Atari 像素）。深度强化学习（Deep RL）的核心思想：

> 用神经网络来**逼近**价值函数或策略，从而处理高维、连续的状态空间。

三条主线：价值网络（DQN）、策略网络（Policy Gradient）、两者结合（Actor-Critic）。

## 2. 价值网络：DQN

### 一句话直觉

> 把 Q-Learning 里的“Q 表格”换成一个神经网络：输入状态（如游戏画面），输出每个动作的 Q 值。

```text
表格 Q：Q[s][a]
DQN：  神经网络 Q_θ(s) -> [Q(s,a1), Q(s,a2), ...]
```

### 两个关键技巧（让训练稳定）

DQN（DeepMind 2013/2015，玩 Atari 超越人类）的成功靠两招：

```text
1. 经验回放 (Experience Replay)：
   把交互产生的 (s,a,r,s') 存进一个大池子，训练时随机抽 batch。
   作用：打破数据时间相关性，重复利用数据（off-policy 才能这么做）。

2. 目标网络 (Target Network)：
   用一个"慢更新"的网络算 TD 目标，隔一段时间才同步。
   作用：避免"自己追自己"导致的训练发散。
```

### 损失（就是 TD 误差的 MSE）

```text
Loss = E[ ( r + γ·max_a' Q_target(s',a') - Q_θ(s,a) )² ]
```

## 3. 策略网络：Policy Gradient

### 为什么需要它

DQN 适合**离散动作**（上/下/开火）。但很多任务是**连续动作**（方向盘转 23.5°、关节力矩）。而且有时我们想直接学“策略”而非价值。

### 一句话直觉

> 直接用神经网络表示策略 π_θ(a|s)（输入状态，输出动作概率/分布）。哪个动作带来高回报，就调高它的概率；带来低回报，就调低。

### 策略梯度定理（核心公式，直觉版）

```text
∇J(θ) = E[ ∇log π_θ(a|s) · G ]
              └提高/降低该动作概率┘ └回报作为权重┘

回报 G 高的动作 -> 梯度推高它的概率
回报 G 低的动作 -> 梯度压低它的概率
```

REINFORCE 是最基础的策略梯度算法（用整局回报 G 做权重）。

### 问题：方差大

用整局回报 G 当权重，噪声很大，训练不稳。怎么降方差？→ 引入“基准线”，这就走向 Actor-Critic。

## 4. Actor-Critic：两者结合

### 一句话直觉

> 一个网络当“演员（Actor）”负责选动作（策略），一个网络当“评论家（Critic）”负责打分（价值）。演员根据评论家的反馈改进表演。

```text
Actor（策略网络 π_θ）：决定做什么动作
Critic（价值网络 V_w）：评估这个状态/动作有多好

用 Critic 的估计替代"整局回报 G"，大幅降低方差。
```

### 优势函数（Advantage）

关键概念，衡量“某动作比平均水平好多少”：

```text
A(s,a) = Q(s,a) - V(s)
         └该动作的价值┘ └该状态的平均价值┘

A > 0：这个动作比平均好 -> 提高其概率
A < 0：比平均差 -> 降低其概率
```

Actor 用优势 A 替代回报 G 来更新，比纯策略梯度稳得多。常见实现 A2C / A3C。

## 5. 三条路线总结

| 方法 | 学什么 | 动作类型 | 代表 |
|---|---|---|---|
| 价值法 | Q(s,a) | 离散 | DQN |
| 策略法 | π(a|s) | 离散/连续 | REINFORCE |
| Actor-Critic | 策略 + 价值 | 离散/连续 | A2C、PPO（下一章）|

```text
价值法：    只学"每个动作多好"，再选最好的（间接得到策略）
策略法：    直接学"该怎么做"，但方差大
Actor-Critic：策略法 + 用价值法降方差 -> 现代主流（PPO 就属于此类）
```

## 6. 代码直觉（Actor-Critic 更新骨架）

```python
# actor: π_θ(a|s)  critic: V_w(s)
logits = actor(state); value = critic(state)
dist = torch.distributions.Categorical(logits=logits)
action = dist.sample()

# 与环境交互得到 reward, next_state
td_target = reward + gamma * critic(next_state).detach()
advantage = (td_target - value).detach()       # 优势

actor_loss  = -dist.log_prob(action) * advantage   # 策略梯度（用优势加权）
critic_loss = (td_target - value) ** 2             # 价值回归
loss = actor_loss + critic_loss
loss.backward(); optimizer.step()
```

## 经典论文与开源项目

- Mnih et al., "Playing Atari with Deep RL" (DQN), 2013；"Human-level control...", 2015。
- Sutton et al., "Policy Gradient Methods", 2000；Williams, "REINFORCE", 1992。
- Mnih et al., "Asynchronous Methods for Deep RL" (A3C), 2016。
- GitHub: `DLR-RM/stable-baselines3`、`vwxyzjn/cleanrl`（单文件清晰实现，强烈推荐）。

## 本章小结

Deep RL 用神经网络逼近价值或策略。DQN 用经验回放 + 目标网络把 Q-Learning 神经网络化，攻克 Atari；Policy Gradient 直接学策略、能处理连续动作但方差大；Actor-Critic 用“评论家”的价值估计（优势函数）给“演员”降方差，是现代主流框架。下一章的 PPO 正是在此基础上让更新更稳。
