# 参考资料（强化学习篇）

## 核心教材与课程（必读）

- Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed.)（RL 圣经，官网免费）。
- David Silver, UCL RL Course（经典视频课程）。
- Stanford CS234: Reinforcement Learning。
- OpenAI Spinning Up in Deep RL（动手友好的入门，强烈推荐）。

## 标准工具

- GitHub: `Farama-Foundation/Gymnasium`（环境标准）。
- GitHub: `DLR-RM/stable-baselines3`（成熟算法库，开箱即用）。
- GitHub: `vwxyzjn/cleanrl`（单文件算法实现，最适合读懂细节）。
- GitHub: `openai/spinningup`（教学实现 + 文档）。

## 01–02 基础与数学

- Sutton & Barto，第 1–4 章（RL 框架、MDP、动态规划）。
- David Silver Lecture 1–3。

## 03–04 经典 RL

- Sutton & Barto，第 5–6 章（MC、TD）。
- Watkins & Dayan, "Q-Learning", 1992。

## 05 Deep RL

- Mnih et al., "Playing Atari with Deep RL" (DQN), 2013；"Human-level control...", Nature 2015。
- Williams, "REINFORCE", 1992；Sutton et al., "Policy Gradient Methods", 2000。
- Mnih et al., "A3C", 2016。

## 06 TRPO / PPO

- Schulman et al., "TRPO", 2015；"PPO", 2017；"GAE", 2015。
- Ouyang et al., "InstructGPT"（PPO 用于 RLHF）, 2022。

## 07 实战

- GitHub: `stable-baselines3`、`cleanrl`、`Gymnasium`（LunarLander、Atari）。

## 08–10 棋类与 AlphaZero

- Silver et al., "AlphaGo", Nature 2016；"AlphaGo Zero", Nature 2017；"AlphaZero", 2017。
- Schrittwieser et al., "MuZero", 2020。
- Browne et al., "MCTS Survey", 2012。
- GitHub: `suragnair/alpha-zero-general`、`junxiaosong/AlphaZero_Gomoku`、`leela-zero/leela-zero`。

## 学习建议

1. Sutton & Barto 前 6 章 + 手写表格 Q-Learning（FrozenLake）。
2. 用 CleanRL 精读一份 PPO 单文件实现，跑通 CartPole/LunarLander。
3. 用 Stable-Baselines3 玩一个 Atari。
4. 用 `alpha-zero-general` 跑通井字棋，理解 MCTS + 自我对弈。
5. 把 PPO 与 Part4 的 RLHF、Part6 的对齐串起来理解。
