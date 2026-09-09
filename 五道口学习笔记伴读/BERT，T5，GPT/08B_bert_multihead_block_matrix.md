# 08B · 多头注意力的分块矩阵实现（BertSelfAttention / BertSelfLayer）

> **接 08**：[08](./08_bert_encoder_self_attention.md) 用"把 `Wq` 切成 12 段"讲清了多头注意力的**数学**；本篇讲 HuggingFace 的**实现**——它根本不去切权重，而是**一次大矩阵乘法 + `view/transpose`** 就把 12 个头切出来了。
>
> **视频**：[动手写 BERT 系列] BertSelfLayer 多头注意力机制（multi head attention）的分块矩阵实现
>
> **一句话主旨**：所谓"12 个头"，**只是把 768 个通道按顺序切成 12 段**，模型里并没有 12 份独立的权重矩阵；用**分块矩阵**的视角，多头注意力 = 一次 `(N,768)@(768,768)` + 一次**分块对角**的打分 + 一次 `(N,768)@(768,768)`。

**命名对照**（视频说的 BertSelfLayer 就是这块）：

```
BertLayer
├── attention
│   ├── self      = BertSelfAttention   ← 本篇主角：Q/K/V + 打分 + 混合 + 拼头
│   └── output    = BertSelfOutput      ← W_o 输出投影 + 残差 + LayerNorm
├── intermediate  = 768 → 3072
└── output        = 3072 → 768 + 残差 + LayerNorm
```

---

## 一、为什么需要"分块矩阵实现"

同一个多头注意力，至少有三种写法：

| 写法 | 做法 | 评价 |
|---|---|---|
| **A. 按头循环** | `for h in range(12):` 每次切一段权重、做一次小 matmul | 最直白，**最慢**（12 次小 GEMM，GPU 吃不饱），但最适合理解 |
| **B. 整乘 + reshape** | 一次算完 `[N,768]`，再 `view(h, dk)` + `transpose` 切成 12 头 | **HuggingFace 真做法**，快；也是 A 的等价变形 |
| **C. 分块大矩阵** | 把 12 个头竖着堆成 `[12N, 64]`，做一个 `[12N, 12N]` 的大打分矩阵，只保留**块对角** | **理解用**（最直观地看出"头之间互不干扰"），实际不这么写（浪费 12 倍算力在无用的跨头块上） |

三者的输出**数值完全相同**（本篇第六节有可运行的 `allclose` 验证）。

> 核心工程动机：**GPU 喜欢大而少的矩阵乘法，讨厌小而多的**。一次 `[N,768] @ [768,768]` 比 12 次 `[N,768] @ [768,64]` 快得多，而它们算的是同一件事——这正是分块矩阵要证明的。

---

## 二、第一处分块：权重矩阵按**行**分块

以 `Wq` 为例（`(out, in) = (768, 768)`，见 08 的 3.1）。把它的 **768 个输出行**按顺序切成 12 段：

```
        ⎡ Wq_0  ⎤  ← 行 0:63     [64, 768]
Wq  =   ⎢ Wq_1  ⎥  ← 行 64:127   [64, 768]        Wq_i = Wq[i*64 : (i+1)*64, :]
        ⎢  ...  ⎥
        ⎣ Wq_11 ⎦  ← 行 704:767  [64, 768]
```

**转置之后变成列分块**（这才是 `x @ Wqᵀ` 里出现的形态）：

```
Wqᵀ = [ Wq_0ᵀ | Wq_1ᵀ | ... | Wq_11ᵀ ]      每一块 [768, 64]
```

按**分块矩阵乘法**规则 `X · [A|B] = [XA | XB]`：

```
Q = X @ Wqᵀ + bq
  = [ X·Wq_0ᵀ+bq_0 | X·Wq_1ᵀ+bq_1 | ... | X·Wq_11ᵀ+bq_11 ]
  = [   Q_0   |   Q_1   | ... |   Q_11   ]            ← [N, 768]，天然按头排好
```

**这就是全部秘密**：一次 `X @ Wqᵀ` 就已经把 12 个头的 Q**按顺序摆好**了，第 h 个头就在第 `[h*64, (h+1)*64)` 列。后面只需要 `view`/`transpose` 把这段通道"拎出来"，不需要真的做 12 次乘法。

`Wk / Wv` 完全同理。

