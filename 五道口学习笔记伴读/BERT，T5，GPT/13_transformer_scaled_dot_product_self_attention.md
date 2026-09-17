# 13 · Transformer 架构：scaled dot-product self-attention（QKV）

> **接 12**：12 把预训练 backbone 拿去微调，跑通了完整的 `Trainer` 流程。但一直没停下问一句：**backbone 内部那些"注意力"到底在算什么？** 本篇回头补这块地基。
>
> **视频**：`BV14s4y127kk`（合集第 14 集）
> **本期 code**：`github.com/chunhuizhang/bert_t5_gpt/blob/main/tutorials/02_transformer_architecture_self_attention.ipynb`
> **本地**：`bert_t5_gpt/tutorials/02_transformer_architecture_self_attention.ipynb`（**41 个 cell**，纯代码、几乎无预存输出，**每个 cell 都该亲手跑**）
> **系列视频**：`space.bilibili.com/59807853/channel/collectiondetail?sid=496538`
>
> **一句话主旨**：self-attention 就是 **"每个词按相关度，从整句话里取信息来更新自己"**。公式只有三行——`Q·Kᵀ / √d_k` → `softmax` → `·V`；而本集最有价值的**不是公式，是那个"softmax 变成单位矩阵"的实验结果**（下文 §六）。
>
> **与 08 / 08B 的区别**：08/08B 是**打开 BERT 看内部**——切出已训练好的 `W_q/W_k/W_v`、验证 12 头分块矩阵；本篇是**从零推导**——先假装 `W_q = W_k = W_v = I`（直接拿 embedding 当 Q/K/V），把**公式本身**推一遍，并暴露一个 08 没讲的"坑"。两篇配合看最完整。

---

## 〇、30 秒直觉

一句话：**self-attention = 让每个词，按"相关度"从整句话里取信息，重新描述自己。**

它解决的问题是：`bank` 在 "river bank" 和 "bank account" 里应该是**不同的向量**，但 embedding 查表只能给同一个——**上下文信息得靠注意力注入**。

notebook 用两个经典例子说明了这件事（§二详解）：

| 词 | 语境 A | 语境 B |
|---|---|---|
| `apple` | keynote / phone / Jobs → **公司** | banana / food / fruit → **水果** |
| `flies` | time **flies** like an arrow → 飞（动词） | fruit **flies** like a banana → 苍蝇（名词） |

注意第二组就是本集 `sample_text = 'time flies like an arrow'` 的出处——**同样一个 `flies`，在两句里是完全不同的东西**。

三步动机（notebook cell 16 的原文骨架）：

| 步骤 | 做什么 | 数学 |
|---|---|---|
| ① 打分 | 每个词问问"你和我多相关" | `scores = Q · Kᵀ` |
| ② 归一 | 把分数变成"配方百分比" | `÷ √d_k` 后 `softmax` |
| ③ 混合 | 按配方把各词的值掺起来 | `output = weights · V` |

---

## 一、notebook 全景（41 个 cell，四段）

| 段 | cell | 内容 |
|---|---|---|
| **A. 架构综述** | 0–8 | 三种架构（encoder-only / decoder-only / encoder-decoder）、encoder layer 结构、contextual embedding |
| **B. 公式** | 9–16 | self-attention 定义 `x'_i = Σ w_ji x_j`、scaled dot-product 四步 |
| **C. 可视化** | 17–25 | `bertviz` 交互式看注意力 + Q/K/V 的"逛超市"比喻 |
| **D. 手算** | 26–40 | `nn.Embedding` → Q/K/V → 打分 → softmax → 混合，并**封装成函数**验证一致 |

**关键**：D 段是本集的"肉"——**41 个 cell 里有 15 个是纯代码计算**，而 A/B/C 三段只是铺垫。

---

## 二、三种架构：先站对位置

notebook cell 3 与 cell 6 把 Transformer 家族分成了**三支**。这不是名词背诵，而是**决定"每个 token 能看到谁"**的问题：

| 架构 | 每个 token 能看到 | 代表模型 | 典型任务 | notebook 的比喻 |
|---|---|---|---|---|
| **encoder-only** | **左右都看**（bidirectional） | BERT、RoBERTa、DistilBERT | 文本分类、NER、MLM | **完形填空** |
| **decoder-only** | **只看左边**（causal / autoregressive） | GPT | 语言生成 | **词语接龙** |
| **encoder-decoder** | encoder 全看；decoder 看左边 + encoder | T5、BART | 翻译、摘要 | **看图说话 / 翻译** |

> **`seq2seq` 是"任务形状"，不是"架构"**。notebook cell 3 的原话：`seq of tokens (input) => seq of tokens (output)`——**输入一个序列、输出另一个序列**（如机器翻译）。它通常由 encoder-decoder 实现，但**不是必须**（decoder-only 的 GPT 也能做翻译）。

