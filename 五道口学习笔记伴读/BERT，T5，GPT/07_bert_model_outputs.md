# 07 · 解析 BertModel 的 output：last_hidden_state / pooler_output / hidden_states / attentions

> 接 03（架构）、04（`eval` + `no_grad`）、05（BertEmbeddings）、06（WordPiece）。
>
> 本篇回答两个问题：
> 1. `BertModel` 的 forward 四步链（Embeddings → Encoder ×12 → Pooler）**每一步到底在干嘛**；
> 2. 返回的 `last_hidden_state` / `pooler_output` / `hidden_states` / `attentions` **分别是什么、什么形状、用在哪**。
>
> 参考：
> - 本地 notebook：`bilibili_vlogs/fine_tune/bert/tutorials/05_model_outputs.ipynb`
> - 教程链接：`https://github.com/chunhuizhang/bilibili_vlogs/blob/master/fine_tune/bert/tutorials/05_model_outputs.ipynb`
> - 官方文档：`https://huggingface.co/docs/transformers/model_doc/bert#transformers.BertModel`

---

## 〇、全局直觉：BERT 是一条"信息加工流水线"

先建立一个贯穿全篇的直觉。进去的是 22 个整数 ID，出来的东西分几份：

```text
输入：22 个整数 ID                        shape [1, 22]
  ↓
【第1步 BertEmbeddings】每个整数 → 768 维向量    shape [1, 22, 768]
  ↓
【第2步 BertEncoder × 12】22 个词互相"看"12 遍    shape [1, 22, 768]（形状不变）
  ↓
【第3步 BertPooler】把整句压成 1 个向量          shape [1, 768]
  ↓
输出（在不同位置"抽头"得到）
```

**核心一句话**：形状从 `[1,22]`（22个ID）→ `[1,22,768]`（22个向量）→ 抽出 `[1,768]`（1个句子向量）。

**最关键的认知**：

> **四个输出不是四次独立计算，而是同一条流水线上不同位置的"抽头"。**
> - `hidden_states` = 完整录像（13 帧）
> - `last_hidden_state` = 最后一帧
> - `pooler_output` = 最后一帧里抽一格再加工
> - `attentions` = 每层加工时"谁看了谁"的记录表

---

## 一、先把例子跑起来

### 1.1 加载与推理

```python
import torch
from transformers import BertModel, BertTokenizer

model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name, output_hidden_states=True)
```

注意 `output_hidden_states=True`——这是**能不能拿到 `hidden_states` 的开关**。

### 1.2 经典例句（三个 "bank"）

```python
text = ("After stealing money from the bank vault, the bank robber was seen "
        "fishing on the Mississippi river bank.")
```

分词后：

```text
input_ids: [101, 2044, 11065, 2769, 2013, 1996, 2924, 11632, 1010,
            1996, 2924, 27307, 2001, 2464, 5645, 2006, 1996,
            5900, 2314, 2924, 1012, 102]
shape: [1, 22]        # batch_size=1, seq_len=22
```

- `101` = `[CLS]`，`102` = `[SEP]`
- `2924` 出现了 **3 次**：第 6 位「bank(金库)」、第 10 位「bank(劫匪)」、第 19 位「bank(河岸)」

> **这个例句的用意**：同一个词、三个不同词义。最后要看到——**三个位置最终得到三个不同的向量**。

### 1.3 推理（接 04 的标配组合）

```python
model.eval()
with torch.no_grad():
    outputs = model(**token_input)
```

- `eval()`：关闭 Dropout 随机性
- `no_grad()`：不建计算图，省显存

notebook 中 `len(outputs) == 3`（因为开了 `output_hidden_states`）。

---

## 二、四步链逐步详解

notebook 注释：

```166:167:bilibili_vlogs/fine_tune/bert/tutorials/05_model_outputs.ipynb
- forward
    - embedding => encoder => pooler
```

---

### 第 1 步 · BertEmbeddings：整数 → 向量

**要解决的问题**：计算机不认识整数 ID `2924`，只认识数值向量。

**它干的事**（05 学过）：给 22 个位置各造一个 768 维向量，塞进三种信息：

```text
第 i 个位置的向量 = word_embeddings[ input_ids[i] ]
                 + position_embeddings[ i ]
                 + token_type_embeddings[ token_type_ids[i] ]
然后 LayerNorm + Dropout
```

**形状变化**：

```text
输入：[1, 22]          （22 个整数）
输出：[1, 22, 768]     （22 个向量，每个 768 维）
```

**★ 关键状态**：这 22 个向量此刻**还是"孤立"的**。

第 6 位的 bank(金库)、第 10 位的 bank(劫匪)、第 19 位的 bank(河岸)——**三个向量此刻几乎一样**（都是 ID 2924 的词向量 + 各自位置向量 + 句子0向量，只有位置不同）。

