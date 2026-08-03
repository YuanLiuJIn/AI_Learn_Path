# 01b. 《The Landscape of Agentic RL for LLMs》逐章详解

> 论文：Guibin Zhang, Hejia Geng, et al. (牛津 / 上海AI实验室 / NUS 等 25 位作者)
> **The Landscape of Agentic Reinforcement Learning for LLMs: A Survey**
> arXiv:2509.02547（v5, 2026-04，已发表于 TMLR）。综合 500+ 篇近期工作。
>
> 本文是专题的总纲。建议配合 arxiv 原文 PDF 一起读，本文件是"导读 + 重点标注"。

## 为什么这篇 Survey 值得精读

```text
它不是"罗列论文"，而是做了三件难而正确的事：
1. 用 MDP/POMDP 把"什么是 Agentic RL"严格定义清楚（§2）
2. 提出"能力 × 任务"双重分类法，给 500+ 工作一个坐标系（§3,§4）
3. 整理开源环境/基准/框架的实用汇编（§5），并指出 6 大开放挑战（§6）

读它 = 拿到一张 Agent RL 领域的"地图 + 索引"。
```

---

## §1 Introduction：RL 与 LLM 的协同，以及研究空白

核心铺垫：

```text
RL 与 LLM 的协同有三个层次：
  (a) RL 作为后训练手段（RLHF/RLVR）—— 让模型"更对齐/更会推理"
  (b) RL 训练 Agent 能力（规划、工具、记忆）—— 本文重点
  (c) LLM 赋能 RL（用 LLM 做世界模型、策略）—— 反向方向

Research Gap：
  前人工作零散、术语混乱（"Agent RL""LLM Agent RL""Multi-turn RL"混用）
  → 缺一个统一的形式化框架和分类法
```

> 记住这个 Gap：本 Survey 的全部价值，就是**填这个 Gap**。你读后续每篇论文时，
> 都用 Survey 的术语去"翻译"它，知识就能归位。

---

## §2 Preliminary：从 LLM RL 到 Agentic RL（全文最硬核）

这一节是**本专题 01 文件的数学来源**。要点回顾（详见 `01_agent_rl_overview.md`）：

```text
2.1 MDP 形式化：传统 PBRFT = 退化单步 MDP（T=1, γ=1）
2.2 Environment State：Agentic RL 引入动态世界状态 s_t
2.3 Action Space：文本 → 文本 ∪ 结构化动作（工具/GUI/代码）
2.4 Transition Dynamics：确定性 → 随机 P(s_{t+1}|s_t,a_t)
2.5 Reward Function：单标量 → 步级（稀疏终奖 + 过程子奖）
2.6 Learning Objective：E[r(a)] → E[Σ γ^t R]（需信用分配）
2.7 RL Algorithms：REINFORCE / PPO / DPO / GRPO 及变种（见 02 文件）
```

图 2（Figure 2）是关键直觉图：从「传统 RL → LLM RL → Agentic RL」的范式偏移扇形图，
红色 = LLM RL 特征，蓝绿 = Agentic RL 必需能力，紫色 = 已有实现。

> 读原图：arxiv.org/pdf/2509.02547 的 Figure 2。

---

## §3 Agentic RL：能力视角（The Model Capability Perspective）

**这是整篇 Survey 最值得逐节精读的部分。** 每个能力下，Survey 区分了
"RL 作为外部引导"和"RL 作为内部驱动"两种范式，并列出代表方法。

### 3.1 Planning（规划）

