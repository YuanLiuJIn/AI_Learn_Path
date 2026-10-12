# Part01：RL 基础与 MBRL 综述（第 1–2 周）

> 本部分是「世界模型」专题的起点。目标不是把 RL 学完，而是把**世界模型所依赖的那部分 RL 语言**补齐，并建立 Model-Based RL（MBRL）的整体分类坐标。
> 之后每一篇世界模型论文，都会被放回这套坐标里理解：它学什么模型、怎么用模型。

## 0. 本部分要解决的问题

学世界模型最常见的失败方式：直接去读 Dreamer / Genie / Sora，结果卡在三件事上：

1. 不知道"模型"在 RL 里指什么（和"神经网络模型"是同一个词，但不是同一件事）；
2. 不知道"用模型"有几种方式，于是分不清 PlaNet 和 MBPO 的区别；
3. 不知道 MBRL 的经典坑（误差累积、模型被滥用），于是看不懂论文里那些"看起来多余"的设计。

前置要求：

- 概率期望、神经网络、梯度下降（`../Part1_learning_basic/`）
- 先过一遍 `../Part5_reinforcement_learning/01_rl_intro.md` 与 `02_rl_math.md`（MDP、价值、贝尔曼）

本部分只保留"世界模型必需"的 RL 概念，其余一律回 `../Part5_reinforcement_learning/` 补。

```text
本部分在整体路线中的位置

第1-2周  Part01（本文）：RL 基础 + MBRL 综述 + CS285 相关讲次   ← 建立坐标
第3-4周  Part02：World Models (2018) + PlaNet/RSSM              ← 第一条主线
第5-7周  Part03：Dreamer V1/V2/V3 + 代码复现
第8-9周  Part04：MuZero / EfficientZero 对照
第10周+  Part05：JEPA 派 / 生成式视频世界模型 / LLM as world model
```

---

## 1. 先把"世界模型"这个词掰开

### 1.1 两种语境下的"模型"

| 说法 | 意思 | 例子 |
|---|---|---|
| "训练了一个模型" | 参数化的函数近似器 | 一个 CNN、一个 Transformer |
| "世界模型 / 环境模型" | 对环境**动态**的可预测内部表示 | $p(s_{t+1}\mid s_t,a_t)$ |

世界模型是第二种。它本身通常也用神经网络实现，但角色是**替代环境**，而不是替代策略或价值函数。

### 1.2 一句定义

> 世界模型 = 智能体对环境的一个内部、可预测、可用于决策的模型。
> 它回答的不是"该做什么"，而是"**如果我这么做，接下来会发生什么**"。

这与本仓库 `../modern_genai_bilibili/agents/reasoning-planning/worldmodel.ipynb` 中的笔记一致：

```text
预测"说什么"（LLM 的语言建模目标） vs. 预测"会发生什么"（世界模型的目标）
拥有世界模型的智能体，当现实反馈与预测不符时会"惊讶"，
并依据这种预期外的事件来修正自己的模型。
```

"惊讶"在数学上就是**预测误差（negative log-likelihood / KL）**，直接对应 Dreamer 的训练损失。

### 1.3 四条路线（本专题的全局地图）

| 路线 | 核心思想 | 代表 | 安排 |
|---|---|---|---|
| A. 潜在动力学 + RL | 观测压到隐空间，学转移与奖励，在"梦"里训练策略 | PlaNet → DreamerV1/V2/V3、MuZero | Part02–04（**主线**） |
| B. 表征预测式（JEPA） | 不做像素重建，只在表征空间预测未来 | LeCun 2022、I-JEPA、V-JEPA 2 | Part05 |
| C. 生成式视频/交互环境 | 直接生成下一个世界状态 | Sora、Genie、GameNGen、Cosmos | Part05 |
| D. LLM 作为世界模型 | 检验语言模型内部是否涌现环境状态 | Othello-GPT、WebDreamer | Part05 |

记住 A 与 C 的分工：**A 为了决策而压缩世界，C 为了渲染而重建世界。**

---

## 2. RL 最小必备知识（世界模型视角）

完整推导见 `../Part5_reinforcement_learning/02_rl_math.md`，这里只写"读世界模型论文会被反复用到"的部分。

### 2.1 MDP：世界模型要建模的对象

```text
MDP = (S, A, P, R, γ)

S  状态集合        s_t
A  动作集合        a_t
P  转移概率        P(s_{t+1} | s_t, a_t)   ← 世界模型学的就是这个
R  奖励函数        R(s_t, a_t)             ← 通常一起学
γ  折扣因子        0 ≤ γ < 1
```

