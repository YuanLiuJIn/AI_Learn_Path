# 09 · Add & Norm：残差连接与残差模块（BertLayer 的骨架）

> **接 08 / 08B**：08 讲了一层里的"引擎"——多头注意力；本篇讲把引擎装进车里的"骨架"——**残差连接（Add）+ LayerNorm（Norm）**。没有这套骨架，12 层深的 BERT 根本训不动。
>
> **视频**：[动手写 BERT 系列] Bert 中的（add & norm）残差连接与残差模块（residual connections / residual blocks）`BV1VW4y1b79x`
> **配套 notebook**：`bilibili_vlogs/fine_tune/bert/tutorials/07_add_norm_residual_conn.ipynb`
> **本篇可独立验证的结论**：手算出来的 `layer.output(...)` 结果 **等于** `output[2][1]`（第 1 层的官方输出）。

**一句话主旨**：BERT 的每个子层都长成 `LayerNorm(x + Sublayer(x))`。`x + ...` 是**残差**（给梯度修一条高速公路、让子层只学"增量"），`LayerNorm(...)` 是**归一化**（把每层输出的分布按住，别让它越传越飘）。

---

## 一、BertLayer 的完整结构（含形状流）

08 只讲了 `attention.self`；一个完整的 `BertLayer` 其实是**两个残差块串联**：

```
                      ┌─────────────── 残差块 1 ───────────────┐
   x  [N,768] ────────┤                                        ├─→ attn_out [N,768]
        │             │  MHA + W_o  (08/08B 讲的引擎)          │
        │             │       ↓ dense → dropout                │
        └─────────────┤  Add ←────────────────────  ← 捷径 x   │
                      │       ↓ LayerNorm                      │
                      └────────────────────────────────────────┘
                      ┌─────────────── 残差块 2 ───────────────┐
  attn_out ───────────┤  FFN: 768 → 3072 → GELU → 768          ├─→ layer_out [N,768]
        │             │       ↓ dense → dropout                │
        └─────────────┤  Add ←──────────────────── ← 捷径      │
                      │       ↓ LayerNorm                      │
                      └────────────────────────────────────────┘
```

对应 HuggingFace 的模块（notebook 里 `print(model)` 能看到）：

| 模块 | 作用 | 是否含 Add & Norm |
|---|---|---|
| `attention.self` = `BertSelfAttention` | 多头注意力（Q/K/V → 打分 → 混合 → 拼头） | ❌ 纯引擎，不含 |
| `attention.output` = `BertSelfOutput` | `W_o` 投影 + **Add & Norm**（第 1 个） | ✅ |
| `intermediate` = `BertIntermediate` | `768 → 3072` + GELU | ❌ |
| `output` = `BertOutput` | `3072 → 768` + **Add & Norm**（第 2 个） | ✅ |

**12 层 × 2 个残差块 = 24 个残差块**，加上最外层还有个"隐形的"起点：`embeddings` 的输出（就是 07 说的 `hidden_states[0]`）。

> ⚠️ **形状约束（一个被忽略的设计理由）**：`x + F(x)` 要求两条支路形状**完全一致**。这就是为什么——
> - FFN 扩到 3072 之后**必须压回 768**；
> - `d_model = 768` 从 embedding 贯穿到最后一层，**永远不变**（07 说"13 个工位形状都一样"，根源就在这里）。

---

## 二、Add：残差连接

### 2.1 公式与直觉

```
y = x + F(x)
```

- `x`：这条子层**进来之前**的表示（捷径 / skip connection / identity）；
- `F(x)`：子层本身的变换（注意力 或 FFN）；
- `y`：加完的结果。

**关键视角的转变**：有了 `+x`，`F` 就不再是"从 x 直接算出答案"，而是**只学一个"修正量 / 增量"**：

```
F(x) = y - x    ← F 学的是"我要在 x 上改多少"
```

用数字感受一下（2 维）：

```
x        = [1.0,  2.0]
F(x)     = [0.1, -0.3]     ← 子层只输出一个很小的修正
y = x+F  = [1.1,  1.7]
```

