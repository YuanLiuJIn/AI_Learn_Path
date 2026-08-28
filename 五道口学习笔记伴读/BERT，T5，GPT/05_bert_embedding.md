# 05 · BERT Input Embedding 源码解析：word / position / token_type，以及 `LayerNorm + Dropout`

> 接 01（tokenizer 输出）、02（`token_type_ids`）、03（BERT 架构）、04（`no_grad` / `eval` / 训练策略）。
>
> 本篇回答一个问题：Tokenizer 已经给了 `input_ids`，BERT 怎样把一串整数变成真正送进 12 层 Encoder 的向量？
>
> 参考：
> - 本地 notebook：`bilibili_vlogs/fine_tune/bert/tutorials/03_bert_embedding.ipynb`
> - 教程仓库：`https://github.com/chunhuizhang/bilibili_vlogs/tree/master/fine_tune/bert/tutorials`
> - 视频合集：`https://space.bilibili.com/59807853/channel/collectiondetail?sid=496538`

---

## 〇、结论先行：`BertInput = Dropout(LayerNorm(E))` 是什么

这不是一个额外的神秘模块，而是 **BERT 的 embedding 层输出、进入第 1 层 Transformer Encoder 前的最后两步处理**。

先把三种 embedding 相加：

\[
E = E_{\text{word}} + E_{\text{position}} + E_{\text{token type}}
\]

再做：

\[
\text{BertInput} = \text{Dropout}(\text{LayerNorm}(E))
\]

对应 Hugging Face `BertEmbeddings.forward()` 的核心逻辑可理解为：

```python
word = self.word_embeddings(input_ids)
token_type = self.token_type_embeddings(token_type_ids)
position = self.position_embeddings(position_ids)

embeddings = word + token_type + position       # E
embeddings = self.LayerNorm(embeddings)
embeddings = self.dropout(embeddings)           # BertInput
return embeddings
```

> `BertInput` 是便于理解的名字；Hugging Face 源码中这份张量通常就叫 `embeddings`。它的形状不变，仍是 `[batch_size, seq_len, hidden_size]`，但数值已完成归一化和训练期正则化。

完整路线：

```text
原始文本
  ↓ tokenizer
input_ids / token_type_ids / attention_mask
  ↓ BertEmbeddings
词向量 + 位置向量 + 句子类型向量 = E
  ↓ LayerNorm
  ↓ Dropout
BertInput
  ↓（同时带着 attention_mask）
第 1 层 Transformer Encoder
  ↓
... 共 12 层（BERT-base）
```

---

## 一、先把输入三件套接回来

以一句英文 `this is a test sentence` 为例，教程 notebook 得到：

```python
{
    'input_ids': tensor([[ 101, 2023, 2003, 1037, 3231, 6251,  102]]),
    'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0]]),
    'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1]])
}
```

其中：

| 输入 | 形状 | 谁使用它 | 含义 |
|---|---|---|---|
| `input_ids` | `[B, L]` | `word_embeddings` | 每个 token 在词表中的行号 |
| `token_type_ids` | `[B, L]` | `token_type_embeddings` | 每个 token 属于句子 A（0）或 B（1） |
| `attention_mask` | `[B, L]` | 后续 Self-Attention | `1` 是有效 token，`0` 是 `[PAD]`，注意力不应关注它 |

`B=1`（一个样本）、`L=7`（7 个 token）时，`input_ids` 是 `[1, 7]`；经过 embedding 后，每个 token 会变成 768 维向量，形状变为 `[1, 7, 768]`。

> **关键边界**：`attention_mask` 不参与三种 embedding 的相加，也不在 `BertInput = Dropout(LayerNorm(E))` 这个公式里。它会在后面被转换为 Attention 的 mask，屏蔽对 padding 的关注。

---

## 二、三张可训练的「查表」

BERT-base-uncased 的隐藏维度 `hidden_size=768`。三种 embedding 都是 `nn.Embedding`：输入一个整数 ID，取出对应的一行向量；不是把 ID 当作连续数值做运算。

