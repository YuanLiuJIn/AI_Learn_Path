# Harness Engineering 进阶：把 Agent 当作一个小型操作系统来设计

> 本文是 `harness_engineering_guide.md`（入门）的进阶篇，聚焦**生产级系统设计**：确定性外壳、Task Loop 状态机、Checkpoint/幂等、五大子系统、控制论视角、实证案例与工程原则。
> 配套实践项目：`mini_harness_project/`。

## 1. 为什么现在要谈 Harness

当大模型已经能读代码、写前端、连数据库、驱浏览器，真正拉开差距的不再是“能不能生成一个像样的答案”，而是“能不能在真实系统里，稳定地把一件复杂事做完”。

这层差距**不在模型参数里，而在模型外面的工程系统里**。OpenAI 把它叫 Harness，Anthropic 和大量一线团队也在用同一个词。比喻来自“马具”——不是马本身，而是让马力可控、可持续地输出到车上的那套结构。

只要把 Agent 放进生产，几乎所有团队都会撞上同一批问题：

```text
Demo 惊艳，上线即崩：循环卡死、工具乱用、任务半途而废
跨天长任务无法延续：一断会话就"失忆"
代码库被 AI 写碎：风格不一致、架构漂移、测试常挂
审计与回溯不可能：出问题不知道从哪一步开始跑偏
```

共同点是：**这些都不是模型智商问题，而是系统工程问题**。所以业界用一个统一的词指代“模型外面的所有东西”——Harness。

```text
Agent = Model + Harness
如果你不是模型，那你就是 Harness。
```

## 2. 核心定义：模型外面的“操作系统”

> Harness：包裹在模型外部，使其能在真实环境中长期、安全、可控执行任务的系统层。
> 更正式地说：围绕 LLM/Agent 构建的**确定性控制系统**，使其在不确定的模型内核之上，仍能长期、可恢复、可审计地完成复杂任务。

它不是某个库，而是一整套系统能力的组合：上下文注入、工具与执行环境、控制与编排、持久化与状态、观察与验证。

最好用“计算机四件套”来类比：

| 类比 | 对应 |
|---|---|
| CPU | Model（算力与决策）|
| 内存 | 上下文窗口（短时工作区）|
| 操作系统 | Harness Runtime（资源管理、调度、约束、I/O）|
| 应用程序 | Agent（跑在“AI OS”上的具体智能体）|

一句话：**模型决定“上限能做什么”，Harness 决定“实际能做成多少、能撑多久”。**

## 3. Prompt → Context → Harness：问题维度的升级

| 阶段 | 时间 | 核心问题 |
|---|---|---|
| Prompt Engineering | 2022–2024 | 这句话怎么说更好？ |
| Context Engineering | 2025 | 模型这次应该看见哪些信息？ |
| Harness Engineering | 2026 起 | 整个系统怎么运行，才能让模型在几小时、多轮、多工具、多会话下仍稳定交付？ |

> Prompt 让模型能动，Harness 让 Agent 能撑住。

## 4. 模型边界：为什么必须有 Harness

大模型本质就是一个函数：

```text
f: (文本, 图像, 其他模态) -> 文本 / 结构化 token 序列
```

因此它天然**不具备**：长期记忆（只看到当前上下文窗口）、外界执行能力（不能直接跑代码/读写文件/联网）、状态持久化（每次调用是无副作用的函数）、安全隔离（不知道哪些操作危险）。任何超出“函数本身”的能力，都必须由 Harness 提供。

### 最小 Agent Loop：为什么 Demo 能跑，生产就崩

```python
while not finished:
    observation = environment()
    thought = model(observation)
    action = choose_action(thought)
    result = run_tool(action)
    update_state(result)
```

短 Demo 尚可，但有致命缺陷：无进度感知、无阶段划分、无系统级失败恢复、终止完全靠模型“感觉”、context rot（历史越积越多淹没关键信息）、单次崩溃整个长任务报废。这些都不是“模型不够聪明”，而是“没有架子让它长时间可控工作”。

