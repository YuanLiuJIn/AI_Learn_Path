# 03 LSTM 与 GRU：长短期记忆与门控

## 1. 它解决什么问题

上一章说到，普通 RNN 有**长程依赖**问题：信息经过很多时间步后梯度消失，模型记不住远处的内容。

```text
"我在法国长大 …（50 个词）… 我说流利的 ___"
普通 RNN：早就把"法国"忘了
```

LSTM（Long Short-Term Memory）和 GRU（Gated Recurrent Unit）用**门控机制**解决这个问题：让网络学会**有选择地记住、遗忘和输出信息**，而不是每步都把记忆整个重写一遍。

## 2. 一句话直觉

> 普通 RNN 每步都把记忆“擦掉重写”，所以容易丢失旧信息；LSTM 增加一条几乎不被打扰的“记忆传送带”(cell state)，再用几个“阀门”(门) 精细控制往里加什么、丢什么、放什么出来。

生活类比：

- 普通 RNN 像用一块小白板记笔记，每来新内容就大幅擦改，旧的很快没了。
- LSTM 像一个带“笔记本 + 三个开关”的系统：开关决定哪些旧笔记保留、哪些新内容写入、这次该读出哪部分。重要信息可以在笔记本上长期保留。

## 3. LSTM 的核心：细胞状态 + 三个门

LSTM 在隐藏状态 `h_t` 之外，多了一条**细胞状态 `C_t`**（记忆传送带）。

```text
        ┌─────────── C_{t-1} ──(传送带，信息容易长期保留)── C_t ───┐
        │              │            ↑              ↑               │
  遗忘门 f_t       输入门 i_t    候选记忆 ~C_t    输出门 o_t
        │              │            │              │
      决定丢弃       决定写入      新的候选       决定输出
     多少旧记忆      多少新信息      内容          多少记忆
```

### 三个门（都是 0~1 之间的“阀门”，用 sigmoid 算出）

```text
遗忘门 f_t = sigmoid(W_f · [h_{t-1}, x_t] + b_f)   # 旧记忆保留多少
输入门 i_t = sigmoid(W_i · [h_{t-1}, x_t] + b_i)   # 新信息写入多少
输出门 o_t = sigmoid(W_o · [h_{t-1}, x_t] + b_o)   # 这步输出多少记忆
```

### 候选记忆与更新

```text
候选记忆 ~C_t = tanh(W_C · [h_{t-1}, x_t] + b_C)    # 这步想写入的新内容

更新细胞状态:
C_t = f_t * C_{t-1}  +  i_t * ~C_t
      └忘掉一部分旧┘    └写入一部分新┘

输出隐藏状态:
h_t = o_t * tanh(C_t)
```

### 为什么能缓解梯度消失

关键在 `C_t = f_t * C_{t-1} + i_t * ~C_t` 这个**加法**更新。

普通 RNN 是反复**乘法**（连乘导致消失/爆炸）；而细胞状态主要靠加法演进，当遗忘门 `f_t ≈ 1` 时，`C_{t-1}` 几乎原样传到 `C_t`，梯度可以沿传送带顺畅回传，长期信息得以保留。

## 4. GRU：LSTM 的简化版

GRU 把 LSTM 简化：**合并细胞状态和隐藏状态，门也从 3 个减到 2 个**，参数更少、训练更快，效果常常相当。

```text
更新门 z_t = sigmoid(W_z · [h_{t-1}, x_t])   # 旧状态保留 vs 新状态写入的比例
重置门 r_t = sigmoid(W_r · [h_{t-1}, x_t])   # 计算新内容时忽略多少旧状态

候选状态 ~h_t = tanh(W · [r_t * h_{t-1}, x_t])
新状态   h_t  = (1 - z_t) * h_{t-1} + z_t * ~h_t
                └保留旧的┘           └采纳新的┘
```

直觉：更新门 `z_t` 像一个“滑杆”，在“保持旧记忆”和“采纳新内容”之间平滑调节。

## 5. LSTM vs GRU 怎么选

| 维度 | LSTM | GRU |
|---|---|---|
| 门数量 | 3（遗忘/输入/输出） | 2（更新/重置） |
| 状态 | 细胞状态 + 隐藏状态 | 只有隐藏状态 |
| 参数量 | 多 | 少（约少 1/4） |
| 训练速度 | 慢一些 | 快一些 |
| 效果 | 大数据、长序列常略优 | 小数据、要效率常够用 |

经验：先用 GRU 做 baseline，效果不够再试 LSTM。

## 6. PyTorch 用法

```python
import torch
from torch import nn

lstm = nn.LSTM(input_size=10, hidden_size=20, batch_first=True)
gru  = nn.GRU(input_size=10, hidden_size=20, batch_first=True)

x = torch.randn(32, 5, 10)   # [batch, seq_len, input_size]

out_lstm, (h_n, c_n) = lstm(x)   # LSTM 返回隐藏状态 h_n 和细胞状态 c_n
out_gru, h_n2 = gru(x)           # GRU 只返回 h_n

print(out_lstm.shape)  # [32, 5, 20]
print(c_n.shape)       # [1, 32, 20]  这就是 LSTM 多出来的细胞状态
```

注意 LSTM 比 RNN/GRU 多返回一个 `c_n`，这正是那条“记忆传送带”。

## 7. 一个小例子：手写一步 LSTM（NumPy）

```python
import numpy as np

def sigmoid(x): return 1 / (1 + np.exp(-x))

def lstm_step(x_t, h_prev, C_prev, params):
    z = np.concatenate([h_prev, x_t])         # 拼接 [h_{t-1}, x_t]
    f = sigmoid(params["Wf"] @ z + params["bf"])   # 遗忘门
    i = sigmoid(params["Wi"] @ z + params["bi"])   # 输入门
    o = sigmoid(params["Wo"] @ z + params["bo"])   # 输出门
    C_tilde = np.tanh(params["Wc"] @ z + params["bc"])  # 候选记忆
    C = f * C_prev + i * C_tilde              # 更新细胞状态（加法是关键）
    h = o * np.tanh(C)                        # 输出隐藏状态
    return h, C
```

跑一遍能直观看到三个门如何调节 `C` 的更新。

## 8. 经典论文与历史

- Hochreiter & Schmidhuber, "Long Short-Term Memory", *Neural Computation*, 1997：LSTM 原始论文，深度学习史上影响力极大的工作之一。
- Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder", 2014：提出 GRU。
- Gers et al., 2000：引入遗忘门，成为现代 LSTM 标准形态。

## 9. 实际应用

- 机器翻译、语音识别（Transformer 之前的主流）
- 文本生成、手写识别
- 时间序列预测（股价、电力负荷、传感器）

## 10. 局限与演化

```text
LSTM/GRU 解决了长程记忆，但：
- 仍是串行计算，无法像 Transformer 那样大规模并行
- 超长序列依然吃力
=> Transformer 用自注意力一步到位地建模任意距离依赖（见 09 章）
```

## 本章小结

LSTM 用细胞状态这条“传送带”加上遗忘/输入/输出三个门，通过加法式更新缓解梯度消失，能记住长程信息。GRU 是它的轻量版，用更新门和重置门、参数更少。它们是 Transformer 之前序列建模的主力。

## 推荐阅读

- Hochreiter & Schmidhuber, "Long Short-Term Memory", 1997。
- Cho et al., "Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation", EMNLP 2014。
- Christopher Olah, "Understanding LSTM Networks", 2015 (图解经典博客，强烈推荐)。
