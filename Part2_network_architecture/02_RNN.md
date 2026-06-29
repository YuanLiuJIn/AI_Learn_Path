# 02 RNN 循环神经网络

## 1. 它解决什么问题

CNN 擅长图像这种**空间**结构，但很多数据是**序列**，有先后顺序：

```text
文本：    "我 爱 自然 语言 处理"
语音：    一段随时间变化的波形
股价：    按天排列的价格
传感器：  时间序列读数
```

序列数据有两个特点，MLP 和 CNN 处理起来都别扭：

- **变长**：句子有长有短，固定输入大小的网络不好处理。
- **有顺序依赖**：“我爱你” 和 “你爱我” 词一样，意思不同；当前词的理解依赖前面的词。

RNN 的核心想法：**像人读句子一样，从左到右一个词一个词地读，并且边读边记住前面的信息**。

## 2. 一句话直觉

> RNN 有一个会不断更新的“记忆”（隐藏状态 h），每读一个新元素，就用“旧记忆 + 新输入”算出“新记忆”，并可顺便给出输出。

生活类比：你听别人讲故事，脑子里维护一个“目前为止的剧情概要”（隐藏状态）。每听到一句新话，就把它和已有概要融合，更新概要。听到最后，这个概要就浓缩了整段故事。

## 3. RNN 的结构与公式

### 3.1 核心递推公式

在每个时间步 `t`：

```text
h_t = tanh(W_xh * x_t + W_hh * h_{t-1} + b_h)
y_t = W_hy * h_t + b_y
```

- `x_t`：当前时间步输入（如第 t 个词的向量）
- `h_{t-1}`：上一步的隐藏状态（记忆）
- `h_t`：更新后的隐藏状态
- `y_t`：当前步输出（可选）
- `W_xh, W_hh, W_hy`：权重，**所有时间步共享同一套**（类似 CNN 的权重共享）

关键点：`h_t` 同时依赖当前输入 `x_t` 和历史 `h_{t-1}`，信息就这样沿时间传递。

### 3.2 按时间展开

RNN 看似是一个循环，展开后是一条链：

```text
        x_1        x_2        x_3        x_4
         │          │          │          │
         v          v          v          v
h_0 -> [RNN] -h_1-> [RNN] -h_2-> [RNN] -h_3-> [RNN] -> h_4
         │          │          │          │
         v          v          v          v
        y_1        y_2        y_3        y_4
```

注意：图中每个 `[RNN]` 是**同一套权重**，只是在不同时间步重复使用。`h_0` 通常初始化为 0。

## 4. RNN 能做哪些任务

RNN 灵活的输入输出对应方式：

```text
一对多 (1->N)：  看图说话（输入一张图，输出一句话）
多对一 (N->1)：  情感分类（输入一句话，输出一个情感）
多对多 (N->N)：  逐词标注（词性标注）
多对多 (N->M)：  机器翻译（Seq2Seq，见 05 章）
```

## 5. BPTT：随时间反向传播

RNN 的训练用 **BPTT (Backpropagation Through Time)**：把网络按时间展开成一条长链，再用普通反向传播。

直觉：因为所有时间步共享权重，最终某个权重的梯度，是它在**所有时间步**贡献的梯度之和。

## 6. RNN 的致命问题：长程依赖与梯度消失

考虑这个句子：

```text
"我在法国长大，……（中间很长）……，所以我说一口流利的 ___"
```

要填“法语”，模型必须记住开头的“法国”。但信息要经过很多时间步传递。

问题出在递推里反复乘 `W_hh`：

```text
梯度反向传播经过 t 步，大致涉及 W_hh 的 t 次方
|W_hh| < 1 -> 连乘后趋近 0 -> 梯度消失（记不住远处信息）
|W_hh| > 1 -> 连乘后爆炸    -> 梯度爆炸（训练不稳定）
```

- **梯度消失**：RNN 实际上只能记住最近几步，长距离依赖学不到。
- **梯度爆炸**：可用梯度裁剪（gradient clipping）缓解。

这正是 LSTM/GRU 要解决的问题（见 `03_LSTM_GRU.md`）。

## 7. 手写一个最小 RNN 单元（NumPy）

不依赖框架，跑一个时间步，理解递推：

```python
import numpy as np

def rnn_step(x_t, h_prev, W_xh, W_hh, b_h):
    # h_t = tanh(W_xh @ x_t + W_hh @ h_prev + b_h)
    return np.tanh(W_xh @ x_t + W_hh @ h_prev + b_h)

hidden_size, input_size = 4, 3
W_xh = np.random.randn(hidden_size, input_size) * 0.1
W_hh = np.random.randn(hidden_size, hidden_size) * 0.1
b_h  = np.zeros(hidden_size)

h = np.zeros(hidden_size)                 # 初始隐藏状态 h_0
sequence = [np.random.randn(input_size) for _ in range(5)]  # 长度 5 的序列

for t, x_t in enumerate(sequence):
    h = rnn_step(x_t, h, W_xh, W_hh, b_h) # 逐步更新记忆
    print(f"t={t}, h={np.round(h, 3)}")
```

## 8. PyTorch 中的 RNN

PyTorch 内置了高效实现：

```python
import torch
from torch import nn

rnn = nn.RNN(input_size=10, hidden_size=20, batch_first=True)

x = torch.randn(32, 5, 10)   # [batch=32, seq_len=5, input_size=10]
output, h_n = rnn(x)
print(output.shape)          # [32, 5, 20]  每个时间步的隐藏状态
print(h_n.shape)             # [1, 32, 20]  最后一个时间步的隐藏状态
```

shape 含义：

```text
output: 每个时间步都有一个隐藏状态输出
h_n:    整个序列处理完后的最终记忆
```

## 9. 经典论文与历史

- Elman, "Finding Structure in Time", 1990：经典 Elman RNN。
- Werbos, "Backpropagation Through Time", 1990：BPTT。
- Bengio et al., 1994：系统分析了 RNN 长程依赖的梯度困难。

## 10. 局限与演化

```text
RNN          -> 梯度消失，记不住长程  -> LSTM/GRU 用门控解决
RNN 串行计算 -> 无法并行、训练慢      -> Transformer 用注意力并行解决
```

## 本章小结

RNN 通过一个随时间更新的隐藏状态来处理序列，权重在时间步间共享。它的核心公式是 `h_t = tanh(W_xh x_t + W_hh h_{t-1} + b)`。最大问题是梯度消失导致的长程依赖困难，这引出了下一章的 LSTM 和 GRU。

## 推荐阅读

- Elman, "Finding Structure in Time", *Cognitive Science*, 1990。
- Bengio, Simard, Frasconi, "Learning Long-Term Dependencies with Gradient Descent is Difficult", 1994。
- Andrej Karpathy, "The Unreasonable Effectiveness of Recurrent Neural Networks", 2015 (博客)。
- *Dive into Deep Learning*，循环神经网络章节。
