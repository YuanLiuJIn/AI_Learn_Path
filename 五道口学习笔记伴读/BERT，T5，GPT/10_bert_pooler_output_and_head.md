# 10 · pooler_output 与 BERT head：身体与"任务转接头"

> **接 07 / 09**：07 讲清了 `pooler_output` 是什么（`[CLS]` 过 Linear+Tanh），09 讲完了一个 `BertLayer` 的骨架。到 09 为止，BERT 的"**身体**"讲完了。
> 本篇讲"**接口**"——12 层 encoder 出来之后，到底怎么接上具体任务？HF 里那十来个 `BertForXxx` 差在哪？
>
> **视频**：[动手写 BERT 系列] bert pooler output 与 bert head `BV1AG4y1H7wq`（合集第 11 集，13:09）
> **配套 notebook**：`bilibili_vlogs/fine_tune/bert/tutorials/08_bert_head_pooler_output.ipynb`
> ⚠️ 官方仓库里这份 notebook 只写到"加载模型"就断了（前 4 格），正文是视频里即席讲的——所以本篇按主题补全，并补上可运行的验证代码。
>
> **一句话主旨**：**backbone（embeddings + 12×BertLayer + pooler）是通用的，任务靠"head"来切换**；`BertForXxx` 这些类，就是用同一个 backbone 拼上不同的 head。

---

## 〇、30 秒直觉

```
        ┌──────────── backbone（预训练好的，通用）────────────┐   ┌── head（任务相关，多为随机初始化）──┐
inputs → embeddings → 12×BertLayer → pooler → last_hidden_state → ├─ SequenceClassification: Linear(768→2)
                      [B,N,768]      [B,768]    [B,N,768]          ├─ TokenClassification:    Linear(768→K)
                                                                    ├─ QuestionAnswering:      Linear(768→2)
                                                                    └─ MaskedLM: transform + 30522 分类
```

- **07~09 讲的全是左边那个框**。它是"通用语言理解器"，**天生不认识任何具体任务**——它只会输出"每个词的 768 维向量"和"整句的 768 维向量"。
- **右边那些 `Linear(...)` 就是 head**：把 768 维表示"翻译"成任务要的答案（类别分数 / 每个词的标签 / 起止位置）。
- **微调（fine-tune）**做的事：backbone 的权重"轻轻动一下"（它已经懂语言了），head 的权重"从随机开始学"（它只懂这个任务）。

| | backbone | head |
|---|---|---|
| 包含什么 | `embeddings` + 12×`BertLayer` + `pooler` | 一个或几个 `Linear` / `dense` + 激活 + `LayerNorm` |
| 参数从哪来 | 预训练（MLM + NSP）得到的 checkpoint | **随机初始化**（除非是从同一任务的模型继续训） |
| 懂什么 | 语言（语法、语义、指代…） | 只懂这一个任务的输出格式 |
| 训练时 | 微调，小的学习率 | 从头学，大的学习率 |

> 类比：backbone 是**通用发动机**，head 是不同车型的**变速箱 / 轮胎**。预训练负责把发动机造好，微调负责换头。

---

## 一、先分清两个出口：token 级 head vs 句子级 head

这是本篇**最重要的一张表**。07 说过 backbone 有两个默认输出，**这两类 head 就分别接在这两个出口上**：

| 出口 | shape | 接什么任务 | 典型 head |
|---|---|---|---|
| `last_hidden_state`（源码里叫 `sequence_output`） | `[B, N, 768]` | **token 级**：每个词都要一个答案 | TokenClassification（NER/POS）、QuestionAnswering、MaskedLM |
| `pooler_output`（源码里叫 `pooled_output`） | `[B, 768]` | **句子级**：整句只要一个答案 | SequenceClassification、NextSentencePrediction、MultipleChoice |

**关键纠正（07 误区 2 的源码版）**：**pooler 不是所有 head 的必经之路**。

- 接 `pooler_output` 的，只有**句子级**任务；
- 所有 **token 级** head（NER、QA、MLM）**直接接 `last_hidden_state`**，**根本不碰 pooler**。

所以"pooler 是分类头"这个说法两头都错：pooler 是 backbone 的最后一环（07 已讲），而 head 是根据任务选的插头——**句子级任务才可能用到 pooler**。

