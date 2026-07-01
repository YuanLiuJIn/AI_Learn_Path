# 09 Model-based RL 与再谈 AlphaZero

## 1. Model-free vs Model-based

前面的算法（Q-Learning、PPO）大多是 **model-free（无模型）**：不去学“环境怎么运转”，只靠大量试错学价值/策略。

**model-based（有模型）** RL 则不同：

> 先学习（或已知）一个“环境模型”——给定状态和动作，能预测下一个状态和奖励。有了模型，就能在“脑子里”推演规划，不必每次都真实试错。

```text
model-free：  不懂环境规则，靠海量真实试错（样本贵）
model-based：学/知道环境规则，能在想象中规划（样本高效）
```

生活类比：

```text
model-free：每条路都亲自走一遍才知道堵不堵（费时间）
model-based：脑子里有张地图，能预先规划路线（高效，但地图错了会误导）
```

## 2. Model-based 的优缺点

```text
优点：样本效率高（在模型里"想象"很多次，少用真实交互）；能做规划
缺点：学准一个环境模型本身很难；模型有误差会被规划放大
```

棋类是 model-based 的理想场景——**规则完全已知**（落子后棋盘怎么变是确定的），所以可以放心地用模型做搜索规划。这正是 AlphaZero 的前提。

## 3. AlphaZero：把 AlphaGo 推向极致

AlphaZero（DeepMind 2017）相比上一章的 AlphaGo，做了关键简化和升级：

```text
AlphaGo：
  - 需要人类棋谱做监督学习起步
  - 策略网络、价值网络分开
  - 有专门的快速 rollout 网络

AlphaZero：
  - 完全不用人类棋谱，从零自我对弈学习（tabula rasa，白纸开始）
  - 一个网络同时输出策略和价值（双头）
  - 不做随机 rollout，完全用价值网络评估
  - 同一套方法通吃围棋、国际象棋、将棋
```

一句话：

> AlphaZero 只告诉 AI 游戏规则，让它从完全随机开始，通过自我对弈 + MCTS，自己悟出超越人类的棋艺。

## 4. 核心：MCTS 与神经网络的相互成就

AlphaZero 的精髓是一个**自我强化的循环**：

```text
神经网络 f_θ(s) -> (策略 p, 价值 v)   "直觉"：这局面该怎么走、谁会赢
       │
       v
MCTS 用 f_θ 引导搜索 -> 产出比网络更强的走法分布 π   "深思熟虑"
       │
       v
用 MCTS 的结果 π 作为标签，训练网络 f_θ 去逼近它    "把深思蒸馏成直觉"
       │
       └──────────── 网络变强 -> MCTS 更强 -> 网络更强 ... 循环上升
```

直觉：

```text
神经网络 = 快速直觉
MCTS    = 慢速深思（用直觉引导，但搜得更深，结果更准）
训练 = 让"直觉"不断学习"深思"的结论 -> 直觉越来越准 -> 深思也越来越强
```

这是“快思考”与“慢思考”互相提升的优美设计。

## 5. 一个网络，双头输出

```text
输入：棋盘状态 s
        │
   [深度残差网络 ResNet]（呼应 Part2 ResNet）
        │
   ┌────┴────┐
策略头 p     价值头 v
(每个落子    (当前局面
 的概率)      的胜率 -1~1)
```

损失函数同时优化两头：

```text
Loss = (z - v)²        价值：预测胜负 v 对齐真实结局 z（MSE）
     - π·log(p)        策略：网络策略 p 对齐 MCTS 搜索出的 π（交叉熵）
     + 正则项
```

## 6. 自我对弈训练循环

```text
重复：
  1. 自我对弈：当前网络 + MCTS 自己跟自己下很多局，记录每步的 (s, π, z)
       s=局面, π=MCTS 走法分布, z=该局最终输赢
  2. 训练：用这些数据训练网络，让 p→π、v→z
  3. （AlphaGo Zero 会用新网络对战旧网络，更强才替换）
```

完全不需要人类数据，纯靠规则 + 自我博弈。

## 7. 影响与延伸

```text
AlphaZero -> MuZero：连规则都不告诉它，自己学环境模型（真正的 model-based）
           -> 应用扩展到：蛋白质折叠思路、芯片布局、算法发现(AlphaTensor)等
启示：搜索(规划) + 学习(神经网络) 的结合极其强大
```

## 经典论文与开源项目

- Silver et al., "Mastering Chess and Shogi by Self-Play..." (AlphaZero), 2017。
- Silver et al., "Mastering the game of Go without human knowledge" (AlphaGo Zero), Nature 2017。
- Schrittwieser et al., "MuZero", 2020。
- GitHub: `suragnair/alpha-zero-general`（通用、易读的 AlphaZero 实现，强烈推荐）、`leela-zero/leela-zero`。

## 本章小结

Model-based RL 用“环境模型”在想象中规划，样本高效，棋类因规则已知而特别适合。AlphaZero 在 AlphaGo 基础上去掉人类棋谱、统一为单个双头网络、纯用价值网络评估，靠“自我对弈 + MCTS + 网络训练”的自我强化循环（直觉与深思互相提升）从零达到超人水平。下一章动手复现 AlphaZero 训练。
