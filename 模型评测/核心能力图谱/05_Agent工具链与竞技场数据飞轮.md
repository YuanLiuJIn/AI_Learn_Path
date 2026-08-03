# 05 Agent 工具链与竞技场、判别模型、数据飞轮

> 对应 JD：「Agent 工具链、对战平台、模型竞技场、模型效果判别模型、应用数据飞轮」。
> 这五个概念串起来是一条主线：**用工具让模型干活 → 用竞技场比模型 → 用判别模型替代人评 → 用数据飞轮持续进化**。

---

## 0. 五个概念的关系

```
Agent 工具链 ──(产生交互轨迹)──► 对战平台/竞技场 ──(产生人类偏好)──► 判别模型(奖励模型/Judge)
                                                                          │
应用数据飞轮 ◄────────(难例回流训练/评测)──────────────────────────────┘
```

---

## 1. Agent 工具链

### 1.1 什么是 Agent 工具链
让 LLM 能调用外部工具（搜索、代码执行、API、数据库）。核心能力：
- **Function Calling**：模型输出结构化调用（函数名 + 参数 JSON）。
- **工具调度框架**：规划 → 调工具 → 观察 → 再规划（ReAct 范式）。

### 1.2 关键协议与框架
- **ReAct**（Reason + Act）：思考-行动-观察循环。
- **Toolformer**：让模型自己学会何时调工具（自监督）。
- **MCP（Model Context Protocol）**：统一工具/数据源接入标准，解耦 Agent 与工具。
- **框架**：LangChain / LangGraph、AutoGen、MetaGPT、CrewAI。

### 1.3 评测视角（工具链怎么评）
- 工具调用**格式正确率**（JSON 可解析）。
- 工具选择**准确率**（该调 A 没调 B）。
- 参数**填充准确率**（缺参/错参）。
- 多步**轨迹成功率**（最终是否达成目标）。

**论文**：ReAct (arXiv:2210.03629)、Toolformer (arXiv:2302.04761)、ToolBench (arXiv:2307.16789)
**代码库**：[LangChain](https://github.com/langchain-ai/langchain)、[AutoGen](https://github.com/microsoft/autogen)、[MCP](https://github.com/modelcontextprotocol)

---

## 2. 对战平台 / 模型竞技场（Arena）

### 2.1 思想
众包真实用户，抛出问题，两个匿名模型各答一份，用户投票谁更好 → 用大量对战拟合模型实力排名。

### 2.2 Chatbot Arena（LMSYS）
- 累计数百万对战，用 **Bradley-Terry 模型 MLE** 拟合每个模型的 Elo 分数（非简单在线 Elo，避免顺序依赖）。
- 给出 **95% 置信区间**（bootstrap）。
- 衍生：**Arena-Hard**（从真实流量自动筛高质量 prompt，可分离度更高）。

### 2.3 评测视角
- Arena 排名是"真实偏好"的黄金标准，但**慢、贵、易被刷**。
- 内部可自建轻量 Arena（用员工/标注员对战）做版本对比。
- 必须报告置信区间，避免"差 2 分"误导（语言笔记 §7）。

**论文**：Chatbot Arena (arXiv:2403.04132)、Arena-Hard (arXiv:2406.11939)
**代码库**：[lmsys-chatbot-arena](https://github.com/lm-sys/FastChat)（含 MT-Bench/Arena 实现）

---

## 3. 模型效果判别模型（Reward Model / Judge）

### 3.1 三类判别模型
| 类型 | 训练数据 | 用途 | 局限 |
|---|---|---|---|
| **Reward Model (RM)** | (prompt, chosen, rejected) | RLHF 奖励信号 | 易奖励黑客 |
| **LLM-as-Judge** | 无训练，靠 prompt | 快速 pairwise/单答打分 | 位置/长度/自我偏好偏差 |
| **偏好模型（图像）** | 人 pairwise | T2I 排序 | reward hacking |

### 3.2 LLM-as-Judge 三大偏差与解法（面试高频）
- **位置偏差**：GPT-4 偏好第一个 → 交换顺序各评一次，不一致判平局。
- **长度偏差**：更长更易赢 → 长度控制回归（AlpacaEval-LC）。
- **自我增强**：偏好自家输出 → 多 judge 投票 / 换 judge 交叉。

### 3.3 验证 Judge 靠谱的方法
抽样人工标注，算 **agreement rate + Spearman/Kendall**，目标 ≥0.7 才能替代人评做日常回归。

> 详细见 `语言模型评测/学习笔记.md` §3-§4（MT-Bench、RewardBench、AlpacaEval-LC）。

**论文**：MT-Bench (arXiv:2306.05685)、RewardBench (arXiv:2403.13787)、AlpacaEval-LC (arXiv:2404.04475)

---

## 4. 应用数据飞轮

### 4.1 什么是数据飞轮
```
用户使用产品
  → 收集真实 query + 模型输出 + (可选)用户反馈(点赞/点踩/修正)
  → 难例挖掘(答错/低分/长尾)
  → 构造/标注训练与评测数据
  → 重新训练 + 重新评测(回归)
  → 模型变好 → 更多用户 → 更多数据
```

### 4.2 评测在数据飞轮里的位置
- **挖掘难例**：用现有评测集 + 线上 bad case 找短板维度。
- **构造评测锚点**：难例沉淀为黄金集，防回归。
- **闭环监控**：线上分布漂移触发重新评测。

### 4.3 工程要点
- 反馈噪声大（用户误点），需**置信度过滤**。
- 数据回流要**防污染**（线上数据别进训练后又进评测）。
- 飞轮要可观测：每转一圈，哪些维度提升了（看板）。

---

## 5. 评测视角整合（这章与评测岗的连接）

| JD 概念 | 评测岗要做的 |
|---|---|
| Agent 工具链 | 设计工具调用准确率 / 任务完成率评测集 |
| 对战平台 | 搭内部轻量 Arena，做版本 Elo 对比 |
| 判别模型 | 选型/验证 Judge（偏差+人评一致性），建 RM 评测 |
| 数据飞轮 | 用评测难例反哺训练数据，建回归黄金集 |

---

## 6. 关键论文与代码库

| 主题 | 论文 | 代码 |
|---|---|---|
| Agent 范式 | ReAct (2210.03629)、Toolformer (2302.04761) | langchain/autogen |
| 竞技场 | Chatbot Arena (2403.04132)、Arena-Hard (2406.11939) | FastChat |
| 判别模型 | MT-Bench (2306.05685)、RewardBench (2403.13787) | FastChat / trl |
| Agent 评测 | τ-bench (2406.12045)、WebArena (2307.13854)、BFCL | tau-bench |
| 数据飞轮 | 多为企业内部实践，参考 InstructGPT 反馈收集 | — |
