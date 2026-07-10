# 07. 简历描述参考

---

## 标准版（一段话）

> **GeoInfoAgent：基于 GUI Agent + Agentic RAG 的多源地理信息汇总平台**
> 
> 设计并实现融合 GUI Agent 与 Agentic RAG 的多源地理信息汇总系统。GUI Agent 端采用 DOM 文本化与截屏识别混合感知方案，集成 OmniParser 结构化 UI 理解与 LangGraph 状态机工作流，实现对无 API 气象数据站点的自动化采集，结合记忆增强防死循环与坐标归一化适配多分辨率，并基于 GRPO 进行领域特化训练（自研五维度奖励函数），以 500 条样本将操作准确率从 72% 提升至 91%。Agentic RAG 端基于 LangGraph 实现 Self-RAG 检索质量评估与 CRAG 自动修正，引入 Search-P1 风格的双轨数据质量评分（自洽性+对齐性），融合向量搜索、BM25、Web 搜索多源检索，检索准确率较朴素 RAG 提升 35%。系统采用 Planner-Worker-Reviewer 三角色多 Agent 协作架构，基于 asyncio 实现 5 路并行采集与自动交叉验证，单次查询耗时从串行 120s 压缩至 35s。

---

## 技术要点拆解版（面试准备用）

```text
项目：GeoInfoAgent 多源地理信息智能汇总平台

解决的核心问题：
  气象、环境等数据分散在多个无 API 平台上，传统 RAG 无法覆盖。
  用 GUI Agent 操作无 API 站点 + Agentic RAG 智能检索，
  实现全自动数据采集、交叉验证、报告生成。

技术亮点：
  1. 混合感知 GUI Agent
     - DOM 文本化（标准网页）+ 截屏识别（地图/Canvas）
     - OmniParser + Gemini Flash 多模态视觉决策
     - LangGraph 状态机工作流
     - 记忆增强防死循环 + 坐标归一化

  2. GRPO 领域特化训练
     - 自研五维度奖励函数（动作类型+坐标命中+文本F1+格式+效率）
     - 500 条样本 → 准确率 72%→91%
     - 基于 Qwen2.5-VL + Verl 框架

  3. Agentic RAG 智能检索
     - Self-RAG 检索质量评估 + CRAG 自动修正
     - 向量搜索 + BM25 + Web 搜索 混合检索
     - Search-P1 风格双轨评分（自洽性+对齐性）

  4. 多 Agent 协作
     - Planner-Worker-Reviewer 三角色 + asyncio 并行
     - 5 路 Worker 并行采集，单查询 120s→35s
     - 数据融合 + 交叉验证

技术栈：
  Python、FastAPI、LangGraph、Playwright、ChromaDB、
  OmniParser、GRPO、Verl、Qwen2.5-VL、BGE Embedding、
  asyncio、Docker、PostgreSQL、Redis
```
