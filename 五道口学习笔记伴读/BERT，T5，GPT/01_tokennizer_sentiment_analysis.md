# 01. Tokenizer 与情感分析入门（从零开始）

> 配套 notebook：`bilibili_vlogs/hugface/01_tokenizer_sentiment_analysis.ipynb`
> 目标读者：对 AI / NLP 零基础。跟着这个 notebook，理解「把人话变成机器码 + 让 AI 判断一句话是夸还是骂」的完整流程。
> 本机环境提示：若想真跑这份代码，需要装 `transformers` + `torch`（本机尚未安装 Python）；最省事的办法是用 **Google Colab** 在线运行，免安装。

---

## 一、这个 notebook 在做什么（一句话）

教你：**怎么把一句英文变成计算机能算的数字，再喂给一个现成的 AI，让它判断这句话是「正面/夸」还是「负面/骂」。**

这就是所谓的**情感分析（sentiment analysis）**——NLP 里最经典的任务之一。

---

## 二、先认几个「大词」（背景知识）

| 词 | 白话解释 |
|---|---|
| **NLP** | 自然语言处理（Natural Language Processing）：让计算机理解和处理人类语言的技术 |
| **情感分析** | 判断一段文字是正面还是负面，比如影评、商品评价、微博情绪 |
| **Hugging Face（HF）** | 一个 AI 模型的「应用商店」，里面有成千上万个训练好的模型可直接下载用，不用自己从头训练 |
| **Transformer / BERT** | 现在所有语言 AI（包括 ChatGPT）的共同祖先架构。BERT 是 Google 2018 年提出的代表模型 |
| **DistilBERT** | BERT 的「轻量蒸馏版」（更小、更快）。注意 **Distil = Distillation（知识蒸馏）**——用大模型教小模型，正是论文里常见的「蒸馏」概念 |
| **tokenizer（分词器）** | 本 notebook 的绝对主角：把文字翻译成数字的工具（详见第三步） |

---

## 三、第一步：tokenizer —— 把「人话」翻译成「机器码」

### 3.1 核心矛盾

> 计算机只认识数字，不认识字。

所以，在把一句话喂给模型之前，必须先用 tokenizer 把它翻译成数字序列。tokenizer 就是干这个的「翻译官」。

### 3.2 翻译流程（以 `"today is not that bad"` 为例）

notebook 里准备了三句测试文本：
```python
test_sentences = ['today is not that bad', 'today is so bad', 'so good']
model_name = 'distilbert-base-uncased-finetuned-sst-2-english'
```

**① 切词（tokenize）**：把句子拆成小块
```
[today] [is] [not] [that] [bad]
```

**② 查字典（vocab）变编号**：每个词对应一个 ID（notebook 真实输出）
```
[101, 2651, 2003, 2025, 2008, 2919, 102]
```
- `101` = `[CLS]`（「开始」标志，分类任务专用）
- `2651` = today，`2003` = is，`2025` = not，`2008` = that，`2919` = bad
- `102` = `[SEP]`（「结束」标志）

> **类比**：就像把中文地址翻译成快递单号。快递公司（模型）不认识「北京市朝阳区…」，只认单号 `101-2651-…`。vocab 就是那本「单词 ↔ 编号」对照表。

notebook 里演示了这几组互转（建议自己跑一遍体会）：
```python
tokenizer("today is not that bad")                      # → input_ids + attention_mask
tokenizer.encode("today is not that bad")               # → [101, 2651, 2003, 2025, 2008, 2919, 102]
tokenizer.decode([101, 2651, 2003, 2025, 2008, 2919, 102])  # → '[CLS] today is not that bad [SEP]'
```

### 3.3 几个特殊符号

notebook 用 `special_tokens_map` 列出了模型字典里预留的「特殊记号」：

| 符号 | 含义 | 作用 |
|---|---|---|
| `[CLS]` | 开头标志 | 分类任务把整句话的「总结信息」放在这里 |
| `[SEP]` | 分隔符 | 两句话之间 / 句子结尾的分隔 |
| `[PAD]` | 填充（padding） | 把短句补到和长句一样长（编号是 `0`） |
| `[UNK]` | 不认识的字 | 字典里查不到的生僻词 |
| `[MASK]` | 挖空 | BERT 做「完形填空」游戏时用的占位符 |

### 3.4 批量处理时的 padding + attention_mask（最容易绕晕的一点）

计算机要**一次性**算很多句话，但每句话长短不一，必须补齐成一样长。notebook 真实输出：

```
句1 "today is not that bad" → input_ids: [101, 2651, 2003, 2025, 2008, 2919, 102]
句2 "today is so bad"      → input_ids: [101, 2651, 2003, 2061, 2919, 102,   0 ]
                                                    ↑ 短了，用 0 ([PAD]) 补到第 7 格
attention_mask: [1, 1, 1, 1, 1, 1, 0]   ← 1=真内容，0=凑数的 padding，模型要忽略
```

> **类比**：考试卷子每题留一样宽的空位，短答案后面用空白补。`attention_mask` 就是告诉「阅卷老师」（模型）：哪些空位是真写的、哪些是空白，别给空白打分。

---

## 四、第二步：把数字喂给模型，让它「读」

### 4.1 模型是什么