三条线的分解（notebook cell 3 逐字）：

```text
encoder :  seq of tokens  →  seq of embedding vectors (hidden state / context)
decoder :  encoder 的 hidden state  →  seq of tokens
              └─ 迭代生成：一次一个 token，直到 EOS 或到达 max length
```

**decoder 的"一次一个 token"就是它和 encoder 最本质的差别**——encoder 一遍算完（并行），decoder 必须**串行**（第 `t` 个 token 依赖第 `t-1` 个的输出）。这也是为什么 GPT 类模型推理慢：**它的计算量随生成长度线性增长，且无法并行**。

### 2.1 encoder layer 里到底有什么（cell 8）

```text
输入：seq of embeddings
  ↓
① multi-head self attention      ← 本集主题
  ↓
② FFN (fc)                       ← 768 → 3072 → 768
  ↓
输出：same shape as input        ← 形状不变，这是能堆叠 12 层的前提
```

两个重点：

1. **形状进出完全相同**（`[B, N, 768] → [B, N, 768]`）。所以 encoder layer 可以**无限堆叠**——12 层、24 层、100 层都合法。
2. **输出叫 `contextualized embeddings`（上下文化表示）**——cell 8 的原话是 "encoding the **contextual** information"。**这就是注意力的产出物**：同样一个 token，在不同句子里的输出向量**不再相同**。

> **Skip connection & LayerNorm 也在这里出场**（cell 8 最后一行）：notebook 只说了一句"高效训练深度神经网络的技巧"，展开在 [09](./09_bert_add_norm_residual.md)——那是让 12 层能训得动的原因。

---

## 三、公式先行：`x'_i = Σ w_ji x_j`

notebook cell 12 把定义写得非常干净，我逐项拆开：

```math
x'_i = \sum_{j=1}^{n} w_{ji}\, x_j
```

| 符号 | 含义 | 形状 |
|---|---|---|
| `x_1 ... x_n` | 输入：n 个 token 的 embedding | 每个 `[768]` |
| `x'_1 ... x'_n` | 输出：n 个**更新后**的 embedding | 每个 `[768]` |
| `w_ji` | **attention weight**——第 `i` 个词从第 `j` 个词取信息的比例 | 标量 |
| `W` | 所有权重组成一个矩阵 | `[n, n]`（**方阵**） |

三个必须记住的性质（notebook 原话）：

1. **`x'_i` 是整句 embedding 的"加权平均"**——cell 12 原话："不是 fixed embeddings，而是 **weighted average of each embedding of the whole input sequence**"。
2. **`Σ_j w_ji = 1`**——对**每一列** `i` 求和为 1（这就是 `softmax(dim=-1)` 的职责）。
3. **`W ∈ R^{n×n}`**——**行数和列数都等于序列长度**。所以序列变长，注意力矩阵是**平方级增长**（这正是长文本贵的原因，见 §十 误区 4）。

> **下标约定要特别小心**：`w_ji` 的第一个下标 `j` 是"被取信息的词"（source），第二个 `i` 是"要更新的词"（target）。写成矩阵 `W[j, i]` 后，**第 `i` 列**（固定 `i`、遍历所有 `j`）就是"`i` 该看谁"。而 `Σ_j w_ji = 1` 正是对**第一个下标**求和——所以 `softmax(dim=-1)` 作用在分数张量 `scores[i, j]` 的 **`j`（最后一个）维度**上，与 `Σ_j` 是同一件事。**下标写反是这一节最常见的笔误。**

---

## 四、scaled dot-product：四步，一步不多

notebook cell 16 把整个流程写成四条，我把每条的"输入 → 输出形状"一起补上（`B`=batch，`N`=序列长度，`d_k`=每个头的维度）：

### 第 ① 步：投影出 Q、K、V

```text
Project each token embedding into three vectors called query, key, and value.
```

`W_q, W_k, W_v` 是**可学习参数**（learnable parameters）。

```text
x: [B, N, 768]  ──W_q──▶  Q: [B, N, 768]
                ──W_k──▶  K: [B, N, 768]
                ──W_v──▶  V: [B, N, 768]
```

> **本集的重要简化**：notebook **没有**真的做这一步——cell 35 直接写了 `query = key = value = input_embeddings`，并注释 "W_q, W_k, W_v: nn.Linear，作用在 token_embedding 得到……"。**先把这个"没投影"的版本算通，下一篇再把 W 加上去**。这个简化正是 §六 那个"意外结果"的来源。

### 第 ② 步：打分

```text
dot-product(query, key) => attention scores
```

```text
scores = Q · Kᵀ   →   [B, N, N]
```

cell 16 原话强调："a sequence with `n` input tokens there is a corresponding **`R^{n×n}`** matrix of attention scores"——**方阵，每行是"我要看谁"的分数**。

### 第 ③ 步：缩放 + 归一

