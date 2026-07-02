# Hermes 参考文献与资源索引

> 本文档统一收纳 Hermes 专题涉及的所有论文、项目、文章和代码仓库。

## 开源项目

| 项目 | 说明 | 仓库 |
|---|---|---|
| Hermes Agent | Nous Research 长寿命自进化 Agent（主仓库，Python ≥3.11） | 内网 Git (hermes-agent) |
| Hermes Hatchery | Go 控制面，Agent 生命周期管理 | 内网 Git (hatchery) |
| OpenClaw | 多 Agent 协作平台，与 Hermes 互补 | 内网版 |
| Nous Research | Hermes 的出身组织，以高质量微调模型闻名 | nousresearch.com |

## 腾讯内部文章（KM）

| 标题 | 作者 | 日期 | 内容 |
|---|---|---|---|
| 一颗大脑，多种皮肤：Hermes 是怎么做"长寿命 AI Agent"的 | tianhongsu | 2026-06 | Hermes 架构全景、消息流转、记忆系统 |
| OpenClaw & Hermes 快速从 0 到 1 完成多Agent开发 | danielxiao | 2026-06 | Skill/Agent 区别、提示词心法、多 Agent 模式 |
| 每日一个hermes小设计 | angoyang | 2026-07 | Hermes 安全防护设计 |
| Hermes Agent 排障指南 | jackybzhou | 2026-06 | 取证三源、现象→线索→根因→处置 |
| Hermes Agent 架构调研 | shingao | 2026-06 | 架构调研与评估 |
| OpenClaw 与 Hermes Agent 架构深度剖析 | tingcheng | 2026-06 | 从核心能力看真实 Agent 工程实现 |
| 面向服务化 HermesAgent 的 Bot 接入 | minchangwei | 2026-05 | Gateway 设计与 tRPC-Agent 扩展 |

## 相关论文与理论基础

### 上下文与记忆
| 论文 | 贡献 | 与 Hermes 的关系 |
|---|---|---|
| **Lost in the Middle** (Liu et al., 2023) | LLM 注意力 U 型曲线 | 支持 Hermes 的"保护头尾"压缩策略 |
| **MemGPT** (Packer et al., 2023) | 虚拟内存思想应用于 LLM | 上下文压缩与记忆系统设计参考 |
| **Anthropic Context Engineering** (2025) | System Prompt 分层 + Prompt Cache | Hermes 的 Prompt 分层设计理论来源 |

### Agent 设计与安全
| 论文 | 贡献 | 与 Hermes 的关系 |
|---|---|---|
| **ReAct** (Yao et al., 2022) | Thought→Action→Observation 交替 | Agent Loop 的基本范式 |
| **Toolformer** (Schick et al., 2023) | 模型自学调用工具 | 桥接工具的渐进式发现理论支撑 |
| **Anthropic Managed Agents** (2025) | Session/Harness/Sandbox 解耦 | 子 Agent 隔离设计参考 |
| **SWE-agent** (Yang et al., 2024) | Agent-Computer Interface | 工具接口设计参考 |

### 多 Agent 协作
| 论文 | 贡献 | 与 Hermes 的关系 |
|---|---|---|
| **AutoGen** (Wu et al., 2023) | 多 Agent 对话框架 | Hermes 的 delegate_task 设计参考 |

## 关键技术概念速查

| 概念 | 在 Hermes 中的位置 |
|---|---|
| 双消息轨 | `messages` vs `api_messages` — 数据纯净性与 API 适配分离 |
| 桥接工具 | `tool_search` / `tool_describe` / `tool_call` — 渐进式工具发现 |
| 双通路记忆 | 内置层（System Prompt 快照）+ 外部 Provider（围栏注入）|
| Background Review | 暗线自进化触发 → fork Review Agent → 写记忆/建技能 |
| Curator | 周级知识生命周期管理 → 状态流转 + 伞状合并 |
| Prompt Cache 策略 | 按变化频率分层 → Stable→Context→Volatile |
| 上下文压缩流水线 | 预剪枝 → 保护头尾 → LLM 总结中段 → 重组防护 |
| Subagent 隔离 | delegate_task → 独立上下文 + 最小权限 + 摘要回传 |
| 安全三层防线 | Skill 扫描 + Review 白名单 + Subagent 隔离 |

## 相关工具与平台

| 工具/平台 | 用途 | 与 Hermes 的关系 |
|---|---|---|
| Venus | 内网模型统一接入平台 | Hermes 可通过 Venus 调用多种模型 |
| 智研日志 | 日志查询平台 | Hermes 可通过 API 查询业务日志 |
| AnyDev | 内网开发容器 | Hermes 的推荐部署环境 |
| 企业微信机器人 | 即时通讯接入 | Hermes 可通过 Gateway 接入企微 |

## 学习建议

### 按主题深入
1. **对记忆系统感兴趣** → 精读 `04_memory_and_self_evolution.md` + 搜索 "MemGPT"、"RAPTOR" 论文
2. **对安全设计感兴趣** → 精读 `05_subagent_and_safety.md` + Anthropic 安全系列
3. **对多 Agent 感兴趣** → 看 OpenClaw（更适合多 Agent），而非 Hermes
4. **想动手实践** → `07_practical_guide.md` + 搭建自己的 Hermes 实例