---

## 二、HF 家族族谱：同一个 backbone，十来个"拼装"

HuggingFace 的命名规律：**`BertFor<任务>`**。全部都是 `BertModel` 加了点东西：

| 类名 | 在 backbone 上加了什么 | 输出 | 用途 |
|---|---|---|---|
| `BertModel` | **什么都没加**（就是 backbone 本身） | `last_hidden_state` `[B,N,768]`、`pooler_output` `[B,768]` | 拿特征、自己接网络 |
| `BertForPreTraining` | MLM head + NSP head（`cls.predictions.*` + `cls.seq_relationship.*`） | `prediction_logits` `[B,N,30522]`、`seq_relationship_logits` `[B,2]` | 复现预训练 |
| `BertForMaskedLM` | 只加 **MLM head**（`cls.predictions.*`） | `logits` `[B,N,30522]` | 完形填空、MLM 微调 |
| `BertForNextSentencePrediction` | 只加 **NSP head**（`cls.seq_relationship.*`） | `logits` `[B,2]` | 句对关系 |
| `BertForSequenceClassification` | `dropout` + `classifier: Linear(768→num_labels)` | `logits` `[B,num_labels]` | 情感分析、文本分类 |
| `BertForTokenClassification` | `dropout` + `classifier: Linear(768→num_labels)` | `logits` `[B,N,num_labels]` | NER、POS 标注 |
| `BertForQuestionAnswering` | `qa_outputs: Linear(768→2)` | `start_logits` `[B,N]`、`end_logits` `[B,N]` | 抽取式问答 |
| `BertForMultipleChoice` | 同 SequenceClassification | `logits` `[B,num_choices]` | 选择题 |

> 注意表里有两处 **`num_labels`**：SequenceClassification 的一个样本出**一个**答案，TokenClassification 的一个样本出 **N 个**答案。同名不同用，形状差异全在"接哪个出口"。

---

## 三、逐个解剖 head（源码级，看形状怎么变）

以下都基于 `bert-base-uncased`：`H=768`、`vocab=30522`、`B=1`、`N=8`。

### 3.1 SequenceClassification：句子级

```python
# BertForSequenceClassification.forward 关键两行
pooled_output = outputs[1]                      # [B, 768]  ← 就是 pooler_output
logits = self.classifier(self.dropout(pooled_output))   # [B, num_labels]
```

- `self.classifier = nn.Linear(768, num_labels)`，**随机初始化**；
- `num_labels=2` → `logits` `[1, 2]`，配合 `CrossEntropyLoss`（HF 里 `problem_type` 决定：单标签分类用 CE，多标签用 BCE，回归用 MSE）；
- ⚠️ **`classifier` ≠ `pooler`**：`pooler` 是 768→768 且带 Tanh（07 讲的那个），`classifier` 是 768→`num_labels`。两个模块前后串在一条线上，但一个属于 backbone、一个是 head。

### 3.2 TokenClassification：token 级

```python
sequence_output = outputs[0]                    # [B, N, 768]  ← 换出口了！
logits = self.classifier(self.dropout(sequence_output))   # [B, N, num_labels]
```

- 同样是 `Linear(768, num_labels)`，但作用在**每个词**上，结果自然多一维 `N`；
- 每个位置独立分类（NER 里 9 类 BIO 标签 → `[B,N,9]`），**位置之间不做 softmax 归一化**，每个位置各自 softmax。

### 3.3 QuestionAnswering：token 级的"两分类"

```python
sequence_output = outputs[0]                    # [B, N, 768]
logits = self.qa_outputs(sequence_output)       # [B, N, 2]  ← 一个 Linear(768→2)
start_logits, end_logits = logits.split(1, dim=-1)   # 各 [B, N, 1] → squeeze → [B, N]
```

- 一个 `Linear(768→2)` 同时产出"这一位是不是答案**开始**"和"是不是答案**结束**"两套分数；
- 训练时把两套 logits 各做一次 CE，相加；推理时在 `[B,N]` 上找 start/end 的最大值（再满足 `end ≥ start`）。

### 3.4 MaskedLM：最"重"的 head（附权重共享）