## 5. 核心哲学：确定性外壳 vs 非确定性内核

> 用一个尽可能**确定性的外壳（deterministic shell）**，包裹一个能力强但**非确定的模型内核（stochastic core）**，让系统整体表现出可预测、可恢复、可审计的行为。

| 层 | 职责 |
|---|---|
| 内核（LLM/Agent）| 自然语言理解生成、复杂规划、代码与文档撰写 |
| 外壳（Harness）| 任务生命周期管理、资源预算与限流、错误分类/重试/回滚、状态持久化与检查点、工具权限与安全、审批与人机协作 |

**最常见的误区是“把所有逻辑都 prompt 化”**：在系统提示里写“请不要删除文件”。短对话尚可，几百步长任务里概率性违约几乎必然发生。

```text
原则：凡是能用确定性机制表达的约束，就不要只写在 Prompt 里。
- 文件只读/只写某目录 -> sandbox + allowlist
- 删除操作       -> 单独 tool + 人工确认
- 网络访问       -> MCP / Tools 白名单过滤
```

### 与传统软件工程的本质差异

| 维度 | 传统软件工程 | Harness Engineering |
|---|---|---|
| 核心执行体 | 确定性代码，可静态分析 | LLM：概率性、会幻觉 |
| 推理与控制 | 都在代码里 | 推理在 LLM 内部，控制留在外壳（状态机/检查点/回滚/重试）|
| 状态管理 | 内存/存储对象 | 还多了“语言上下文”，需决定哪些持久化、哪些动态注入 |
| 评估验收 | 单元/集成测试 + Code Review | LLM Evaluator + 工具做自我 QA，evaluator 本身也要调教 |

> 软件工程假定核心逻辑确定、不确定性在外界；Harness 假定核心执行者本身就概率、会犯错——目标从“让程序按 spec 跑”变成“在一个不可靠但聪明的执行体上，构建可靠系统”。

## 6. Task Loop：长任务执行引擎

Task Loop 是 Harness 在长任务上的核心体现——从“无状态 Agent Loop”进化到“任务级管理系统”。

### 6.1 它是一个显式状态机（运行在模型外部）

```text
INIT → PLANNING → EXECUTING → QA → FIXING → HUMAN_REVIEW → DONE / FAILED
```

模型只在特定状态被调用做“思考+生成”，状态转移由控制层（harness 代码）驱动。

### 6.2 Checkpoint（检查点）与幂等性

长任务必须接受的现实：**中断几乎必然发生**（网络波动、限流、重启、部署）。Checkpoint 做两件事：周期性持久化任务状态、提供可恢复入口。

```python
def save_checkpoint(task):
    snapshot = {
        "task_id": task.id, "state": task.state, "plan": task.plan,
        "current_feature_idx": task.idx,
        "artifacts": {"git_commit": "a1b2c3d", "test_report": "reports/s3.json"},
        "budget": {"tokens_used": 3_200_000, "tokens_max": 10_000_000},
        "progress_log": task.progress_log,
    }
    db.put(f"checkpoint:{task.id}", json.dumps(snapshot))

def start_or_resume(task_id, goal):
    cp = db.get(f"checkpoint:{task_id}")
    return deserialize(cp) if cp else Task(goal=goal)   # 有存档就断点续跑
```

关键认知：**模型对 Checkpoint 毫无感知**。存/取/注入全是 harness 硬编码的确定性逻辑（像游戏自动存档点，模型不需要“决定”是否存档）。模型看到的“已完成 Sprint 1-3”，不是它记住的，而是 harness 从 checkpoint 读出来塞给它的——这正是“确定性外壳 vs 非确定性内核”的体现。

> Checkpoint ≠ 上下文压缩。压缩仍在同一会话里把早期对话总结成摘要；Checkpoint 是把状态写出模型、交给系统保存，新会话只注入必要片段。