```text
范式 A｜RL 作为外部引导（LLM 生成动作，RL 训练值/启发函数指导搜索）
  代表：
    RAP / LATS        —— 用 LLM + MCTS 做树搜索规划
    Planning w/o Search —— 离线目标条件 RL
    Learning When to Plan —— 动态决定"何时该规划"（分配测试时算力）
    MAPF-DT           —— 决策 Transformer 做多智能体路径规划

范式 B｜RL 作为内部驱动（LLM 本身就是策略，靠环境交互微调）
  代表：
    ETO                —— 把 DPO 用在成败轨迹上
    VOYAGER            —— 迭代构建"技能库"（Minecraft）
    DSP (Dynamic Speculative Planning)
    PilotRL / AdaPlan  —— 过程级奖励塑形
    Planner-R1         —— 过程级奖励提升规划

展望：deliberation（慢思考）与 intuition（快思考）融合的元策略。
```

### 3.2 Tool Use（工具使用）

```text
阶段 1｜ReAct 风格（提示/SFT 模仿，缺乏自适应）
  ReAct / Toolformer / FireAct / AgentTuning

阶段 2｜工具集成 RL（TIR, Tool-Integrated Reasoning）
  代表（这是近年爆发点）：
    ToolRL / OTC-PO / ReTool / AutoTIR / VTool-R1
    DeepEyes / Pixel-Reasoner / Agentic Reasoning / ARTIST / ToRL
    ASPO  —— 优势塑形策略优化，理论上证明长 horizon TIR 的信用分配
  涌现能力：自纠正、多工具组合

长 horizon 挑战：时序信用分配难（GiGPO, SpaRL 初步尝试 turn-level 优势）
```

### 3.3 Memory（记忆）

```text
类型 1｜RAG 风格（外部存储，RL 调检索）
  Prospect（反射式检索）/ Memory-R1（PPO/GRPO 学 ADD/UPDATE/DELETE）/
  Mem-α / Memory-as-action

类型 2｜Token 级记忆
  显式自然语言 token：MemAgent / MEM1 / Memory Token / ReSum / Context Folding
  隐式潜 token：MemoryLLM / M+ / IMM / Memory / MemGen

类型 3｜结构化记忆（展望，目前靠手工规则，RL 控制尚开放）
  时序知识图 Zep / 原子记忆 A-MEM / 层次图 G-Memory, Mem0

Table 3 概览三类记忆，† 标注的是 RL 方法。
```

### 3.4 Self-Improvement（自我改进）

```text
类型 1｜言语自纠正（无梯度）
  Reflexion / Self-refine / CRITIC / CoV / Self-Debugging

类型 2｜内化自纠正（RL 有梯度）
  KnowSelf (DPO+RPO) / Reflection-DPO / DuPo / SWEET-RL / ACC-Collab

类型 3｜迭代自训练
  自对弈/搜索：R-Zero / ISC
  执行引导课程：Absolute Zero / Self-Evolving Curriculum / TTRL
  集体引导：SiriuS / MALT / ALAS

展望：反射能力的"元进化"（meta-policy 学"如何自纠正"）。
```

### 3.5 Reasoning（推理）

```text
System 1（快推理）：直觉启发式、next-token，易幻觉
System 2（慢推理）：CoT、多步验证、RL 增强（o1, DeepSeek-R1, 动态测试时缩放）
展望：把慢推理机制整合进 Agentic 推理，混合效率与严谨。
```

### 3.6 Perception（感知，多模态）

```text
被动→主动视觉认知：
  Visual-RFT / Reason-RFT / STAR-R1 / Vision-R1 / VLM-R1 / MM-Eureka（GRPO+视觉可验证奖励）
接地驱动的主动感知：
  GRIT / Ground-R1 / BRPO / DeepEyes / Chain-of-Focus（Zoom-in）
工具驱动：
  VisTA / VTool-R1 / OpenThinkIMG / Visual-ARFT / Pixel Reasoner（crop/erase/paint + 好奇奖励）
生成驱动：
  Visual Planning / GoT-R1 / T2I-R1（语义/像素级 CoT）
音频：Wen et al. / Diao et al. / EchoInk-R1
```

### 3.7 Others：长 horizon 时序信用分配

