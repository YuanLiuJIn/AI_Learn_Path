# 以 SFT 为主线的论文优化与学术包装方案

> 配套文档：`意图识别与ComputerUse课题总结.md`（系统设计 + 近两年文献）。
> 本文只解决一个问题：**在"只用 SFT / 不做 RL"的前提下，怎样把课题包装成一篇能过审的论文。**
> 检索时间：2026-09-28。文中 2026 年 arXiv 编号来自本轮与上一轮检索，正式引用前请再核对版本、会议与实验数字。

---

## 0. 结论先行

### 0.1 先说坏消息

如果你的论文卖点是：

> "我们用 SFT 教会 Qwen 在指令不完整时主动向用户提问。"

**这句话已经不够发表了。** 2026 年已有工作把这句话分别说完了，而且说得更细：

| 已占位的工作 | 它已经做掉了什么 |
|---|---|
| **CLAIM**（arXiv:2608.11631） | 用多模型答案分歧的熵量化查询不确定性 → 自动合成数据 → 把澄清建模成**结构化决策生成**，用 **SFT + GRPO** 训统一澄清决策模型 |
| **Ask or Assume?**（arXiv:2603.26233, EMNLP 2026） | 在欠规约 SWE-bench 上把**"欠规约检测"与"执行"解耦**，多智能体架构，并观察到**良好校准的信息寻求行为** |
| **AmbiBench**（arXiv:2602.11750） | 移动 GUI Agent 的**四级指令清晰度分类法**（Detailed / Standard / Incomplete / Ambiguous）+ MUSE 评测，明确提出了"双向意图对齐" |
| **BALAR**（arXiv:2605.05386） | 免训练，维护潜状态信念，**最大化期望互信息**来选澄清问题 |
| **Conf-Gen**（ICML 2026, arXiv:2605.28920） | 为"**是否已提出足够澄清问题**"提供**保形（conformal）保证** |
| **AmbiK**（ACL 2025, arXiv:2506.04089） | 歧义指令数据集 + 澄清问答 + 意图 + 任务规划（1000 对 / 2000 任务） |
| **AT-CoT**（SIGIR 2025, arXiv:2504.12113） | "歧义类型思维链"：先预测歧义类型，再据此生成澄清 |
| **Fairy / Agentic SE**（arXiv:2509.20729） | 移动 GUI Agent 的 RGR 运行时目标精炼 + **人在回路澄清**，整体系统工程框架 |

所以"主动澄清"已经不是空白。**再写一篇同构的 SFT 论文，审稿人会直接判 novelty 不足。**

### 0.2 好消息

上面所有工作都缺同一样东西，而这样东西恰好只能用监督学习的方式落地：

> **没有人把"该执行 / 该询问"建模成一个带风险约束与成本约束的"推迟决策"（deferral）问题，用监督目标去学它，并给这个决策边界提供可校准、可保证的统计性质；更没有人让这个决策同时依赖"语言的模糊程度"和"当前屏幕上的候选证据"。**

这就是你的位置。把课题从

> "训练模型会提问"

换成

> **"学习一个风险校准的推迟策略（risk-calibrated deferral policy）：在信息不足以安全执行时，把决策权移交给用户；其触发条件同时由语言歧义与观测到的界面候选证据决定，并通过监督式成本敏感目标学习、通过保形校准获得有限样本的误执行风险上界。"**

**同一份 SFT 训练，换一层定义，就从"工程 pipeline"变成"学习问题"。** 这是本文档的全部目的。

### 0.3 推荐的三条包装路线

| 方案 | 主贡献 | 风险 | 建议 |
|---|---|---|---|
| **A. 数据 + 基准**（Resource 论文） | 反事实配对的"歧义-澄清-执行"数据集 + 新指标 + 基准 | 最低，最稳 | **必做，作为骨架** |
| **B. 方法**（Risk-Calibrated Deferral + 成本敏感 SFT + 保形校准） | 形式化 + 监督目标 + 统计保证 | 中 | **必做，作为方法章** |
| **C. 分析**（SFT 为什么学不会真正的不确定性） | 捷径线索分析 + 反事实诊断 | 低 | 作为核心分析章，最出彩 |

**推荐 A + B 合并为主线，C 作为第四章的分析。** 这样一篇论文同时有新问题定义、新数据、新方法、新指标、可证伪的分析，把审稿人四个常见拒稿理由（"没新问题""数据是凑的""方法太工程""实验不充分"）全部堵住。

---

## 1. 把"主动澄清"重新定义为一个学习问题

这一节是整篇论文的理论地基。**不做 RL，就靠这一节让方法显得有分量。**

### 1.1 Learning to Defer 视角（核心包装）

医疗 AI 有一条成熟脉络叫 **Learning to Defer（L2D）**：模型没把握时把决策**推迟给人类专家**，并证明"预测 + 推迟"的联合决策具有 Bayes 一致性。

