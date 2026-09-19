# 14 · AttentionHead 与 MultiHeadAttention：把 768 切成 12 × 64

> **接 13**：13 集把 scaled dot-product 的公式推完了，也留下了那个"`softmax` 变成单位矩阵"的尴尬结果。结尾说还差**三块拼图**——① `W_q/W_k/W_v` 可学习投影；② **分头 / 拼头 / `W_o`**；③ position encoding + mask。本篇补上**前两块**：把 attention 从"一个公式"变成一个**能装参数、能训练、能堆叠的 `nn.Module`**。
>
> **视频**：`BV14V4y1f7L2`（合集第 15 集）
> **本期 code**：`github.com/chunhuizhang/bert_t5_gpt/blob/main/tutorials/03_transformer_architecture_multi_head_attention.ipynb`
> **本地**：`bert_t5_gpt/tutorials/03_transformer_architecture_multi_head_attention.ipynb`（**54 个 cell**；⚠️ **cell 0–40 是 13 集内容的重录**，本篇新代码从 **cell 41** 开始）
> **系列视频**：`space.bilibili.com/59807853/channel/collectiondetail?sid=496538`
> **环境**：`torch 2.0.0+cu118` / `transformers 4.28.0.dev0`
>
> **一句话主旨**：**`AttentionHead` = 三个 `Linear(768→64)` + 一次 scaled dot-product；`MultiHeadAttention` = 12 个 `AttentionHead` + `torch.cat` 拼回 768 + 一个 `Linear(768→768)` 的 `W_o`。** 全部代码只有一个等式撑着——**`768 = 64 × 12`**。
>
> **本篇要还的债**：13 集证明了"**不投影的注意力 ≈ 恒等变换**"。本篇的 `W_q/W_k/W_v` 就是**把那个单位矩阵拆掉**的东西——这是全集最该盯住的一条因果链。

---

## 〇、30 秒直觉

| 问题 | 答案 |
|---|---|
| `AttentionHead` 是什么 | **一个头**：把 768 维的输入压到 64 维的三个子空间（`q/k/v`），在这 64 维里算一次 scaled dot-product，输出还是 64 维 |
| `MultiHeadAttention` 是什么 | **12 个头并排**，每个吐 64 维，`cat` 起来回到 768 维，再过 `W_o` 混合 |
| 为什么必须分头 | 一个头只能在一个子空间里比"相关度"；12 个头 = **12 种不同的相关度视角**同时工作 |
| 为什么是 64 | 因为 `768 = 64 × 12`——**预算固定，切成 12 份**（§五会证明这样切参数量不变） |
| 本集和 13 集的关系 | 13 集：`Q = K = V = embedding` → softmax 是单位阵 → **注意力什么都没做**。本集：装上 `W_q/W_k/W_v` → **那个单位阵就消失了** |

一句话：**注意力缺的不是公式，是"可学习的视角"；`W_q/W_k/W_v` 提供视角，12 个头提供 12 个视角。**

---

## 一、notebook 全景（54 个 cell，五段）

| 段 | cell | 内容 | 状态 |
|---|---|---|---|
| **A. 架构综述** | 0–8 | 三种架构、encoder layer 结构、contextual embedding、`apple`/`flies` 两个例子 | 复习（= 13 集） |
| **B. 公式** | 9–16 | `x'_i = Σ_j w_ji x_j`、scaled dot-product 四步 + 两张图 | 复习 |
| **C. 可视化 + 比喻** | 17–25 | `bertviz.neuron_view` 看单个头、Q/K/V 的"逛超市"比喻 | 复习 |
| **D. 无投影手算** | 26–40 | embedding → `Q=K=V` → 打分 → softmax → **单位矩阵** | 复习（13 集 §六） |
| **E. 多头（新内容）** | **41–53** | `mha.png` → `AttentionHead` → `MultiHeadAttention` → 跑形状 → `head_view` | ⭐ **本篇** |

**先给读者排个雷**：这个 notebook 的前 41 个 cell 和 13 集（notebook 02）几乎逐字相同——

- 同一个 `scaled_dot_product_attention` 函数在本篇出现了 **两次**（cell 39 和 cell 45）；
- 同一段"Project → scores → weights → value"的 markdown 也出现了 **两次**（cell 16 和 cell 44）。

**这不是笔误，是课程的设计**：cell 39/16 是"13 集讲完了"，cell 45/44 是"现在把它当**已有积木**再引用一次，准备往上搭"。所以你**不需要重跑前 41 个 cell**，直接从 **cell 41** 开始读代码即可。

---

## 二、为什么"不分头"不行：13 集留下的坑

回顾 13 集的实验（notebook 02 / 本篇 cell 35–36）：把 embedding 直接当 Q/K/V 时，

```text
attn_scores 的对角线  ≈ 27.5 ~ 29.2        ← ‖x‖² / √768
attn_scores 的非对角  ≈  -2 ~ +0.8         ← 两个独立随机向量的点积 / √768
```

差距被 `softmax` 放大成（本篇 cell 36 的真实输出）：

