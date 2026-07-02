# Harness Engineering 参考文献与资源索引

> 本文档统一收纳 Harness Engineering 专题涉及的所有论文、项目、文章和代码仓库。

## 核心论文

### Agent 交互范式
| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al.) | 2022 | arxiv.org/abs/2210.03629 | Thought→Action→Observation 交替范式 |
| Toolformer: Language Models Can Teach Themselves to Use Tools (Schick et al.) | 2023 | arxiv.org/abs/2302.04761 | 模型自学何时/如何调用工具 |

### 评测 Harness
| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| HELM: Holistic Evaluation of Language Models (Liang et al.) | 2022 | arxiv.org/abs/2211.09110 | 多场景多指标标准化评测 |
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? (Jimenez et al.) | 2023 | arxiv.org/abs/2310.06770 | 真实 GitHub issue 评测 coding agent |
| WebArena: A Realistic Web Environment for Building Autonomous Agents (Zhou et al.) | 2023 | arxiv.org/abs/2307.13854 | 真实 Web 环境评测 browser agent |
| AgentBench: Evaluating LLMs as Agents (Liu et al.) | 2023 | arxiv.org/abs/2308.03688 | 8 类交互环境评测 Agent |

### 上下文与记忆
| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| Lost in the Middle (Liu et al.) | 2023 | arxiv.org/abs/2307.03172 | 模型注意力 U 型曲线 |
| MemGPT (Packer et al.) | 2023 | arxiv.org/abs/2310.08560 | 虚拟内存思想引入上下文管理 |
| RAPTOR (Sarthi et al.) | 2024 | arxiv.org/abs/2401.18059 | 树状层次化摘要检索 |

### 多 Agent 系统
| 论文 | 年份 | 链接 | 核心贡献 |
|---|---|---|---|
| AutoGen (Wu et al.) | 2023 | arxiv.org/abs/2308.08155 | 多 Agent 对话 + 工具 + 人类参与 |
| SWE-agent (Yang et al.) | 2024 | arxiv.org/abs/2405.15793 | Agent-Computer Interface 设计 |

### 工程实践
| 论文/文章 | 来源 | 核心内容 |
|---|---|---|
| Harness engineering for coding agent users (Böckeler) | Thoughtworks/Martin Fowler | Agent = Model + Harness, Guides/Sensors 模型 |
| Effective harnesses for long-running agents | Anthropic | 长任务 Agent 跨 context window 设计 |
| Harness design for long-running application development | Anthropic | Planner/Generator/Evaluator 三 Agent 架构 |
| Scaling Managed Agents: Decoupling the brain from the hands | Anthropic | Session/Harness/Sandbox 解耦架构 |
| My AI Adoption Journey (Mitchell Hashimoto) | 个人博客 | Engineer the Harness 理念 |
| Harness Engineering: leveraging Codex in an agent-first world | OpenAI | Codex ~100 万行代码生成实践 |

## 开源项目

| 项目 | 维护方 | 仓库 | 说明 |
|---|---|---|---|
| lm-evaluation-harness | EleutherAI | github.com/EleutherAI/lm-evaluation-harness | 评测 harness 基础模板 |
| HELM | Stanford CRFM | crfm.stanford.edu/helm/ | living benchmark |
| OpenAI Evals | OpenAI | github.com/openai/evals | 私有 eval 框架 |
| Inspect AI | UK AISI | inspect.aisi.org.uk | 生产级评测（含沙箱） |
| SWE-bench | SWE-bench Team | swebench.com | Coding Agent 评测 |
| OpenHands | OpenHands | github.com/OpenHands/OpenHands | 自托管 coding agent |
| AutoGen | Microsoft | microsoft.github.io/autogen/ | 多 Agent 框架 |
| ToolBench | OpenBMB | github.com/OpenBMB/ToolBench | 大规模工具学习平台 |

## Hermes 相关

| 项目 | 仓库 | 说明 |
|---|---|---|
| Hermes Agent | 内网 Git (hermes-agent) | Nous Research 长寿命自进化 Agent |

## 腾讯内部文章（KM）

| 标题 | 作者 | 日期 |
|---|---|---|
| Agent Harness Engineering 如何驱动云端智能体：Tencent Cloud ADP 的设计实践 | jouislu | 2026-05 |
| 从Harness Engineering到AgentTeams | eivenchen | 2026-05 |
| Context / Harness Engineering：AI Agent 的上下文工程 | dorismo | 2026-06 |
| Harness Engineering 实践指南 | miloguo | 2026-05 |
| 5 天补齐 4 万行文档！（多Agent Harness 实战） | zesui | 2026-04 |
| 让 AI 管理 AI 跑几千个 agent（调度系统设计） | zorrozou | 2026-04 |
| 一颗大脑，多种皮肤：Hermes 是怎么做"长寿命 AI Agent"的 | tianhongsu | 2026-06 |
| OpenClaw & Hermes 快速从 0 到 1 完成多Agent开发 | danielxiao | 2026-06 |

## 行业博客与报告

| 文章 | 来源 |
|---|---|
| Stripe Minions: Building an AI-Native Engineering Culture | Stripe Engineering Blog |
| How Cursor builds self-driving codebases | Cursor Blog |
| The next evolution of the Agents SDK | OpenAI |
| Building LangGraph: Designing an Agent Runtime | LangChain |
| Google Agent Development Kit | Google |
| Microsoft Agent Framework Overview | Microsoft |

## 阅读建议

### 入门（2-4 小时）
1. Böckeler "Harness engineering for coding agent users"（30 分钟）
2. Mitchell Hashimoto "My AI Adoption Journey"（20 分钟）
3. 本项目 `harness_engineering_guide.md`（1 小时）
4. 本项目 `mini_harness_project/`（1 小时动手）

### 进阶（6-10 小时）
1. ReAct 论文（1 小时）
2. SWE-bench 论文（1 小时）
3. Anthropic 三篇 Harness 系列（2 小时）
4. 本项目 `harness_engineering_advanced.md`（3 小时）

### 系统设计（8-12 小时）
1. OpenAI Codex 实践系列（2 小时）
2. AutoGen 论文 + 源码阅读（3 小时）
3. 本项目子系统深挖四篇（3 小时）
4. ADP 设计实践（2 小时）
