# Skill 也能 SFT？——Skill-Evolver 详细解读

> 来源文章：《Skill 也能 SFT？与其口把口教，不如让它自己进化》（作者 serriezhang）
> 核心仓库（公开）：https://github.com/FishSerrie/skill-evolver （v0.6, MIT）

---

## 〇、一句话核心

Skill 不应是手工打磨的工艺品，而应是「可被训练、可被回滚、可被择优」的对象。你只需准备数据（GT）、定好指标，剩下的交给一个自我迭代的闭环。

全文约 6000 字，前两章讲思想，第三章讲工程实践与验证。

---

## 一、为什么要「训练」Skill（动机）

### 1.1 Skill 表面像 prompt，实际更像 harness（一套系统）

随便写个 `SKILL.md` 模型就能跑，但要让它**稳定**干活就完全不同。触发边界、安全规则、`references` 一致性、脚本版本兼容……这些加在一起早已不是「写一段 prompt」，而是在搭一套系统。于是你不断加规则（MUST/NEVER），又会遇到三个崩溃点：

- **稳定性**：加了「git 状态不干净就拒绝执行」，你自己的测试环境都在 git 下，测不出「用户还没 git init」直接报错。
- **边界**：cleanup 用字符串排序，`iteration-9` 之前正常，`iteration-10` 突然排到 `iteration-2` 前面，把最新结果删了——因为你的测试从没超过 9 轮。
- **规则打架**：保护 A 场景的安全规则，把写在你自己协议文档里的 B 场景正常路径封死了。规则越多，行为越不确定，这是规则复杂度在爆炸。

### 1.2 「能跑」≠「真的好」

调三天不崩了，但它不 match 你的数据。例如用户问「员工离职后邮箱还在不在」，被路由到邮箱分类，正确答案却在通讯录章节。你不知道有多少类似问题、改了会不会弄坏别的。

> 这就像训模型不是让代码编过，是让 loss 收敛——「真的好」= behavior 匹配你的数据分布。

### 1.3 思想来源（四个外部灵感）

| 来源 | 借了什么 |
|---|---|
| Karpathy `autoresearch` | 自主迭代外循环：630 行脚本让 AI agent 迭代 LLM 训练代码，改一点、训练 5 分钟、看指标、好就留坏就回滚；两天跑 700 实验、找 20 个优化、性能 +19% → 提供 **8 阶段骨架 + 5 原则**（one metric / constrained scope / fast verification / automatic rollback / git as memory） |
| Udit Goenka 的泛化 | 把「优化训练代码」泛化成「优化任何可测量的东西」，落地到 Claude Code 生态 |
| skill-creator | 评测引擎 + 创建能力（硬依赖）：`quick_validate` 结构检查、`grader` 逐条打分、`comparator` A/B 盲审、自动生成 GT 用例 → 解决「好/坏怎么测」 |
| 斯坦福 Meta-Harness | Trace 驱动诊断：让 AI 优化另一个 AI 时，最关键的是**完整原始执行轨迹**而非摘要/分数；消融实验显示只给分数比给完整 trace 效果差 **44%** |

### 1.4 拼成 Skill-Evolver

```
Skill-Evolver = AutoResearch 的 loop 骨架 + Creator 的评测引擎 + Meta-Harness 的诊断大脑
```

- 外层：不断试错 / 回滚 / 保留
- 内层：把「好不好」测清楚
- 再用 trace 把每次失败变成可诊断证据，而非一个模糊分数

**本文的增量贡献**：5 维 AND 门控 + 分层 mutation + Meta-Harness trace 架构 + workspace git 隔离 + meta-evolution 自证。

---

## 二、设计：一个「用对话驱动的 Skill 训练框架」

### 2.1 把「训练模型」类比成「训练 Skill」

| 训练模型 | 训练 Skill |
|---|---|
| 训练集 | GT（Ground Truth，标准答案用例） |
| 梯度下降 SGD | 8 阶段循环逐轮逼近 |
| 分层学习率 / 微调粒度 | 分层 mutation（改触发词 → 改正文 → 改脚本） |