**幂等性**：恢复后对外部世界的副作用不能重复。发邮件前先写 outbox 表、发送后标记 sent，重放时只处理 `sent=false`；支付/工单用业务 idempotency key 保护。

### 6.3 系统级错误分类与恢复

不要把错误字符串塞回上下文让模型自行决定——模型可能把临时故障当永久失败，也可能对确凿错误视而不见。

| 类别 | 场景 | 策略 |
|---|---|---|
| A 临时性 | 超时、短期限流 | 指数退避重试，限次数 |
| B 幂等可回滚 | 写中间状态失败 | 回滚到上一个 checkpoint |
| C 权限/安全 | 越权访问 | 直接 fail + 触发人工检查 |
| D 逻辑错误 | 代码 bug、设计缺陷 | 生成详细 bug 描述交给 Generator 修复 |

LLM 的角色变成“生成修复方案”，而不是“自己当错误分类器+调度器”。

### 6.4 资源管控与终止条件

```python
MAX_STEPS = 200
MAX_TOKENS = 10_000_000
if state.steps > MAX_STEPS or state.tokens > MAX_TOKENS:
    state.status = "FAILED"; state.reason = "budget_exceeded"
```

终止判定不能只靠 LLM“我觉得完成了”：编码任务以测试全过为准；UI 以 Playwright 清单通过为准；数据任务以校验查询通过为准。

### 6.5 人机协作节点（Human-in-the-Loop）

不可逆操作（删库、批量退款、群发邮件）、超预算、高风险修改必须人来拍板。Task Loop 设计 `WAITING_HUMAN` 状态：记录 snapshot → 向审批 UI 发结构化问题（建议方案+风险评估+可选操作）→ 人决策后继续。

### 6.6 四条工程原则

```text
1. 规划与执行分离：路线先走通再跑；规划用强推理模型，执行用便宜模型
2. 每步都有可观测输出：输入/思考/输出/工具调用全记录，不允许黑盒 step
3. 幂等性是硬要求：任何可能被重放的动作必须幂等
4. 任务状态与模型上下文解耦：状态由系统管，模型每步只被告知"当下必需信息"
```

## 7. 生产级架构：五大子系统

多家实践（Anthropic、OpenAI Codex、LangChain、Stripe、Cursor）可抽象成五层：

```text
1. Environment   受控工作世界：文件系统、沙箱终端、浏览器(CDP)、受控网络
2. Tool System   对环境能力的抽象封装：read_file/write_file/run_test/search_code
3. Control       执行边界：步数/时长限制、循环结构约束、权限拦截、错误处理
4. Memory/State  长任务/跨会话状态：progress file、feature list、AGENTS.md、Git、长期记忆
5. Evaluation    自动化验证：单元/集成测试、Linter、UI 自动化、第二模型评审
```

### Anthropic 的两个架构模式

**模式一：两角色接力（Initializer + Coding Agent）**

```text
Initializer：建仓库 → 写 feature list → 初始化 progress file(结构化JSON,定义完成标准)
             → 配置环境脚本 → 写基础架构文档
Coding Agent：读 progress → 选一个未完成 feature → 只围绕它工作 → 跑测试
             → 更新 progress → git commit
```

要点：完成条件是结构化 JSON，每次只拿一个任务跑短闭环，所有决策写入文件和 Git。

**模式二：三 Agent（Planner + Generator + Evaluator）**

| 角色 | 职责 |
|---|---|
| Planner | 把一句短 prompt 展开为详细 spec 和多 sprint 计划 |
| Generator | 按 sprint 逐个实现 feature 并自评 |
| Evaluator | 独立 QA，用 Playwright 驱动真实页面/API/DB，按预定 contract 打分 |

解决两个核心问题：长上下文衰减（用 Context Reset + 结构化 Handoff）、自评失真（把“评价”从生成者剥离，单独调教更苛刻的 Evaluator）。

## 8. 关键工程实践模式

