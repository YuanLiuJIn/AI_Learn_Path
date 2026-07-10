# 06. 实施路线（四阶段）

---

## 阶段 1：单数据源基础采集（2 周）

```text
目标：Playwright 实现 CMA 数据平台自动采集

任务清单：
□ Playwright 环境搭建 + 浏览器启动
□ 登录态保存与复用（storage_state）
□ 表单字段提取（explore_page.py）
□ 关键词填写 + 时间范围选择 + 站点选择
□ 查询提交 + 结果等待
□ 下载事件监听 + 文件保存
□ 网络请求捕获（寻找后台API）
□ 基础异常处理（超时重试、页面加载等待）

里程碑：
  可命令行运行的 CMA 数据采集脚本
  自动下载指定时间范围的气象数据
```

---

## 阶段 2：Agentic RAG 管道（2 周）

```text
目标：LangGraph 搭建 Agentic RAG 检索管道

任务清单：
□ 向量数据库搭建（ChromaDB + BGE Embedding）
□ 导入历史气象报告、分析文档
□ Query Router 实现（复杂度分流）
□ Multi-Source Retriever 实现（向量+BM25+Web）
□ Self-RAG Evaluator（相关性/完整性/可靠性评估）
□ CRAG Corrector（检索不足→自动修正）
□ Citation Tracer（来源追溯）
□ 与阶段1的集成（RAG可检索GUI采集的数据）

里程碑：
  自然语言查询 → 自动检索 + 质量评估 + 补充搜索
  准确率对比：vs 朴素 RAG
```

---

## 阶段 3：GUI Agent 增强（3 周）

```text
目标：从单数据源扩展到多数据源，提升GUI Agent智能度

任务清单：
□ 集成 OmniParser UI 元素识别
□ 混合感知实现（DOM + 截图）
□ 接入第二个数据源（卫星数据/政府公开数据）
□ 两阶段采集策略（探索模式→固化模式）
□ LangGraph 工作流整合
□ 记忆增强（防死循环、经验复用）
□ 新增 3-5 种操作指令支持
□ GRPO 领域特化训练（可选，加分项）
  □ 构建训练数据（500条标注数据）
  □ 自研奖励函数（5维度）
  □ Verl 分布式训练
  □ 效果对比（训练前 vs 训练后准确率）

里程碑：
  跨 2+ 数据站的 GUI Agent
  操作准确率提升对比
```

---

## 阶段 4：多 Agent 协作 + Web UI（3 周）

```text
目标：完整系统集成 + 可视化

任务清单：
□ Planner Agent 实现
□ Worker Pool 并行执行框架
□ Data Fusion Layer（多源交叉验证）
□ Reviewer Agent（质量审核）
□ Writer Agent（报告生成）
□ FastAPI 后端接口
□ Web UI（Streamlit 原型 或 Jinja2 模板）
□ 数据可视化（ECharts/Plotly 图表）
□ 完整 Trace/日志系统（JSONL）
□ Docker 容器化部署
□ 端到端测试

里程碑：
  完整 GeoInfoAgent 系统
  输入查询 → 自动采集 + 检索 + 验证 + 报告
```

---

## 时间线总览

```text
Week 1-2:  ████████  CMA 数据采集脚本
Week 3-4:  ████████  Agentic RAG 管道
Week 5-7:  ██████████████  GUI Agent 增强 + GRPO训练
Week 8-10: ██████████████  多Agent协作 + Web UI
```

---

## 每个阶段的交付物

| 阶段 | 交付物 | 可展示指标 |
|---|---|---|
| 1 | `cma_collector.py` | 采集成功率、单次耗时 |
| 2 | `agentic_rag/` | 检索准确率 vs 朴素 RAG |
| 3 | `gui_agent/` | 操作准确率、GRPO 提升幅度 |
| 4 | `GeoInfoAgent` 完整系统 | 端到端查询处理时间、数据覆盖率 |