cell 16 给的**理由**（比公式重要）：

> "Dot products 的结果**可能是任意大的数**，会让整个训练过程非常不稳定。"

所以两步：

```text
scores / √d_k    →   softmax(dim=-1)   →   weights: [B, N, N]，Σ_j w_ji = 1
```

HuggingFace 的写法（cell 35/39）：

```python
attn_scores = torch.bmm(query, key.transpose(1, 2)) / np.sqrt(dim_k)   # ① 先缩放
attn_weights = F.softmax(attn_scores, dim=-1)                          # ② 再 softmax
```

> **顺序不能换**：先 `softmax` 再缩放，归一化就白做了（`softmax` 之后的数不再和为 1 的补集关系）。

### 第 ④ 步：混合

```text
attn_outputs = weights · V   →   [B, N, N] @ [B, N, 768] = [B, N, 768]
```

cell 38 的注释一句话点破形状：`# 5*5, 5*768 => 5*768`。

**注意这里的 `v_j` 而不是 `x_j`**——cell 16 写的是：

```math
x'_i = \sum_{j=1}^{n} w_{ji}\, v_j
```

**对比 §三 的 `Σ w_ji x_j`**：形式完全一样，只是 `x_j` 换成了 `v_j`。**这就是 Q/K/V 的分工**——`Q·K` 只负责**算出 `w`**，而真正被混合的是 `V`。

> **一句话总结 Q/K/V**：`Q`/`K` 是**用来算权重的**（考完就扔），`V` 是**真正被加权求和的内容**。

---

## 五、逐 cell 手算：从 5 个 token 到 `[1, 5, 768]`

这一章把 notebook cell 27–38 **一行一行对照**。整个流程只有 6 行有效代码，但每行都值得停下来看一眼形状。

### 5.1 准备输入（cell 27–29）

```python
tokenizer.model_input_names           # cell 27：模型认哪些字段（12 集讲过）
sample_text = 'time flies like an arrow'
model_inputs = tokenizer(sample_text, return_tensors='pt', add_special_tokens=False)
```

```text
{'input_ids':      tensor([[ 2051, 10029, 2066, 2019, 8612]]),
 'token_type_ids': tensor([[0, 0, 0, 0, 0]]),
 'attention_mask': tensor([[1, 1, 1, 1, 1]])}
```

**两个细节**：

- **`add_special_tokens=False`**——不加 `[CLS]`/`[SEP]`。notebook 那行 `# [CLS][SEP]` 注释就是在提醒这一点。**为什么必须关掉？** 因为要 5 个 token **一一对应 5 个单词**，注意力矩阵 `5×5` 才能和"time / flies / like / an / arrow"对上。若加上特殊 token 变成 7 个，人肉读矩阵时就多两行两列干扰。
- **`'pt'`**（PyTorch tensors）——后面立刻要喂给 `nn.Embedding`，所以要 tensor 不要 python list。

### 5.2 造一张 embedding 查表（cell 31–32）

```python
config = AutoConfig.from_pretrained(model_ckpt)                        # cell 31
token_embedding = nn.Embedding(config.vocab_size, config.hidden_size)  # cell 32
```

> **⚠️ 这是全篇最容易看漏的一行**：`nn.Embedding(...)` 是**现场新建的随机初始化查表**——它和 `bert-base-uncased` 训练好的词向量**没有任何关系**。cell 32 的注释 "lookup-table, learnable" 就是这个意思。
> **这个"随机"不是疏漏，而是本实验能成立的前提**——§六会说明它推出了什么。

### 5.3 三次前向，形状一路长出来（cell 33–35）

```python
print(model_inputs['input_ids'].shape)      # torch.Size([1, 5])
input_embeddings = token_embedding(model_inputs['input_ids'])
input_embeddings.shape                      # torch.Size([1, 5, 768])
```

| 步骤 | 形状 | 含义 |
|---|---|---|
| `input_ids` | `[1, 5]` | batch=1，5 个 token id |
| `input_embeddings` | `[1, 5, 768]` | 每个 id → 一个 768 维向量（= `hidden_size`） |

然后 cell 35 **一次性完成"造 Q/K/V + 打分 + 缩放"**：

```python
# 暂时先不考虑 position encoding
# W_q, W_k, W_v: nn.Linear，作用在 token_embedding 得到
query = key = value = input_embeddings          # ← 关键简化：不做投影
dim_k = key.size(-1)                            # 768
attn_scores = torch.bmm(query, key.transpose(1, 2)) / np.sqrt(dim_k)
```

三个动作：

1. **`query = key = value = input_embeddings`**——**没有 `W_q/W_k/W_v`**。先把"投影"这一层拿掉，只留下注意力的骨架。
2. **`key.transpose(1, 2)`**：`[1, 5, 768] → [1, 768, 5]`，把**序列维换到最后**，这样才能 `bmm` 出 `[1, 5, 5]`。
3. **`torch.bmm`**（batch matrix multiply）：对 batch 里每一条独立做矩阵乘，正好匹配 `[1, 5, 768] @ [1, 768, 5] = [1, 5, 5]`。