- **GT（Ground Truth）**：你为 skill 准备的标准答案，如「用户问离职邮箱，应引用 `通讯录/功能介绍.md`」。每轮拿 GT 测 skill 答对多少。
- **8 种 assertion**：GT 的检查方式。6 种程序直接判（`contains`、`regex`、`script_check`…），2 种需 LLM 做 YES/NO 分类（`path_hit`、`fact_coverage`）。
- **holdout split**：故意藏起来不给优化器看的测试集，迭代中优化器只能看 dev 集，结束再拿 holdout 验证是否真变好（防「背答案」）。
- **分层 mutation**：先改最便宜的（Layer1 触发关键词）→ 改不动再 Layer2（SKILL.md 正文）→ 还不行才 Layer3（辅助脚本/references）。每轮只动一层，不准跨层。
- 没有 GT 也没关系：可让 AI 生成，或用 skill-creator 的 eval 功能自动生成。

### 2.2 8 阶段 Loop（核心机制一）

- **Phase 0 Setup（一次性）**：检查 SKILL.md / git / GT 是否就绪，分析后自动生成 `evolve_plan.md`（评测策略、门控阈值、起始 mutation 层），决定后续所有轮次行为。
- **Phase 1 Review**：读最近 20 条 git log、20 行 results.tsv、10 条 experiments.jsonl，扫描失败 case，提取 5 个信号：成功改法（利用）/ 失败改法（避免）/ 持续失败（优先攻克）/ 脆弱 case（当回归守卫）/ 是否卡住（切激进策略）。
- **Phase 2 Ideate**：按 6 级优先级（修崩溃 → 用成功模式 → 攻克持久失败 → 探索新方向 → 简化 → 激进变异）。**硬规矩**：改动前必须引用具体 trace 做反事实诊断（「Case X 因 Y 失败，改 Z 输出就变 W」），没证据不许动手。
- **Phase 3 Modify**：只允许**一个原子化改动**（描述需用到「和」字就该拆两轮；`git diff --stat` 超 5 文件大概率非原子）。
- **Phase 4 Commit**：先 commit 再验证，保留审计轨迹。
- **Phase 5 Verify**：三层评测流水线（见 2.3）。
- **Phase 6 Gate**：5 维 AND 门控（见 2.4）。
- **Phase 7 Log**：写 `results.tsv` + `experiments.jsonl` + per-case trace。
- **Phase 8 Loop**：连续 K 轮无 keep → 升层；连续 5 次 discard → 激进策略；三层都无改善 → 终止出报告。

### 2.3 三层评测（核心机制二）

| 层级 | 成本 | 触发 | 内容 |
|---|---|---|---|
| **L1 快速门卫** | 秒级，每轮 | 每轮都跑 | 纯程序：检查 SKILL.md 结构、`quick_validate` 格式校验、11 条安全扫描（危险删除命令/硬编码密钥等）。2 条 critical 不过直接阻断，其余 warning 记录给 Phase 2。**L1 挂了直接 discard，不跑 L2**——把坏迭代成本压到最低 |
| **L2 Dev Eval** | 分钟级，每轮 | 每轮都跑 | 全量 dev 集 GT，逐条跑 8 种 assertion；程序判的由程序判，需语义理解的让 LLM 做 YES/NO，结果写入 per-case JSON 供下轮诊断 |
| **L3 Strict Eval** | ~10 分钟，条件 | 每 N 轮 / dev 超阈值 / 层晋升前 | 跑 **holdout 集**（从没见过，防过拟合）+ **regression 集**（确保老 case 没坏）+ 盲 A/B 对比 |

### 2.4 5 维 AND 门控（核心机制三）

每一轮改动必须 5 个问题**全 YES** 才保留，任一 NO 就 `git revert`，当这轮没发生过：

- 质量（+2%）
- 触发（±5%）
- 成本（≤20%）
- 延迟（≤20%）
- 回归（≤5%）

**为什么用 AND 而非加权求和**：加权求和允许一个维度高分补另一个低分（质量 +10% 但 token 翻倍可能 PASS），AND 逻辑不会。

### 2.5 Trace 诊断（核心机制四）

一般工具只告诉你「这轮 80 分」让你自己猜。Skill-Evolver 把上一轮每个 case 的完整执行记录落盘，下轮直接告诉 proposer：这几个 case 挂了，trace 文件路径，自己去看。

- **不是把 10M token 全塞 prompt，而是给一张「地图」让它去现场看**。
- 协议硬约束：先看 trace 再诊断再改，不准猜。
- 每步改动都有 trace 背书，像论文引文献。

---

## 三、验证：它真的跑起来了

### 3.1 自迭代 19 轮（meta-evolution，自己改自己）

残酷之处：SKILL.md 既是「菜谱」又是「被烤的蛋糕」，任何协议缺陷都会在执行中暴露。

