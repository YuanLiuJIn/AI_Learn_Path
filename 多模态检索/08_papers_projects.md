# 08. 重要论文、文章、项目与实践路线

> 目标：整理学习多模态检索时最值得读的论文、文章和开源项目，并说明它们分别解决什么问题。

## 1. 论文阅读路线

建议按四条线读：

```text
表示学习线：CLIP / ALIGN / BLIP / ImageBind
文本检索线：BM25 / DPR / ColBERT / SPLADE / Rerank
向量索引线：HNSW / IVF-PQ / DiskANN / RaBitQ
RAG 应用线：RAG / GraphRAG / Multimodal RAG / Agentic RAG
```

## 2. 多模态表示与跨模态检索

### 2.1 CLIP: Learning Transferable Visual Models From Natural Language Supervision

关键词：

```text
图文对比学习
双塔结构
文本搜图片
零样本分类
```

为什么重要：

```text
它把图像和文本对齐到统一向量空间，是现代图文检索和多模态 Embedding 的基础之一。
```

建议重点读：

```text
模型结构
对比学习目标
zero-shot 方式
图文相似度计算
```

### 2.2 ALIGN: Scaling Up Visual and Vision-Language Representation Learning

关键词：

```text
大规模噪声图文对
图文对齐
规模化训练
```

为什么重要：

```text
说明大规模弱监督图文数据对跨模态表示学习非常有效。
```

### 2.3 BLIP / BLIP-2

关键词：

```text
图文理解
图片 Caption
视觉语言预训练
Query Transformer
```

为什么重要：

```text
相比只做对比学习，BLIP 系列更强调图文生成、理解与多任务预训练，对多模态 RAG 中的图片理解很重要。
```

### 2.4 ImageBind: One Embedding Space To Bind Them All

关键词：

```text
多模态统一空间
文本、图片、音频、视频等模态对齐
跨模态检索
```

为什么重要：

```text
它把 CLIP 的图文对齐思路扩展到更多模态，是理解“多模态统一表示空间”的重要论文。
```

### 2.5 ColPali / 文档视觉检索方向

关键词：

```text
PDF/文档页面检索
视觉语言模型
Late Interaction
图文混排文档
```

为什么重要：

```text
很多企业知识不是纯文本，而是 PDF、PPT、扫描件、图表混排文档。文档视觉检索能减少“先 OCR 再文本化”的信息损失。
```

## 3. 文本检索、稀疏检索与重排

### 3.1 BM25

关键词：

```text
倒排索引
词频
逆文档频率
长度归一化
```

为什么重要：

```text
虽然古老，但仍是关键词精确匹配的强基线。很多 RAG 系统只用 Dense Vector，实际容易漏掉错误码、专有名词和短语精确匹配。
```

### 3.2 DPR: Dense Passage Retrieval

关键词：

```text
双塔文本召回
问题向量
段落向量
开放域问答
```

为什么重要：

```text
它推动了 Dense Retrieval 在问答场景中的应用，是文本 RAG 召回的重要基础。
```

### 3.3 ColBERT / ColBERTv2

关键词：

```text
Late Interaction
token 级匹配
MaxSim
高精度检索
```

为什么重要：

```text
它在双塔效率和 Cross-Encoder 精度之间做折中，适合理解“为什么一个向量压缩整篇文档不够”。
```

### 3.4 SPLADE

关键词：

```text
学习型稀疏检索
词项扩展
倒排索引
可解释召回
```

为什么重要：

```text
它让稀疏检索具备语义扩展能力，是 Hybrid Search 中的重要一路。
```

### 3.5 Cross-Encoder Reranker

关键词：

```text
Query-Document 联合编码
相关性打分
精排
```

为什么重要：

```text
召回阶段负责“别漏”，Rerank 阶段负责“排准”。Cross-Encoder 是理解精排的核心模型范式。
```

## 4. 向量索引与 ANN

### 4.1 HNSW: Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs

关键词：

```text
小世界图
多层图
高召回低延迟
```

为什么重要：

```text
HNSW 是现代向量数据库和搜索系统中最常见的内存型 ANN 索引之一。
```

### 4.2 Product Quantization for Nearest Neighbor Search

关键词：

```text
向量压缩
子空间量化
码本
近似距离
```

为什么重要：

```text
PQ 是大规模向量压缩和 IVF-PQ 的基础。
```

### 4.3 DiskANN

关键词：

```text
SSD 向量索引
大规模 ANN
图索引
成本优化
```

