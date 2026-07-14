# 02. Embedding 与跨模态对齐

> 目标：理解多模态检索的底层原理：不同模态为什么能互相搜索。

## 1. 什么是 Embedding？

Embedding 是把一个对象变成向量。

```text
文本：“一只猫坐在沙发上”
  ↓ Text Encoder
向量：[0.12, -0.33, 0.88, ...]

图片：猫坐在沙发上的照片
  ↓ Image Encoder
向量：[0.10, -0.31, 0.85, ...]
```

如果两个向量距离近，就表示语义相似。

常见相似度：

```text
内积：        score = q · x
余弦相似度：  score = q · x / (||q|| ||x||)
L2 距离：     distance = ||q - x||²
```

在大规模检索中，通常会把向量归一化，然后用内积近似余弦相似度。

## 2. 单模态 Embedding vs 多模态 Embedding

单模态文本检索：

```text
文本 Query → 文本 Encoder → 文本向量
文本文档   → 文本 Encoder → 文本向量
```

多模态检索：

```text
文本 Query → Text Encoder  → 向量
图片数据   → Image Encoder → 向量
视频片段   → Video Encoder → 向量
音频片段   → Audio Encoder → 向量
```

关键问题是：

> 不同 Encoder 输出的向量必须处在可比较的语义空间里。

否则文本向量和图片向量没有可比性。

## 3. 跨模态对齐是什么？

跨模态对齐就是让不同模态表达同一语义时，向量距离更近。

```text
文本：“一只狗在草地上奔跑”
图片：狗在草地上奔跑的照片

训练目标：
  text_embedding 和 image_embedding 越近越好
```

同时，不匹配的样本要远离：

```text
文本：“一只狗在草地上奔跑”
图片：一辆汽车在公路上行驶

训练目标：
  两个向量越远越好
```

## 4. CLIP 的核心思想：对比学习

CLIP 类模型的训练数据是一批图文对：

```text
(image_1, text_1)
(image_2, text_2)
...
(image_N, text_N)
```

模型包括两个编码器：

```text
Image Encoder: image → image_embedding
Text Encoder:  text  → text_embedding
```

对一个 batch 来说，正确配对在对角线上：

```text
              text_1   text_2   text_3
image_1        正确     错误     错误
image_2        错误     正确     错误
image_3        错误     错误     正确
```

训练目标：

```text
正确图文对相似度高
错误图文对相似度低
```

也就是 InfoNCE / Contrastive Loss。

## 5. 对比学习公式的直觉

对于第 i 张图片，它对应的正确文本是 text_i。

模型希望：

```text
sim(image_i, text_i) 高
sim(image_i, text_j) 低，j ≠ i
```

可以写成：

\[
L_i = -\log \frac{\exp(sim(I_i, T_i) / \tau)}{\sum_j \exp(sim(I_i, T_j) / \tau)}
\]

人话翻译：

```text
分子：正确图文对的相似度
分母：这张图和 batch 中所有文本的相似度总和
目标：让正确文本在所有候选中概率最大
```

\(\tau\) 是温度系数，用来控制分布的尖锐程度。

## 6. 为什么 CLIP 能文本搜图片？

训练完成后：

```text
文本：“穿红色衣服的人在滑雪”
  ↓ Text Encoder
query_vector

图片库中每张图片
  ↓ Image Encoder
image_vector

计算 query_vector 和 image_vector 的相似度
  ↓
返回最相似的图片
```

因为训练时模型已经学会：

```text
文本语义和图片语义要在同一空间对齐。
```

所以文本和图片可以直接相似度比较。

## 7. ImageBind：把更多模态绑定到一个空间

CLIP 主要对齐文本和图片。

ImageBind 进一步希望把更多模态绑定到统一空间：

```text
文本
图片
音频
视频
深度图
热成像
IMU 传感器
```

它的直觉是：

```text
同一个事件往往同时产生多种信号。
例如“狗叫”：
  有狗的图片
  有狗叫音频
  有视频画面
  有文本描述
```

如果这些模态都对齐到同一个空间，就可以支持：

```text
文本搜音频
音频搜图片
图片搜视频
视频搜文本
```

## 8. 多模态检索的几种对齐方式

### 8.1 双塔结构

```text
Query Encoder      Document Encoder
文本/图片/音频  →  向量
文档/图片/视频  →  向量
```

优点：

```text
可以离线预计算文档向量
在线检索速度快
适合大规模召回
```

缺点：

```text
Query 和 Document 交互较弱
精度不如 Cross-Encoder
```

### 8.2 Cross-Encoder

把 Query 和候选一起输入模型：

```text
[Query, Document/Image] → 模型 → 相关性分数
```

优点：

```text
相关性判断更准
适合 Rerank
```

缺点：

```text
每个候选都要跑一次模型
成本高，不能用于全库召回
```

### 8.3 Late Interaction

代表思想：不要把整篇文档压成一个向量，而是保留 token/patch 级别表示。

```text
Query tokens → 多个向量
Document tokens/patches → 多个向量

通过 MaxSim 等方式计算细粒度匹配
```

优点：

```text
比单向量更细粒度
比 Cross-Encoder 更容易预计算
```

适合复杂文档、图文混排文档、长文本检索。

## 9. 多模态表示的常见问题

### 9.1 语义鸿沟

图片和文本天然不是同一种信息。

```text
图片中有颜色、位置、布局、纹理
文本中有抽象概念、逻辑关系、命名实体
```

对齐并不完美，尤其是细粒度属性：

```text
“左边第二个蓝色按钮”
“第 3 行第 2 列的数值”
“穿红衣服的人后面那辆车”
```

### 9.2 长尾概念

训练数据中少见的专业概念、内部术语、领域图片，通用模型可能不懂。

解决方式：

```text
领域数据微调
领域 Caption 生成
领域词表和稀疏检索补充
Rerank 精排
```

### 9.3 向量空间坍缩和 hubness

高维空间里有些向量会成为“万能近邻”，被很多 query 命中。

常见缓解：

```text
向量归一化
温度调节
负样本优化
重排
多路召回融合
```

## 10. 一句话总结

> 多模态检索的底层是跨模态表示学习：通过对比学习等方法，让文本、图片、音频、视频等不同模态的语义表示进入同一个可比较的向量空间。双塔模型负责大规模召回，Cross-Encoder 或 Late Interaction 负责高质量重排。