# 07 · 解析 BertModel 的 output：last_hidden_state / pooler_output / hidden_states / attentions

> 接 03（架构）、04（`eval` + `no_grad`）、05（BertEmbeddings）、06（WordPiece）。
> 本篇回答两个问题：
> - 这些 output 分别是什么、什么 shape？
> - 它们之间是什么关系？（核心认知：同一流水线、不同抽头）
> 参考：本地 `bilibili_vlogs/fine_tune/bert/tutorials/05_model_outputs.ipynb`

---

## 〇、全局直觉：BERT 是一条"信息加工流水线"

**30 秒直觉（先记住三件事，再看细节）**：

1. **一条流水线**：ID 进 → 向量 → 12 轮加工 → 抽句子向量。
2. **四个输出 = 四个抽头**，不是四次计算。
3. **bank 三兄弟**：同一个 ID 2924，出流水线后变成三个不同的向量——这就是 BERT 的意义。

流水线全貌（ASCII 版）：

```
输入 input_ids [1,22]（22 个整数）
   │
   ▼
第1步  BertEmbeddings（整数 → 向量）
   │    [1,22,768]
   ▼
第2步  BertEncoder × 12（词互相"看" 12 遍）
   │    [1,22,768]（形状不变）
   ▼
第3步  BertPooler（抽 [CLS] + Linear + Tanh）
        [1,768]
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

### 1.3 开头那个 `1`：一次喂了几句话（batch size）

`[1, 22]`、`[1, 22, 768]` 前面都有个 `1`——它叫 **batch size（批次）**：**一次喂了几句话**。shape 的每一维都对应一个"标签"，从左往右读：

```text
[ 1 ,  22  ,  768 ]
  ↑     ↑      ↑
 几句   每句    每个词用
 话    几个词  几个数字描述
```

- `22` = 这句话被切成了 22 个 token
- `768` = 每个 token 用一个 768 维向量表示
- 最前面的 `1` = **这次只处理了 1 句话**

**为什么明明只有一句话还要写个 `1`？** PyTorch 模型天生按"批量"设计——训练时一次喂 64、128 句。所以最左永远留一维当"第几条"的下标；喂 3 句话就是 `[3, 22, 768]`。这一维在**索引**时才有意义：`x[0]` = 第 1 句话，`x[1]` = 第 2 句话……

现在回头读第 3 步的切片就顺了：

```python
last_hidden_state[:, 0, :]   # → [1, 768]
#     ↑           ↑     ↑
# 取全部句子     第0个词  全部768维
```

第一个 `:` 读作"把每句话都取出来"——虽然只有 1 句，代码要保持通用性，所以切片结果 `[1, 768]` 开头还是那个 `1`。

> **一句话**：这个 `1` 不是"1 个词"也不是"1 个向量"，是"1 句话"。你给它塞 5 句话，它就会变 5。

### 1.4 推理（接 04 的标配组合）

```python
model.eval()
with torch.no_grad():
    outputs = model(**token_input)
```

- `eval()`：关闭 Dropout 随机性
- `no_grad()`：不建计算图，省显存

notebook 中 `len(outputs) == 3`（因为开了 `output_hidden_states`）。

**检查点自测 1**：去掉 `output_hidden_states=True` 后，`len(outputs)` 会是几？（答案在 3.3 节）

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

**常见误区 1**：别以为"Embeddings 就完成语义区分了"。它只做**查表**（ID → 向量），不读上下文；三个 bank 此刻的向量差异**只有位置编号**，语义上仍相同。

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

回到 bank 的例子——三兄弟分道扬镳：

```text
第 1 轮 Self-Attention 后：
  bank(第6位)  看到 vault、money      → 往"金融机构"偏
  bank(第10位) 看到 robber、stealing  → 往"抢劫目标"偏
  bank(第19位) 看到 river、fishing    → 往"河岸"偏

第 12 轮后：
  vec[6]  = bank(金库)   ← 三个向量已明显不同
  vec[10] = bank(劫匪)
  vec[19] = bank(河岸)