模型不需要让 `F` 重新把 `x` 完整造一遍（那很难学），它只要说"第 1 维 +0.1、第 2 维 -0.3"就行了。**学"改多少"比学"是什么"简单得多。**

> 极端情况：如果这一层觉得"我没什么可贡献的"，只要 `F(x) → 0`，这一层就退化成**恒等映射** `y = x`，信息原封不动传过去——**至少不会变坏**。这叫"保底"。

### 2.2 为什么必须有它？（三个理由，一个比一个重要）

**① 给梯度修一条高速公路（最重要）**

反向传播时，链式法则要从第 12 层一路乘回第 1 层。

- **没有残差**：梯度 = 一堆 Jacobian 连乘 `∏ ∂F_i/∂x`。每一项都可能远小于 1，乘 12 次之后 → **梯度消失**，浅层根本学不到东西。
- **有残差**：每一层变成 `y = x + F(x)`，于是

```
∂y/∂x = I + ∂F/∂x
        ↑
     单位矩阵：无论 ∂F/∂x 多小，这一项恒为 1
```

连乘之后 `∏(I + J_i)` 展开里永远**含有一个 `I`**——即使所有 `∂F/∂x → 0`，梯度仍能无损地从第 12 层直达第 1 层。这就是"高速公路"三个字的字面意思。

**② 保底（恒等映射）**

初始化时 `F` 的输出接近 0（权重小），整个网络**初始等价于一个浅网络**，然后随训练逐步"长出"深度。这比一上来就硬啃 12 层稳定得多。

**③ 防止表示退化**

纯注意力是加权平均，连续做 12 次会让所有词的向量越来越像（理论上叫 **rank collapse / 表示坍缩**，多层 Softmax 混合会趋向低秩）。残差每步都把"原来的自己"加回来，保证了信息不会被反复稀释。

### 2.3 残差块（residual block）的标准定义

ResNet 提出的标准结构，BERT 原样沿用：

```
一个残差块 = 主路 F（一到多层变换） + 捷径 x（恒等，零参数） + 逐元素相加 + 归一化
```

BERT 的两个残差块：

| 块 | 主路 `F` | 捷径 `x` |
|---|---|---|
| 块 1 | 多头注意力 + `W_o` + dropout | 本层的输入 |
| 块 2 | FFN（`768→3072→GELU→768`）+ dropout | 块 1 的输出 |

**注意：捷径是零参数的**（不乘任何矩阵），所以残差几乎不增加参数量和计算量，却换来了可训练性的巨大提升——这是深度学习里性价比最高的设计之一。

---

## 三、Norm：LayerNorm

### 3.1 公式

对每个 token 自己的 768 维向量做标准化，然后学一个缩放和平移：

```
          x - mean(x)                    ← 减均值、除标准差：变成"均值 0、方差 1"
y = ────────────────────────  × γ + β
     sqrt( var(x) + eps )                ← γ、β 是可学习的 [768] 向量
```

- `mean / var`：**在这一个 token 的 768 个维度上**算（不是跨 batch、不是跨句子）；
- `eps = 1e-12`：防止方差为 0 时除以 0（BERT config 里 `layer_norm_eps: 1e-12`）；
- `γ / β`：可学习参数（`elementwise_affine=True`），各 768 个。归一化会把向量的"个性"抹掉一部分，`γ/β` 让模型**自己决定要不要恢复、恢复多少**。

### 3.2 手算一个 4 维例子

```
x = [1, 2, 3, 4]        mean = 2.5
var = ((-1.5)² + (-0.5)² + 0.5² + 1.5²) / 4 = 5/4 = 1.25        ← 注意是有偏方差（除以 N）
std = √1.25 ≈ 1.1180

y = [(1-2.5), (2-2.5), (3-2.5), (4-2.5)] / 1.1180
  = [-1.3416, -0.4472, 0.4472, 1.3416]        （取 γ=1, β=0）
```

验证一下：

