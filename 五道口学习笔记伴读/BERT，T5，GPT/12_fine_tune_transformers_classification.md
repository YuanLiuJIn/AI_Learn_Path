# 12 · fine tune transformers（文本分类 / 情感分析）

> **接 11**：11 讲完 MLM 预训练任务，"动手写 bert"子系列收官（合集第 12 集）。本篇起进入**「BERT、T5、GPT」正片**——第一次把 backbone + head **真正拿去训练、真正跑出指标**。
>
> **视频**：`BV1tM411L7HE`（合集第 13 集）
> **本期 code**：`github.com/chunhuizhang/bert_t5_gpt/blob/main/tutorials/01_fine_tune_transformers_on_classification.ipynb`
> **本地**：`bert_t5_gpt/tutorials/01_fine_tune_transformers_on_classification.ipynb`（90 个 cell，**完整可跑**）
> **系列视频**：`space.bilibili.com/59807853/channel/collectiondetail?sid=496538`
>
> **一句话主旨**：微调 = **换一个 head、拿自己的数据、交给 `Trainer` 训几轮**。本篇用 16000 条推文、6 类情感，在 **2 张卡上 71 秒**把 `distilbert` 训到 **93.25%** 准确率，并演示了"**按 loss 排序揪出标错的样本**"这一经典套路。

---

## 〇、30 秒直觉

整篇微调的**代码主体就三行**：

```python
model = AutoModelForSequenceClassification.from_pretrained(backbone, num_labels=6)  # ① 换个头
args  = TrainingArguments("/tmp/emotion_ft", evaluation_strategy="epoch", lr=2e-5, ...)  # ② 配超参
Trainer(model, args, train_dataset=..., eval_dataset=..., compute_metrics=..., tokenizer=...).train()  # ③ 开训
```

**真正的功夫全在两件事上**（也是本篇篇幅所在）：

- **数据怎么变成 token**（§四）
- **训完怎么读结果**（§八：混淆矩阵 + loss 排序）

### 0.1 微调 vs 预训练：一张表说清

| | **预训练**（11 讲，MLM） | **微调**（本篇，6 分类） |
|---|---|---|
| 任务 | 挖空填空 | 句子打标签 |
| 数据 | 海量**无标注**文本 | 16000 条**带标签**推文 |
| 监督粒度 | **token 级**：每个位置一个答案 | **句子级**：一整句只有一个答案 |
| 头 | `cls.predictions`（768→30522，与词嵌入 tied） | `classifier`（768→6，**随机初始化**） |
| loss 算法 | `CE`，`-100` 屏蔽非 mask 位置 | `CE`，直接对句子标签算 |
| 学习率 | 大（~1e-4），从头学 | **小（2e-5）**，只"轻推"已有的语言知识 |
| 耗时 | 几天 / 几十张卡 | **71 秒 / 2 张卡** |

**一句话**：**头是新的（从随机开始学），身体是旧的（只轻轻动）**——这就是"微调"和"从头训练"的本质区别（呼应 10 讲：backbone 懂语言，head 懂任务）。

---

## 一、notebook 全景（90 个 cell，六段）

| 段 | 大致 cell | 内容 | 本篇 |
|---|---|---|---|
| **0 · 环境** | 0~5 | 装包、`import`、版本号、GPU 检查 | — |
| **1 · 数据 & EDA** | 6~32 | `load_dataset('emotion')`、8:1:1、`ClassLabel`、标签频率、词数箱线图 | §二、§三 |
| **2 · tokenize** | 34~46 | `AutoTokenizer`、`model_input_names`、`all_special_ids`、`map`、`set_format` | §四 |
| **3 · 选模型** | 48~56 | `AutoModel` vs `AutoModelForSequenceClassification`、`distilbert` vs `bert` | §五 |
| **4 · 训练** | 58~65 | `notebook_login`、`TrainingArguments`、`Trainer.train()`、`predict` | §六、§七 |
| **5 · 分析 & 上线** | 67~89 | 混淆矩阵、loss 排序找错标、`push_to_hub`、`pipeline` | §八、§九 |

> **看这个结构**：数据/EDA 花了近 1/3 的 cell，训练核心只有 2 个 cell。**微调工程的真相是"数据与评估占了大部分时间"，而不是调模型。**

---

## 二、数据集：`emotion`（8:1:1 六分类，且**不均衡**）

```python
from datasets import load_dataset
emotions = load_dataset('emotion')
emotions
```

```text
DatasetDict({
    train:      Dataset({features: ['text', 'label'], num_rows: 16000})
    validation: Dataset({features: ['text', 'label'], num_rows: 2000})
    test:       Dataset({features: ['text', 'label'], num_rows: 2000})
})
```

### 2.1 三个必须记住的元信息

```python
emotions['train'].features
```

```text
{'text':  Value(dtype='string'),
 'label': ClassLabel(num_classes=6,
                     names=['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'])}
```

| 项 | 值 |
|---|---|
| 规模 | **16000 / 2000 / 2000**（≈ **8 : 1 : 1**） |
| 输入列 | `text`（一句推文） |
| 标签列 | `label`，`ClassLabel`，**6 类** |
| 映射 | `0=sadness, 1=joy, 2=love, 3=anger, 4=fear, 5=surprise` |

> `ClassLabel` 是 datasets 的一个 feature 类型：**存的是 int，但带着"int ↔ 人类可读名字"的映射**。所以你要标签名时得走 `features['label'].names[i]`——这就是 §三 里 `label_name` 那一列的来源。

### 2.2 标签分布：**严重不均衡**（这张表后面要用两次）

```python
emotions_df.label.value_counts()
```

```text
1    5362      joy
0    4666      sadness
3    2159      anger
4    1937      fear
2    1304      love
5     572      surprise
```

| 观察 | 数字 | 含义 |
|---|---|---|
| 最多类 | `joy` 5362 | |
| 最少类 | `surprise` 572 | |
| **不均衡比** | **5362 / 572 ≈ 9.4 倍** | 差一个数量级 |
| 两个头部类合计 | (5362+4666)/16000 ≈ **62.7%** | 光猜"joy 或 sadness"就有六成 |