```python
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

`model_name = distilbert-base-uncased-finetuned-sst-2-english`，意思是：一个 **DistilBERT**，已经在 **SST-2**（影评数据集）上微调好，专门干「判断正负情感」这一件事。

`model.config` 显示了它的「大脑结构」：6 层、12 个注意力头、词汇表 30522 个词，并且规定了 `0 = NEGATIVE（负面）`、`1 = POSITIVE（正面）`。

### 4.2 logits → softmax → argmax（三步出结论）

```python
batch_input = tokenizer(test_sentences, truncation=True, padding=True, return_tensors='pt')
with torch.no_grad():
    outputs = model(**batch_input)              # 把数字喂进去
    scores = F.softmax(outputs.logits, dim=1)   # 分数变百分比
    labels = torch.argmax(scores, dim=1)        # 选最大的
    labels = [model.config.id2label[i] for i in labels.tolist()]
print(labels)
```

模型先吐出 **logits**（内部两盏灯的「亮度」）。注意 `model.config` 规定 `0 = NEGATIVE（负面）、1 = POSITIVE（正面）`，所以 logits 数组里**第 1 个数永远对应「负面」、第 2 个数永远对应「正面」**。notebook 真实输出：

```
"today is not that bad" → logits = [-3.46, +3.61]
                          负面分= -3.46 (暗)   正面分= +3.61 (亮)   → 正面灯亮
"today is so bad"      → logits = [+4.75, -3.79]
                          负面分= +4.75 (亮)   正面分= -3.79 (暗)   → 负面灯亮
```

> **⚠️ 易混淆点：数字前面的「+ / −」≠ 情感的「正 / 负」**
>
> 看第二行 `[+4.75, -3.79]`：那个 `+4.75` 前面的加号，**只是这个数值本身是正数，不代表「正面情感」**。
> 它处在「第 1 个位置」，而第 1 个位置 = 负面分，所以它其实是「负面灯的亮度 = +4.75」。
>
> 判断标准只有一条：**看位置，不看正负号**。
> - 第 1 个位置（index 0） = 负面分
> - 第 2 个位置（index 1） = 正面分
> - 谁的数值更大，模型就判为哪种情感。
>
> 三句话对照一下就顺了（注意「负面分」「正面分」谁大谁小由句子意思决定，跟数字前面带不带 +/− 无关）：
> ```
> "today is not that bad"   负面分 -3.46 (暗)   正面分 +3.61 (亮)  → POSITIVE
> "today is so bad"         负面分 +4.75 (亮)   正面分 -3.79 (暗)  → NEGATIVE
> "so good"                 负面分 -4.19 (暗)   正面分 +4.56 (亮)  → POSITIVE
> ```

再用两步变成人话结论：
- **softmax**：把灯亮度变成百分比（两个分数加起来 = 100%）
  ```
  [-3.46, +3.61] → [0.0008, 0.99915]   # 99.9% 正面
  ```
- **argmax**：选最亮的那盏灯 → 标签 `1` → 查表 → `POSITIVE`

---

## 五、第三步：看结果（最有意思的地方）

notebook 最终输出：

```
['POSITIVE', 'NEGATIVE', 'POSITIVE']
```

即：
```
"today is not that bad" → POSITIVE  (99.9%)
"today is so bad"      → NEGATIVE  (99.98%)
"so good"             → POSITIVE  (99.98%)
```

**重点看第一句**：`"not that bad"`（没那么糟）被判定为**正面**。这说明模型不是简单数「good/bad」单词，而是真的理解了「双重否定 = 偏正面」的含义。这就是 Transformer 架构比老式方法强的地方——它能捕捉词与词之间的关系。

---

## 六、最小可运行代码（想自己跑就复制这段）

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, torch.nn.functional as F

model_name = 'distilbert-base-uncased-finetuned-sst-2-english'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

texts = ['today is not that bad', 'today is so bad', 'so good']
batch = tokenizer(texts, truncation=True, padding=True, return_tensors='pt')

with torch.no_grad():
    logits = model(**batch).logits
    probs = F.softmax(logits, dim=1)
    labels = [model.config.id2label[i] for i in probs.argmax(dim=1).tolist()]
print(labels)   # ['POSITIVE', 'NEGATIVE', 'POSITIVE']
```

---

## 七、和你已学的知识连接

1. **tokenizer 是所有语言 AI 的「第一道关口」**。你之前聊的 ChatGPT、Kimi、GPT 系列，收到你的问题后**第一步**也是 tokenizer（把提问变成数字）。理解了这一步，就理解了大模型工作的起点。
2. **DistilBERT 的「Distil」= 知识蒸馏**，正是之前论文笔记里见过的「蒸馏」——用大模型教小模型，让它又小又聪明。
3. **「softmax + 选最大」** 这种把分数变概率再决策的思想，后面学分类、甚至学 RL 里「选动作」时还会反复见到，是一脉相承的。

---

## 八、下一步可以往哪走

- **深入 tokenizer 本身**：BPE 子词切分（为什么 `"playing"` 会被切成 `"play" + "ing"`）、以及它和之前聊的 **Re-tokenize** 问题怎么串起来。
- **看反向传播 / 梯度**：`learn_torch/grad/03_computation_graph.ipynb`——理解模型是怎么「被训练出来」的（和训练框架、RL 直接相关）。
- **看同一个仓库里的 LLM notebook**：`llm/tutorials/01_openai_api.ipynb` 等，从「传统情感分类」过渡到「对话式大模型」。
