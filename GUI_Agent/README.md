# GUI Agent 学习专题

> GUI Agent = 像人一样通过"看屏幕、动鼠标/键盘"来操作图形界面的 AI 智能体
> 与 API Agent 的本质区别：**不依赖 API，直接操作像素**

## 这个文件夹讲什么？

```
┌─ 01 概述与原理     → GUI Agent 是什么、怎么工作、四大模块
├─ 02 底座模型与平台  → 可用的模型（Claude/Gemini/豆包…）、能跑 PC 吗？
├─ 03 强化训练       → 如何用 RL(特别是 GRPO)让 GUI Agent 适应你的场景
├─ 04 Page-Agent     → 阿里开源纯前端方案：DOM 文本化 vs 截图，深入源码
├─ 05 633893 专项    → KM 万字长文：GRPO 在 UI 自动化上的完整实践
└─ references.md     → 统一文献索引
```

## 从零入门路线

| 顺序 | 文件 | 时间 | 目标 |
|---|---|---|---|
| 1 | `01_gui_agent_overview.md` | 1h | 理解"GUI Agent 是什么、怎么工作" |
| 2 | `02_base_models_and_platforms.md` | 45min | 知道用什么模型、能在哪些平台跑 |
| 3 | `03_training_and_fine_tuning.md` | 1.5h | 掌握 GRPO 训练方法、企业落地方案 |
| 4 | `04_page_agent_deep_dive.md` | 1.5h | 理解阿里 Page-Agent 的设计哲学与技术架构 |
| 5 | `05_grpo_gui_agent_633893.md` | 1h | 精读 KM 实战文章 |

## 前置知识

- 了解 AI Agent 基本概念（Agent Loop、工具调用、System Prompt）
- 了解多模态模型基本概念（能理解图片的 LLM）
- 可选：看过 `Harness_Engineering/` 专题（理解 Agent 外部控制系统的设计思想）

## 核心开源项目

| 项目 | 说明 | 链接 |
|---|---|---|
| **Page-Agent** | 阿里开源，纯前端 JS，DOM 文本化方案 | github.com/alibaba/page-agent |
| **Open-AutoGLM** | 智谱开源，手机端 GUI Agent | github.com/THUDM/AutoGLM |
| **OmniParser** | 微软开源，UI 截图 → 结构化元素识别 | github.com/microsoft/OmniParser |
| **browser-use** | 浏览器自动化 GUI Agent | github.com/browser-use/browser-use |
| **UI-TARS** | 字节开源，桌面端 GUI Agent | github.com/bytedance/UI-TARS |
| **Computer Use** | Anthropic Claude 的桌面操控能力 | docs.anthropic.com |

## 核心论文

| 论文 | 说明 |
|---|---|
| **GUI Agents: A Survey** (2024) | 权威综述，200+ 参考文献 |
| **GUI-R1** (2025) | GRPO 训练 GUI Agent（统一动作空间+跨平台） |
| **Mobile-R1** (2025) | 三阶段 RL 训练手机 GUI Agent |
| **OmniParser** (2024) | 微软 UI 解析器 |
| **OS-Copilot** (2024) | 操作系统级 GUI Agent |