**这为什么重要？** 因为 §八 的混淆矩阵要拿它当"基准线"读：

- `joy` 错 44 条（绝对数**最大**）——但它有 5362 条（占 33.5%），错得**相对**不算多；
- `surprise` 只错 14 条（绝对数**最小**）——但它只有 572 条，错得**相对**最惨。

> **只看绝对数会误判**。这就是为什么 §七 里 `compute_metrics` 同时报了 **accuracy（加权）** 和 **precision（macro）**：macro 平均让每个类**权重相同**，专门用来暴露小类被忽略的问题。

---

## 三、EDA 三个动作 + 它抓到的两个事实

```python
emotions_df = emotions['train'].to_pandas()                                  # ① Dataset → DataFrame
emotions_df['label_name'] = emotions_df.label.apply(
    lambda x: emotions['train'].features['label'].names[x])                  #    int → 名字（更好读）

emotions_df['label_name'].value_counts(ascending=True).plot.barh()           # ② 标签频率条形图
plt.title('freq of labels')

emotions_df['words per tweet'] = emotions_df['text'].str.split().apply(len)  # ③ 词数分布
emotions_df.boxplot('words per tweet', by='label_name', grid=False, color='black')
```

> 三步：**`to_pandas()` → 看标签分布 → 看文本长度分布**。接手任何文本分类数据的标准开场，5 分钟就能回答："类平不平衡？文本多长？要不要截断？有没有脏数据？"

### 3.1 事实一：文本**极短**

```python
print(emotions_df['words per tweet'].max(), emotions_df['words per tweet'].idxmax())
# 66  6322
print(emotions_df['words per tweet'].min(), emotions_df['words per tweet'].idxmin())
# 2   4150
```

| | 值 | 样本 |
|---|---|---|
| 最长 | **66** 词 | index `6322`（`sadness`） |
| 最短 | **2** 词 | index `4150`：`"earth crake"`（标 `fear`） |

最长那条原文（含越南语碎句，说明数据集是**多语言混的**）：

```text
i guess which meant or so i assume no photos no words or no other way to convey what it really
feels unless you feels it yourself or khi bi t au th m i bi t th ng ng i b au i rephrase it to
a bit more gloomy context unless you are hurt yourself you will never have sympathy for the hurt ones
```

**两个推论**：

1. **不需要担心截断**：最长 66 词 ≈ 70 个 token，`tokenizer.model_max_length = 512`，离得很远。所以 §四 的 `truncation=True` 在这个数据集里**从不触发**（写了是防御性的好习惯）。
2. **短文本本身很难**：`"earth crake"` 只有 2 个词、还疑似拼错（earthquake?），信息量不够 → 这种样本**注定难以分类**。这为 §八 里"错得最多的样本"埋了伏笔。

### 3.2 事实二：数据集**有 label 噪声**

`"earth crake"` 标成 `fear`——**这标注本身就可疑**。这不是个例：§八 用 loss 排序会给出更硬的证据（`iloc[882]` 那条被标成 `love` 却被模型高置信判为 `sadness`）。

> **这是一次"数据质量侦察"**：EDA 的目的不是画图好看，而是**在训练前就建立"指标上限"的直觉**——如果 5% 的标签是错的，那 93% 准确率可能已经接近天花板了。

---

## 四、text → token：`tokenizer` 与 `set_format`

### 4.1 先验明 tokenizer 的"身份"

```python
model_ckpt = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
```

```python
tokenizer.encode('hello world')   # [101, 7592, 2088, 102]
tokenizer.encode('HELLO WORLD')   # [101, 7592, 2088, 102]
tokenizer.encode('Hello World')   # [101, 7592, 2088, 102]
```

三行输出**完全一致**——因为 `uncased`。这就是 06 讲的 uncased 词表：`HELLO` 与 `hello` 是同一个 token `7592`。

- **好处**：词表更小、`[UNK]` 更少、稀有词更少。
- **代价**：**大小写信息丢失**。情感分析里 `"GREAT!!!"` 和 `"great"` 对模型毫无区别——这类任务偶尔想要 cased 版本。

再确认三件事（11 讲的 id 表在这里又用了一次）：

```python
tokenizer.vocab_size          # 30522
tokenizer.model_max_length    # 512
tokenizer.model_input_names   # ['input_ids', 'attention_mask']
```

```python
for special_id in tokenizer.all_special_ids:
    print(special_id, tokenizer.decode(special_id))
# 100 [UNK] / 102 [SEP] / 0 [PAD] / 101 [CLS] / 103 [MASK]
```

> ⚠️ **注意 `model_input_names` 只有两项**：`['input_ids', 'attention_mask']`，**没有 `token_type_ids`**。因为 DistilBERT **不区分句子对**（没有 segment embedding）。BERT 在这里会是三项（02 讲）。本例单句输入时即使 BERT 的 `token_type_ids` 也全是 0，但**这个差别在句子对任务（如 NLI）上会真正体现**。

编码一条完整样本（`101 ... 102` 包裹，首尾就是 `[CLS]`/`[SEP]`）：

```python
tokenizer.encode(emotions_df.iloc[6322]['text'])
# [101, 1045, 3984, 2029, ..., 3924, 102]
```

### 4.2 批量 tokenize：`map` + `batched=True` + **`batch_size=None`**

```python
def batch_tokenize(batch):
    return tokenizer(batch['text'], padding=True, truncation=True)

emotions_encoded = emotions.map(batch_tokenize, batched=True, batch_size=None)
```

```text
DatasetDict({
    train:      Dataset({features: ['text', 'label', 'input_ids', 'attention_mask'], num_rows: 16000})
    validation: Dataset({features: ['text', 'label', 'input_ids', 'attention_mask'], num_rows: 2000})
    test:       Dataset({features: ['text', 'label', 'input_ids', 'attention_mask'], num_rows: 2000})
})
```