```python
import torch
x  = torch.tensor([1., 2., 3., 4.])
ln = torch.nn.LayerNorm(4, eps=1e-12, elementwise_affine=False)   # γ=1, β=0
print(ln(x))            # tensor([-1.3416, -0.4472,  0.4472,  1.3416])

# 手写版对照
mean, var = x.mean(), x.var(unbiased=False)      # 有偏方差
print((x - mean) / torch.sqrt(var + 1e-12))      # 同上 ✓
```

### 3.3 为什么是 LayerNorm 而不是 BatchNorm？

| | BatchNorm | LayerNorm |
|---|---|---|
| 在**哪些元素**上算均值/方差 | 跨 **batch**（同一个特征维，所有样本） | 跨 **特征维**（同一个样本自己的 768 个数） |
| 依赖 batch 大小吗 | 强依赖，batch 小了统计不准 | 完全无关，**batch=1 也成立** |
| 变长序列（有 `<PAD>`） | 麻烦：PAD 会污染统计量 | 无影响，每个 token 独立算 |
| 训练/推理要两套统计量吗 | 要（推理用滑动平均） | 不要，训练推理**完全一致** |

NLP 里句子长度不齐、batch 常常很小（甚至推理时 batch=1），BatchNorm 的统计量会又脏又抖。**LayerNorm 天然适配 Transformer**，所以从 BERT 到现在所有 LLM 都用它。

### 3.4 它到底在解决什么问题？

**把每一层输出的数值分布"按回"均值 0、方差 1。** 没有它，12 层连乘下来激活值会漂移（有的维度爆炸、有的维度死掉），训练要非常小心地调学习率。有了它，每层输入分布都稳定 → 可以用更大的学习率 → 训练快得多、稳得多（这就是 BatchNorm 论文里 internal covariate shift 的动机，LayerNorm 同理）。

### 3.5 参数量（微不足道）

每个 LN：`γ` 和 `β` 各 768 → **1536** 个参数。

```
每层 2 个 LN          = 3,072
12 层                 = 36,864
+ embeddings 的 1 个   =  1,536
合计                   ≈ 38,400  ← 占 1.1 亿参数的 0.035%
```

**几乎不要钱，收益巨大。**

### 3.6 进阶：Post-LN vs Pre-LN（面试常问）

`Add & Norm` 的**顺序**有两种写法：

| 写法 | 公式 | 谁在用 |
|---|---|---|
| **Post-LN**（原始 Transformer / **BERT**） | `y = LN(x + F(x))` | BERT、原始 Transformer |
| **Pre-LN** | `y = x + F(LN(x))` | GPT-2 之后几乎所有现代 LLM（LLaMA 等用 RMSNorm 变体） |

区别：

- **Post-LN**：归一化在残差**之后**，每层输出分布非常规整；但梯度主干要**穿过 LN 的 Jacobian**，深层容易不稳定 → 训练必须做 **learning rate warmup**。
- **Pre-LN**：归一化在残差分支**内部**，从输入到输出有一条**完全不被 LN 阻挡的恒等路径** → 梯度更顺、训练更稳、warmup 需求小、更容易堆到几十上百层。

> 记住：**BERT 是 Post-LN**，以后读现代 LLM 源码看到 `x = x + attn(ln(x))` 别奇怪，那是 Pre-LN。

---

## 四、跟着 notebook 手算一遍（真模型）

notebook 用 `'this is a test sentence'` → 7 个 token（`[CLS] this is a test sentence [SEP]`），所以形状是 `[1, 7, 768]`。

### 4.1 拿官方输出当"标准答案"

```python
import torch
from transformers.models.bert import BertModel, BertTokenizer

model_name = 'bert-base-uncased'
tokenizer  = BertTokenizer.from_pretrained(model_name)
model      = BertModel.from_pretrained(model_name, output_hidden_states=True)

test_sent   = 'this is a test sentence'
model_input = tokenizer(test_sent, return_tensors='pt')

model.eval()
with torch.no_grad():
    output = model(**model_input)

embeddings = output[2][0]      # [1, 7, 768]  第 0 个工位：embedding 输出
layer1_out = output[2][1]      # [1, 7, 768]  第 1 个工位：第 0 层 BertLayer 的出口
```

