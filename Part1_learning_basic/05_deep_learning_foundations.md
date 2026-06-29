# 05 深度学习基础

深度学习是大模型的直接基础。大语言模型、扩散模型、视觉模型、多模态模型，本质上都是大规模神经网络。

## 1. 神经网络的基本直觉

传统模型往往需要人手工设计特征。

深度学习希望模型自己从数据中学习表示。

例如图片识别：

- 低层学习边缘、颜色。
- 中层学习纹理、局部形状。
- 高层学习物体部件和整体语义。

对于文本：

- 低层可能学习词形、局部搭配。
- 高层学习句法、语义、任务相关模式。

## 2. 神经元

一个最简单的神经元可以写成：

```text
z = w1*x1 + w2*x2 + ... + wn*xn + b
a = activation(z)
```

它先做线性变换，再通过激活函数引入非线性。

如果没有激活函数，多层线性网络仍然等价于一层线性模型。

## 3. 张量

张量是深度学习中的基本数据结构。

| 维度 | 名称 | 例子 |
|---|---|---|
| 0 维 | 标量 | 一个损失值 |
| 1 维 | 向量 | 一个词向量 |
| 2 维 | 矩阵 | 一批样本的特征 |
| 3 维及以上 | 张量 | 图片 batch、文本 batch |

常见形状：

```text
表格数据: [batch_size, features]
图片数据: [batch_size, channels, height, width]
文本数据: [batch_size, sequence_length]
词嵌入: [batch_size, sequence_length, hidden_size]
```

大模型中的很多错误都来自 shape 理解不清。

## 4. 前向传播

前向传播是从输入计算输出的过程。

```text
输入 x -> 第 1 层 -> 第 2 层 -> ... -> 输出 y_hat
```

例如一个 MLP：

```text
h1 = ReLU(W1*x + b1)
h2 = ReLU(W2*h1 + b2)
y_hat = W3*h2 + b3
```

## 5. 损失函数

损失函数衡量模型输出和真实答案的差距。

常见损失：

- 回归：MSE、MAE。
- 分类：Cross Entropy。
- 语言模型：next token prediction 的 Cross Entropy。

训练神经网络就是让损失函数尽量变小。

## 6. 反向传播

反向传播用于计算每个参数对损失的影响。

直觉：

- 前向传播负责算预测。
- 损失函数负责算错了多少。
- 反向传播负责算每个参数应该怎么改。
- 优化器负责真正更新参数。

反向传播本质上是链式法则的大规模应用。

## 7. 梯度下降与优化器

最基本更新公式：

```text
参数 = 参数 - 学习率 × 梯度
```

常见优化器：

| 优化器 | 特点 |
|---|---|
| SGD | 简单、泛化常较好，但调参要求高 |
| Momentum | 加入动量，减少震荡 |
| RMSProp | 自适应学习率 |
| Adam | 常用，收敛快 |
| AdamW | 深度学习和大模型训练常用，解耦 weight decay |

大模型训练中 AdamW 非常常见。

## 8. 激活函数

激活函数提供非线性能力。

常见激活：

| 激活函数 | 特点 |
|---|---|
| Sigmoid | 输出 0 到 1，容易梯度消失 |
| Tanh | 输出 -1 到 1，也可能梯度消失 |
| ReLU | 简单高效，常用 |
| GELU | Transformer 中常见 |
| SiLU / Swish | 现代网络中常见 |

## 9. 梯度消失与梯度爆炸

### 梯度消失

梯度在反向传播中越来越小，前面层几乎学不到。

常见原因：

- 网络太深。
- 激活函数饱和。
- 初始化不合适。

### 梯度爆炸

梯度变得非常大，训练不稳定，损失可能变成 NaN。

常见解决方法：

- 合理初始化。
- 归一化层。
- 残差连接。
- 梯度裁剪。
- 调小学习率。

## 10. 正则化与泛化

深度学习中常见防过拟合方法：

- 更多数据
- 数据增强
- weight decay
- dropout
- early stopping
- batch normalization
- label smoothing

大模型场景中，数据规模、去重、质量控制和训练策略都影响泛化能力。

## 11. Batch Normalization 与 Layer Normalization

### Batch Normalization

对 batch 维度做归一化，常用于 CNN。

### Layer Normalization

对特征维度做归一化，常用于 Transformer。

大语言模型中更常见 LayerNorm 或 RMSNorm。

## 12. Dropout

Dropout 在训练时随机丢弃一部分神经元输出，让模型不要过度依赖某些路径。

直觉像是训练很多个略有不同的子网络，提升泛化能力。

## 13. MLP、CNN、RNN、Transformer 的位置

本部分只打基础，后续会系统学习网络结构。这里先建立地图：

| 结构 | 适合数据 | 核心思想 |
|---|---|---|
| MLP | 表格、简单特征 | 全连接层堆叠 |
| CNN | 图像、局部结构 | 卷积提取局部模式 |
| RNN/LSTM/GRU | 序列数据 | 递归处理时间序列 |
| Transformer | 文本、多模态 | Attention 建模全局关系 |

大模型主要基于 Transformer 及其变体。

## 14. 深度学习训练流程

标准流程：

```text
准备数据
  -> 构建模型
  -> 定义损失函数
  -> 选择优化器
  -> 前向传播
  -> 计算损失
  -> 反向传播
  -> 更新参数
  -> 验证模型
```

PyTorch 中对应：

```text
model(x)
loss_fn(output, y)
loss.backward()
optimizer.step()
optimizer.zero_grad()
```

## 15. 与大模型的关系

| 深度学习基础 | 大模型中的对应 |
|---|---|
| 张量 | token embedding、attention matrix |
| 反向传播 | 训练数十亿参数 |
| 优化器 | AdamW、学习率调度 |
| 归一化 | LayerNorm、RMSNorm |
| 激活函数 | GELU、SwiGLU |
| 正则化 | weight decay、dropout、数据去重 |
| GPU | 分布式训练、显存优化 |

## 本章小结

深度学习的核心是用多层可微函数从数据中学习表示。你需要重点理解张量、前向传播、损失函数、反向传播和优化器。掌握这些后，学习 Transformer 和大语言模型会容易很多。

## 推荐阅读

- Ian Goodfellow, Yoshua Bengio, Aaron Courville, *Deep Learning*, 2016。
- Aston Zhang et al., *Dive into Deep Learning*。
- Michael Nielsen, *Neural Networks and Deep Learning*。
- Stanford CS231n: Convolutional Neural Networks for Visual Recognition。