> **只 `transpose` 后两个维度**（`(1, 2)`），**不动 batch 维**——这是 `bmm` 的要求：两个输入必须是 `[B, n, m]` 和 `[B, m, p]`。写完 `bmm` 后矩阵每行是"我这个词对整个句子的原始分数"。

真实输出：

```text
dim_k:  768
attn_scores.shape:  torch.Size([1, 5, 5])

tensor([[[27.9989,  0.5235, -1.9310, -1.9866,  0.2585],
         [ 0.5235, 29.1748, -0.1630,  0.7868, -1.4294],
         [-1.9310, -0.1630, 27.0096, -0.8972, -0.1020],
         [-1.9866,  0.7868, -0.8972, 28.9856,  0.7115],
         [ 0.2585, -1.4294, -0.1020,  0.7115, 27.4751]]])
```

**先别急着往下走，这张矩阵有两个必须看见的事实：**

| 位置 | 数值 | 含义 |
|---|---|---|
| **对角线** | `27.99 / 29.17 / 27.01 / 28.99 / 27.48` | **每个词跟自己**的分数——**极大，且几乎全相等** |
| **非对角** | 都在 `±2` 以内 | 词与词之间——**小，且正负都有** |
| **对称性** | `scores[0,1] == scores[1,0] == 0.5235` | 因为 `Q == K`，所以 `Q·Kᵀ` **必然对称** |

### 5.4 softmax：结果出乎意料（cell 36–37）

```python
attn_weights = F.softmax(attn_scores, dim=-1)
attn_weights.sum(axis=-1)     # tensor([[1., 1., 1., 1., 1.]])
```

```text
tensor([[[1.0000e+00, 1.1683e-12, 1.0037e-13, 9.4935e-14, 8.9637e-13],
         [3.6049e-13, 1.0000e+00, 1.8145e-13, 4.6910e-13, 5.1142e-14],
         [2.6995e-13, 1.5816e-12, 1.0000e+00, 7.5900e-13, 1.6811e-12],
         [3.5395e-14, 5.6682e-13, 1.0522e-13, 1.0000e+00, 5.2567e-13],
         [1.5135e-12, 2.7987e-13, 1.0554e-12, 2.3807e-12, 1.0000e+00]]])
```

**注意力矩阵变成了单位矩阵**——`1.0` 只出现在对角线上，非对角全是 `1e-12` 量级（**真正的 0**）。

### 5.5 混合：`x'_i ≈ v_i`（cell 38）

```python
attn_outputs = torch.bmm(attn_weights, value)     # [1,5,5] @ [1,5,768] = [1,5,768]
```

```text
tensor([[[-1.3950,  0.5791, -1.0480,  ..., -0.6396,  0.1464,  0.3892],
         ...]])
```

形状 `[1, 5, 768]` 回来了——**进出形状完全一致**（§二 说过的"形状不变"）。但因为权重是单位矩阵，**输出第 `i` 行 ≈ 输入第 `i` 行的 `value`**：

```python
torch.allclose(attn_outputs, value)     # ✅ True（数值上）
```

> **也就是说：这一次注意力运算，什么都没做。** `x'_i == x_i`。**这个"什么都没做"的结论，正是本集最值得花 5 分钟的地方。**

---

## 六、为什么 softmax 会变成单位矩阵？（本集最值钱的 30 秒）

上面这一幕**不是 bug、不是笔误，是数学上的必然**。三行推完：

### 6.1 对角线为什么是 `≈ √d_k`

`Q == K == X` 时，对角线元素是**自己和自己点积**：

```math
s_{ii} = \frac{x_i \cdot x_i}{\sqrt{d_k}} = \frac{\lVert x_i \rVert^2}{\sqrt{d_k}}
```

而 `nn.Embedding` 初始化后，每个分量近似 `N(0, 1)`，所以

```math
\lVert x_i \rVert^2 = \sum_{j=1}^{d_k} x_{ij}^2 \;\approx\; d_k
\;\;\Longrightarrow\;\;
s_{ii} \;\approx\; \frac{d_k}{\sqrt{d_k}} \;=\; \sqrt{d_k}
```

**`√768 ≈ 27.71`——和实测的 `27.99 / 29.17 / 27.01 / 28.99 / 27.48` 完全吻合。**

### 6.2 非对角线为什么只有 `±1` 左右

两个**相互独立**的随机向量点积：

```math
x_i \cdot x_j \sim \mathcal{N}(0,\; d_k)
\quad\Longrightarrow\quad
\mathrm{std}\left(\frac{x_i \cdot x_j}{\sqrt{d_k}}\right) \approx \mathcal{O}(1)
```