**`batch_size=None` 是关键**（也是最容易踩的坑）：

| 写法 | 含义 | 结果 |
|---|---|---|
| `batch_size=None` | 把**整个 split 当成一个 batch** 交给 `batch_tokenize` | `padding=True` → pad 到**全局最长** → 全部样本长度一致 ✅ |
| `batch_size=32` | 每 32 条一个 batch，各自 pad 到**本 batch 最长** | 不同 batch 长度不同 ❌ 下一步会炸 |

为什么必须一致？因为下一步要"转成张量"：

```python
print(type(emotions_encoded['train']['input_ids']))   # <class 'list'>

emotions_encoded.set_format('torch', columns=['label', 'input_ids', 'attention_mask'])

print(type(emotions_encoded['train']['input_ids']))   # <class 'torch.Tensor'>
```

**`set_format('torch')` 要求同一列的所有样本形状一致**（它要把 list of list 堆成一个矩阵）。如果按 batch 各自 padding，长度参差不齐，就堆不起来。

所以最终是**两层 padding**：

1. **`map` 阶段（本节的 `batch_size=None`）**：全局统一长度 —— 目的是让 `set_format` 能用；
2. **`DataCollator` 阶段（§七）**：按**实际训练 batch** 内的最长重新 pad —— 目的是省算力。

> 长度到底是多少？最长样本 66 词 ≈ 70 个 token，**远小于 512**。所以 `truncation=True` 在这个数据集里**从头到尾没触发过**——写着是防御性的好习惯，不是必需品。

### 4.3 `set_format` 的 `columns` 在干嘛

```python
emotions_encoded.set_format('torch', columns=['label', 'input_ids', 'attention_mask'])
```

`columns=[...]` 是**白名单**：只保留这三列（`text` 被排除在 `__getitem__` 之外）。**这一步很必要**——否则取样本时会带出字符串 `text`，`DataCollator` 收到字符串会直接报错。

> 记住这个三段式管线：**`Dataset`（list）→ `map` tokenize → `set_format('torch')`（Tensor）**。以后所有 datasets + transformers 的微调都长这样。

---

## 五、选 backbone：`distilbert` vs `bert`（66M vs 109M）

### 5.1 三次 `from_pretrained` 的警告对照（"族谱体检报告"第三次出现）

```python
from transformers import AutoModel, AutoModelForSequenceClassification

AutoModel.from_pretrained('distilbert-base-uncased')
AutoModel.from_pretrained('bert-base-uncased')
AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=6)
```

| 加载 | 被忽略的 key | 为什么 |
|---|---|---|
| `AutoModel('distilbert-base-uncased')` | `vocab_transform.*`、`vocab_layer_norm.*`、`vocab_projector.*`（6 个） | 这是 **DistilBERT 的 MLM 头** |
| `AutoModel('bert-base-uncased')` | `cls.predictions.*` + `cls.seq_relationship.*`（8 个） | BERT 的 **MLM 头 + NSP 头**（与 11 讲完全一致） |
| `AutoModelForSequenceClassification('distilbert-base-uncased', num_labels=6)` | ① 忽略 `vocab_*`（MLM 头）② **新建** `pre_classifier.*`、`classifier.*` | 分类头 checkpoint 里本来就没有 |

第三条会打出**两个**警告，第二个尤其重要（notebook 原文）：

```text
Some weights of DistilBertForSequenceClassification were not initialized from the model
checkpoint at distilbert-base-uncased and are newly initialized:
['pre_classifier.bias', 'pre_classifier.weight', 'classifier.weight', 'classifier.bias']
You should probably TRAIN this model on a down-stream task to be able to use it for predictions.
```

> **这第二个警告不是错误，是"设计如此"**：新头随机初始化，正是微调要训练的东西。**看到它 = 微调配置正确**；如果它出现在一个"你说好要冻结 backbone、只训头"的场景里而你又没设 `requires_grad`，才需要警惕（04 讲）。

**DistilBERT 的 MLM 头命名 ↔ BERT（换个马甲，同一个 head）**：

| BERT（11 讲） | DistilBERT | 作用 |
|---|---|---|
| `cls.predictions.transform.dense` | **`vocab_transform`** | 768→768 + GELU |
| `cls.predictions.transform.LayerNorm` | **`vocab_layer_norm`** | LayerNorm |
| `cls.predictions.decoder` | **`vocab_projector`** | 768→30522（tied） |

### 5.2 参数量：66M vs 109M

```python
from transformers_utils import get_params
get_params(AutoModel.from_pretrained('distilbert-base-uncased'))  # 66,362,880
get_params(AutoModel.from_pretrained('bert-base-uncased'))        # 109,482,240
```

**1.65 倍差距**，来源是层数：DistilBERT **6 层** vs BERT **12 层**。

> DistilBERT 用的是"**知识蒸馏**"：让 6 层学生去模仿 12 层老师的输出分布。它保留约 **97%** 的 BERT 性能，但**小 40%、快 1.65 倍**。所以"线上要快 → distilbert，要极致精度 → bert"，本篇选它做教学（跑得快，能立刻看到结果）。
>
> 注：`get_params` 统计的是 `requires_grad=True` 的参数（§七 3.1），微调时全部可训练，所以数值 == 全模型参数量。

### 5.3 结构对照：`DistilBertForSequenceClassification`（notebook 真实打印）

```text
DistilBertForSequenceClassification(
  (distilbert): DistilBertModel(
    (embeddings): Embeddings(
      (word_embeddings):     Embedding(30522, 768, padding_idx=0)
      (position_embeddings): Embedding(512, 768)
      (LayerNorm): LayerNorm((768,))
      (dropout): Dropout(p=0.1)
    )
    (transformer): Transformer(
      (layer): ModuleList(
        (0-5): 6 x TransformerBlock(
          (attention): MultiHeadSelfAttention(q_lin, k_lin, v_lin, out_lin)
          (sa_layer_norm): LayerNorm((768,))
          (ffn): FFN(lin1: 768→3072, lin2: 3072→768, activation: GELU)
          (output_layer_norm): LayerNorm((768,))
        )
      )
    )
  )
  (pre_classifier): Linear(in_features=768, out_features=768)    ← ⚠️ BERT 没有这一层
  (classifier):     Linear(in_features=768, out_features=6)      ← 6 类
  (dropout):        Dropout(p=0.2)
)
```

