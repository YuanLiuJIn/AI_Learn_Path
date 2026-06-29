# 08 ResNet 残差网络

> He et al., "Deep Residual Learning for Image Recognition", CVPR 2016。
> 这是被引用最多的 AI/深度学习论文之一（引用量数十万级），ImageNet 2015 冠军。

## 1. 它解决什么问题：网络退化

直觉上，网络越深，能力应该越强。但 2015 年前人们发现一个反常现象：

```text
20 层网络 vs 56 层网络（都在训练集上）
56 层的训练误差反而更高！
```

注意：这**不是过拟合**（过拟合是训练误差低、测试误差高）。这里是**训练误差本身就降不下去**，称为**退化问题 (degradation)**。

为什么？网络太深时：

- 梯度在反向传播中消失/衰减，前面的层学不动。
- 让很多层去学“恒等映射”（什么都不改，原样传递）居然很难——优化器很难把一堆非线性层调成“什么都不做”。

## 2. 一句话直觉与核心想法

> 与其让每几层去学“目标输出 H(x)”，不如让它们只学“目标和输入的差 F(x) = H(x) - x”，最后再把输入加回来：输出 = F(x) + x。

这就是**残差连接 (residual / skip connection)**：

```text
普通块：  x ->[层]->[层]-> H(x)
残差块：  x ->[层]->[层]-> F(x) ──(+)── H(x) = F(x) + x
          └──────────skip──────────┘
```

为什么这样更好：

- 如果最优解就是“什么都不改”（恒等映射），网络只需让 `F(x) → 0` 即可，这比让一堆层凑出恒等映射**容易得多**。
- 加法形成“梯度高速公路”：反向传播时梯度能通过 skip 直接回传，缓解梯度消失，于是能训练上百层甚至上千层。

生活类比：让你“把一篇文章改好”比“从零重写一篇一样好的文章”容易。残差就是只学“需要改动的部分 F(x)”，原文 x 直接保留。

## 3. 残差块结构

### 基础残差块（BasicBlock，用于 ResNet-18/34）

```text
x ──┬─> Conv3x3 -> BN -> ReLU -> Conv3x3 -> BN ──(+)─> ReLU -> 输出
    │                                            ↑
    └──────────────── skip (恒等) ───────────────┘
```

### 瓶颈块（Bottleneck，用于 ResNet-50/101/152）

用 `1×1` 卷积先降维再升维，减少计算量：

```text
x ──┬─> 1x1 conv(降维) -> 3x3 conv -> 1x1 conv(升维) ──(+)──> 输出
    └──────────────────── skip ────────────────────────┘
```

当输入输出通道数不一致时，skip 路径用一个 `1×1` 卷积调整维度，保证能相加。

## 4. PyTorch 实现残差块

```python
import torch
from torch import nn

class BasicBlock(nn.Module):
    def __init__(self, in_ch, out_ch, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_ch)

        # 当维度不匹配时，用 1x1 卷积调整 shortcut
        self.shortcut = nn.Sequential()
        if stride != 1 or in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_ch),
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = out + self.shortcut(x)      # 核心：F(x) + x
        return torch.relu(out)

# 验证
x = torch.randn(4, 64, 32, 32)
block = BasicBlock(64, 128, stride=2)
print(block(x).shape)   # [4, 128, 16, 16]
```

整行的关键就是 `out = out + self.shortcut(x)`——这一个加号，就是 ResNet 的全部精髓。

## 5. 残差为什么让梯度更稳（公式直觉）

残差块输出 `y = x + F(x)`，反向传播时对 `x` 的梯度：

```text
∂loss/∂x = ∂loss/∂y * (1 + ∂F/∂x)
                       └─ 这个 "1" 很关键
```

即使 `∂F/∂x` 很小（接近梯度消失），那个 `+1` 也保证梯度能直接传回前面的层。这就是“梯度高速公路”的数学来源。

## 6. ResNet 家族

| 网络 | 层数 | 块类型 |
|---|---|---|
| ResNet-18 / 34 | 18 / 34 | BasicBlock |
| ResNet-50 / 101 / 152 | 50 / 101 / 152 | Bottleneck |

ResNet 在 ImageNet 上首次让 152 层网络稳定训练并夺冠，错误率超过人类水平的里程碑之一。

## 7. 残差思想的深远影响

残差连接早已超越图像领域，成为**几乎所有现代深层网络的标配**：

```text
- Transformer 的每个子层都有残差连接（见 09 章）
- 几乎所有大语言模型（GPT、LLaMA 等）每一层都用残差
- 没有残差，就训不动几十上百层的深度模型
```

可以说，残差连接是让“深度”学习真正变“深”的关键发明之一。

## 8. 实际应用

- 图像分类、检测、分割的标准骨干网络（backbone）
- 作为预训练特征提取器广泛迁移
- 残差思想嵌入 Transformer，进而支撑整个大模型时代

## 9. 与本部分其他章节的关系

```text
CNN（01）提供卷积基础
ResNet（本章）解决"深"的问题 -> 让深层网络可训练
Attention（06）解决"长程依赖与并行"
Transformer（09）= 自注意力 + 残差 + LayerNorm + FFN
```

注意：Transformer 同时继承了 Attention 和 ResNet 的残差思想。

## 本章小结

ResNet 用残差连接 `y = x + F(x)` 解决深层网络的退化问题：让网络只学“增量” F(x)，并通过加法形成梯度高速公路，使上百层网络可训练。这个简单而强大的思想成为所有现代深层网络（包括 Transformer 和大模型）的基础组件。

## 推荐阅读

- He, Zhang, Ren, Sun, "Deep Residual Learning for Image Recognition", CVPR 2016。
- He et al., "Identity Mappings in Deep Residual Networks", 2016（残差块的进一步分析）。
- *Dive into Deep Learning*，残差网络 (ResNet) 章节。
