# 03. BERT 模型结构与参数（掀开引擎盖）

> 配套 notebook：`bilibili_vlogs/fine_tune/bert/tutorials/00_bert_model_architecture_params.ipynb`
> 目标读者：对 AI / NLP 零基础。本篇是 [01_tokennizer_sentiment_analysis.md](./01_tokennizer_sentiment_analysis.md) 和 [02_tokenizer_encode_plus_token_type_ids.md](./02_tokenizer_encode_plus_token_type_ids.md) 的递进——01 讲 tokenizer、02 讲 BERT 预训练游戏（MLM/NSP），本篇把 BERT 的「身体结构」拆开看，并统计它有多少「可调旋钮（参数）」。
> 本机环境提示：想真跑需要装 `transformers` + `torch`（本机尚未安装 Python）；最省事用 **Google Colab** 在线运行，免安装。

---

## 一、这个 notebook 在做什么（一句话）

把 `bert-base-uncased` 这个真实模型**加载进来、打印内部结构**，并**统计总参数**。相当于给车掀开引擎盖，看有哪些部件、各占多少。

---

## 二、加载时的「警告」——其实是重要知识点

```python
model     = BertModel.from_pretrained('bert-base-uncased')                     # 只要编码器
cls_model = BertForSequenceClassification.from_pretrained('bert-base-uncased') # 编码器 + 分类头
```

运行时警告：`'cls.predictions...'`、`'cls.seq_relationship...'` 这些权重**没被用上**。

**这正好接 02 的 MLM / NSP**：
- `cls.predictions` = **MLM 完形填空** 的「填空头」
- `cls.seq_relationship` = **NSP 下一句预测** 的「判断头」

`bert-base-uncased` 文件里存的是**完整预训练模型**，这俩头都在。但加载 `BertModel`（只要编码器主体）或 `BertForSequenceClassification`（只要编码器 + 分类头）时，这俩预训练头用不上，被丢弃——**警告不是出错**。

> 警告在说：BERT 当学生时练过的两套游戏（MLM/NSP），现在上班用不上了。

---

## 三、BERT 的「身体结构」：三大部件

```
BERT
├── embeddings（嵌入层）：把每个 token 变成 768 维向量
│   ├── word_embeddings        词向量（词典 30522 个词，每个 768 数）
│   ├── position_embeddings    位置向量（第 0~511 位，每个 768 数）
│   └── token_type_embeddings 句子标签向量（0 或 1，每个 768 数）★接 02
├── encoder（编码器）：12 个相同「层」叠起来，是真正「思考」的地方
│   └── (0)~(11) 每层：
│       ├── self-attention（自注意力）：Query/Key/Value 三个线性层（kqv）
│       └── feed forward（前馈）：先扩 3072，再压回 768
└── pooler（池化层）：只对 [CLS] 再做一次变换，给分类任务用
```

### 3.1 反复出现的「768」是什么

BERT 把每个词表示成 **768 个小数排成一列**的向量（给每个词一个 768 维「特征指纹」）。

三个 embedding **逐位相加**（同位置 768 个数相加）：
- **词向量**：这个词本身长什么样
- **位置向量**：它在句子第几个位置（"猫追狗" vs "狗追猫" 位置不同）
- **句子标签向量**：它属于第几句（就是 02 的 `token_type_ids=0/1`！）★

三者相加得每个 token 的最终 768 维输入向量。

> **⚠️ 易混淆点：`token_type_ids` 只有 0/1，向量化会很单一吗？**
>
> 不会。要分清两层：
> 1. **`0` 和 `1` 是「索引」不是「数值」**。`token_type_embeddings` 是 `Embedding(2, 768)`——一张只有 2 行的查找表，第 0 行、第 1 行各是一个 768 维**被训练出来的向量**。id=0 查第 0 行，id=1 查第 1 行。
> 2. **每张向量本身是满满 768 个数、且模型学出来的**，例如：
>    ```
>    row0（句A标记）: [0.13, -0.87, 0.42, ..., 0.05]   ← 768 个数
>    row1（句B标记）: [-0.31, 0.55, -0.19, ..., 0.91]  ← 768 个数
>    ```
> 虽然「只有 2 种取值」，但每种都是高维富向量。BERT 处理的句子对最多就「句 A + 句 B」，**只需 2 个标记就够**，不需要 100 种；它要的是「稳定告诉模型每个词属于哪句」，且这个 768 维标记会加到每个 token 上、**贯穿全部 12 层**。
>
> 一句话：`0/1` 少是因为只需区分两句；但每个标记是 768 维富向量，不是单调的 0/1 数字。