**与 10 讲的 `BertForSequenceClassification` 对照，三个差别值得记**：

| | BERT | DistilBERT |
|---|---|---|
| 层数 | 12 层 `(0-11)` | **6 层** `(0-5)` |
| 分类头 | **只有** `classifier(768→num_labels)` | **`pre_classifier(768→768)` + `classifier(768→6)`** 两层 |
| dropout | `p=0.1` | **`p=0.2`**（头更宽，加大正则） |
| **pooler** | 有 `pooler`（10 讲纠结的"两个出口"） | **完全没有 pooler** |

最后一条最关键：**DistilBERT 没有 pooler，它直接取 `last_hidden_state[:, 0]`（即 `[CLS]` 位置的向量）**：

```python
hidden_state  = distilbert_output[0]        # last_hidden_state [B, N, 768]
pooled_output = hidden_state[:, 0]          # ← 直接切第 0 个位置 = [CLS]
pooled_output = self.pre_classifier(pooled_output)
pooled_output = nn.ReLU()(pooled_output)
pooled_output = self.dropout(pooled_output)
logits        = self.classifier(pooled_output)   # [B, 6]
```

> 10 讲那个"`pooler_output` 还是 `last_hidden_state`"的纠结，在 DistilBERT 里**被简化成了"直接取 `[CLS]`"**。理解这一点，你就看懂了"为什么 10 讲要专门讲 pooler"——因为不同架构在"句子级表示怎么拿"这件事上**真的不统一**。

---

## 六、`TrainingArguments` 逐字段拆解

```python
batch_size = 64
logging_steps = len(emotions_encoded['train']) // batch_size     # 16000 // 64 = 250
model_name = f'{model_ckpt}_emotion_ft_0416'                     # distilbert-base-uncased_emotion_ft_0416

training_args = TrainingArguments(
    output_dir=f'/home/whaow/nlp_with_transformers/{model_name}',
    num_train_epochs=4,
    learning_rate=2e-5,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    weight_decay=0.01,
    evaluation_strategy='epoch',
    disable_tqdm=False,
    logging_steps=logging_steps,
    push_to_hub=True,
    log_level='error',
)
```

| 字段 | 值 | 作用 / 为什么是这个值 |
|---|---|---|
| `output_dir` | `.../distilbert-base-uncased_emotion_ft_0416` | 权重、日志、checkpoint 落盘位置（`0416` 是日期，防覆盖） |
| `num_train_epochs` | **4** | 微调只需 **2~5** 轮；轮数一多就过拟合 |
| `learning_rate` | **2e-5** | **微调黄金值**（原论文 2e-5 ~ 5e-5）；预训练是 1e-4，**差 5 倍** |
| `per_device_train_batch_size` | 64 | **每张卡** 64（不是全局！见下） |
| `per_device_eval_batch_size` | 64 | 同上 |
| `weight_decay` | 0.01 | AdamW 的 L2 正则权重 |
| `evaluation_strategy` | `'epoch'` | 每轮结束在 `eval_dataset` 上评估一次（也可 `'steps'`） |
| `logging_steps` | **250** | 每 250 步打一行日志 |
| `disable_tqdm` | `False` | 保留进度条（想看每个 batch 的 loss 就 `True`） |
| `push_to_hub` | `True` | 训完自动推 Hugging Face Hub（§九） |
| `log_level` | `'error'` | 把 HF 的 INFO 唠叨关掉 |

### 6.1 `logging_steps = 16000 // 64 = 250` 的巧思

**一轮的步数 = `len(train) / batch_size`**。所以"每 250 步 log 一次" = **每轮 log 一次**。这样写的好处是**自适应**：你把 `batch_size` 改成 32，它自动变成 500，仍然是"每轮一次"，不用手改。

### 6.2 ⚠️ `per_device_*_batch_size` 的 "per_device"

**它要乘上"可见 GPU 数"**。notebook 跑在 **2 张卡**上：

```text
全局 batch = 64 × 2 = 128
每轮步数   = 16000 / 128 = 125
4 轮总步数 = 500          ← 正好等于训练输出里的 global_step=500
```

**这是本篇最值得做的一次"对账"**：如果只看到 500 就以为是 1000，说明你忘了"多卡把 batch 翻倍"。Trainer 会自动启用 `DataParallel`/`DistributedDataParallel`，**你不需要手写任何并行代码**——但你必须知道它在乘。

### 6.3 真实训练输出 + 逐项对账

```text
TrainOutput(global_step=500, training_loss=0.4075538852214813,
  metrics={'train_runtime': 70.5276,
           'train_samples_per_second': 907.44,
           'train_steps_per_second': 7.089,
           'total_flos': 1.4406e+15,
           'train_loss': 0.4075538852214813,
           'epoch': 4.0})
```

| 字段 | 值 | 怎么来的（都会算 = 真懂） |
|---|---|---|
| `global_step` | **500** | `4 轮 × (16000 / (64×2))` = 4 × 125 ✅ |
| `train_runtime` | **70.5 s** | 2 卡 71 秒训完；单卡约 2 倍 |
| `train_samples_per_second` | **907.4** | `16000 × 4 / 70.53 ≈ 907.4` ✅ |
| `train_steps_per_second` | 7.09 | `500 / 70.53 ≈ 7.09` ✅ |
| `total_flos` | 1.44e15 | 浮点运算总量（估算训练成本） |
| `train_loss` | **0.4076** | **4 轮训练 loss 的平均**（不是最后一轮的值） |

> `train_loss` 是**整个训练过程的平均**——所以它总比你在日志末尾看到的当轮 loss 高。看到日志最后一行 loss 0.12、而 `train_loss` 0.40 时，**不要以为是 bug**。