> ⚠️ 再强调一次（08 的坑 5）：分的是 **Wq 的行 / Wqᵀ 的列**，也就是**输出维**。输入维始终是完整 768，每个头都看得见整句的全部信息。

---

## 三、第二处分块：打分矩阵是**分块对角**的

把 12 个头的 `Q_h`（各 `[N, 64]`）**竖着堆**成一个大矩阵：

```
        ⎡ Q_0  ⎤                    ⎡ K_0  ⎤
Q̃  =    ⎢ Q_1  ⎥   [12N, 64]   K̃ = ⎢ K_1  ⎥   [12N, 64]
        ⎢ ...  ⎥                    ⎢ ...  ⎥
        ⎣ Q_11 ⎦                    ⎣ K_11 ⎦
```

于是打分矩阵是 `[12N, 12N]`，按 `(头, 头)` 分成 `12×12` 个 `[N,N]` 的块：

```
              K̃ᵀ
         ⎡ Q_0K_0ᵀ   Q_0K_1ᵀ  ...  Q_0K_11ᵀ ⎤
S_big =  ⎢ Q_1K_0ᵀ   Q_1K_1ᵀ  ...  Q_1K_11ᵀ ⎥   / √d_k     第 (h,g) 块 = Q_h · K_gᵀ
         ⎢   ...                             ⎥
         ⎣ Q_11K_0ᵀ  ...       ...  Q_11K_11ᵀ⎦
           └─ 只要对角块（h == g）─┘
```

**只有对角块有定义**：`Q_h · K_hᵀ` 是"第 h 个头内部，N 个词互相打分"。

**非对角块 `Q_h · K_gᵀ`（h ≠ g）是"跨头打分"**——拿第 0 头的问题去问第 1 头的标签，两个子空间的坐标系统都不一样，这个分数没有任何意义，**必须屏蔽掉**。

屏蔽后的结构就是**分块对角矩阵**：

```
     ⎡ S_0    -∞    ...   -∞  ⎤
     ⎢ -∞    S_1    ...   -∞  ⎥         S_h = softmax(Q_h K_hᵀ / √d_k)   [N,N]
     ⎢  ...                   ⎥
     ⎣ -∞    ...    ...  S_11 ⎦
```

softmax 之后，`-∞` 处权重严格为 0 —— **每个词只在自己头内部做归一化，头与头之间零交流**（直到后面 `W_o` 才第一次交流）。

> **工程上不会真的建这个 `[12N, 12N]` 大矩阵**（12 倍算力浪费在被屏蔽的块上）。实际做法是 `transpose` 把头维挪到 batch 维，然后用 **batched GEMM（`torch.bmm` / `matmul` 的广播）一次算 12 个 `[N,N]`** —— 语义上等价于"只算块对角"，算力上一点不浪费。**大矩阵只是帮你"看见"结构的等价形式。**

---

## 四、第三处分块：输出与 `W_o` 的行分块

混合完之后，12 个头的输出拼回来（列分块）：

```
ctx = [ ctx_0 | ctx_1 | ... | ctx_11 ]      [N, 768]，12×64 = 768
```

再过输出投影 `W_o`（`(768, 768)`）。把 `W_o` 按**行**分块成 12 个 `[64, 768]`，则 `W_oᵀ` 是列分块：

```
out = ctx @ W_oᵀ + bo
    = [ctx_0 | ... | ctx_11] · [ Wo_0ᵀ | ... | Wo_11ᵀ ]ᵀ 的转置形态
    = Σ_i  ctx_i @ Wo_i            ← 分块乘法沿内部分块展开 = 求和
      ↑ [N,64]      ↑ [64,768]
```

写成显式求和：

```
out = ctx_0·Wo_0 + ctx_1·Wo_1 + ... + ctx_11·Wo_11 + bo        [N, 768]
```

**这一行正好回答了 08 里"为什么必须有 `W_o`"**：拼头只是堆叠，头与头零交流；`W_o` 的这 12 个行块把 12 个头的结果**加**到一起，这才是第一次跨头信息融合。没有 `W_o`，多头就是 12 个互不相干的模型。

---

## 五、HuggingFace 源码（精简版对照）

`transformers/models/bert/modeling_bert.py` 的 `BertSelfAttention`：

