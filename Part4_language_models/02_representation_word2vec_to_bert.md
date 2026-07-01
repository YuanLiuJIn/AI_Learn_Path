# 02 表征学习：从 Word2Vec 到 BERT

## 1. 它解决什么问题

计算机不懂文字，只懂数字。第一步必须把词变成向量。怎么变，才能让向量**带上语义**（意思相近的词，向量也相近）？这就是表征学习（representation learning）的核心。

## 2. 最朴素的做法及其问题

```text
One-hot：每个词一个超长向量，只有一位是 1
  "猫" = [0,0,1,0,...]   "狗" = [0,1,0,0,...]
问题：① 维度等于词表大小（几万维）② 任意两词都正交，"猫"和"狗"毫无关系
```

我们想要的是**稠密、低维、且能反映语义**的向量。

## 3. Word2Vec：用上下文定义词义

核心思想（分布假设）：

> “一个词的意思，由它周围经常出现的词决定。”（You shall know a word by the company it keeps.）

“猫”和“狗”周围常出现“喂”“可爱”“宠物”，所以它们语义相近。Word2Vec 用神经网络从大量文本里学这种共现关系。

两种训练方式：

```text
CBOW：    用上下文词预测中心词（"喂___宠物" -> 猫）
Skip-gram：用中心词预测上下文词（猫 -> 喂、宠物、可爱）
```

训练完，每个词得到一个稠密向量（如 300 维）。神奇的性质：

```text
向量可以做语义运算：
  vec("国王") - vec("男人") + vec("女人") ≈ vec("王后")
  vec("巴黎") - vec("法国") + vec("中国") ≈ vec("北京")
```

说明向量空间里编码了“性别”“首都”这类语义关系。

## 4. Word2Vec 的致命局限：一词多义

Word2Vec 给每个词**一个固定向量**，无法处理多义词：

```text
"苹果"在 "我吃了一个苹果" 和 "苹果发布新手机" 里意思不同，
但 Word2Vec 只给它一个向量 -> 无法区分。
```

这叫**静态词向量**的局限。

## 5. ELMo：上下文相关的动态词向量

ELMo（2018）用双向 LSTM 读整句话，让同一个词在**不同句子里有不同向量**：

```text
"苹果"(吃的) 和 "苹果"(公司) 得到不同向量 —— 因为上下文不同
```

这是从“静态”到“动态/上下文相关”表征的关键一步。

## 6. BERT：深度双向预训练

BERT（2018）用 Transformer 编码器（Part2）做更强的上下文表征，是表征学习的集大成者。

### 6.1 两个预训练任务

```text
1. MLM（掩码语言模型）：随机遮住句中 15% 的词，让模型根据"左右两边"猜
   "我今天去[MASK]买菜" -> 预测 [MASK]=超市
   关键：同时看左右（双向），比 GPT 的单向理解更全面

2. NSP（下一句预测）：判断两句话是否相邻（后被证明可有可无）
```

### 6.2 为什么“双向”重要

```text
GPT（单向）：只能从左往右看，预测下一个词
BERT（双向）：能同时看左右上下文 -> 对"理解"类任务更强
```

填空式的 MLM 迫使模型必须利用两侧信息，学到更深的语义表征。

### 6.3 预训练 + 微调范式

```text
预训练：在海量无标注文本上学 MLM（通用语言理解）
微调：  在小规模有标注数据上，针对具体任务（分类、问答、NER）微调
```

这套范式让 BERT 在十几个 NLP 任务上一举刷新纪录，影响了之后所有模型。

## 7. 演化总结

```text
One-hot：稀疏、无语义
  ↓
Word2Vec：稠密、有语义，但静态（一词一向量）
  ↓
ELMo：上下文相关（一词多向量），但用 LSTM
  ↓
BERT：基于 Transformer 的深度双向表征 + 预训练微调范式
```

## 8. 代码直觉（用预训练 BERT 拿词向量）

```python
from transformers import AutoTokenizer, AutoModel
import torch

tok = AutoTokenizer.from_pretrained("bert-base-chinese")
model = AutoModel.from_pretrained("bert-base-chinese")

ids = tok("苹果发布新手机", return_tensors="pt")
with torch.no_grad():
    out = model(**ids)
# out.last_hidden_state: [1, seq_len, 768]，每个 token 一个上下文相关向量
print(out.last_hidden_state.shape)
```

## 经典论文与开源项目

- Mikolov et al., "Efficient Estimation of Word Representations" (Word2Vec), 2013。
- Pennington et al., "GloVe", 2014。
- Peters et al., "Deep Contextualized Word Representations" (ELMo), 2018。
- Devlin et al., "BERT", 2018（必读）。
- GitHub: `huggingface/transformers`、`google-research/bert`。
- 博客：Jay Alammar, "The Illustrated Word2vec" / "The Illustrated BERT"。

## 本章小结

表征学习解决“词怎么变成有语义的向量”。Word2Vec 用上下文学到静态词向量并能做语义运算，但无法处理多义词；ELMo 引入上下文相关的动态向量；BERT 用 Transformer + 掩码语言模型做深度双向预训练，并确立“预训练 + 微调”范式。理解型 NLP 由此进入新时代。
