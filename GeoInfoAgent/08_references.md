# 08. 参考论文与项目

---

## 核心论文

### GUI Agent 方向

| 论文 | 年份 | 贡献 |
|---|---|---|
| OmniParser (Lu et al.) | 2024 | 截屏→结构化 UI 元素识别 |
| Ferret-UI (You et al.) | 2024 | 高分辨率 UI 理解，Any-Resolution 技术 |
| Mobile-Agent-v2 (Wang et al.) | 2024 | 多 Agent 架构 + 自我反思机制 |
| GUI Agents: A Survey | 2024 | 200+ 参考文献的系统综述 |

### Agentic RAG 方向

| 论文 | 年份 | 贡献 |
|---|---|---|
| Self-RAG (Asai et al.) | 2023 | 自主检索评估 + 反思 token |
| CRAG (Yan et al.) | 2024 | 检索失败时自动修正策略 |
| Adaptive RAG (Jeong et al.) | 2024 | 查询复杂度自适应路由 |
| Agentic RAG Survey (Singh et al.) | 2025 | 首次系统综述 |
| Search-P1 | 2026 (ACL) | 双轨路径评分破解稀疏奖励 |

### RL 训练方向

| 论文 | 年份 | 贡献 |
|---|---|---|
| GUI-R1 | 2025 | GRPO 统一动作空间训练 GUI Agent |
| Mobile-R1 | 2025 | 三阶段 RL 训练手机 GUI Agent |
| SAGE | 2025 | 技能增强 GRPO |

---

## 开源项目

| 项目 | 链接 | 用途 |
|---|---|---|
| Playwright | playwright.dev | 浏览器自动化主引擎 |
| OmniParser | github.com/microsoft/OmniParser | UI 截屏结构化识别 |
| LangGraph | github.com/langchain-ai/langgraph | Agent 工作流编排 |
| ChromaDB | github.com/chroma-core/chroma | 向量数据库 |
| BGE | github.com/FlagOpen/FlagEmbedding | 中文 Embedding |
| Verl | github.com/volcengine/verl | 分布式 RL 训练框架 |
| Page-Agent | github.com/alibaba/page-agent | DOM 文本化 GUI Agent |
| browser-use | github.com/browser-use/browser-use | 浏览器 Agent 框架 |
| AgentEvolver | github.com/alibaba/AgentEvolver | 自进化 Agent 框架 |

---

## 内部技术参考

| 方向 | 核心内容 |
|---|---|
| GUI Agent 从零搭建 | LangGraph 工作流、坐标归一化、记忆防死循环 |
| 多模态 UI 自动化综述 | Ferret-UI vs Mobile-Agent 两大路线 |
| RAG 发展全景 | Naive→Advanced→Modular→Graph→Agentic 五阶段 |
| Search-P1 详解 | 双轨路径评分、软性结果评分、消融实验 |