```text
tensor([[[1.0000e+00, 1.1683e-12, 1.0037e-13, 9.4935e-14, 8.9637e-13],
         [3.6049e-13, 1.0000e+00, 1.8145e-13, 4.6910e-13, 5.1142e-14],
         ...
```

**`softmax` 输出 ≈ 单位矩阵** → `attn_outputs = I · V = V = 输入` → **注意力什么都没做**（cell 38 的输出就是原封不动的 `input_embeddings`）。

cell 41 的标题就是答案：

```markdown
### multi head (self/cross)attention
```

要修好它，必须同时换掉两件事：

| # | 换掉什么 | 为什么有效 |
|---|---|---|
| ① | `Q/K/V` 改为 `W_q/W_k/W_v · x` | 对角线优势 `‖x‖²` **消失了**（见下） |
| ② | 768 维切成 **12 × 64** | 一个头只能有一个"相关度视角"，12 个头能同时看 12 种关系 |

### 2.1 为什么投影能让单位矩阵消失（一行的推导）

不投影时，对角线元素是

```text
q_i · k_i = x_i · x_i = ‖x_i‖² ≈ d = 768
```

**它的期望正比于维度 `d`，而非对角线是两个独立向量的点积、期望为 0**——这就是单位阵的来源。

投影之后（`Wq, Wk` 随机初始化、`Wq Wkᵀ ≠ I`）：

```text
q_i · k_i = x_iᵀ · (Wq Wkᵀ) · x_i
```

**对角线变成了一个二次型 `x_iᵀ M x_i`，而 `M = Wq Wkᵀ` 的迹的期望是 0**——对角线和非对角线**回到同一个量级**，单位阵塌掉，`softmax` 才给出真正有分布的权重。

粗算一下量级（`nn.Linear` 默认初始化是 `U(-1/√768, 1/√768)`，方差 ≈ `1/2304`）：

```text
q / k 每个分量:      var ≈ 768 × 1/2304 = 1/3
q · k (64 维点积):   sd  ≈ √(64 × (1/3)²) ≈ 2.67
÷ √d_k = √64 = 8:    sd  ≈ 0.33
```

于是 **score 的典型大小从 13 集的 ±27.7 掉到 ±0.3 左右（差约 80 倍）**——`softmax` 不再饱和成 one-hot。

> **但别高兴太早**：本篇的 `MultiHeadAttention` 是**随机初始化、没训练过**的。它的注意力**既不接近单位阵、也不是均匀分布**，而是一堆"无意义的随机分布"。**真正的语义要等训练**——这也正是 §七 `head_view` 必须换成**真 BERT** 的原因。

---

## 三、`AttentionHead`：一个头就是"三行投影 + 一次打分"

notebook cell 46，全文只有 14 行：

```python
class AttentionHead(nn.Module):
    def __init__(self, embed_dim, head_dim):
        super().__init__()
        # learnable parameters
        self.Wq = nn.Linear(embed_dim, head_dim)
        self.Wk = nn.Linear(embed_dim, head_dim)
        self.Wv = nn.Linear(embed_dim, head_dim)

    def forward(self, hidden_states):
        # project
        q = self.Wq(hidden_states)
        # project
        k = self.Wk(hidden_states)
        # project
        v = self.Wv(hidden_states)
        attn_outputs = scaled_dot_product_attention(q, k, v)
        return attn_outputs
```

**逐行读**（`embed_dim=768, head_dim=64`，输入 `[1, 5, 768]`）：

| 行 | 做什么 | 形状变化 |
|---|---|---|
| `self.Wq = nn.Linear(768, 64)` | 定义一个 **768→64** 的可学习投影（含 bias） | 参数 `768×64 + 64 = 49,216` |
| `q = self.Wq(hidden_states)` | 每个 token 投到 64 维的"**问题空间**" | `[1, 5, 768] → [1, 5, 64]` |
| `k = self.Wk(hidden_states)` | 投到 64 维的"**标签空间**" | `[1, 5, 64]` |
| `v = self.Wv(hidden_states)` | 投到 64 维的"**内容空间**" | `[1, 5, 64]` |
| `scaled_dot_product_attention(q, k, v)` | 在 64 维里打分 → softmax → 加权求和 | `→ [1, 5, 64]` |

**三个关键认知**：

1. **`embed_dim ≠ head_dim`**。`AttentionHead.__init__` 同时收这两个参数，**这是它和 13 集那段代码最本质的差别**——13 集的输入输出都是 768，这里"进 768 出 64"，**降维就是分头的物理含义**。
2. **`Wq / Wk / Wv` 就是 13 集说的"可学习参数"**。cell 35 的注释写着"`W_q, W_k, W_v: nn.Linear`，作用在 token_embedding 得到，或者说依然是通过 learning 最终确定的"——**这句话在本篇变成了三行 `nn.Linear`**。
3. **`scaled_dot_product_attention` 里 `dim_k = key.size(-1)` 现在等于 64**，所以缩放因子是 `√64 = 8`（不是 13 集的 `√768 ≈ 27.71`）。

