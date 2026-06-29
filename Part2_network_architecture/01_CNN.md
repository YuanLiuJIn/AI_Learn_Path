# 01 CNN 卷积神经网络

## 1. 它解决什么问题

设想用普通全连接网络（MLP）处理一张 `1000 × 1000` 的彩色图片：

```text
输入像素数 = 1000 × 1000 × 3 = 300 万
如果第一层隐藏层有 1000 个神经元
第一层权重数 = 300 万 × 1000 = 30 亿
```

光第一层就 30 亿参数，根本训不动。而且 MLP 有两个根本缺陷：

- **参数爆炸**：每个像素都和每个神经元连一根线。
- **没有平移不变性**：猫在图片左上角和右下角，对 MLP 是完全不同的输入，要重新学。

CNN 用三个思想一次性解决：

1. **局部连接**：一个神经元只看图片的一小块区域（人看图也是先看局部）。
2. **权重共享**：同一个“找边缘”的卷积核在整张图滑动复用，参数大幅减少。
3. **平移不变性**：同一个核在哪都能检测到同样的模式。

## 2. 一句话直觉

> CNN 就是用一堆可学习的“小滤镜”（卷积核）在图像上滑动扫描，逐层从边缘 → 纹理 → 部件 → 物体地提取特征。

生活类比：你在一张大地图上找“加油站图标”。你不会一次盯着整张地图，而是拿个小放大镜（卷积核）从左到右、从上到下逐块扫描，发现匹配就标记。这个“滑动扫描 + 匹配模式”就是卷积。

## 3. 卷积是怎么算的

### 3.1 单个卷积操作

卷积核（kernel/filter）是一个小矩阵，在输入上滑动，每个位置做“逐元素相乘再求和”。

以 `3×3` 输入、`2×2` 卷积核为例：

```text
输入:            卷积核:
1  2  3          1  0
4  5  6          0  1
7  8  9

左上角对齐计算:
1*1 + 2*0 + 4*0 + 5*1 = 1 + 5 = 6
```

核滑过所有位置，得到一张更小的“特征图”(feature map)：

```text
输出特征图:
6   8
12  14
```

### 3.2 三个关键超参数

```text
kernel_size：卷积核大小，常用 3×3
stride：     步长，每次滑动几格。stride=2 会让输出尺寸减半
padding：    在边缘补零，控制输出尺寸、保护边缘信息
```

输出尺寸公式：

```text
输出边长 = (输入边长 - kernel_size + 2*padding) / stride + 1
```

例如输入 `32×32`，kernel `3×3`，padding=1，stride=1：

```text
(32 - 3 + 2*1) / 1 + 1 = 32   （尺寸不变，padding=1 的常见用法）
```

### 3.3 通道（channel）

彩色图有 RGB 三个通道。卷积核的深度要和输入通道数一致；而我们通常用**多个**卷积核，每个核负责检测一种模式，输出多个通道。

```text
输入:  [batch, 3,  H, W]      3 = RGB
卷积:  16 个 3×3 卷积核
输出:  [batch, 16, H', W']    16 = 学到 16 种特征
```

## 4. 池化（Pooling）

池化是下采样，缩小特征图、减少计算、增强平移鲁棒性。最常用最大池化：

```text
2×2 最大池化，stride=2：
1  3 | 2  4              取每个 2×2 区域的最大值
5  6 | 7  8       ->     6   8
-----+-----              14  16
9  10| 11 12
13 14| 15 16
```

直觉：我们只关心“这块区域里有没有出现某个特征”，不必关心它精确在哪。

## 5. 感受野（Receptive Field）

感受野指**输出特征图上一个点，对应原始输入的多大区域**。

```text
第 1 层 3×3 卷积：每个点看到原图 3×3
再叠一层 3×3：    每个点看到原图 5×5
层数越深，感受野越大 -> 高层能“看到”整体语义
```

这解释了为什么 CNN 是“低层看边缘、高层看物体”——越往上感受野越大。

## 6. 一个典型 CNN 的结构

经典图像分类 CNN 的骨架：

```text
输入图片
  -> [卷积 -> 激活(ReLU) -> 池化]   提取低层特征
  -> [卷积 -> 激活(ReLU) -> 池化]   提取中层特征
  -> [卷积 -> 激活(ReLU) -> 池化]   提取高层特征
  -> Flatten 展平
  -> 全连接层
  -> 输出类别概率(Softmax)
```

特征图尺寸越来越小、通道越来越多，相当于“空间信息换成语义信息”。

## 7. 手写 CNN（PyTorch，跑 MNIST/CIFAR-10）

下面是一个完整可运行的小型 CNN，分类 CIFAR-10（`3×32×32`，10 类）。

