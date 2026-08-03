# 07. 论文精读清单（按 Survey "能力 × 任务" 双重分类组织）

> 本文件把 Landscape Survey（500+ works）**精选**成可执行的精读路线。
> 每篇标注：它属于哪个「能力分类」、解决什么痛点、用什么算法/奖励。
> 用 `00` 的「读论文 6 问」模板拆解。

## 总纲必读（先读这个，否则后面没地图）

```text
[1] The Landscape of Agentic RL for LLMs: A Survey
    Zhang et al., arXiv:2509.02547 (TMLR)  ← 全专题骨架
    精读目标：MDP vs POMDP 形式化(§2)、能力分类(§3)、任务分类(§4)、挑战(§6)
```

---

## A. 能力视角（Capability）—— 按 Survey §3

### A1. Planning（规划）

| 论文 | 范式 | 关键点 | 链接 |
|---|---|---|---|
| RAP / LATS | RL 外部引导 | LLM+MCTS 树搜索规划 | arXiv:2305.14992 / 2310.14628 |
| VOYAGER | RL 内部驱动 | Minecraft 迭代构建技能库 | arXiv:2305.16291 |
| ETO | RL 内部驱动 | 把 DPO 用在成败轨迹 | arXiv:2403.00616 |
| PilotRL / AdaPlan | RL 内部驱动 | 过程级奖励塑形提升规划 | Survey §3.1 |

### A2. Tool Use（工具使用，近年爆发点）

| 论文 | 贡献 | 链接 |
|---|---|---|
| ToolRL | 工具 RL 训练，涌现纠错/组合 | arXiv:2504.13829 |
| ReTool | 让模型学会"调工具"替代纯推理 | arXiv:2504.11554 |
| OTC-PO / AutoTIR / VTool-R1 | 工具集成推理变体 | Survey §3.2 |
| DeepEyes / Pixel-Reasoner | 视觉主动工具调用 | Survey §3.2/§3.6 |
| ASPO | 长 horizon TIR 优势塑形（理论证明信用分配） | Survey §3.2 |
| GiGPO / SpaRL | turn-level 优势，缓解长轨迹信用分配 | Survey §3.2 |

### A3. Memory（记忆）

| 论文 | 类型 | 链接 |
|---|---|---|
| Prospect | 反射式检索(RAG) | Survey §3.3 |
| Memory-R1 | PPO/GRPO 学 ADD/UPDATE/DELETE | Survey §3.3 |
| MemAgent / MEM1 | Token 级显式记忆 | Survey §3.3 |
| MemoryLLM / IMM | 隐式潜 token 记忆 | Survey §3.3 |
| Zep / A-MEM / G-Memory | 结构化记忆（规则，RL 开放） | Survey §3.3 |

### A4. Self-Improvement（自我改进）

| 论文 | 类型 | 链接 |
|---|---|---|
| Reflexion / Self-refine / CRITIC | 言语自纠正（无梯度） | 经典 |
| KnowSelf (DPO+RPO) | 内化自纠正 | Survey §3.4 |
| Reflection-DPO | 把"反思后"当偏好 win | arXiv:2406.19567 |
| Absolute Zero / TTRL | 迭代自训练/课程 | Survey §3.4 |
| R-Zero / ISC | 自对弈/搜索 | Survey §3.4 |

### A5. Reasoning（推理）

```text
System 1 vs System 2：o1 / DeepSeek-R1（慢推理）
混合效率与严谨是开放方向（Survey §3.5）
```

### A6. Perception（感知/多模态）

| 论文 | 贡献 | 链接 |
|---|---|---|
| Visual-RFT / Vision-R1 / VLM-R1 | GRPO + 视觉可验证奖励 | Survey §3.6 |
| MM-Eureka | 多模态 Eureka | arXiv:2503.07365 |
| Ground-R1 / BRPO | 接地驱动主动感知 | Survey §3.6 |
| DeepEyes / Chain-of-Focus | Zoom-in 视觉聚焦 | Survey §3.6 |
| Visual Planning / GoT-R1 | 生成驱动视觉 CoT | Survey §3.6 |

### A7. 长 horizon 信用分配（Others）

| 论文 | 贡献 | 链接 |
|---|---|---|
| EPO / ThinkRM / SPO / RLVMR | 过程监督+结果奖励族 | Survey §3.7 |
| AgentPRM | MC 采样估每步价值 | arXiv:2502.10325 |
| InversePRM | 免 MC 直接从成功轨迹学 PRM | Survey §3.7 |
| SDPO | 段级 DPO 扩到多步 | Survey §3.7 |

---

## B. 任务视角（Task）—— 按 Survey §4

### B1. Search & Research
```text
DeepRetrieval / Search-R1 / WebDancer（开源）
ZeroSearch / SSRL（内部知识搜索）
OpenAI Deep Research（闭源）
```
### B2. Code Agent
```text
DeepCoder-14B / StepCoder / PSGPO（Outcome/Process reward 代码 RL）
自动软件工程（SWE-bench 系，见 06）
```
### B3. Mathematical Agent
```text
非正式/形式数学推理；结果/过程/混合奖励（连 Math 形式证明环境）
```
### B4. GUI Agent
```text
RL-free / 静态环境 RL / 交互环境 RL 三类（OSWorld/AndroidEnv）
```
### B5–B8. Vision / Embodied / Multi-Agent / Others
```text
Vision: 图像/视频/3D
Embodied: VLA 导航/操控（VOYAGER case study）
Multi-Agent: 非参数协调模块优化 / 选定策略优化 / 端到端 MARL
Others: TextGame / Table / Time Series / General QA
```

---

## C. 算法与框架（支撑性必读）

```text
[C1] PPO (Schulman 2017)               arXiv:1707.06347
[C2] DPO (Rafailov 2023)               arXiv:2305.18290
[C3] GRPO (DeepSeekMath 2024)          arXiv:2402.03300
[C4] DAPO (动态采样+Clip-Higher)        arXiv:2503.14476
[C5] Dr.GRPO / GSPO                    arXiv:2503.24412 / 2507.18071
[C6] AgentRL (全异步多轮)              arXiv:2510.04206
[C7] RAGEN + StarPO (轨迹级)           arXiv:2504.20073
[C8] AgentGym-RL (长程跨环境)          arXiv:2509.08750
[C9] MUA-RL (用户交互)                 arXiv:2508.18669
[C10] Slime 框架 / veRL / OpenRLHF     官方 GitHub
```

---

## D. 精读路线建议（4 周计划）

```text
Week 1（建地图）: [1] Landscape Survey + 01b + 02 算法族
Week 2（多轮+框架）: [C6][C7][C8] + 03 + 04，跑通一个 GRPO demo
Week 3（能力深入）: 选 2 个能力方向精读（建议 A2 工具 + A7 信用分配）
Week 4（任务+前沿）: 选 1 个任务方向（建议 B2 Code / 你的 UE5 测试）
                    + 跟进 Survey §6 的 6 大开放挑战最新工作
```

---

## E. 读论文的自检清单

```text
读每篇都回答（贴到笔记里）：
□ 它属于 Survey 哪个能力 / 任务分类？
□ 建模成 MDP 还是 POMDP？
□ Action Space 是什么？（文本/工具/GUI/代码）
□ Reward 从哪来？（RLVR/Outcome/Process/RM）
□ 用哪个算法？（PPO/GRPO/DPO/变体）
□ 解决的具体痛点？
□ 我能复现/改编到自己的项目吗？
```
