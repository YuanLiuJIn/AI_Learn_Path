# 00. 多模态检索学习路线

> 目标：先建立整体地图，再逐层深入底层原理与工程实现。

## 1. 先建立总图

多模态检索可以拆成四层：

```text
第一层：表示层
  问题：不同模态怎么变成可比较的向量？
  关键词：Embedding、Contrastive Learning、CLIP、ImageBind

第二层：数据处理层
  问题：原始文本/图片/视频/音频怎么变成可检索资产？
  关键词：算子、清洗、去重、脱敏、OCR、ASR、Caption、Embedding Pipeline

第三层：检索引擎层
  问题：海量向量和文本怎么快速搜？
  关键词：BM25、Sparse、Dense、HNSW、IVF、PQ、DiskANN、RaBitQ、Rerank、CBO

第四层：应用层
  问题：检索结果怎么服务大模型应用？
  关键词：RAG、多模态 RAG、Agent Memory、智能搜索、推荐
```

## 2. 学习路径

### 阶段一：理解“多模态为什么能互相搜索”

先学：

```text
Embedding
相似度计算
对比学习
图文对齐
统一语义空间
```

阅读：

```text
02_embeddings_and_alignment.md
```

重点理解：

```text
为什么一句话“海边落日”能搜到对应图片？
为什么一张截图能搜到相关文档？
为什么视频片段可以被文本 query 命中？
```

---

### 阶段二：理解“数据怎么被加工成可检索资产”

多模态数据不是天然可检索的。

一张图片需要：

```text
解码 → Resize → OCR → 目标检测 → 标签生成 → Image Embedding
```

一段视频需要：

```text
抽帧 → 镜头切分 → ASR → OCR → Caption → Video/Text Embedding
```

阅读：

```text
03_multimodal_operators_and_processing.md
04_cpu_gpu_stateful_sqlfirst.md
```

重点理解：

```text
多模态算子是什么？
为什么 CPU/GPU 要协同？
为什么文本去重是有状态算子？
SQL-First 如何让 AI 计算进入数据分析体系？
```

---

### 阶段三：理解“向量检索为什么难”

如果有 10 亿条向量，不能对每条都算相似度。

所以需要 ANN 近似最近邻索引。

阅读：

```text
05_vector_index_ann.md
```

重点理解：

```text
HNSW：图索引，适合内存高召回
IVF：聚类倒排，先找桶再搜索
PQ/SQ：量化压缩，减少内存
DiskANN：把大规模索引放到 SSD
RaBitQ：随机量化，用低比特近似距离
```

---

### 阶段四：理解“工业检索为什么必须混合”

纯关键词不懂语义，纯向量不擅长精确匹配。

所以工业系统通常是：

```text
BM25 + Sparse Vector + Dense Vector + Metadata Filter + Rerank
```

阅读：

```text
06_hybrid_search_rerank_cbo.md
```

重点理解：

```text
BM25 负责精确匹配
Sparse 负责可解释的语义扩展
Dense 负责深层语义召回
Rerank 负责高质量排序
CBO 负责选最省成本的执行路径
```

---

### 阶段五：理解“多模态检索如何进入 RAG / Agent”

最终，多模态检索不是为了检索本身，而是为了让上层 AI 应用可以使用外部知识。

阅读：

```text
07_multimodal_rag_agent_architecture.md
```

重点理解：

```text
多模态 RAG：检索文本、图片、视频片段，再生成答案
Agent：把多模态检索当作工具或长期记忆
智能搜索：把搜索结果组织成答案卡片、引用、推荐
```

## 3. 推荐实践顺序

```text
实践 1：用 CLIP 做文本搜图片
实践 2：用 FAISS/HNSW 建一个图文向量索引
实践 3：加入 BM25，做 Hybrid Search
实践 4：加入 Cross-Encoder 或多模态 Rerank
实践 5：把结果接入一个简单的多模态 RAG
实践 6：让 Agent 调用检索工具完成一个多步任务
```

## 4. 一句话总结

> 多模态检索的学习路线是：先理解跨模态表示，再理解数据处理流水线，然后深入向量索引和混合检索，最后把检索能力接入 RAG、Agent、智能搜索等应用。