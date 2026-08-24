# Skill-Evolver 详解：方法论 + 开源实现（合并笔记）

> 本笔记合并两份来源：
> 1. **方法论文章**（内部技术博客，已脱敏）→ 讲"为什么"和整体设计思路；
> 2. **开源实现** `github.com/FishSerrie/skill-evolver`（MIT，作者 GitHub: FishSerrie，公开可查）→ 讲"具体怎么落地"。
>
> 两篇是同一套东西：文章是设计思路叙述，仓库是可执行落地。代码实测把文章里"19 轮"推进到了 "21+ 轮 / 100% 通过"。

---

## 一、项目概览

- **定位**：面向 Claude Code / Codex CLI / OpenCode 的"技能（Skill）自主进化引擎"。
- **标语**："Point it at a skill. Wake up to a better skill."
- **一句话核心**：把 Skill 当成"可训练对象"——你备好数据(GT)、定好指标，剩下的交给自我迭代闭环（搜索→修改→评估→门控→保留/丢弃→重复）。
- **融合三个公开 SOTA 来源**：
  - **AutoResearch**（Karpathy 启发，uditgoenka 泛化）→ 自主外循环骨架（试错/回滚/保留）
  - **skill-creator**（Anthropic 官方，硬依赖）→ 基于 GT 的评测引擎
  - **Meta-Harness**（Stanford, Lee et al.）→ 失败诊断必须喂完整原始执行轨迹（只给分数比给 trace 差 44%）

---

## 二、为什么"训练" Skill（动机）

Skill 表面像 prompt，实际更像 harness（一套系统）。随便写个 SKILL.md 模型就能跑，但要让它**稳定**干活就完全不同：触发边界、安全规则、references 一致性、脚本版本兼容……加在一起早已不是"写一段 prompt"，而是在搭一套系统。三个崩点：

1. **稳定性**：加了"git 状态不干净就拒绝执行"，你自己的测试环境都在 git 下，测不出"用户还没 git init"直接报错。
2. **边界**：cleanup 用字符串排序，`iteration-9` 之前正常，`iteration-10` 突然排到 `iteration-2` 前面把最新结果删了——因为测试从没超过 9 轮。
3. **规则打架**：保护 A 场景的安全规则，把写在协议文档里的 B 场景正常路径封死了。规则越多行为越不确定（规则复杂度爆炸）。

**核心认知**：训练 Skill 不是让代码编过，而是让 behavior 收敛到你的数据分布——就像训模型看 loss 收敛。"真的好" = behavior 匹配你的数据分布。

**思想来源拼接**：`Skill-Evolver = AutoResearch 的 loop 骨架 + Creator 的评测引擎 + Meta-Harness 的诊断大脑`。外层不断试错/回滚/保留，内层把"好不好"测清楚，再用 trace 把每次失败变成可诊断证据。

---

## 三、循环协议详解（8 阶段）

实现里 SKILL.md 主入口**不直接硬编码逻辑，而是协议索引**：把各阶段指向 `scripts/*.py` 与 `references/*.md`，保证可维护、可移植（不依赖 skill-creator 也能独立运行）。

**协议文件索引**（references/）：
- `evolve_protocol.md` 完整 8 阶段协议
- `gate_rules.md` 多门控规则 + 伪代码
- `mutation_policy.md` 分层突变策略
- `memory_schema.md` results.tsv + experiments.jsonl 结构
- `isolation_protocol.md` Phase2/3 隔离（诊断器/修改器窄签名）
- `agents/`：search_agent（变体生成）/ grader_agent（评分）/ comparator_agent（盲 A/B）/ analyzer_agent（归因）

**8 阶段在代码里的精确归属**（architecture.md v0.6，2026-04-10）：