### 8.1 Context Reset + Handoff vs Compaction

```text
Compaction：同一会话内对早期对话做摘要 —— 连续性好，但"上下文焦虑"仍在，
            错误可能以摘要形式继续污染
Handoff：   清空历史，用结构化文档(handoff.json)向新会话传递状态 —— 干净 slate
```

为什么 Handoff 更能避免错误污染：Compaction 是模型给自己写笔记，分不清对错；**Handoff 是 harness 从外部可验证事实拼出交接报告**（completed_features 看测试报告、known_issues 来自独立 Evaluator、git_commit 是真实版本），新会话没有“思维惯性”，过程噪音直接不进交接文档。

> Anthropic 经验：Sonnet 4.5 上必须用 reset，Opus 4.5+ 可依赖 compaction。但 handoff artifact 作为“状态接口”的思想始终保留。

### 8.2 Heartbeat 与 Watchdog

几小时甚至几十小时的任务必须有外部监护：Heartbeat 把健康信号（当前 step、最近成功工具调用时间、累计 token/错误）写入存储；Watchdog 独立进程监控——心跳超时就告警/恢复，发现环路（多次状态未变或震荡）触发循环检测。

### 8.3 工具编排与并发

```python
def dispatch_tool_call(agent, tool, args):
    policy = TOOL_POLICIES[tool]
    if not policy.allowed_for(agent):
        raise SecurityError("tool not allowed")
    if policy.mutation and not acquire_lock(policy.resource_key(args)):
        raise TemporaryError("resource locked")
    return tools[tool](args)
```

按风险分组（只读/高风险写/系统）、按角色控制可见性（Planner 不给数据库写权限）、对会冲突的写操作加锁串行化。

### 8.4 并发模式

```text
队列 + Worker Pool         ：高吞吐、任务独立，每个 worker 内部仍是 Task Loop
Session per branch/worktree：OpenAI 做法，每次改动起一个 git worktree，跑完经 PR 合并
多 Agent 分职责并行         ：Evaluator 跑 QA 时 Planner 预拆下一块，harness 协调交接点
```

## 9. 控制论视角：第三次历史重演

| 时代 | 系统 | 变化 |
|---|---|---|
| 18 世纪 | 瓦特离心调速器 | 工人从“实时拧阀门”→ 设计调速器自动调节 |
| 2010s | Kubernetes 控制器 | 从“手动重启/扩容”→ 声明期望状态，自动收敛 |
| 2026 | Harness Engineering | 从“逐步提示 Agent”→ 设计环境/约束/反馈回路，Agent 自动运行 |

反馈回路在更高一层闭合，人的工作从“亲手调参”变成“设计控制系统”。大模型首次让“架构决策与长期演化层”的反馈闭合成为可能——但要形成闭环，必须由 Harness 提供**传感器**（架构文档、依赖图、测试结果、监控）和**执行器**（代码修改权限、重构工具、CI/CD）。

## 10. 实证数据与真实案例

### 10.1 改壳不改模，性能翻倍

| 实验 | 结果 | 唯一变量 |
|---|---|---|
| Nate B Jones | 编程基准 42% → 78% | 仅更换 Agent Harness |
| LangChain (Terminal Bench 2.0) | 52.8% → 66.5%，排名 30 → 前 5 | 优化 Harness |
| Pi Research | 一个下午 15 个 LLM 编码表现整体提升 | 统一优化 Harness |
| Vercel | 准确率 80% → 100% | 工具从 15 个精简到 2 个 |

> 好 Harness = 免费升级几代模型。

### 10.2 工业级案例

