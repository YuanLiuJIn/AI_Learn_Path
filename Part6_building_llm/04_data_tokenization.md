# 04 数据：数据集、数据清洗与 Tokenization

## 1. 为什么数据是上限

一句业界共识：

> 模型架构决定下限，**数据质量决定上限**。同样的模型，喂干净高质量数据和喂脏数据，效果天差地别。GPT、LLaMA 的成功很大程度来自数据工程。

本章讲 LLM 数据的三件事：从哪来、怎么洗、怎么切成 token。

## 2. 数据从哪来

```text
网页：     Common Crawl（海量但脏）、FineWeb、C4
代码：     GitHub（The Stack）
书籍/论文：Books、arXiv、维基百科
问答/对话：StackExchange、Reddit（许可范围内）
高质量精选：教科书、百科（"教科书级"数据，质量高）
```

规模感：现代 LLM 预训练动辄数万亿（trillion）token。

## 3. 数据清洗：把脏数据变干净

原始网页数据极脏，清洗是重活也是关键。常见步骤：

```text
1. 语言过滤：只保留目标语言（用语言识别模型打分）
2. 质量过滤：去掉乱码、广告、导航栏、低质量页
   - 规则过滤（标点比例、平均词长、是否像自然语言）
   - 模型打分（用分类器判断"像不像高质量文本"）
3. 去重(Deduplication)：极其重要！见下节
4. 去隐私/有害内容：删除个人信息(PII)、有害/违规内容
5. 去基准污染：删掉评测集(benchmark)的内容，防止"作弊"
   （呼应 Part1 的 benchmark contamination）
```

## 4. 去重为什么这么重要

```text
重复数据的危害：
- 浪费算力：同样的内容学很多遍
- 损害泛化：模型倾向"背诵"高频重复段落，而非学习规律
- 评测失真：训练集混入评测内容 -> 虚高分数
```

去重粒度：

```text
精确去重：完全相同的文档/段落直接删
近似去重：用 MinHash / SimHash 找"高度相似"的内容删
         （网页有大量模板化、转载、镜像内容）
```

研究表明：好的去重能用更少数据达到更好效果。

## 5. Tokenization：把文本切成模型能吃的单元

模型不直接处理文字，要先切成 **token**（最小单元）再映射成 id。

### 三种粒度

```text
词级(word)：    词表巨大，遇到没见过的词(OOV)就歇菜
字符级(char)：  词表小，但序列太长、效率低
子词级(subword)：折中 ✓ 现代主流（BPE 等）
```

### BPE（Byte Pair Encoding）：主流方法

一句话直觉：

> 从字符开始，**反复把最常一起出现的相邻单元合并**成一个新 token，直到达到目标词表大小。常见词成为整体，罕见词拆成子词。

```text
例子（简化）：
初始：l o w e r
统计发现 "l o" 最常一起出现 -> 合并成 "lo"
再发现 "lo w" 常见 -> 合并成 "low"
...
结果："low" 是一个 token，罕见词如 "lowest" 可能切成 "low" + "est"
```

好处：

```text
- 常见词高效（一个 token）
- 罕见词/新词也能表示（拆成子词，不会 OOV）
- 词表大小可控（如 5 万、10 万）
```

现代多用 **byte-level BPE**（在字节上做 BPE），能表示任意字符（包括 emoji、各种语言），永不 OOV。

### 代码直觉

```python
import tiktoken                          # OpenAI 的 BPE tokenizer
enc = tiktoken.get_encoding("cl100k_base")
ids = enc.encode("Hello, 大模型!")        # 文本 -> token id 序列
print(ids)
print(enc.decode(ids))                   # id -> 文本（可逆）
```

训练自己的 tokenizer 可用 `huggingface/tokenizers` 或 `sentencepiece`。

## 6. Tokenization 的隐藏影响

```text
- 影响序列长度：切得碎 -> 序列长 -> 计算贵
- 影响多语言公平：中文/小语种可能被切得更碎，相同内容花更多 token
- 影响数字/代码：早期 tokenizer 对数字处理差，影响数学能力
- 词表大小权衡：大词表序列短但 embedding 矩阵大
```

所以 tokenizer 看似不起眼，实则影响效率、成本和能力。

## 7. 数据配比与课程

```text
- 领域配比：网页/代码/书籍/数学按比例混合（代码和数学能提升推理）
- 质量分层：高质量数据可多过几遍(epoch)，低质量少过
- Chinchilla 配比：参数量与训练 token 数要匹配（别让大模型"吃不饱"）
- 数据课程(curriculum)：有的训练后期加大高质量/特定领域数据比例
```

## 8. 完整数据流水线

```text
原始语料(Common Crawl 等)
  -> 抽取正文(去 HTML)
  -> 语言过滤
  -> 质量过滤(规则 + 模型)
  -> 去重(精确 + 近似)
  -> 去隐私/有害/基准污染
  -> Tokenize(BPE)
  -> 打包成定长样本(如 2048 token 一条)
  -> 训练
```

## 经典论文与开源项目

- Raffel et al., "C4 / T5", 2019（大规模清洗语料）。
- Penedo et al., "RefinedWeb / FineWeb", 2023–2024（高质量网页数据）。
- Lee et al., "Deduplicating Training Data Makes LMs Better", 2021。
- Sennrich et al., "BPE for NMT", 2016；Kudo, "SentencePiece", 2018。
- GitHub: `huggingface/datatrove`（数据处理）、`huggingface/tokenizers`、`google/sentencepiece`、`openai/tiktoken`。

## 本章小结

数据质量决定模型上限。LLM 数据工程包括：多来源收集 → 语言/质量过滤 → 去重（极关键）→ 去隐私/有害/基准污染 → Tokenization。BPE（尤其 byte-level）是主流分词法，常见词整体、罕见词拆子词、永不 OOV，但会影响序列长度、多语言公平和成本。配比与去重往往比模型结构更影响最终效果。