```python
self.cls = BertOnlyMLMHead(config)              # 内部 = BertLMPredictionHead
sequence_output = outputs[0]                    # [B, N, 768]
prediction_scores = self.cls(sequence_output)   # [B, N, 30522]
```

MLM head 是**两段式**（不是一层 Linear）：

```
[B,N,768] → dense(768→768) → GELU → LayerNorm  →  decoder(768→30522, bias=False) → [B,N,30522]
            └──────── BertPredictionHeadTransform ────────┘
```

**关键秘密：`decoder.weight` 与词嵌入 `word_embeddings.weight` 是同一块参数**（tied weights）：

```python
self.cls.predictions.decoder.weight = self.bert.embeddings.word_embeddings.weight   # 同一个 DataPtr
```

- 30522 × 768 ≈ **23.4M** 参数，占 BERT-base（110M）的 1/5；共享之后**不额外占参数、还强制"输入/输出同一套词向量空间"**；
- 这也是 [GPT 番外] `wte 与 lm_head` 那集要讲的主题——GPT-2 同样共享；
- 为什么两段而非直接一层？`dense + GELU + LN` 让词向量先"在自己的空间里非线性重组一次"，再拿去和 30522 个词比相似度。**去掉这一段，MLM 效果会明显变差。**

### 3.5 NextSentencePrediction：句子级，只用一个 Linear

```python
pooled_output = outputs[1]                      # [B, 768]
seq_relationship_scores = self.cls(pooled_output)   # [B, 2]  ← Linear(768→2)，即 cls.seq_relationship
```

- 输入就是 `pooler_output`，输出"两句是否相邻"的 2 类分数；
- 这就是 07 说的"**pooler 的 Linear 是 NSP 训出来的**"的来源——它不仅参与 NSP，还接收 NSP 的反向传播。

### 3.6 BertForPreTraining = 3.4 + 3.5

```python
self.cls = BertPreTrainingHeads(config)   # = BertLMPredictionHead + Linear(768→2)
```

一次前向同时吐两组 logits。**回到那个问题：`cls.*` 里的 `cls` 是"classification"吗？** 不是——它是源码里 `self.cls` 这个**属性名**（预训练头容器的习惯命名）：

| 属性 | 实际内容 | 任务 |
|---|---|---|
| `cls.predictions.*` | MLM 头（transform + decoder） | 完形填空 |
| `cls.seq_relationship.*` | `Linear(768→2)` | 下一句预测 |

所以 **`cls.*` ≠ 分类头**，它是"预训练头"的统称。

---

## 四、那条加载警告怎么读（notebook 唯一真实输出）

notebook 里 `BertModel.from_pretrained('bert-base-uncased')` 打印了这么一段（stderr）：

```
Some weights of the model checkpoint at bert-base-uncased were not used when initializing BertModel:
['cls.predictions.transform.dense.weight', 'cls.predictions.transform.LayerNorm.weight',
 'cls.seq_relationship.weight', 'cls.predictions.decoder.weight', 'cls.predictions.transform.dense.bias',
 'cls.predictions.bias', 'cls.seq_relationship.bias', 'cls.predictions.transform.LayerNorm.bias']
- This IS expected if you are initializing BertModel from the checkpoint of a model trained on another task...
```

**这段警告恰恰是本篇最直观的教材**：checkpoint 里存着预训练用的 `cls.*` 权重（MLM + NSP 头），但 **`BertModel` 这个类里没有对应的模块**（它只有 backbone + pooler），所以这些权重被"丢掉/忽略"。

换句话说，**警告就是模型族谱的体检报告**：忽略哪些 key，说明这个类**缺哪些模块**。

| 你实例化的类 | 被忽略的 key | 说明 |
|---|---|---|
| `BertModel` | `cls.predictions.*`、`cls.seq_relationship.*` | 没有预训练头（本篇主角的对照） |
| `BertForMaskedLM` | 只有 `cls.seq_relationship.*` | 有 MLM 头，但没 NSP 头 |
| `BertForSequenceClassification` | `cls.predictions.*`、`cls.seq_relationship.*` | 两个预训练头都没有；`classifier` 是**新初始化**的 |

反过来，`BertForMaskedLM` 能**直接用** `cls.predictions.*` 的权重（因为 checkpoint 里有）——这就是为什么 MLM 微调是"接着预训练往下走"，而分类任务是从"head 随机"开始。

