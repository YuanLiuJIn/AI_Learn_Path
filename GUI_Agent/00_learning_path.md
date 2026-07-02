# GUI Agent 学习路线

## 学习地图

```
第 1 步：理解原理（1h）
  01_gui_agent_overview.md
  → 什么是 GUI Agent？和 API Agent 有什么区别？
  → 四大模块：感知 → 推理 → 执行 → 记忆
  → 感知-决策-执行循环

第 2 步：知道用什么（45min）
  02_base_models_and_platforms.md
  → 可用底座模型（Claude/Gemini/豆包/MiniCPM…）
  → 能在 PC 上跑吗？（能！甚至是核心场景）
  → 手机/Web/桌面三端的差异

第 3 步：学会训练（1.5h）★ 最实用的章节
  03_training_and_fine_tuning.md
  → SFT vs RL → 为什么 GRPO 是现在主流
  → 三阶段训练法（感知预训练→单步优化→任务级优化）
  → 企业落地方案：数据准备→奖励设计→训练→迭代

第 4 步：深入源码（1.5h）
  04_page_agent_deep_dive.md
  → 阿里 Page-Agent：纯前端 JS 方案
  → DOM 文本化 vs 截图识别（两种路线的核心差异）
  → 架构解析、关键代码、适用场景

第 5 步：精读实战（1h）
  05_grpo_gui_agent_633893.md
  → KM 万字长文精读
  → GUI-R1 / Mobile-R1 / MobileGUI-RL 论文解读
```

## 核心论文推荐

| 论文 | 必读程度 | 阅读时间 |
|---|---|---|
| **GUI Agents: A Survey** (2024) | ⭐⭐⭐⭐⭐ | 2h（综述） |
| **GUI-R1** (2025) | ⭐⭐⭐⭐⭐ | 1h |
| **Mobile-R1** (2025) | ⭐⭐⭐⭐ | 1h |
| **OmniParser** (2024) | ⭐⭐⭐⭐ | 45min |
| **OS-Copilot** (2024) | ⭐⭐⭐ | 45min |

## 动手实践推荐

| 难度 | 项目 | 时间 |
|---|---|---|
| ★☆☆ 快速体验 | `browser-use` — 用一行代码让 AI 操作浏览器 | 30min |
| ★★☆ 深入理解 | `Open-AutoGLM` — 在手机上跑 GUI Agent | 1h |
| ★★★ 从零搭建 | 参考 `从原理到实践 \| 从0到1快速手搓GUI Agent`（KM:649442） | 2h |
| ★★★ 生产级 | 参考 GRPO 训练流程（633893 文章）| 按需 |

## 常见问题

**Q: GUI Agent 和 RPA 有什么区别？**
A: RPA 是**确定性规则**（"找 ID=xxx 的按钮，点击"），GUI 一变就坏。GUI Agent 是**语义理解**（"找那个写着'提交'的按钮"），UI 改版也能自适应。

**Q: 我需要 GPU 吗？**
A: 推理可以用云端 API（无需 GPU）。训练才需要 GPU（RL 训练通常用 4-8 张 A100）。

**Q: 能操作我公司的内部系统吗？**
A: 能。这就是 GUI Agent 相对于 API Agent 的最大优势——不依赖 API，只要是看得见的界面就能操作。
