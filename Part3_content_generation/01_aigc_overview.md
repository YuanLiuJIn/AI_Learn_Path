# 01 AIGC 生成模型原理综述

## 1. 判别模型 vs 生成模型

这是理解整章的第一把钥匙。

```text
判别模型 (Discriminative)：学 P(y | x)
  给定一张图 x，判断它是猫还是狗。
  只关心"边界"：怎么把不同类分开。

生成模型 (Generative)：学 P(x) 或 P(x | y)
  学会"猫长什么样"，然后能画出一只新的猫。
  关心"分布"：数据本身是怎么分布的。
```

一句话直觉：

> 判别模型是“考官”，只判断对错；生成模型是“画家”，能创造新作品。

## 2. 生成模型到底在干什么

真实世界的图片（比如所有人脸）在高维空间里构成一个**分布** `p_data(x)`。生成模型的目标：

> 学一个模型分布 `p_θ(x)`，让它尽量接近真实分布 `p_data(x)`；然后从 `p_θ` 里**采样**，得到新样本。

```text
训练：让 p_θ(x) ≈ p_data(x)
生成：从 p_θ 采样 x_new（训练集里没出现过的新图）
```

难点在于：图像维度极高（一张 256×256×3 的图有近 20 万维），直接建模这么高维的分布几乎不可能。各种生成模型的差别，就在于**用什么巧妙办法绕过这个难题**。

## 3. 四大类生成模型的核心差异

| 模型 | 怎么建模分布 | 怎么采样 | 特点 |
|---|---|---|---|
| VAE | 用编码器压到低维隐空间 + 解码器还原 | 隐空间采样 → 解码 | 训练稳，但图偏糊 |
| GAN | 不显式建分布，靠对抗逼近 | 噪声 → 生成器 | 图清晰，但训练不稳 |
| Diffusion | 把生成拆成多步去噪 | 噪声 → 逐步去噪 | 质量最高，采样慢 |
| 自回归 (如 PixelCNN/GPT) | 逐元素预测下一个 | 一个一个生成 | 可控，但慢 |

记一个对比框架：每种生成模型都要回答三个问题——

```text
1. 怎么表示分布？
2. 怎么训练（损失是什么）？
3. 怎么从中采样？
```

## 4. 一张演化地图

```text
2013  VAE（变分自编码器，Kingma & Welling）
2014  GAN（对抗生成，Goodfellow）
2015  Diffusion 思想雏形（Sohl-Dickstein）
2020  DDPM（扩散模型真正爆发，Ho et al.）
2021  Score-based SDE（Song et al.，统一视角）
2021  CLIP（连接图文）+ Stable Diffusion 路线
2022  文生图爆发（DALL·E 2、Imagen、Stable Diffusion）
2023  Flow Matching（统一框架，Lipman et al.）
2024+ 视频生成（Sora、Wan 等）
```

## 5. 为什么生成模型现在这么重要

```text
图像：Midjourney、Stable Diffusion
视频：Sora、Wan、可灵
语音：TTS、音乐生成
文本：GPT 本质也是自回归生成模型
3D / 分子 / 蛋白质设计：AlphaFold 之后的生成式科学
```

生成模型是 AIGC（AI Generated Content）的技术内核。

## 6. 本章要建立的直觉

后面每一章，你都用这套提问法去理解：

```text
- 它把"生成"这件事拆成了什么子问题？
- 它的损失函数本质是在让 p_θ 靠近 p_data（都源于最大似然，见下一章）
- 采样时，噪声是怎么一步步变成图像的？
```

## 经典论文与开源项目

- Kingma & Welling, "Auto-Encoding Variational Bayes" (VAE), 2013.
- Goodfellow et al., "Generative Adversarial Networks", 2014.
- Ho et al., "Denoising Diffusion Probabilistic Models" (DDPM), 2020.
- GitHub: `huggingface/diffusers`（最主流的扩散模型库，强烈推荐）。
- GitHub: `CompVis/stable-diffusion`、`Stability-AI/generative-models`。
- 课程：MIT 6.S978 Deep Generative Models；Stanford CS236。

## 本章小结

生成模型学的是数据分布 `p_data(x)`，目标是采样出新样本。VAE、GAN、Diffusion、自回归是四条主要路线，差别在于“如何建模分布、如何训练、如何采样”。它们的损失函数大多可以追溯到同一个根基——最大似然估计，这是下一章的内容。