- Madras, Pitassi, Zemel. *Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer.* NeurIPS 2018（arXiv:1711.06664）
- Mozannar & Sontag. *Consistent Estimators for Learning to Defer to an Expert.* ICML 2020
- Mao, Mohri, Zhong. *Principled Approaches for Learning to Defer with Multiple Experts.* ISAIM 2024（arXiv:2310.14774）
- Mao, Mohri, Zhong. *Realizable H-Consistent and Bayes-Consistent Loss Functions for Learning to Defer.* 2024（arXiv:2407.13732）
- Hemmer et al. *Learning to Defer with Limited Expert Predictions.* AAAI-23（arXiv:2304.07306）
- Joshi, Parbhoo, Doshi-Velez. *Learning-to-defer for sequential medical decision-making under uncertainty.*（arXiv:2109.06312）

**映射关系**（直接做论文 Figure 1）：

```text
L2D 里的概念                你的课题
─────────────────────────────────────────────
专家 (expert)        ←→    用户 (user)
推迟 (defer)         ←→    主动澄清 / 请求确认
预测代价             ←→    错误执行 + 不可逆后果
推迟代价             ←→    用户交互成本（多问一轮）
专家可用性           ←→    用户是否在场 / 是否有权限
专家能力偏差         ←→    用户自己也表达不清
```

于是你的问题变成：**在联合动作空间 \(A = A_{\text{act}} \cup \{\text{defer}\}\) 上学策略 \(x \mapsto a\)，最小化带约束的风险**：

\[
R(\pi)=\underbrace{\mathbb{E}\big[c_{\text{err}}\cdot \ell(\pi(x),y)\cdot \mathbb{1}[\pi(x)\in A_{\text{act}}]\big]}_{\text{错误执行}}
+\underbrace{c_{\text{unsafe}}\cdot P(\text{不可逆损害})}_{\text{高风险误操作}}
+\underbrace{c_{\text{def}}\cdot P(\pi(x)=\text{defer})}_{\text{交互成本}}
\]

Bayes 最优解就是对"充分性后验"设阈值：

\[
\pi^*(x)=\text{act} \iff \max_{z} P(\text{sufficient}\mid z, x) \ge \tau(\text{risk}, c_{\text{def}})
\]

**价值**：你不需要发明理论，只需要说明"L2D 经典结论可迁移到 GUI/Computer Use，且该场景引入了一个新变量（观测到的界面候选），使经典 L2D 假设失效"。**迁移 + 证伪经典假设 = 标准的方法论贡献。**

### 1.2 命题 1：为什么"朴素 SFT"在原理上就不够

> **命题 1.** 标准 SFT 最大化 \(\log p(y\mid x)\)，即拟合轨迹后验；但最优阈值 \(\tau\) 由非对称代价 \((c_{\text{err}}, c_{\text{unsafe}}, c_{\text{def}})\) 决定，与后验无关。因此**即使 SFT 完美学到后验，其决策边界仍不是 Bayes 最优**；需要显式的代价敏感目标，或事后校准 + 阈值选择。

作用：一次性论证"为什么不直接 SFT 就完事"，从而正当化三段式流程：

```text
结构化状态与行为 SFT  →  校准（calibration）  →  风险阈值选择（risk-controlled threshold）
```

**关键判断：这三段全部不需要 RL。** 你用"校准 + 阈值"替代了"RL 调决策边界"，成本低一个数量级，且能得到更强的结论（有限样本保证，而非经验改进）。

### 1.3 命题 2：为什么"只看文本的不确定性"必然不够

这是你区别于 CLAIM / AT-CoT / FATA 等全部文本方法的**唯一硬差异化**。