---

## 七、`Trainer` 三件套 + `compute_metrics`

### 7.1 训练：就一个 `train()`

```python
trainer = Trainer(
    model=model,                                              # ① 已 num_labels=6 的模型
    args=training_args,                                       # ② 超参
    compute_metrics=compute_classification_metrics,           # ③ 评估函数
    train_dataset=emotions_encoded['train'],                  # ④ 训
    eval_dataset=emotions_encoded['validation'],              # ⑤ 验（test 留到最后）
    tokenizer=tokenizer,                                      # ⑥ 给 collator 用
)
trainer.train()
```

| 参数 | 关键点 |
|---|---|
| `model` | **必须已经 `num_labels=6`**，否则最后那层是 2 维，dimension mismatch |
| `compute_metrics` | **不传就只有 loss**，不会有 accuracy/f1 |
| `train_dataset` / `eval_dataset` | eval 用 **validation**；`test` 留到全部调完再看（防止"看着测试集调参"） |
| `tokenizer` | Trainer 用它把 `default_data_collator` 换成 **`DataCollatorWithPadding`** |

**`tokenizer=tokenizer` 到底做了什么？** 这一步很隐蔽：

> 传了 tokenizer，Trainer 就会用 `DataCollatorWithPadding` —— 取一个 batch，**按 batch 内最长样本重新 padding**，并生成对应的 `attention_mask`。**这就是 §4.2 说的"第二层 padding"**。
>
> 于是数据流的每个 step 是：`长 tensor（全局 padding 70）` → `collator 裁/补到本 batch 最长` → `[64, L, ...]` → 模型。
>
> 📌 **版本注意**：较新版本的 transformers 把 `tokenizer=` 改名成了 `processing_class=`，旧的写法会报 deprecation 警告。功能不变。

### 7.2 预测与评估

```python
trainer.predict(emotions_encoded['test'])     # 返回 PredictionOutput
trainer.evaluate()                            # 用 eval_dataset
```

`PredictionOutput` 有三个成员，全部要用到：

| 成员 | 形状 | 用途 |
|---|---|---|
| `predictions` | `[N, 6]` | **原始 logits**（未过 softmax） |
| `label_ids` | `[N]` | 真实标签 |
| `metrics` | dict | 含 `test_loss`、`test_accuracy`、… |

### 7.3 `transformers_utils.py` 的三个函数（原文，很短，逐行读）

```python
from transformers_utils import get_params, compute_classification_metrics, plot_confusion_matrix
```

```python
def get_params(model):
    model_parameters = filter(lambda p: p.requires_grad, model.parameters())
    return sum([np.prod(p.size()) for p in model_parameters])

def model_size(model):
    return sum(t.numel() for t in model.parameters())

def compute_classification_metrics(pred):
    labels = pred.label_ids                    # 真实标签 [N]
    preds  = pred.predictions.argmax(-1)       # logits [N,6] → argmax → 预测标签 [N]
    f1        = f1_score(labels, preds, average="weighted")
    acc       = accuracy_score(labels, preds)
    precision = precision_score(labels, preds, average='macro')
    return {"accuracy": acc, "f1": f1, 'precision': precision}

def plot_confusion_matrix(y_preds, y_true, labels):
    cm   = confusion_matrix(y_true, y_preds, normalize="true")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap="Blues", values_format=".2f", ax=ax, colorbar=False)
```

**五个点必须抠清**：

1. **`get_params` vs `model_size` 只差一个 `filter`**：前者是**可训练**参数，后者是**全部**参数。微调时（全都在训）两者相等；一旦你 freeze 了 backbone（04 讲），`get_params` 会明显变小——**这正是"验证冻结有没有生效"的最快方法**。
2. **`compute_metrics` 拿到的是 raw logits**：`argmax(-1)` 这一步**必须自己做**。Trainer 不会替你 argmax。
3. **`argmax(-1)` 的 `-1`**：在最后一维（6 类）上取最大值下标。对 `[N, 6]` 就是"每行选一个类"。
4. **三个指标的分工**（§二 2.2 的伏笔在这里收了）：

| 指标 | 平均方式 | 偏向 |
|---|---|---|
| `accuracy` | 全部样本 | **多数类主导** |
| `f1` | `weighted`（按类样本数加权） | 同样偏向多数类 |
| `precision` | **`macro`（每类等权）** | **能暴露小类被忽略** |

> 一个 6 类不均衡任务（9.4 倍差距）里，**只看 accuracy 会被骗**。加一个 `macro` 指标是最便宜的保险。

5. **⚠️ `test_` 前缀是"假的"**（最容易误读的一处）：

```text
test_loss 0.17137 / test_accuracy 0.9325 / test_f1 0.9327 / test_precision 0.9028
```

**这组数字是在 `validation`（2000 条）上算的**，不是 test split！因为 `trainer.predict(emotions_encoded['validation'])` 之后，Trainer 返回的 metrics 会**无条件**加 `test_` 前缀（框架里的固定命名，改不了）。

> **记住**：`test_*` 只是 Trainer 的字段名，**跟 split 名字无关**。想知道到底在哪份数据上算的，回去看你传了哪个 dataset。

## 八、结果分析：不止于"93%"

准确率只是**一个数**，它不告诉你"错在哪、为什么错"。这一章做三件事：看**混淆矩阵**、按 **loss 排序**找出最可疑的样本、统计**错误都堆在哪些类**。

### 8.1 混淆矩阵：把 accuracy 拆成 6×6

```python
preds_output = trainer.predict(emotions_encoded["validation"])
y_preds = np.argmax(preds_output.predictions, axis=-1)   # logits [N,6] → 预测标签 [N]
y_true  = emotions_encoded['validation']['label']        # 真实标签 [N]

from transformers_utils import plot_confusion_matrix
plot_confusion_matrix(y_preds, y_true, labels)
```

