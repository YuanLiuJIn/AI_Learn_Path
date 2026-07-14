# 模型评测学习专题

> 模型评测 = 用科学方法判断"一个模型到底有多强"。
> 不是看排行榜谁分高，而是理解评测的底层逻辑：测什么、怎么测、测得多可靠。

## 文件夹结构

| 文件 | 内容 | 预计时间 |
|---|---|---|
| `00_learning_path.md` | 学习路线与建议顺序 | 10min |
| `01_evaluation_overview.md` | 评测全景：为什么需要评测、评测分类法 | 1h |
| `02_benchmark_landscape.md` | 核心评测基准：MMLU、HumanEval、Chatbot Arena 等 | 1.5h |
| `03_contamination_and_reliability.md` | 数据污染、Goodhart 定律、评测信任危机 | 1h |
| `04_llm_as_judge.md` | LLM 做裁判：MT-Bench、AlpacaEval、偏好泄漏 | 1.5h |
| `05_evaluation_frameworks.md` | 工业化评测框架：HELM、lm-eval-harness、OpenCompass | 1.5h |
| `06_agent_evaluation.md` | Agent 评测：SWE-bench、WebArena、AgentBench | 1h |
| `07_practical_guide.md` | 动手：跑一个评测、设计自定义评测 | 1h |
| `08_projects_and_papers.md` | 论文索引、开源项目、学习路线 | 15min |

## 核心论文

| 论文 | 年份 | 贡献 |
|---|---|---|
| **HELM** (Liang et al.) | 2022 | 全景式评测框架：多场景、多指标、透明度 |
| **lm-evaluation-harness** (EleutherAI) | 2021- | 标准化评测框架，60+ benchmarks |
| **MMLU** (Hendrycks et al.) | 2021 | 跨 57 学科知识评测标准 |
| **Chatbot Arena / MT-Bench** (Zheng et al.) | 2023 | LLM-as-Judge + 人类偏好 Arena |
| **AlpacaEval** (Li et al.) | 2023 | 自动化 LLM 指令遵循评测 |
| **LiveBench** (White et al.) | 2024 | 防数据污染的实时更新评测 |
| **SWE-bench** (Jimenez et al.) | 2023 | 真实 GitHub Issue 评测 Coding Agent |

## 开源项目

| 项目 | 说明 | 链接 |
|---|---|---|
| **lm-evaluation-harness** | EleutherAI 统一评测框架 | github.com/EleutherAI/lm-evaluation-harness |
| **HELM** | Stanford 全景评测 | crfm.stanford.edu/helm |
| **OpenCompass** | 上海AI Lab 评测平台 | github.com/open-compass/opencompass |
| **Chatbot Arena** | LMSYS 实时人类投票 | chat.lmsys.org |
| **SWE-bench** | Coding Agent 评测 | swebench.com |
| **Inspect AI** | UK AISI 安全评测框架 | inspect.aisi.org.uk |
