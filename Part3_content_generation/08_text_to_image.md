# 08 时下最先进的文生图模型原理解析（Text-to-Image）

## 1. 它解决什么问题

前面的生成模型能生成图，但**不可控**——你只能随机采样，不能说“画一只戴帽子的柯基在月球上”。文生图（Text-to-Image）要解决的是：

> 让生成过程**听文字的指挥**：输入一句话，输出符合描述的图像。

代表作：DALL·E 2、Imagen、Stable Diffusion、Midjourney、Flux。

## 2. 一句话直觉

> 文生图 = 扩散模型（会画图）+ 文本编码器（懂人话）+ 一种把文字“注入”去噪过程的机制（让画图时一直盯着文字要求）。

## 3. 三大核心组件

以 Stable Diffusion 为代表，拆成三块：

```text
1. 文本编码器 (Text Encoder)：把句子变成向量（语义条件）
      "a corgi on the moon" ──CLIP/T5──> 文本嵌入

2. 扩散 U-Net (去噪网络)：在文本条件下一步步去噪
      噪声 + 文本嵌入 ──> 逐步去噪 ──> 图像隐表示

3. VAE 编解码器：在低维"隐空间"里扩散，省算力
      图像 <──VAE Decoder── 隐表示 ──VAE Encoder──> 图像
```

### 3.1 文本编码器：让模型懂人话

用 CLIP 或 T5 的文本编码器把 prompt 编码成向量。CLIP 尤其关键——它在海量图文对上训练，让“文字”和“图像”落在同一语义空间（详见 Part4 多模态章节）。

### 3.2 潜空间扩散（Latent Diffusion）：省算力的关键

直接在 512×512 像素上扩散太贵。Stable Diffusion 的核心技巧：

```text
先用 VAE 把图像压到小得多的隐空间（如 64×64）
在隐空间里做扩散（去噪）          <- 计算量降低几十倍
最后用 VAE 解码器还原成高清图像
```

这就是 LDM（Latent Diffusion Model），让文生图能在消费级显卡上跑。

### 3.3 条件注入：Cross-Attention

文本怎么影响去噪？用**交叉注意力**（Part2 学过）：U-Net 在去噪时，把图像特征作 Query，文本嵌入作 Key/Value，让每个图像区域“查询”文字描述，从而画出对应内容。

```text
图像特征(Query) × 文本嵌入(Key/Value) -> 注意力 -> 让图像对齐文字
"戴帽子" 这几个 token 会引导对应区域生成帽子
```

## 4. Classifier-Free Guidance（CFG）：让图更贴文字

一个极其重要的技巧。同一个模型既学“有文字条件的去噪”，也学“无条件去噪”，生成时把两者按比例外推：

```text
最终预测 = 无条件预测 + w · (有条件预测 - 无条件预测)
                          └──────── 引导强度 w ────────┘

w 越大：越严格贴合文字（但可能过饱和、不自然）
w 适中：兼顾贴合度与自然度（常用 7~8）
```

你在 Stable Diffusion WebUI 里调的 “CFG Scale” 就是这个 `w`。

## 5. 完整生成流程

```text
输入 prompt "a corgi on the moon"
  1. 文本编码器 -> 文本嵌入
  2. 隐空间取随机噪声
  3. U-Net 在文本条件下，配合 CFG，循环去噪 N 步
  4. VAE 解码器把隐表示还原成高清图
输出：一只在月球上的柯基
```

## 6. 主流文生图模型对比

| 模型 | 关键特点 |
|---|---|
| DALL·E 2 (2022) | CLIP 隐空间 + 扩散先验 |
| Imagen (2022) | 用大型 T5 文本编码器 + 级联超分 |
| Stable Diffusion (2022) | 潜空间扩散，开源，生态最繁荣 |
| SDXL / SD3 (2023–24) | 更大、用 Flow Matching（SD3）、多文本编码器 |
| Flux (2024) | Rectified Flow + DiT，质量领先 |

注意趋势：U-Net 正逐渐被 **DiT（Diffusion Transformer，用 Transformer 做去噪骨干）** 取代，这也是视频生成（Sora、Wan）的基础。

## 7. 控制与扩展

```text
ControlNet：    用边缘图/姿态/深度图额外控制构图
LoRA：          少量参数微调，定制画风/人物
Inpainting：    只重绘图像的指定区域
IP-Adapter：    用参考图控制风格
```

## 经典论文与开源项目

- Radford et al., "CLIP", 2021（图文对齐基础）。
- Ramesh et al., "DALL·E 2 / unCLIP", 2022。
- Saharia et al., "Imagen", 2022。
- Rombach et al., "Latent Diffusion (Stable Diffusion)", 2022（必读）。
- Ho & Salimans, "Classifier-Free Diffusion Guidance", 2022。
- Peebles & Xie, "Scalable Diffusion Models with Transformers" (DiT), 2023。
- GitHub: `huggingface/diffusers`、`Stability-AI/generative-models`、`lllyasviel/ControlNet`、`AUTOMATIC1111/stable-diffusion-webui`。

## 本章小结

文生图 = 扩散（会画）+ 文本编码器（懂话）+ 交叉注意力（把文字注入去噪）+ 潜空间扩散（省算力）+ CFG（贴合文字）。Stable Diffusion 是开源代表，去噪骨干正从 U-Net 走向 DiT。掌握这套组件，就能看懂几乎所有现代文生图系统，也为视频生成打下基础。