```python
import torch
from torch import nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            # 输入: [B, 3, 32, 32]
            nn.Conv2d(3, 32, kernel_size=3, padding=1),  # -> [B, 32, 32, 32]
            nn.ReLU(),
            nn.MaxPool2d(2),                              # -> [B, 32, 16, 16]

            nn.Conv2d(32, 64, kernel_size=3, padding=1), # -> [B, 64, 16, 16]
            nn.ReLU(),
            nn.MaxPool2d(2),                              # -> [B, 64, 8, 8]

            nn.Conv2d(64, 128, kernel_size=3, padding=1),# -> [B, 128, 8, 8]
            nn.ReLU(),
            nn.MaxPool2d(2),                              # -> [B, 128, 4, 4]
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                  # -> [B, 128*4*4 = 2048]
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),   # -> [B, 10]
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ---- 训练骨架 ----
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleCNN().to(DEVICE)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

for epoch in range(10):
    model.train()
    for images, labels in train_loader:           # train_loader 来自 torchvision CIFAR-10
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        logits = model(images)                     # 前向
        loss = loss_fn(logits, labels)
        optimizer.zero_grad()
        loss.backward()                            # 反向
        optimizer.step()
```

数据准备（torchvision）：

```python
import torchvision
import torchvision.transforms as T
from torch.utils.data import DataLoader

transform = T.Compose([T.ToTensor()])
train_set = torchvision.datasets.CIFAR10(root="./data", train=True,
                                         download=True, transform=transform)
train_loader = DataLoader(train_set, batch_size=64, shuffle=True)
```

### 看懂 shape 的变化（最重要）

```text
[B, 3, 32, 32] -conv+pool-> [B, 32, 16, 16]
               -conv+pool-> [B, 64, 8, 8]
               -conv+pool-> [B, 128, 4, 4]
               -flatten--->  [B, 2048]
               -linear---->  [B, 10]
```

理解每一步 shape 怎么变，就真正看懂了 CNN。

## 8. 手写一次卷积（不依赖框架，加深理解）

```python
import numpy as np

def conv2d_single(x, kernel):
    """x: [H, W], kernel: [kh, kw], stride=1, no padding"""
    H, W = x.shape
    kh, kw = kernel.shape
    out_h, out_w = H - kh + 1, W - kw + 1
    out = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            region = x[i:i+kh, j:j+kw]   # 取出当前窗口
            out[i, j] = np.sum(region * kernel)  # 逐元素相乘求和
    return out

x = np.array([[1,2,3],[4,5,6],[7,8,9]], dtype=float)
kernel = np.array([[1,0],[0,1]], dtype=float)
print(conv2d_single(x, kernel))   # [[6, 8], [12, 14]]
```

跑一遍这段代码，卷积就不再是抽象概念。

## 9. 经典论文与里程碑

| 网络 | 论文/年份 | 关键贡献 |
|---|---|---|
| LeNet-5 | LeCun et al., 1998 | 最早成功的 CNN，用于手写数字识别 |
| AlexNet | Krizhevsky et al., 2012 | ImageNet 夺冠，引爆深度学习，ReLU+Dropout+GPU |
| VGG | Simonyan & Zisserman, 2014 | 全用 3×3 小卷积堆叠，结构简洁 |
| GoogLeNet/Inception | Szegedy et al., 2014 | 多尺度卷积并联 |
| ResNet | He et al., 2015 | 残差连接，见 `08_resnet.md` |

AlexNet（2012）是历史转折点：它在 ImageNet 上大幅领先传统方法，标志着深度学习时代开始。

## 10. 实际应用

- 图像分类、目标检测（YOLO、Faster R-CNN）、语义分割
- 人脸识别、医学影像、自动驾驶感知
- 即使在 Transformer 时代，CNN 仍广泛用于视觉任务和混合架构

## 11. 局限与演化

- CNN 擅长局部模式，但建模长距离全局关系不如注意力机制。
- 后来 Vision Transformer (ViT, 2020) 把 Transformer 引入视觉，证明纯注意力也能做好图像。
- 但 CNN 依然是理解“局部特征提取”和“权重共享”最好的入口。

## 本章小结

CNN 用局部连接、权重共享和池化，高效地从图像中逐层提取特征。核心要理解：卷积是“滑动窗口做加权求和”，感受野随深度增大，shape 沿网络逐层变化。手写一次卷积 + 跑通一个 CIFAR-10 分类器，就掌握了 CNN 的本质。

## 推荐阅读

- LeCun et al., "Gradient-Based Learning Applied to Document Recognition", 1998 (LeNet)。
- Krizhevsky, Sutskever, Hinton, "ImageNet Classification with Deep CNNs", NeurIPS 2012 (AlexNet)。
- Stanford CS231n: Convolutional Neural Networks for Visual Recognition。
- *Dive into Deep Learning*，卷积神经网络章节。