```

> **这就是 BERT 的意义**：同一个词在不同上下文里得到不同的向量——即 06 说的**上下文相关表示**，Word2Vec 做不到。

**12 层的含义**：不是 12 个不同模型，是**同一套操作重复 12 次**（每层有自己的参数）。

| 层 | 大致学到什么 |
|---|---|
| 低层（1-4） | 句法：词性、短语结构 |
| 中层（5-8） | 语义：词义消歧、实体 |
| 高层（9-12） | 任务相关：情感、逻辑、推理 |

**检查点自测 2**：12 层 Encoder 的输出形状不变——"不变"的是形状，"变"的是什么？

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

**`Linear + Tanh` 各自在干嘛（拆开看）**：

`pooler_output = Tanh(Linear([CLS]向量))` 就两步：

- **`Linear`（线性层，`y = Wx + b`）**：一个 768→768 的矩阵乘 + 偏置，把所有数字重新加权组合。为什么需要这一步？原始 `[CLS]` 向量是"为预训练任务优化的通用表示"，**不一定适合直接当句子向量用**。Linear 做一次**可学习的特征重排**——相当于"给原始向量调个音"，让它在空间里更易被下游分类器分开。注意它"可学习"意味着权重不是拍脑袋定的，而是 NSP 任务训练出来的（这正是下面 ⚠️ 提醒的由来）。
- **`Tanh`（激活函数）**：把每个数字压到 `(-1, 1)`。做两件事：① **引入非线性**——如果没有它，`Linear` 叠下一个 `Linear` 还是线性，等于白加深，加了它才能拟合非线性关系；② **数值有界**——向量里可能有很大的数，Tanh 把它钳制在 `(-1, 1)`，防止极端值在后续任务里"爆炸"，数值更稳。

> **比喻**：`Linear` = 把原始向量"重新搅拌调配"（可学习的），`Tanh` = 调配完再"压模定型"（限数值范围）。合起来就是"给 `[CLS]` 做一次小的精加工"。

**⚠️ 实践提醒（重要）**：

官方文说明，这个 `Linear` 的权重是**在预训练的 NSP（Next Sentence Prediction）任务上训出来的**。而 NSP 后来被证明效果有限（RoBERTa 已去掉），因此：

> **`pooler_output` 在很多下游任务中，不一定比直接用 `last_hidden_state[:, 0, :]`（跳过 Linear+Tanh）或对所有位置做 mean pooling 更好。**
> `BertForSequenceClassification` 传统上接 `pooler_output`，但很多现代实现改用 `[CLS]` 原始向量或平均池化。

**常见误区 2**："pooler 是分类头"是高频误解。pooler 是 **BERT 自带**模块（`embeddings → encoder → pooler` 的最后一环），分类头是你额外加的 `Linear(768→2)`，两者不是一回事（接 03）。

**记忆卡**：`last_hidden_state[:, 0, :]` 是"生的 `[CLS]`"，`pooler_output` 是"熟的 `[CLS]`"（过了 Linear+Tanh）。熟的不一定更好吃——NSP 训过的线性层有时反而帮倒忙。

---

### 第 4 步 · 输出：从流水线上"抽头"

"抽头"直白翻译：**从流水线的某一环节，把中间结果导出来给你**（就像电路里从某处接个端子出来）。

**为什么模型要这样设计？** 因为 `BertModel` 是个"底座"，**不同下游任务要不同粒度的东西**：

| 下游任务 | 需要什么 | 从哪"抽" | 对应输出 |
|---|---|---|---|
| NER（标出每个词是啥） | 每个词的最终向量 | 最后一帧，22 个词全要 | `last_hidden_state` |
| 情感分类（整句夸还是骂） | 一句话 → 1 个向量 | 最后一帧抽 `[CLS]` 再加工 | `pooler_output` |
| 层融合 / 可解释性 | 每一层的表示 | 每个工位都抽 | `hidden_states` |
| 画注意力热力图 | 谁在看谁 | 每层加工内部 | `attentions` |

所以代码里那两个开关翻译过来就是：

```python
output_hidden_states=True   # "把每帧录像都存下来给我" → 多给 outputs[2]（13 帧）
output_attentions=True      # "把加工过程记录表也给我" → 多给 attentions
```

**不开开关 = 只默认抽最常见的两个头**（`last_hidden_state` + `pooler_output`）。这就是为什么 3.3 节说"不开则 `len(outputs) == 2`"——也是自测 1 的答案。

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

**四个输出怎么"录"下来的（把比喻展开）**：前向是一条流水线，流水线上有 13 个工位——工位 0 是 Embeddings，工位 1~12 是 Encoder 12 层，每个工位的输出都是 `[1, 22, 768]`：

| 你笔记里的说法 | 展开 | 拿到的数据 |
|---|---|---|
| `hidden_states` = **完整录像（13 帧）** | 在**每个工位出口装一个摄像头**，13 个工位的输出全部录下来，打包成 tuple | 13 个 `[1, 22, 768]` |
| `last_hidden_state` = **最后一帧** | 不看全部录像，**只截取最后一帧**（工位 12 的输出） | 1 个 `[1, 22, 768]` |
| `pooler_output` = 最后一帧里**抽一格再加工** | 从最后一帧 22 个词里只挑 `[CLS]`（第 0 格），再单独 Linear+Tanh 加工 | 1 个 `[1, 768]` |
| `attentions` = **"谁看了谁"的记录表** | 上面录的是"工位产出"，这个是"工位工作过程"——每层每个头，哪个词在看哪个词、看得多重 | 12 个 `[1, 12, 22, 22]` |

**关键认知**：这四个**不是四次独立计算，是同一趟前向的四个"视图"**——摄像头没让工位多干一遍活，只是顺手把过程录下来了。所以下面恒等式 1 才能成立：`outputs[0] == outputs[2][-1]`，录像最后一帧本来就是默认抽的那一帧。

> 类比手机"录像 + 截屏"：`hidden_states` = 整段录像，`last_hidden_state` = 从录像里截的最后一张图——不是两个不同的视频，是同一段。

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

**记忆卡**："**last** = 最后一层的**每个** token"：想拿"每个词最后的向量"就用它；想拿"整句一个向量"就用 pooler。一个偏"细"（22 个），一个偏"总"（1 个）。

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

**开关**：只有 `output_hidden_states=True`（或 `config.output_hidden_states=True`）才返回；**不开则 `len(outputs) == 2`**（即自测 1 的答案：2）。

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

**常见误区 3**：`hidden_states[0]` **不是**"第 1 层输出"，而是 **embedding 层输出**（还没进 encoder）。13 = 1(embedding) + 12(层)，不是 12 层算 13 帧。

---

## 四、三个恒等式（notebook 的核心验证）

**为什么 notebook 要花力气验证这三件事？** 因为"眼见为实"——代码证明比口头断言更能消除"这四个输出是不是四套独立计算"的怀疑。你以后读源码遇到类似怀疑，也可以直接写一行 `==` 验证。

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

**检查点自测 3**：恒等式 1 和 3 合起来能推出 `pooler_output == model.pooler(hidden_states[-1])` 吗？（提示：等号可传递）三个恒等式共同证明了什么？

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

读一个具体值：

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

**记忆卡**：产品 vs 配料表——`hidden_states` 是"每道菜"（成品向量），`attentions` 是"每道菜的配料用量"（谁掺了多少进来）。想研究"怎么做的"看配料表，想直接拿成品用看 hidden_states。

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
2. **接 03**：`pooler` 是 03 架构图 `embeddings → encoder → pooler` 的最后一环；它是 **BERT 自带模块，不是分类头**。
3. **接 04**：`eval()` + `no_grad()` 正是 04 的推理标配。
4. **接 06**：三个 bank 输入 ID 相同、输出不同 = 06 说的「上下文相关表示」。
5. **接 01**：`[CLS]` 被 pooler 拿出来做句子级表示，对应 01 情感分析的输出来源。

---

## 八、一句话总收

> **BertModel 的四个输出不是四次独立计算，而是同一条流水线上的不同"抽头"：**
> - `hidden_states` = 完整录像（13 帧）
> - `last_hidden_state` = 最后一帧
> - `pooler_output` = 最后一帧抽 `[CLS]` 再 Linear+Tanh
> - `attentions` = 每层"谁看了谁"的权重表
>
> **四步链精髓**：Embeddings 把整数变向量（孤立、无上下文）→ Encoder ×12 让词互相看 12 遍（形状不变、数值吸收上下文、同词不同副本分道扬镳）→ Pooler 抽 `[CLS]` 压成句子向量。

---

## 九、费曼三连问（学完合上文档自测）

1. **一句话**：BERT 的四个输出是什么关系？（提示：四个字——"同一流水线"）
2. **画出来**：不看文档，画出 `[1,22]` → `[1,22,768]` → `[1,768]` 的流动图，标出四个输出分别在哪里"抽头"。
3. **讲出去**：给一个只懂 Word2Vec 的人讲——为什么 BERT 里同一个词的三个副本会有不同向量？中间发生了什么？

如果三问都能脱口而出，这一章就真正是你的了。