| Phase | 代码归属 | 自动化 | 核心动作 |
|---|---|---|---|
| 0 Setup | `setup_workspace.py` + `LocalEvaluator.full_eval` | 全自动 | 建隔离工作区 + 跑 baseline，每案例 JSON 持久化供诊断 |
| 1 Review | `evolve_loop.py::phase_1_review` | 全自动 | 读 git log / `results.tsv` / `experiments.jsonl` / `meta.json` / **`failed_case_paths`** |
| 2 Ideate | `llm.py::phase_2_diagnose` | Claude 推理 | 诊断失败、决定改什么；**对 holdout 证据盲化**，强制基于 trace |
| 3 Modify | `llm.py::phase_3_modify` / Edit | Claude 执行 | **一次一个原子改动**；对原始诊断文本盲化 |
| 4 Commit | `evolve_loop.py::phase_4_commit` | 全自动 | `git commit -m … -- <pathspec>` 局部提交 |
| 5 Verify | `run_l1_gate.py` / `run_l2_eval.py` | L1 全自动；L2/L3 编排 | 三层评测（见下） |
| 6 Gate | `gate.py::phase_6_gate_decision` | 全自动 | 5 维 AND 门控（keep/discard/revert） |
| 6.5 复检 | `verifier_panel.py::phase_6_5_review` | 全自动 | 对抗式复检：overfit / assertion_gaming / structural |
| 7 Log | `evolve_loop.py::phase_7_log` | 全自动 | 写 `results.tsv` + `experiments.jsonl` |
| 8 Loop | `evolve_loop.py::phase_8_loop_control` | 全自动 | 继续/升层/结束 + 自动起 HTML 报告 |

**两个贯穿约束**：
- 每轮只允许 **ONE atomic change**（描述里出现"和"字就该拆两轮；git diff 超 5 文件大概率非原子）。
- **分层突变** Layer1(描述/触发词) → Layer2(正文) → Layer3(脚本/refs)，只在下层 plateau 才升层。

**架构视角（四层）**：Layer4 Search（外循环）/ Layer3 Gate（门控）/ Layer2 Eval（自适应评测）/ Layer1 Memory（结构化实验记忆：results.tsv + experiments.jsonl + git history + best_versions/）。

---

## 四、三层评测（Phase 5）

L1/L2/L3 是脚本历史命名，Quick Gate / Dev Eval / Strict Eval 是概念名，指向相同事物（全部由 `evolve_plan.md` per-skill 参数化，不写死）：

| 标签 | 别名 | 作用 | 速度 | 频率 |
|---|---|---|---|---|
| L1 | Quick Gate | 语法/结构/Creator `quick_validate` 秒级门卫 | 秒级 | 每轮必跑（`run_l1_gate.py`） |
| L2 | Dev Eval | dev split 逐条断言打分（程序 + BinaryLLMJudge） | 分钟级 | 每轮/按 plan（`run_l2_eval.py` + `evaluators.py`） |
| L3 | Strict Eval | holdout + regression + 可选盲 A/B | ~10 分钟 | 条件触发（复用 L2 + 换 split） |

- **L1 挂了直接 discard，不跑 L2**——把坏迭代成本压到最低。
- **L2**：8 种断言，6 程序判 + 2 LLM 语义判（见第六节）。
- **L3**：仅三种情况触发——每 N 轮自动 / dev pass_rate 超阈值 / 层晋升前。跑**holdout（防过拟合，从没见过）+ regression（老 case 没坏）+ 盲 A/B**。

---

## 五、门控机制（5 维 AND）

**核心逻辑：AND 而非加权求和**——加权允许"质量+10% 但 token 翻倍"照样 PASS，AND 不允许。所有"保留条件"必须同时满足，任一 NO 即 `git revert`，当没发生。

**默认阈值**（可在 `evolve_plan.md` 按技能覆盖）：
- `min_delta=0.02`（质量 pass_rate 最小提升）
- `trigger_tolerance=0.05`（触发 F1 容忍）
- `max_token_increase=0.20`（成本/token 上限）
- `regression_tolerance=0.05`（回归容忍）
- 延迟：+20% 上限

**决策结果**：keep / discard / revert。质量提升但造成 regression 的改动会被 discard。

**防作弊设计**（实现新增，文章未详写）：
- `gate.py` 提供纯函数：`check_structure`（大小预算/结构契约）、`check_metric_thresholds`（逐维度下限与回归容忍）。
- 评分层 `scoring.py` 通过 **`check_conservation` 守恒方程**，使分类器"多报"在结构上无法隐藏。
- Rubric 评分默认开启 **commit-first**（裁判先答任务再看到候选），防"看似合理实则不正确"。

---

## 六、GT 与 8 种断言

**GT 格式**（JSON）：`prompt` + `assertions[]` + `split`（dev/holdout/regression），支持任意语言。

**8 种断言**：
- 程序直接判（6 种）：`contains` / `not_contains` / `regex` / `file_exists` / `json_schema` / `script_check`
- LLM 二元判（2 种）：`path_hit` / `fact_coverage`（支持预设 facts 或在线关键词）