### 2.1 `word_embeddings`：这个 token 是什么

概念代码：

```python
self.word_embeddings = nn.Embedding(
    num_embeddings=30522,
    embedding_dim=768,
    padding_idx=0,
)
```

即一张 `30522 × 768` 的可训练参数表：

```text
第 0 行       → [PAD] 的向量
第 101 行     → [CLS] 的向量
第 2023 行    → "this" 的向量
...
第 30521 行   → 词表中最后一个 token 的向量
```

教程中手动调用：

```python
token_embed = model.embeddings.word_embeddings(input_ids)
# [1, 7] → [1, 7, 768]
```

所以 `input_ids` 中的 `2023` 不是「数值 2023 的特征」，而是「到词表第 2023 行取一条 768 维向量」。

这张表的参数量最大：

\[
30522 \times 768 = 23,440,896
\]

也就是约 2344 万参数。

---

### 2.2 `position_embeddings`：这个 token 在第几位

Self-Attention 本身只关心 token 之间的关联，不自带「先后顺序」概念；若只给词向量，它难以天然区分「猫追狗」与「狗追猫」。

BERT 用**可学习的绝对位置 embedding**补上顺序：

```python
self.position_embeddings = nn.Embedding(
    num_embeddings=512,
    embedding_dim=768,
)
```

这是一张 `512 × 768` 的表：

```text
第 0 行 → 第 0 个位置的向量
第 1 行 → 第 1 个位置的向量
...
第 511 行 → 第 511 个位置的向量
```

教程中：

```python
pos_ids = torch.arange(input_ids.shape[1])
# tensor([0, 1, 2, 3, 4, 5, 6])

pos_embed = model.embeddings.position_embeddings(pos_ids)
# [7] → [7, 768]
```

实际 BERT 源码通常会自动生成 / 缓存默认的 `position_ids`，调用者一般不必手工传入。经典 BERT 的表最多 512 行，因此它的标准最大长度是 **512 个位置**（含 `[CLS]`、`[SEP]`、`[PAD]` 等特殊 token）。

> BERT 的位置向量是**训练出来的参数**，不是原始 Transformer 里的固定正余弦编码。

---

### 2.3 `token_type_embeddings`：这个 token 属于句子 A 还是 B

也叫：

- segment embedding；
- sentence embedding；
- 由 `token_type_ids` 查得的 embedding。

概念代码：

```python
self.token_type_embeddings = nn.Embedding(
    num_embeddings=2,
    embedding_dim=768,
)
```

它只有两行：

```text
第 0 行 → 句子 A 的 768 维标记向量
第 1 行 → 句子 B 的 768 维标记向量
```

单句输入：

```text
[CLS] this is a test sentence [SEP]
  0     0   0  0    0     0    0
```

教程里：

```python
seg_embed = model.embeddings.token_type_embeddings(token_type_ids)
# [1, 7] → [1, 7, 768]
```

因为 7 个 `token_type_ids` 都是 `0`，所以 7 个位置查到的都是第 0 行——**输出的 7 个 segment 向量完全相同**。这不是信息丢失，而是在每个 token 上统一盖了一个「属于句子 A」的标签。

句对输入才会用到两行：

```text
[CLS] 句子 A 的 token [SEP] 句子 B 的 token [SEP]
  0          0          0          1          1
```

- 句子 A 和它后面的第一个 `[SEP]`：通常标 `0`；
- 句子 B 和最终 `[SEP]`：通常标 `1`。

若没传 `token_type_ids`，标准 BERT 实现通常默认补成全 `0`，即视为单段文本。

---

## 三、三张表怎样相加成 `E`

对 batch 中第 `b` 个样本、位置 `i` 的 token：

\[
E_{b,i} = W_{\text{word}}[\text{input\_id}_{b,i}]
        + W_{\text{position}}[i]
        + W_{\text{type}}[\text{token\_type\_id}_{b,i}]
\]

三项都是 768 维向量，因此可以逐维相加，结果仍是 768 维：

