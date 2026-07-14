# 多模态检索学习专题

> 目标：系统理解多模态检索从底层表示、数据处理、向量索引、混合检索到 RAG/Agent 应用的完整链路。

## 一句话定义

多模态检索不是“用向量库搜图片”这么简单，而是：

```text
把文本、图片、音频、视频、表格、点云等不同模态的数据，
经过清洗、切分、脱敏、向量化、建索引、混合召回、重排，
最终变成 RAG、Agent、智能搜索、推荐系统可以消费的知识资产。
```

## 建议学习顺序

| 顺序 | 文件 | 内容 |
|---|---|---|
| 1 | `00_learning_path.md` | 学习路线与整体地图 |
| 2 | `01_multimodal_retrieval_overview.md` | 多模态检索是什么，为什么需要它 |
| 3 | `02_embeddings_and_alignment.md` | Embedding、跨模态对齐、CLIP/ImageBind 等底层原理 |
| 4 | `03_multimodal_operators_and_processing.md` | 多模态算子、清洗、去重、脱敏、Embedding 构建 |
| 5 | `04_cpu_gpu_stateful_sqlfirst.md` | CPU/GPU 异构协同、有状态算子分布式化、SQL-First |
| 6 | `05_vector_index_ann.md` | 向量索引、HNSW、IVF、PQ、DiskANN、RaBitQ |
| 7 | `06_hybrid_search_rerank_cbo.md` | 全文检索、稀疏/稠密向量、Hybrid Search、Rerank、CBO |
| 8 | `07_multimodal_rag_agent_architecture.md` | 多模态 RAG、Agent、智能搜索的系统架构 |
| 9 | `08_papers_projects.md` | 重要论文、文章、项目与实践路线 |
| 10 | `references.md` | 参考资料索引 |

## 核心链路

```text
多模态原始数据
  ↓
多模态数据处理层
  ├─ 清洗
  ├─ 去重
  ├─ 脱敏
  ├─ 切分
  ├─ OCR / ASR / Caption / 标签生成
  ├─ Embedding
  └─ 数据治理
  ↓
混合检索层
  ├─ 全文检索 BM25
  ├─ 稀疏向量检索 SPLADE / Learned Sparse
  ├─ 稠密向量检索 Dense Embedding
  ├─ 多模态语义检索 Text-Image / Text-Video / Image-Text
  ├─ Rerank
  └─ CBO 查询优化
  ↓
上层应用
  ├─ RAG
  ├─ Agent
  ├─ 智能搜索
  ├─ 知识库问答
  └─ 推荐 / 内容理解
```

## 学习目标

学完这个专题后，你应该能回答：

1. 为什么多模态检索需要统一 Embedding 空间？
2. CLIP 这类模型是如何实现图文对齐的？
3. 多模态算子和普通大数据算子有什么区别？
4. CPU/GPU 异构协同为什么能提升吞吐？
5. 为什么文本去重属于有状态算子？如何分布式化？
6. SQL-First 如何把 AI 能力嵌入传统分析系统？
7. HNSW、IVF、PQ、DiskANN、RaBitQ 分别解决什么问题？
8. 为什么工业检索系统不能只用 Dense Vector？
9. Hybrid Search、Rerank、CBO 在检索链路中各自负责什么？
10. 多模态检索如何支撑 RAG 与 Agent？