> 这就是问题：**同一个词、三个意思，向量却几乎没区别**。下一步就是来解决这个。

---

### 第 2 步 · BertEncoder（12 层）：互相"看"，吸收上下文

**它干的事**：让 22 个词**互相看、互相交流，然后根据邻居更新自己**，**连续做 12 轮**。

这就是 Self-Attention（自注意力）。每一轮：

```text
每个词问自己："我跟谁关系最密切？"
  → 给其他 21 个词打分（attention 权重）
  → 按分数把别人的信息"加权平均"到自己身上
  → 更新自己的 768 维向量
```

**形状变化（重要！）**：

```text
输入：[1, 22, 768]
输出：[1, 22, 768]      ← 形状完全不变！
```

**为什么形状不变？** 因为它是"**原地更新**"：22 个词还是 22 个词，每个词还是 768 维，**只是向量里的数值变了**——吸收了上下文。

**回到 bank 的例子**：

```text
第 1 轮后：
  bank(第6位)  看到 "vault(金库)"、"money"      → 向量往"金融机构"方向偏
  bank(第10位) 看到 "robber(劫匪)"、"stealing"   → 向量往"抢劫目标"方向偏
  bank(第19位) 看到 "river(河)"、"fishing"       → 向量往"河岸"方向偏

第 2 轮：基于第 1 轮的结果再看一遍，理解更深
...
第 12 轮：三个 bank 的向量已经明显不同
```

> **这就是 BERT 的核心价值**：同一个词在不同语境得到不同向量（**上下文相关表示**）。这是 Word2Vec 那种"一个词永远一个向量"做不到的。

**12 层的含义**：不是 12 个不同模型，是**同一套操作重复 12 次**（每层有自己的参数）。

| 层 | 大致学到什么 |
|---|---|
| 低层（1-4） | 句法：词性、短语结构 |
| 中层（5-8） | 语义：词义消歧、实体 |
| 高层（9-12） | 任务相关：情感、逻辑、推理 |

---

### 第 3 步 · BertPooler：22 个向量 → 1 个句子向量

**要解决的问题**：Encoder 出来是 **22 个**向量，但**句子级任务**（"这句话是夸还是骂"）只需要 **1 个**向量。

**它干的事**：从 22 个向量里**挑出第 0 个（就是 `[CLS]`）**，再做个小变换：

```python
pooler_output = Tanh(Linear(last_hidden_state[:, 0, :]))
```

**切片怎么读（重点）**：

```python
last_hidden_state              # shape [1, 22, 768]
last_hidden_state[:, 0, :]     # → [1, 768]
#               ↑  ↑  ↑
#               │  │  └─── : 保留全部 768 个维度
#               │  └────── 0 : 取第 0 个 token，就是 [CLS]
#               └───────── : : 取全部 batch
```

**为什么用 `[CLS]`？**

`[CLS]` 是不属于原句任何词的一个特殊位置。经过 12 层 Self-Attention，**所有词的信息都可以往它身上汇聚**，它就成了"整句话的摘要"。

**`Linear + Tanh` 是干嘛的？**

- `Linear(768→768)`：一个可学习的线性变换
- `Tanh`：把数值压到 `(-1, 1)` 区间

**⚠️ 实践提醒（重要）**：

官方文说明，这个 `Linear` 的权重是**在预训练的 NSP（Next Sentence Prediction）任务上训出来的**。而 NSP 后来被证明效果有限（RoBERTa 已去掉），因此：

> **`pooler_output` 在很多下游任务中，不一定比直接用 `last_hidden_state[:, 0, :]`（跳过 Linear+Tanh）或对所有位置做 mean pooling 更好。**
> `BertForSequenceClassification` 传统上接 `pooler_output`，但很多现代实现改用 `[CLS]` 原始向量或平均池化。

---

### 第 4 步 · 输出：从流水线上"抽头"

四个输出是**同一条流水线的不同取样点**：

```
input_ids [1,22]
   │
   ├─ embedding 输出 ────────────────────────► hidden_states[0]
   │       [1,22,768]
   │
   ├─ 第1层 encoder 输出 ─────────────────────► hidden_states[1]
   │       [1,22,768]
   │
   ├─ 第2层 ... ──────────────────────────────► hidden_states[2]
   │
   │   ...（中间层）
   │
   ├─ 第12层 encoder 输出 ─────────────────────► hidden_states[12]
   │       [1,22,768]                            = outputs[0] last_hidden_state ★
   │                                                    │
   │                                                    │ 抽第0个位置 + Linear+Tanh
   │                                                    ▼
   │                                            outputs[1] pooler_output [1,768]
```

