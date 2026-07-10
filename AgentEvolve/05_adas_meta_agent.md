# 05. ADAS：Agent 的设计也能自动进化

> 核心突破：不只是 Agent 的行为在进化，Agent 的"设计"本身也在自动优化。

---

## 1. 基本信息

| 项目 | 详情 |
|---|---|
| 论文 | "Automated Design of Agentic Systems" |
| 年份 | 2025（ICLR 2025） |
| GitHub | github.com/ShengranHu/ADAS |

---

## 2. 核心思路

```text
传统方法：
  人类工程师设计 Agent 架构：
    "我觉得应该用 Planner-Worker-Evaluator 模式"
    "我觉得工具应该这样注册..."
  → 人的认知局限 = Agent 能力上限

ADAS 的方法：
  让一个"元 Agent（Meta Agent）"自动设计和改进 Agent 架构：
    元 Agent 尝试不同设计 → 评估效果 → 保留好的 → 改进差的
  → 可能发现人类没想到的更好设计
```

---

## 3. 一个具体例子

```text
人类设计的 Agent：
  单 Agent，带记忆模块 + 5 个工具

ADAS 元 Agent 搜索后可能发现：
  方案 A：单 Agent + memory + 5 tools → 准确率 72%
  方案 B：主 Agent + 2 个子 Agent 并行 → 准确率 78%
  方案 C：Planner + Worker + Reviewer 三角色 → 准确率 85% ★
  方案 D：方案 C + 每个角色带独立记忆 → 准确率 82%（反而不如 C）

元 Agent 自动选择方案 C
它发现：三角色协作比独立记忆更重要
而这个发现不需要人类参与
```

---

## 4. 自进化的三个层次

```text
Level 1：行为进化（GRPO / SkillRL）
  Agent 在执行任务的过程中变聪明
  "给定 Agent，优化它的行为"

Level 2：记忆/技能进化（Voyager / AgentEvolver）
  Agent 的经验和技能在积累
  "给定 Agent，让它自己积累知识"

Level 3：设计进化（ADAS）
  Agent 的架构本身在自动优化
  "不只是优化 Agent 的行为，
   而是让'Agent 的设计'也在进化"
```

---

## 5. 一句话总结

> ADAS 证明了：Agent 的架构设计不再是人类的专属工作。元 Agent 可以自动搜索、评估和改进 Agent 的设计，可能发现人类从未想到的更好的架构。