| | 13 集（无投影） | 本篇（分头后） |
|---|---|---|
| Q / K / V 来源 | embedding 本身（`= x`） | `W_q/W_k/W_v · x` |
| `dim_k` / `d_k` | 768 | **64** |
| 缩放因子 `√d_k` | `√768 ≈ 27.71` | **`√64 = 8`** |
| `attn_weights` | ≈ 单位阵（退化） | 真正的分布（训练后有意义） |

> **一个容易漏掉的细节**：这里的 `k` 和 `v` 都来自**同一个** `hidden_states`。这就是**自注意力（self-attention）**的定义。如果 `k/v` 换成另一个序列（比如编码器的输出），同样的类就变成**交叉注意力（cross-attention）**——cell 41 的标题 `multi head (self/cross)attention` 正是在提示这一点，**两个概念共享同一份代码**。

---

## 四、`MultiHeadAttention`：12 个头 + `W_o`

notebook cell 47：

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        embed_dim = config.hidden_size            # 768
        num_heads = config.num_attention_heads    # 12
        # 768/12 == 64
        head_dim = embed_dim // num_heads
        self.heads = nn.ModuleList([
            AttentionHead(embed_dim, head_dim) for _ in range(num_heads)
        ])
        # 768 => 768
        self.output_layer = nn.Linear(embed_dim, embed_dim)

    def forward(self, hidden_state):
        print(f'input hidden_state: {hidden_state.shape}')
        print(f'head(hidden_state): {self.heads[11](hidden_state).shape}')
        x = torch.cat([head(hidden_state) for head in self.heads], dim=-1)
        print(f'cat heads: {x.shape}')
        x = self.output_layer(x)
        return x
```

### 4.1 `nn.ModuleList` 不是装饰，是**必须**

那句 `nn.ModuleList([...])` 是**全篇最容易写错、后果最严重**的一行。对比：

```python
self.heads = [AttentionHead(embed_dim, head_dim) for _ in range(12)]   # ❌ 普通 list
self.heads = nn.ModuleList([AttentionHead(embed_dim, head_dim) ...])   # ✅ 正确
```

| 写法 | `model.parameters()` | `.to(device)` / `.cuda()` | 会被优化器更新 |
|---|---|---|---|
| 普通 Python `list` | **看不到这 12 个头** | **不迁移** | ❌ 不训练 |
| `nn.ModuleList` | 全部注册在册 | 一起迁移 | ✅ |

> 用普通 list 的后果**极其隐蔽**：`__init__` 不报错、`forward` 不报错、训练能跑、**loss 也照样下降**（因为 `output_layer` 还在学）——但你实际上在训练"**12 个完全冻结的随机映射**"。这种 bug 只能靠 `sum(p.numel() for p in model.parameters())` 对参数量才能发现。

### 4.2 `torch.cat(..., dim=-1)`：这就是"拼头"

- 12 个头各自吐 `[1, 5, 64]`；
- `cat(dim=-1)` 沿**最后一维**接起来 → `[1, 5, 768]`；
- 头的**顺序**就是通道的顺序：头 `0` 占通道 `0–63`，头 `1` 占 `64–127`，……，头 `11` 占 `704–767`。

**这一步就是论文里的 "concat"**。13 集 §三讲的 `x'_i = Σ_j w_ji v_j`，在多头里变成"每个头先各算一次 `Σ_j w^{(h)}_{ji} v^{(h)}_j`，再拼起来"。分块矩阵视角下这一步是列分块拼接——已在 [08B](./08B_bert_multihead_block_matrix.md) 推过。

### 4.3 `self.output_layer`：论文里的 `W^O`

拼完的 `[1, 5, 768]` 里，"通道"是按头硬拼的——**头 0 和头 1 的信息彼此还没交流过**。`output_layer`（即论文的 `W^O`）做两件事：

1. **跨头混合**：输出第 `i` 维是全部 768 维（12 个头）的加权和，让不同头的结论融合；
2. **回到原空间**：形状 `768 → 768`，可以直接和输入做残差相加（下一集要做的事）。

---

## 五、参数量对账：分头是"免费"的

这是本篇**最值得自己算一遍**的一张表。

### 5.1 "12 个 `Linear(768,64)`" vs "1 个 `Linear(768,768)`"

| 方案 | 单项参数（含 bias） | 数量 | 小计 |
|---|---|---|---|
| 单头不分的 `Wq` | `768×768 + 768 = 590,592` | ×3（q/k/v） | **1,771,776** |
| `AttentionHead` 的 `Wq` | `768×64 + 64 = 49,216` | ×3（q/k/v）×12（头） | **1,771,776** |

```text
12 × 3 × 49,216   = 1,771,776
 3 ×    590,592   = 1,771,776     ← 一模一样
```

**结论：把 768 维切成 12 个 64 维的头，`W_q/W_k/W_v` 的总参数量和"单头但不分头"完全相同。分头不是"增加容量"，而是"把同一份预算改成 12 个独立视角"。**

### 5.2 加上 `W_o`，和真 BERT 严丝合缝

