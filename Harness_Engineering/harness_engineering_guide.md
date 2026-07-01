# Harness Engineering 讲解（深入浅出版）

> 配套阅读：同目录 `research_report_harness_engineering.md`（更系统的研究报告）。
> 进阶系统设计（确定性外壳、Task Loop、Checkpoint、五大子系统、控制论、实证案例）：见 `harness_engineering_advanced.md`。
> 动手实践：见 `mini_harness_project/`。
> 本文目标：用通俗的方式把「Harness Engineering 是什么、为什么重要、有哪些著名论文和项目」讲清楚。

## 1. 它解决什么问题

你已经有了一个很强的大模型（比如能写代码的 LLM）。但真把它丢进真实工作里，常常出现：

```text
- 它改完代码，但你不知道改对没有（没有测试反馈）
- 它误删了不该动的文件（没有权限边界）
- 它反复犯同一个错（没有把经验沉淀下来）
- 它调用工具失败却继续硬编（没有结构化的工具反馈）
- 你想比较两个模型谁更强，却没有统一的评测方式
```

这些问题**几乎都不是“模型不够聪明”，而是模型周围的环境没搭好**。Harness Engineering 就是专门解决这件事：

> 给模型/Agent 搭一套“外部控制系统”，让它在行动前被正确引导、行动中被安全约束、行动后能被快速检查和修正。

`harness` 这个词来自传统软件工程的 **test harness（测试夹具）**：把被测代码放进一个可控环境，喂输入、装断言、收日志、出报告。大模型时代把这个概念放大了。

## 2. 一句话直觉与生活类比

> Harness 就是套在模型外面的“马具/缰绳 + 跑道 + 仪表盘”。马（模型）有力气，但要靠这套装备才能朝正确方向、安全可控地拉车。

几个类比帮助理解：

```text
模型     = 一个很有天赋但莽撞的新员工
Harness  = 入职手册 + 操作规范 + 测试流程 + 权限系统 + 主管review
```

新员工再聪明，没有手册、没有测试、没有权限控制，也会闯祸。让他靠谱的，往往不是“换一个更聪明的人”，而是“把工作环境和流程设计好”。

## 3. 核心公式：Agent = Model + Harness

Martin Fowler 网站上 Birgitta Böckeler 给了一个很好记的定义：

```text
Agent = Model + Harness
```

即：一个 AI Agent，除了模型本身，**剩下的一切都是 Harness**——提示词、工具、运行环境、测试、日志、审批……

Mitchell Hashimoto 则给了一个很务实的动作定义，叫 **“Engineer the Harness”**：

> 当 Agent 犯错时，不要只是手动修这一次，而是花点功夫工程化一个方案，让它以后不再犯同类错误。

例如 Agent 老是忘了项目用的是 `pnpm` 而不是 `npm`，与其每次纠正，不如在 `AGENTS.md` 里写死一条规则——这就是在“工程化 harness”。

## 4. 它和 Prompt / Context / Eval Engineering 的关系

很多相近的词容易混，用一句话区分：

| 概念 | 关注点 | 一句话 |
|---|---|---|
| Prompt Engineering | 这次怎么问 | 优化单次提问的措辞 |
| Context Engineering | 模型这次看见什么 | 组织喂给模型的信息（检索、记忆、工具结果）|
| Eval Engineering | 输出好不好 | 设计衡量质量的评测 |
| **Harness Engineering** | 整个外部系统怎么设计 | 把上面这些 + 工具/环境/反馈/治理组装成可靠系统 |

Harness 是**范围最大**的那个：它包含 prompt 和 context，但还多了工具调用、沙箱、权限、评测器、日志和回归测试。

## 5. 一个 Harness 由哪几块组成

可以拆成四类组件（沿用 Böckeler 的“控制系统”视角）：

```text
        ┌───────────────────── Harness ─────────────────────┐
输入 -> │ 1.Guides(前馈)  -> 2.执行环境 -> 3.Sensors(反馈) │ -> 结果
        │      ↑                                  │          │
        │      └──────────── 4.可观测/治理 ───────┘          │
        └────────────────────────────────────────────────────┘
```

1. **Guides（前馈控制，行动前引导）**
   - `AGENTS.md`、架构说明、编码规范、任务模板、工具说明、示例轨迹。
   - 作用：让 Agent 出手前更可能走对方向。

2. **执行环境（行动中约束）**
   - Docker/K8s、浏览器环境、repo checkout、git worktree、数据库快照、API mock。
   - 作用：动作可执行、可隔离、可回滚，犯错也不污染真实系统。

3. **Sensors（反馈控制，行动后检查）**
   - 计算型 sensor（便宜、确定）：单元测试、lint、类型检查、静态分析。
   - 推断型 sensor（贵、不完全确定）：语义代码审查、LLM-as-judge、人工 review。
   - 作用：告诉 Agent 哪里错了，让它自我修复。

4. **可观测性与治理**
   - trace、token/成本、工具调用记录、审批策略、权限边界、审计留痕。
   - 作用：出了问题能查、能管、能控成本。

