# 参考资料索引

> 本页只整理公开论文、开源项目与通用技术方向，方便后续继续补充。

## 1. 多模态表示与跨模态检索

- CLIP: Learning Transferable Visual Models From Natural Language Supervision
- ALIGN: Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision
- BLIP: Bootstrapping Language-Image Pre-training
- BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models
- ImageBind: One Embedding Space To Bind Them All
- ColPali: Efficient Document Retrieval with Vision Language Models
- Multimodal Representation Alignment for Cross-modal Information Retrieval

## 2. 文本检索、稀疏检索与 Rerank

- BM25 / Okapi BM25
- DPR: Dense Passage Retrieval for Open-Domain Question Answering
- ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction
- ColBERTv2: Efficient and Effective Retrieval via Lightweight Late Interaction
- SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking
- Cross-Encoder Reranking
- BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

## 3. 向量索引与 ANN

- HNSW: Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs
- Product Quantization for Nearest Neighbor Search
- FAISS: A Library for Efficient Similarity Search and Clustering of Dense Vectors
- DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node
- RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search
- ScaNN: Efficient Vector Similarity Search at Scale

## 4. RAG 与多模态 RAG

- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- REALM: Retrieval-Augmented Language Model Pre-Training
- HyDE: Precise Zero-Shot Dense Retrieval without Relevance Labels
- GraphRAG 相关论文与工程文章
- Agentic RAG 相关 Survey
- Multimodal RAG 相关 Survey 与项目集合

## 5. 开源项目

### 向量索引 / 向量数据库

- FAISS
- Milvus
- Qdrant
- Weaviate
- LanceDB
- hnswlib
- DiskANN

### 搜索与混合检索

- Elasticsearch
- OpenSearch
- Vespa
- Pyserini
- BEIR

### RAG / 多模态 RAG 框架

- LlamaIndex
- LangChain
- Haystack
- Awesome-Multimodal-RAG

### 多模态模型与工具

- OpenCLIP
- sentence-transformers
- transformers
- ColPali 相关实现
- OCR / ASR / Caption 相关开源工具

## 6. 推荐关键词

检索资料时可以搜索：

```text
multimodal retrieval survey
cross-modal retrieval CLIP
multimodal embedding alignment
hybrid search dense sparse retrieval
SPLADE ColBERT reranker
vector database internals HNSW IVF PQ
DiskANN vector search
RaBitQ quantization ANN
multimodal RAG
video RAG ASR OCR retrieval
document visual retrieval ColPali
```

## 7. 后续补充建议

后续可以继续扩展：

```text
1. 增加 CLIP 论文细读
2. 增加 HNSW 论文细读
3. 增加 RaBitQ 论文细读
4. 增加 ColPali 文档检索实践
5. 增加一个 FAISS + CLIP 文本搜图片 Demo
6. 增加一个 BM25 + Dense + Rerank 的 Hybrid Search Demo
7. 增加一个视频 RAG 实战案例
```