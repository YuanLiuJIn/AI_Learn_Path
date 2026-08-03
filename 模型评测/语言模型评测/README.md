# 语言模型（LLM）评测：标准、评测集、方法与论文项目

> 整理时间：2026-07。面向模型评测岗位准备。

---

## 一、评测标准（能力维度拆解）

大厂/学术界通用的 LLM 能力维度切分：

| 维度 | 说明 | 代表评测集 |
|---|---|---|
| 知识广度 | 学科知识、常识 | MMLU、MMLU-Pro、C-Eval、CMMLU、AGIEval |
| 深度推理 | 数学、逻辑、科学 | GSM8K、MATH、GPQA Diamond、AIME、FrontierMath |
| 代码能力 | 生成、补全、仓库级修复 | HumanEval、MBPP、LiveCodeBench、SWE-bench |
| 指令遵循 | 格式/约束遵守 | IFEval、FollowBench |
| 长上下文 | 检索、聚合、推理 | Needle-in-a-Haystack、RULER、LongBench、∞Bench |
| Agent / 工具调用 | 多轮决策、函数调用 | τ-bench、BFCL、AgentBench、WebArena、GAIA |
| 对话与人类偏好 | 开放式回答质量 | MT-Bench、Arena Elo、AlpacaEval 2.0、Arena-Hard |
| 真实性 / 幻觉 | 事实性、拒答校准 | TruthfulQA、SimpleQA、HaluEval |
| 安全与对齐 | 有害内容、越狱鲁棒性 | HarmBench、AdvBench、SafetyBench |
| 效率 | 延迟、吞吐、成本、Token 效率 | 自建性能压测 |

**评测范式三分法**（面试高频）：
1. **客观评测**：选择题/可判定答案 → 准确率、EM、pass@k。稳定、可复现，但易饱和、易污染。
2. **主观评测**：开放式生成 → 人工标注 / LLM-as-a-Judge → 胜率、Elo、评分。贴近真实体验，但成本高、有偏差。
3. **场景化/业务评测**：面向具体产品链路的端到端评测集，大厂 JD 中的「业务领域 Benchmark 构建」。

---

## 二、热门评测集与原始论文

### 知识与综合
| 评测集 | 论文 | 说明 |
|---|---|---|
| MMLU | arXiv:2009.03300 | 57 学科 4 选 1，最经典基线，已接近饱和 |
| MMLU-Pro | arXiv:2406.01574 | 10 选 1、更强推理，缓解饱和 |
| BIG-bench | arXiv:2206.04615 | 204 任务的超大集合 |
| HELM | arXiv:2211.09110 | 斯坦福「整体评估」框架，多指标（准确率/校准/鲁棒/公平/效率）同时报告 |
| C-Eval | arXiv:2305.08322 | 中文 52 学科 |
| CMMLU | arXiv:2306.09212 | 中文多任务，强调中国特有知识 |
| AGIEval | arXiv:2304.06364 | 人类考试题（高考、法考、GRE） |
| GPQA | arXiv:2311.12022 | 研究生级理科题，Google-proof |
| Humanity's Last Exam (HLE) | arXiv:2501.14249（Nature 2026） | 2500 道专家级题，多模态，前沿难度基准 |

### 推理与数学
- **GSM8K** arXiv:2110.14168 — 小学数学应用题，CoT 经典基线
- **MATH** arXiv:2103.03874 — 竞赛数学
- **ARC** arXiv:1803.05457 / **HellaSwag** arXiv:1905.07830 — 常识推理老三样
- **ARC-AGI** — 抽象推理网格题，测「流体智能」而非知识
- **FrontierMath** — Epoch AI 出品，未公开的高难数学题，抗污染

### 代码
- **HumanEval** arXiv:2107.03374（Codex 论文）— pass@k 指标的源头
- **MBPP** arXiv:2108.07732
- **SWE-bench** arXiv:2310.06770 — 真实 GitHub issue 修复，Agent 时代主战场；衍生 SWE-bench Verified / Multimodal
- **LiveCodeBench** — 持续更新题目，抗污染
- **Terminal-Bench** — 终端环境下的复杂命令行任务

### 指令遵循与人类偏好
- **MT-Bench + Chatbot Arena** arXiv:2306.05685 — **必读**，LLM-as-a-Judge 的奠基论文，系统分析 position/verbosity/self-enhancement bias
- **AlpacaEval 2.0（长度控制）** arXiv:2404.04475 — 修正长度偏好
- **Arena-Hard** arXiv:2406.11939 — 从 Arena 真实流量自动构建高区分度评测集
- **IFEval** arXiv:2311.07911 — 可程序化验证的指令约束