> 这正是 04 讲的 `from_pretrained` 做的事：**按名字匹配地装权重**，名字对不上的就忽略（或随机初始化并提示）。

---

## 五、pooler vs 分类头：别再混淆（承 07 误区 2）

| | `pooler`（`bert.pooler`） | `classifier`（`classifier`） |
|---|---|---|
| 属于谁 | **backbone** 的一部分 | **head** |
| 结构 | `Linear(768→768)` + `Tanh` | `Linear(768→num_labels)` |
| 参数来源 | 预训练（NSP 训过） | 随机初始化，微调时学 |
| 输出 | `[B, 768]`（还是个**通用句子向量**） | `[B, num_labels]`（**任务答案的分数**） |
| 是否存在 | 只要用 `BertModel` 就永远在 | 只有 `BertForXxx` 才有 |

**为什么很多现代实现绕开 pooler？**（07 ⚠️ 的延伸）
`pooler` 的 Linear 是为 NSP 服务的，NSP 后来被认为收益有限（RoBERTa 直接删掉了 NSP）。于是：

- 分类任务常用 `last_hidden_state[:, 0, :]`（**原始 `[CLS]`**，跳过那个 NSP 线性层）；
- 句子向量任务（sentence-transformers）常用**所有 token 的 mean pooling**（合集第 26~27 集）；
- 这些做法在不少任务上 ≥ 用 `pooler_output`。

> 记忆：**`pooler_output` 是"免费送的"，不是"必须用的"**；`BertForSequenceClassification` 用它只是历史沿袭。

---

## 六、动手验证（4 个可跑实验）

```python
import torch
from transformers import BertConfig, BertModel, BertForSequenceClassification
from transformers import BertForTokenClassification, BertForMaskedLM

config = BertConfig.from_pretrained("bert-base-uncased")   # H=768, num_labels 默认 2
```

### 6.1 backbone 完全一致，head 是"多出来的"

```python
backbone = BertModel(config)
clf      = BertForSequenceClassification(config)

print(sum(p.numel() for p in backbone.parameters()))       # 约 1.09 亿
print(sum(p.numel() for p in clf.bert.parameters()))       # 一模一样（clf.bert 就是 BertModel）
print(clf.classifier)      # Linear(in_features=768, out_features=2, bias=True)
print(clf.bert.pooler)     # BertPooler(dense=Linear(768→768), activation=Tanh)  ← 07 讲的那个
```

**结论**：`BertForSequenceClassification` = `BertModel`（`clf.bert`）+ `dropout` + `classifier`。**backbone 参数量分毫不差。**

### 6.2 SequenceClassification 的 logits 确实来自 pooler_output

```python
ids = torch.tensor([[101, 2924, 2075, 1996, 2924, 2572, 102]])   # [B=1, N=7]
am  = torch.ones_like(ids)

clf.eval()
with torch.no_grad():
    bb_out = clf.bert(input_ids=ids, attention_mask=am)         # 只跑 backbone
    manual = clf.classifier(bb_out.pooler_output)                # 手动接 head → [1, 2]
    auto   = clf(input_ids=ids, attention_mask=am).logits        # 完整模型 → [1, 2]

print(manual.shape, auto.shape)                     # torch.Size([1, 2]) torch.Size([1, 2])
print(torch.allclose(manual, auto, atol=1e-6))      # True
```
（`eval()` 下 dropout 是恒等映射，所以能对上；`train()` 下两者会因随机 dropout 不同。）

### 6.3 TokenClassification 换成了 last_hidden_state

```python
tok_clf = BertForTokenClassification(config)
tok_clf.eval()
with torch.no_grad():
    bb_out = tok_clf.bert(input_ids=ids, attention_mask=am)
    manual = tok_clf.classifier(bb_out.last_hidden_state)   # [1, 7, 2] ← 每个词一份
    auto   = tok_clf(input_ids=ids, attention_mask=am).logits

print(manual.shape, auto.shape)                     # [1,7,2] 与 [1,7,2]；再 allclose → True
```

**这一条直接验证了第一节的结论**：句子级任务吃 `pooler_output` `[B,768]`，token 级任务吃 `last_hidden_state` `[B,N,768]`——**同一套 backbone，出口不同，head 的输出形状自然差一维**。