### 4.2 手动拆开第 0 层

```python
layer = model.encoder.layer[0]

# ① 纯注意力引擎（08 讲的部分，形状 [1,7,768]，但注意：它不是这一层的出口！）
mha_output = layer.attention.self(embeddings)          # 返回 tuple，取 [0]

# ② 第 1 个 Add & Norm：LN( W_o(mha) + embeddings )
#                                              ↑ 捷径传的是「本层的输入」
attn_output = layer.attention.output(mha_output[0], embeddings)      # [1, 7, 768]

# ③ FFN：768 → 3072
mlp1 = layer.intermediate(attn_output)                 # [1, 7, 3072]

# ④ 第 2 个 Add & Norm：LN( 3072→768(mlp1) + attn_output )
#                                              ↑ 捷径传的是「块 1 的输出」
mlp2 = layer.output(mlp1, attn_output)                 # [1, 7, 768]
```

### 4.3 关键验证

```python
torch.allclose(mlp2, layer1_out, atol=1e-5)     # True ✅
```

**这一行是本集最重要的输出**：它证明"第 1 层的官方输出 = 两个残差块串联的结果"，也就是说——

> **`hidden_states[1]` 不是注意力的输出，而是 `LN(FFN(LN(MHA(x)+x)) + LN(MHA(x)+x))`。**

（对应 07 的 13 个工位：第 0 个是 embedding，第 k 个就是第 k-1 层 BertLayer 的出口。）

> 📌 **notebook 里有个小笔误**：第二个小标题写的是 "### 2.2 **第一次** add & norm，发生在 mlp 内部"，应该是**第二次**。看代码 `layer.output(mlp1, attn_output)` 就知道这是第 2 个残差块。

---

## 五、HuggingFace 源码（两个残差块的真身）

```python
class BertSelfOutput(nn.Module):          # 残差块 1 的 Add & Norm
    def __init__(self, config):
        self.dense     = nn.Linear(config.hidden_size, config.hidden_size)   # W_o [768,768]
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout   = nn.Dropout(config.hidden_dropout_prob)              # p=0.1

    def forward(self, hidden_states, input_tensor):
        hidden_states = self.dense(hidden_states)          # W_o 投影
        hidden_states = self.dropout(hidden_states)        # dropout
        hidden_states = self.LayerNorm(hidden_states + input_tensor)   # ★ Add & Norm
        return hidden_states


class BertOutput(nn.Module):              # 残差块 2 的 Add & Norm（结构一模一样）
    def __init__(self, config):
        self.dense     = nn.Linear(config.intermediate_size, config.hidden_size)  # [3072,768]
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout   = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states, input_tensor):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)   # ★ Add & Norm
        return hidden_states


class BertIntermediate(nn.Module):        # FFN 的上半段，没有 Add & Norm
    def __init__(self, config):
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)  # [768,3072]
        self.intermediate_act_fn = ACT2FN[config.hidden_act]                  # gelu

    def forward(self, hidden_states):
        return self.intermediate_act_fn(self.dense(hidden_states))
```

三点值得注意：

1. **`forward` 有两个入参**：`hidden_states`（主路）+ `input_tensor`（捷径）。这个签名就是残差连接的**接口证据**——08B 里那个"只有引擎"的 `BertSelfAttention.forward` 只有一个入参。
2. **顺序是 `dense → dropout → add → LN`**：dropout 在 add **之前**，只对主路生效（捷径不加噪声）。
3. **LN 在最后**：所以每层输出的 768 维都是"均值 0 方差 1 再经 γ/β 缩放"的（Post-LN 特征）。

---

## 六、常见疑问

**Q1：捷径和主路形状不一致怎么办？**
BERT 里永远一致（都是 768），直接相加。ResNet 里遇到通道数变化时，会在捷径上加一个 `1×1 卷积` 做投影（叫 projection shortcut）。Transformer 里没有这种情况——这正是 `d_model` 全程不变的理由。

