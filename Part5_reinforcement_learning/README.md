# Part5_reinforcement_learning：强化学习篇

本部分讲清楚“智能体如何通过试错、与环境交互来学会决策”。强化学习（RL）是 AlphaGo、游戏 AI、机器人控制的核心，也是大模型对齐（RLHF）的基础——把 Part4 的 InstructGPT 那条线真正补全。

## 主线

```text
RL 基本框架（MDP）
   │
   ├── 不用神经网络的经典 RL：
   │     蒙特卡罗 / TD ──> SARSA / Q-Learning
   │
   ├── 深度强化学习（Deep RL）：
   │     DQN（价值网络）──> Policy Gradient（策略网络）──> Actor-Critic
   │     ──> TRPO ──> PPO（现代主力，也用于 RLHF）
   │
   └── 棋类与规划：
         Minimax ──> MCTS ──> AlphaGo ──> AlphaZero（Model-based）
```

## 章节顺序

1. `01_rl_intro.md`：强化学习基础入门
2. `02_rl_math.md`：强化学习数学基础（MDP、价值、贝尔曼方程）
3. `03_monte_carlo_td.md`：基础 RL（上）——蒙特卡罗与 TD
4. `04_sarsa_qlearning.md`：基础 RL（下）——SARSA 与 Q-Learning
5. `05_deeprl_actor_critic.md`：DeepRL——价值网络、策略网络与 Actor-Critic
6. `06_trpo_ppo.md`：RL 优化算法基石——从 TRPO 到 PPO
7. `07_rl_practice.md`：RL 实战——月球车降落与 Atari
8. `08_minimax_to_alphago.md`：棋类 AI——从 Minimax 到 AlphaGo
9. `09_modelbased_alphazero.md`：Model-based RL 与再谈 AlphaZero
10. `10_alphazero_training.md`：AlphaZero 训练（完结篇）
11. `references.md`：论文、教材与开源项目

## 前置要求

- Part1：概率、期望、梯度下降、神经网络。
- Part2：用神经网络逼近函数（DeepRL 用到）。
- 名词查 `glossary.md`。

## 学完后应达到

- 能用 MDP（状态、动作、奖励、策略、价值）描述一个决策问题。
- 能区分蒙特卡罗与 TD、on-policy（SARSA）与 off-policy（Q-Learning）。
- 能讲清 DQN、Policy Gradient、Actor-Critic 各自在学什么。
- 能解释 PPO 为什么稳定、为什么被广泛使用（含 RLHF）。
- 能讲清 AlphaGo / AlphaZero 如何把 MCTS 与神经网络结合。