目标：求策略 $\pi(a\mid s)$ 最大化期望折扣回报

$$
J(\pi)=\mathbb{E}_{\pi}\Big[\sum_{t=0}^{\infty}\gamma^{t}r_{t+1}\Big]
$$

**关键认知**：$P$ 和 $R$ 就是"世界的规则"。model-free 绕过它，model-based 显式学它。

### 2.2 两个价值函数

$$
V^{\pi}(s)=\mathbb{E}_{\pi}\big[r+\gamma V^{\pi}(s')\mid s\big],\qquad
Q^{\pi}(s,a)=\mathbb{E}\big[r+\gamma\,\mathbb{E}_{a'\sim\pi}Q^{\pi}(s',a')\mid s,a\big]
$$

论文里被反复借用：

- 用模型 rollout 时，拿 $\hat V/\hat Q$ 给想象轨迹打分（model as value estimator）；
- "在想象中训练"本质是对**学出来的** $P$ 施加贝尔曼更新。

### 2.3 model-free vs model-based：一条分界线

| 问题 | model-free（DQN、PPO） | model-based（PlaNet、Dreamer、MBPO） |
|---|---|---|
| 是否显式学 $P,R$ | 否 | 是 |
| 样本效率 | 低（动辄百万步） | 高（常提升 10–100×） |
| 计算成本 | 低 | 高（要前向模拟） |
| 主要风险 | 学得慢 | 模型误差被策略利用 |
| 数据来源 | 真实环境 | 真实环境 + 模型想象数据 |

**这就是学世界模型的全部动机**：真实交互太贵，先学一个便宜的"世界"，在那个世界里练习。

### 2.4 三个会被反复引用的概念

```text
on/off-policy：模型产生的数据天然是 off-policy 数据（不是当前策略采的），
               所以 MBRL 常配 off-policy 算法，或需要做分布修正。

POMDP：真实任务里 agent 看不到完整状态 s，只看到观测 o（图像/传感器）。
       所以学的其实是 p(o_{t+1} | o_{≤t}, a_t)，并需要额外学一个
       "从观测推断隐状态"的编码器 —— RSSM 就是干这个。

信用分配 + 探索：见 Part5，不重复。但要记住世界模型给了探索一个新工具：
                用模型预测"哪里不确定性高"，就知道哪里值得去试。
```

能不看笔记解释清"$P(s'\mid s,a)$ 是什么、为什么学它有用"，就可以进入第 3 节。

---

## 3. MBRL 综述精读（本部分核心）

主读一篇：**Moerland et al., _Model-based Reinforcement Learning: A Survey_, 2020, arXiv:2006.16712**。
它是整个专题的坐标系，读完每篇世界模型论文都能被放进某个格子。

### 3.1 综述的两个正交问题

```text
问题一：模型怎么学？（model learning）
   └─ 表示：高斯过程 / 神经网络 / 隐变量模型 / 集成模型
   └─ 目标：单步预测 / 多步预测 / 重建 + KL 的 ELBO

问题二：模型怎么用？（model usage）   ← 更重要，直接决定算法形态
```

### 3.2 "怎么用模型"的四类（重点记这张表）

| 用法 | 直觉 | 代表 | 优点 | 缺点 |
|---|---|---|---|---|
| ① 当模拟器产数据（Dyna-style） | 在模型里跑，把假经验丢给 model-free 算法 | Dyna-Q、MBPO | 实现简单，易接现有算法 | 长 rollout 误差爆，需限长 |
| ② 价值扩展（value expansion） | 用模型 rollout 几步，拿多步回报修正目标值 | MVE | 不改原算法框架 | 只在短视野有效 |
| ③ 通过模型求梯度（analytic gradient） | 把模型当可微一层，反传到策略 | SVG、Dreamer | 方差低，不用采样估梯度 | 需可微模型，易陷局部 |
| ④ 规划（planning / MPC） | 不训策略，每步在模型里搜最优动作序列 | PETS、PlaNet、MCTS/AlphaZero | 可在线适应 | 每步都规划，推理慢 |

口诀：**产数据、修目标、求梯度、做搜索。** 这张表能把 Part02–05 全部排列清楚：

```text
PlaNet  → ④ 规划（在隐空间做 CEM 规划）
Dreamer → ③ 求梯度（在隐空间想象中反传训练 actor-critic）
MBPO    → ① 产数据（短 rollout + 模型集成）
MuZero  → ④ 规划（但学价值/奖励/隐状态，不重建观测）
MVE     → ② 修目标
```

### 3.3 最小对照实验：Dyna-Q

Sutton 1991 的 Dyna 架构（*Dyna, an Integrated Architecture for Learning, Planning, and Reacting*）把"学"与"规划"统一起来：

```text
真实经验 ──► 更新 Q
    │
    └──► 存入模型 ──► 模拟 n 次假经验 ──► 再更新 Q

n = 0  → 纯 Q-Learning（model-free）
n > 0  → 样本效率提升（确定性环境下 n 越大越明显）
```

意义：**"规划"就是复用已有经验做额外更新**，不需要新算法。世界模型路线在概念上是它的深度版。

### 3.4 四个经典陷阱（论文里那些设计就是在防这个）

```text
1. 误差累积（compounding error）
   单步误差 ε，H 步 rollout 后误差随 H 放大。
   → 对策：短 rollout（MBPO）、隐空间建模降噪（Dreamer）。

2. 模型被滥用（model exploitation）
   策略会跑到模型预测不准但"看起来奖励高"的区域。
   → 对策：模型集成 + 不确定性惩罚（PETS）、缩短 rollout、加正则。

3. 分布偏移
   模型只在数据覆盖区准；策略越界后模型失效，形成恶性循环。
   → 对策：真实数据与模型数据混合（MBPO 的 branching rollout）。

4. 重建 vs 可控性的取舍
   像素级重建把容量花在"画背景"上，而决策不关心背景。
   → 这正是 Dreamer 走隐空间、JEPA 干脆不重建的动机。
   带着这条读 Part02，会顺很多。
```

---

## 4. CS285 相关讲次（第 1–2 周视频任务）

课程：**UC Berkeley CS285 Deep Reinforcement Learning（Sergey Levine）**，官网 `rail.eecs.berkeley.edu/deeprlcourse/`，B 站有中/英字幕转载。

> 讲次编号每年会变，**按标题找，不要按编号找**。

| 顺序 | 讲次标题（按标题检索） | 要回答的问题 | 配套论文 |
|---|---|---|---|
| 1 | Model-Based Planning / MPC | 怎么把模型当模拟器来搜动作？随机打靶、CEM、MPC 的差别？ | MPPI(2017)、PETS(2018) |
| 2 | Model-Based Policy Learning | 用模型产数据训练策略有哪几种做法？长短 rollout 如何取舍？ | Dyna(1991)、MVE(2018)、MBPO(2019)、SVG(2015) |
| 3 | Variational Inference / Latent Variable Models | ELBO 是什么？为什么隐变量模型能处理高维观测？ | 直接衔接 Part02 的 RSSM |

三讲的地位：

- 第 1 讲决定你能不能读懂 PlaNet（Part02）；
- 第 2 讲决定你能不能读懂 Dreamer 的训练循环（Part03）；
- 第 3 讲是 Dreamer 的数学地基，**不要跳**。

按需补充：CS234（Emma Brunskill）的 MBRL/exploration 视角作为第二讲法；OpenAI Spinning Up 的 "Kinds of RL Algorithms" 一节用来定位坐标（约 10 分钟）。

---

## 5. 文献清单与阅读顺序

### 5.1 必读（两周内完成）

| # | 文献 | 读法 | 必须抓到 |
|---|---|---|---|
| 1 | Sutton & Barto, *RL: An Introduction*, **第 3–4 章** | 复习/速读 | MDP、贝尔曼方程、策略迭代/价值迭代 |
| 2 | Sutton & Barto, **第 8 章**（Planning and Learning with Tabular Methods） | 精读 | Dyna 架构、"规划=复用经验做更新" |
| 3 | Sutton, *Dyna, an Integrated Architecture...*, 1991 | 泛读 | 原始动机，篇幅很短 |
| 4 | Moerland et al., *Model-based RL: A Survey*, 2020, arXiv:2006.16712 | **精读分类框架部分** | 两大问题、四类用法、MBRL 普遍挑战 |
| 5 | Janner et al., *When to Trust Your Model* (MBPO), 2019, arXiv:1906.08253 | 读方法与实验 | 为什么用短 rollout、模型集成怎么用 |
| 6 | Chua et al., *Deep RL in a Handful of Trials* (PETS), 2018, arXiv:1805.12114 | 读方法与实验 | 概率集成模型 + CEM 规划 + 不确定性惩罚 |
| 7 | Feinberg et al., *Model-Based Value Expansion*, 2018, arXiv:1803.00101 | 泛读 | 用模型 rollout 修正 TD 目标 |

### 5.2 选读（第 2 周末有余力再看）

- Deisenroth & Rasmussen, *PILCO*, ICML 2011：高斯过程做动力学，样本效率的经典标杆。
- Heess et al., *Stochastic Value Gradients*, 2015：第 ③ 类用法的源头。
- Nagabandi et al., *Neural Network Dynamics for Model-Based Deep RL with Model-Free Fine-Tuning*, 2018：模型预训练 + 微调范式的早期代表。
- 一份 POMDP 入门材料：对"隐状态"概念不熟时补一节。

### 5.3 与已有笔记的分工（避免重复劳动）

```text
Part5 已覆盖：Policy Gradient、Actor-Critic、PPO、AlphaZero / MCTS
Part01 新增：把 AlphaZero 重新认识为"第④类用法（规划）"的实例
            MuZero 在 Part04 会作为"学价值模型的规划法"再读一次
```

---

## 6. 会议与前沿渠道

### 6.1 顶会与目标期刊

| 类型 | 场所 | 说明 |
|---|---|---|
| 机器学习主会 | **NeurIPS / ICLR / ICML** | 世界模型论文的主要首发出处 |
| 机器人/具身 | **CoRL / RSS / ICRA** | 世界模型落地具身智能的主要出口 |
| 正刊级 | **Nature / Science**（DreamerV3、MuZero） | 极少工作能走到这步，值得精读写法 |
| 视觉会议 | CVPR / ICCV / ECCV | 生成式世界模型（C 路线）多发于此 |

### 6.2 值得盯的 workshop

- NeurIPS / ICLR 历年的 **Model-Based RL** 与 **World Models** 主题 workshop：综述性与观点类文章多，建全景最快。
- CoRL 的 world model 相关 session：能看到真实进展与失败案例。

### 6.3 长期跟踪方法

```text
1. arXiv 关键词订阅："world model"、"latent dynamics"、"model-based RL"
2. 作者订阅：Danijar Hafner、Jürgen Schmidhuber、David Ha、Sergey Levine、
   Yann LeCun（JEPA）、Chelsea Finn
3. 机构博客（比论文好读）：DeepMind、Meta FAIR、NVIDIA、World Labs、Wayve
4. 每读完一篇填统一模板（见 7.1），半年后你会有一张自己的地图
```

---

## 7. 博客与公开笔记

| 资源 | 用途 | 怎么用 |
|---|---|---|
| Danijar Hafner 博客（danijar.com） | Dreamer 作者的思路演进 | 读论文前先看对应博文，把动机看懂 |
| David Ha & Schmidhuber, *World Models*（worldmodels.github.io，含 Colab） | 世界模型最直观的演示 | Part02 动手时再回来跑 |
| Lilian Weng 的 RL / MBRL 系列长文（lilianweng.github.io） | 概念速查与公式梳理 | 卡住时当第二本参考书 |
| OpenAI Spinning Up 文档 | 算法坐标与术语 | 查 on/off-policy 等术语 |
| Berkeley CS285 讲义 PDF | 最规范的定义与推导 | 看视频时对照 |
| 本仓库 `../Part5_reinforcement_learning/09_modelbased_alphazero.md` | 已有中文 MBRL 笔记 | 对照阅读，检查概念一致性 |
| 本仓库 `../glossary.md` | 术语表 | 新增术语请补录进去 |

### 7.1 笔记模板（每篇论文填一遍，约 10 分钟）

```text
论文 / 年份 / 会议：
它学什么模型？（表示 + 学习目标）
模型怎么用？（①产数据 ②修目标 ③求梯度 ④规划）
怎么防模型被滥用？
实验环境与基线：
我没懂的地方 / 待验证的疑问：
```

---

## 8. 动手实验（两周内至少完成实验 1）

> 原则：世界模型的直觉只能靠"亲手让模型误差打脸"获得。

### 实验 1（必做）：手写 Dyna-Q，看到样本效率提升

环境：`FrozenLake` 或自写 GridWorld（确定性版本），同一张图跑两个配置。

```python
from collections import defaultdict
import random

alpha, gamma, eps = 0.5, 0.99, 0.1
Q = defaultdict(lambda: defaultdict(float))
model = {}                          # (s, a) -> (r, s_next, done)

def dyna_q(env, n_planning, episodes=200):
    for _ in range(episodes):
        s, _ = env.reset(); done = False
        while not done:
            # 1) 真实交互（epsilon-greedy）
            a = env.action_space.sample() if random.random() < eps \
                else max(Q[s], key=Q[s].get, default=env.action_space.sample())

            s_next, r, term, trunc, _ = env.step(a)
            done = term or trunc

            # 2) 真实经验更新 Q
            target = r + gamma * (0 if done else max(Q[s_next].values(), default=0.0))
            Q[s][a] += alpha * (target - Q[s][a])

            # 3) 写入模型
            model[(s, a)] = (r, s_next, done)

            # 4) 规划：采样 n 次假经验做同样更新
            for _ in range(n_planning):
                (s_, a_), (r_, s2_, d_) = random.choice(list(model.items()))
                t_ = r_ + gamma * (0 if d_ else max(Q[s2_].values(), default=0.0))
                Q[s_][a_] += alpha * (t_ - Q[s_][a_])

            s = s_next
    return Q
```

要观察并记录：

1. `n_planning=0` 与 `n_planning=20` 收敛所需**真实步数**差多少？
2. 环境改成**随机**（stochastic）后 Dyna-Q 会出什么问题？为什么？（直连"模型不可信"主题）
3. 把模型数据与真实数据的更新比例调大，会不会反而变差？

### 实验 2（选做，强烈建议）：用"已知模型"做 CEM 规划

不学模型，直接用环境的真实动态函数，在 CartPole 上实现 MPC（滚动时域，每步只执行第一个动作后重新规划）：

```python
import numpy as np

def cem_plan(dynamics, s0, horizon=20, n_samples=200, n_iter=3, n_elite=20):
    mu, sigma = np.zeros(horizon), np.ones(horizon)
    for _ in range(n_iter):
        cand = np.random.randn(n_samples, horizon) * sigma + mu
        returns = []
        for seq in cand:
            s, total = s0, 0.0
            for t in range(horizon):
                s, r, done = dynamics(s, seq[t])
                total += r
                if done:
                    total -= 10          # 失败惩罚，防止"自杀式"序列
                    break
            returns.append(total)
        elite = cand[np.argsort(returns)[-n_elite:]]
        mu, sigma = elite.mean(axis=0), elite.std(axis=0) + 1e-6
    return mu[0]
```

要思考：把 `dynamics` 换成**神经网络学出来的**，会引入哪些新问题？（这就是 Part02 的入口）

---

## 9. 两周日程表

| 天 | 任务 |
|---|---|
| D1 | Part5 的 01/02 复习；Sutton & Barto 第 3–4 章 |
| D2 | Sutton & Barto 第 8 章 + Dyna(1991) |
| D3 | CS285 Model-Based Planning 讲 |
| D4 | 实验 2：CEM 规划跑通 CartPole |
| D5 | Moerland 综述前半（model learning） |
| D6 | Moerland 综述后半（model usage），画自己的四类用法表 |
| D7 | 复盘 + 笔记模板填 2 篇 |
| D8 | CS285 Model-Based Policy Learning 讲 |
| D9 | MBPO + MVE 泛读 |
| D10 | PETS 精读（重点看不确定性惩罚） |
| D11–D12 | 实验 1：Dyna-Q 三组对比 + 随机环境实验 |
| D13 | CS285 Variational Inference 讲（为 Part02 铺路） |
| D14 | 写 Part01 小结：用自己的话复述"四类用法"+ 更新 `glossary.md` |

---

## 10. 自检清单（两周后应能回答）

- [ ] 世界模型和"神经网络模型"的区别是什么？它建模的对象是谁？
- [ ] $P(s'\mid s,a)$ 与 $R(s,a)$ 分别是什么？为什么 model-free 可以不学它们？
- [ ] MBRL 的四类用法各是什么？各举一例，并说出各自缺点。
- [ ] Dyna-Q 里"规划"到底做了什么？为什么它能提升样本效率？
- [ ] 什么是 compounding error？为什么 MBPO 只用短 rollout？
- [ ] 什么是 model exploitation？PETS 用什么手段缓解？
- [ ] "惊讶 / 预测误差 / NLL / KL"这几个词在 Dreamer 里如何对应到损失函数？
- [ ] 为什么 Dreamer 不直接重建像素？（提示：重建 vs 可控性）

## 11. 与后续 Part 的衔接

```text
Part01 → Part02 三个入口：
  1) 综述里的"隐变量模型"分支 → PlaNet/RSSM 的动机
  2) 第③类用法（通过模型求梯度）→ Dreamer 的想象训练
  3) 实验 2 中"dynamics 换成学出来的网络"→ 世界模型的核心难点

进入 Part02 前的最小准备：
  - 会写 ELBO 的直觉解释（不必手推全部推导）
  - 跑通实验 1 与实验 2
  - 完成 7.1 笔记模板至少 4 篇
```