所以非对角是 `±2` 以内的正态小量——**这也正是"除以 `√d_k`"想达到的效果**（让随机配对的分数落进 `N(0,1)` 这种"好数值区间"，softmax 不会饱和）。

### 6.3 两条合起来：`√d_k : 1` 的悬殊

```text
对角线  ≈ 27.7
非对角  ≈ ±1
```

`softmax` 面对 `[27.7, 0.5, -1.9, -2.0, 0.3]`：`exp(27.7) / exp(0.5) ≈ e^{27.2} ≈ 6.5 × 10^{11}`。**对角线独吞全部概率**，其余位置变成 `1e-12`。

> **所以：`÷ √d_k` 这个缩放，救得了"非对角"，救不了"对角"。**
> 因为 `x·x = ‖x‖²` 本来就是 `d_k` 量级，除以 `√d_k` 后还是 `√d_k`——**它随维度单调增长，维度越高越独裁**。

### 6.4 这个实验教了我们什么

| 结论 | 说明 |
|---|---|
| **① `÷ √d_k` 的作用是"让随机分数回到 `O(1)`"** | 这正是 notebook cell 35 那句注释的意思："avoid the **saturate of softmax**: grad => zero" |
| **② 但"自己和自己"的点积天然最大** | `x·x` 恒为正且是 `‖x‖²`，任何别的词都比不过 |
| **③ 所以"不做投影的注意力"≡ 恒等变换** | 每个词只会看自己 → 上下文什么都没注入 → **等于白算** |
| **④ 这是引入 `W_q / W_k / W_v` 的真正动机** | 通过**可学习**的投影，把 `x` 打散到三个**不同的**子空间，让"自己和自己"不再天然最强——**这才让注意力真的开始"选信息"** |

> **一句话**：`query = key = value = input_embeddings` 这个简化，**恰恰证明了投影不可省**。它不是"简化版注意力"，而是"退化成恒等的注意力"。下一篇（`W_q/W_k/W_v` 到位）才是真正能工作的 self-attention。

这也是为什么 §七 的 `bertviz` 必须**先用真模型**看——真模型有训练好的 `W_q/W_k/W_v`，注意力矩阵既不近单位阵、也不对称，**各头各有分工**。

---

## 七、`bertviz`：把注意力"看"出来（cell 17–25）

数值矩阵 5 行 5 列还能人肉读，到了 `[12, 22, 22]` 就没法读了。notebook 用 `bertviz` 把它变成**可交互的连线图**：

```python
from bertviz.transformers_neuron_view import BertModel
from bertviz.neuron_view import show

model_ckpt = 'bert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = BertModel.from_pretrained(model_ckpt)

sample_text = 'time flies like an arrow'
show(model, model_type="bert", tokenizer=tokenizer, sentence_a=sample_text,
     display_mode="light", layer=0, head=8)
```

四个参数各有讲究：

| 参数 | 值 | 说明 |
|---|---|---|
| `model_type` | `"bert"` | 告诉 bertviz 按 BERT 的结构去钩取注意力 |
| `sentence_a` | 单个句子 | **只传一句 = self-attention**（传 `sentence_b` 就变成 cross-attention，即 encoder-decoder 那支） |
| `display_mode` | `"light"` | 浅色背景（截图/投屏友好） |
| `layer` / `head` | `0` / `8` | **只看第 0 层的第 8 号头**——BERT 有 12×12=144 个头，一次只能看一个 |

**读图方式**（`neuron_view` 的经典布局）：

- 左右两列是**同一句 token**（左 = query 侧，右 = key 侧）；
- **连线的粗细 / 颜色深浅 = 注意力权重**；
- 点某个 token，就能看到它"看谁最多"。

> **为什么是 `layer=0, head=8`？** 没有特殊理由——**这就是"随手挑一个"，然后来回切换 layer/head 观察不同头的分工**（有的头盯语法、有的盯相邻词、有的盯 `[SEP]`）。这正是"多头"的意义：**不同的头学不同的关系**（08B 从矩阵分块角度讲过这件事）。

### 7.1 Q / K / V 的"逛超市"比喻（cell 25）

notebook 换了一个比图书馆更生活化的比喻——**做一顿晚餐**：

| Q/K/V | 晚餐场景 |
|---|---|
| **query** | 你**想做的那顿晚餐**（我的需求） |
| **key** | 超市**货架上的标签**（每个货架"能提供什么"） |
| **匹配** | 拿"晚餐需求"去和"货架标签"比 → 找到最合适的货架与层 |
| **value** | **从命中货架取出的食材**（真正拿到手的东西） |

和 08 的图书馆比喻是一回事（`Q`=心里的问题、`K`=索书标签、`V`=正文）。notebook 还点明这叫 **information retrieval systems**（信息检索系统）——**注意力本质是一次"软"的检索**：不是命中一个货架，而是**所有货架都按匹配度加权取一点**。

