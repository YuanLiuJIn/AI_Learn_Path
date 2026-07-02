# Harness Engineering 学习路线

> Harness Engineering = 为 AI Agent 设计外部控制系统（引导/约束/反馈/治理）
> 公式：`Agent = Model + Harness`

## 学习地图

```
第0步：先读这个 → 理解“是什么”和“为什么”
  ↓
第1步：入门概念 → harness_engineering_guide.md（1-2 小时）
  理解：Agent=Model+Harness、Guides/Sensors、四大组件
  ↓
第2步：动手实践 → mini_harness_project/（2-4 小时）
  跑通 ReAct Agent Loop + Sandbox + Tools + Sensors + Trace
  ↓
第3步：进阶系统设计 → harness_engineering_advanced.md（3-5 小时）
  理解：确定性外壳、Task Loop 状态机、Checkpoint/幂等、五大子系统、控制论
  ↓
第4步：子系统深挖（逐个击破）
  ├─ 03_deep_dive_agent_loop.md      → Agent Loop 到底怎么设计
  ├─ 04_deep_dive_context_memory.md   → 上下文压缩、记忆系统
  ├─ 05_cloud_harness_adp.md          → 云端 Harness 架构（ADP 案例）
  └─ 06_empirical_cases.md            → 真实案例（OpenAI Codex/Stripe/Cursor）
  ↓
第5步：延伸专题
  ├─ Hermes/ 专题 → 长寿命自进化 Agent（与 Harness 互补视角）
  └─ OpenClaw/ 相关文章 → 多 Agent 协作（KM 搜索）
```

## 推荐学习顺序

| 顺序 | 文件 | 预计时间 | 学完后能做什么 |
|---|---|---|---|
| 1 | `harness_engineering_guide.md` | 1-2h | 理解 Harness 的核心公式和四大组件 |
| 2 | `mini_harness_project/` | 2-4h | 手动跑通一个最小闭环的 Agent Harness |
| 3 | `harness_engineering_advanced.md` | 3-5h | 学会生产级系统设计（状态机/检查点/五大子系统）|
| 4 | `03_deep_dive_agent_loop.md` | 2-3h | 从 ReAct 到 Task Loop 的完整演化 |
| 5 | `04_deep_dive_context_memory.md` | 2-3h | 掌握上下文压缩、长期记忆工程 |
| 6 | `05_cloud_harness_adp.md` | 2-3h | 理解云端解耦 Harness 架构设计 |
| 7 | `06_empirical_cases.md` | 1-2h | 看工业级实践如何落地 |

## 核心论文必读（按学习阶段）

### 入门阶段
- **ReAct (2022)**: Reason→Act→Observe 循环范式 — arxiv.org/abs/2210.03629
- **SWE-bench (2023)**: Coding Agent 评测标准 — arxiv.org/abs/2310.06770

### 进阶阶段
- **Anthropic** "Effective harnesses for long-running agents"
- **Anthropic** "Scaling Managed Agents: Decoupling the brain from the hands"
- **Böckeler (Thoughtworks/Martin Fowler)** "Harness engineering for coding agent users"
- **Mitchell Hashimoto** "My AI Adoption Journey"（Engineer the Harness）

### 系统设计阶段
- **Toolformer (2023)**: 模型自学调用工具 — arxiv.org/abs/2302.04761
- **WebArena (2023)**: 真实 Web 环境 Agent — arxiv.org/abs/2307.13854
- **AutoGen (2023)**: 多 Agent 协作框架 — arxiv.org/abs/2308.08155

## 关键开源项目

| 项目 | 用途 | 链接 |
|---|---|---|
| lm-evaluation-harness | 评测 Harness 基础模板 | github.com/EleutherAI/lm-evaluation-harness |
| SWE-bench | Coding Agent 评测 | swebench.com |
| Inspect AI | 生产级评测（含沙箱） | inspect.aisi.org.uk |
| OpenHands | 自托管 Coding Agent | github.com/OpenHands/OpenHands |
| AutoGen | 多 Agent 框架 | microsoft.github.io/autogen/ |

## 学习建议

1. **先跑代码再读理论**：mini_harness_project 只依赖 Python 标准库，10 分钟就能跑通
2. **带着问题读论文**：不要泛读，先列出自己的问题（"Agent 卡住怎么办""上下文太长怎么处理"），再去论文里找答案
3. **从单 Agent 开始**：多 Agent 是解耦手段不是炫技，先把单 Agent 长任务跑稳
4. **踩坑记笔记**：Agent 每次犯错，问自己"这个问题能通过改 harness 一劳永逸解决吗"

## 与 Hermes 专题的关系

Harness Engineering 是**工程方法论**（抽象层），Hermes 是**具体实现**（产品层）。
- 先学 Harness Engineering → 理解"Agent 需要什么样的外部系统"
- 再看 Hermes → 理解"一个具体系统怎么把记忆、自进化、安全性打包实现"
- 两者互补：Harness 给你上层设计思维，Hermes 给你底层实现参考