### Agent 与工具
- **τ-bench** arXiv:2406.12045 — 真实客服场景多轮工具调用 + 规则遵守
- **AgentBench** arXiv:2308.03688 — 8 类环境的 Agent 综合评测
- **WebArena** arXiv:2307.13854 — 可复现的真实网站环境
- **GAIA** arXiv:2311.12983 — 通用助手任务，人类简单/模型困难
- **BFCL**（Berkeley Function Calling Leaderboard）— 函数调用能力事实标准

### 真实性与安全
- **TruthfulQA** arXiv:2109.07958
- **SimpleQA**（OpenAI）— 短事实问答，测幻觉与拒答校准
- **RewardBench** arXiv:2403.13787 — 奖励模型评测（RLHF 链路必需）

### 抗污染 / 动态基准
- **LiveBench** arXiv:2406.19314 — 每月更新题目 + 客观可判定答案，**抗污染范式代表作**

---

## 三、评测方法与指标

### 3.1 客观题的实现细节（面试常考）
- **打分方式**：生成式匹配 vs. **PPL/loglikelihood 选项打分**（harness 默认），两者结果差异大
- **Few-shot 设置**：0-shot / 5-shot / CoT，必须与被比较模型对齐
- **答案抽取**：正则 / 格式化输出 / judge 抽取，抽取失败率要单独报告
- **pass@k 无偏估计**：\(\text{pass@}k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}\)
- **解码参数**：temperature、top_p、seed 会显著影响结果，需固定并记录

### 3.2 主观评测
- **人工标注**：Side-by-side 双盲对比、Likert 评分、标注规范（Rubric）设计、标注员一致性（Cohen's κ / Krippendorff's α）
- **Elo / Bradley-Terry**：Arena 排名的数学基础，置信区间与采样策略
- **LLM-as-a-Judge**：
  - 三种模式：pairwise comparison / single answer grading / reference-guided grading
  - 已知偏差：位置偏差（交换顺序取平均）、冗长偏差（长度控制）、自我偏好、格式偏好
  - 校验方法：与人工标注的一致率（agreement rate）、Spearman 相关

### 3.3 结果可靠性
- **数据污染检测**：n-gram 重叠、canary string、成员推断、时间切分（cut-off 前后对比）
- **方差控制**：多次采样取均值 + 置信区间、bootstrap
- **饱和与区分度**：题目难度分布、item response theory 思路
- **Goodhart 定律**：刷榜 vs 真实能力，业务侧需要私有 holdout 集

---

## 四、开源框架与项目（必须动手跑通）

| 项目 | 说明 |
|---|---|
| **OpenCompass**（open-compass/opencompass）| 上海 AI Lab，国内大厂最常用，中英文数据集全，配置化评测 |
| **lm-evaluation-harness**（EleutherAI）| 国际事实标准，HF Open LLM Leaderboard 的底座 |
| **EvalScope**（ModelScope）| 阿里出品，评测 + 性能压测一体 |
| **HELM**（stanford-crfm/helm）| 多指标整体评估范式 |
| **FastChat**（lm-sys/FastChat）| MT-Bench、Arena 的实现 |
| **LiveBench** | 抗污染动态基准的工程实现参考 |
| **SWE-bench / SWE-agent** | Agent 代码评测的容器化沙箱设计范本 |
| **DeepEval / Ragas / promptfoo** | 面向应用层（RAG、Prompt）的评测库，业务评测常用 |
| **LMSYS Chatbot Arena** | Elo 排行榜与投票数据集 |

---

## 五、精读论文清单（按优先级）

1. **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena**（2306.05685）
2. **HELM: Holistic Evaluation of Language Models**（2211.09110）
3. **MMLU-Pro**（2406.01574）+ 原始 **MMLU**（2009.03300）
4. **LiveBench**（2406.19314）— 抗污染设计
5. **SWE-bench**（2310.06770）
6. **τ-bench**（2406.12045）
7. **Length-Controlled AlpacaEval**（2404.04475）
8. **Arena-Hard / BenchBuilder**（2406.11939）— 如何自动造高质量评测集
9. **RewardBench**（2403.13787）
10. **Humanity's Last Exam**（2501.14249）

---

## 六、动手任务建议

1. 用 OpenCompass 对 Qwen / Llama 系列跑 MMLU + C-Eval + GSM8K，对比官方分数，分析差异来源；
2. 用 lm-evaluation-harness 复现同一评测集，比较两个框架结果差异（打分方式、prompt 模板）；
3. 实现一个 pairwise LLM-Judge，量化位置偏差与长度偏差，并与人工标注算一致率；
4. 自建一个 200 题的垂类评测集（含标注规范文档），跑通端到端 Pipeline 并出报告。