```text
过程监督 + 结果奖励：EPO / ThinkRM / SPO / AgentPRM / RLVMR
段级 DPO（SDPO）：把偏好优化扩展到多步
→ 这是 Agentic RL 的"皇冠难题"，05 奖励设计会深入。
```

---

## §4 Agentic RL：任务视角（The Task Perspective）

按应用领域梳理（每个领域有独特奖励与环境动态）：

```text
4.1 Search & Research：DeepRetrieval / Search-R1 / WebDancer（开源）；
    ZeroSearch / SSRL（内部知识搜索）；OpenAI Deep Research（闭源）。Table 4 总结。

4.2 Code Agent：代码生成（Outcome/Process reward RL，如 DeepCoder-14B, StepCoder, PSGPO）、
    迭代精炼、自动软件工程。Table 5。

4.3 Mathematical Agent：非正式 / 形式数学推理，结果/过程/混合奖励。

4.4 GUI Agent：RL-free、静态环境 RL、交互环境 RL。

4.5 Vision Agents：图像/视频/3D。

4.6 Embodied Agents：VLA 导航/操控，Case Study 用 Voyager。

4.7 Multi-Agent Systems：非参数协调模块优化、选定策略优化、端到端 MARL。

4.8 Other Tasks：TextGame / Table / Time Series / General QA / Social。
```

---

## §5 Environment and Frameworks（实用汇编）

### 5.1 Environment Simulator（环境分类，对应本专题 06 文件）

```text
Web Environments
GUI Environments
Coding & SWE Environments（交互 SWE、基准数据集、程序化世界模型）
Domain-specific（Science / MLE / Biomedical / Cybersecurity）
Simulated & Game Environments
General-Purpose Environments
```

### 5.2 RL Framework（框架分类，对应本专题 04 文件）

```text
Agentic RL frameworks          —— 专为 Agent 多步训练设计
RLHF and LLM fine-tuning       —— 通用后训练框架
General-purpose RL frameworks  —— 通用 RL 库
```

> Figure 1 是整篇组织结构树，建议打印出来当"地图"。

---

## §6 Open Challenges and Future Directions（6 大开放挑战）

这是读完全文后要带走的"研究前沿清单"：

```text
6.1 Trustworthiness（可信度）
  奖励黑客、幻觉/谄媚被 RL 放大、动作空间扩大攻击面

6.2 Scaling up Agentic Training（训练扩展）
  计算昂贵、数据密集；RL 是"放大"还是"创造"推理能力？（机制之争）

6.3 Scaling up Agentic Environments（环境扩展）
  当前基准多为简化沙盒，缺能自动生成课程与适配奖励的复杂动态环境

6.4 The Mechanistic Debate on RL in LLMs
  RL 在 LLM 内部到底改变了什么？（可解释性开放问题）

6.5 Architectural Patterns for Real-World Deployment
  真实部署的架构范式（异步、容错、环境失败隔离）

6.6 Broader Social Impact
  社会影响
```

---

## §7 Conclusion

> RL 是把静态启发式模块转化为自适应、鲁棒 Agent 行为的关键机制；
> POMDP 形式化为碎片化领域提供了统一术语与理论基石。

---

## 读完这篇 Survey，你应该能回答

```text
□ Agentic RL 在数学上为什么是 POMDP 而不是单步 MDP？
□ Survey 的双重分类法两个维度分别是什么？
□ 每个能力（规划/工具/记忆/自我改进/推理/感知）下，
  "RL 作为外部引导" vs "RL 作为内部驱动" 有何区别？
□ 长 horizon 的信用分配为什么是核心难题？有哪些初步解法（GiGPO/SpaRL/EPO）？
□ 6 大开放挑战里，哪几个和你自己的项目最相关？
```

## 下一步

回到 `02_rl_foundations.md`，把 §2.7 提到的 REINFORCE/PPO/DPO/GRPO 及其变体族
一个个拆开，配上目标函数和伪代码。