---

## 八、`BertConfig`：768 / 12 / 3072 是哪来的（cell 31–32）

print 出来的 config 里，真正和注意力相关的只有 5 个字段：

```text
"hidden_size": 768,               ← 每个 token 的向量维度
"num_attention_heads": 12,        ← 12 个头
"num_hidden_layers": 12,          ← 12 层 encoder
"intermediate_size": 3072,        ← FFN 中间层 = 4 × 768
"max_position_embeddings": 512,   ← 最长 512 个 token
```

**`768 = 64 × 12`**——cell 32 的注释写得很直白。这个等式是理解多头的钥匙：

```text
768 维的 Q/K/V
   │  按通道切成 12 份
   ▼
每头 64 维（d_k = 64）
```

> **注意区分两个 `d_k`**：08 里 `÷ √64`（**每头** 64 维），本篇 `÷ √768`（**没分头**，`d_k = hidden_size`）。**本篇算的是"单头 = 全维度"的退化版本**，所以 `dim_k` 是 768。分头是下一步的事。

其他几个字段（面试常问）：

| 字段 | 值 | 一句话 |
|---|---|---|
| `vocab_size` | 30522 | WordPiece 词表（06 讲过） |
| `type_vocab_size` | 2 | `token_type_ids` 的取值范围（02 讲过） |
| `hidden_act` | `"gelu"` | FFN 激活函数 |
| `layer_norm_eps` | `1e-12` | LayerNorm 数值稳定项 |
| `position_embedding_type` | `"absolute"` | 绝对位置编码（可学习查表） |
| `use_cache` | `true` | 推理时缓存 K/V（**生成式模型的加速开关**，GPT 那支更重要） |
| `architectures` | `["BertForMaskedLM"]` | **hub 上 config 里的原始标注**，不代表你这次加载的就是 MLM 模型 |

> **最后一行是个小坑**：`architectures` 是**发布者在 `config.json` 里写的字符串**，它**不会**因为你 `AutoModel.from_pretrained()`（拿裸 backbone）而改变。**别用它判断"我加载的是哪个类"**——看类名。

---

## 九、封装成函数（cell 39–40）

最后两行把整个流程收成一个函数：

```python
def scaled_dot_product_attention(query, key, value):
    dim_k = key.size(-1)                                     # hidden_size
    attn_scores = torch.bmm(query, key.transpose(1, 2)) / np.sqrt(dim_k)
    attn_weights = F.softmax(attn_scores, dim=-1)
    return torch.bmm(attn_weights, value)
```

```python
scaled_dot_product_attention(query, key, value)
```

**这两行是"验收测试"**——函数返回的结果和 §5.5 手写三步的 `attn_outputs` **逐位相同**：

```python
torch.allclose(scaled_dot_product_attention(query, key, value), attn_outputs)   # ✅
```

**为什么这个函数长这样值得背下来**：

1. **它和 `torch.nn.functional.scaled_dot_product_attention` 同名同思路**——PyTorch 2.x 内置了这个算子（内部会调用 FlashAttention 之类的加速内核）。**手写这一版的意义是：知道里面在算什么。**
2. **`dim_k = key.size(-1)` 而不是 `query.size(-1)`**——因为缩放因子由 **K 的维度**决定（分数是 `Q·Kᵀ`）。两者在标准注意力里通常相同，但写 `key` 更严谨。
3. **`np.sqrt` 和 `torch.sqrt` 都行**——`dim_k` 是 python `int`，`np.sqrt` 返回 `numpy.float64`，和 tensor 相除会自动 broadcast。**不是 bug**。

> **还差什么才算"完整的一层注意力"？** 三样：① `W_q/W_k/W_v` 投影；② **分头 + 拼头 + `W_o`**；③ **padding mask**（`-10000`，softmax 前）。①在下一篇，②见 [08B](./08B_bert_multihead_block_matrix.md)，③见 [08 §5.1](./08_bert_encoder_self_attention.md)。

---

## 十、常见误区（9 个）

1. **误区：`query = key = value = input_embeddings` 就是 self-attention。**
   不是。它**退化成恒等变换**（§六）——每个词只看自己，上下文没注入。它是"注意力公式"的最小骨架，**不是能工作的注意力**。
2. **误区：`d_k` 就是 64。**
   本篇 `dim_k = 768`——因为**没有分头**，`d_k = hidden_size`。`64 = 768 / 12` 是**分头之后**每头拿到的维度（08 / 08B 讲的才是那个）。
3. **误区：除以 `√d_k` 只是为了"防止数值溢出"。**
   更准确的说法是**防止 softmax 饱和 → 梯度消失**（cell 35 注释原文：`avoid the saturate of softmax: grad => zero`）。数值稳定只是副产品。