**数据切分**：`dev`（优化目标，喂给优化器）/ `holdout`（过拟合检测，藏起来不喂）/ `regression`（防能力退化，守护核心规范）。

**Trace 诊断**（Meta-Harness 核心）：每案例结构化 JSON，路径形如 `/evolve/iteration-E*/cases/case_{id}.json`，保存四个组件——`prompts` / `tool calls` / `model outputs` / `state updates`，设计为 grep 友好（如 `grep -l '"pass": false' /evolve/iteration-E*/cases/*.json`）。`trace_enrichment.py` 提供 `locate_in_corpus` / `excerpt` / `nearest_match` / `build_skill_snapshot` 等富化辅助。Phase1 只**选择性读取** `failed_case_paths`，Phase2 通过 `isolation.py` 构建窄签名诊断提示，确保诊断器看不到 holdout 证据——**不是把 10M token 全塞 prompt，而是给一张"地图"让它去现场看**。协议硬约束：先看 trace 再诊断再改，不准猜。

---

## 七、五种运行模式

| 模式 | 作用 |
|---|---|
| **Evolve**（核心） | 无人值守自主优化循环，真正执行 keep/discard/revert |
| **Eval** | 一次性评估，输出通过率 + 逐案细分 + 可选 HTML 查看器 |
| **Create** | 从需求生成新技能 + 初始 GT |
| **Improve** | 人工定向改进，Evolver 提供基于 trace 的诊断证据并代执行 |
| **Benchmark** | 两个技能版本 A/B 对比、判定胜者 |

**跨平台**：`plugin/skills/skill-evolver/` 是唯一事实来源，通过 `sync-codex.sh` / `sync-opencode.sh` 自动生成 Codex(`.agents/`) / OpenCode(`.opencode/`) 适配版本。实验提交落在**独立工作区 git**，不污染业务项目（这是 `git revert` 能安全执行的前提）。
**硬依赖**：必须先装 `skill-creator`，否则抛 `CreatorNotFoundError` 退出。

---

## 八、最小可跑 GT 示例（examples/hello-skill / code-review-helper）

示例 skill：**code-review-helper**（Python 代码审查助手）。初始 `SKILL.md`：

```markdown
---
name: code-review-helper
description: "Reviews Python code snippets and provides improvement suggestions.
Triggers on: 'review this code', 'code review', 'check my Python'."
---

# Code Review Helper
A simple skill that reviews Python code snippets and suggests improvements.

## What You Do
When the user shares Python code for review, you should:
1. Read the code carefully
2. Identify issues in these categories:
   - Bug risks (potential runtime errors, edge cases)
   - Style issues (naming, formatting)
   - Performance concerns
3. Provide specific, actionable suggestions

## Output Format
For each issue found, use this format:
**[Category]** Line N: Description of the issue
  Suggestion: How to fix it

## Rules
- Be specific — reference exact line numbers and variable names
- Prioritize bugs over style issues
- If the code is clean, say so briefly — do not invent issues
- Keep suggestions concise (one sentence each)
```

配套 `evals.json`（真实可跑，8 个 case）：

```json
{
  "evals": [
    {"id":1,"prompt":"review this code",
     "assertions":[{"type":"contains","value":"code review"},{"type":"contains","value":"Python"}],
     "split":"dev"},
    {"id":2,"prompt":"check my Python function",
     "assertions":[{"type":"contains","value":"bug"},{"type":"contains","value":"style"},{"type":"contains","value":"performance"}],
     "split":"dev"},
    {"id":3,"prompt":"review this code for security issues",
     "assertions":[{"type":"contains","value":"security"},{"type":"not_contains","value":"always find issues"}],
     "split":"dev","metadata":{"note":"intentionally fails at baseline — security not in initial SKILL.md"}},
    {"id":4,"prompt":"review my code and show examples of fixes",
     "assertions":[{"type":"regex","value":"\\*\\*\\[.+\\]\\*\\*"},{"type":"contains","value":"example"},{"type":"contains","value":"line number"}],
     "split":"dev","metadata":{"note":"Example assertion intentionally fails — not in baseline"}},
    {"id":5,"prompt":"is this code efficient?","split":"holdout",
     "assertions":[{"type":"contains","value":"performance"},{"type":"not_contains","value":"rewrite everything"}]},
    {"id":6,"prompt":"review this Python class for best practices","split":"holdout",
     "assertions":[{"type":"contains","value":"specific"},{"type":"contains","value":"actionable"},{"type":"regex","value":"(?i)line\\s*(number|N|\\d)"}]},
    {"id":7,"prompt":"[regression guard] output format spec must survive evolution","split":"regression",
     "assertions":[{"type":"contains","value":"Output Format"},{"type":"regex","value":"\\*\\*\\[.+\\]\\*\\*"}],
     "metadata":{"note":"Guards against the evolve loop accidentally removing the output format section"}},
    {"id":8,"prompt":"[regression guard] anti-hallucination rule must persist","split":"regression",
     "assertions":[{"type":"contains","value":"Rules"},{"type":"contains","value":"do not invent"}],
     "metadata":{"note":"Guards against losing the 'do not invent issues' rule during body rewrites"}}
  ]
}
```

