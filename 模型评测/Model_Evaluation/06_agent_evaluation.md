# 06. Agent 评测

> 目标：理解如何评测一个 AI Agent，而不只是一个 LLM。

---

## 1. Agent 评测和 LLM 评测的区别

```text
LLM 评测：
  给一个 prompt → 模型输出一段文字 → 和标准答案对比
  简单、标准化

Agent 评测：
  给一个任务 → Agent 在环境中执行多步操作 → 判断任务是否完成
  复杂、难以标准化

关键差异：
  Agent 的"答案"不是一段文字，而是一系列操作。
  评测的是操作后的最终状态，而不是中间步骤。
```

---

## 2. 核心评测：SWE-bench

```text
全名：SWE-bench
论文：Jimenez et al., 2023
网站：swebench.com

做什么：
  从 GitHub 上抓取 2,294 个真实 Issue
  每个 Issue = 一个代码 bug / 功能需求
  给 Agent 代码仓库 + Issue 描述
  Agent 需要定位问题、修改代码、通过测试

评测方式：
  给 Agent 一份代码库副本
  给 Agent 一份 Issue 描述
  Agent 自己读代码 → 修改 → 跑测试
  如果测试通过 → 这个 Issue 被"解决"

关键指标：
  Resolved Rate = 解决的 Issue 数 / 总 Issue 数

子集：
  SWE-bench Verified：精选 500 个高质量 Issue
  SWE-bench Lite：精选 300 个，适合快速评测
  SWE-bench Multilingual：多语言版本

代表分数：
  2023 初始论文：最强模型 ≈ 1.96%
  2025 年：Devin ≈ 13.86%，Claude Code ≈ 40%+
```

---

## 3. 核心评测：WebArena

```text
全名：WebArena
论文：Zhou et al., 2023

做什么：
  自托管 4 个真实 Web 环境：购物、GitLab、CMS、地图
  812 个 Web 操作任务
  每个任务需要 Agent 在网页上完成具体操作

例：
  "在购物网站上搜索'蓝牙耳机'，加入购物车"
  "在 GitLab 上创建一个新的 Issue"
  "在地图上找到最近的咖啡店"

评测方式：
  Agent 在浏览器环境中操作
  操作完成后，评估页面的最终状态
  评分函数检查目标是否达成
```

---

## 4. 核心评测：AgentBench

```text
全名：AgentBench
论文：Liu et al., 2023

做什么：
  8 类交互环境：操作系统、数据库、知识图谱、网页、游戏...

评测方式：
  在不同环境中给 Agent 任务
  评估 Agent 能否在环境中完成目标

创新点：
  不只看"能不能聊天"
  看"能不能在不同类型环境中干活"
```

---

## 5. 其他重要 Agent 评测

| 评测 | Agent 类型 | 规模 | 特点 |
|---|---|---|---|
| **GAIA** | 通用 Agent | 466 题 | 需要多步推理 + 工具调用 |
| **OSWorld** | 桌面 Agent | 369 任务 | 操作真实操作系统 |
| **AndroidWorld** | 手机 Agent | 116 任务 | 操作真实 Android 系统 |
| **Mind2Web** | Web Agent | 2,350 任务 | 跨网站泛化能力 |
| **WebVoyager** | Web Agent | 643 任务 | 端到端 Web Agent 评测 |
| **OmniACT** | 桌面+Web | 9,802 任务 | 跨应用操作 |

---

## 6. Agent 评测的三大挑战

```text
挑战 1：环境搭建复杂
  不是给一个 prompt → 等一段文字
  需要搭建 Docker、配置沙箱、准备代码仓库
  SWE-bench 单次评测需要大量计算资源

挑战 2：评分标准非二元
  "解决了这个 Issue" → 是/否
  "完成了一半" → 怎么评分？
  需要更细粒度的评分方式

挑战 3：不可复现
  Agent 的行为受随机性影响
  同一任务跑两次结果不同
  需要多次运行取平均值
```

---

## 7. 一句话总结

> Agent 评测的核心是"能不能在环境中完成任务"而非"能不能答题"。SWE-bench（代码）、WebArena（网页）、AgentBench（多环境）是三大代表。Agent 评测比 LLM 评测复杂：环境搭建难、评分非二元、结果不可复现。
