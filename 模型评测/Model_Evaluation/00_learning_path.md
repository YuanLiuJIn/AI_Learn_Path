# 00. 模型评测学习路线

---

## 学习地图

```
第 1 步：为什么需要评测？（1h）
  01_evaluation_overview.md
  → 评测分类法：知识/推理/安全/Agent/多模态
  → 评测的四大挑战：覆盖、公平、可靠、时效

第 2 步：有哪些评测？（1.5h）
  02_benchmark_landscape.md
  → 50+ 主流评测基准全景
  → 什么时候用哪个？

第 3 步：评测可信吗？（1h）
  03_contamination_and_reliability.md
  → 数据污染：模型的分数可能是"背答案"得来的
  → Goodhart 定律：当指标变成目标，它就不再是好指标

第 4 步：LLM 能当裁判吗？（1.5h）
  04_llm_as_judge.md
  → MT-Bench、AlpacaEval、Chatbot Arena
  → 偏好泄漏：裁判可能偏袒自己

第 5 步：怎么工业级跑评测？（1.5h）
  05_evaluation_frameworks.md
  → lm-eval-harness 从入门到自定义
  → HELM 多维全景评测
  → OpenCompass 中文评测

第 6 步：怎么评测 Agent？（1h + 2h 深入）
  06_agent_evaluation.md
  → SWE-bench：代码能否通过测试？
  → WebArena：能不能操作真实网页？
  → AgentBench：8 类交互环境
  06b_agent_evaluation_deepdive.md（深入版）
  → Agent 是什么 / 评估系统组成 / 评估维度（pass@k、pass^k）
  → 评分器三类（规则 / 模型 / 人工）+ 9 大场景全集与 benchmark
  → 发展趋势：环境 / 代理 / 评估者 / 指标 四视角

第 7 步：动手实践（1h）
  07_practical_guide.md
  → 跑通 lm-eval-harness
  → 设计自己的评测任务
```

## 前置知识

- 了解 LLM 基本能力（预训练、SFT、RLHF）
- 了解 Python 基础
- 可选：了解 AI Agent 基本概念

## 核心论文阅读优先级

```text
必读（3 篇）：
  HELM (2022) — 评测哲学：不只一个分数
  MMLU (2021) — 最广泛使用的知识评测
  SWE-bench (2023) — Agent 评测的代表作

选读：
  Chatbot Arena / MT-Bench (2023) — LLM-as-Judge
  LiveBench (2024) — 防污染评测
```
