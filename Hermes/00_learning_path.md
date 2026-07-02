# Hermes 学习路线

> Hermes Agent 的完整学习路径：从概念理解到动手实践。

## 学习地图

```
第 1 步：架构全景（1h）
  01_hermes_overview.md
  → 理解 Hermes 是什么、为什么要"长寿命"、三段式架构

第 2 步：消息如何流转（1.5h）
  02_message_flow_agent_loop.md
  → 一条消息从进入到返回的完整路径
  → 双消息轨、桥接工具、主循环设计

第 3 步：上下文管理（1.5h）
  03_context_management.md
  → Prompt 分层（最大化缓存命中率）
  → 三级压缩流水线
  → Compaction vs Handoff

第 4 步：记忆与自进化（2h）★ 最独特的章节
  04_memory_and_self_evolution.md
  → 双通路记忆注入（内置层 + 外部 Provider）
  → Background Review：暗线自进化
  → Curator：知识生命周期管理

第 5 步：安全与委派（1.5h）
  05_subagent_and_safety.md
  → 子 Agent 委派流程（leaf vs orchestrator）
  → 三级安全防线
  → Skill 安装静态扫描

第 6 步：对比理解（0.5h）
  06_hermes_vs_openclaw.md
  → 两种哲学：自进化 vs 连接一切
  → 什么时候选 Hermes，什么时候选 OpenClaw

第 7 步：动手实践（2h）
  07_practical_guide.md
  → 环境搭建 → 配置模型 → 企微接入 → 培养助手
```

## 核心论文与理论基础

### 直接相关
- **Hermes Agent** — Nous Research，GitHub（内网版：hermes-agent 仓库）
- **OpenClaw** — 多 Agent 协作平台，与 Hermes 互补

### 间接支撑
- **Anthropic Context Engineering** (2025) — System Prompt 分层、Prompt Cache
- **Lost in the Middle** (Liu et al., 2023) — 为什么不能全量加载所有 Skill
- **ReAct** (Yao et al., 2022) — Agent Loop 的基本范式
- **Anthropic Managed Agents** (2025) — Session/Harness/Sandbox 解耦

## 适合人群

- 对 AI Agent 有一定了解（知道 Agent Loop、Tool Call 是什么）
- 想知道"Agent 怎么越用越懂我"的具体实现
- 想给 Agent 加上长期记忆和自学习能力
- 想了解生产级 Agent 的安全设计

## 前置要求

- 了解 Python（Hermes Agent 主要用 Python 3.11+）
- 了解 LLM API 调用基础
- 建议先看过 `Harness_Engineering/harness_engineering_guide.md`

## 配套开源项目

| 项目 | 链接 | 说明 |
|---|---|---|
| Hermes Agent | 内网 Git (hermes-agent) | 主仓库，Python ≥3.11 |
| Hermes Hatchery | 内网 Git (hatchery) | Go 控制面，Agent 生命周期管理 |
| OpenClaw | 内网版 | 多 Agent 协作平台 |

## 学习技巧

1. **画你自己的图**：每读完一章，尝试手动画出核心流程图
2. **对号入座**：把 Hermes 的设计和其他文章（Claude Code、ADP）对比，找出相同点与不同点
3. **提真实问题**：比如"我自己的 Agent 经常在第 30 轮忘了要干嘛——Hermes 怎么解决这个问题？"

## 常见问题

**Q: Hermes 和 Harness Engineering 是什么关系？**
A: Harness Engineering 是方法论（Agent ≈ Model + Harness），Hermes 是一个具体实现。看 Hermes 就是看"好的 Harness 长什么样"。

**Q: 我需要自己搭一个 Hermes 吗？**
A: 不需要。Hermes 是开箱即用的。但理解它的设计能帮你改进自己的 Agent 系统。

**Q: Hermes 能做多 Agent 吗？**
A: 技术上可以（delegate_task + kanban），但 Hermes 官方建议用于单 Agent 个人使用场景。多 Agent 推荐 OpenClaw。
