# 02. 技术栈详解

---

## 分层技术栈全景

```text
┌── 前端展示层 ──────────────────────────────────────┐
│ FastAPI（后端API）+ Jinja2 / Streamlit（原型）       │
│ ECharts / Plotly（数据可视化）                       │
└──────────────────────────────────────────────────┘

┌── Agent 编排层 ────────────────────────────────────┐
│ LangGraph（状态机工作流）                            │
│ LangChain（工具封装、Prompt模板）                     │
│ Pydantic（结构化校验）                                │
│ asyncio + ThreadPoolExecutor（并行调度）              │
└──────────────────────────────────────────────────┘

┌── Agentic RAG 检索引擎 ─────────────────────────────┐
│ ChromaDB / Milvus（向量数据库）                       │
│ BGE-large-zh（中文Embedding）                         │
│ BM25 + Dense（混合检索）                              │
│ GPT-4o-mini / Claude Haiku（RAG推理模型）              │
│ Tavily API（Web搜索补充）                             │
└──────────────────────────────────────────────────┘

┌── GUI Agent 采集引擎 ───────────────────────────────┐
│ Playwright（浏览器自动化）                            │
│ OmniParser（UI截屏结构化识别）                         │
│ mss（高性能截图）                                    │
│ Gemini Flash / Doubao-Seed（多模态视觉决策）           │
│ Qwen2.5-VL（GRPO训练基座）                            │
│ pyperclip（中文输入方案）                              │
└──────────────────────────────────────────────────┘

┌── 强化学习训练层 ───────────────────────────────────┐
│ GRPO（去Critic策略优化）                              │
│ Verl / TRL（分布式RL框架）                             │
│ 自研奖励函数（5维度：动作/坐标/文本/格式/效率）         │
│ W&B / TensorBoard（训练监控）                         │
└──────────────────────────────────────────────────┘

┌── 数据与存储层 ────────────────────────────────────┐
│ PostgreSQL（结构化持久化）                            │
│ Redis（任务队列+结果缓存）                             │
│ MinIO / 本地FS（文件存储）                            │
│ JSONL（Agent执行Trace）                              │
└──────────────────────────────────────────────────┘

┌── 基础设施层 ──────────────────────────────────────┐
│ Docker + docker-compose（容器化部署）                 │
│ pytest（单元测试+Agent行为测试）                       │
│ ruff（代码质量）                                      │
│ Git + pre-commit（版本管理）                          │
└──────────────────────────────────────────────────┘
```

---

## 各层选型理由

### GUI Agent

| 技术 | 用途 | 为什么选 |
|---|---|---|
| Playwright | 浏览器自动化 | 比 Selenium 快，支持 download/session_api |
| OmniParser | 截屏识别 | 微软开源，BBOX+语义标签 |
| mss | 高性能截图 | 比 pyautogui 快 5-10× |
| Gemini Flash | 多模态视觉决策 | 轻量、不贵、GUI 理解好 |
| Qwen2.5-VL | GRPO 训练基座 | 中文强、本地部署 |
| pyperclip | 中文输入 | pyautogui 不支持中文 |

### Agentic RAG

| 技术 | 用途 | 为什么选 |
|---|---|---|
| ChromaDB | 向量数据库 | 嵌入式、无需额外部署 |
| BGE-large-zh | 中文 Embedding | MTEB 中文 Top3 |
| BM25+Dense | 混合检索 | 准确率提升 15-20% |
| GPT-4o-mini | RAG 推理 | $0.15/M tokens，够用 |
| Tavily | Web 搜索 | 专为 Agent 设计的结构化搜索 API |

### RL 训练

| 技术 | 用途 | 为什么选 |
|---|---|---|
| GRPO | 策略优化 | 不需要 Critic（省50%显存） |
| Verl | 分布式 RL 框架 | 支持 FSDP+GRPO |
| 自研奖励函数 | 训练信号 | 动作类型+坐标命中+文本F1+格式+效率 |
| W&B | 实验追踪 | 可视化 reward curve + KL |

### Agent 编排

| 技术 | 用途 | 为什么选 |
|---|---|---|
| LangGraph | 工作流引擎 | 声明式状态机、原生循环/分支 |
| Pydantic | 结构校验 | Agent间通信契约 |
| asyncio | 异步并发 | 5 Worker 并行 → 120s→35s |
| FastAPI | 对外API | 高性能异步、自带文档 |

### 基础设施

| 技术 | 用途 | 为什么选 |
|---|---|---|
| Docker | 容器化 | Playwright 环境一致性 |
| pytest | 测试 | Agent 行为测试+单元测试 |
| ruff | 代码质量 | Rust 实现，比 flake8 快 100× |
| JSONL Trace | 可观测性 | 每步记录完整调用链 |
