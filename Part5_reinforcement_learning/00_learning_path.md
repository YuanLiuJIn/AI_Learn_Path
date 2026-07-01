# 00 学习路线（强化学习篇）

## 总体目标

建立从“经典表格 RL”到“深度 RL”再到“AlphaZero”的完整脉络，能讲清每种算法解决了什么问题，并能跑通至少一个实战环境（如 CartPole / LunarLander）。

## 演化与解决的问题

| 阶段 | 方法 | 解决的问题 |
|---|---|---|
| 框架 | MDP / 贝尔曼方程 | 怎么形式化“决策”问题 |
| 无模型经典 | 蒙特卡罗 / TD | 不知道环境规则也能学价值 |
| 控制 | SARSA / Q-Learning | 学到“怎么行动最好” |
| 深度化 | DQN | 状态太多，用神经网络逼近价值 |
| 策略法 | Policy Gradient / Actor-Critic | 直接学策略，处理连续动作 |
| 稳定优化 | TRPO / PPO | 让策略更新又快又稳（RLHF 用它）|
| 规划+学习 | MCTS / AlphaGo / AlphaZero | 把搜索与神经网络结合，超越人类 |

## 建议节奏（约 10 周）

```text
第1周  RL 是什么、与监督学习的区别、MDP 直觉
第2周  数学基础：状态价值、动作价值、贝尔曼方程
第3周  蒙特卡罗 与 TD
第4周  SARSA 与 Q-Learning（手写表格 RL）
第5周  DQN：用神经网络做 Q
第6周  Policy Gradient 与 Actor-Critic
第7周  TRPO → PPO
第8周  实战：LunarLander + Atari
第9周  Minimax → MCTS → AlphaGo
第10周 AlphaZero（Model-based、自我对弈）
```

## 学习原则

- RL 的核心是“延迟奖励”：现在的动作影响未来的回报，难点在于把功劳/责任分配到正确的动作上。
- 先把表格 RL（Q-Learning）在小网格世界里手推一遍，再上神经网络。
- 每个算法问三件事：学什么（价值/策略）？on-policy 还是 off-policy？怎么更新？
- 一定要跑通 Gymnasium 的 CartPole / LunarLander，纸上谈兵学不会 RL。
