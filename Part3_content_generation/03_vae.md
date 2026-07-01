# 03 最基础的生成模型 VAE

## 1. 它解决什么问题

普通自编码器（Autoencoder）能把图片压缩成一个向量再还原，但它的隐空间是“散点”，**没法用来生成新图**：你随便取一个向量解码，往往得到噪声。

VAE（Variational Autoencoder，变分自编码器）的目标：

> 让隐空间变成一个**规整、连续的概率分布**（通常是标准正态），这样就能从中随机采样、解码出有意义的新图。

## 2. 一句话直觉

> VAE = 自编码器 + “把隐空间逼成正态分布”的约束。编码器不再输出一个点，而是输出一个“分布”（均值和方差），从中采样再解码。

生活类比：普通自编码器把每张脸记成地图上一个孤立的点，点与点之间是空白（解码出来是乱码）；VAE 强迫所有脸的编码挤成一团规整的“云”（正态分布），云里任意一点解码出来都是一张合理的脸。

## 3. 结构

```text
            编码器                      解码器
  x ──> [Encoder] ──> (μ, σ) ──采样──> z ──> [Decoder] ──> x_hat
 输入图        输出"分布"参数    隐变量          重建图

采样用重参数化:  z = μ + σ * ε,  ε ~ N(0, 1)
```

- 编码器输出隐变量分布的均值 `μ` 和标准差 `σ`。
- 从 `N(μ, σ²)` 采样得到 `z`。
- 解码器把 `z` 还原成图像。

## 4. 重参数化技巧（Reparameterization）

问题：从 `N(μ, σ²)` 采样这一步是随机的，**随机采样不可导**，梯度没法回传到编码器。

技巧：把随机性“挪到外面”——

```text
不可导写法： z ~ N(μ, σ²)
可导写法：   z = μ + σ * ε,  其中 ε ~ N(0,1) 是外部噪声
```

这样 `z` 对 `μ`、`σ` 可导，随机性被隔离到与参数无关的 `ε` 里。这是 VAE 能用梯度训练的关键。

## 5. 损失函数：ELBO

上一章说过 `p_θ(x)` 算不出来，VAE 转而最大化它的**下界 ELBO**（证据下界），等价于最小化两项之和：

```text
VAE Loss = 重建损失 + KL 正则

重建损失：x_hat 要像 x（MSE 或交叉熵）—— 保证还原得好
KL 项：   让编码分布 N(μ,σ²) 靠近标准正态 N(0,1) —— 保证隐空间规整可采样
```

两项的拉扯很直观：

```text
只要重建好 -> 隐空间会乱（退化成普通自编码器，不能生成）
只要分布正 -> 还原会糊（信息丢失）
ELBO 让两者平衡
```

## 6. 生成新图（采样）

训练完后，**丢掉编码器**，直接：

```text
从 N(0,1) 采样 z  ->  解码器 Decoder(z)  ->  一张新图
```

因为隐空间被逼成了标准正态，随便采样都能得到合理图像。

## 7. 手写 VAE 生成 MNIST（PyTorch 核心代码）

```python
import torch
from torch import nn
import torch.nn.functional as F

class VAE(nn.Module):
    def __init__(self, x_dim=784, h=400, z_dim=20):
        super().__init__()
        self.fc1 = nn.Linear(x_dim, h)
        self.fc_mu = nn.Linear(h, z_dim)       # 输出均值
        self.fc_logvar = nn.Linear(h, z_dim)   # 输出 log 方差（更稳定）
        self.fc2 = nn.Linear(z_dim, h)
        self.fc3 = nn.Linear(h, x_dim)

    def encode(self, x):
        h = F.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)            # ε ~ N(0,1)
        return mu + eps * std                  # 重参数化

    def decode(self, z):
        return torch.sigmoid(self.fc3(F.relu(self.fc2(z))))

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar

def vae_loss(x_hat, x, mu, logvar):
    recon = F.binary_cross_entropy(x_hat, x, reduction="sum")   # 重建
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())  # KL
    return recon + kld

# 生成：训练后从标准正态采样并解码
# z = torch.randn(64, 20); imgs = model.decode(z).view(-1,1,28,28)
```

把 MNIST 拉平成 784 维输入，训练几个 epoch，就能从 `randn` 采样生成手写数字。换成人脸数据集（如 CelebA）并把全连接换成卷积，就能生成人脸——只是 VAE 生成的人脸通常偏模糊（这是它的固有缺点）。

## 8. VAE 的优缺点

```text
优点：训练稳定、有规整可解释的隐空间、能做插值（两张脸之间平滑过渡）
缺点：生成图偏模糊（KL 约束 + 重建损失平均化导致）
```

VAE 偏糊正是 GAN（更清晰）和 Diffusion（最清晰）要改进的地方。

## 经典论文与开源项目

- Kingma & Welling, "Auto-Encoding Variational Bayes", 2013（VAE 原始论文）。
- Higgins et al., "β-VAE", 2017（控制解耦表示）。
- van den Oord et al., "VQ-VAE", 2017（离散隐空间，后来影响文生图）。
- GitHub: `pytorch/examples` 里的 `vae`；`AntixK/PyTorch-VAE`（多种 VAE 变体合集）。

## 本章小结

VAE 用“概率编码器 + 解码器 + 重参数化”把隐空间逼成标准正态，从而能采样生成新图。损失是“重建 + KL”两项（ELBO）。它训练稳、隐空间可解释，但生成偏糊。下一章的 GAN 用对抗思路换来更清晰的图像。
