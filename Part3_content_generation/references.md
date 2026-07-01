# 参考资料（内容生成篇）

## 通用教材与课程

- Goodfellow, Bengio, Courville, *Deep Learning*, 2016（第 20 章生成模型）。
- Stanford CS236: Deep Generative Models。
- MIT 6.S978: Deep Generative Models。
- 博客：Lilian Weng, "What are Diffusion Models?" / "From GAN to WGAN"（强烈推荐）。
- 博客：Yang Song, "Generative Modeling by Estimating Gradients of the Data Distribution"。

## 01 综述 / 02 MLE

- Bishop, *Pattern Recognition and Machine Learning*（MLE、KL 散度）。
- Stanford CS236 讲义（似然、变分推断）。

## 03 VAE

- Kingma & Welling, "Auto-Encoding Variational Bayes", 2013。
- Higgins et al., "β-VAE", 2017。
- van den Oord et al., "Neural Discrete Representation Learning" (VQ-VAE), 2017。
- GitHub: `AntixK/PyTorch-VAE`、`pytorch/examples`。

## 04 GAN

- Goodfellow et al., "Generative Adversarial Networks", 2014。
- Radford et al., "Unsupervised Representation Learning with DCGAN", 2015。
- Arjovsky et al., "Wasserstein GAN", 2017；Gulrajani et al., "WGAN-GP", 2017。
- Karras et al., "StyleGAN / StyleGAN2 / StyleGAN3", 2019–2021。
- GitHub: `NVlabs/stylegan3`、`eriklindernoren/PyTorch-GAN`。

## 05 Diffusion

- Sohl-Dickstein et al., 2015；Ho et al., "DDPM", 2020。
- Song et al., "DDIM", 2020；Lu et al., "DPM-Solver", 2022。
- GitHub: `huggingface/diffusers`、`lucidrains/denoising-diffusion-pytorch`。

## 06 Score-based

- Song & Ermon, "NCSN", 2019。
- Song et al., "Score-Based Generative Modeling through SDEs", 2021。
- GitHub: `yang-song/score_sde_pytorch`。

## 07 Flow Matching

- Lipman et al., "Flow Matching for Generative Modeling", 2022。
- Liu et al., "Rectified Flow", 2022。
- Esser et al., "SD3 / Scaling Rectified Flow Transformers", 2024。
- GitHub: `facebookresearch/flow_matching`、`gnobitab/RectifiedFlow`。

## 08 文生图

- Radford et al., "CLIP", 2021。
- Ramesh et al., "DALL·E 2", 2022；Saharia et al., "Imagen", 2022。
- Rombach et al., "Latent Diffusion (Stable Diffusion)", 2022。
- Ho & Salimans, "Classifier-Free Guidance", 2022。
- Peebles & Xie, "DiT", 2023。
- GitHub: `Stability-AI/generative-models`、`lllyasviel/ControlNet`、`AUTOMATIC1111/stable-diffusion-webui`。

## 09 视频生成

- Ho et al., "Video Diffusion Models", 2022。
- Blattmann et al., "Stable Video Diffusion", 2023。
- OpenAI Sora 技术报告, 2024。
- GitHub: `Wan-Video/Wan2.1`、`hpcaitech/Open-Sora`、`guoyww/AnimateDiff`。

## 学习建议

1. 先把 VAE、GAN、DDPM 三个最小 demo 跑通（MNIST 起步）。
2. 用 `huggingface/diffusers` 跑一次 Stable Diffusion 文生图，再回看第 8 章拆解组件。
3. 读 Lilian Weng 的扩散综述博客，配合本部分章节建立全局观。
4. 研读 `Wan2.1` 源码，把“VAE 压缩 + DiT + Flow Matching + 条件”串起来。