```text
Stripe "Minions"：每周 1300+ 无人值守 PR。Blueprint 把流水线拆成
   确定性节点(跑 linter/推送，不调 LLM) + Agentic 节点(实现/修 CI)。
   CI 最多两轮，仍失败交人类。Toolshed 注册 ~500 工具，只给 Agent 精选子集。
   结论：对人类工程师友好的环境/测试/反馈，对 LLM 同样友好。

Cursor "Self-Driving Codebases"：峰值 ~1000 commit/h。经历 5 次 Harness 重构，
   最终是"递归 Planner + Worker，每个 Agent 在隔离上下文与仓库副本中工作"。
   结论：Harness 不是一次设计成的，而是持续重构演化的控制系统。

OpenAI Codex：5 个月、7 个工程师、~100 万行、~1500 PR，人类零行代码。
   关键实践：仓库即大脑(没进 codebase 的知识=不存在)、AGENTS.md 作"地图"(约百行)、
   强分层架构+静态约束(linter 拦截)、可观测性接进 Agent、CI 错误信息内嵌修复指引、
   持续"工程化修补"。最大挑战不是写代码，而是设计环境、反馈循环和控制系统。
```

### 10.3 同任务对比：单 Agent vs Harness

构建一个 2D retro 游戏编辑器：

| 维度 | 单 Agent | Harness（三 Agent）|
|---|---|---|
| 时长/成本 | 20 分钟 / ~$9 | 6 小时 / ~$200 |
| 实际质量 | 实体无响应，fillRectangle 未正确触发 | 功能丰富、真正可玩 |

模型和 prompt 都没变，差别全在 Harness。Evaluator 的 bug 报告能精确到函数级（“fillRectangle 存在但 mouseUp 时未正确触发”）。

> Harness 的真正价值不是提升模型能力，而是让能力有机会转化为“真正完成的产品”。

## 11. 反模式与常见陷阱

```text
1. 把所有规则都写进 Prompt   -> 约束应落在 linter/CI/sandbox/状态机/权限里
2. 只追求"多 Agent"忽略 Task Loop -> 先用单 Agent 把长任务跑稳，再按责任引入 Agent
3. 把长期状态只放上下文里    -> 引入外部 Task Store，每步只注入必要片段
4. 没有系统级 QA，只让模型自评 -> 独立 evaluator + 真实运行(pytest/Playwright)
5. 没有幂等性，Checkpoint 一恢复就乱套 -> 业务级幂等 key，记录已完成的外部动作
```

## 12. 路线之争：Big Model vs Big Harness

**“拐杖论”（Noam Brown / OpenAI）**：很多复杂 Agentic 系统是在推理模型之前搭的，新一代推理模型出来后“花哨脚手架很多不仅不再需要，甚至拖后腿”。METR 评估也显示：维护者真正愿意合并的 Agent PR 只相当于自动评分通过的一半左右；高级 Harness 与简单脚手架在 SWE-bench 上差距并不显著。

**“护栏论”（Big Harness）**：时速 30 可以没护栏，时速 300 必须全线封闭——引擎越强、速度越快，护栏越重要。约束还能提升效率（清晰架构+有限工具+严格测试让模型更快收敛，避免在死胡同浪费 token）。

**综合判断**：

```text
- "复杂编排/多层路由"的脚手架确实有被更强模型淘汰的趋势
- "控制论意义上的 Harness"(状态/约束/工具/安全/验证)不会消失，只会标准化下沉为基础设施
- 真正的风险是"花 6 个月造一个又厚又僵硬的 Harness"
- 理想状态：Harness 提供稳定原语(环境/工具/状态/日志)，上层策略可快速实验与重写
            —— Start simple, build to delete
```

## 13. 五大工程原则（落地心法）

```text
1. 尽量减少模型需要记住的内容：状态存 harness 持久化层，模型只关心当下决策
2. 把规则写进系统而非 prompt：  "必须做到"的事由系统强制（CI 必跑测试、linter 拦跨层依赖）
3. 工具接口尽可能简单：         复杂操作拆成小工具（read_file+write_file 比超级工具更稳）
4. 任务状态必须持久化：         feature list + progress file，崩溃后从文件恢复
5. 系统必须可观测、可诊断：     记录每轮调用/状态变更/资源/错误，形成"失败→诊断→Harness化"闭环
```

