# 06. 混合检索、Rerank 与 CBO 查询优化

> 目标：理解为什么工业检索系统不能只靠 Dense Vector，以及 BM25、Sparse、Dense、Rerank、CBO 如何协同。

## 1. 为什么需要混合检索？

纯关键词检索不懂语义。

```text
Query: “怎么提升模型推理速度”
可能漏掉：
  “inference latency optimization”
  “提高吞吐量的服务优化”
  “LLM 推理加速实践”
```

纯向量检索不擅长精确匹配。

```text
Query: “错误码 50013”
可能误召回：
  错误码 50014
  错误码 40013
  错误码 50103
```

所以高质量检索通常是：

```text
BM25 + Sparse Vector + Dense Vector + Metadata Filter + Rerank
```

## 2. BM25：关键词精确匹配的基线

BM25 来自传统全文检索。

它关注：

```text
词是否出现
词出现多少次
词在多少文档中出现
文档长度
```

直觉：

```text
一个词在当前文档中频繁出现 → 更相关
一个词在全库中很少出现 → 区分度更高
文档太长 → 需要长度归一化
```

适合：

```text
错误码
人名
接口名
产品名
代码符号
专有名词
精确短语
```

不适合：

```text
同义表达
跨语言
抽象语义
图片/视频检索
```

## 3. 稀疏向量检索

稀疏向量介于 BM25 和 Dense 之间。

传统 BM25 的向量可以看作：

```text
维度 = 词表大小
大多数维度为 0
非零维度表示某个词的权重
```

学习型稀疏模型，如 SPLADE，会生成可扩展的词项权重。

例如 Query：

```text
“推理加速”
```

模型可能激活：

```text
推理: 0.9
加速: 0.8
inference: 0.7
latency: 0.5
throughput: 0.4
optimization: 0.3
```

优点：

```text
比 BM25 更语义化
比 Dense 更可解释
仍可利用倒排索引
对关键词和专业词友好
```

缺点：

```text
不如 Dense 擅长深层语义
索引可能比 BM25 更大
需要模型生成稀疏表示
```

## 4. 稠密向量检索

Dense Vector 是常见 Embedding。

```text
文本 / 图片 / 视频 → Encoder → [0.12, -0.33, ...]
```

优点：

```text
语义理解强
支持跨语言
支持跨模态
适合相似推荐和 RAG 召回
```

缺点：

```text
精确匹配弱
解释性差
容易误召回相似但不满足约束的内容
需要 ANN 索引
```

## 5. 多路召回与融合

典型查询链路：

```text
Query
  ↓
Query Rewrite / Query Understanding
  ↓
并行召回：
  ├─ BM25 Top-N
  ├─ Sparse Top-N
  ├─ Dense Top-N
  ├─ Metadata Filter
  └─ 业务召回
  ↓
候选合并与去重
  ↓
分数归一化与融合
  ↓
Rerank
  ↓
Top-K
```

常见融合方式：

### 5.1 加权融合

```text
score = α * bm25_score + β * sparse_score + γ * dense_score + δ * business_score
```

问题：不同分数尺度不同，需要归一化。

### 5.2 Reciprocal Rank Fusion

RRF 不直接看分数，而看排名。

```text
score(d) = Σ 1 / (k + rank_i(d))
```

优点：

```text
简单稳定
不依赖不同召回器分数尺度
适合多路召回融合
```

## 6. Rerank：为什么需要重排？

召回阶段追求“别漏”，所以会带来误召回。

Rerank 阶段追求“排准”。

流程：

```text
多路召回 Top-1000
  ↓
Rerank 模型重新判断 query-doc 相关性
  ↓
输出 Top-20
```

常见 Rerank 模型：

```text
Cross-Encoder：Query 和 Document 一起输入
ColBERT / Late Interaction：token 级细粒度匹配
多模态 Reranker：Query 与图片/视频/图文文档一起判断
LLM Reranker：让大模型判断相关性，但成本较高
```

## 7. 双塔召回 vs Cross-Encoder 重排

| 方式 | 输入 | 优点 | 缺点 | 用途 |
|---|---|---|---|---|
| 双塔 Bi-Encoder | Query 和 Doc 分别编码 | 可预计算，速度快 | 交互弱 | 大规模召回 |
| Cross-Encoder | Query 和 Doc 一起输入 | 相关性判断准 | 成本高，不能全库跑 | Rerank |
| Late Interaction | 保留 token/patch 向量 | 精度和效率折中 | 存储较大 | 精细检索/重排 |

## 8. 多模态 Rerank

对于图片/视频/文档，Rerank 可能使用更丰富输入：

```text
Query
候选文本
候选图片
候选 OCR
候选 ASR
候选 Caption
候选元数据
```

模型综合判断：

```text
这个候选是否真的回答了用户问题？
图片中的内容和文本 query 是否一致？
视频片段时间点是否准确？
OCR/ASR 是否支持这个结果？
```

## 9. CBO：基于成本的查询优化

CBO = Cost-Based Optimizer。

它负责选择最省成本、效果最好的执行路径。

一个混合查询可能包含：

```text
自然语言 query
关键词条件
向量相似度
结构化过滤
权限过滤
时间范围
业务排序
Rerank 数量
```

不同执行顺序成本差异很大。

## 10. 执行路径例子

查询：

```text
Query: “大模型推理优化”
Filter: doc_type = '技术文档' AND time > '2025-01-01'
TopK: 20
```

路径 A：先过滤，再向量检索

```text
全库 → 过滤 doc_type/time → 剩余 10 万条 → 向量检索 → TopK
```

适合：过滤条件很强。

路径 B：先向量检索，再过滤

```text
全库向量检索 Top-10000 → 过滤 doc_type/time → TopK
```

适合：过滤条件很弱。

路径 C：多路召回并行

```text
BM25 Top-N
Dense Top-N
Sparse Top-N
  ↓
合并 → Rerank
```

适合：既要精确匹配，也要语义召回。

## 11. CBO 需要哪些统计信息？

```text
索引规模
字段基数
过滤条件选择率
向量索引类型
TopK 大小
候选集大小
BitSet 构建成本
Rerank 单条成本
历史查询延迟
缓存命中情况
```

CBO 根据这些信息估算：

```text
哪条路径延迟最低
哪条路径资源最省
哪条路径召回风险最低
```

## 12. BitSet 与过滤代价

过滤条件常用 BitSet 表示：

```text
每个 doc 一个 bit
1 = 符合过滤条件
0 = 不符合过滤条件
```

如果过滤很强：

```text
只命中 1 万 / 10 亿
```

先构建 BitSet 很划算。

如果过滤很弱：

```text
命中 8 亿 / 10 亿
```

构建巨大 BitSet 可能很浪费。

CBO 要判断：

```text
先过滤是否值得？
还是先向量召回更划算？
```

## 13. 一句话总结

> 混合检索解决“关键词精确匹配”和“语义召回”之间的矛盾；Rerank 解决召回候选的排序质量问题；CBO 解决复杂查询链路中执行顺序和资源成本的问题。高质量多模态检索系统通常不是单一路径，而是多路召回、融合、重排和成本优化的组合。