（notebook 里对 `validation` 画了一张，随后又对 `test` 画了一张——两次流程完全一样，只是换了 dataset。）

`plot_confusion_matrix` 的关键一行：

```python
cm = confusion_matrix(y_true, y_preds, normalize="true")   # ← 按"真实类"归一化
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(cmap="Blues", values_format=".2f", ax=ax, colorbar=False)
```

**`normalize="true"` 的方向很关键**（反复考）：

| 参数 | 归一化方向 | 第 (i, j) 格的含义 | 对角线读作 |
|---|---|---|---|
| `normalize="true"` | 按 `y_true` | 真实是第 i 类里，被预测成第 j 类的**比例** | **召回率（recall）** |
| `normalize="pred"` | 按预测 | 预测成第 j 类里，真实其实是第 i 类的比例 | **精确率（precision）** |
| `normalize=None` | 不归一化 | 原始**样本数** | 正确样本数 |

> notebook 用 `normalize="true"`，所以**每一行的和是 1**：对角线 = 该类召回率，非对角线 = 该类"漏到别的类"去的比例。

怎么读这张图（方法比数字重要）：

1. **先看对角线**：越接近 1 越好。
2. **再看每一行的"最大误解"**：某类最常被误判成谁？（例：`joy` 与 `love` 互相串——语义本来就重叠）
3. **最后看列**：某一列非对角偏大 = 这个类在"吸金"（把别的类吸成自己），这就是 precision 偏低的来源。

### 8.2 逐样本 loss：让模型说出"哪条最可疑"

混淆矩阵是"类的视角"，接下来换成"样本的视角"：给 `validation` 里每条样本算一个 loss，**按 loss 从大到小排**。

```python
def forward_pass_with_label(batch):
    inputs = {k: v.to(device) for k, v in batch.items()
              if k in tokenizer.model_input_names}    # ① 只挑模型认的字段
    with torch.no_grad():                              # ② 纯推理，不建图
        output = model(**inputs)
        pred_label = torch.argmax(output.logits, axis=-1)
        loss = cross_entropy(output.logits, batch["label"].to(device),
                             reduction="none")         # ③ 关键：不平均，每样本一个
    return {"loss": loss.cpu().numpy(),                # ④ 回 CPU，才能塞回 Dataset
            "predicted_label": pred_label.cpu().numpy()}
```

然后：

```python
emotions_encoded["validation"] = emotions_encoded["validation"].map(
    forward_pass_with_label, batched=True, batch_size=16)   # map 批量跑，自动拼列
```

**四个必须看清的点**：

1. **`k in tokenizer.model_input_names`**：这是 §四讲过的——DistilBERT 只有 `input_ids`/`attention_mask`，`label` 不能喂模型，所以先过滤；`label` 单独取出来当 loss 的 target。
2. **`reduction="none"`**：默认是 `"mean"`（一个 batch 一个标量）。这里要**每个样本各自的 loss**，所以设 `none`，返回形状 `[B]`。
3. **`torch.no_grad()`**：分析阶段不训练，省显存、也避免 `.numpy()` 报错（§04 讲过）。
4. **`map(..., batched=True)` 输出会自动对齐**：返回的 `{"loss": [...], "predicted_label": [...]}` 会被**按顺序拼成同长度的新列**加回 Dataset。所以之后 `emotions_encoded['validation']['loss']` 能直接取。

### 8.3 从排序里读出两件事

```python
valid_df.sort_values('loss', ascending=False).head(10)
```

这张表最有价值的是 **loss 最高的那 10 条**——它们通常是两类：

| 类型 | 表现 | 例 |
|---|---|---|
| **真·难样本 / 标注存疑** | 人看了也觉得"标错了吧" | `i feel badly about reneging on my commitment...`，标 `love`、模型猜 `sadness`，loss **6.04** |
| **标签本身的模糊性** | 句子确实同时像两个类 | `joy`/`love`、`fear`/`surprise` 互串 |

notebook 专门验了第一条：

```python
valid_df.iloc[882].text
# 'i feel badly about reneging on my commitment to bring donuts to the faithful at holy family catholic church in columbus ohio'
```

这条被标成 `love`、模型预测 `sadness`、loss 高达 6.04。**"爽约没送成甜甜圈"到底是不是 love？** 模型觉得不是——这个"错"更可能是**数据集标注本身的问题**。这就是"用 loss 找脏数据"的标准做法。

反过来，`sort_values('loss', ascending=True).head(20)` 是**模型最自信**的 20 条（loss ≈ 0.008，几乎 100% 确信），清一色 `sadness`/`joy`——两类样本最多、特征最典型。

> **一句话**：`ascending=False` 找**脏数据/难样本**，`ascending=True` 找**最典型的代表**。loss 不只是训练指标，还是个**数据质检工具**。

### 8.4 135 条错误都堆在哪些类？

```python
valid_df[valid_df['label'] != valid_df['pred_label']]        # 2000 条里错 135 条
1 - 135/2000                                                # → 0.9325，正好是 test_accuracy
```

```python
valid_df[valid_df['label'] != valid_df['pred_label']].label.value_counts()
```

```text
joy         44
fear        25
anger       19
love        17
sadness     16
surprise    14
```

**两件事同时成立**：

- `joy` 错误最多（44 条）——但它是**样本最多的类**（§二：joy 5362 条 vs surprise 572 条），错误多是因为"基数大"，不一定是"学得差"。
- `surprise` 错误最少（14 条）——但它**基数最小**，`14/572 ≈ 2.4%` 的真实错误率其实**最高**。

> 这正是 §7.3 那份伏笔的收口：**只看 accuracy 会以为各类都挺好，配上 `value_counts` + `macro precision` 才发现小类最差**。在 9.4 倍不均衡的数据上，永远别只看一个全局数。

---

## 九、上线：`push_to_hub` → `pipeline`

### 9.1 一行发布

```python
trainer.push_to_hub(commit_message="Training completed!")
```

它做的事（= 训练完你还得手动做的那些）：