| 模块 | 参数量 |
|---|---|
| 12 头 × (Wq + Wk + Wv) | 1,771,776 |
| `output_layer`（= `W_o`） | `768×768 + 768 = 590,592` |
| **`MultiHeadAttention` 总计** | **2,362,368** |

对照真 BERT（§八会细说）的 `BertLayer`：

| BERT 模块 | 参数量 |
|---|---|
| `attention.self.query` + `key` + `value` | `3 × 590,592 = 1,771,776` |
| `attention.output.dense`（= `W_o`） | 590,592 |
| **`attention` 部分合计** | **2,362,368** ✅ |

**完全相等。** 也就是说：**notebook 里手写的 `MultiHeadAttention`，参数量和真 BERT 的注意力子层一字不差**（真 BERT 还多出 `attention.output.LayerNorm` 的 1,536 个参数，那是下一集的内容）。

> **所以"12 个头"到底换来了什么？** 换的不是参数量，而是**注意力的结构**：
> - 单头：一个 `5×5` 的 softmax，覆盖完整的 768 维；
> - 多头：**12 个 `5×5` 的 softmax**，各自只在 64 维子空间里比。
>
> 同一个 `flies`，可以"在 64 维子空间 A 里和 `time` 高度相关"，同时"在 64 维子空间 B 里和 `fruit` 高度相关"——**这是单个大 softmax 做不到的**（它只能给出一组归一化权重）。

---

## 六、跑一遍：形状的"分—拼"往返

### 6.1 拿一份真 config（cell 48）

```python
model_ckpt = 'bert-base-uncased'
config = AutoConfig.from_pretrained(model_ckpt)
```

打印出来的 `BertConfig` 里，本篇只关心这几个字段：

| 字段 | 值 | 在本篇的作用 |
|---|---|---|
| `hidden_size` | **768** | `embed_dim` |
| `num_attention_heads` | **12** | 头的个数 |
| `vocab_size` | 30522 | `nn.Embedding` 的词表大小 |
| `attention_probs_dropout_prob` | **0.1** | 真 BERT 有、手写版没有（§八） |
| `num_hidden_layers` | **12** | ⚠️ **和 `num_attention_heads` 的 12 不是一回事**（§九） |
| `transformers_version` | `4.28.1` | ⚠️ 这是 **checkpoint 存盘时**的版本写死在 config 里的，**不等于**你本地跑的版本（本篇 notebook 的实际版本是 `4.28.0.dev0`） |

### 6.2 造输入（cell 50）

```python
mha = MultiHeadAttention(config)          # cell 49

token_embedding = nn.Embedding(config.vocab_size, config.hidden_size)
sample_text = 'time flies like an arrow'
model_inputs = tokenizer(sample_text, return_tensors='pt', add_special_tokens=False)
input_embeddings = token_embedding(model_inputs['input_ids'])
input_embeddings.shape
# torch.Size([1, 5, 768])
```

**注意 `add_special_tokens=False`**：所以 `time flies like an arrow` 是**干净的 5 个 token**，没有 `[CLS]`/`[SEP]`，才有 `[1, 5, 768]`。这和 13 集保持一致（`[1, 5, 768]`）。

### 6.3 forward 的真实输出（cell 51）

```text
input hidden_state: torch.Size([1, 5, 768])
head(hidden_state): torch.Size([1, 5, 64])      ← 单个头降维到 64
cat heads:          torch.Size([1, 5, 768])     ← 12 × 64 拼回 768
```

返回值：

```text
tensor([[[-0.0367, -0.1626, -0.0573,  ...,  0.0750, -0.0801,  0.0180],
         [-0.0486, -0.1244, -0.1812,  ...,  0.0597, -0.0203,  0.0569],
         [-0.0389, -0.0601, -0.1183,  ...,  0.0795, -0.1367,  0.0241],
         [ 0.0482, -0.1169, -0.1876,  ...,  0.1026, -0.0929,  0.0467],
         [ 0.0248, -0.1505, -0.1073,  ...,  0.1200, -0.1589, -0.0224]]],
       grad_fn=<ViewBackward0>)
```

**三条读数**：

1. **形状闭环了**：`[1,5,768] → 12×[1,5,64] → [1,5,768] → [1,5,768]`。**这就是"多头注意力可以嵌进任意深度的 Transformer"的全部原因**——输入输出同形。
2. **数值全在 `±0.2` 以内**。这是**默认初始化**的必然结果：`q·k` 的 score 只有 `±0.3` 量级 → softmax 接近均匀 → 输出是 5 个 `v` 的平均，再乘一个权重只有 `±1/√768 ≈ ±0.036` 的 `output_layer`。**别从这些数字里读语义。**
3. **`grad_fn=<ViewBackward0>`**——`torch.cat` 的反向是 `View`，说明梯度能从 `output_layer` 一路流回 12 个头（以及 `token_embedding`）。

### 6.4 想自己验证"12 个头真的不一样"

随机初始化时，12 个头的权重互不相同，所以它们的输出必然不同（**但"不同"≠"有意义"**）。可以加几行看看：