```python
class BertSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.num_attention_heads  = config.num_attention_heads                          # 12
        self.attention_head_size  = config.hidden_size // config.num_attention_heads    # 64
        self.all_head_size        = self.num_attention_heads * self.attention_head_size # 768

        self.query = nn.Linear(config.hidden_size, self.all_head_size)   # Wq [768,768]
        self.key   = nn.Linear(config.hidden_size, self.all_head_size)   # Wk
        self.value = nn.Linear(config.hidden_size, self.all_head_size)   # Wv

    def transpose_for_scores(self, x):                 # x: [B, N, 768]
        new_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_shape)                         # [B, N, 12, 64]   ← 切通道
        return x.permute(0, 2, 1, 3)                   # [B, 12, N, 64]   ← 头提到 batch 后

    def forward(self, hidden_states, attention_mask=None):
        q = self.transpose_for_scores(self.query(hidden_states))   # [B,12,N,64]
        k = self.transpose_for_scores(self.key(hidden_states))
        v = self.transpose_for_scores(self.value(hidden_states))

        scores = torch.matmul(q, k.transpose(-1, -2)) / math.sqrt(self.attention_head_size)
        #                                          [B,12,N,N]  ← 12 张表一次算完（batched GEMM）
        if attention_mask is not None:
            scores = scores + attention_mask            # padding mask: 0 → -10000（见 08 的 5.1）

        probs = torch.softmax(scores, dim=-1)           # 每行和为 1
        ctx   = torch.matmul(probs, v)                  # [B,12,N,64]

        ctx = ctx.permute(0, 2, 1, 3).contiguous()      # [B,N,12,64]  ← 必须 contiguous 才能 view
        ctx = ctx.view(ctx.size()[:-2] + (self.all_head_size,))   # [B,N,768]  ← 拼头
        return ctx
```

**逐行对应本篇的分块视角**：

| 源码行 | 分块矩阵含义 |
|---|---|
| `self.query(hidden_states)` | 一次 `X @ Wqᵀ`，`Wqᵀ` 的列分块 `[Wq_0ᵀ\|…\|Wq_11ᵀ]` → Q 天然按头排好 |
| `x.view(B, N, 12, 64)` | **切通道**：把 768 分成 `(12, 64)`，头 h 拿第 `[h*64, (h+1)*64)` |
| `.permute(0, 2, 1, 3)` | 把头维挪到 batch 后 → 12 个头变成 12 个"batch 样本"，可做 batched GEMM |
| `q @ k.transpose(-1,-2)` | **只算块对角**：一次性产出 12 张 `[N,N]`，等价于 `[12N,12N]` 的分块对角矩阵 |
| `softmax(dim=-1)` | 每个头内部独立归一化（对应大矩阵里同一行只在同一块内有值） |
| `permute + contiguous + view` | **拼头**：把 12 段 64 维接回 768 |

---

## 六、可运行验证：三种写法数值完全一致

把维度缩小到能打印（`hidden=8, 头数=2, d_k=4, N=5`），验证 A/B/C 三种写法 + `W_o` 求和形式互相等价。

