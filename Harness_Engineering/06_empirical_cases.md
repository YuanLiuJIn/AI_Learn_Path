# 工业级实战案例：Harness Engineering 的落地证据

> 本文收集了 Harness Engineering 在真实工业场景中的落地案例，从 OpenAI、Stripe、Cursor、Vercel 到腾讯内部的实践。
> 核心观点：好 Harness = 免费升级几代模型。比换模型更关键。

## 1. 核心数据：改壳不改模，性能翻倍

| 实验/团队 | 改进 | 唯一变量 |
|---|---|---|
| Nate B Jones | 编程基准 42% → 78% | **仅更换 Agent Harness** |
| LangChain (Terminal Bench 2.0) | 52.8% → 66.5%，排名 30 → 前 5 | **优化 Harness** |
| Pi Research | 一个下午 15 个 LLM 编码表现整体提升 | **统一优化 Harness** |
| Vercel | 准确率 80% → 100% | **工具从 15 个精简到 2 个** |
| miloguo (腾讯 AMS) | 编码基准 6.7% → 68.3% | **只改工具接口格式** |

> 这些数据反复验证同一个结论：**模型之外的工程系统，对最终效果的影响远超模型本身的代际差异。**

## 2. OpenAI Codex：5 个月、7 人、100 万行、0 行人类代码

> 来源：OpenAI 官方 Harness Engineering 系列

这是目前最震撼的 Harness Engineering 案例——OpenAI 用 Codex Agent 在 5 个月内生成了约 100 万行代码，完成了约 1500 个 PR，**人类工程师写了 0 行代码**。

### 关键实践

**① 仓库即大脑（Repo as Brain）**

没有进 codebase 的知识 = 不存在。项目架构、规范、约定全部要形式化成文件放进仓库。

```text
project/
├── AGENTS.md          ← Agent 的"入职手册"（约百行，不是百科全书）
├── docs/
│   ├── architecture/  ← 架构决策、模块职责
│   └── conventions/   ← 编码规范、命名约定
├── scripts/           ← Agent 可调用的工具脚本
└── tests/             ← Agent 改代码后立即验证
```

**② AGENTS.md 是"地图"不是"操作手册"**

```markdown
# AGENTS.md（约百行）

## 项目结构
- src/api/：对外 HTTP API（RESTful，OpenAPI 3.1）
- src/core/：业务逻辑（纯函数，不依赖框架）
- src/db/：数据访问层（PostgreSQL，使用 sqlc 生成）

## 约束
- Never 修改 src/generated/ 下的文件（自动生成）
- Always 先运行 npm test -- --changed 再做 commit
- 新功能 Always 先写测试
- 使用 pnpm，不是 npm

## 常见坑
- env.d.ts 的环境变量类型需要和 .env.example 同步更新
- 数据库迁移用 prisma migrate，不要手动改 schema
```

**③ 强分层 + 静态约束**

```text
架构硬约束（靠 linter 而非 prompt 保证）：
- API 层不能 import 数据库层
- Core 层不能依赖框架
- 用 eslint-plugin-boundaries 强制分层
```

**④ CI 错误信息内嵌修复指引**

普通 CI 报错：
```
ERROR: src/api/users.ts:32 - Type 'string' is not assignable to type 'number'.
```

被 OpenAI 改造后：
```
ERROR: src/api/users.ts:32 - Type 'string' is not assignable to type 'number'.
→ 修复：将第 32 行的 parseInt(req.params.id) 改为 Number(req.params.id)
→ 相关文档：docs/types.md#user-id-type
→ 上次类似修复：commit a1b2c3d
```

**⑤ 持续的"工程化修补"（Engineer the Harness）**

> Mitchell Hashimoto 核心理念：当 Agent 犯错时，不只是修正这次错误，而是花功夫工程化一个方案，让它以后再也不会犯同类错误。

- 第一次忘了跑 lint → 把 lint 加进 agent 的工具链（自动执行）
- 第一次用错包管理器 → 在 AGENTS.md 写死规则
- 第一次改了生成文件 → 在 linter 里加"禁止修改 src/generated/"规则

## 3. Stripe "Minions"：每周 1300+ 无人值守 PR

> 来源：Stripe Engineering Blog

### 核心架构

```text
Blueprint（流水线模板）
  │
  ├── 确定性节点（不调 LLM）
  │   ├── 跑 linter
  │   ├── 推送到 CI
  │   └── 合并结果
  │
  └── Agentic 节点（调 LLM）
      ├── 实现功能
      ├── 修复 CI 失败（最多两轮）
      └── 仍失败 → 交人类
```

### 关键数据

- 每周 1300+ 无人值守 PR
- Toolshed 注册了约 500 个工具，但只给 Agent 精选子集
- CI 最多两轮自动修复，仍失败就交给人

### 启示

> 对人类工程师友好的环境（清晰的文档、稳定的测试、明确的规范），对 LLM 同样友好。**好的工程基础设施，人机共享。**

## 4. Cursor "Self-Driving Codebases"：峰值 1000 commit/h

> 来源：Cursor Engineering Blog

### 演进历程（5 次 Harness 重构）

```
V1: 简单 Agent Loop → 卡死/上下文爆炸
V2: 加 Checkpoint → 能恢复了，但质量不稳
V3: Planner + Worker 分离 → 大任务能拆了
V4: 递归 Planner + Worker，隔离上下文 → 大规模代码库可处理
V5: 每个 Agent 在独立仓库副本中工作 → 峰值 1000 commit/h
```