---

## 三、三个输出逐个解析

因为开了 `output_hidden_states=True`，本例 `len(outputs) == 3`。

### 3.1 `outputs[0]`：`last_hidden_state`

- **shape**：`(batch_size, sequence_length, hidden_size)` = **`[1, 22, 768]`**
- **含义**：**第 12 层（最后一层）输出后，每一个 token 的向量**

```text
位置 0  [CLS]      → vec[0]     (768 维)
位置 1  After      → vec[1]
位置 2  stealing   → vec[2]
...
位置 6  bank(金库)  → vec[6]     ★
...
位置 10 bank(劫匪)  → vec[10]    ★
...
位置 19 bank(河岸)  → vec[19]    ★
位置 21 [SEP]      → vec[21]
```

**★ 关键**：第 6、10、19 号位置输入的 ID **完全相同**（都是 2924），但经过 12 层 Self-Attention 后，**三个位置的向量已经不同**——各自吸收了不同上下文。

**用在哪**：**token 级任务**——NER（命名实体识别）、序列标注、QA 起止位置预测、抽取式任务。

---

### 3.2 `outputs[1]`：`pooler_output`

- **shape**：`(batch_size, hidden_size)` = **`[1, 768]`**
- **含义**：取最后一层的 `[CLS]` 位置向量，再过 `Linear(768→768) + Tanh`

```python
pooler_output = Tanh(Linear(last_hidden_state[:, 0, :]))
```

| | `last_hidden_state[:, 0, :]` | `pooler_output` |
|---|---|---|
| 是什么 | `[CLS]` 最后一层原始输出 | `[CLS]` 再过 `Linear + Tanh` |
| shape | `[1, 768]` | `[1, 768]` |
| 训练来源 | 通用编码器 | NSP 目标专门训过 |
| 典型用途 | 分类（很多现代做法直接用它） | 句子级表示（传统 BERT 分类头输入） |

**用在哪**：**句子级任务**——文本分类、句对匹配、语义相似度（注意上面 ⚠️ 的提醒）。

---

### 3.3 `outputs[2]`：`hidden_states`（需开关）

```python
type(outputs[2]), len(outputs[2])
# (tuple, 13)
```

- **shape**：**13 个** `[1, 22, 768]` 组成的 tuple
- **为什么是 13**：`1`（embedding 层输出）+ `12`（12 层 encoder 各层输出）

notebook 打印：

```text
0  torch.Size([1, 22, 768])    ← embedding 输出（05 的 BertInput）
1  torch.Size([1, 22, 768])    ← 第 1 层 encoder 输出
2  torch.Size([1, 22, 768])    ← 第 2 层
...
12 torch.Size([1, 22, 768])    ← 第 12 层（= last_hidden_state）
```

**开关**：只有 `output_hidden_states=True`（或 `config.output_hidden_states=True`）才返回；**不开则 `len(outputs) == 2`**。

**为什么需要 13 份？** 因为不同层学到的东西不同：

| 层 | 信息类型 | 适合任务 |
|---|---|---|
| 第 0 项（embedding） | 纯词义，无上下文 | — |
| 第 1-4 层 | 句法信息 | 句法分析、词性标注 |
| 第 5-8 层 | 语义信息 | 词义消歧、实体识别 |
| 第 9-12 层 | 任务相关信息 | 分类、情感 |

**典型用法 1：层融合**（把最后几层加权/求和，常比只用最后一层好）

```python
# 取最后 4 层，求和
sum_last_4 = sum(outputs[2][-4:])    # 4 个 [1,22,768] 相加
```

**典型用法 2：可解释性分析**——研究"BERT 哪一层学会了什么"，是 NLP 可解释性的经典方法。

---

## 四、三个恒等式（notebook 的核心验证）

notebook 用 `==` 比较验证了三件事。**它们本质上都在证明：这些输出是同一条流水线上的东西，不是独立算出来的。**

### 恒等式 1：`last_hidden_state == hidden_states[-1]`

```python
outputs[0] == outputs[2][-1]
# tensor([[[True, True, True, ..., True, ...]]])     全 True
```

**含义**：`hidden_states` 的第 12 项（最后一项）**就是** `last_hidden_state`。

> 不是"算了两遍得到相同结果"，而是**同一份数据的两个引用**。
> 就像流水线上第 12 个工位的产品，你既叫它"最终产品"，也可以叫它"第 12 个快照"——**同一个东西**。

### 恒等式 2：`hidden_states[0] == BertEmbeddings 的输出`

```python
outputs[2][0] == model.embeddings(
    token_input['input_ids'], token_input['token_type_ids']
)
# 全 True
```