4. **误区：注意力矩阵是 `n×n`，所以长文本只是"线性"变贵。**
   是**平方级**——`scores` 本身就是 `n×n` 个元素（`n=4096` 时单头就有 1600 万个 float），**还要完整存下来做 softmax**。这才是长上下文的真正瓶颈。
5. **误区：`attn_weights` 是"每一列"和为 1。**
   `softmax(dim=-1)` 归一化的是**最后一个维度**，对 `[B, N, N]` 来说就是**每一行**和为 1。notebook cell 37 的 `attn_weights.sum(axis=-1) → tensor([[1., 1., 1., 1., 1.]])` 就是直接证据。
6. **误区：`Q·Kᵀ` 一定是对称矩阵。**
   只有本例 `Q == K` 才对称。真实 BERT 里 `W_q ≠ W_k`，**注意力矩阵一般不对称**——"A 看 B"和"B 看 A"本来就不该等强。
7. **误区：`bertviz.show` 会展示所有头。**
   一次只能给一个 `layer` + 一个 `head`。要看别的头，得改参数重画。
8. **误区：`config.architectures` 告诉你"加载了什么类"。**
   它只是 hub 上 `config.json` 里的一段字符串。用 `AutoModel.from_pretrained()` 拿裸 backbone 时，它**依然是** `["BertForMaskedLM"]`——**判断类看类名，不看这个字段**。
9. **误区：`add_special_tokens=False` 是手滑漏写。**
   是**故意的**：为了让 5 个 token 精确对应 5 个单词，`5×5` 的注意力矩阵才能和"time / flies / like / an / arrow" 逐格对上。**生产代码里不会这么写。**

---

## 十一、记忆卡

- **三种架构看"能看到谁"**：encoder-only（左+右，BERT）/ decoder-only（只看左，GPT）/ encoder-decoder（T5、BART）
- **`seq2seq` 是任务形状，不是架构**；decoder 必须**串行生成**，直到 `EOS` 或 `max_length`
- **公式**：`x'_i = Σ_j w_ji x_j`，`w ∈ R^{n×n}`，`Σ_j w_ji = 1`
- **scaled dot-product 四步**：投影 Q/K/V → `Q·Kᵀ` 打分 → `÷√d_k` + `softmax` → `·V` 混合
- **Q/K 用来算权重（用完即弃），V 才是被混合的内容**：`x'_i = Σ_j w_ji v_j`
- **`÷√d_k` 的职责**：让随机配对的分数回到 `O(1)`，**避免 softmax 饱和、梯度为 0**
- **`bmm` 的三要素**：`key.transpose(1,2)` 只换后两维、不动 batch、形状 `[B,N,d]@[B,d,N]=[B,N,N]`
- **本集最重要的一课**：`Q=K=V=X` 时对角线 `≈ √d_k`、非对角 `≈ O(1)` → `softmax` ≈ **单位矩阵** → **注意力 ≡ 恒等变换**
- **所以 `W_q/W_k/W_v` 不是可选项**：它是把自相似性打散、让注意力真正"选信息"的唯一手段
- **`config` 五件套**：`hidden_size=768`、`num_attention_heads=12`、`num_hidden_layers=12`、`intermediate_size=3072`、`max_position_embeddings=512`；且 **`768 = 64 × 12`**
- **`scaled_dot_product_attention(q, k, v)`** 和 PyTorch 2.x 的内置同名算子一个思路

---

## 十二、自测（先答再看）

1. `time flies like an arrow` 有 5 个词，notebook 里 `input_ids.shape` 是 `[1, 5]` 而不是 `[1, 7]`。为什么？
2. cell 35 里 `attn_scores` 的对角线是 `27.99 / 29.17 / 27.01 / 28.99 / 27.48`，为什么**恰好都接近 `√768 ≈ 27.71`**？用一行公式解释。
3. 承上，既然 `÷√d_k` 是为了"数值稳定"，为什么这个例子里 softmax 还是变成了单位矩阵？缩放到底没能救哪个部分？
4. `attn_weights.sum(axis=-1)` 输出 `tensor([[1., 1., 1., 1., 1.]])`。若把 `F.softmax(..., dim=-1)` 改成 `dim=-2`，这个结果会变成什么？语义上还叫"注意力权重"吗？
5. notebook 里 `attn_scores` 是**对称**的（`scores[0,1] == scores[1,0]`）。真实 BERT 的注意力矩阵对称吗？为什么？
6. `dim_k = key.size(-1)` 为什么写 `key` 而不是 `query`？（两者在本例都是 768）
7. 想把本集的代码变成"真正能工作的单头注意力"，**最少**还要加哪两样东西？（一样是权重，一样和 batch 里长度不齐有关）

<details>
<summary>参考答案</summary>

