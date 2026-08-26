# 02. Tokenizer 进阶：encode_plus 与 token_type_ids（MLM / NSP）

> 配套 notebook：`bilibili_vlogs/hugface/02_tokenizer_encode_plus_token_type_ids.ipynb`
> 目标读者：对 AI / NLP 零基础。本篇是 [01_tokennizer_sentiment_analysis.md](./01_tokennizer_sentiment_analysis.md) 的姐妹篇——01 讲了 tokenizer 怎么把一句话变成数字、再做个情感分类；本篇深入 BERT 的两个预训练「游戏」（MLM / NSP），以及为此服务的 `encode_plus` 和 `token_type_ids`。
> 本机环境提示：想真跑需要装 `transformers` + `torch`（本机尚未安装 Python）；最省事用 **Google Colab** 在线运行，免安装。

---

## 一、这个 notebook 在做什么（一句话）

在 01 的基础上，进一步讲清楚 **BERT 是怎么「练出来」的**，以及为了让它练两个游戏，tokenizer 多给了我们一个数组 **`token_type_ids`**（标记「这个词属于第一句还是第二句」）。

顺带区别一个名字：01 用的是 `DistilBERT`（BERT 的瘦身版），02 直接用了完整的 **`bert-base-uncased`**（原始 BERT）。因为要讲 BERT 专属的训练机制。

---

## 二、BERT 的两个「预训练游戏」（核心背景）

BERT 在出厂前，是在海量文本上玩了两个自学的游戏，才变成「懂语言」的模型。「预训练」= 先在无标注文本上自学，之后才能做具体任务（如 01 的情感分析）。

### 2.1 MLM（Masked Language Model，完形填空）

- 随机把句子里 15% 的词**抠掉**，换成 `[MASK]` 占位符，让模型猜「这里本来是哪个词」。
- 例：`"今天天气[MASK]好" → 模型要猜出 [MASK]=很`。
- 这解释了 01 里见过的特殊符号 **`[MASK]`** 是干嘛的——它就是给这个游戏准备的「挖空位」。
- 也就是 01 笔记里写的 `[MASK] = 挖空 / 完形填空占位符`，根源就在这里。

### 2.2 NSP（Next Sentence Prediction，下一句预测）

- 给模型两句话 A、B，问它：「B 真的是 A 在原文里的下一句吗？」
- 一半情况是真相邻的句子（标签 = IsNext），一半是随机拼的（标签 = NotNext）。
- 这事需要模型**分清哪些词属于 A、哪些词属于 B**——于是就有了 `token_type_ids`。

> **小知识**：NSP 后来被一些模型（如 RoBERTa）废掉了，认为它帮助不大；但它仍是原版 BERT 的一部分，**它正是 `token_type_ids` 存在的理由**。

---

## 三、新角色：`token_type_ids`（句子分段标记）

在 01 里，每句话 tokenizer 给我们两个数组：`input_ids`（词变编号）和 `attention_mask`（哪些是真内容、哪些是 padding）。

02 里多了一个 **`token_type_ids`**，规则极简单：

| 值 | 含义 |
|---|---|
| `0` | 这个词属于**第一句**（A） |
| `1` | 这个词属于**第二句**（B） |

- **单句话**：全部是 `0`（没有第二句可言）。
- **两句话拼一起**：第一句（含它自己的 `[SEP]`）全是 `0`，第二句（含它自己的 `[SEP]`）全是 `1`。

> **类比**：`token_type_ids` 就像给两段文字**贴不同颜色的便利贴**——蓝色（0）是第一段，黄色（1）是第二段，让模型别把两段的词搞混。

---

## 四、`encode_plus` 是什么

`encode_plus` 是 tokenizer 的一个「加强版」方法，能**一次性把 input_ids、token_type_ids、attention_mask 打包成一个字典返回**。

其实 01 里用的 `tokenizer(...)`（直接调用）如今也会返回这三个数组；`encode_plus` 是更老、更显式的写法，本 notebook 用来演示「句子对」场景。

```python
# 单句：token_type_ids 全 0
tokenizer(test_news[0], truncation=True, max_length=32)
# → token_type_ids: [0, 0, 0, ..., 0]

# 句子对：用 encode_plus，传 text 和 text_pair
tokenizer.encode_plus(text=test_news[0], text_pair=test_news[1],
                      max_length=32, truncation=True)
# → token_type_ids: [0,...,0, 1,...,1]
```

---

## 五、notebook 真实输出走一遍

notebook 用了 `sklearn` 的 20 类新闻组数据集（`fetch_20newsgroups`），取前几条邮件当语料。

### 5.1 单句（cell 115）

```
input_ids:     [101, 2013, 1024, ..., 102]      # [CLS] ... [SEP]
token_type_ids:[0, 0, 0, ..., 0]                 # 全 0（只有一句）
attention_mask:[1, 1, 1, ..., 1]                 # 全是真内容
```

### 5.2 句子对（cell 118）

把两封新闻邮件的「发件人抬头」拼一起，解码后文字是：

```
'[CLS] from : lerxst @ wam. umd. edu [SEP] from : guykuo @ carson. u. washington. edu [SEP]'
```

对应的数组：

```
input_ids:     [101, ...(第一句词)..., 102, ...(第二句词)..., 102]
                                      ↑第一个[SEP]           ↑第二个[SEP]
token_type_ids:[0, 0, ..., 0, 1, 1, ..., 1]
               第一句(含它的[SEP])=0   第二句(含它的[SEP])=1
attention_mask:[1, 1, ..., 1]
```

注意分割点：第一个 `[SEP]`（词编号 `102`）被归到 `0`（属于第一句），第二个 `[SEP]` 归到 `1`（属于第二句）。这是 BERT 的固定约定。

---

## 六、和你已学的知识连接

1. **接 01 的 tokenizer 三件套**：`input_ids` + `attention_mask` 在 01 讲过了；02 补上 `token_type_ids`，凑齐 BERT 输入的三件套。
2. **接 01 的 `[MASK]` 特殊符号**：01 只说「`[MASK]` 是挖空占位符」，02 讲清了它服务的游戏叫 **MLM**。
3. **`[SEP]` 的真正使命**：01 说 `[SEP]` 是「分隔 / 结尾标志」；02 揭示它**更是句子对的分界**——配合 `token_type_ids`，让 BERT 知道 NSP 游戏里 A 句到哪、B 句从哪开始。
4. **为后面铺路**：理解 MLM / NSP，是看懂「BERT、T5、GPT 三大架构差异」的关键——GPT 是「只往右看」、BERT 是「双向 + 完形填空 + 句子对」，这正是本目录 `BERT，T5，GPT` 的主题。

---

## 七、下一步可以往哪走

- **看三大架构对比**：本目录后续讲 BERT（双向 + MLM）、GPT（单向自回归）、T5（把一切变「文本到文本」）的异同。
- **深入 tokenizer 本身**：BPE 子词切分（为什么 `"playing"` 会被切成 `"play" + "ing"`）、以及它和 **Re-tokenize** 问题怎么串起来。
- **看反向传播 / 梯度**：`learn_torch/grad/03_computation_graph.ipynb`——理解模型是怎么「被训练出来」的（和训练框架、RL 直接相关）。
- **看同一个仓库里的 LLM notebook**：`llm/tutorials/01_openai_api.ipynb` 等，从「传统预训练分类」过渡到「对话式大模型」。