**设计要点**：
- `dev` 1-4 是开发目标，其中 **3、4 故意在 baseline 失败**（初始 SKILL.md 没提 security、没要求给 example/line number）——正是 Evolver 要"修掉"的缺口，驱动它改 SKILL.md。
- `holdout` 5-6 藏起来不喂优化器，防过拟合背答案。
- `regression` 7-8 回归守卫：确保演化中"输出格式"和"不杜撰问题"两条核心规则不被意外删掉。
- 断言类型覆盖 `contains` / `not_contains` / `regex` 三种（对应"程序直接判"类断言）。

跑法（仅说明，不在本地执行）：
`python3 scripts/evolve_loop.py ./examples/hello-skill/ --gt ./examples/hello-skill/evals.json --run --max-iterations 20`

---

## 九、实战验证数据

**元进化（自己改自己）**：文章讲 19 轮，开源 README 实测 **21+ 轮、最终 100% 通过、零崩溃零 discard**。SKILL.md 既是"菜谱"又是"被烤的蛋糕"，任何协议缺陷都会在执行中暴露。

**真实业务**：优化一个客服问答 skill（从近千篇知识库检索候选路径），候选数从 10 压到 6、召回率一度掉到 86%；Evolver 迭代修掉 9/10 个 miss，最终 **S1 路径召回 86% → 98.67%**（标准题 100%、难题 97.3%），候选数 ~10 → ~6，下游处理压力降 59%。

**代码瘦身**：主文件 1411 → 557 行（-60%），拆成 13 个单一职责小文件。

---

## 十、局限与认知

1. **LLM 评测噪声**：同状态同 GT 跑 4 次结果在 0.79~0.92 漂移，分不清是改动功劳还是 LLM 心情；解法跑 3 次取均值，但成本翻 3 倍。
2. **GT 决定天花板**：答案本身无共识的 case，5 轮修不好就标记"不可修"移入 regression 集纯防护——**当一个 case 5 轮没修好时，先怀疑数据而非 skill**。
3. **昂贵**：19 轮零人工干预，成本约百美元级。
4. **初期需人工引导**：前 3-5 轮最好瞄一眼帮它建立方向，之后 `experiments.jsonl` 积累足够 memory 越跑越准。

**两个深刻认知**：
- **程序掌握控制流、LLM 只管单点生成**：与其写更长 prompt 说服 LLM 别偷懒/别过拟合，不如把规矩写进代码——门控不过就 `git revert HEAD`，控制流交给程序，生成交给 LLM。
- **互补而非分工**：人在"明处"看着，AI 在"暗处"替你试错那些你从没见过的 regime。最有价值的不是自动化省时间，是它替一个你从没见过的用户，跑了一遍你永远跑不到的路径。

---

## 附：文章解读 vs 开源实现 对照表

| 维度 | 方法论文章 | 开源实现 |
|---|---|---|
| 性质 | 设计思路叙述 + 内部实战 | 可执行落地（MIT，15 stars） |
| 模式 | 只讲 Evolve | Evolve + Eval/Create/Improve/Benchmark 五模式 |
| 元进化 | 19 轮零崩溃 | 21+ 轮、100% 通过 |
| 工程保险 | 提了 git revert | 明确"工作区 git 隔离 + 不污染业务项目" |
| 防作弊 | 未详写 | 守恒方程 + 对抗复检(Phase 6.5) + commit-first |
| 来源 | 泛化名 | 实名（Karpathy/uditgoenka、Stanford Lee et al.、Anthropic skill-creator） |
| 协议组织 | 概念图 | SKILL.md 索引 + references/*.md + 15 个单一职责 .py |