1. 把模型权重 + `config.json` + `tokenizer` 文件写进 `output_dir`（即 `distilbert-base-uncased_emotion_ft_0416/`）；
2. 自动生成一张 **model card**（含超参、指标）；
3. `git add/commit` 后 **push 到你的 Hugging Face 仓库**。

> 前置条件：`training_args` 里必须 `push_to_hub=True`，且已经 `notebook_login()`（notebook §五 开头那步），否则这一步会报"没有可推送的仓库"。

### 9.2 `pipeline` 一行推理

```python
from transformers import pipeline
model_id = "lanchunhui/distilbert-base-uncased_emotion_ft_0416"
classifier = pipeline("text-classification", model=model_id)

custom_tweet = "I saw a movie today and it suck."
preds = classifier(custom_tweet, return_all_scores=True)
```

输出：

```text
[[{'label': 'LABEL_0', 'score': 0.2951},
  {'label': 'LABEL_1', 'score': 0.0896},
  {'label': 'LABEL_2', 'score': 0.0177},
  {'label': 'LABEL_3', 'score': 0.4004},
  {'label': 'LABEL_4', 'score': 0.1750},
  {'label': 'LABEL_5', 'score': 0.0221}]]
```

**⚠️ 这是全篇最容易懵的一处：标签怎么变成 `LABEL_0` 了？**

| 问题 | 答案 |
|---|---|
| `LABEL_0~5` 是什么？ | 分类头**默认的** id2label（下载权重时只知"6 个类"、不知"类名"） |
| 怎么知道 `LABEL_3` 是哪个情绪？ | 回去对 `labels` 列表的**下标**——`LABEL_3 = anger` |
| 为什么会这样？ | `from_pretrained(model_ckpt, num_labels=6)` 只给了**数量**、没给**名字**；名字只是展示问题，不影响预测 |

所以 "it suck" 的最高分是 `LABEL_3 = anger`（0.40），其次 `LABEL_0 = sadness`（0.30）——模型判它**偏愤怒**，符合直觉。

> **想让它输出真名？** 训练时用 `AutoConfig(id2label=..., label2id=...)` 设置，或推 hub 时补进 `config.json`；否则一律是 `LABEL_i`。

绘制概率柱（注意这里靠**我们的 `labels`** 才能对上名字）：

```python
preds_df = pd.DataFrame(preds[0])
plt.bar(labels, 100 * preds_df["score"], color='C0')
plt.title(f'"{custom_tweet}"')
plt.ylabel("Class probability (%)")
```

### 9.3 两种"用起来"的方式

| 方式 | 代码 | 适合 | 坑 |
|---|---|---|---|
| **Trainer** | `trainer.predict(ds)` | 批量评测、算指标、拿 logits | 还得自己 `argmax`、自己组织 dataset |
| **pipeline** | `pipeline("text-classification", model=...)` | 单条/少量推理、demo、服务 | 返回 `LABEL_i`；已 softmax，不需要再算 |

两者**模型完全一样**，只是"外壳"不同：Trainer 是训练/评测外壳，pipeline 是**推理服务外壳**（自动做 tokenize → 前向 → softmax → 标签映射）。

---

## 十、常见误区（10 个）

1. **误区：`test_accuracy` 就是在 `test` split 上算的。**
   不是。它是在你传给 `trainer.predict(...)` 的那个 dataset 上算的——notebook 传的是 **validation**。`test_` 只是 Trainer 的固定字段前缀（§7.3）。**判断"在哪算的"只看你传了谁。**
2. **误区：`num_labels=6` 会自动带上类名。**
   不会。它只改分类头大小，`LABEL_0..5` 依旧。类名要靠 `id2label` 显式提供。
3. **误区：`reduction="none"` 让 loss 变小了。**
   不。"none" 只是**不聚合**，返回每样本一个 loss；对总体 loss 无影响（求和/平均后一样）。
4. **误区：混淆矩阵 `normalize="true"` 的对角线是 precision。**
   不是，是 **recall**。`normalize="pred"` 才是 precision（§8.1 表）。
5. **误区：`label != pred_label` 就是模型错了。**
   不一定。§8.3 的 `iloc[882]` 表明**可能是标注本身有问题**。accuracy 的上限被标注质量封顶。
6. **误区：`map(batched=True)` 里的自定义函数必须返回原 dataset 的全部列。**
   不必。只返回新列即可，HF 会按顺序拼回去（前提：`batch_size` 与产出顺序一致）。
7. **误区：多卡一定更快。**
   不一定。多卡要**同步等待最慢的卡**（notebook §六 原文警告）：快卡得等慢卡，可能反而更慢。
8. **误区：`train_loss=0.4076` 是最后一轮的 loss。**
   不是，是**全程平均**——所以它比日志末尾那轮高（§六 表）。
9. **误区：`get_params` 和 `model_size` 是一回事。**
   差一个 `filter(requires_grad)`。全量微调时相等；一旦冻结（§04），`get_params` 会变小。
10. **误区：`push_to_hub` 会把数据集也传上去。**
    不会。只传模型 + config + tokenizer + model card，不碰你的 dataset。

---

## 十一、记忆卡

- **文本分类 = sequence classification**：backbone + `[CLS]`/首 token 之上的线性头
- **三段数据**：train 微调 / validation 调参+看混淆 / test 只在最后看一眼
- **两层 padding**：`map(batched=True, batch_size=None)` 全局对齐 → `DataCollatorWithPadding` 按 batch 再裁
- **`tokenizer.model_input_names`**：DistilBERT 只 `input_ids`+`attention_mask`（没有 `token_type_ids`）
- **`TrainingArguments` 五件套**：`num_train_epochs=4`、`lr=2e-5`、`batch=64`、`weight_decay=0.01`、`logging_steps=len(train)//batch`
- **Trainer 三件套**：`model(已 num_labels)` + `args` + `compute_metrics`；`tokenizer=` 负责换 collator
- **`compute_metrics` 收 logits**：`argmax(-1)` 自己做；`accuracy`/`f1(weighted)`/`precision(macro)` 三个一起看
- **`test_` 前缀 ≠ test split**，只代表"Trainer 返回的评测字段"
- **混淆矩阵**：`normalize="true"` → 行和为 1 → 对角线 = 召回率
- **loss 排序**：降序找脏数据，升序找典型样本；`reduction="none"` 是钥匙
- **上线两步**：`trainer.push_to_hub()` → `pipeline(...)`；标签默认 `LABEL_i`