**含义**：`hidden_states` 的第 0 项**不是第 1 层**，而是**还没进 encoder 的 embedding 结果**。

**这把 05 和 07 直接串起来了**：

```text
hidden_states[0]   =  BertInput（05 的 Dropout(LayerNorm(E))）
hidden_states[12]  =  last_hidden_state
```

### 恒等式 3：`pooler_output == model.pooler(last_hidden_state)`

```python
outputs[1] == model.pooler(outputs[2][-1])
```

**含义**：`pooler` 是一个**独立可调用的小模块**，输入 `last_hidden_state`，只取 `[CLS]` 再 Linear+Tanh。

---

## 五、第四个输出：`attentions`（notebook 未开，但很重要）

**一句话区分**：

- `hidden_states` = 每层加工**后的产品**（向量）
- `attentions` = 每层加工**时的配料表**（"谁看了谁、看得多重"）

| 字段 | shape | 开关 |
|---|---|---|
| `attentions` | `(batch_size, num_heads, seq_len, seq_len)` = `[1, 12, 22, 22]` | `output_attentions=True` |

**shape 怎么读**：

```text
attentions[i]  shape: [1, 12, 22, 22]
                ↑    ↑   ↑    ↑
                │    │   │    └─── 被看的词（22 个）
                │    │   └──────── 正在看的词（22 个）
                │    └──────────── 第几个注意力头（12 个）
                └───────────────── batch
```

**怎么读一个具体值**：

```python
attentions[0][0, 3, 6, 19]
# 第 0 层、第 3 个注意力头、"bank(第6位)" 看向 "bank(第19位)" 的权重
```

- 取值范围 `0~1`，是 **softmax 之后**的权重
- 每一行（某个词看向所有词）和为 1
- 权重高 = "我看你比较多"

**用途**：可视化——画热力图看模型在关注什么。例如检查代词 "it" 是否正确指向了它指代的名词。

**同时开两个开关**：

```python
model = BertModel.from_pretrained(
    model_name,
    output_hidden_states=True,
    output_attentions=True,
)
outputs = model(**token_input)
# last_hidden_state, pooler_output, hidden_states, attentions → 4 项
```

---

## 六、总览表

| 输出 | shape（本例） | 需要开关 | 含义 | 典型用途 |
|---|---|---|---|---|
| `last_hidden_state` | `[1, 22, 768]` | 默认有 | 最后一层每个 token 的向量 | token 级：NER、QA、序列标注 |
| `pooler_output` | `[1, 768]` | 默认有 | `[CLS]` 过 Linear+Tanh（NSP 训出） | 句子级：分类、句对（注意提醒） |
| `hidden_states` | 13 × `[1, 22, 768]` | `output_hidden_states=True` | embedding + 12 层各自输出 | 层融合、可解释性分析 |
| `attentions` | 12 × `[1, 12, 22, 22]` | `output_attentions=True` | 各头 attention softmax 权重 | 注意力可视化 |

本例参数：`batch_size=1, seq_len=22, hidden_size=768, num_layers=12, num_heads=12`。

---

## 七、与前面笔记的连接

1. **接 05**：`hidden_states[0]` 就是 05 的 `BertInput = Dropout(LayerNorm(E))`——恒等式 2 实证。
2. **接 03**：`pooler` 是 03 架构图 `embeddings → encoder → pooler` 的最后一环；它是 **BERT 自带模块，不是分类头**（分类头是额外的 `Linear(768→2)`）。
3. **接 04**：`model.eval()` + `with torch.no_grad()` 正是 04 讲的推理标配组合。
4. **接 06**：三个 "bank" 的输入 ID 完全相同（都是 2924），但输出向量不同——这就是 06 说的「上下文相关表示」，也是 BERT 相对静态词向量的突破。
5. **接 01**：`[CLS]` 的向量被 pooler 拿出来做句子级表示，对应 01 情感分析的输出来源。

---

## 八、一句话总收

> **BertModel 的四个输出不是四次独立计算，而是同一条流水线上的不同"抽头"：**
> - `hidden_states` = 完整录像（13 帧：embedding + 12 层）
> - `last_hidden_state` = 最后一帧（22 个词的最终向量，token 级任务用）
> - `pooler_output` = 最后一帧抽 `[CLS]` 再 Linear+Tanh（1 个句子向量，句子级任务用，但因 NSP 训练而不一定最优）
> - `attentions` = 每层"谁看了谁"的权重表（可视化用）
>
> **四步链的精髓**：Embeddings 把整数变向量（孤立、无上下文）→ Encoder ×12 让词互相看 12 遍（形状不变，但数值吸收了上下文，同一个词的不同副本从此分道扬镳）→ Pooler 抽 `[CLS]` 压成句子向量。
