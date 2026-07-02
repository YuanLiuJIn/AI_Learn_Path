# Hermes 学习专题

> Hermes = 长寿命、自我进化的 AI Agent
> 核心理念：**同步内核 + 异步外壳 + 自学习闭环**
> 定位：与 Harness Engineering 互补 —— Harness 讲"方法论"，Hermes 讲"具体怎么做"

## 文件夹结构

| 文件 | 内容 | 预计时间 |
|---|---|---|
| `00_learning_path.md` | 学习路线与建议顺序 | 10 min |
| `01_hermes_overview.md` | Hermes 概述、架构全景、设计哲学 | 1h |
| `02_message_flow_agent_loop.md` | 一条消息的完整流转 + Agent Loop | 1.5h |
| `03_context_management.md` | 上下文管理、Prompt 分层、压缩策略 | 1.5h |
| `04_memory_and_self_evolution.md` | 双通路记忆 + Background Review + Curator | 2h |
| `05_subagent_and_safety.md` | 子 Agent 委派、安全体系设计 | 1.5h |
| `06_hermes_vs_openclaw.md` | 对比分析：什么时候用哪个 | 0.5h |
| `07_practical_guide.md` | 从零搭建、配置、实战 | 2h |
| `references.md` | 统一参考文献与资源 | - |

## 前置知识

- 了解 AI Agent 的基本概念（什么是 Agent Loop、工具调用、System Prompt）
- 推荐先看完 `Harness_Engineering/` 专题，建立"Harness 是什么"的整体认知
- 看完后回过来理解 Hermes，会发现它就是"Harness Engineering 原则的一个高质量实现"

## 学习原则

1. **先看架构图，再读细节**：每章都配有 ASCII 架构图，先形成全局印象
2. **对比 OpenClaw 来理解差异**：Hermes 和 OpenClaw 是两种不同哲学的实现
3. **不要只看原理，要动手**：第 7 章提供了从零搭建的完整流程
4. **带着问题学**：比如"Agent 怎么记住上次教它的事？"→ 去看第 4 章记忆系统

## 与 Harness_Engineering 的关系

```
Harness_Engineering/          Hermes/
├─ 方法论/工程原则             ├─ 一个具体实现
├─ Agent = Model + Harness    ├─ 同步内核 + 异步外壳 + 自学习
├─ 五大子系统                  ├─ 消息流转 + 记忆 + 上下文 + 安全
├─ 工业案例                   ├─ 实战：从零培养助手
└─ 通用设计                   └─ 源码级分析（内置 60+ 工具
                                 、SQLite 持久化等）
```

建议学习顺序：
1. Harness 入门 (`harness_engineering_guide.md`)
2. Harness 进阶 (`harness_engineering_advanced.md`)
3. **然后来看 Hermes** → 看一个具体系统怎么把抽象原则落地
4. 最后看 ADP 云端 Harness (`05_cloud_harness_adp.md`) → 看企业级怎么做
