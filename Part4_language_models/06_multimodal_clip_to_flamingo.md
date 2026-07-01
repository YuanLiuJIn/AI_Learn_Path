# 06 从 CLIP 到 Flamingo：语言模型的多模态之路

> 本部分完结篇。讲清楚语言模型如何“长出眼睛”——从只懂文字，到能看懂图像。

## 1. 它解决什么问题

前面的模型只处理文字。但真实世界是多模态的（图、文、声、视频）。多模态要解决：

> 怎么让模型**同时理解图像和文字**，并把两者关联起来（看图说话、按文搜图、视觉问答）？

两个关键里程碑：CLIP（对齐图文）和 Flamingo（让语言模型看图对话）。

## 2. CLIP：把图像和文字对齐到同一空间

### 2.1 一句话直觉

> CLIP 训练两个编码器（一个看图、一个读字），让“一张图”和“描述它的文字”在向量空间里**靠得很近**，不匹配的则推远。学完后，图和文就能直接比较了。

### 2.2 对比学习（Contrastive Learning）

```text
拿 4 亿对(图, 文字描述)训练：
  图像编码器 -> 图像向量
  文本编码器 -> 文本向量

目标：匹配的(图,文)向量相似度高，不匹配的相似度低
  一个 batch 里 N 张图 × N 句话 -> N×N 相似度矩阵
  对角线(正确配对)拉高，其余拉低
```

```text
   猫图  狗图  车图
猫文 ■(高)  低    低
狗文  低   ■(高)  低
车文  低    低   ■(高)
```

### 2.3 神奇能力：零样本分类

训练完，不需要再训练就能分类任意类别：

```text
给一张图，和一组文字 "a photo of a cat" / "a photo of a dog" / ...
看图向量和哪个文字向量最接近 -> 就是哪一类
```

这叫 zero-shot：没见过的类别，只要能用文字描述就能分类。CLIP 也成了文生图（Part3）的文本理解基石。

## 3. 从“对齐”到“对话”：让 LLM 看图

CLIP 能对齐图文，但不能“看着图聊天”。要让一个强大的语言模型（只懂文字）接受图像输入，需要把图像“翻译”成它能懂的形式。

### 3.1 基本套路

```text
图像 ──[视觉编码器(如CLIP)]──> 图像特征
图像特征 ──[连接器/投影]──> "视觉 token"（伪装成语言模型能读的向量）
视觉 token + 文字 token ──> 大语言模型 ──> 回答
```

把图像变成一串“视觉 token”插进文字序列，LLM 就能“边看图边说话”。

## 4. Flamingo：少样本视觉语言模型

Flamingo（DeepMind 2022）是这条路的代表：

```text
1. 冻结一个强大的预训练 LLM（不动它，省算力、保住语言能力）
2. 冻结一个视觉编码器
3. 只训练中间的"连接组件"：
   - Perceiver Resampler：把任意数量的图像特征压成固定数量的视觉 token
   - Gated Cross-Attention：在 LLM 各层插入门控交叉注意力，让文字"看到"图像
4. 支持图文交错输入，能做少样本视觉问答
```

关键设计哲学：

> 不重新训练庞大的 LLM 和视觉模型，只训练“桥梁”，用少量算力让语言模型获得视觉能力。

这也是后续大量多模态模型（BLIP-2、LLaVA、Qwen-VL 等）的通用思路。

## 5. 多模态演化地图

```text
CLIP (2021)：图文对齐，零样本分类，文生图基石
       │
ALIGN / BLIP：改进的图文预训练
       │
Flamingo (2022)：冻结 LLM + 连接器 -> 看图对话、少样本
       │
BLIP-2 (2023)：Q-Former 连接器，更高效
       │
LLaVA / Qwen-VL / GPT-4V (2023+)：指令微调的多模态对话模型
       │
       v
原生多模态大模型（统一处理图/文/音/视频）
```

## 6. 代码直觉（用 CLIP 做零样本分类）

```python
import torch, clip
from PIL import Image

model, preprocess = clip.load("ViT-B/32")
image = preprocess(Image.open("cat.jpg")).unsqueeze(0)
texts = clip.tokenize(["a photo of a cat", "a photo of a dog"])

with torch.no_grad():
    logits_per_image, _ = model(image, texts)
    probs = logits_per_image.softmax(dim=-1)   # 哪个描述最匹配
print(probs)   # cat 概率更高
```

## 7. 与其他部分的关系

```text
Part2 Transformer/Attention -> 多模态用交叉注意力连接图文
Part3 文生图               -> 用的就是 CLIP 文本编码器
Part4 LLM                  -> Flamingo 复用冻结的 LLM
Part6 大模型工程            -> 多模态训练同样面临数据/算力挑战
```

## 经典论文与开源项目

- Radford et al., "Learning Transferable Visual Models From Natural Language Supervision" (CLIP), 2021（必读）。
- Alayrac et al., "Flamingo: a Visual Language Model for Few-Shot Learning", 2022。
- Li et al., "BLIP-2", 2023。
- Liu et al., "LLaVA", 2023（开源多模态对话，易上手）。
- GitHub: `openai/CLIP`、`mlfoundations/open_clip`、`haotian-liu/LLaVA`、`salesforce/LAVIS`。

## 本章小结

多模态让语言模型“长出眼睛”。CLIP 用对比学习把图文对齐到同一空间，实现零样本分类并成为文生图基石；Flamingo 用“冻结 LLM + 训练连接器”的思路让语言模型看图对话，确立了后续多模态大模型的通用范式。至此，语言模型从纯文本走向图文统一，为通用多模态智能铺路。