```python
x = input_embeddings
outs = torch.stack([head(x) for head in mha.heads], dim=1)   # [1, 12, 5, 64]
print(outs.shape)
print((outs[0, 0] - outs[0, 1]).abs().mean())                 # 头 0 vs 头 1 的平均差异
```

更值一算的是注意力矩阵的形状：**一个头给的是 `[5, 5]`，12 个头叠起来才是 `[12, 5, 5]`**。这和 [07](./07_bert_model_outputs.md) 里 `attentions` 的 `[1, 12, 22, 22]` 完全对上（那里 batch=1、seq=22）。

> **一个自我检查**：`sum(p.numel() for p in mha.parameters())` 应该是 **2,362,368**。如果你写成了普通 list，这个数字会**少 1,771,776**——这是发现 §4.1 那个 bug 最快的办法。

---

## 七、`head_view`：看真 BERT 的第 8 个头（cell 52）

终于要从"随机初始化"切到"训练过的模型"了：

```python
from bertviz import head_view
model = AutoModel.from_pretrained(model_ckpt, output_attentions=True)

sentence_a = "time flies like an arrow"
sentence_b = "fruit flies like a banana"
viz_inputs = tokenizer(sentence_a, sentence_b, return_tensors='pt')
print(viz_inputs)
attention = model(**viz_inputs).attentions
sentence_b_start = (viz_inputs.token_type_ids == 0).sum(dim=1)
print(sentence_b_start)
tokens = tokenizer.convert_ids_to_tokens(viz_inputs.input_ids[0])
head_view(attention, tokens, sentence_b_start, heads=[8])
```

**真实输出**：

```text
{'input_ids': tensor([[ 101, 2051, 10029, 2066, 2019, 8612, 102, 5909, 10029, 2066,
                       1037, 15212, 102]]),
 'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]]),
 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])}
tensor([7])
```

### 7.1 逐项拆解

| 项 | 含义 |
|---|---|
| `tokenizer(sentence_a, sentence_b, ...)` | **传两个句子** = BERT 的 NSP 输入格式，自动拼成 `[CLS] A [SEP] B [SEP]` |
| 13 个 token | `[CLS] time flies like an arrow [SEP] fruit flies like a banana [SEP]` |
| `token_type_ids` | **前 7 个 `0`、后 6 个 `1`** —— `0` 段是句子 A，`1` 段是句子 B |
| `sentence_b_start = 7` | `(token_type_ids == 0).sum()` = 前 7 个位置属于 A → **第 7 个位置起是 B** |
| `attention` | `output_attentions=True` 才返回；12 层 × `[1, 12, 13, 13]` |
| `heads=[8]` | **只画头索引 8**（0-indexed，即第 9 个头），避免 12 个头糊成一片 |

### 7.2 这个例子为什么被选中：`10029` 出现了两次

看 token id 列表：**`10029` 在位置 2 和位置 8 各出现一次**。

```text
位置:  0     1     2      3     4      5     6     7      8      9     10    11      12
token: [CLS] time flies  like  an   arrow  [SEP] fruit  flies  like   a   banana  [SEP]
type:    0     0    0      0     0      0      0     1      1      1     1     1      1
                └────── 句子 A ──────┘             └───────── 句子 B ─────────┘
```

**同一个词、同一个 subtoken id，被放进了两个完全不同的语境**：

- 句子 A：`time flies like an arrow` —— `flies` 是**动词**（"时间飞逝"）；
- 句子 B：`fruit flies like a banana` —— `flies` 是**名词**（"果蝇"）。

`head_view` 画的就是"**位置 2 的 `flies` 连向哪些词、位置 8 的 `flies` 连向哪些词**"。这正是 §五结尾说的"**多头才能同时容纳两种解释**"的可视化证据：位置 2 的连线应该偏向 `time`/`arrow` 一侧，位置 8 的偏向 `fruit`/`banana` 一侧。**具体哪条线亮、亮多少，得自己点开图看**——这也是这类可视化唯一正确的用法。

### 7.3 `neuron_view` vs `head_view`（和 13 集的呼应）

| | `neuron_view`（13 集 cell 23） | `head_view`（本篇 cell 52） |
|---|---|---|
| 看什么 | **单个 query 神经元**和单个 key 神经元的匹配 | **整个头**的完整注意力矩阵 |
| 参数 | `layer=0, head=8` | `heads=[8]` |
| 用途 | 理解 `q·k` 是怎么一格一格算出来的 | 理解"头"作为一个整体的行为模式 |

**两者都在讲同一件事：`q · k`。** 一个放大到神经元，一个拉远到头。

> **加载时的警告是正常的**：`Some weights of the model checkpoint at bert-base-uncased were not used ... ['cls.predictions.*', 'cls.seq_relationship.*']`——`bert-base-uncased` 的 checkpoint 里存着预训练头（MLM + NSP），而这里只加载 `BertModel`（裸编码器），所以那些 head 参数被**丢弃**。**这是预期行为，不是报错。** 相关讨论见 [12](./12_fine_tune_transformers_classification.md) 里 `LABEL_0~5` 的成因。

