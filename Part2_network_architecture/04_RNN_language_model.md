# 04 手写 RNN 语言模型

## 1. 什么是语言模型

语言模型（Language Model, LM）做一件事：

> 给定前面的内容，预测下一个 token 的概率分布。

```text
输入："今天天气真"
模型输出下一个字的概率：
  好 -> 0.6
  热 -> 0.2
  冷 -> 0.1
  ...
```

这就是 GPT 等大模型的训练目标（next token prediction）的雏形。把预测出的字接到输入末尾，再预测下一个，不断重复，就能**生成文本**。

本章用 RNN（可换成 LSTM/GRU）手写一个**字符级**语言模型：输入一串字符，预测下一个字符。

## 2. 字符级 vs 词级

```text
词级：   以"词"为单位     ["今天", "天气", "真", "好"]
字符级： 以"字符"为单位   ["今","天","天","气","真","好"]
```

字符级实现简单、词表小（适合学习），缺点是序列更长。我们用字符级入门。

## 3. 整体流程

```text
文本 "hello"
  -> 建词表，每个字符给一个编号        {h:0, e:1, l:2, o:3}
  -> 输入序列 "hell"  目标序列 "ello"  （目标是输入右移一位）
  -> 每个字符 -> embedding 向量
  -> 过 RNN，得到每步隐藏状态
  -> 每步接一个全连接 + softmax，预测下一个字符
  -> 用交叉熵损失训练
```

核心思想：**目标 = 输入向右移一位**。模型在每个位置都学习“看了到目前为止的字符，下一个该是什么”。

```text
位置:    h    e    l    l    o
输入:    h    e    l    l        （喂给模型）
目标:         e    l    l    o   （要预测的下一个）
```

## 4. 完整可运行代码（PyTorch）

```python
import torch
from torch import nn

# ---------- 1. 准备数据 ----------
text = "hello world. " * 50          # 玩具语料
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = {c: i for i, c in enumerate(chars)}   # char -> id
itos = {i: c for i, c in enumerate(chars)}   # id -> char

def encode(s): return [stoi[c] for c in s]
def decode(ids): return "".join(itos[i] for i in ids)

data = torch.tensor(encode(text), dtype=torch.long)

# ---------- 2. 定义模型 ----------
class CharRNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=32, hidden_dim=128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)   # 字符 -> 向量
        self.rnn = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)        # 隐藏状态 -> 下一字符分数

    def forward(self, x, hidden=None):
        x = self.embed(x)                  # [B, T] -> [B, T, embed_dim]
        out, hidden = self.rnn(x, hidden)  # [B, T, hidden_dim]
        logits = self.fc(out)              # [B, T, vocab_size]
        return logits, hidden

# ---------- 3. 训练 ----------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CharRNN(vocab_size).to(DEVICE)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-3)

seq_len = 16
for step in range(2000):
    # 随机取一段，输入是 [i:i+seq_len]，目标是右移一位 [i+1:i+seq_len+1]
    i = torch.randint(0, len(data) - seq_len - 1, (1,)).item()
    x = data[i:i+seq_len].unsqueeze(0).to(DEVICE)       # [1, T]
    y = data[i+1:i+seq_len+1].unsqueeze(0).to(DEVICE)   # [1, T]

    logits, _ = model(x)                                # [1, T, vocab_size]
    loss = loss_fn(logits.view(-1, vocab_size), y.view(-1))  # 展平后算交叉熵

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if step % 500 == 0:
        print(f"step={step}, loss={loss.item():.4f}")

# ---------- 4. 生成文本（采样） ----------
@torch.no_grad()
def generate(model, start="h", length=50, temperature=1.0):
    model.eval()
    ids = encode(start)
    x = torch.tensor([ids], device=DEVICE)
    hidden = None
    result = list(ids)
    for _ in range(length):
        logits, hidden = model(x, hidden)        # 只需最后一步
        logits = logits[0, -1] / temperature     # 取最后时间步，温度缩放
        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, 1).item()   # 按概率采样
        result.append(next_id)
        x = torch.tensor([[next_id]], device=DEVICE)    # 把新字符接回输入
    return decode(result)

print(generate(model, start="h", length=60))
```

## 5. 几个关键概念

### 5.1 Embedding

`nn.Embedding` 把每个字符 id 映射成一个可学习的稠密向量。比 one-hot 更高效，也能学到字符间关系。

```text
字符 'h' (id=0) -> [0.2, -0.1, 0.5, ...]  （embed_dim 维向量）
```

### 5.2 为什么要把 logits 展平算损失

```text
logits: [B, T, vocab_size]   每个位置一个 vocab_size 维分布
y:      [B, T]               每个位置一个正确字符 id

交叉熵要求: 输入 [N, vocab_size]，目标 [N]
所以 view(-1, vocab_size) 把 B*T 个位置拉平，一起算损失
```

### 5.3 温度（temperature）

生成时控制随机性：

```text
temperature < 1：分布更尖锐，输出更保守、更可预测
temperature = 1：按原始概率采样
temperature > 1：分布更平，输出更随机、更有创意
```

这和你以后调大模型生成参数（`temperature`、`top-k`、`top-p`）是同一个概念。

## 6. 训练时与生成时的区别

```text
训练：一次性喂整段，每个位置并行算损失（teacher forcing 思想）
生成：一个字符一个字符地产出，把上一步输出接回作为下一步输入（自回归）
```

“自回归 (autoregressive)”——用自己之前的输出当下一步输入——正是 GPT 生成文本的方式。

## 7. 与大模型的关系

| 本章概念 | 大模型中的对应 |
|---|---|
| next char prediction | next token prediction |
| Embedding | token embedding |
| 交叉熵损失 | 预训练损失 |
| 自回归生成 | GPT 推理时逐 token 生成 |
| temperature | 推理采样参数 |

唯一的大区别是：大模型把 RNN 换成了 Transformer，并把规模放大了百万倍。

## 8. 经典参考

- Mikolov et al., "Recurrent Neural Network Based Language Model", 2010。
- Sutskever, Martens, Hinton, "Generating Text with Recurrent Neural Networks", ICML 2011。
- Andrej Karpathy, "The Unreasonable Effectiveness of RNNs", 2015（char-rnn，本章思路来源）。

## 本章小结

语言模型的本质是“预测下一个 token”。用 RNN/LSTM + Embedding + 全连接 + 交叉熵就能训练一个字符级语言模型，再用自回归 + 温度采样生成文本。理解了这一章，就理解了 GPT 训练目标的最小原型。

## 推荐阅读

- Karpathy, char-rnn 项目与 min-char-rnn.py。
- *Dive into Deep Learning*，语言模型与循环神经网络章节。