1. 因为 cell 29 传了 **`add_special_tokens=False`**，所以没有加 `[CLS]`/`[SEP]`，5 个单词就是 5 个 token。（notebook 那行 `# [CLS][SEP]` 注释就是提醒。）目的是让 `5×5` 注意力矩阵与 5 个单词一一对应，方便人肉读。
2. 因为 `Q == K == X`，对角线是**自点积** `s_ii = (x_i·x_i)/√d_k = ‖x_i‖²/√d_k`。而 `nn.Embedding` 随机初始化后各分量近似 `N(0,1)`，`‖x_i‖² ≈ d_k = 768`，故 `s_ii ≈ 768/√768 = √768 ≈ 27.71`。
3. `÷√d_k` 只把**随机配对**（非对角）的分数压回 `O(1)`；**对角线**是 `‖x‖²`，本来就是 `d_k` 量级，除以 `√d_k` 后仍是 `√d_k`——**缩放对"自相似"无效**。于是 `[27.7, ~0.5, ~-2, ...]` 的 softmax 被对角线独吞，变成单位矩阵。
4. 会变成**每一列**和为 1。语义上**不再**是"每个 query 对全句的注意力分布"了——`dim=-1`（每个 query 对所有 key 归一）才是注意力的定义；`dim=-2` 变成"每个 key 被所有 query 归一"，是另一种（非注意力的）归一化。
5. **不对称**。对称只在 `Q == K`（本例）时成立。真实 BERT 有各自独立的 `W_q`、`W_k`，所以 `q_i·k_j ≠ q_j·k_i`——"i 看 j"和"j 看 i"强度不同，这是必需的（否则注意力没有方向性）。
6. 因为缩放因子由**分数 `Q·Kᵀ` 的内积维度**决定，而内积是在 `K` 的最后一维（`d_k`）上做的。两者在标准多头注意力里相等，但写 `key` 语义更准确（`query`、`value` 的最后一维可以不同）。
7. ① **`W_q / W_k / W_v` 三个可学习投影**（否则退化成§六的恒等）；② **padding mask**（把 `attention_mask == 0` 的位置在 softmax 前置 `-10000`，否则短句的 padding 会参与平均）。②在 [08 §5.1](./08_bert_encoder_self_attention.md)。

</details>

---

## 十三、费曼三连问

1. **一句话**：self-attention 就是"每个词拿自己的 `query` 去和全句的 `key` 比对出权重，再按权重把所有词的 `value` 加权平均，得到自己的新表示"。
2. **说形状**：`B=2, N=5, d=768` 时，写出 `Q/K/V`、`attn_scores`、`attn_weights`、`attn_outputs` 的形状；并说明 `softmax(dim=-1)` 之后哪一个维度上和为 1。
3. **讲出去**：向一个只听过"注意力很厉害"的人解释——**为什么"不做投影的注意力"等于什么都没做**（用 `‖x‖² ≈ d_k` 和 `√d_k : 1` 这个悬殊比），以及 `W_q/W_k/W_v` 是怎么救场的。

---

## 十四、与前面笔记的连接

- **接 08 / 08B**：08 是**打开真 BERT 看**（切出 `W_q/W_k/W_v`、`÷√64`、12 头分块）；本篇是**从零推**（`W_q=W_k=W_v=I`、`÷√768`、单头）。两篇对照，正好看出"有投影 vs 无投影"的差别——**08 的注意力矩阵不近单位阵，本篇的是**。
- **接 07**：07 展示过 `attentions` 的形状 `[1, 12, 22, 22]`——那个 `22×22` 就是本篇 `5×5` 的放大版（层数 × 头数堆叠），**本篇算的是里面**一格**的来历。
- **接 03**：`hidden_size=768 / 12 heads / 3072 FFN / 12 layers` 的全景在 03 建过；本篇把 `768 = 64 × 12` 这个"为什么能分头"的等式讲透了。
- **接 12**：12 是"**用**预训练模型微调"（把注意力当黑盒），本篇是"**拆**注意力的公式"——**先会用、再懂原理**，顺序反过来也成立。
- **接 02 / 06**：`tokenizer.model_input_names`、`add_special_tokens`、`input_ids` 的数字（`2051=time`、`10029=flies`）都在 02/06 的 tokenizer 章节铺过。
- **→ 下一集**：`scaled dot-product self-attention` 只差**三块拼图**就完整了——① `W_q/W_k/W_v` 可学习投影；② **分头 / 拼头 / `W_o`**；③ **position encoding + mask**。下一集（`multi-head attention / transformer block`）会把它们全部装上，把这个"退化成恒等的注意力"变成 **BERT 内部真正的 12 头注意力**。

---

*13 完。跟着跑一遍 notebook：**重点盯 §五 的 `query = key = value = input_embeddings` 那一行（以及它导致的单位矩阵）、§六 的 `√d_k : 1` 推导、§八 的 `768 = 64 × 12`**——这三处想通，"注意力"就从"一个名词"变成"一行可以手算的公式"了。*