---

## 八、教学版 vs 真 BERT：三处差别

notebook 的 `MultiHeadAttention` 是**参数量完全一致、但写法不同**的教学版。差别如下：

| # | 项目 | notebook 手写版 | 真 BERT（`BertSelfAttention`） |
|---|---|---|---|
| 1 | **头怎么切** | 12 个独立的 `Linear(768, 64)`，`cat(dim=-1)` 拼回来 | **一个** `Linear(768, 768)`，forward 里 `view` 成 `[B, N, 12, 64]` 再 `transpose` 成 `[B, 12, N, 64]` |
| 2 | **头掩码** | 无 | `head_mask`（**bool** 类型，可以把某些头整体关掉） |
| 3 | **attention probs dropout** | 无 | `attention_probs_dropout_prob = 0.1`，作用在 `softmax` 之后 |
| 4 | **残差 + LayerNorm** | 无 | `BertSelfOutput` 里 `LayerNorm(x + attn_out)` |
| — | **参数量** | **2,362,368** | **2,362,368**（+ LayerNorm 1,536） |
| — | **缩放因子** | `√64 = 8` | `math.sqrt(64) = 8` ✅ 一致 |

**第 1 条最值得体会**：真 BERT 用一次 `Linear(768,768)` 完成 12 个头的投影，再靠 `view` + `transpose` 把结果掰成 12 个头——**因为两者参数量相等（§5.1 已经算过），所以数学上完全可以互换**。教学版用 12 个 ModuleList 只是**为了让"分头"看得见**；工业版用一次大矩阵乘是**为了 GPU 效率**（12 次小 matmul 不如 1 次大 matmul）。

**第 3 条的坑**：`attention_probs_dropout_prob=0.1` 只在 `model.train()` 下生效。`head_view` 分析时模型是 `eval` 状态（`from_pretrained` 默认 `eval`），所以 dropout 是关掉的。

**第 4 条是本篇的出口**：残差 + LayerNorm + FFN 就是 **Encoder Layer**，也就是 13 集说的第三块拼图所在的地方——下一集 `04_ffn_layer_norm_skip_conn.ipynb`。

---

## 九、常见误区

### ❌ 误区 1：`self.heads` 写成普通 Python list

**全篇最致命**。不会报错、loss 会降，但那 12 个头**根本没被训练**（§4.1）。判断方法：对参数量。

```python
# 正确写法下
sum(p.numel() for p in mha.parameters())    # 2,362,368
```

### ❌ 误区 2：`head_dim = embed_dim // num_heads` 不整除

```text
embed_dim = 768, num_heads = 10
→ head_dim = 768 // 10 = 76（整数除法，静默截断，不报错）
→ 10 个头拼起来: 10 × 76 = 760 ≠ 768
→ output_layer(x) 报错: mat1 and mat2 shapes cannot be multiplied (760x768)
```

**`768 / 12 = 64` 这个整除关系不是巧合，是 BERT 能跑起来的前提。** 如果你要改 `num_attention_heads`，必须保证 `hidden_size % num_attention_heads == 0`。

### ❌ 误区 3：把两个 12 混为一谈

```text
num_attention_heads = 12   ← 每层里"并排 12 个头"
num_hidden_layers   = 12   ← 整个模型"堆 12 层"
```

**它们都等于 12，但毫无关系。** `768 = 64 × 12` 里的那个 12 是**前者**。改错一个会得到形状对不上或参数暴增/暴减的模型。

### ❌ 误区 4：`self.heads[11](hidden_state)` 被 forward 了两次

```python
print(f'head(hidden_state): {self.heads[11](hidden_state).shape}')      # 第 1 次
x = torch.cat([head(hidden_state) for head in self.heads], dim=-1)      # 第 2 次（含 head 11）
```

在**没有 dropout** 的这篇里只是白算一遍；但如果头里带 dropout，这次多余的 forward 会**消耗随机数状态**，让后续结果和"不打印时"不一致。**调试语句别留在 forward 里**。

### ❌ 误区 5：从本篇的 MHA 输出里读语义

本篇 cell 51 的 `mha` 是 `MultiHeadAttention(config)` —— **随机初始化、零训练**。它的输出 `±0.2` 的数值没有任何语义。**能读出语义的是 §七的真 BERT。**

### ❌ 误区 6：忘了 `output_attentions=True`

```python
model = AutoModel.from_pretrained(model_ckpt)                        # ❌ 没有 attentions
model = AutoModel.from_pretrained(model_ckpt, output_attentions=True) # ✅
```

不加这个参数，`model(**inputs).attentions` 是 `None`——**注意力权重默认不返回**，因为存下来很占显存（13 层 × 12 头 × `N×N`）。

### ❌ 误区 7：以为 `heads=[8]` 是"第 8 个头"

bertviz 的头索引**从 0 开始**，所以 `heads=[8]` = **第 9 个头**。同理，13 集 `neuron_view(..., head=8)` 也是索引。

