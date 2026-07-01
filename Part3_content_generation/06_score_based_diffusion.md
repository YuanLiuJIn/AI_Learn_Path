# 06 最容易理解的扩散模型：Score-based Diffusion

## 1. 为什么还要 Score 视角

上一章的 DDPM 是“预测噪声”。Score-based 模型（Song & Ermon 等）给扩散一个**更统一、更几何直观**的解释，并把它和随机微分方程（SDE）联系起来。理解它，你会发现 DDPM、Score、后面的 Flow Matching 其实是同一件事的不同说法。

## 2. 什么是 Score（分数）

Score 的定义是**对数概率密度的梯度**：

```text
score(x) = ∇_x log p(x)
```

别被符号吓到，直觉非常简单：

> Score 是一个“指向数据更可能出现的方向”的箭头场。在任意一点，它告诉你“往哪个方向走，能到达密度更高（更像真实数据）的地方”。

生活类比：把数据分布想象成一片山地，山峰是“最像真实数据”的地方。Score 就是每个位置的“上山方向”——顺着箭头走，就走向真实数据。

## 3. 一句话直觉

> 如果我们知道每个位置的“上山箭头”（score），就能从一团随机噪声出发，**顺着箭头一步步爬向数据分布**，最终到达一个真实样本。生成 = 跟着 score 爬山。

## 4. 怎么学 Score：Score Matching

我们训练一个网络 `s_θ(x)` 去逼近真实 score `∇ log p(x)`。直接算真实 score 不可能（`p` 未知），但有个巧妙办法叫 **denoising score matching**：

```text
关键事实：对加了高斯噪声的数据，
  "预测噪声" 与 "估计 score" 在数学上等价！

具体：score 方向 ≈ -(噪声方向) / 噪声标准差
```

所以：

> DDPM 的“预测噪声”和 Score-based 的“估计 score”本质是同一件事，只差一个符号和缩放。这就是两套理论的统一点。

## 5. 多噪声尺度（NCSN 的关键洞察）

单一噪声不够：数据密集区域 score 好学，空旷区域（噪声多）score 难学。

解决：**用多个噪声尺度**，从大噪声（覆盖全空间，方便起步）到小噪声（精修细节）。这与 DDPM 的“多时间步”完全对应。

```text
大噪声：粗略指明大方向（从纯噪声起步也有箭头可循）
小噪声：精细修正（接近真实数据时雕刻细节）
```

## 6. 采样：Langevin 动力学

知道了 score，用 **朗之万采样** 从噪声爬向数据：

```text
x ← x + η · score(x) + √(2η) · z,   z ~ N(0,1)

直觉：每步沿 score（上山方向）走一点，再加一点随机扰动（防止卡住）
重复多次，x 就从随机点漂移到高密度区（真实样本）
```

## 7. 统一视角：SDE（随机微分方程）

Song et al. (2021) 用 SDE 把一切统一起来：

```text
前向 SDE：连续地往数据加噪 -> 最终变成纯噪声（对应 DDPM 前向）
反向 SDE：从噪声出发，沿 score 反向积分 -> 还原数据（对应 DDPM 反向）

DDPM、SMLD（score matching）都是这个 SDE 框架的离散特例。
```

一张关系图：

```text
            统一在 SDE 框架下
   DDPM(预测噪声) ≈ Score-based(估计score) ≈ 反向 SDE 积分
                       │
                       v
              Flow Matching（下一章，用 ODE 进一步简化）
```

## 8. 核心代码直觉（Langevin 采样）

```python
import torch

@torch.no_grad()
def langevin_sample(score_model, shape, n_steps=1000, step=1e-4):
    x = torch.randn(shape)                       # 从纯噪声起步
    for _ in range(n_steps):
        s = score_model(x)                       # 估计 score（上山方向）
        x = x + step * s + (2 * step) ** 0.5 * torch.randn_like(x)
    return x                                      # 漂移到高密度区 = 生成样本
```

## 经典论文与开源项目

- Song & Ermon, "Generative Modeling by Estimating Gradients of the Data Distribution" (NCSN), 2019。
- Song et al., "Score-Based Generative Modeling through SDEs", 2021（统一框架，必读）。
- Vincent, "A Connection Between Score Matching and Denoising Autoencoders", 2011（理论基础）。
- GitHub: `yang-song/score_sde_pytorch`（作者官方实现）。
- 博客：Yang Song, "Generative Modeling by Estimating Gradients of the Data Distribution"。

## 本章小结

Score 是“对数密度的梯度”，即指向真实数据的“上山箭头”。学会 score 后，用朗之万动力学从噪声爬向数据即可生成。Score-based 与 DDPM 的“预测噪声”本质等价，并在 SDE 框架下统一。这个几何视角为下一章的 Flow Matching 铺路。