```python
import math, torch

torch.manual_seed(0)
B, N, C, h = 2, 5, 8, 2          # batch, 词数, hidden, 头数
dk = C // h                       # 每头维度 = 4

x = torch.randn(B, N, C)
Wq, bq = torch.randn(C, C), torch.randn(C)
Wk, bk = torch.randn(C, C), torch.randn(C)
Wv, bv = torch.randn(C, C), torch.randn(C)
Wo, bo = torch.randn(C, C), torch.randn(C)

# ============ A. 按头循环（最直白，最慢）============
outs = []
for i in range(h):
    sl = slice(i * dk, (i + 1) * dk)
    Qi = x @ Wq[sl, :].T + bq[sl]                                  # [B,N,dk]  注意是行块
    Ki = x @ Wk[sl, :].T + bk[sl]
    Vi = x @ Wv[sl, :].T + bv[sl]
    si = Qi @ Ki.transpose(-1, -2) / math.sqrt(dk)                 # [B,N,N]
    ai = si.softmax(-1)
    outs.append(ai @ Vi)                                           # [B,N,dk]
ctxA = torch.cat(outs, dim=-1)                                     # [B,N,C]
outA = ctxA @ Wo.T + bo

# ============ B. 一次大 matmul + view/transpose（HF 真做法）============
Q, K, V = x @ Wq.T + bq, x @ Wk.T + bk, x @ Wv.T + bv               # 各 [B,N,C]

def split_heads(T):   return T.view(B, N, h, dk).transpose(1, 2)    # [B,N,C] -> [B,h,N,dk]
def merge_heads(T):   return T.transpose(1, 2).contiguous().view(B, N, C)

q, k, v = split_heads(Q), split_heads(K), split_heads(V)
s = q @ k.transpose(-1, -2) / math.sqrt(dk)                         # [B,h,N,N]
ctxB = merge_heads(s.softmax(-1) @ v)                               # [B,N,C]
outB = ctxB @ Wo.T + bo

# ============ C. 分块大矩阵（理解用，把头摊平成序列维）============
def stack_heads(T):                                                 # [B,N,C] -> [B,h*N,dk]
    return T.view(B, N, h, dk).permute(0, 2, 1, 3).reshape(B, h * N, dk)

Qb, Kb, Vb = stack_heads(Q), stack_heads(K), stack_heads(V)
Sbig = Qb @ Kb.transpose(-1, -2) / math.sqrt(dk)                    # [B, hN, hN]

block = torch.block_diag(*[torch.ones(N, N) for _ in range(h)]).bool()   # [hN,hN]
Sbig  = Sbig.masked_fill(~block, float("-inf"))      # 屏蔽所有跨头块 → 分块对角
ctxC  = (Sbig.softmax(-1) @ Vb).view(B, h, N, dk).permute(0, 2, 1, 3).reshape(B, N, C)
outC  = ctxC @ Wo.T + bo

# ============ D. W_o 的分块求和形式 ============
outD = sum(ctxB[:, :, i*dk:(i+1)*dk] @ Wo[i*dk:(i+1)*dk, :] for i in range(h)) + bo

# ============ 断言：四种写法完全一致 ============
print(torch.allclose(outA, outB, atol=1e-5))   # True  A ≡ B（整乘+reshape ≡ 按头循环）
print(torch.allclose(outA, outC, atol=1e-5))   # True  A ≡ C（分块对角大矩阵）
print(torch.allclose(outB, outD, atol=1e-5))   # True  W_o 行分块 = 按头求和
```

再验证一次"Q 的通道天然按头排好"：

```python
for i in range(h):
    sl = slice(i * dk, (i + 1) * dk)
    assert torch.allclose(Q[:, :, sl], x @ Wq[sl, :].T + bq[sl], atol=1e-5)
# 通过 → 说明"整乘后取第 i 段通道" ≡ "只用第 i 个行块单独算"
```

> 需要 `torch`。本机若没装，用 Google Colab 直接粘上去跑（08 系列笔记一直推荐的做法）。

---

## 七、工程细节（面试 / 读源码时会被问到）

1. **`transpose` / `permute` 是零拷贝的**：它只改张量的 `stride`（步长元数据），不动数据。所以"切头"本身**不花时间**。
2. **但 `view` 要求内存连续**：`permute` 之后张量不连续，直接 `view` 会报错，所以拼头时必须 `.contiguous()`——这一步**会真正拷贝一次数据**，是多头实现里唯一的数据搬运开销。
3. **`reshape` vs `view`**：`reshape` 会在需要时自动拷贝（等价于"必要时 `.contiguous().view()`"），`view` 不拷贝、不连续就报错。源码里用 `view` + 显式 `contiguous()`，意图更明确。
4. **为什么不真的用写法 C**：`[12N, 12N]` 里 11/12 的块被屏蔽，等于白算 12 倍。把头放进 batch 维用 **batched GEMM** 只算对角块，才是正确写法。
5. **头数必须整除 hidden_size**：`768 % 12 == 0` 才能用 `view(12, 64)` 均分。这是 BERT 选 12/16 头的原因之一（768=12×64，1024=16×64）。
6. **参数量没有变**：分块只是**视角**，参数还是 `Wq/Wk/Wv/Wo` 四个 `[768,768]`（+ 4 个 bias）。
   - 注意力部分每层 `4 × (768×768 + 768) = 2,362,368`
   - FFN 部分每层 `(768×3072+3072) + (3072×768+768) = 4,722,432`
   - **注意力 : FFN ≈ 1 : 2**，注意力占每层约 1/3（对照 03 的 encoder 占 77.7% 参数）。
7. **再往下优化就是 FlashAttention**：连那 12 张 `[N,N]` 都不写回显存，把 Q/K/V 分块（tiling）搬进 SRAM 里算完 softmax 再出来——名字里的 "block" 也是分块，但是为了**省显存带宽**而不是为了切头。仓库里有论文 `docs/papers/FlashAttention.pdf`。

