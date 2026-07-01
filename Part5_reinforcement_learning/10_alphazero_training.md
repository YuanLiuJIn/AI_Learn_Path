# 10 略有遗憾的 AlphaZero 训练（完结篇）

> 本章动手复现一个迷你 AlphaZero，并诚实记录“略有遗憾”——业余条件下复现 AlphaZero 的真实困难。

## 1. 目标与现实

```text
目标：在一个小棋（如井字棋 / 五子棋 / 黑白棋）上，从零训练出 AlphaZero 风格的 AI
现实：核心算法不难复现；但要达到论文级强度，算力是普通人难以承受的
      （AlphaZero 用了数千 TPU）。所以本章追求"跑通 + 理解"，而非"超越人类"。
```

## 2. 迷你 AlphaZero 的组成

```text
1. 游戏逻辑：合法走法、落子后局面、胜负判定（井字棋最简单）
2. 神经网络：双头（策略 + 价值），小棋用小 CNN 即可
3. MCTS：用网络引导的蒙特卡罗树搜索
4. 自我对弈：生成训练数据 (s, π, z)
5. 训练循环：用数据训练网络，迭代变强
6. 评估：新网络 vs 旧网络对战，胜率高才替换
```

## 3. 训练主循环（伪代码）

```python
net = PolicyValueNet()          # 双头网络

for iteration in range(N):
    # 1. 自我对弈，收集数据
    data = []
    for _ in range(num_selfplay_games):
        data += self_play_one_game(net)   # 返回若干 (state, mcts_pi, winner_z)

    # 2. 训练网络：让 p→π(MCTS结果)，v→z(对局结果)
    for batch in make_batches(data):
        p, v = net(batch.states)
        loss = cross_entropy(p, batch.pi) + mse(v, batch.z)
        loss.backward(); optimizer.step()

    # 3. 评估：新网络 vs 旧网络
    if win_rate(new=net, old=best_net) > 0.55:
        best_net = copy(net)              # 更强才替换
```

```python
def self_play_one_game(net):
    game, states_pis = new_game(), []
    while not game.over():
        pi = mcts_search(game.state, net, n_sim=200)  # MCTS 用网络引导
        states_pis.append((game.state, pi))
        move = sample(pi)                  # 按搜索分布走（前期加噪声促探索）
        game.play(move)
    z = game.result()                      # 最终胜负
    # 给每个局面打上"从该局面看，本方最终是赢还是输"
    return [(s, pi, z_from_perspective(s, z)) for s, pi in states_pis]
```

MCTS 部分复用上一章的四步（Selection/Expansion/Simulation/Backprop），只是把“随机 rollout”换成“用价值网络评估 + 用策略网络给先验”。

## 4. 几个关键实现细节（容易踩坑）

```text
1. 探索噪声：自我对弈时在根节点策略上加 Dirichlet 噪声，否则早期太确定、学不到多样棋
2. 温度参数：开局用高温度(按访问次数概率采样，多样)，后期降温(选最优)
3. 数据视角统一：价值标签要从"当前落子方"的视角标 z（赢=+1/输=-1）
4. 对称增强：棋盘可旋转/翻转，扩充数据（围棋/五子棋有对称性）
5. MCTS 模拟次数：次数越多越强但越慢，业余条件要折中
```

## 5. “略有遗憾”：业余复现的真实困难

```text
1. 算力：自我对弈极其耗时，每次迭代要下成百上千局，CPU 上慢到绝望
2. 收敛慢：井字棋几小时能学会；五子棋/围棋则需要大量算力和时间
3. 调参敏感：噪声、温度、学习率、模拟次数都影响成败，容易"学不动"
4. 评估成本：新旧网络对战也要下很多局才有统计意义
=> 所以很多复现止步于"井字棋能下到不败"，更大棋盘往往因算力遗憾收尾
```

但这正是宝贵的学习：

```text
你会真切理解——AlphaZero 的"简洁优美"背后，是工程与算力的巨大投入。
算法人人能写，规模才是壁垒。
```

## 6. 推荐的动手路径

```text
1. 先用 suragnair/alpha-zero-general 跑通井字棋（Othello 也行）
2. 读懂它的 MCTS、网络、自我对弈三块代码如何咬合
3. 把模拟次数、网络大小调小，在自己电脑上完整跑一轮迭代
4. 观察：随着迭代，AI 是否越来越难被打败
5. 有 GPU 再尝试更大的棋盘
```

## 7. 从 AlphaZero 回望整个 Part5

```text
RL 基础(MDP/价值) -> 表格法(Q-Learning) -> 深度RL(DQN/PPO)
                                              │
                                  搜索 + 学习(MCTS + 网络)
                                              │
                                      AlphaGo -> AlphaZero -> MuZero
这条线展示了 RL 从"试错学价值"到"规划 + 学习"的完整威力。
而 PPO 那条线，则通向了大模型对齐(RLHF) —— 与 Part4、Part6 相连。
```

## 经典论文与开源项目

- Silver et al., "AlphaZero", 2017；"AlphaGo Zero", 2017。
- Surag Nair, "A Simple Alpha(Go) Zero Tutorial"（配套教程）。
- GitHub: `suragnair/alpha-zero-general`（最适合动手，支持多种棋）、`junxiaosong/AlphaZero_Gomoku`（五子棋，中文友好）。

## 本章小结（Part5 完结）

迷你 AlphaZero 由“游戏逻辑 + 双头网络 + MCTS + 自我对弈 + 训练循环”组成，核心算法不难复现，井字棋等小棋能跑通。但要达到论文强度需要巨大算力，业余复现常“略有遗憾”地止步于小棋盘——这恰恰让人体会到“算法易得、规模为王”。至此强化学习篇完结：从 MDP 到 PPO（连接 RLHF），从 Minimax 到 AlphaZero（搜索 + 学习），你已掌握 RL 的主干。
