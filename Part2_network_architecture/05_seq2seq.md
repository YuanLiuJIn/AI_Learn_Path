# 05 手写 Seq2Seq 机器翻译模型

## 1. 它解决什么问题

很多任务的**输入和输出长度不一样**，而且不是一一对应：

```text
机器翻译：  "我 爱 你"(3 词) -> "I love you"(3 词)
            "我 喜欢 自然语言处理" -> "I like NLP"（长度不同）
文本摘要：  一长段 -> 几句话
对话：      一句问 -> 一句答
```

普通 RNN 是“一个输入对一个输出”，没法处理“输入 N 个、输出 M 个且 N≠M”。

Seq2Seq（Sequence to Sequence）用**编码器-解码器（Encoder-Decoder）**结构解决：

> 先用一个 RNN（编码器）把整个输入序列压缩成一个“语义向量”，再用另一个 RNN（解码器）从这个向量出发，逐词生成输出序列。

## 2. 一句话直觉

> 编码器像一个“读者”，读完整句外语，在脑中形成一个理解（上下文向量）；解码器像一个“译者”，拿着这个理解，一个词一个词地写出译文。

## 3. 整体结构图

```text
            编码器 (Encoder)                      解码器 (Decoder)
   x1    x2    x3   <eos>                  <sos>   y1    y2   y3
    │     │     │     │                      │     │     │     │
    v     v     v     v                      v     v     v     v
  [RNN]-[RNN]-[RNN]-[RNN] ──── c ────────> [RNN]-[RNN]-[RNN]-[RNN]
                          上下文向量          │     │     │     │
                       (最后的隐藏状态)        v     v     v     v
                                             y1    y2    y3  <eos>
                                             │_____↑（上一步输出作为下一步输入）
```

- 编码器读完输入，最后的隐藏状态 `c` 作为整句的“浓缩理解”。
- 解码器以 `c` 为初始状态，从起始符 `<sos>` 开始逐词生成，直到产出结束符 `<eos>`。

## 4. 几个关键概念

### 4.1 特殊标记

```text
<sos> (start of sequence)：告诉解码器"开始生成"
<eos> (end of sequence)：  模型生成它表示"翻译完成"
<pad>：                    补齐批内不同长度序列
```

### 4.2 Teacher Forcing（教师强制）

训练解码器时有个选择：每一步喂给它的，是**模型上一步的预测**，还是**真实的正确答案**？

```text
不用 teacher forcing：喂模型自己上一步的输出（可能是错的，错误会累积）
用 teacher forcing：  喂真实目标词（训练更快更稳）
```

Teacher forcing 用真实答案当输入，训练收敛快。但训练（喂真值）和推理（喂自己的输出）不一致，可能导致 exposure bias，实践中常按一定概率混合使用。

### 4.3 训练 vs 推理

```text
训练：知道完整目标句，可以并行 + teacher forcing
推理：不知道答案，必须自回归一个词一个词生成，遇到 <eos> 停止
```

## 5. 完整可运行代码（PyTorch，玩具翻译任务）

用一个简单任务演示：把数字串“翻译”成逆序（如 `1 2 3 -> 3 2 1`），结构与真实翻译一致，便于聚焦 Seq2Seq 本身。

```python
import torch
from torch import nn
import random

# ---------- 编码器 ----------
class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)

    def forward(self, x):
        x = self.embed(x)              # [B, T] -> [B, T, embed]
        _, h = self.rnn(x)             # h: [1, B, hidden] 上下文向量
        return h

# ---------- 解码器 ----------
class Decoder(nn.Module):
    def __init__(self, vocab_size, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, token, hidden):
        # token: [B, 1] 当前输入词；hidden: 上一步状态
        x = self.embed(token)          # [B, 1, embed]
        out, hidden = self.rnn(x, hidden)
        logits = self.fc(out.squeeze(1))   # [B, vocab_size]
        return logits, hidden

# ---------- Seq2Seq ----------
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, sos_id):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.sos_id = sos_id

    def forward(self, src, tgt, teacher_forcing=0.5):
        B, T = tgt.shape
        vocab_size = self.decoder.fc.out_features
        outputs = torch.zeros(B, T, vocab_size, device=src.device)

        hidden = self.encoder(src)                       # 编码
        token = torch.full((B, 1), self.sos_id, device=src.device)  # 以 <sos> 开始

        for t in range(T):
            logits, hidden = self.decoder(token, hidden) # 解码一步
            outputs[:, t] = logits
            # 决定下一步输入：真值 or 模型预测
            if random.random() < teacher_forcing:
                token = tgt[:, t].unsqueeze(1)           # teacher forcing
            else:
                token = logits.argmax(-1, keepdim=True)  # 用自己的预测
        return outputs

# ---------- 训练骨架 ----------
# vocab: 0=<pad>, 1=<sos>, 2=<eos>, 3..12 表示数字 0..9
VOCAB = 13
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Seq2Seq(Encoder(VOCAB), Decoder(VOCAB), sos_id=1).to(DEVICE)
loss_fn = nn.CrossEntropyLoss(ignore_index=0)   # 忽略 <pad>
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-3)

def make_batch(B=32, L=5):
    src = torch.randint(3, 13, (B, L))
    tgt = torch.flip(src, dims=[1])             # 目标 = 逆序
    eos = torch.full((B, 1), 2)
    tgt = torch.cat([tgt, eos], dim=1)          # 末尾加 <eos>
    return src.to(DEVICE), tgt.to(DEVICE)

for step in range(2000):
    src, tgt = make_batch()
    outputs = model(src, tgt)                   # [B, T, vocab]
    loss = loss_fn(outputs.reshape(-1, VOCAB), tgt.reshape(-1))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if step % 500 == 0:
        print(f"step={step}, loss={loss.item():.4f}")
```

## 6. 看懂数据流（最重要）

```text
src "3 5 7 2 9"
  -> Encoder GRU -> h (上下文向量, 浓缩整句)

h + <sos>
  -> Decoder 第1步 -> 9
  -> Decoder 第2步(输入9) -> 2
  -> ... 直到输出 <eos>
结果 "9 2 7 5 3 <eos>"
```

## 7. Seq2Seq 的瓶颈：信息压缩

注意编码器把**整个输入**压缩成**一个固定长度的向量 `c`**。

```text
短句 "你好"        -> c   （够用）
长句 50 个词的段落 -> c   （一个向量装不下，信息丢失）
```

句子越长，这个“信息瓶颈”越严重，翻译质量下降。

**这正是 Attention 要解决的问题**（见 `06_attention.md`）：与其把整句压成一个向量，不如让解码器每生成一个词时，都回头“看”输入的相关部分。

## 8. 经典论文

- Sutskever, Vinyals, Le, "Sequence to Sequence Learning with Neural Networks", NeurIPS 2014：Seq2Seq 开山之作（用 LSTM 做翻译）。
- Cho et al., "Learning Phrase Representations using RNN Encoder-Decoder", 2014：编码器-解码器框架与 GRU。

## 9. 实际应用

- 机器翻译（神经机器翻译 NMT 的起点）
- 文本摘要、对话生成、语音识别、代码生成

## 本章小结

Seq2Seq 用编码器把输入压缩成上下文向量，再用解码器自回归地生成输出，解决了输入输出不等长的问题。teacher forcing 让训练更稳。它的核心瓶颈是“单一上下文向量装不下长句”，由此引出注意力机制。

## 推荐阅读

- Sutskever et al., "Sequence to Sequence Learning with Neural Networks", 2014。
- *Dive into Deep Learning*，编码器-解码器与机器翻译章节。
