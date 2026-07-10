# Agentic RAG 学习专题

> Agentic RAG = 让 Agent 自主规划检索策略、多步查询、验证结果、动态调整的智能检索增强生成系统。
> 传统 RAG 只能"检索→生成"一步到位；Agentic RAG 能像专业研究员一样自主设计检索路径。

## 文件夹结构

| 文件 | 内容 | 预计时间 |
|---|---|---|
| `01_agentic_rag_overview.md` | RAG 演化全景：从 Naive RAG 到 Agentic RAG | 45min |
| `02_agentic_rag_architecture.md` | 架构模式：Single-Agent、Multi-Agent、核心设计原则 | 1h |
| `03_key_techniques.md` | 核心机制：Self-RAG、Corrective RAG、Adaptive RAG | 1.5h |
| `04_implementation.md` | 动手：LangGraph / LlamaIndex 实现 Agentic RAG | 2h |
| `05_search_p1.md` | 前沿：Search-P1 — 双轨路径评分 + 软性结果评分 | 1.5h |
| `06_projects_and_papers.md` | 论文索引、开源项目、学习路线 | 15min |
| `08_geo_project_blueprint.md` | 实战：GeoInfoAgent 项目完整蓝图 | 1h |
| `09_gui_agent_for_rag.md` | 进阶：GUI Agent 如何赋能 Agentic RAG | 45min |

## 前置知识

- 了解传统 RAG 的基本流程（检索→增强→生成）
- 了解 AI Agent 基本概念（Agent Loop、工具调用）
- 推荐先学过 `Harness_Engineering/` 里的 Agent Loop 部分

## 核心论文

| 论文 | 年份 | 贡献 |
|---|---|---|
| **Self-RAG** (Asai et al.) | 2023 | 模型自主决定是否需要检索、自己评估检索质量 |
| **Corrective RAG (CRAG)** (Yan et al.) | 2024 | 检索结果不好时自动修正：重新搜索、切换知识源 |
| **Adaptive RAG** (Jeong et al.) | 2024 | 根据查询复杂度自适应选择检索策略 |
| **Agentic RAG Survey** (Singh et al.) | 2025 | 首次系统综述，提出完整分类体系 |
| **Search-P1** (ACL 2026) | 2026 | 路径中心奖励破解 Agentic RAG 稀疏奖励困境 |

## 开源项目

| 项目 | 说明 | 链接 |
|---|---|---|
| **LangGraph Agentic RAG** | LangChain 官方 Agentic RAG 教程 | github.langchain.ac.cn |
| **LlamaIndex Agentic RAG** | LlamaIndex 官方实现 | llamaindex.ai |
| **Awesome Agentic RAG** | 生产级 Agentic RAG 示例合集 | github.com/amsayeed |
| **AgenticRAG-Survey** | 综述配套代码库 | github.com/asinghcsu |