---

## 十二、自测（先答再看）

1. `preds_output = trainer.predict(emotions_encoded["validation"])` 之后 `metrics['test_accuracy']` 是 0.9325。这 0.9325 是在**哪份数据**上算的？为什么字段叫 `test_`？
2. `metrics` 里给的是 `test_precision`（`average='macro'`）。为什么在 `emotion` 这个数据集上，它比 `test_accuracy` 更值得盯？
3. §8.2 的 `forward_pass_with_label` 里，如果把 `reduction="none"` 改成默认的 `"mean"`，返回的 `loss` 形状会变成什么？后面 `sort_values('loss')` 还能不能逐样本排序？
4. `plot_confusion_matrix(y_preds, y_true, labels)` 的**调用方**参数顺序是 `(y_preds, y_true)`，而 `sklearn` 的 `confusion_matrix(y_true, y_preds)` 反过来。如果调用方把两个数组传反，`normalize="true"` 的图会变成什么？
5. `pipeline` 输出 `LABEL_3` 得 0.40、`LABEL_0` 得 0.295。结合 `labels = ['sadness','joy','love','anger','fear','surprise']`，"I saw a movie today and it suck." 被判成什么情绪？
6. `trainer.push_to_hub()` 之前，`TrainingArguments` 里必须有的设置、以及必须完成的一个动作，各是什么？

<details>
<summary>参考答案</summary>

1. 在 **validation**（2000 条）上算的。因为 `predict` 的入参就是 `emotions_encoded["validation"]`。`test_` 是 Trainer 给评测指标统一加的**固定前缀**，跟 split 名字无关。
2. `emotion` 六类严重不均衡（joy 5362 条 vs surprise 572 条，9.4 倍）。`accuracy`/`f1(weighted)` 都被多数类主导，会"掩盖"小类；`precision(macro)` 每类等权，能**暴露 surprise 等小类学得差**（§8.4）。
3. `"mean"` 会把整个 batch 聚成一个标量，返回的 `loss` 变成**单个标量**（而不是 `[B]` 向量），无法与 2000 条样本一一对应，逐样本排序就失效了。
4. `confusion_matrix` 的**第一个**位置参数才是 `y_true`。若把两个数组传反，`normalize="true"` 就会**变成按预测类归一化**，对角线从"召回率"变成"精确率"，每行含义整个错位。
5. `LABEL_3 = anger`（0.40）最高，`LABEL_0 = sadness`（0.295）次之 → 判成 **anger（愤怒）**。不是 `joy`，因为 `suck`（糟糕）与"看电影很开心"相悖，模型的语境表示指向负面情绪。
6. ① `TrainingArguments(..., push_to_hub=True)`；② 事先 `notebook_login()`（或 `huggingface-cli login`）完成鉴权。

</details>

---

## 十三、费曼三连问

1. **一句话**：文本分类就是"在预训练 backbone 的 `[CLS]`/首 token 表示上接一个 6 类的线性头，用带标签的评论数据微调"；最后得到的不再是"更好的语言模型"，而是一个**情感判别器**。
2. **说形状**：给定 batch `B=64`、全局 padding 到 `L=70`，写出从 `tokenizer` → `DataCollatorWithPadding` → `model` → `logits` → `loss` 的每一步张量形状（含 `attention_mask`），并说明 `num_labels` 在哪一步把最后的维度定为 6。
3. **讲出去**：向只用过 `sklearn` 做文本分类的人解释——为什么这里要"两层 padding"、为什么评估要同时看 `accuracy` 与 `macro precision`、以及为什么"loss 最高的样本"值得先怀疑标注而不是模型。

---

## 十四、与前面笔记的连接

- **接 11**：11 讲的是**预训练任务 MLM**——在无标签语料上"自己挖空当标签"；本篇是**下游微调**——在 `emotion` 上用人工标签训练。backbone 复用，任务换成分类。
- **接 10**：10 给了 head 家族的"族谱"（`ForSequenceClassification` 正在其中）；本篇把它**真正拿去训练**，并补充了 DistilBERT **没有 pooler**、直接取 `last_hidden_state[:, 0]` 的红旗。
- **接 07**：07 讲模型输出有哪些"出口"（`last_hidden_state`/`pooler_output`/`hidden_states`）；本篇的 `output.logits` 就是"最后一个出口"在分类任务下的形态，`forward_pass_with_label` 里的 `output.logits` 与 07 的图一一对应。
- **接 04**：`torch.no_grad()`、`requires_grad`（`get_params` 的 `filter`）都来自 04；本篇把"冻结/不冻结"落成了"参数量对比"这个可观测动作。
- **接 02 / 06**：`tokenizer.model_input_names`、`token_type_ids` 的有无、subword 切分，都在 02/06 铺过；本集是它们的**下游复用**。
- **→ 下一阶段**：本集是「BERT、T5、GPT」子系列"微调"的第一集。往后进入 **T5** 家族（text-to-text 统一框架）与 **GPT** 系列（自回归 / 生成式），你会发现同一个 `Trainer`、同样的 `DataCollatorWithPadding` 被反复复用——**先把这一集的数据管线与 Trainer 流程吃透，后面几集几乎就是换模型、换 dataset**。

---

*12 完。跟着跑一遍 notebook：**重点盯 §四的 `set_format('torch')` 与两层 padding、§六的 `logging_steps` 对账、§7.3 的 `test_` 前缀骗局、以及 §8.3 的 `reduction="none"` 逐样本 loss**——这四处跑通，"微调一个分类模型"就真正落地了。*
