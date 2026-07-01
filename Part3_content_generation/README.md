# Part3_content_generation：内容生成（AIGC）篇

本部分讲清楚“机器如何生成新内容”——图像、人脸、视频。前两部分你已经掌握了神经网络和 Transformer，这一部分进入**生成模型**：不再只是判别（分类/回归），而是学会数据的分布，从而创造出训练集里没有的新样本。

## 一条主线：生成模型的演化

```text
最大似然估计 (MLE)  ← 所有生成模型损失函数的共同根基
        │
        ├── VAE：用概率编码-解码，显式建模分布
        ├── GAN：生成器 vs 判别器，对抗博弈
        └── Diffusion：一步步去噪，当前最强
                │
                ├── Score-based：从"分数"视角理解扩散
                └── Flow Matching：用最优传输统一各种生成模型
                        │
                        v
                文生图（Text-to-Image）→ 视频生成
```

## 章节顺序

1. `01_aigc_overview.md`：AIGC 生成模型原理综述
2. `02_mle_behind_loss.md`：损失函数背后是最大似然估计
3. `03_vae.md`：最基础的生成模型 VAE（生成手写数字与人脸）
4. `04_gan.md`：当年最火的 GAN（生成明星人脸）
5. `05_diffusion_models.md`：扩散模型 Diffusion 原理详解
6. `06_score_based_diffusion.md`：最易理解的扩散模型——Score-based
7. `07_flow_matching.md`：大一统的生成模型 Flow Matching（含训练 Coding）
8. `08_text_to_image.md`：时下最先进的文生图模型原理解析
9. `09_video_generation.md`：视频生成原理与 Wan 研究（含视频 Agent Demo）
10. `references.md`：论文、教材、开源项目

## 前置要求

- Part1：概率、最大似然、损失函数、梯度下降、PyTorch。
- Part2：CNN、Attention、Transformer、残差与 LayerNorm。
- 不熟的名词查根目录 `glossary.md`。

## 学完后应达到

- 能解释判别模型与生成模型的区别。
- 能说清 VAE、GAN、Diffusion 三者“在优化什么、怎么采样、各自优缺点”。
- 能用一句话讲明白“扩散就是学会把噪声一步步变回图像”。
- 能理解 Score / Flow Matching 是从不同视角看同一件事。
- 能讲清文生图（如 Stable Diffusion）和视频生成的核心组件。