---

## 八、常见疑问

**Q1：既然结果是"拼起来"，多头和一个 768 维的大头有什么区别？**
区别在**打分那一步**。一个大头会用全部 768 维算一张 `[N,N]` 表；多头是 12 张各自只用 64 维算出来的 `[N,N]` 表，然后**沿通道拼**、再经 `W_o` 混合。12 张表互不干扰，才能各学各的关系（08 的 4.5）。

**Q2：`view(B, N, 12, 64)` 为什么能保证"头 h = 第 h 段"？**
因为 `Q = X @ Wqᵀ` 时，`Wqᵀ` 的第 h 个**列块**就是 `Wq` 的第 h 个**行块** `Wq[h*64:(h+1)*64, :]`，而 `Q` 的第 h 个列块 = `X @ Wq_hᵀ`（分块乘法）。所以通道顺序 = 头的顺序，这是权重布局决定的，不是巧合。

**Q3：能不能让不同头有不同维度（比如 32 + 96）？**
理论可以，但 `view` 均分就不行了，得用循环或 `narrow` 切片。BERT / 主流实现都选均分，因为简单且能一次 batched GEMM。

**Q4：拼头之后一定要 `W_o` 吗？**
数学上可以不加（`W_o = I` 也能跑），但那样 12 个头永远不交流，实验效果明显变差。原论文和 BERT 都保留它。

**Q5：写法 C 里 `masked_fill(-inf)` 会不会产生 NaN？**
不会。每一行在**自己那个头**的块里有 N 个正常值，`softmax` 有合法分母。（如果某一整行全被屏蔽——比如那个 token 是 PAD 且你连它自己都屏蔽了——才会 NaN，所以 padding mask 至少保留对角/自身位置，实现上用 attention_mask 保证每行至少有一个 1。）

---

## 九、记忆卡

| 问题 | 答案 |
|---|---|
| 12 个头是 12 份权重吗 | **不是**。只有 `Wq/Wk/Wv/Wo` 四个 `[768,768]`；头 = 把 768 个**输出通道**切 12 段 |
| 一次 matmul 为什么能出 12 头 | `X@[Wq_0ᵀ\|…\|Wq_11ᵀ] = [Q_0\|…\|Q_11]`，分块乘法保证通道天然按头排好 |
| 头 h 占哪些通道 | 第 `[h*64, (h+1)*64)` 个 |
| 切头那两行在干嘛 | `view(B,N,12,64)` 切通道；`permute(0,2,1,3)` 把头提到 batch 后做 batched GEMM |
| 打分矩阵的结构 | `[12N,12N]` 的**分块对角**，只有 `(h,h)` 块有定义，跨头块屏蔽 |
| 头之间什么时候第一次交流 | `W_o`：`out = Σ_h ctx_h · Wo_h` |
| 为什么 `contiguous()` | `permute` 后不连续，`view` 要求连续；这一步是唯一真实拷贝 |
| 为什么不用真的 `[12N,12N]` | 11/12 的块被屏蔽，白算 12 倍；batched GEMM 只算对角块 |
| 三种写法的关系 | A（循环）≡ B（整乘+reshape）≡ C（分块对角），数值完全相同 |

**一句话**：**多头注意力 = 一次大 matmul 把 12 头一次算出来（`Wqᵀ` 的列分块） + 一次只算块对角的打分 + 一次按行分块的 `W_o` 求和。**

---

## 十、连接

- **接 08**：08 用"列切片"讲数学，本篇证明它 ≡ HuggingFace 的 `view/transpose` 实现；08 的坑 5（切行不切列）在这里有完整解释。
- **接 03**：本篇第七节的参数账，对上 03 的"encoder 占 77.7%"。
- **→ 09**：本篇的 `BertSelfAttention` 只是引擎，把它装进 BertLayer 的两套 Add & Norm 骨架，见 [09_bert_add_norm_residual.md](./09_bert_add_norm_residual.md)。
- **下一步 10**：自注意力只解决"谁跟谁相关"，还没编码位置——Positional Embedding 与绝对/相对位置编码。
- **延伸阅读**：`docs/papers/Attention_Is_All_You_Need.pdf`（3.2.2 Multi-Head Attention 原文）、`docs/papers/FlashAttention.pdf`（分块 tiling 的另一种"block"）。
