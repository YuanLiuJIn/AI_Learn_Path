# Part2_network_architecture：网络结构篇

本部分进入深度学习的核心——网络结构。第一部分打好了基础（张量、前向/反向传播、优化、PyTorch），这一部分讲清楚现代深度学习和大模型背后的几类关键结构，最终落到 Transformer。

学习主线是一条清晰的演化路径：

```text
CNN（空间）       RNN（时间/序列）
    │                  │
    │                  ├─> LSTM/GRU（解决长程遗忘）
    │                  ├─> 语言模型（预测下一个词）
    │                  ├─> Seq2Seq（编码器-解码器）
    │                  └─> + Attention（动态对齐）
    │                              │
    └────> ResNet（残差，能训练很深）
                                   │
                                   v
                            Transformer（纯注意力）
                                   │
                                   v
                            现代大模型的基石
```

## 章节顺序

1. `01_CNN.md`：卷积神经网络与手写 CNN
2. `02_RNN.md`：循环神经网络
3. `03_LSTM_GRU.md`：长短期记忆与门控循环单元
4. `04_RNN_language_model.md`：手写 RNN 语言模型
5. `05_seq2seq.md`：手写 Seq2Seq 机器翻译模型
6. `06_attention.md`：深入浅出 Attention 机制
7. `07_rnn_attention_translation.md`：RNN + Attention 机器翻译模型
8. `08_resnet.md`：ResNet 残差网络（史上引用最多的 AI 论文之一）
9. `09_transformer.md`：Transformer 详解
10. `references.md`：本部分参考论文与资料

## 学习方法

每章都按同一节奏：

```text
1. 它解决什么问题（为什么需要这个结构）
2. 一句话直觉 + 生活类比
3. 结构图与数据如何流动
4. 关键公式（先直觉后符号）
5. 最小可运行代码（PyTorch）
6. 经典论文与实际应用
7. 局限与下一步演化
```

## 前置要求

确保你已经掌握 Part1 的：张量与 shape、前向/反向传播、损失函数与交叉熵、优化器、PyTorch 训练循环、`nn.Module`。遇到不熟悉的名词查根目录 `glossary.md`。

## Part2 学完后应达到的程度

- 能解释 CNN 的卷积、池化、感受野，并手写一个图像分类 CNN。
- 能解释 RNN 为什么适合序列，以及它的梯度问题。
- 能说清楚 LSTM/GRU 的门控如何缓解长程遗忘。
- 能手写一个字符级 RNN 语言模型并采样生成文本。
- 能理解 Seq2Seq 编码器-解码器和 teacher forcing。
- 能用自己的话解释 Attention 在做什么，并推导 QKV。
- 能解释残差连接为什么让深网络可训练。
- 能完整讲清 Transformer 的每个模块，并理解它为何取代 RNN。