为什么重要：

```text
当向量规模大到内存放不下时，需要磁盘型索引。DiskANN 是理解十亿级向量检索的重要系统。
```

### 4.4 RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for ANN Search

关键词：

```text
随机量化
低比特表示
误差界
高维向量压缩
```

为什么重要：

```text
它代表了向量量化压缩的新路线：用更小表示完成快速近似搜索，再配合精排保证质量。
```

## 5. RAG 与多模态 RAG

### 5.1 Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

关键词：

```text
检索增强生成
外部知识
开放域问答
```

为什么重要：

```text
RAG 的经典起点，解释为什么大模型需要外部检索。
```

### 5.2 Multimodal RAG 方向

关键词：

```text
文本 + 图片 + 视频 + 表格
多模态上下文
多模态模型生成
```

建议关注问题：

```text
不同模态如何切分？
检索结果如何组装给模型？
图片和视频证据如何引用？
多模态 Rerank 如何做？
```

### 5.3 Agentic RAG 方向

关键词：

```text
自主查询规划
多步检索
反思与验证
工具调用
```

为什么重要：

```text
复杂问题往往不是一次检索能解决，Agentic RAG 让 Agent 接管查询拆解、补充检索和验证过程。
```

## 6. 值得动手的项目

### 6.1 FAISS

适合学习：

```text
Flat
IVF
PQ
HNSW
向量检索评估
```

练习：

```text
用 CLIP 生成图片向量，用 FAISS 做文本搜图片。
```

### 6.2 Milvus / Qdrant / Weaviate / LanceDB

适合学习：

```text
向量数据库
元数据过滤
HNSW 参数
向量索引工程化
```

练习：

```text
构建一个图文检索 Demo，支持文本搜图片和图片搜图片。
```

### 6.3 Vespa / Elasticsearch / OpenSearch

适合学习：

```text
全文检索
向量检索
Hybrid Search
排序表达式
在线检索服务
```

练习：

```text
实现 BM25 + Dense Vector 的混合检索。
```

### 6.4 LlamaIndex / LangChain

适合学习：

```text
RAG 管道
文档解析
索引构建
Retriever
多模态 RAG 原型
```

练习：

```text
做一个能检索 PDF 文本和图片的问答系统。
```

### 6.5 ColPali / 文档视觉检索项目

适合学习：

```text
PDF 页面级检索
视觉语言模型
Late Interaction
图文混排文档理解
```

练习：

```text
上传一批 PDF 页面截图，用自然语言检索相关页面。
```

### 6.6 Awesome-Multimodal-RAG

适合学习：

```text
多模态 RAG 论文列表
系统设计模式
开放项目集合
```

练习：

```text
选一个文档型或图片型多模态 RAG 项目复现。
```

## 7. 文章阅读主题

除了论文，建议找这些主题的工程文章：

```text
向量数据库内部原理
HNSW 参数调优
Hybrid Search 实践
RAG 检索质量优化
多模态 RAG 架构设计
PDF 文档解析与表格抽取
视频 RAG：ASR/OCR/抽帧/片段检索
Embedding 模型评测
Reranker 选型
```

## 8. 实践路线

### 实践一：文本搜图片

```text
数据：一批图片 + 图片描述
模型：CLIP
索引：FAISS / Qdrant
功能：输入文本，返回相关图片
```

### 实践二：图片搜图片

```text
输入：上传图片
过程：Image Encoder 生成 query 向量
输出：相似图片
```

### 实践三：Hybrid Search

```text
数据：文档 chunk
召回：BM25 + Dense Vector
融合：RRF
重排：Cross-Encoder
```

### 实践四：视频片段检索

```text
视频 → 抽帧 + ASR + OCR + Caption
  ↓
片段级索引
  ↓
文本 query 搜视频时间段
```

### 实践五：多模态 RAG

```text
检索文本 + 图片 + 表格
  ↓
组装上下文
  ↓
多模态模型或 LLM 回答
  ↓
返回答案与证据引用
```

### 实践六：Agent 调用多模态检索

```text
Agent 接收任务
  ↓
判断需要查什么模态
  ↓
调用多模态检索工具
  ↓
根据结果继续规划下一步
```

## 9. 一句话总结

> 多模态检索的学习资料可以分成四类：表示学习论文解释“不同模态如何对齐”，检索论文解释“如何高质量召回和排序”，向量索引论文解释“如何在海量数据上快速搜索”，RAG/Agent 项目解释“如何把检索结果变成智能应用”。