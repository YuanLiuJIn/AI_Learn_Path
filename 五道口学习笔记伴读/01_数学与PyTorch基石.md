# 01 · 数学与 PyTorch 基石（伴读）

> 对应原始库：`math/` 全目录 + README 的"PyTorch / core concepts"段落。
> 定位：所有 LLM / Agent / RL 的地基。up 主反复强调"原理先行"，这一章就是原理的源头。

## 1. 三种方法论范式（README 的灵魂框架）

up 主把 AI 方法归为三大范式，这是理解后面一切的顶层视角：

| 范式 | 代表 | 本质 | 在库里的位置 |
|---|---|---|---|
| **Sampling-based** | MCMC、Importance Sampling、MC in RL | 用采样估计期望/积分（大数定律 LLN） | `math/` 采样部分 |
| **Search-based** | AlphaGo、树搜索、TongGeometry | 在决策树上搜索最优 | `agents/tree_search/`、`math/` |
| **Learning-based** | ML / DL（数据驱动） | 从数据学参数 | 全库主线 |

**关键洞察**：现代 LLM + RL 是"learning + sampling + search"的混合——SFT 是 learning，RLHF 是 learning+sampling，Agent 的 tree_search / MCTS 是 search。不要孤立看。

## 2. 概率统计（必会）

### 2.1 MLE vs Bayes
- **MLE（最大似然）**：固定数据，找使 `P(data|θ)` 最大的 θ。先建模型，再估参数。
- **Bayes**：θ 也是随机变量，`P(θ|data) ∝ P(data|θ)P(θ)`。引入先验。

### 2.2 似然与概率
- 概率是"给定参数，数据的可信度"：`P(x|θ)`
- 似然是"固定数据，参数的可信度"：`L(θ) = P(x|θ)`
- 训练时我们最大化似然（即最小化负对数似然 NLL）

## 3. 矩阵分析（LLM 的线性代数底）

| 主题 | 为什么重要 | 关联 |
|---|---|---|
| **SVD** | 任何矩阵的"主成分"分解；**LoRA 的数学本质**就是低秩分解 | `math/matrix/`、你的 `AgentRl/`、`升腾910b_infra` 不涉及但训练必懂 |
| **谱范数（spectral norm）** | 矩阵最大奇异值；用于 Lipschitz 约束、GAN/扩散稳定性 | `math/matrix/谱范数奇异值与权重初始化` |
| **雅可比矩阵** | 向量值函数对向量的导数；反向传播的推广形式 | 自动微分的数学基础 |
| **特征值/正定性** | 优化收敛性、Hessian 分析 | `math/matrix/eigen`、`matrix_definiteness` |

**LoRA 一句话数学**：原权重 `W ∈ R^{m×n}`，LoRA 训 `W + ΔW = W + BA`，其中 `B∈R^{m×r}, A∈R^{r×n}`，`r ≪ min(m,n)`。SVD 告诉我们：低秩 `BA` 近似了 `ΔW` 的主奇异方向——这正是"用极少参数学大变化"的原理。

## 4. Sampling-based methods（RL 的前置）

### 4.1 Monte Carlo（大数定律）
用样本均值估计期望：`E[f(X)] ≈ (1/N)Σ f(x_i)`，靠 LLN 保证收敛。用于：
- 估计难解析的多维积分
- RL 里的 return 估计（MC 方法）

### 4.2 Importance Sampling（你之前问过）
用 Q 采样估 P 的期望：`E_P[f] ≈ (1/N)Σ f(x_i)·P(x_i)/Q(x_i)`。
- 在 RL 里就是 PPO 的 `r_t = π_新/π_旧`（详见 `02_核心概念.md` 与你的 `AgentRl/02`）
- 在库里：`math/` 采样部分、RL 训练全程

### 4.3 MCMC / Metropolis-Hastings
从难归一化的分布采样，用于贝叶斯推断。理解思路即可，不必深抠。

## 5. PyTorch：计算图与梯度流（最实用的一块）

### 5.1 计算图 & 梯度可反传 = 可学习
- 前向建图，反向沿图链式法则求梯度
- **只有梯度能反传（可微）的部分才是 learnable 的**

```python
x = torch.randn(3, requires_grad=True)
y = x * 2
loss = y.sum()
loss.backward()        # 沿计算图反传
print(x.grad)          # 有值 → 可学习
```

### 5.2 梯度断流：出现 sampling 时
当计算图里出现**采样（不可微）**，梯度就断了。两个解法：
- **Policy Gradient**：绕过梯度，用"期望梯度 = 对数概率 × 回报"直接估计（见 `02` 与 `AgentRl/02`）
- **Reparameterization Trick**（重参数化）：把随机性从"采样"挪到"固定分布 + 可微变换"，如 `z = μ + σ ⊙ ε, ε~N(0,1)`，让 μ、σ 可学（VAE 的核心）

### 5.3 优化视角
> learning 即 optimization（对 DL 而言）。

训练 = 在由数据定义的损失面上，用梯度下降找最优参数。所有技巧（学习率、动量、warmup、schedule）都是为了让这个优化更稳更快。

## 6. 本章与后续的接口

- 第 2 章的 **KL / on-off-policy / MC-TD** 直接用到这里的采样与概率 → 见 `02_核心概念.md`
- 第 3 章 Agentic RL 的 PPO/GRPO 用到 **重要性采样、梯度流、优化视角** → 见 `03_AgenticRL主线.md`
- LoRA 的低秩思想在 `AgentRl` 与微调场景反复出现

## 7. 在原始库里的阅读落点

- `math/basics`、`math/matrix/`（basics/eigen/谱范数/SVD 思想）、`math/bayesian`、`math/calculus`、`math/markovian`、`math/graph`
- README 的 PyTorch / core concepts 段落
- 代码范式散见各 `*.ipynb`（如 `training_practices/kl_数值内涵.ipynb` 里的 KL 代码）

## 验收

- [ ] 能说清 MLE / Bayes / 似然的区别
- [ ] 能解释 LoRA 为什么是"SVD 低秩近似"的特例
- [ ] 能写出重要性采样公式，并说清它在 PPO 里的角色
- [ ] 能解释"为什么采样会断梯度"以及 PG / 重参数两个解法
- [ ] 理解"learning 即 optimization"