| 指标 | 数值 | 含义 |
|---|---|---|
| 迭代轮数 | 19 轮 | 10 修 bug/文档、3 修安全漏洞、1 清死代码、5 代码重构 |
| 被丢弃轮次 | 0 | 每轮都过 5 维门控，无 revert |
| 崩溃 | 0 | 19 轮一次没崩 |
| 测试用例 | 17 → 31 | 新增 14 个都是迭代中发现的新问题，AI 自动补 |
| 最终通过率 | 71/71 = 100% | 训练 56 + 留出 8 + 回归 7，全绿 |
| 主文件行数 | 1411 → 557 | 减 60%，拆成 13 个单一职责小文件 |

前 6 轮改文档规范，第 7 轮进代码层，第 15-19 轮连续 5 次重构；全程不跨层。

### 3.2 印象深刻案例

第 7 轮工具自己加安全检查「git 不干净就拒绝」，测试全过；但用户 skill 可能没 git init 被封死，作者测不出。第 12 轮工具**自己发现这个回归**，按协议重写初始化逻辑（干净 git→继续 / 脏 git→报错 / 没 git→自动 init / 没装→给安装指令），并在全新空目录端到端验证通过。

因为整个在对话中进行（agent 架构），作者可在第 10 轮直接说「帮我把 gate 逻辑提取成独立文件」，下一轮照做并跑门控——像搭档而非黑盒管道，随时给方向、它随时执行+验证。

### 3.3 真实业务实战

优化一个客服问答 skill（从近千篇知识库检索候选路径），召回率已到 96%。新需求：候选数从 10 压到 6，recall 不能掉。压完后召回率掉到 86%（75 case 中约 10 个 miss）。交给 evolver 迭代修掉 9 个，最后仅 1 个 miss：

- S1 路径召回 **86% → 98.67%**（标准题 100%、难题 97.3%）
- 候选数 ~10 → ~6
- Stage2 处理压力降 **59%**

---

## 四、局限与反思（作者坦诚）

1. **LLM 评测噪声**：同状态同 GT 跑 4 次结果在 0.79~0.92 漂移，分不清是改动功劳还是 LLM 状态。解法跑 3 次取均值，但成本翻 3 倍。
2. **GT 决定天花板**：有争议 case 答案本身无共识，5 轮都修不了，标记「不可修」移入回归集纯防护——**当一个 case 5 轮没修好时，先怀疑数据而非 skill**。
3. **昂贵**：19 轮零人工干预，但 API 成本可观（原文明示约 100 美元）。
4. **初期需人工引导**：前 3-5 轮最好瞄一眼帮它建立方向，之后 `experiments.jsonl` 积累足够 memory 越跑越准。

### 两个深刻认知

- **每一步都验证**：LLM 会偷懒（跳验证）、过拟合（硬编码 case 涨分）、自作主张（并行你禁止的 stage）。与其写更长 prompt 说服它，不如把规矩写进代码——门控不过就 `git revert HEAD`，**程序掌握控制流，LLM 只管单点生成**。
- **互补而非分工**：人在「明处」看着，AI 在「暗处」替你试错。19 轮就是 19 个不同 regime，每一次 rebaseline 都暴露一类你意想不到的失败。最有价值的不是自动化省时间，是它替一个你从没见过的用户，跑了一遍你永远跑不到的路径。

> 呼应 Karpathy 的观点：spawn a swarm of agents to collaborate in tuning smaller models, promoting the most promising ideas to larger scales, with humans contributing on the edges optionally. 人在 edge 上 optionally 贡献。

---

## 五、可复用的方法论小结

| 要素 | 做法 |
|---|---|
| 数据 | 准备 GT 用例（可 AI 生成），严格分 dev / holdout / regression |
| 迭代 | 8 阶段 Loop，原子化改动 + trace 证据绑定，禁止猜测 |
| 评测 | L1 秒级门卫（坏迭代成本最低）→ L2 dev 全量 → L3 严格（防过拟合/回退） |
| 门控 | 5 维 AND，任一不过即 revert |
| 控制 | 程序掌握控制流，LLM 只做单点生成；人在 edge 上 optionally 贡献 |

**对 Agent 工程团队的启示**：Skill 质量不应靠「手艺活」，而应像训练模型一样，用「数据 + 指标 + 闭环」把它变成可被择优、回滚、进化的对象——这正与「Agent 自进化飞轮（评测→记忆→落地→控制）」中 Harness 层自动优化的思路一致。