```text
词义向量（768 维）
+ 位置向量（768 维）
+ A/B 类型向量（768 维）
= 初始输入向量 E（768 维）
```

教程的手工复现：

```python
input_embed = token_embed + seg_embed + pos_embed.unsqueeze(0)
# [1, 7, 768] + [1, 7, 768] + [1, 7, 768]
# = [1, 7, 768]
```

`pos_embed` 原来是 `[7, 768]`，`unsqueeze(0)` 把它变成 `[1, 7, 768]`，以匹配 batch 维度。实际模型内部会利用广播或预先准备好带 batch 维度的位置 ID。

### 为什么是相加而不是拼接？

若拼接，维度会变为 `768 × 3 = 2304`，后面的每一层 Encoder 都要改成接受 2304 维，参数和计算量会陡增。

相加让三类信息叠在同一个 768 维语义空间中，保持 BERT 的统一接口：

```text
Encoder 的输入： [B, L, 768]
Encoder 的输出： [B, L, 768]
```

> 直觉：不是把「词是谁 / 在哪 / 属于哪句」塞进三个彼此隔离的抽屉，而是把它们叠加成这个 token 在当前上下文中的「带身份、带坐标、带归属」初始表示。

---

## 四、`LayerNorm(E)`：对每一个 token 的 768 个维度做归一化

三种向量相加后，数值尺度和分布会改变。BERT 先对每个 token 的合成向量做 LayerNorm，稳定送进深层网络的输入分布。

若某一个 token 的向量是：

\[
x = [x_1, x_2, \dots, x_H], \quad H=768
\]

LayerNorm 只在这个 token 自己的 `H` 个维度上计算：

\[
\mu = \frac{1}{H}\sum_{j=1}^{H}x_j
\]

\[
\sigma^2 = \frac{1}{H}\sum_{j=1}^{H}(x_j-\mu)^2
\]

\[
\hat{x}_j = \frac{x_j-\mu}{\sqrt{\sigma^2+\epsilon}}
\]

最后再做一层可学习的缩放、平移：

\[
y_j = \gamma_j\hat{x}_j + \beta_j
\]

- `ε`：极小常数，防止除以 0；BERT 常用 `1e-12`；
- `γ`（weight）和 `β`（bias）：各有 768 个可训练参数；
- 这组 `γ, β` 在所有 batch、所有位置共享，但每一个 hidden 维度有自己的值。

### 4.1 它归一化的轴到底是哪一个？

若整体张量是：

```text
E.shape = [B, L, H] = [32, 128, 768]
```

LayerNorm 的 `normalized_shape=768`，意味着：

```text
第 1 个样本、第 1 个 token：只在它自己的 768 维里算 mean / var
第 1 个样本、第 2 个 token：重新独立算一套 mean / var
...
第 32 个样本、第 128 个 token：也独立算一套 mean / var
```

它**不会**：

- 不在 batch 维（32 个样本）之间统计；
- 不在 token 位置维（128 个 token）之间统计；
- 不需要依赖 batch 大小。

所以 LayerNorm 很适合 NLP 里长度可变、batch 大小可变的序列模型。

### 4.2 它与 BatchNorm 的区别

| | LayerNorm（BERT 使用） | BatchNorm（CNN 常见） |
|---|---|---|
| 统计范围 | 一个 token 的 hidden 维 | 一个 batch 中同一通道的样本 |
| 是否依赖 batch 大小 | 否 | 是 |
| batch=1 是否稳定 | 是 | 训练时可能不稳定 |
| 适合变长文本 | 是 | 通常不如 LayerNorm 自然 |

### 4.3 一个容易说错的细节

常说「LayerNorm 后均值为 0、方差为 1」，这只精确描述了中间的标准化结果 `x̂`（并忽略 `ε` 的微小影响）。

真正的输出是：

\[
y = \gamma\hat{x} + \beta
\]

由于 `γ`、`β` 可训练，**最终输出 `y` 不保证严格均值为 0、方差为 1**。模型保留这两个参数，正是为了能在「数值稳定」和「任务所需的表达尺度」之间学习平衡。