记一个要点：**好的 sensor 要快、要局部、要结构化**——错误信息最好能直接告诉 Agent“下一步怎么改”。

## 6. 著名论文（按层次理解）

这些工作大多没用“Harness Engineering”这个新词，但共同构成了它的技术基础。按“离生产由远及近”分三层：

### 第一层：模型评测 Harness（怎么统一地比较模型）

| 论文 / 工作 | 年份 | 关系 |
|---|---|---|
| **HELM**（Holistic Evaluation of Language Models）| 2022 | 多场景、多指标、标准化评测，强调“一个分数不够，要暴露能力/风险/效率/公平多维度”|
| **lm-evaluation-harness**（EleutherAI）| 2021– | 把任务、prompt、模型适配、指标、结果管理工程化，名字里就带 harness |

### 第二层：交互环境 Harness（Agent 怎么在环境里行动并被评分）

| 论文 / 工作 | 年份 | 关系 |
|---|---|---|
| **ReAct**（Reason + Act）| 2022 | Reason→Act→Observe 循环，是 Agent harness 的基本交互范式 |
| **Toolformer** | 2023 | 模型自学“何时调哪个工具、如何吸收结果”，为工具 harness 提供学习范式 |
| **WebArena** | 2023 | 自托管真实 Web 环境 + 812 个任务，展示 browser agent 需要的环境 harness |
| **AgentBench** | 2023 | 用 8 类交互环境（OS/DB/KG/网页等）评测 LLM-as-Agent |
| **ToolLLM / ToolBench** | 2023 | 3,451 工具、16,464 API、126,486 实例的工具学习与评测平台 |

### 第三层：软件工程 / Coding Agent Harness（最靠近真实工作）

| 论文 / 工作 | 年份 | 关系 |
|---|---|---|
| **SWE-bench** | 2023 | 把真实 GitHub issue 变成可评测任务：改代码 + 跑测试判定是否解决 |
| **AutoGen** | 2023 | 多 Agent 对话 + 工具 + 人类输入 + 外部执行，组织成应用框架 |

一个震撼的数据点：在 **SWE-bench 最初的论文里，当时最强的模型只解决了约 1.96% 的真实 GitHub issue**。后来这个 resolved rate 大幅提升，靠的不只是模型变强，更是 Agent 工作流、repo 环境、patch 生成、测试执行和错误恢复（也就是 harness）的改进。这正是“harness 比换模型更关键”的最佳证据。

## 7. 著名项目（工程实现）

| 项目 | 维护方 | 关键能力 | Harness 启示 |
|---|---|---|---|
| **lm-evaluation-harness** | EleutherAI | 60+ benchmark、多模型后端、YAML 任务、缓存 | 评测 harness 的基础模板：标准化任务/适配/指标 |
| **HELM** | Stanford CRFM | living benchmark，多场景多指标 | 不只给分数，要暴露多维度能力与风险 |
| **OpenAI Evals** | OpenAI | 私有 eval、model-graded eval | 把真实业务工作流转成可重复回归的评测 |
| **Inspect AI** | UK AI Security Institute | Dataset/Solver/Scorer/Task + Docker/K8s 沙箱 | 生产级评测要有沙箱、工具审批、可视 transcript |
| **SWE-bench** | SWE-bench Team | 2,294 真实 issue（Verified/Lite/Multilingual 等子集）| coding agent 要用真实 repo + 测试 + resolved rate 验证 |
| **WebArena** | WebArena Team | 自托管购物/后台/GitLab/地图等站点，812 任务 | browser agent 要有可复现网页环境 + 登录态 + 自动评分 |
| **AgentBench** | THUDM | 8 类交互环境 | Agent 能力 ≠ 单轮问答，要多环境多轮评测 |
| **ToolBench / ToolLLM** | OpenBMB | 海量工具/API + ToolEval | 工具调用要有检索、参数规划、执行反馈、稳定评估 |
| **AutoGen** | Microsoft | 多 Agent、事件驱动、Docker 执行、MCP 扩展 | 多 Agent 应用要有消息协议、运行时、人类介入 |
| **OpenHands** | OpenHands | 自托管 coding agent 控制台，支持多种 Agent | coding agent 正走向“常驻工程团队”式编排控制台 |

从这些项目能抽象出一个**通用 Harness 架构**：

```text
任务层  -> 定义输入、目标、约束、评分标准
适配层  -> 把不同模型/Agent/工具/浏览器/repo 接到统一接口
执行层  -> 沙箱、依赖、数据库、浏览器、repo checkout、资源限制
观察层  -> 记录每步 prompt/response/tool call/stdout/截图/成本
评分层  -> 确定性测试 + 规则匹配 + LLM-as-judge + 人工
治理层  -> 权限、审批、数据隔离、审计、回滚、CI/CD
```

## 8. 如何落地：从小到大三步

### 第一步：把隐性经验外显化