**Q2：残差是不是让网络变"深"了但没变"强"？**
不是。有个著名的"unrolled view"（展开视角）：`n` 个残差块展开后相当于 `2^n` 条不同长度路径的**集成**（每条路径可以选择"走主路"或"走捷径"）。深度带来的表达力是真的，只是梯度被保护住了。

**Q3：为什么 `attention.self` 里没有 LayerNorm？**
`BertSelfAttention` 是纯引擎，只负责 Q/K/V → 打分 → 混合 → 拼头（08/08B 的内容）。Add & Norm 统一放在外面一层的 `BertSelfOutput` 里，这样"引擎"和"骨架"解耦，代码更干净。

**Q4：`γ / β` 能不能关掉？**
可以（`elementwise_affine=False`），但效果会变差。归一化强行把方差压成 1，会抹掉一些有用信息；`γ/β` 让模型自己学"哪些维度该放大、该平移多少"，是廉价且重要的自由度。

**Q5：LayerNorm 是对 768 维算，还是对 `[N,768]` 整块算？**
**对每个 token 独立算**自己的 768 维。`normalized_shape=(768,)` 的意思是"最后 1 维内部求统计量"，前面的 `[batch, seq_len]` 维各自独立。所以 PAD token 的统计量**不会污染**真实 token（这是 LayerNorm 相对 BatchNorm 的关键优势）。

**Q6：BERT 用的是 Post-LN，那 warmup 是什么？**
训练初期先用很小的学习率"热机"几千步再升上去。Post-LN 的梯度主干要穿过 LN，深层初期容易不稳，warmup 就是为了躲开这段危险期。改用 Pre-LN 后，warmup 的需求就小很多了。

---

## 七、记忆卡

| 问题 | 答案 |
|---|---|
| Add & Norm 的公式 | `y = LayerNorm(x + Sublayer(x))`，BERT 每个子层一套 |
| 一个 BertLayer 有几个残差块 | **2 个**（注意力后、FFN 后），12 层共 24 个 |
| 残差为什么能训动深层 | `∂y/∂x = I + ∂F/∂x`，连乘后恒含单位阵 → 梯度高速公路 |
| 残差让 F 学什么 | 学**增量 / 修正量**，不是"重新造一遍 x"；`F→0` 时退化为恒等（保底） |
| 捷径有参数吗 | **没有**，零参数零成本 |
| LayerNorm 在哪一维算 | 每个 token 自己的 **768 维**（跨特征，不跨 batch） |
| 为什么不用 BatchNorm | NLP 变长 + PAD + batch 小；LN 与 batch 无关、训练推理一致 |
| `eps=1e-12` 干嘛 | 防止方差为 0 时除零 |
| `γ/β` | 可学习的缩放/平移，每个 LN `2×768` 参数 |
| 残差的形状约束 | 两路必须同形 → 这就是 FFN 要压回 768、`d_model` 全程不变的原因 |
| BERT 是 Post-LN 还是 Pre-LN | **Post-LN** `LN(x+F(x))`；现代 LLM 多为 Pre-LN `x+F(LN(x))` |
| 怎么验证手算对了 | `torch.allclose(layer.output(mlp1, attn_output), output[2][1])` → True |

**一句话**：**残差负责"让梯度回得来、让增量学得动"，LayerNorm 负责"让数值不漂移"；两者加起来，才把 08 那个引擎安全地叠成 12 层。**

---

## 八、自测（合上文档先答）