> **命题 2.** 存在两对输入 \((u,h,s)\) 与 \((u,h,s')\)，指令与历史完全相同、仅界面状态不同，但任务充分性不同（屏幕上有 1 个 vs 3 个候选目标）。因此任何形如 \(f(u,h)\)、不依赖 \(s\) 的决策函数都不可能是 Bayes 最优。

直接写进论文的 motivating example：

```text
用户："把那个文件发给他。"

屏幕状态 A：只有 1 个文件、1 个联系人
  → 语言歧义高，但环境将其消解 → 应当直接执行

屏幕状态 B：3 个文件、2 个"他"
  → 同样的语言，环境无法消解 → 必须澄清

屏幕状态 C：邮件应用根本没打开
  → 应当先观察 / 切换环境，而不是立刻问用户
```

**同一个句子，正确答案分别是 act / defer / observe。** 所有纯语言不确定性方法在这里都会给出同一个分数，必然错。这一个人为构造就能撑起 motivation 段落和一张有说服力的图。

建议把这一现象命名为 **State-Coupled Ambiguity（状态耦合歧义）**——好名字本身是包装的重要组成部分。

### 1.4 Selective Prediction / Risk–Coverage 视角（换掉现有评估体系）

现有文档的指标是 Intent Accuracy、Slot F1、Task Success。**这些指标在论文里是减分项**，因为它们把"该问不问"和"不该问却问"混进一个数，恰好掩盖你最想证明的东西。

选择性预测（selective prediction / abstention）已有现成且审稿人认可的语言：

- Chen et al. *Adaptation with Self-Evaluation to Improve Selective Prediction in LLMs.* EMNLP 2023 Findings（arXiv:2310.11689）
- Luo et al. *Aligning Language Models with Selective Prediction.* ICML 2026 Workshop（arXiv:2607.03528）——把 **AURC（风险-覆盖曲线下面积）** 直接当 RL 奖励
- Bai & Jin. *Conformal Selective Prediction with General Risk Control.*（arXiv:2603.24704）
- Salem et al. *Hierarchical Group-Conditional Conformal Risk Control.*（arXiv:2607.24562）
- Liu et al. *Uncertainty Quantification and Confidence Calibration in LLMs: A Survey.*（arXiv:2503.15850）

**包装动作**：把你的主结果图从"准确率柱状图"换成 **Risk–Interaction Curve**：

```text
纵轴：不可逆误执行率（Unsafe Execution Rate）
横轴：平均用户交互成本（每任务澄清轮数 / 提问信息量）
```

你的 SFT + 校准方法应当画出一条**支配**基线（prompt-only、CoT、BALAR 式互信息选择、"永远问"、"从不问"）的 Pareto 前沿。**这张图比任何准确率表都更能让审稿人相信你的贡献。** 而且它天然呼应 L2D 与 selective prediction 两条线，让方法章有理论支撑。

### 1.5 State-Grounded 视角

参考 **SAGE**（arXiv:2609.00434）的"状态差分"思想：把每轮澄清看作对工作流状态的**原子化改变**，并在证据不足时允许评测器拒答。

用于你的训练目标与评测：

```text
澄清前状态 → 澄清问题 → 用户回答 → 新状态（少了一个不确定项）
```

模型不只要生成"语言上合理的问题"，而要真正**消除一个关键不确定项**。这给了你一个新指标（见 §5）和一个新消融轴（有无显式任务状态变量）。

---

## 2. 方法包装：让 SFT 从"训练步骤"升级为"方法"

整章目标：让读者相信你的核心不是"跑了 SFT"，而是**设计了一个适合 deferral 的监督学习方案**。

### 2.1 结构化任务状态 + 决策头

模型输出统一中间表示（沿用现有文档 §15.5 的状态 schema），并显式分出两个头：

```text
① 状态头：slots / missing_information / candidate_targets / risk
② 决策头：status ∈ {act, defer, confirm, observe}
```

**为什么必须分开**：状态头是"描述"，决策头是"决策"。命题 1 说明二者的最优性条件不同，因此必须在架构上区分，才能分别校准。这就是一个有理由的架构设计，而不是随手多输出几个字段。

### 2.2 成本敏感的监督目标（不是朴素 CE）

这是方法章的技术核心。朴素 SFT 是

\[
\mathcal{L}_{\text{SFT}}=-\sum_t \log p_\theta(y_t\mid y_{<t},x)
\]

你的目标是**按字段与代价加权的分段损失**：

\[
\mathcal{L}=\sum_{t} w_t \cdot \big(-\log p_\theta(y_t \mid y_{<t}, x)\big),
\qquad
w_t =
\begin{cases}
w_{\text{dec}}\cdot \rho(\text{risk}) & t \in \text{决策 token}\\
w_{\text{slot}} & t \in \text{状态字段}\\
1 & t \in \text{计划/问题文本}
\end{cases}
\]

要点：

1. **决策 token 加权**（\(w_{\text{dec}} > 1\)）：让模型把容量优先放在"act vs defer"上。
2. **风险相关权 \(\rho(\text{risk})\)**：高风险样本（删除、发送、支付、提交）的决策错误惩罚更高，实现"非对称代价"。这是把 \(c_{\text{unsafe}}\) 写进损失的最简方式。
3. **可选：拒答感知的不对称损失**。对"漏掉必要澄清"（false negative，危险）与"多余澄清"（false positive，只是啰嗦）使用不同权重 \(\lambda_{\text{miss}} \gg \lambda_{\text{over}}\)。

**这段的价值**：它把 Proposition 1 从"只能靠事后校准"变成"训练时就已经代价敏感"，同时保持了纯监督（无 RL、无 reward model、无 rollout）。**审稿人问"方法贡献在哪"，答案就是这一条。**

### 2.3 校准与阈值选择（SFT 之后、RL 之前的关键一步，且非 RL）

三步，全部可在单机完成：

```text
1. Temperature scaling：在留出校准集上对决策头 logits 做温度标定，降低 ECE
2. 分组阈值：按 risk ∈ {low, medium, high} 分别选阈值 τ_low < τ_medium < τ_high
3. 风险控制：用 conformal / CRC（SCoRE 式 e-values）选 τ，使
      P(不可逆误执行) ≤ α  在有限样本下成立
```

**这是全篇性价比最高的一段。** 你不需要推导新定理：把 SCoRE（arXiv:2603.24704）或 HG-CRC（arXiv:2607.24562）的"选择性风险控制"直接套在你的决策头上，就得到一个**有分布无关有限样本保证**的"何时该问"准则。而 Conf-Gen（ICML 2026）刚证明"为澄清充分性提供保形保证"是可行且有价值的方向——**但它没有做在 GUI/Computer Use 上**，这就是你的增量。

> 论文里可以这样写贡献："To our knowledge, we are the first to provide a distribution-free finite-sample guarantee on the unsafe-execution risk of a GUI agent's decision to act without clarification."

### 2.4 明确"不做什么"（写进 method 的 scope 段）

主动写清楚边界，能预防审稿人攻击：

- 不做 RL、不训 reward model、不做在线 rollout；
- 不做像素级坐标回归，grounding 交给现成模型（SeeClick / GUI-Actor）；
- 不追求端到端 SOTA，专注"决策边界"的正确性。

**"我们只改了一件事"比"我们什么都做了"更容易被接受。**

### 2.5 一篇论文只讲一个机制

不要在一篇里同时声称"任务状态建模 + 成本敏感损失 + 保形校准 + 反事实数据 + 新基准"都是核心。**选一个做主角**：

```text
主角：风险校准的 deferral 决策边界
配角：任务状态（可解释性）、成本敏感损失（实现手段）、保形校准（提供保证）
道具：反事实数据（使主角可被验证）、新指标（使主角可被度量）
```

---

## 3. 数据贡献：反事实配对的"歧义–澄清–执行"数据集

数据是你最强、最难被抢的护城河，而且**不需要 RL 就能做**。

### 3.1 核心设计原则：反事实配对

不要只是"收集一堆模糊指令 + 正确答案"。那种数据 AmbiK 和 AmbiBench 已经做了。你要做的是**成对构造**，让数据本身就能证明你的论点：

```text
类型 I：指令固定，屏幕变化（验证命题 2）
  (u, s1, y=act)      (u, s2, y=defer)      (u, s3, y=observe)

类型 II：屏幕固定，指令变化（验证决策不依赖表面线索）
  (u1, s, y=act)      (u2, s, y=defer)     u1/u2 语义等价但措辞不同

类型 III：风险变化，其他不变（验证风险敏感的阈值）
  (u, s, risk=low,   y=act)
  (u, s, risk=high,  y=confirm)   ← 同一指令，仅因不可逆性而改为请求确认

类型 IV：多轮澄清轨迹（验证"最小必要问题"）
  (u0, s) → q1 → a1 → (u1, s) → q2 → a2 → ... → y=act
```

**类型 I 和 III 是别人没有的。** 它们直接对应你的两条命题，而且是**自动可生成的**：固定指令模板，程序化地改变界面候选数、改变动作后果等级（可撤销 / 不可撤销），就能批量生产。

### 3.2 清晰度与风险的二维标注法

AmbiBench 用了四级清晰度（Detailed / Standard / Incomplete / Ambiguous），但它是**一维**的。你可以做成**二维**：

```text
             风险：低            风险：中            风险：高
清晰度：详细    直接执行          直接执行           执行前确认
清晰度：标准    直接执行          直接执行           执行前确认
清晰度：不完整  推断后执行        澄清或确认         必须澄清 + 确认
清晰度：模糊    推断后执行        澄清               必须澄清 + 确认
```

这张表本身就是论文的一个小贡献：**它说明"是否澄清"不是清晰度的函数，而是清晰度与风险的联合函数**。所有只按清晰度分级的工作（含 AmbiBench）都无法表达这种交互。

### 3.3 数据来源与规模建议

| 来源 | 用途 | 备注 |
|---|---|---|
| **Mind2Web** | 真实网页任务与轨迹骨架 | 指令较完整，需注入歧义 |
| **OSWorld / WebArena** | 桌面/网页执行与最终状态验证 | 用于"执行后是否真的成功" |
| **AmbiK**（ACL 2025） | 歧义类型分类法参考 | 厨房场景，可借 taxonomy |
| **AmbiBench**（2026） | 清晰度分级参考 + 对照基准 | 移动端，你是桌面端 |
| **模板化程序合成** | 类型 I / II / III 反事实对 | 规模的主要来源，可控、可扩展 |
| **LLM 合成 + 人工抽检** | 自然措辞多样性 | 参考 CLAIM 的熵驱动合成 |
| **人类用户研究（可选）** | 小规模、10–20 人 | 极大提升可信度，见 §6 |

规模建议（第一版）：

```text
核心反事实对：3,000–8,000 组
多轮澄清轨迹：1,000–3,000 条
高风险样本占比：不低于 25%（否则学不会风险分层）
人工校验比例：不低于 10%
```

### 3.4 负样本与失败轨迹（必须做）

现有文档 §13.3 已指出这一点，这里给出可操作形式：

```text
负样本 A：该问却猜 → "默认选第一个文件发送"
负样本 B：不该问却问 → 对已完整说明的信息再次提问
负样本 C：虚假高置信 → confidence=0.99 但目标完全错误
负样本 D：未验证就声称完成 → 无 verification 字段却输出 completed
负样本 E：被界面诱导 → 网页文本诱使模型改变用户目标
```

每种负样本都要有对应的**偏好对或分类标签**，用于：训练时的代价敏感加权、评测时的错误率分解、以及 §5.4 的捷径线索分析。

### 3.5 合成产物的风险（提前自我批评）

审稿人一定会问"合成数据是否真实"。**在论文里主动写一段 Limitations**：

- 模板化任务可能低估真实用户的表达多样性；
- 程序合成的"歧义"可能与人类真实歧义分布不同；
- 缓解手段：小规模人类用户研究 + 人工抽检 + 报告合成/人工比例。

**主动承认并给缓解方案，比被审稿人指出要好得多。**

---

## 4. 评测贡献：新指标与新基准

### 4.1 现有指标为什么不够

| 指标 | 问题 |
|---|---|
| Intent Accuracy | 意图对了但该问却没问，仍得高分 |
| Slot F1 | 槽位填全了但决策错了，仍得高分 |
| Task Success | "永远问用户"会降低成功率，但"从不问"在高风险任务上更危险 |
| 单一 confidence | 混淆语言歧义 / 感知不确定 / 执行不确定，且不可校准 |

### 4.2 建议引入的六个指标

```text
① Appropriate Clarification Rate (ACR)   ← 主指标
   在 {该执行, 该澄清, 该确认, 该观察} 四类上取平衡准确率
   （而不是"澄清准确率"这一个单项）

② Deferral Precision / Recall (DPR / DRR)
   把 defer 当成一个类，算 P/R/F1 —— 直接对齐 L2D 文献语言

③ Unsafe Execution Rate (UER)   ← 第二主指标
   在"本应澄清或本应确认"的样本上，模型仍执行且造成不可逆后果的比例
   （这是 UER，不是简单的错误率，因为它只统计"危险的那部分错误"）

④ Risk–Interaction Curve / AURC-deferral   ← 主图
   纵轴 UER，横轴平均交互成本（澄清轮数或提问信息量）
   报曲线下面积，使不同方法可在同一张图上比较

⑤ Clarification Minimality (CM)
   提问覆盖的"必要信息单元"数 / 提问总信息单元数
   惩罚"请重新完整描述需求"这类偷懒问题

⑥ State-Coupled Consistency (SCC)   ← 你的独有指标
   在类型 I 反事实对上，决策应不同的比例；决策应相同的比例
   直接度量命题 2 是否被满足，纯语言方法在此接近随机
```

**⑥ 是最关键的。** 它把你 §1.3 的命题从"理论论证"变成"可测量现象"，而且任何文本方法在这上面都会暴露。**审稿人看到这个指标会立刻理解你的差异化。**

### 4.3 基准设计建议

命名建议（挑一个，易记、可搜索）：

```text
ACU-Bench   — Ambiguity–Clarification–Computer-Use Benchmark
SCA-Bench   — State-Coupled Ambiguity Benchmark
DEFER-Bench — Desktop Executable-act / Flexible-clarification Evaluation Resource
```

基准组成：

```text
层次 1（文本层）：残缺 / 模糊指令 → 结构化状态 + 澄清问题
层次 2（耦合层）：指令 × 屏幕反事实对 → act/defer/observe 决策
层次 3（风险层）：高中低风险 × 清晰度 → act/confirm/defer
层次 4（执行层）：真实网页/桌面执行 → 最终状态验证 + UER
层次 5（多轮层）：用户模拟器 → 多轮澄清直到可执行 → 任务成功
```

层次 1–3 可由你独立构造（不依赖 RL，成本可控），层次 4–5 复用 OSWorld / WebArena / Playwright。**即使层次 4–5 只做到初步，论文也已成立**——因为你的主指标（ACR、UER、SCC）主要在 1–3 上度量。

### 4.4 评测必须包含的对照条件

```text
上界（Oracle）：人工标注的正确答案          ← 给出可达上限
下界：        永远执行（never-ask）
下界：        永远询问（always-ask）
```

`always-ask` 是审稿人最爱用的攻击点。**你必须主动给出它的 UER/交互成本，说明它虽然 UER 低但不可用**，否则审稿人会替你说。

---

## 5. 实验矩阵（审稿人会问什么，就做什么）

### 5.1 核心 Research Questions（与现有文档 §15.6 对齐，但可度量化）

```text
RQ1  模型能否区分 act / defer / confirm / observe？
     → 指标：ACR、DPR、混淆矩阵
RQ2  决策是否真的依赖界面证据，而非语言表面线索？
     → 指标：SCC（类型 I）、捷径线索消融
RQ3  风险敏感性是否被学到？
     → 指标：类型 III 上的 UER、不同 τ 下的 UER
RQ4  澄清是否真的提升执行成功率与安全性？
     → 指标：层次 4–5 的 Task Success 与 UER
RQ5  保形校准是否给出可验证的风险保证？
     → 指标：覆盖率 vs 目标 α、违规率
RQ6  SFT 的成本敏感与校准分别贡献多少？
     → 消融
```

### 5.2 Baselines（必须全，否则被判实验不充分）

| 类型 | 基线 | 说明 |
|---|---|---|
| 基础 | Qwen 原始模型，zero-shot | 下界 |
| Prompt | 提示中加入"不确定就问" | 最常见的弱基线 |
| Prompt | CoT / Self-Ask / FATA 式先问后答 | 文本方法对照 |
| Prompt | AT-CoT（先预测歧义类型） | 强文本基线 |
| 免训练 | BALAR 式互信息最大化选问题 | 强对手，必须比 |
| 多智能体 | Ask or Assume? 式"检测/执行解耦" | 结构对照 |
| 训练 | 朴素 SFT（无成本敏感、无校准） | **最关键对照** |
| 训练 | SFT + 温度缩放（无风险阈值） | 分离"校准"与"阈值"贡献 |

**"朴素 SFT" 这一行决定了论文成败。** 若你的方法只比 prompt 强，审稿人会说"这只是 SFT 本身有效"；你必须证明"是成本敏感 + 校准有效，而不是 SFT 有效"。

### 5.3 消融轴

```text
A. 去掉显式任务状态（直接出决策）        → 测状态头的必要性
B. 去掉成本敏感权重（退回朴素 CE）        → 测 §2.2 的贡献
C. 去掉风险分层阈值（统一 τ）             → 测 §2.3 的贡献
D. 去掉保形校准（仅温度缩放）             → 测保证的贡献
E. 去掉屏幕状态输入（只给 u, h）          → 测命题 2 的实践后果
F. 去掉反事实数据（只训普通样本）         → 测 §3.1 的贡献
G. 去掉负样本                             → 测 §3.4 的贡献
```

**每个消融对应一个可写进论文的结论句，这是审稿人最看重的部分。**

### 5.4 分析实验（最出彩的部分）

```text
分析 1（捷径线索 / shortcut）
  构造"含有'那个/他'等模糊词但实际充分"的测试样本
  若模型仍倾向 defer，说明它学的是表面线索而非真实充分性
  → 这是对你方法的自我证伪，也是论文最有价值的发现

分析 2（校准曲线）
  ECE / Brier / Reliability Diagram，展示 SFT 后仍不校准、
  校准后显著改善

分析 3（OOD 清晰度泛化）
  训练用 Detailed/Standard/Incomplete，测试用 Ambiguous
  → 看决策边界是否能泛化到未见歧义类型

分析 4（错误归因）
  把错误分成：漏检缺失 / 问题生成质量差 / 计划错误 / 校准失败
  → 借鉴 OSWorld-Pro 的过程级评测思想

分析 5（虚拟用户模拟）
  用 LLM 模拟不同"配合度"的用户（模糊回答、拒绝回答、给出错误信息）
  → 测鲁棒性，同时呼应 AREAs-Lab 的交互评测
```

---

## 6. 论文标题、摘要骨架与贡献清单

### 6.1 标题候选

**偏方法 / 理论（推荐）**

```text
Risk-Calibrated Deferral: When Should a GUI Agent Ask Instead of Act?
```

```text
State-Coupled Ambiguity: Learning to Defer in Computer-Use Agents under
Incomplete Instructions
```

**偏数据 / 基准**

```text
ACU-Bench: Benchmarking Risk-Aware Clarification for Computer-Use Agents
```

**偏分析**

```text
Why SFT Agents Ask the Wrong Questions: A Counterfactual Study of
Clarification in GUI Agents
```

**中文题目（用于开题、基金本子）**

> 状态耦合歧义下 GUI Agent 的风险校准式推迟与主动澄清

### 6.2 摘要骨架（照这个填，约 150 词）

```text
[问题] Computer-Use Agent 通常假设指令完整；真实指令残缺、模糊、指代不明。
[现状] 已有工作让模型"会提问"，但 (i) 把澄清当作语言问题，忽略当前界面证据；
       (ii) 把"执行 / 询问"当成普通分类，忽略非对称风险与交互成本；
       (iii) 缺少对"何时必须问"的统计保证。
[观察] 我们指出 State-Coupled Ambiguity：同一指令在不同界面状态下应得到
       act / defer / observe 三种不同决策，任何纯语言不确定性度量都无法表达。
[方法] 我们把该决策形式化为 risk-calibrated deferral，用成本敏感的分段监督目标
       在 Qwen 上训练，并在决策头上施加分组阈值与 conformal 风险控制。
[数据] 我们构造反事实配对的 ACU-Bench，包含指令×界面、清晰度×风险两类对照。
[结果] 相对朴素 SFT 与免训练基线，我们的方法在 Unsafe Execution Rate 上降低 X%，
       同时保持 ACR 与执行成功率；并在 α 目标下达到经验覆盖率 Y%。
```

### 6.3 贡献清单（直接写进 Introduction 的 bullet）

```text
1. 我们指出并形式化了 State-Coupled Ambiguity：GUI 场景下任务充分性同时依赖
   语言歧义与观测到的界面候选，并证明任何不含界面状态的决策函数都非 Bayes 最优
   （Proposition 2）。

2. 我们把"执行 / 澄清 / 确认 / 观察"统一建模为 risk-calibrated deferral，
   给出标准 SFT 无法达到 Bayes 最优决策边界的论证（Proposition 1），
   并提出成本敏感的监督目标以在训练阶段引入非对称代价。

3. 我们提出在决策头上施加分组阈值与 conformal 风险控制，为"未经澄清即执行"
   的不可逆风险提供有限样本上界。

4. 我们构造 ACU-Bench：包含指令×界面反事实对与清晰度×风险对照的基准，
   并提出 ACR / UER / SCC 等指标，其中 SCC 直接度量界面耦合性。

5.（分析）我们表明朴素 SFT 会依赖表面模糊线索而非真实充分性，
   并展示反事实数据与代价敏感目标如何缓解该捷径行为。
```

---

## 7. 与最接近工作的差异化对照

**这张表建议做成论文的 Related Work 表格，也建议在 rebuttal 里直接复用。**

| 工作 | 何时提问 | 依赖界面状态 | 风险/成本建模 | 统计保证 | 执行闭环 | 桌面/跨应用 |
|---|---|---|---|---|---|---|
| AT-CoT (SIGIR'25) | 有（歧义类型） | 否 | 否 | 否 | 否 | 否 |
| AmbiK (ACL'25) | 数据集 | 否 | 否 | 否 | 否 | 否 |
| BALAR (2605.05386) | 互信息最大化 | 部分（潜状态） | 否 | 否 | 否 | 否 |
| Conf-Gen (ICML'26) | 保形保证 | 否 | 部分 | **是** | 否 | 否 |
| CLAIM (2608.11631) | 熵驱动 | 否 | 否 | 否 | 否 | 否 |
| Ask or Assume? (EMNLP'26) | 有（解耦检测） | 否（代码） | 否 | 否 | 部分 | 否 |
| AmbiBench (2602.11750) | 基准 | 否（一维清晰度） | 否 | 否 | 部分 | 移动端 |
| Fairy (2509.20729) | 人在回路 | 部分 | 否 | 否 | 是 | 移动端 |
| **本课题** | **风险校准 deferral** | **是（核心）** | **是** | **是** | **是** | **是** |

**读法**：只有你的方法同时在"界面耦合 + 风险成本建模 + 统计保证 + 执行闭环"四列打勾。这是最有力的 novelty 论证方式——**不要用文字吵架，用矩阵。**

---

## 8. 审稿意见预判与回应

提前把 rebuttal 写进论文，或至少写进你的心理准备。

| 可能的审稿意见 | 应对 |
|---|---|
| "只是 SFT，方法贡献弱" | 用 Proposition 1 + 成本敏感目标 + 保形校准三点回应；强调"朴素 SFT 是消融项，不是我们的方法" |
| "和 CLAIM 有何不同？" | CLAIM 是开放域文本问答、无界面状态、无风险成本、无保证；你是状态耦合 + 风险校准 + 保形 + 桌面执行。用 §7 表格 |
| "和 Ask or Assume? 有何不同？" | 它解耦"检测/执行"但不建模代价，也不依赖界面证据，且限于代码任务 |
| "和 AmbiBench 有何不同？" | AmbiBench 是评测基准、一维清晰度、移动端；你提供一维→二维（清晰度×风险）的推广、训练方法、以及界面反事实对照 |
| "数据是合成的，不真实" | 主动写 Limitations + 人类用户研究 + 人工抽检比例；引用 CLAIM 的合成数据被接受的事实 |
| "指标是自创的，不标准" | ACR/DPR 对齐 L2D 与 selective prediction 既有语言；SCC 有 Proposition 2 作为理论依据；AURC 是既有指标 |
| "confidence 不可信" | 这正是你做的：温度缩放 + ECE 曲线 + 保形校准；不要声称模型自报 confidence 可用 |
| "该不该问需不需要真人工确认" | 用 10–20 人小规模用户研究证明自动评测与人类判断的相关性 |
| "没做 RL，不算强" | 明确声明 scope：本文专注决策边界的正确性与可保证性；RL 是 future work（§10） |
| "always-ask 也能降低错误率" | 主动报告 always-ask 的交互成本，用 Risk–Interaction 曲线说明它不可用 |

---

## 9. 投稿策略与时间线

### 9.1 目标会议匹配

| 侧重 | 推荐 | 说明 |
|---|---|---|
| 数据 + 基准为主 | **ACL / EMNLP / NAACL 主会，或 Resources & Evaluation track**；**NeurIPS Datasets & Benchmarks** | 最稳，接受"数据 + 指标 + 分析"型贡献 |
| 方法 + 保证为主 | **EMNLP / ACL 主会**；若理论再强可冲 **ICLR** | 需要 Proposition 与保证更完整 |
| 人机交互侧重 | **CHI / IUI / CSCW** | 需要真实用户研究 |
| 快速占位 | **ICML "Agents in the Wild"** 等工作坊（RLSR、Conf-Gen 都在此） | 适合先发一版 workshop，再扩期刊/会议长文 |

**建议路线**：先投一个 workshop 占位（3–4 个月可完成），同步把长文做到 workshop 反馈之后，投 ACL/EMNLP 主会。

### 9.2 时间线（约 16 周）

```text
第 1–3 周   确定 taxonomy（清晰度×风险）+ 反事实数据设计 + 种子集 200 组
第 4–6 周   程序化生成数据 + 标注协议 + 人工抽检 + 跑通朴素 SFT 基线
第 7–9 周   实现成本敏感损失 + 校准与阈值 + 保形控制
第 10–12 周 构造 ACU-Bench 层次 1–3 + 全部基线与消融
第 13–14 周 分析实验（捷径线索、校准曲线、OOD）+ 小规模用户研究
第 15–16 周 写作、图表、rebuttal 预案
```

**关键判断**：第 1–6 周产出数据后，**即使后面全部实验失败，你仍有一篇 Resource 论文**。这是低成本保底策略。

---

## 10. 与后续 DPO / RL 的衔接（本篇写进 Future Work）

不要在首篇做 RL，但要在 Discussion 里点明路线，让审稿人看到可扩展性：

```text
本篇：SFT 定义决策结构 + 校准确定决策边界（offline，可复现，有保证）

后续一：偏好优化（DPO / ORPO / SimPO / KTO）
  偏好对来源：§3.4 的负样本 A–E
  目标：缓解"表面线索"捷径、提升澄清问题的自然度

后续二：离线 RL（reward-weighted fine-tuning，arXiv:2506.06964 思路）
  在固定长度决策上，用 AURC（arXiv:2607.03528 思路）做奖励
  注意：这与本篇的保形保证互补，不重叠

后续三：在线 RL（OSWorld / WebArena 环境）
  动作空间显式加入 ask_clarification / request_confirmation / observe_more
  风险：奖励污染、绕过确认、把"多问"当捷径（见现有文档 §13.5）
```

**写法建议**：Future Work 里只写"结构上如何接入"，不要写小规模 RL 实验结果——一旦写了就要被审。

---

## 11. 立即可执行的下一步

```text
□ 确定论文主角：在"风险校准 deferral"与"反事实数据集"之间选一个作为主线
□ 写出清晰度×风险的二维表（§3.2），并标注 3 个真实例子
□ 手写 20 组类型 I 反事实对（同指令、不同屏幕），验证命题 2 站得住
□ 手写 10 组类型 III（同指令、不同风险等级）
□ 定义状态 schema 与决策头输出格式（沿用现有文档 §15.5）
□ 跑通朴素 SFT 基线（LoRA，先 200–500 条），确认模型能学"何时问"
□ 写一版 Proposition 1 / 2 的严格表述（各半页，含假设与证明思路）
□ 画一张 motivation 图：同一指令 × 三种屏幕 → 三种决策
□ 复核所有 2026 年 arXiv 编号与会议信息（正式引用前必做）
□ 决定目标会议 + workshop 占位计划
```

---

## 附：一句话版本（用于开题口头陈述）

> 现有 GUI Agent 研究"怎么执行"，现有澄清研究研究"怎么问"；我们研究**"在什么条件下不得执行"**——把"执行 / 澄清 / 确认 / 观察"统一成一个风险校准的推迟决策，用监督学习学出这个边界，用保形校准给这个边界加上有限样本的风险保证，并用反事实数据证明这个边界必须同时依赖语言歧义和屏幕证据。