### 核心架构

```text
Planner Agent（只看大局）
  ├── 分析 issue
  ├── 拆成子任务
  └── 派发给 Worker

Worker Agent（只改局部）
  ├── 克隆仓库副本
  ├── 在一个隔离上下文中工作
  ├── 改代码 → 跑测试 → git commit
  └── 提 PR（由 Planner 审核）

Evaluator Agent（只负责评判）
  ├── 独立 QA
  ├── 运行完整测试套件
  └── 通过/拒绝 PR
```

### 启示

> Harness 不是一次设计成的，而是**持续重构演化的控制系统**。5 次重构才走到今天的架构。

## 5. 腾讯内部案例

### 5.1 微信支付：5 天补齐 4 万行文档（zesui 团队）

> 来源：KM 文章 "5 天补齐 4 万行文档！用多 Agent 架构跑通 Harness Engineering 实战"

**背景**：65 个老模块没有文档，AI 每次都要从头读几万行源码，烧掉的 Token 和返工时间远超想象。

**方案**：用 OpenClaw + Claude Code 搭建多 Agent 文档生成流水线：

```
文档规划 Agent → 代码分析 Agent → 文档编写 Agent → 文档审核 Agent
```

**成果**：
- 5 天内 65 个模块全部补齐文档
- 总计约 4 万行文档
- 沉淀出"踩坑 → 沉淀规范 → 自动继承"的 AI 协作方法论

**核心 insight**：
> AI 时代，文档不是不重要了，而是变成了给 AI 看的"工作记忆"。

### 5.2 系统技术团队：几千个 Agent 并发调度（zorrozou 团队）

> 来源：KM 文章 "让 AI 管理 AI 跑几千个 agent，调度系统当场失控"

**问题**：当 sub-agent 数量从几十膨胀到几千时，简单的 spawn 模式直接失控。

**解决**：
- 三套 Prompt 设计原则：任务边界清晰、上下文传递结构化、失败隔离
- Harness Engineering 设计原则：**每个 Agent 看到的必须是最小必要上下文**

**启示**：
> 多 Agent 的难点不是"怎么造 Agent"，而是"Agent 之间的通信、状态管理和失败隔离"——这恰好是 Harness Engineering 的核心课题。

### 5.3 腾讯知点：Context / Harness Engineering 实践（dorismo）

> 来源：KM 文章 "Context / Harness Engineering：AI Agent 的上下文工程"

提出了 Harness Engineering 与 Context Engineering 的递进关系：
```
Prompt Engineering  → "这句话怎么说更好？"           (2022-2024)
Context Engineering → "模型这次应该看见哪些信息？"    (2025)
Harness Engineering → "整个系统怎么让 Agent 稳定运行？" (2026起)
```

## 6. 经验教训汇总

### 6.1 共同的成功模式

```text
1. 文档先行：AGENTS.md 写得越好，Agent 表现越稳定
2. 测试兜底：Agent 改完代码必须自动跑测试，不能靠"它说完成了"
3. 小步快跑：每次只做一个 feature，短闭环频繁合并
4. 约束落地：能硬编码的规则不要靠 prompt（用 linter/CI/权限）
5. 持续修补：Agent 每条犯错都找机会"工程化解决"
```

### 6.2 常见的失败模式

```text
1. 把所有规则写进 Prompt   → 约束应在 linter/CI/sandbox/权限里
2. 一次给 Agent 太多工作    → 每次只做一件事，做完立即验证
3. 不做 Checkpoint         → 跑了 2 小时崩了重来 = 浪费
4. 不跟踪 token/成本        → 跑着跑着账单爆了
5. 没有独立验证             → 模型说"完成了" ≠ 真的完成了
```

## 7. Big Model vs Big Harness 路线之争

这是 Harness Engineering 社区最核心的辩论：

### "拐杖论"（Big Model 派）

Noam Brown (OpenAI)：很多复杂 Agentic 系统是在推理模型之前搭的，新一代推理模型出来后，"花哨脚手架很多不仅不再需要，甚至拖后腿"。

证据：METR 评估显示，维护者真正愿意合并的 Agent PR 只相当于自动评分通过的一半左右。高级 Harness 与简单脚手架在 SWE-bench 上差距不显著。

### "护栏论"（Big Harness 派）

时速 30 可以没护栏，时速 300 必须全线封闭——引擎越强、速度越快，护栏越重要。

证据：上面六个实证案例全部指向"harness 比模型更重要"。

### 综合判断

```text
- "复杂编排/多层路由"的脚手架确实有被更强模型淘汰的趋势
- "控制论意义上的 Harness"（状态/约束/工具/安全/验证）不会消失，
  只会标准化下沉为基础设施
- 真正的风险是"花 6 个月造一个又厚又僵硬的 Harness"
- 理想：Harness 提供稳定原语（环境/工具/状态/日志），
  上层策略可快速实验重写 —— Start simple, build to delete
```

## 8. 一句话总结

> 工业级证据反复证明：在 AI Agent 这个领域，**工程系统 > 模型代际**。OpenAI Codex 用 7 个人 5 个月写出 100 万行代码，靠的不是"换了更强的模型"，而是把 Harness 做到了极致。