### 6.4 MLM head 的 decoder 与词嵌入是同一块参数（tied）

```python
mlm = BertForMaskedLM(config)

w_dec = mlm.cls.predictions.decoder.weight
w_emb = mlm.bert.embeddings.word_embeddings.weight

print(w_dec.shape)                      # torch.Size([30522, 768])
print(w_dec.data_ptr() == w_emb.data_ptr())     # True ← 同一块显存
print(mlm.cls.predictions.transform)    # dense(768→768) + GELU + LayerNorm
```

> 反过来试一下：`mlm.cls.predictions.decoder.bias.shape` → `[30522]`，这个 bias **不共享**。

### 6.5 参数账本（head 到底加了多少）

| head | 新增参数 | 占比 |
|---|---|---|
| SequenceClassification（2 类） | `768×2+2 = 1,538` | 约 0.001% |
| TokenClassification（9 类） | `768×9+9 = 6,921` | 约 0.006% |
| QuestionAnswering | `768×2+2 = 1,538` | 约 0.001% |
| MaskedLM | transform 约 0.59M + 输出 bias 30,522；**decoder 23.4M 被 tie 掉** | 约 0.6% |

**这就是 BERT 微调"便宜"的根本原因**：你要新学的东西极少，绝大部分能力都来自 backbone。也因此，"微调"能只用几千条标注数据。

---

## 七、常见误区

1. **"pooler 就是分类头"** —— 错两次：pooler 属于 backbone（768→768+Tanh），分类头是 `classifier`（768→`num_labels`），且 token 级任务根本不用 pooler。
2. **"换个 head 要重训 backbone"** —— 不用。backbone 已经懂语言，通常 2~4 个 epoch 小学习率微调即可；甚至可以冻结 backbone 只训 head（04 的 `requires_grad`）。
3. **"`logits` 就是概率"** —— 不是，是**未归一化的分数**。要概率仍需 `softmax`（多分类）或 `sigmoid`（多标签）。HF 的 `outputs.logits` 一律是 softmax 之前的值。
4. **"二分类就用 sigmoid"** —— 在 HF 里，`num_labels=2` 走的是 `CrossEntropyLoss`（其实内部用 `[B,2]` 分类）；只有在 `problem_type="multi_label_classification"` 时才用 BCE，`num_labels=1` 的回归才用 MSE。
5. **"`cls.*` 是分类头"** —— 错。`cls` 只是"预训练头容器"的属性名，`cls.predictions` 是 MLM 头，`cls.seq_relationship` 是 NSP 头。
6. **"MLM 头就是一层 Linear"** —— 错，是 `dense+GELU+LayerNorm` + `decoder` 两段式，并且 decoder 与词嵌入共享权重。
7. **"TokenClassification 的 `[B,N,K]` 要在 N 维度 softmax"** —— 错，**每个位置独立归一化**（在最后一维 `K` 上做），位置之间不互相竞争。
8. **"加载警告都可以无视"** —— 大多数情况下是"正常的"（本篇第四节），但要**看懂它**：忽略的 key 说明这个类缺哪些模块；如果忽略的恰好是你想加载的（比如自己保存的 head 权重对不上名字），那就是真 bug。

---

## 八、记忆卡

- **backbone 通用，head 管任务**：`BertFor<任务>` = `BertModel`（`model.bert`）+ 任务头
- **两个出口**：`last_hidden_state [B,N,768]` → token 级；`pooler_output [B,768]` → 句子级
- **谁用谁**：SequenceClassification / NSP / MultipleChoice → pooler；TokenClassification / QA / MLM → last_hidden_state
- **MLM 头** = `dense+GELU+LN` + `decoder(tied with word_embeddings)`
- **`cls.*`** = 预训练头（`predictions` = MLM，`seq_relationship` = NSP）
- **加载警告** = 模型族谱的体检报告（忽略哪些 key = 缺哪些模块）
- **logits 未过 softmax**；head 参数几乎可忽略（1.5K ~ 0.6M）

---

## 九、自测（先答再看）

