# 知识图谱学习专题

> 目标：系统学习知识图谱从底层表示、构建、存储、查询、推理到 GraphRAG / LLM 应用的完整链路。

## 一句话定义

知识图谱不是“画一张关系图”，而是：

```text
用节点表示实体/概念，用边表示关系，
把分散在文本、表格、数据库、文档里的知识，
组织成可查询、可推理、可解释、可服务 AI 应用的结构化知识网络。
```

## 文件结构

| 顺序 | 文件 | 内容 |
|---|---|---|
| 1 | `00_learning_path.md` | 学习路线与整体地图 |
| 2 | `01_knowledge_graph_overview.md` | 知识图谱是什么，解决什么问题 |
| 3 | `02_graph_data_models.md` | RDF、属性图、本体、Schema、三元组 |
| 4 | `03_kg_construction_pipeline.md` | 知识抽取、实体识别、关系抽取、实体对齐、知识融合 |
| 5 | `04_storage_query_graph_database.md` | 图数据库、RDF Store、Neo4j、SPARQL、Cypher |
| 6 | `05_reasoning_and_quality.md` | 规则推理、本体推理、路径推理、质量评估 |
| 7 | `06_kg_embedding_and_gnn.md` | TransE、RotatE、ComplEx、R-GCN、图表示学习 |
| 8 | `07_llm_graphrag.md` | LLM + 知识图谱、GraphRAG、问答系统 |
| 9 | `08_papers_projects.md` | 重要论文、文章、开源项目 |
| 10 | `09_practical_projects.md` | 适合学习的专业实战项目 |
| 11 | `references.md` | 参考资料索引 |

## 核心链路

```text
原始数据
  ├─ 文本 / PDF / 网页
  ├─ 表格 / 数据库
  ├─ 日志 / 业务记录
  └─ 多模态数据
      ↓
知识抽取
  ├─ 实体识别 NER
  ├─ 关系抽取 RE
  ├─ 事件抽取 EE
  └─ 属性抽取
      ↓
知识融合
  ├─ 实体对齐
  ├─ 消歧
  ├─ 去重
  └─ 冲突解决
      ↓
图谱建模与存储
  ├─ RDF / OWL / SPARQL
  ├─ 属性图 / Cypher
  └─ 图数据库 / 三元组库
      ↓
查询、推理与表示学习
  ├─ 图查询
  ├─ 规则推理
  ├─ 图算法
  ├─ KG Embedding
  └─ GNN
      ↓
上层应用
  ├─ 知识问答
  ├─ 推荐系统
  ├─ 风险分析
  ├─ 搜索增强
  ├─ GraphRAG
  └─ Agent 记忆与工具
```

## 学习目标

学完后你应该能回答：

1. 知识图谱和普通数据库、向量数据库有什么区别？
2. RDF 图和属性图有什么区别？
3. 本体、Schema、实体、关系、属性分别是什么？
4. 知识抽取 pipeline 如何从文本中构建图谱？
5. 实体对齐和知识融合为什么重要？
6. 图数据库如何存储和查询知识图谱？
7. SPARQL 和 Cypher 有什么区别？
8. 规则推理、本体推理、路径推理分别解决什么问题？
9. TransE、RotatE、R-GCN 这类模型在知识图谱里做什么？
10. GraphRAG 为什么比普通文本 RAG 更适合复杂关系型问题？
