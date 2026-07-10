# GeoInfoAgent：基于 GUI Agent + Agentic RAG 的地理信息汇总平台

> 一句话：用 GUI Agent 自动采集无 API 数据源，用 Agentic RAG 智能检索与交叉验证，生成结构化地理洞察报告。

## 项目目录

```
GeoInfoAgent/
├── README.md                        # 项目总览
├── 01_system_design.md              # 系统架构设计
├── 02_tech_stack.md                 # 技术栈详解
├── 03_gui_agent_engine.md           # GUI Agent 采集引擎设计
├── 04_agentic_rag_pipeline.md       # Agentic RAG 检索引擎设计
├── 05_multi_agent_orchestration.md  # 多 Agent 协作编排
├── 06_implementation_roadmap.md     # 四阶段实施路线
├── 07_resume_template.md            # 简历描述参考
├── 08_references.md                 # 参考论文与项目
├── src/                             # 源代码目录
│   ├── gui_agent/                   # GUI Agent 采集引擎
│   ├── rag_engine/                  # Agentic RAG 检索引擎
│   ├── coordinator/                 # 多 Agent 编排
│   ├── frontend/                    # FastAPI + Web UI
│   └── training/                    # GRPO 训练模块
├── config/                          # 配置文件
├── docker/                          # Docker 部署
└── tests/                           # 测试
```

## 核心技术栈

```text
GUI Agent：Playwright + OmniParser + Gemini Flash + Qwen2.5-VL
Agentic RAG：ChromaDB + BGE Embedding + Self-RAG + CRAG
多 Agent：LangGraph + Planner-Worker-Reviewer 三角色
RL 训练：GRPO + Verl + 自研奖励函数
后端：Python + FastAPI + asyncio
数据：PostgreSQL + Redis + MinIO
工程：Docker + pytest + W&B
```