给项目写一份 `AGENTS.md`：怎么装依赖、怎么跑最小测试、哪些目录不能动、常见坑、API 怎么用、代码风格、PR 标准。

> 重点不是写长文档，而是把 Agent 反复犯错的地方，变成短、准、可执行的规则。

### 第二步：建立快速反馈（做 sensors）

把最常用的验证动作做成 Agent 能一键调用的脚本：

```text
check / test:changed / lint:fix / typecheck / screenshot / run-e2e-one
```

原则：先用便宜确定的“计算型 sensor”（测试、lint、类型检查），把昂贵的“推断型 sensor”（LLM 审查、架构评审）放更靠后。

### 第三步：把 Agent 放进可控执行环境

```text
Coding Agent ：每任务独立 git worktree、容器化依赖、读写目录分离、
               自动回滚、CI 门禁、审计日志
Browser Agent：自托管网站副本、固定初始状态、自动登录、HAR 记录、
               截图轨迹、完成断言
Tool Agent   ：工具 schema、参数校验、速率限制、API mock、
               敏感操作审批、结构化返回
```

## 9. 为什么这比“换更强模型”更重要

```text
很多失败的真正原因：
  环境不可读、工具不可用、反馈太慢、权限过大、任务不可验证
这些都不是"模型智商"问题，而是 harness 问题。
```

- SWE-bench 早期最强模型只解 ~1.96%，靠 harness 改进后大幅提升。
- ToolBench 显示工具性能不只看模型，还看工具检索/轨迹/评测器/API 稳定性。
- HELM / lm-evaluation-harness 显示即使只评测基础模型，也得统一 prompt/适配/指标/缓存，否则分数不可比。

一句话：**当模型越来越强，竞争会越来越多地体现在“谁能把模型放进更好的工作系统里”。** Harness Engineering 就是 AI 时代的软件工程杠杆。

## 10. 局限与风险

- **不是成熟学科**：它是 2026 年工程社区快速形成的术语，和 context/eval engineering、LLMOps 有重叠，边界还在变。
- **会制造虚假安全感**：测试通过 ≠ 行为正确；LLM-as-judge ≠ 客观真值；benchmark 高分 ≠ 真实生产可用（存在数据污染、任务代表性、评分覆盖问题）。
- **Harness 自身会变成技术债**：规则、脚本、prompt、CI、评测数据如果不做版本管理，会堆成新的复杂度。好的 harness 应当可测试、可维护、可观测、可迭代。

## 11. 本章小结

Harness Engineering = **为 AI Agent 设计外部控制系统**。记住三件事：

```text
1. Agent = Model + Harness（模型之外的一切都是 harness）
2. 四大件：Guides(前馈) + 执行环境 + Sensors(反馈) + 可观测/治理
3. 落地三步：经验外显化(AGENTS.md) -> 快速反馈(脚本/测试) -> 可控环境(沙箱/权限)
```

最实用的起点不是追新名词，而是：**把 Agent 反复犯错的地方，沉淀成文档、脚本、测试、沙箱和 CI 反馈，让每次错误都改进下一次的执行环境。**

## 参考论文与项目

论文：
- HELM — Holistic Evaluation of Language Models, 2022. https://arxiv.org/abs/2211.09110
- ReAct: Synergizing Reasoning and Acting in Language Models, 2022. https://arxiv.org/abs/2210.03629
- Toolformer: Language Models Can Teach Themselves to Use Tools, 2023. https://arxiv.org/abs/2302.04761
- SWE-bench: Can LMs Resolve Real-World GitHub Issues?, 2023. https://arxiv.org/abs/2310.06770
- WebArena: A Realistic Web Environment for Building Autonomous Agents, 2023. https://arxiv.org/abs/2307.13854
- ToolLLM (ToolBench), 2023. （OpenBMB）
- AgentBench: Evaluating LLMs as Agents, 2023.
- AutoGen: Next-Gen LLM Applications via Multi-Agent Conversation, 2023. https://arxiv.org/abs/2308.08155

项目：
- EleutherAI lm-evaluation-harness — https://github.com/EleutherAI/lm-evaluation-harness
- Stanford CRFM HELM — https://crfm.stanford.edu/helm/
- OpenAI Evals — https://github.com/openai/evals
- Inspect AI (UK AISI) — https://inspect.aisi.org.uk/
- SWE-bench — https://www.swebench.com/
- WebArena — https://github.com/web-arena-x/webarena
- AgentBench (THUDM) — https://github.com/THUDM/AgentBench
- ToolBench (OpenBMB) — https://github.com/OpenBMB/ToolBench
- AutoGen (Microsoft) — https://microsoft.github.io/autogen/stable/index.html
- OpenHands — https://github.com/OpenHands/OpenHands

观点来源：
- Mitchell Hashimoto, "My AI Adoption Journey"（Engineer the Harness）— https://mitchellh.com/writing/my-ai-adoption-journey
- Birgitta Böckeler, "Harness engineering for coding agent users"（Agent = Model + Harness）— https://martinfowler.com/articles/harness-engineering.html
