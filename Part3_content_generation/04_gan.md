# 04 当年最火的生成模型 GAN

## 1. 它解决什么问题

VAE 生成的图偏糊。GAN（Generative Adversarial Networks，生成对抗网络）用一个全新思路追求**清晰逼真**：不去显式计算概率，而是让两个网络“互相博弈”，在对抗中把生成质量逼上去。

GAN 在 2014–2020 年间是最火的生成模型，催生了“以假乱真的明星人脸”等惊艳效果。

## 2. 一句话直觉

> GAN = 造假者 vs 鉴定师。造假者（生成器）努力造出以假乱真的画，鉴定师（判别器）努力分辨真假。两者对抗升级，最终造假者画得连鉴定师都分不出来。

生活类比：

```text
生成器 G（造假者）：拿一团随机噪声，努力画出"像真的"的人脸
判别器 D（鉴定师）：看一张图，判断是真实照片还是 G 造的假图
对抗：G 想骗过 D，D 想抓住 G，反复较量 -> G 越来越强
```

## 3. 结构与博弈

```text
噪声 z ~ N(0,1) ──> [生成器 G] ──> 假图 G(z) ┐
                                              ├──> [判别器 D] ──> 真/假 概率
真实图 x ─────────────────────────────────────┘
```

训练目标是一个**极小极大博弈（minimax）**：

```text
min_G max_D  E[log D(x)] + E[log(1 - D(G(z)))]

D 想：对真图输出 1，对假图输出 0（最大化）
G 想：让 D(G(z)) 接近 1，即骗过 D（最小化上式第二项）
```

直觉：

```text
D 的目标：真的说真，假的说假
G 的目标：让自己造的假图被 D 当成真
```

## 4. 训练流程（交替优化）

```text
重复：
  1. 固定 G，训练 D：用一批真图(标1) + 一批假图(标0)，让 D 学会分辨
  2. 固定 D，训练 G：生成假图喂给 D，希望 D 判为真，反向更新 G
```

两个网络轮流进步，像跷跷板。

## 5. GAN 为什么难训练

这是 GAN 的著名痛点：

| 问题 | 含义 |
|---|---|
| 训练不稳定 | 两个网络的博弈可能震荡、不收敛 |
| 模式崩溃 (mode collapse) | G 偷懒只生成几种样本（比如只会画一种脸）骗过 D |
| 梯度消失 | D 太强时，G 得不到有用梯度 |
| 难以评估 | 没有明确的 loss 数值告诉你“训得好不好” |

后续大量工作（WGAN、WGAN-GP、谱归一化、StyleGAN）都在解决这些稳定性问题。

## 6. 手写 DCGAN 生成人脸（核心代码）

DCGAN 用卷积实现 GAN，是生成人脸的经典做法。

```python
import torch
from torch import nn

# 生成器：噪声 -> 图像（用转置卷积上采样）
class Generator(nn.Module):
    def __init__(self, z_dim=100, ngf=64, nc=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(z_dim, ngf*4, 4, 1, 0), nn.BatchNorm2d(ngf*4), nn.ReLU(),
            nn.ConvTranspose2d(ngf*4, ngf*2, 4, 2, 1), nn.BatchNorm2d(ngf*2), nn.ReLU(),
            nn.ConvTranspose2d(ngf*2, ngf,   4, 2, 1), nn.BatchNorm2d(ngf),   nn.ReLU(),
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1), nn.Tanh(),   # 输出 [-1,1] 的图
        )
    def forward(self, z): return self.net(z)

# 判别器：图像 -> 真/假分数
class Discriminator(nn.Module):
    def __init__(self, ndf=64, nc=3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(nc, ndf, 4, 2, 1), nn.LeakyReLU(0.2),
            nn.Conv2d(ndf, ndf*2, 4, 2, 1), nn.BatchNorm2d(ndf*2), nn.LeakyReLU(0.2),
            nn.Conv2d(ndf*2, ndf*4, 4, 2, 1), nn.BatchNorm2d(ndf*4), nn.LeakyReLU(0.2),
            nn.Conv2d(ndf*4, 1, 4, 1, 0), nn.Sigmoid(),
        )
    def forward(self, x): return self.net(x).view(-1)

# ---- 训练核心（在 CelebA 明星人脸数据集上）----
G, D = Generator(), Discriminator()
opt_G = torch.optim.Adam(G.parameters(), lr=2e-4, betas=(0.5, 0.999))
opt_D = torch.optim.Adam(D.parameters(), lr=2e-4, betas=(0.5, 0.999))
bce = nn.BCELoss()

for real in dataloader:                 # real: 真实人脸 batch
    b = real.size(0)
    # 1) 训练 D
    z = torch.randn(b, 100, 1, 1)
    fake = G(z)
    loss_D = bce(D(real), torch.ones(b)) + bce(D(fake.detach()), torch.zeros(b))
    opt_D.zero_grad(); loss_D.backward(); opt_D.step()
    # 2) 训练 G（希望 D 把 fake 判为真）
    loss_G = bce(D(fake), torch.ones(b))
    opt_G.zero_grad(); loss_G.backward(); opt_G.step()
```

在 CelebA 上训练，G 就能从随机噪声生成明星风格的人脸。StyleGAN 进一步让生成的人脸达到“以假乱真”的程度。

## 7. GAN 家族里程碑

| 模型 | 贡献 |
|---|---|
| DCGAN (2015) | 用卷积稳定 GAN，奠定图像生成范式 |
| WGAN / WGAN-GP (2017) | 用 Wasserstein 距离大幅改善训练稳定性 |
| pix2pix / CycleGAN (2017) | 图像翻译（马变斑马、照片变油画）|
| StyleGAN 1/2/3 (2019–2021) | 高分辨率、可控的逼真人脸生成 |

## 8. GAN vs VAE vs Diffusion

```text
VAE：       训练稳、图偏糊、隐空间规整
GAN：       图清晰、训练难、可能模式崩溃
Diffusion： 质量最高、训练稳、但采样慢（下一章）
```

2021 年后，Diffusion 在图像质量上全面超越 GAN，成为主流；但 GAN 的对抗思想（如 GAN loss 做感知增强）仍被广泛借用。

## 经典论文与开源项目

- Goodfellow et al., "Generative Adversarial Networks", 2014（开山之作）。
- Radford et al., "DCGAN", 2015。
- Arjovsky et al., "Wasserstein GAN", 2017。
- Karras et al., "StyleGAN" 系列, 2019–2021。
- GitHub: `pytorch/examples` 的 `dcgan`；`NVlabs/stylegan3`；`eriklindernoren/PyTorch-GAN`（GAN 变体合集）。

## 本章小结

GAN 用生成器与判别器的对抗博弈来逼近数据分布，能生成清晰逼真的图像（如明星人脸），但训练不稳定、易模式崩溃。它在 2014–2020 年主导图像生成，之后被 Diffusion 在质量上超越，但对抗思想影响深远。