---

## 十、记忆卡

```text
╔══════════════════════════════════════════════════════════════════╗
║  多头注意力 · 一张卡                                              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  核心等式:   768 = 64 × 12                                       ║
║              hidden = head_dim × num_heads                       ║
║                                                                  ║
║  一个头 (AttentionHead):                                         ║
║      q = Wq(x)   [*, 768] → [*, 64]      Wq: Linear(768, 64)     ║
║      k = Wk(x)   [*, 768] → [*, 64]      Wk: Linear(768, 64)     ║
║      v = Wv(x)   [*, 768] → [*, 64]      Wv: Linear(768, 64)     ║
║      打分   s = q @ k.T / √64            √d_k = √64 = 8          ║
║      权重   a = softmax(s, dim=-1)       [*, 5, 5]  ← 与 64 无关  ║
║      输出   o = a @ v                    [*, 5, 64]              ║
║                                                                  ║
║  多头 (MultiHeadAttention):                                      ║
║      heads = nn.ModuleList([AttentionHead(768,64)] * 12)  ← 必须  ║
║      x = torch.cat([h(x) for h in heads], dim=-1)  [*, 768]      ║
║      x = self.output_layer(x)                       W_o: 768→768  ║
║                                                                  ║
║  参数量:  12 × 3 × (768×64+64)      = 1,771,776  (+ bias)        ║
║           1 ×   (768×768+768)       =   590,592  (W_o)           ║
║           合计                      = 2,362,368                  ║
║           ⚠️ 和"单头不分"完全相等 → 分头不增加参数                ║
║                                                                  ║
║  为什么必须分头:  一个 softmax = 一组归一化权重                   ║
║                   12 个 softmax = 12 种"相关度视角"               ║
║                                                                  ║
║  13 集 → 14 集 的因果:                                            ║
║     无投影 → ‖x‖² 主导 → softmax ≈ I → 注意力 = 恒等（什么都没做）║
║     加投影 → xᵀ(WqWkᵀ)x，迹期望 0 → 单位阵塌掉 → 真正在工作       ║
║                                                                  ║
║  三处工程差别:  ModuleList(必须) / head_mask(bool) / drop 0.1     ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 十一、自测 6 题

1. `AttentionHead(768, 64)` 里三个 `nn.Linear` 一共有多少参数（含 bias）？`MultiHeadAttention` 又一共多少？**和真 BERT 的注意力子层相比是多还是少？**
2. 一个头算出来的 `attn_weights` 形状是 `[1, 5, 64]` 还是 `[1, 5, 5]`？为什么？
3. 把 `self.heads` 从 `nn.ModuleList` 改成普通 list，会发生什么？**至少说出两个可观察的后果。**
4. 13 集的缩放因子是 `√768 ≈ 27.71`，本篇是 `√64 = 8`。为什么变小了？这个变化如何"救活"了注意力？
5. `head_view` 那里，为什么 `sentence_b_start` 等于 `7` 而不是 `6` 或 `5`？`token_type_ids` 长什么样？
6. `config` 里 `num_attention_heads = 12`、`num_hidden_layers = 12`。`768 = 64 × 12` 用的是哪一个？另一个 12 在哪里体现？

<details>
<summary>参考答案</summary>

1. 单头：`3 × (768×64 + 64) = 147,648`；12 头 × 147,648 = **1,771,776**。加 `output_layer` 的 `590,592` → **2,362,368**。真 BERT 的 `attention.self.{query,key,value}` 各是 `Linear(768,768)`，合计也是 1,771,776，加 `attention.output.dense` 590,592 = **2,362,368**——**一模一样**（BERT 额外有 `LayerNorm` 的 1,536）。
2. **`[1, 5, 5]`**。`attn_weights = softmax(Q @ Kᵀ / √d_k)`，其中 `Q @ Kᵀ` 是 `[1, 5, 64] @ [1, 64, 5] = [1, 5, 5]`——**形状只由 seq_len 决定，与 `head_dim` 无关**。`head_dim` 只影响"打分时用多少个维度去比"。
3. ① `model.parameters()` / `sum(numel)` 里**少掉 1,771,776**；② `.to(device)` **不会迁移这 12 个头**（会把 device 不一致的错误暴露或静默在 CPU 上算）；③ 优化器不更新它们 → 实际只在训练 `output_layer`。**`__init__` 和 `forward` 都不报错**，是典型的静默 bug。
4. 因为分头后每个头只在 **64 维**里算点积，`Q @ Kᵀ` 是 64 个乘积之和，方差随维度线性增长——所以缩放要跟着 `√d_k = √64 = 8` 一起变小，才能把 score 拉回 `O(1)`。不投影时 `d_k = 768`，对角线 `‖x‖² ≈ 768`，缩放后仍是 `√768 ≈ 27.7`，softmax 必然饱和成 one-hot（≈ 单位阵）。**投影后对角线不再是 `‖x‖²`（变成迹期望为 0 的二次型），和非对角线回到同一量级，softmax 才有分布。**
5. 因为 `[CLS] time flies like an arrow [SEP]` 共 **7** 个 token 属于句子 A（`token_type_ids` 前 7 位是 `0`），第 8 个（索引 7）才是 `fruit`。`token_type_ids = [0,0,0,0,0,0,0, 1,1,1,1,1,1]`，共 13 位；`sentence_b_start = (token_type_ids == 0).sum() = 7`。
6. 用 **`num_attention_heads = 12`**（每层里并排 12 个头，所以 `head_dim = 768 / 12 = 64`）。另一个 `num_hidden_layers = 12` 指的是**堆 12 层 Encoder**，和 `64` 没关系——它只决定"`MultiHeadAttention` 这个模块被实例化 12 次"。

</details>

---

## 十二、费曼三连问

**Q1：用一句话向同事解释 `AttentionHead` 和 `MultiHeadAttention` 的区别。**

> `AttentionHead` 是"一个视角"——把 768 维压到 64 维，在这 64 维里问一次"谁该关注谁"；`MultiHeadAttention` 是"12 个视角同时提问，再把 12 份答案拼起来用一个 `W_o` 融合"。代码上，前者是 3 个 `Linear(768,64)`，后者是 12 个前者 + 1 个 `Linear(768,768)`。

**Q2：如果我说"多头就是参数更多所以更强"，你怎么反驳？**

> 算一下就知道不是：`12 头 × 3 × (768×64+64) = 1,771,776`，而"单头但不分头"是 `3 × (768×768+768) = 1,771,776`——**完全相同**。多头换来的不是参数预算，而是**注意力的结构**：一个大 softmax 只能给出一组归一化权重，12 个 softmax 能同时给出 12 组，且每组只在自己那 64 维子空间里比较。**"同一个 `flies`，既能和 `time` 相关、又能和 `fruit` 相关"——这是单头做不到的。**

**Q3：13 集那个"softmax 变成单位矩阵"的实验，到底修好了没有？**

> **修好了，而且修的过程能一句话说清**：不投影时 `q·k` 的对角线是 `‖x‖² ≈ 768`（正比于维度），非对角线是两个独立向量的点积（期望 0）——这个"对角线碾压"就是单位阵的来源。一旦乘上 `Wq Wkᵀ`，对角线变成 `xᵀ(Wq Wkᵀ)x`，而这个矩阵的迹期望是 **0**，对角线和非对角线回到同一量级，softmax 给出真正的分布。**外加 `√64 = 8` 的缩放，score 从 `±27.7` 掉到 `±0.3`。**

---

## 十三、与前面笔记的连接

| 本篇概念 | 前面的哪一集 | 关系 |
|---|---|---|
| `scaled_dot_product_attention` | [13](./13_transformer_scaled_dot_product_self_attention.md) | 13 推公式，本篇**给它装上 `W_q/W_k/W_v` 并复制 12 份** |
| `Q = K = V = embedding` → softmax ≈ I | [13](./13_transformer_scaled_dot_product_self_attention.md) §六 | 本篇 §二**解释了这个退化的成因并给出修法** |
| `x'_i = Σ_j w_ji x_j` / 分块矩阵 | [08B](./08B_bert_multihead_block_matrix.md) | 08B 是**分块视角看真 BERT**，本篇是**从零写一遍** |
| `attentions` 的形状 `[1, 12, N, N]` | [07](./07_bert_model_outputs.md) | 07 看到的 `[1,12,22,22]`，本篇给出它的**来源**（12 个头 × `N×N`） |
| `neuron_view` 看单个头 | [13](./13_transformer_scaled_dot_product_self_attention.md) | 本篇的 `head_view` 是它的"**拉远版**" |
| `BertConfig` 的字段 | [13](./13_transformer_scaled_dot_product_self_attention.md) | 本篇首次真正**用** `hidden_size` / `num_attention_heads` |
| 残差 + LayerNorm + FFN | [09](./09_bert_add_norm_residual.md) | 本篇的 MHA 输出**还没有**残差和 LayerNorm → 下一集补上 |

### → 下一集

本篇把 13 集遗留的**三块拼图里的①②装上了**（可学习投影 + 分头/拼头/`W_o`）。剩下的是**③**：

- **残差连接**（`LayerNorm(x + attn(x))`）——让梯度能穿过 12 层；
- **LayerNorm**——把分布拉回标准正态；
- **FFN**（`768 → 3072 → 768`）——注意力的"非线性后处理"；
- **position encoding / mask**——本篇的 `nn.Embedding` 里**完全没有位置信息**，5 个词的顺序信息是丢掉的。

下一集（`04_ffn_layer_norm_skip_conn.ipynb`）把这四样补齐，`MultiHeadAttention` 就升级成完整的 **Encoder Layer**——也就是 13 集 §一里那张 `encoder layer` 结构图的最终形态。

### → 更远

第 16 集之后是 `sin_position_encoding.ipynb`、`05(06)_transformer_encoder(multi_task_learn).ipynb`、`07_gpt_decoder.ipynb`——从"能读"的编码器走到"能写"的解码器。
