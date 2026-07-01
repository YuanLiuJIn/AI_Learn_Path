# 06 RL 优化算法的基石：从 TRPO 到 PPO

## 1. 它解决什么问题

策略梯度有个致命问题：**更新步子不好控制**。

```text
步子太大：策略一下子变太多，可能从"还不错"跌到"彻底崩"，再也学不回来
步子太小：学得太慢
而且 RL 数据是策略自己产生的：策略一崩，后续采的数据也全是垃圾 -> 雪崩
```

TRPO 和 PPO 就是为了解决“**如何稳定地、又不太慢地更新策略**”。PPO 因为简单有效，成了当今最主流的 RL 算法，也是 **RLHF（对齐大模型）** 的标准选择。

## 2. 一句话直觉

> 每次更新策略时，**不要离旧策略太远**——小步快跑、稳扎稳打。就像调音量，每次只拧一点，避免一下子拧爆。

## 3. TRPO：用“信任区域”限制更新

TRPO（Trust Region Policy Optimization）的思想：

```text
在"新策略和旧策略差异不超过一个范围"的约束下，最大化期望回报。
"差异"用 KL 散度衡量（新旧策略的分布差距）。
```

```text
maximize 期望回报
subject to  KL(π_old || π_new) ≤ δ      （新旧策略别差太远）
```

效果好、有理论保证，但**实现复杂**（要算二阶信息、约束优化），工程上很麻烦。

## 4. PPO：用“裁剪”把复杂约束变简单

PPO（Proximal Policy Optimization, OpenAI 2017）保留 TRPO“别更新太猛”的精神，但用一个**极其简单的裁剪技巧**实现，成为事实标准。

### 核心：概率比 + 裁剪

```text
概率比 r(θ) = π_new(a|s) / π_old(a|s)
  r > 1：新策略更爱这个动作
  r < 1：新策略更不爱

PPO 裁剪目标：
L = E[ min( r·A,  clip(r, 1-ε, 1+ε)·A ) ]
                  └ 把 r 限制在 [1-ε, 1+ε] ┘  (ε 常取 0.2)
```

直觉：

```text
A > 0（好动作）：想提高概率，但 r 最多到 1+ε 就"封顶"，不让一次提太多
A < 0（坏动作）：想降低概率，但 r 最低到 1-ε 就"封底"，不让一次降太狠
=> 自动限制每次更新幅度，无需 TRPO 的复杂约束
```

一句话：PPO 用一个 `clip` 函数，简单粗暴地实现了“别更新太远”。

## 5. PPO 完整目标

```text
总损失 = 裁剪策略损失 - c1·价值损失 + c2·熵奖励
         └稳定地改进策略┘ └Critic拟合回报┘ └鼓励探索┘
```

- 价值损失：训练 Critic（Actor-Critic 框架，见上一章）。
- 熵奖励：鼓励策略保持一定随机性，防止过早收敛。

## 6. 为什么 PPO 这么受欢迎

```text
- 简单：几十行就能实现核心，比 TRPO 好写太多
- 稳定：裁剪机制防止策略崩溃
- 通用：离散/连续动作都行，超参不太敏感
- 可复用数据：一批数据可做多轮小更新（mini-batch、多 epoch）
=> 成为游戏、机器人、RLHF 的默认选择
```

## 7. PPO 与 RLHF（连接 Part4）

大模型对齐（InstructGPT/ChatGPT）就用 PPO：

```text
1. 训练一个奖励模型 RM：学习人类更喜欢哪个回答
2. 把语言模型当作"策略"，生成回答
3. 用 RM 给回答打分作为奖励，用 PPO 更新语言模型
4. 加 KL 惩罚：别让模型偏离原始模型太远（又是"别更新太远"的思想！）
```

所以学好 PPO，就理解了大模型“变听话”的核心机制。（近年也有 DPO 等更简化的替代，但 PPO 仍是基石。）

## 8. 代码直觉（PPO 裁剪损失）

```python
import torch

def ppo_loss(logp_new, logp_old, advantage, eps=0.2):
    ratio = torch.exp(logp_new - logp_old)          # 概率比 r
    unclipped = ratio * advantage
    clipped = torch.clamp(ratio, 1 - eps, 1 + eps) * advantage
    return -torch.min(unclipped, clipped).mean()    # 取更保守的那个
```

## 经典论文与开源项目

- Schulman et al., "Trust Region Policy Optimization" (TRPO), 2015。
- Schulman et al., "Proximal Policy Optimization Algorithms" (PPO), 2017（必读）。
- Schulman et al., "GAE"（广义优势估计）, 2015。
- Ouyang et al., "InstructGPT", 2022（PPO 用于 RLHF）。
- GitHub: `vwxyzjn/cleanrl`（PPO 单文件实现，最适合学习）、`openai/spinningup`。

## 本章小结

策略更新最怕“步子太大导致崩溃”。TRPO 用 KL 约束限制更新幅度，理论好但实现复杂；PPO 用一个简单的概率比裁剪（clip 到 1±ε）达到类似效果，简单稳定通用，成为 RL 的事实标准，并是 RLHF 对齐大模型的核心算法。“别更新太远”这一思想贯穿始终。