### 3.2 encoder 的 12 层，每层干两件事

**自注意力（self-attention）=「每个词看一眼上下文里其他词」**。对每个词造 3 个向量：

| 向量 | 名字 | 含义（类比） |
|---|---|---|
| **Q** Query | 查询 | 「我在找什么信息」 |
| **K** Key | 键 | 「我这里有什么信息（供别人查）」 |
| **V** Value | 值 | 「我实际能贡献的内容」 |

实现上 Q/K/V 就是三个 `Linear(768→768)`：把每个 token 的 768 维输入用三套权重分别变换。

「看一眼」的过程：
1. 拿「我」的 Q，和**所有词**的 K 做点积 → 「我该关注每个词多少」的原始分数；
2. 分数 softmax 归一化成权重（加起来=1）；
3. 用权重把**所有词**的 V **加权求和**，作为「我」这一轮的新表示。

> 直觉：处理 "bad" 时，它的 Q 会和 "not" 的 K 高度匹配（"not bad" 是固定搭配），于是 "bad" 的新向量里融进 "not" 的信息——这就是「上下文」被注入的方式。它同时看左右，所以 BERT 是**双向**的（对应 02 的 BERT 双向 vs GPT 单向）。

**前馈（feed forward）=「每个词自己再想想」**。注意力让词与词通气后，每个位置独立过一遍小网络：
```
768 → 3072（扩 4 倍，配 GELU 激活）→ 768（压回来）
```
`intermediate: Linear(768→3072)` + `output: Linear(3072→768)` 就是这两步。扩到 3072 是给每个词更大「思考容量」加工上下文，再压回 768 保维度一致。每层还有 `LayerNorm`（用 **mean/std** 归一化，呼应之前学的 mean/std）和残差连接（输入加到输出，防深层信息丢失）。

**为什么叠 12 层**：逐层提炼——第 1 层学「词与邻近词关系」，越深越学「句法、指代、语义角色」。12 层叠起，表示从「表面词义」到「深层语义」。这 12 层在 MLM/NSP 预训练时已被教得「会提炼语义」，所以下游只要接个小头就能用。

### 3.3 pooler 很小

只对 `[CLS]`（句首总结位，01 见过）再过 `Linear(768→768) + Tanh`，给分类任务用。占全部参数 **0.5%**。`[CLS]` 在预训练时被设计成「整句总结位」（和所有词都做了注意力，天然汇总全句）。

---

## 四、BertModel vs BertForSequenceClassification（接 01！）

- **`BertModel`**：只有「编码器 + pooler」，输出每个 token 的 768 维向量（一堆数字）。
- **`BertForSequenceClassification`**：在 `BertModel` 外再套一层 `classifier`（`Linear(768→2)`）。

打印最后一行：
```
(classifier): Linear(in_features=768, out_features=2, bias=True)
```
这个 `768→2` 就是**两盏灯（负面分、正面分）的来源**——正是 01 情感分析的产出处！

即：01 用的 `distilbert...sst-2-english`（带情感分类头）和这里 `BertForSequenceClassification`（带 `768→2` 分类头）是**同一类结构**。01 没看内部，现在看到了——情感判断就是 encoder 后挂个小分类头做出来的。

加载 `BertForSequenceClassification` 时警告还说：`classifier.weight/bias` 是**新随机初始化**的、「你应该在下游任务上 TRAIN 它」——因为原 BERT 预训练时没练过「正面/负面」这个具体任务，分类头得自己（或别人）微调。

---

## 五、参数统计：BERT 有多大

```
总参数 total_params        = 109,482,240  ≈ 1.1 亿（109M）
可训练参数 total_learnable = 同样 109M（全部可训练）
```

「参数」= 模型里所有可调小数旋钮。BERT base 约 **1.1 亿**个。按部件拆分占比：

| 部件 | 占比 | 说明 |
|---|---|---|
| **encoder（编码器）** | **77.7%** | 真正「思考」主体，绝大多数参数在这 |
| **embeddings（嵌入）** | 21.8% | 主要是 30522×768 的大词表 |
| **pooler（池化）** | 0.5% | 很小 |