### 4.4 LayerNorm 的作用

1. **稳定尺度**：三种 embedding 相加后，不让某一来源或某些 token 的数值规模失控；
2. **帮助优化**：后续 12 层反复做 Attention、残差连接、FFN，较稳定的输入通常让梯度传播和收敛更顺畅；
3. **逐 token 独立**：不会让一个样本的统计量影响另一个样本。

> 它不是删掉词义或位置，而是对已经融合的信息重新调节数值尺度。

---

## 五、`Dropout(...)`：训练时随机遮住部分 hidden 维度

LayerNorm 后，BERT 在 embedding 输出处应用 Dropout：

```python
embeddings = self.dropout(embeddings)
```

对每个元素独立随机处理。设 dropout 概率为 `p`（BERT-base 常见 `hidden_dropout_prob=0.1`）：

### 5.1 训练模式：`model.train()`

随机采样 mask：

\[
m_j \sim \text{Bernoulli}(1-p)
\]

PyTorch 采用 *inverted dropout*，实际输出是：

\[
\text{Dropout}(y_j)=\frac{m_j}{1-p}y_j
\]

- 概率 `p`：该维被置为 `0`；
- 概率 `1-p`：该维保留，但除以 `1-p` 放大；
- 放大的目的：让训练期输出的期望值仍等于输入，不必等到推理期再额外缩放。

例如 `p=0.1`：保留下来的维度会乘以 `1 / 0.9 ≈ 1.111`，不是简单地原样保留。

它的作用是避免模型死记、过度依赖某几个固定维度，从而提升泛化能力。

### 5.2 推理 / 评估模式：`model.eval()`

```python
model.eval()
```

这时 Dropout 变成恒等操作：

\[
\text{Dropout}(y)=y
\]

不会随机置零，因此同一个输入的结果稳定可复现（忽略其他随机源）。

> 接 04：`model.eval()` 只切换 Dropout、BatchNorm 等模块的行为，**不等于** `torch.no_grad()`。推理常见正确组合是：
>
> ```python
> model.eval()
> with torch.no_grad():
>     outputs = model(**inputs)
> ```
>
> - `eval()`：关闭 Dropout 的随机丢弃；
> - `no_grad()`：不建计算图，节省显存和计算。

---

## 六、为什么顺序是 `LayerNorm → Dropout`

BERT 采用：

```text
三种 embedding 相加 → LayerNorm → Dropout → Encoder
```

可以这样理解：

1. **先 LayerNorm**：先把原始的合成表示 `E` 调整到稳定、可控的数值尺度；
2. **后 Dropout**：再只在训练期引入随机扰动，作为正则化；
3. **送进 Encoder**：让第 1 层接收的是稳定基础上经过训练增强的表示。

这不是所有神经网络唯一正确的顺序。不同 Transformer 架构可采用不同的归一化位置（例如 Pre-LN / Post-LN 主要讨论的是每个 Encoder block 内的 LayerNorm 位置）。但对于经典 BERT 的**输入 embedding 层**，这个顺序就是其预训练时采用并验证有效的设计。

---

## 七、完整例子：`[CLS] 句子 A [SEP] 句子 B [SEP]`

假设分词后是：

```text
位置:              0      1      2      3      4      5      6
Token:          [CLS]    我    喜欢  [SEP]  BERT    很   [SEP]
input_ids:        101    ...    ...    102    ...    ...    102
token_type_ids:     0      0      0      0      1      1      1
position_ids:       0      1      2      3      4      5      6
```

第 4 个位置（`BERT`）的合成表示为：

\[
E_4 = \text{word\_table}[\text{BERT 的 ID}]
    + \text{position\_table}[4]
    + \text{type\_table}[1]
\]

含义是：

```text
“BERT”这个 token 的词义
+ “它排在整个输入第 4 位”
+ “它属于句子 B”
```

每个位置都按同样方式得到一个 768 维的 `E_i`。整句组成：

