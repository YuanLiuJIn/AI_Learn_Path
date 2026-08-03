# 08. 参考文献与资源索引

---

## 核心论文

### 评测框架与哲学

| 论文 | 年份 | 贡献 |
|---|---|---|
| **HELM** (Liang et al.) | 2022 | 全景式评测框架，7 维度分析 |
| **lm-evaluation-harness** (Gao et al.) | 2021- | 标准化评测框架 |

### 知识评测

| 论文 | 年份 | 贡献 |
|---|---|---|
| **MMLU** (Hendrycks et al.) | 2021 | 57 学科知识评测 |
| **C-Eval** (Huang et al.) | 2023 | 中文 52 学科评测 |
| **AGIEval** (Zhong et al.) | 2023 | 标准化考试评测 |

### 推理评测

| 论文 | 年份 | 贡献 |
|---|---|---|
| **GSM8K** (Cobbe et al.) | 2021 | 小学数学文字题 |
| **MATH** (Hendrycks et al.) | 2021 | 竞赛数学 |
| **BBH** (Suzgun et al.) | 2022 | Big-Bench 难点精选 |

### LLM-as-Judge

| 论文 | 年份 | 贡献 |
|---|---|---|
| **MT-Bench / Chatbot Arena** (Zheng et al.) | 2023 | LLM-as-Judge + 人类投票 |
| **AlpacaEval** (Li et al.) | 2023 | 自动化指令遵循评测 |
| **Preference Leakage** | 2025 | 偏好泄漏问题研究 |

### 数据污染

| 论文 | 年份 | 贡献 |
|---|---|---|
| **Data Contamination Survey** | 2025 | 污染检测方法综述 |
| **LiveBench** (White et al.) | 2024 | 防污染实时评测 |

### Agent 评测

| 论文 | 年份 | 贡献 |
|---|---|---|
| **SWE-bench** (Jimenez et al.) | 2023 | 代码 Agent 评测 |
| **WebArena** (Zhou et al.) | 2023 | Web Agent 评测 |
| **AgentBench** (Liu et al.) | 2023 | 多环境 Agent 评测 |
| **GAIA** (Mialon et al.) | 2023 | 通用 Agent 评测 |

---

## 开源项目

| 项目 | 链接 | 用途 |
|---|---|---|
| lm-evaluation-harness | github.com/EleutherAI/lm-evaluation-harness | 标准评测框架 |
| HELM | crfm.stanford.edu/helm | 全景评测 |
| OpenCompass | github.com/open-compass/opencompass | 中文评测 |
| Chatbot Arena | chat.lmsys.org | 人类投票排名 |
| SWE-bench | swebench.com | Coding Agent 评测 |
| Inspect AI | inspect.aisi.org.uk | 安全评测框架 |
| LightEval | github.com/huggingface/lighteval | HuggingFace 官方评测 |

---

## 学习路线

```text
入门（2h）：
  01 → 02 → 跑通 lm-eval-harness 一次评测

进阶（3h）：
  03 → 04 → 05 → 理解污染/LLM-as-Judge/三大框架

深入（3h）：
  06 → 07 → 设计自己的评测 → 评测自己的 Agent

论文（4h）：
  HELM → MMLU → SWE-bench → Chatbot Arena
```