1. 一个 BertLayer 里有几次 Add & Norm？分别发生在哪两个模块里？
2. 写出 `∂y/∂x`（`y = x + F(x)`），并说明为什么这一项能让梯度穿过 12 层。
3. 残差块让子层 `F` 学的是"答案"还是"增量"？为什么说 `F → 0` 时是"保底"？
4. `x = [1,2,3,4]` 过 LayerNorm（γ=1, β=0）结果是多少？均值和方差分别是几？
5. 为什么 Transformer 用 LayerNorm 而不是 BatchNorm？说两点。
6. 为什么 FFN 扩到 3072 之后**必须**压回 768？
7. BERT 是 Post-LN 还是 Pre-LN？换成另一种写法，公式长什么样？
8. notebook 里 `layer.attention.output(mha_output[0], embeddings)` 为什么要传第二个参数？

<details>
<summary>参考答案</summary>

1. **2 次**：`attention.output`（BertSelfOutput，注意力之后）和 `output`（BertOutput，FFN 之后）。
2. `∂y/∂x = I + ∂F/∂x`。即使所有 `∂F/∂x → 0`，连乘 `∏(I + J_i)` 展开后仍含一个 `I`，梯度可以无损从第 12 层直达第 1 层，不会消失。
3. 学**增量**（`F(x) = y - x`）。`F → 0` 时 `y = x`，该层退化为恒等映射，信息原样通过、至少不变坏。
4. `mean = 2.5`，`var = 1.25`（有偏，除以 N=4），`std ≈ 1.1180`；结果 `[-1.3416, -0.4472, 0.4472, 1.3416]`。
5. ① 句子变长且有 PAD，BatchNorm 的跨 batch 统计量会被污染；② NLP batch 常很小甚至推理时 batch=1，BN 统计不准，而 LN 与 batch 完全无关；③ BN 训练/推理要两套统计量，LN 一致。
6. 因为残差相加要求捷径（768）与主路输出同形，所以 FFN 必须压回 768——这也是 `d_model` 贯穿始终的原因。
7. **Post-LN**：`y = LN(x + F(x))`。Pre-LN 是 `y = x + F(LN(x))`（GPT-2 之后主流）。
8. 第二个参数是**捷径**（残差连接的 `x`），即本层的输入 `embeddings`；模块内部会算 `LN(dense(mha) + embeddings)`。
</details>

---

## 九、费曼三连问

1. **一句话**：Add & Norm = 每个子层都先在主路上算一个"修正量"，加回原始输入（`Add`），再把结果归一化（`Norm`）。
2. **手推**：一个 2 层无残差网络 `y = F2(F1(x))` 与有残差网络 `y = x + F2(x + F1(x))`，分别写出 `∂y/∂x`，指出后者展开后哪一项保证了梯度不消失。
3. **讲出去**：给一个只懂 BatchNorm 的人解释，为什么 NLP 必须用 LayerNorm——重点说清"统计量的方向"（跨 batch vs 跨特征）和"变长序列 + PAD + batch=1"这三个场景。

---

## 十、连接

- **接 08 / 08B**：08 讲了引擎（多头注意力），08B 讲了它的分块矩阵实现；本篇讲引擎装进 BertLayer 的两套骨架。08 第五节"从单头回到完整的一层"就是本篇的预告。
- **接 07**：`hidden_states` 的 13 个工位，每个工位 = 本篇一整个 BertLayer 的出口；07 说"形状永远 `[1,22,768]`"，本篇解释了**为什么必须不变**（残差相加的形状约束）。
- **接 03**：`LayerNorm` 用的 mean/std 就是 03 提过的 mean/std；本篇补上了"归一化之后还有可学习的 γ/β"。
- **→ 10**：08~09 讲的都是 BERT 的"**身体**"（encoder 内部）；[10_bert_pooler_output_and_head.md](./10_bert_pooler_output_and_head.md) 转向"**接口**"——`pooler_output` 与 `BertForXxx` 各种任务头（head）。
- **位置编码**留到番外（合集第 24 集 Positional Embedding）。
- **延伸**：`bilibili_vlogs/learn_torch/basics/add_norm.py` 是本篇的最小可运行骨架（加载模型 + 前向，可在此基础上加第四节的拆解代码）。

---

*09 完。动手跑的路径：notebook `07_add_norm_residual_conn.ipynb`，重点盯最后那格 `torch.allclose(mlp2, output[2][1])`。*