1. `BertForSequenceClassification` 和 `BertForTokenClassification` 的 `classifier` 结构几乎一样，为什么输出形状差一维？
2. `pooler_output` 和 `classifier` 的输出，哪个是"任务答案"？哪个是"通用句子表示"？
3. 为什么 `BertForMaskedLM` 加载 checkpoint 时只忽略 `cls.seq_relationship.*`，而 `BertModel` 忽略一大堆？
4. 不跑代码，估算 `num_labels=10` 的 TokenClassification head 有多少参数？相比 1.09 亿占多少？
5. 你保存了一个 `BertForSequenceClassification` 微调模型，用 `BertModel` 加载它，会看到什么警告？这说明了什么？

<details>
<summary>参考答案</summary>

1. 因为接的出口不同：前者接 `pooler_output` `[B,768]`（整句压成一个向量）→ `[B,num_labels]`；后者接 `last_hidden_state` `[B,N,768]`（每个词都保留）→ `[B,N,num_labels]`。`classifier` 本身只是 `Linear(768→num_labels)`，形状差异来自输入。
2. `classifier` 的输出是任务答案（logits `[B,num_labels]`）；`pooler_output` 是 backbone 送的通用句子向量 `[B,768]`，对任何任务都一样。
3. 因为 checkpoint 里有 MLM 头（`cls.predictions.*`），`BertForMaskedLM` **有对应模块能接住**，所以只用忽略 NSP 头；`BertModel` 里连 MLM 头都没有，所以 `cls.predictions.*` 和 `cls.seq_relationship.*` 全被忽略。
4. `768×10+10 = 7,690`，约占 1.09 亿的 **0.007%**——几乎可以忽略。
5. 会警告忽略 `classifier.weight`、`classifier.bias`（以及 `bert.pooler` 之外没有的键）；**说明 `BertModel` 的类结构里没有 `classifier` 这个模块**，你微调出来的分类头无法被 `BertModel` 接住。要复用必须用同名结构（`BertForSequenceClassification` 或自己写同名的 `classifier`）。
</details>

---

## 十、费曼三连问

1. **一句话**：backbone（`BertModel`）是预训练好的通用语言理解器，`BertForXxx` 就是在它出口处挂上不同的 `Linear` 头来回答不同任务；token 级任务从每个词的位置取向量，句子级任务用整句的 pooled 向量。
2. **说形状**：给定 `B=1, N=7, H=768`，写出 `BertModel` 的两个默认输出、`BertForSequenceClassification`（2 类）、`BertForTokenClassification`（9 类）、`BertForMaskedLM` 各自的输出形状。
3. **讲出去**：向只会用 `BertModel` 拿特征的人解释——为什么做分类时你自己接一个 `Linear(768→2)` 和用 `BertForSequenceClassification` 效果通常差不多？两者差在哪（pooler、loss、标签约定）？

---

## 十一、与前面笔记的连接

- **接 07**：07 讲 `pooler_output` 怎么写出来的（`[CLS]` + Linear + Tanh）；本篇讲它**接给谁用**（句子级 head），以及它**为什么常常被绕过**（`last_hidden_state[:,0,:]` / mean pooling）。
- **接 08 / 08B / 09**：这三篇讲的都是 backbone **内部**（自注意力、分块矩阵、Add & Norm）；本篇是 backbone **出口之后**的事。
- **接 03**：03 的架构参数表里出现过 `BertForMaskedLM` 等类名，本篇给出了它们的模块级"族谱"。
- **接 04**：`from_pretrained` 的"按名装权重"和本篇第四节的加载警告是同一件事的两面。
- **→ 11**：合集第 12 集「masking 机制、bert head 与 BertForMaskedLM」，见 [11_bert_masking_and_masked_lm.md](./11_bert_masking_and_masked_lm.md)——把本篇 3.4 的 MLM 头展开成训练任务：`[MASK]` token、80/10/10 的 masking 策略、`labels` 与 `loss`（`-100` / 只算被 mask 的位置）。
- **顺延的番外**：位置编码（Sin Position Encoding，合集第 24 集）、tied weights 的通用讲法（GPT 番外 `wte / lm_head`）——本篇 3.4 已经先见了一次。

---

*10 完。跟着跑一遍第六节的 4 个实验，本篇的核心（"两个出口 + head 只是拼装"）就落地了。*
