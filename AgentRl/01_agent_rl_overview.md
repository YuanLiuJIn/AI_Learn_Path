# 01. Agent RL 概述：从单步 MDP 到 POMDP（概念基石）

> 目标：用 Landscape Survey §2 的**形式化**，把"Agentic RL 到底是什么"讲清楚。
> 这是整个专题的基石——后面所有论文都挂在这套语言上。读完你应该能区分
> "传统 LLM RL（LLM-RL）"和"Agentic RL"，并说出它们数学上的本质差异。

## 1. 一个被很多人忽略的事实：传统 RLHF 其实是"退化的单步 MDP"

Landscape Survey 一针见血地指出：我们熟悉的 RLHF / RLVR / DPO，在数学上根本不是
"Agent"在做决策，而是**退化的单步马尔可夫决策过程（degenerate single-step MDP）**。

直观理解：

```text
传统 LLM RL（一次生成、一次打分）：
  输入 prompt → 模型一次性吐出整段回答 → 给一个标量奖励 → 结束（T=1）

这和"下棋走一步看结果"完全不同，
更像"写完整篇作文，老师给一个总分"。
模型没有在过程中观察环境、调整动作。
```

## 2. 形式化对比：MDP（LLM-RL） vs POMDP（Agentic RL）

Survey 的 Table 1 给出了严谨对比。下面用"人话 + 公式"双层解释。

### 2.1 传统 PBRFT（Preference-Based RL Fine-Tuning，即 LLM-RL）

论文把传统 LLM RL 称为 PBRFT，其 MDP 元组为：

```text
⟨ 𝒮_trad, 𝒜_trad, 𝒫_trad, ℛ_trad, T=1, γ=1 ⟩

状态空间 𝒮_trad：只有一个状态 s0 = 输入 prompt，回合立刻结束（T=1）
动作空间 𝒜_trad：一段纯文本 token 序列（action = 整个回答）
转移动态 𝒫_trad：确定性转移到终止态（生成完就结束）
奖励 ℛ_trad：单个标量 r(a)（无中间反馈，只有最终一个分）
目标 J(θ)：E_{a~πθ}[ r(a) ]，无折扣（γ=1）
```

关键点：**没有时间维度**。生成的每一步 token 之间没有"环境反馈"介入，奖励是
生成结束后才有的单一标量。

### 2.2 Agentic RL（POMDP）

Agentic RL 把 LLM 建模为**部分可观测 MDP（POMDP）**中的可学习策略：

```text
⟨ 𝒮_agent, 𝒜_agent, 𝒫_agent, ℛ_agent, γ, 𝒪 ⟩

状态空间 𝒮_agent：世界状态 s_t ∈ 𝒮_agent，多步（T>1）
观测 𝒪：Agent 只能看到 o_t = O(s_t)（部分可观测！）
动作空间 𝒜_agent：𝒜_text ∪ 𝒜_action（文本推理 + 可调用工具/环境交互的结构化动作）
转移动态 𝒫_agent：s_{t+1} ~ P(·|s_t, a_t)（动态、不确定）
奖励 ℛ_agent：步级奖励 R(s_t, a_t)（稀疏的最终奖 + 密集的过程子奖）
目标 J(θ)：E_{τ~πθ}[ Σ γ^t R ]，需长期信用分配（discounted, multi-step）
```

### 2.3 对照表（Survey Table 1 精要）

| 维度 | 传统 LLM-RL（PBRFT） | Agentic RL（POMDP） |
|---|---|---|
| 状态空间 𝒮 | `{s0}` 单一 prompt，T=1 | `s_t`，多步 T>1，世界动态演化 |
| 观测 | 全程可见完整 prompt | `o_t = O(s_t)`，仅部分可观测 |
| 动作空间 𝒜 | 纯文本序列 | 文本 + 工具调用/环境操作的结构化动作 |
| 转移动态 𝒫 | 确定性到终止态 | 随机 `s_{t+1} ~ P(·|s_t,a_t)` |
| 奖励 ℛ | 单个标量 `r(a)`，无中间反馈 | 步级 `R(s_t,a_t)`：稀疏终奖 + 密集过程奖 |
| 目标 J(θ) | `E[r(a)]`，γ=1 | `E[Σ γ^t R]`，需长期信用分配 |

> 一句话：**LLM-RL 是"生成即结束"，Agentic RL 是"边干边看、长期规划"。**
> 这个区别解释了为什么直接把 RLHF 经验搬到 Agent 上会崩——问题本质变了。

## 3. Survey 的核心论点（Core Thesis）

> 强化学习是把"规划、工具使用、记忆、推理、自我改进、感知"这些能力，
> 从**静态启发式模块**变成**自适应、鲁棒 Agent 行为**的关键机制。

展开理解：

```text
"静态启发式"指什么？
  例如 ReAct 提示词：写死"Thought→Action→Observation"模板
  Toolformer 的 SFT：模仿人类标注的工具调用模式
  → 这些不会根据环境反馈自我调整，遇到新情况就傻了

"RL 变成自适应行为"指什么？
  Agent 通过环境反馈（测试过没过、网页点没点到）
  自主强化"有效的动作序列"、抑制"无效的动作"
  → 涌现出静态提示词从未教过的纠错、多工具组合能力
```

这就是 DeepSeek-R1、ToolRL、ReTool 等工作的共同灵魂：**用环境反馈替代人工示范**。

## 4. 双重分类法（Twofold Taxonomy）—— 后面所有论文的坐标系

Survey 用两个正交维度组织 500+ 篇工作：

```text
维度 A｜能力视角（Capability）
  Planning 规划 / Tool Use 工具使用 / Memory 记忆 /
  Reasoning 推理 / Self-Improvement 自我改进 / Perception 感知

维度 B｜任务视角（Task Domain）
  Search & Research / Code / Math / GUI / Vision /
  Embodied / Multi-Agent / Others
```

本专题 `07_papers_projects.md` 完全按这套分类法组织论文清单。
读论文时先问自己：**它在哪个能力下？解决哪个任务？**

## 5. Agentic RL 的三大新难题（由 POMDP 形式化直接导出）

从 §2 的形式化可以**推导**出 Agentic RL 为什么比 LLM-RL 难：

```text
难题 1｜部分可观测（Partial Observability）
  o_t = O(s_t)：Agent 看不到完整世界状态
  → 必须靠 Memory/感知维护状态估计（对应能力分类里的 Memory、Perception）

难题 2｜长程信用分配（Credit Assignment）
  目标 E[Σ γ^t R] 是累积的，但最终奖往往只有终点一个
  → 怎么知道"第 3 步调的工具"对"第 20 步成功"贡献多大？（对应 §3.7）

难题 3｜环境非平稳（Non-stationarity）
  P(s_{t+1}|s_t,a_t) 随多 Agent、实时网页而变
  → 训练分布漂移，稳定性是工程地狱
```

## 6. 下一步

继续读 `01b_Landscape_Survey_详解.md`，逐章拆解这篇总纲综述——
它会把上面的"能力 × 任务"分类法展开成具体论文和方法族。

## 7. 一句话总结

> Agentic RL 不是"RLHF 换个名字"，而是把 LLM 从单步 MDP 重建成多步 POMDP：
> 状态动态演化、动作含工具调用、奖励分步骤、目标要长期信用分配。
> Landscape Survey 的核心贡献，正是用这套形式化 + 双重分类法，
> 把碎片化的工作统一成一张可导航的地图。