\[
E \in \mathbb{R}^{1 \times 7 \times 768}
\]

接着：

```text
E
↓ LayerNorm（每个位置各自对 768 维归一化 + γ/β 仿射变换）
↓ Dropout（仅训练期，以 p=0.1 为例随机遮住部分维度）
BertInput: [1, 7, 768]
↓
Encoder 第 1 层
```

---

## 八、`[PAD]` 和 `attention_mask` 的易错点

假设为了对齐长度，输入末尾加了 `[PAD]`：

```text
[CLS] 我 喜欢 BERT [SEP] [PAD]
mask:  1    1  1    1     1     0
```

容易产生一个误解：`attention_mask=0` 会让这个位置在 embedding 阶段变成零向量。

**不是。** `attention_mask` 不参与 `E` 的三项相加；`[PAD]` 位置仍可能有：

```text
word embedding（通常是 padding 行）
+ position embedding（该位置自己的向量）
+ token type embedding（A 或 B 的向量）
```

`attention_mask` 的主要工作发生在 Self-Attention：模型把 `[PAD]` 位置作为 key/value 屏蔽，避免有效 token 把注意力分配给 padding。任务最终计算 loss、pooling 或输出时，也通常会继续忽略 padding 位置。

> 所以请把两者分开记：**embedding 管“表示成什么向量”；attention mask 管“注意力时允许看谁”。**

---

## 九、参数量与形状总表（BERT-base-uncased）

| 组件 | 表大小 / 参数 | 输入 | 输出形状（例：`B=1, L=7`） | 解决的问题 |
|---|---:|---|---|---|
| `word_embeddings` | `30522 × 768` | `input_ids` | `[1, 7, 768]` | token 是什么 |
| `position_embeddings` | `512 × 768` | `position_ids` | `[7, 768]` / 广播后 `[1, 7, 768]` | token 在第几位 |
| `token_type_embeddings` | `2 × 768` | `token_type_ids` | `[1, 7, 768]` | 属于句子 A 还是 B |
| 三者相加 `E` | 无新参数 | 三路向量 | `[1, 7, 768]` | 融合三类信息 |
| `LayerNorm` | `γ(768) + β(768)` | `E` | `[1, 7, 768]` | 稳定数值尺度 |
| `Dropout` | 无可训练参数 | LayerNorm 输出 | `[1, 7, 768]` | 训练期防过拟合 |

---

## 十、一句话总收 + 与前面笔记的连接

> **`BertInput = Dropout(LayerNorm(E))` 的意思是：BERT 先把“词是谁、在第几位、属于哪句话”三种 768 维向量相加成 `E`；再对每个 token 的 768 个维度独立做 LayerNorm；最后仅在训练时经 Dropout 随机遮住部分维度，得到送入 Transformer Encoder 的最终输入。**

与前文连接：

1. **接 01 的 tokenizer**：`input_ids` 是 `word_embeddings` 的行号；它不是连续数值特征。
2. **接 02 的 `token_type_ids`**：0/1 不是直接相加的数字，而是分别查 `token_type_embeddings` 的第 0/1 行。
3. **接 03 的 BERT 架构**：本篇 `BertEmbeddings` 正是 `embeddings → 12 层 encoder → pooler` 中的第一站。
4. **接 04 的 `no_grad` / `eval`**：`eval()` 会关闭此处 Dropout 的随机性；`no_grad()` 则是不建计算图，两者功能不同但推理时常一起用。
5. **接后续 Self-Attention**：`attention_mask` 不进 embedding 求和，它在 Encoder 的注意力计算里负责屏蔽 `[PAD]`。

---

## 十一、下一步

- 看 Encoder 第 1 层如何接收 `[B, L, 768]` 的 `BertInput`；
- 继续拆 `Self-Attention`：Q、K、V 从哪里来，`attention_mask` 如何变成注意力分数里的负无穷；
- 亲手打印 `word / position / token_type / LayerNorm / Dropout` 五个中间张量，验证形状和训练 / 推理模式下的差异。
