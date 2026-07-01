# 05 扩散模型 Diffusion Models 原理详解

## 1. 它解决什么问题

GAN 清晰但难训，VAE 稳定但偏糊。扩散模型（Diffusion）两头兼顾：**训练稳定 + 生成质量最高**，是当前文生图、视频生成的主流内核（Stable Diffusion、DALL·E、Sora、Wan 都基于它）。

## 2. 一句话直觉

> 扩散模型干两件事：**前向**——把一张清晰图片一步步加噪声，直到变成纯噪声；**反向**——训练一个网络学会“去噪”，从纯噪声一步步还原出清晰图片。生成时就从随机噪声出发，反复去噪，“雕刻”出一张图。

生活类比：

```text
前向（破坏）：一张照片慢慢被雪花噪声盖住，最后全是雪花点
反向（重建）：训练一个"修复师"，每次去掉一点点噪声
生成：    给修复师一团纯雪花，让它一步步修复成一张全新的照片
```

为什么比 GAN 稳：它把“一步到位生成”这个超难任务，拆成了“去掉一点点噪声”这种**很简单的小任务**，重复几百上千次完成。

## 3. 前向过程（加噪，无需学习）

逐步往图像加高斯噪声，共 `T` 步（如 1000 步）：

```text
x_0（原图）-> x_1 -> x_2 -> ... -> x_T（近似纯高斯噪声）

每一步：x_t = √(1-β_t) · x_{t-1} + √β_t · ε,   ε ~ N(0,1)
β_t 是预设的小噪声系数（noise schedule）
```

一个好用的性质：可以**一步直接算出任意时刻 `x_t`**（不用真的循环加 t 次）：

```text
x_t = √(ᾱ_t) · x_0 + √(1-ᾱ_t) · ε,   其中 ᾱ_t = ∏(1-β_i)
```

这让训练时能随机抽一个时间步 `t` 直接构造样本。

## 4. 反向过程（去噪，要学习）

反向是真正要训练的部分：学一个网络 `ε_θ(x_t, t)`，**预测 `x_t` 里被加进去的噪声**。

```text
输入：带噪图 x_t 和 时间步 t
输出：预测的噪声 ε
```

知道了噪声，就能往回退一步，得到更清晰的 `x_{t-1}`。重复 T 次，从纯噪声 `x_T` 还原出 `x_0`。

## 5. 损失函数：简单到惊人

DDPM 论文证明，训练目标可以简化成一行——**让网络预测的噪声接近真实加入的噪声**：

```text
Loss = E[ || ε - ε_θ(x_t, t) ||² ]

即：随机取一张图 x_0、一个时间步 t、一个噪声 ε，
   构造 x_t，让网络预测 ε，用 MSE 对齐。
```

就是个 MSE 回归！这正是扩散模型训练稳定的原因。

## 6. 训练与采样流程

```text
训练：
  1. 取一张真图 x_0
  2. 随机取时间步 t、噪声 ε
  3. 构造 x_t = √ᾱ_t·x_0 + √(1-ᾱ_t)·ε
  4. 网络预测 ε_θ(x_t, t)，用 MSE(ε, ε_θ) 反向更新

采样（生成）：
  1. 从 N(0,1) 取纯噪声 x_T
  2. for t = T..1: 用 ε_θ 预测噪声，去噪得到 x_{t-1}
  3. 得到 x_0，一张新图
```

## 7. 网络结构：U-Net + 时间嵌入

去噪网络 `ε_θ` 通常用 **U-Net**（带下采样-上采样和跳跃连接的 CNN，擅长图像到图像），并把时间步 `t` 编码成嵌入注入各层（让网络知道“现在去噪到第几步”）。文生图里还会注入文本条件（见第 8 章）。

```text
x_t ──> U-Net(下采样→瓶颈→上采样, 跳跃连接) ──> 预测噪声 ε
         ↑ 注入时间步 t 嵌入（+ 文本条件）
```

## 8. 核心代码（训练一步）

```python
import torch

def diffusion_train_step(model, x0, alphas_bar, optimizer):
    B = x0.size(0)
    t = torch.randint(0, len(alphas_bar), (B,), device=x0.device)  # 随机时间步
    abar = alphas_bar[t].view(B, 1, 1, 1)
    eps = torch.randn_like(x0)                                     # 真实噪声
    x_t = abar.sqrt() * x0 + (1 - abar).sqrt() * eps               # 构造带噪图
    eps_pred = model(x_t, t)                                       # 预测噪声
    loss = ((eps - eps_pred) ** 2).mean()                          # MSE
    optimizer.zero_grad(); loss.backward(); optimizer.step()
    return loss.item()
```

## 9. 加速采样

原始 DDPM 要 1000 步采样，很慢。改进：

```text
DDIM：     确定性采样，几十步即可
DPM-Solver：把采样看成解微分方程，10~20 步出图
潜空间扩散(LDM)：在低维隐空间扩散（Stable Diffusion 的关键，省算力）
```

## 经典论文与开源项目

- Sohl-Dickstein et al., 2015（扩散思想起源）。
- Ho et al., "Denoising Diffusion Probabilistic Models" (DDPM), 2020（必读）。
- Song et al., "DDIM", 2020（加速采样）。
- Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", 2022（Stable Diffusion）。
- GitHub: `huggingface/diffusers`（首选）、`lucidrains/denoising-diffusion-pytorch`（简洁实现，适合学习）。
- 博客：Lilian Weng, "What are Diffusion Models?"（最佳图解综述）。

## 本章小结

扩散模型把“生成”拆成“前向加噪 + 反向去噪”，训练目标简化为“预测噪声”的 MSE，因此既稳定又高质量。去噪网络通常是注入时间步的 U-Net。它是现代文生图与视频生成的内核。下一章用 Score-based 视角，给扩散一个更统一直观的解释。
