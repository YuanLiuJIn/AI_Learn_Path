# 08 系统性学习棋类 AI：从 Minimax 到 AlphaGo

## 1. 它解决什么问题

棋类（井字棋、象棋、围棋）是 RL 与搜索的经典舞台。本章讲清楚 AI 下棋的思路演化：从纯搜索（Minimax）到搜索 + 随机模拟（MCTS）再到搜索 + 神经网络（AlphaGo）。

## 2. Minimax：博弈树搜索

### 一句话直觉

> 我走对我最有利的，对手走对他最有利（对我最不利）的。两边都最优地下，往前推演几步，选当前最好的一步。

```text
我方回合：选让我得分最大(MAX)的走法
对方回合：对方选让我得分最小(MIN)的走法
递归推演到一定深度，回溯出当前最优走法
```

### 例子（井字棋）

```text
当前局面 -> 枚举我所有走法 -> 每种走法下枚举对手所有应对 -> ...
假设双方都最优，算出每条路的结局(赢/输/平)，选必胜或最不坏的一步。
```

### Alpha-Beta 剪枝

Minimax 要搜整棵树，太慢。Alpha-Beta 剪枝：

```text
如果已经发现某分支"肯定不会被选"，就不再往下搜 -> 大幅减少计算
```

### 局限

```text
井字棋：9 个格子，能搜完
国际象棋：状态约 10^47，靠剪枝 + 评估函数（深蓝 1997 击败卡斯帕罗夫）
围棋：状态约 10^170，分支因子约 250 —— 搜索空间爆炸，Minimax 彻底无能为力
```

## 3. MCTS：蒙特卡罗树搜索

围棋太大，不能搜完整棵树。MCTS 的思路：**不搜全部，靠随机模拟来"抽样"评估**。

### 一句话直觉

> 不知道哪步好？那就从当前局面随机快速地把棋下完很多次，看哪步走法最终赢得多，就倾向选它。“多试几次，统计胜率。”

### 四个步骤（循环很多次）

```text
1. Selection（选择）：从根节点按"既偏好高胜率、又给少访问的节点机会"(UCB)往下走
2. Expansion（扩展）：到达一个未完全展开的节点，新增一个子节点
3. Simulation（模拟）：从该节点随机快速下到终局，看输赢（rollout）
4. Backpropagation（回传）：把这局结果回传，更新沿途节点的访问次数和胜率
```

UCB 公式平衡探索与利用（呼应第 1 章）：

```text
选择得分 = 平均胜率 + c·√(ln(父访问次数)/本节点访问次数)
           └利用：胜率高的┘  └探索：访问少的给机会┘
```

模拟次数越多，估计越准。MCTS 让围棋 AI 有了质的飞跃，但纯 MCTS 还达不到顶尖人类水平。

## 4. AlphaGo：MCTS + 深度神经网络

AlphaGo（DeepMind 2016，击败李世石）的突破：**用神经网络给 MCTS 装上“直觉”**，不再靠纯随机模拟。

### 两个网络

```text
策略网络 (Policy Network)：看局面，输出"每个落子点的概率"
  -> 告诉 MCTS"哪些走法值得重点搜"，大幅缩小搜索宽度

价值网络 (Value Network)：看局面，输出"当前局面的胜率"
  -> 替代昂贵的随机模拟到底，直接估计胜负，缩小搜索深度
```

### 怎么结合

```text
MCTS 搜索时：
  - 用策略网络引导"选择/扩展"该往哪走（不再盲目）
  - 用价值网络评估局面（不必每次都随机下到终局）
=> 搜索又准又高效，达到超人水平
```

### 训练流程（AlphaGo 版）

```text
1. 监督学习：用人类高手棋谱训练策略网络（先学会"像人一样下"）
2. 强化学习：让策略网络自我对弈，用 RL 改进（超越人类棋谱）
3. 训练价值网络：用自我对弈数据学"局面胜率"
```

## 5. 演化总结

```text
Minimax + Alpha-Beta：能解井字棋、象棋（深蓝）
  └ 围棋太大，失效
MCTS：随机模拟抽样评估，围棋 AI 起飞
  └ 纯随机还不够强
AlphaGo = MCTS + 策略网络(选哪走) + 价值网络(局面胜率)
  └ 击败人类顶尖棋手
  └ 但仍依赖人类棋谱起步 -> AlphaZero 要去掉这个依赖（下一章）
```

## 6. 代码直觉（MCTS 主循环）

```python
def mcts_search(root, n_sim):
    for _ in range(n_sim):
        node = root
        path = [node]
        # 1. Selection：用 UCB 往下走到叶子
        while node.is_fully_expanded() and node.children:
            node = node.best_child_by_ucb()
            path.append(node)
        # 2. Expansion
        if not node.is_terminal():
            node = node.expand()
            path.append(node)
        # 3. Simulation：随机/用价值网络评估
        result = node.rollout()          # AlphaGo 这里用价值网络替代
        # 4. Backpropagation
        for n in path:
            n.update(result)
    return root.most_visited_child()      # 选访问最多的走法
```

## 经典论文与开源项目

- Silver et al., "Mastering the game of Go with deep neural networks and tree search" (AlphaGo), Nature 2016。
- Browne et al., "A Survey of Monte Carlo Tree Search Methods", 2012。
- GitHub: `tensorflow/minigo`、`leela-zero/leela-zero`（开源复现）。

## 本章小结

下棋 AI 的演化：Minimax + Alpha-Beta 剪枝能解决象棋（深蓝），但围棋状态爆炸使其失效；MCTS 用随机模拟抽样评估让围棋 AI 起飞；AlphaGo 用策略网络（选哪走）和价值网络（估胜率）给 MCTS 装上神经网络的“直觉”，击败人类顶尖棋手。它仍需人类棋谱起步——下一章的 AlphaZero 将彻底摆脱这一依赖。
