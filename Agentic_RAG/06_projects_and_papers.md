# Agentic RAG 参考文献与资源索引

## 核心综述论文

| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| **Agentic RAG Survey** (Singh et al.) | 2025 | arxiv.org/abs/2501.09136 | 首次系统综述，提出完整架构分类体系 |

## 关键机制论文

| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| **Self-RAG** (Asai et al.) | 2023 | arxiv.org/abs/2310.11511 | 模型自主决定是否检索、自己评估检索质量 |
| **Corrective RAG (CRAG)** (Yan et al.) | 2024 | arxiv.org/abs/2401.15884 | 检索结果不好时自动修正策略 |
| **Adaptive RAG** (Jeong et al.) | 2024 | arxiv.org/abs/2403.14403 | 根据查询复杂度自适应选择检索策略 |
| **Search-P1** | 2026 | ACL 2026 | 路径中心奖励破解稀疏奖励困境 |

## RAG 基础论文

| 论文 | 年份 | 核心贡献 |
|---|---|---|
| **Retrieval-Augmented Generation** (Lewis et al.) | 2020 | RAG 开山之作 |
| **REALM** (Guu et al.) | 2020 | 检索增强语言模型预训练 |
| **Atlas** (Izacard et al.) | 2022 | 少量样本的检索增强模型 |
| **REPLUG** (Shi et al.) | 2023 | 检索增强黑盒大模型 |

## 开源项目

| 项目 | 说明 | 链接 |
|---|---|---|
| **LangGraph Agentic RAG** | LangChain 官方教程 | github.langchain.ac.cn |
| **LlamaIndex Agentic RAG** | LlamaIndex 官方实现 | llamaindex.ai |
| **Awesome Agentic RAG** | 生产级示例合集 | github.com/amsayeed/awesome-agentic-rag-examples |
| **AgenticRAG-Survey** | 综述配套代码库 | github.com/asinghcsu/AgenticRAG-Survey |
| **Agentic RAG with LlamaIndex** | 多步检索 Agent | github.com/Aftabbs/Agentic-RAG-With-LLamaIndex |

## 企业内部实践参考

| 方向 | 来源 | 核心内容 |
|---|---|---|
| Search-P1 路径中心奖励 | ACL 2026 论文 | 双轨路径评分破解 Agentic RAG 稀疏奖励 |
| GUI Agent 从零搭建 | 内部技术文章 | LangGraph 工作流、坐标归一化、记忆防死循环 |
| 多模态 UI 自动化综述 | 内部技术文章 | Ferret-UI/Mobile-Agent 两大路线、合成数据构建 |
| RAG 发展全景 | 内部技术文章 | Naive→Advanced→Modular→Graph→Agentic 五阶段 |
| Hook 层 Agent 治理 | 内部工程文章 | 用框架切面兜底 LLM 偷懒/越权/失忆 |
| 联盟广告 Agent | 内部工程文章 | 研发 + 运营双层 Agent 全链路实践 |
| Agent Loop 探索 | 内部工程文章 | Harness Engineering 在 RAG Agent 中的应用 |

## 学习路线

```text
入门（2h）：
  1. 01_agentic_rag_overview.md → 理解演化全景
  2. Naive RAG 亲手实现一个 → 对比感受差距

进阶（4h）：
  3. 02_agentic_rag_architecture.md → 三种架构模式
  4. 03_key_techniques.md → Self-RAG / CRAG / Adaptive RAG
  5. Self-RAG 论文精读

深入（4h）：
  6. 04_implementation.md → 动手用 LangGraph 实现
  7. 05_search_p1.md → 前沿 RL 训练方法
  8. Agentic RAG Survey 论文

工程（按需）：
  LlamaIndex / LangGraph 源码阅读
  LangGraph 文档里的 Agentic RAG 教程
  Awesome Agentic RAG 生产级示例
```