## 14. 从 0 到 1 构建路线图

```text
第1步 最小可用 Harness：隔离环境(仓库副本+sandbox) + 2~3 个基础工具 + 简单 Agent Loop
第2步 把"经验"写进 Harness：每次可复现的错 -> 写回系统
       缺文档→补 AGENTS.md / 工具有坑→改接口 / 缺约束→加 linter/test / 缺验证→加测试
第3步 拆出 Control / Memory / Evaluation：状态机+硬边界 / progress file+恢复 / 自动化验证
       （这一步是"能跑 Demo"到"敢跑生产"的分水岭）
第4步 引入多 Agent 与角色接力：仅在任务天然分层/分角色时才有价值
```

最值得先做的五件事：建统一 AI 知识入口(AGENTS.md 指向 docs)、把能硬编码的约束移出 Prompt、设计最小但完整的 Task Loop(每节点有日志+checkpoint)、引入至少一个独立 Evaluator、从真实错误持续工程化修补。

## 15. 适用场景与边界

```text
不需要 Harness：单轮问答/写作、不依赖真实环境的探索、一次性无状态无审计操作
值得投入   ：长周期(跨会话/跨天)、多步多工具、高置信度(出错代价高)、需审计回滚、多Agent协作
```

## 16. 与本项目 MiniHarness 的对应

`mini_harness_project/` 是本文概念的最小可运行实现，对照学习：

| 本文概念 | MiniHarness 对应 | 进阶练习 |
|---|---|---|
| 确定性外壳 vs 非确定性内核 | `agent.py` 编排 + `llm.py` 模型 | 把硬约束从 prompt 移到代码 |
| 五大子系统 | sandbox/tools/agent/trace/sensors | 补齐 Memory（progress file）|
| Task Loop 状态机 | 当前是简单循环 | 改造成 INIT→EXEC→QA→FIXING→DONE 状态机 |
| Checkpoint/幂等 | 暂未实现 | 加 `save_checkpoint` + 断点续跑 |
| 独立 Evaluator | `sensors.py` 跑测试 | 加一个 LLM-as-judge evaluator |
| 可观测性 | `trace.py` JSONL | 加 Heartbeat 与预算统计 |

建议路线：先跑通 MiniHarness（看清最小闭环）→ 按上表逐项把它升级成“小型 Task Loop 系统”，每加一块就回看本文对应章节。

## 17. 一页总结

```text
1. Agent = Model + Harness：模型是大脑，Harness 是操作系统与骨架
2. 模型边界决定 Harness 必要性：无状态/不能执行/无长期记忆 → 都要 Harness 补
3. 核心哲学：确定性外壳 包裹 非确定性内核
4. 生产级 Harness 像小型 OS：Environment→Tools→Control→Memory→Evaluation
5. Task Loop 是长任务引擎：分解→检查点→错误恢复→资源管控→人机协作
6. 实证：壳比模重要（换壳不换模，42%→78%）
7. 本质是控制论：在更高层闭合反馈回路
8. 五大原则：减记忆、规则进系统、工具简单、状态持久化、全可观测
9. 适用：长、复杂、高置信度、需审计的任务
10. 未来：通用 Harness Runtime、领域模板、Agent 管理者角色
```

## 参考资料

- OpenAI, "Harness Engineering". https://openai.com/zh-Hans-CN/index/harness-engineering/
- Anthropic, "Harness design for long-running agents". https://www.anthropic.com/engineering/harness-design-long-running-apps
- Birgitta Böckeler, "Harness engineering for coding agent users", martinfowler.com
- Mitchell Hashimoto, "My AI Adoption Journey"（Engineer the Harness）
- CMU/Yale/Amazon 等, *Harness 工程综述*（ETCLOVG 七层）, 2026
- 实证与案例：Stripe Minions、Cursor Self-Driving Codebases、OpenAI Codex、LangChain Deep Agents、Vercel、METR、Pi Research、Nate B Jones