> 直观：BERT 的「脑子」（encoder）占近八成参数；决定「正面/负面」的分类头只有 2 个矩阵（768×2），相对整个模型微不足道——但正是这小小一层，让通用 BERT 变成情感分类器。

---

## 六、完整流水线（带维度走一遍）

以 01 那句 `"today is not that bad"`（7 个 token）为例：

```
① 文本: "today is not that bad"
        ↓ tokenizer
② 三个数组（长度都=7）:
   input_ids:        [101, 2651, 2003, 2025, 2008, 2919, 102]
   token_type_ids:   [  0,    0,    0,    0,    0,    0,    0]   ← 单句全 0
   attention_mask:   [  1,    1,    1,    1,    1,    1,    1]
        ↓ embeddings（查 3 张表各取 768 维，逐位相加）
③ 7×768 矩阵（7 个 token，每个 768 维向量）
   → LayerNorm（mean/std 归一化）+ dropout
        ↓ 12 层 encoder
④ 仍是 7×768，但每个向量已被「看遍全句」提炼
   第1层 7×768 → 第2层 → ... → 第12层 7×768
        ↓ pooler（只取 [CLS] 位置）
⑤ [CLS] 的 768 维 → Linear(768→768)+Tanh → 768 维
        ↓ classifier 头
⑥ Linear(768→2) → 2 个数: [负面分, 正面分]   ← 「两盏灯」的 logits
        ↓ softmax
⑦ [0.0008, 0.99915] → 99.9% 正面 = POSITIVE
```

**关键认知**：数据形状始终是「token 数 × 768」。token 数随句子变（padding 补齐），768 永远不变——这是 BERT 的「隐藏维度」。

---

## 七、一句话核心思想（本篇重点）

> **整句话 → 同一串数据（encoder 产出的共享表示）→ 不同的「头」对它做不同运算 → 不同答案。**

更准确：那串数据是「7 个 token × 768 维」矩阵；分类头取 `[CLS]` 行做 `768→2`，MLM 头取 `[MASK]` 行做 `768→30522`，NSP 头取 `[CLS]` 行做 `768→2`。**身体（encoder）复用，头按需换**——这就是现代 NLP「预训练 + 微调」范式的根本。

### 什么是「头」（head）

- 模型分两截：**主干 / backbone / encoder**（把输入变成「丰富的内部表示」）+ **头 / head**（把内部表示翻译成某个具体任务的答案）。
- 「头」= 叠在模型**头顶**做最终输出的那一层/几层。同一身体换不同头干不同活：
  ```
  填空头  ──→ 预测被抠掉的词（MLM）
  判断头  ──→ 判断两句是否相邻（NSP）
  分类头  ──→ 判断正面/负面（01 的情感分析）
  ```
- 「内部表示」是**任务无关**的 768 维压缩包（人看不懂）；「头」是便宜的小翻译官，把它变成任务需要的答案格式。换头 = 换任务。

---

## 八、和你已学知识的三条连接

1. **接 02（MLM/NSP）**：加载警告里 `cls.predictions` / `cls.seq_relationship` 被丢弃，正是 02 那两个预训练头的「尸体」——证明 BERT 出厂确实带着 MLM/NSP 装备。
2. **接 01（tokenizer + 情感分析）**：`token_type_embeddings` 是 02 的 `token_type_ids` 向量化；`classifier(768→2)` 是 01 那「两盏灯」的产生处。链路：**文本 → tokenizer(含token_type) → embeddings → 12层encoder → pooler → classifier → 两盏灯**。
3. **接之前的 mean/std**：每层 `LayerNorm` 用 mean/std 归一化；encoder 是 1.1 亿参数、77.7% 在 encoder——后面学训练（反向传播、梯度）就是调这 1.1 亿个旋钮。

---

## 九、下一步可以往哪走

- **看三大架构对比**：本目录后续讲 BERT（双向+MLM）、GPT（单向自回归）、T5（文本到文本）的异同。
- **看反向传播 / 梯度**：`learn_torch/grad/03_computation_graph.ipynb`——理解这 1.1 亿个旋钮是怎么「被训练出来」的。
- **看微调实战**：本仓库 `fine_tune/bert/` 下其他 notebook——如何用你自己的数据训那个 `classifier` 头（对应 03 警告里的「你应该 TRAIN 它」）。
- **深入 tokenizer 本身**：BPE 子词切分，及与 **Re-tokenize** 问题的串联。
