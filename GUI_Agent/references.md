# GUI Agent 参考文献与资源索引

## 核心综述论文

| 论文 | 链接 | 说明 |
|---|---|---|
| **GUI Agents: A Survey** (2024) | arxiv.org/abs/2412.13501 | 权威综述，200+ 参考文献 |
| **A Comprehensive Survey of Agents for Computer Use** (2025) | arxiv.org/abs/2501.16150 | 桌面/手机/Web 全平台 Agent 综述 |

## GRPO 训练系列

| 论文 | 链接 | 说明 |
|---|---|---|
| **GUI-R1** (2025) | arxiv.org/pdf/2504.1... | GRPO 统一动作空间训练 GUI Agent |
| **Mobile-R1** (2025) | - | 三阶段 RL 训练手机 GUI Agent |
| **UI-R1** (2025) | - | GRPO 坐标优化（136 样本收敛） |
| **GUI-Critic-R1** (2025) | - | S-GRPO 术前批评机制 |
| **MobileGUI-RL** (2025) | - | MobGRPO 在线探索学习 |
| **InfiGUI-R1** (2025) | - | 从反应式到推理式 GUI Agent |

## 核心开源项目

| 项目 | 仓库 | Stars | 说明 |
|---|---|---|---|
| **Page-Agent** (阿里) | github.com/alibaba/page-agent | 14K+ | 纯前端 JS，DOM 文本化方案 |
| **UI-TARS Desktop** (字节) | github.com/bytedance/UI-TARS | 34K+ | 桌面端 GUI Agent，Apache 2.0 |
| **Open-AutoGLM** (智谱) | github.com/THUDM/AutoGLM | - | 手机端 GUI Agent |
| **OmniParser** (微软) | github.com/microsoft/OmniParser | - | UI 截图结构化识别 |
| **browser-use** | github.com/browser-use/browser-use | - | 浏览器自动化 Agent |
| **Computer Use** (Anthropic) | docs.anthropic.com | 商业 | Claude 桌面操控能力 |

## 底座模型

| 模型 | 提供方 | 说明 |
|---|---|---|
| Claude Sonnet 4 | Anthropic | Computer Use 能力最强的云端模型 |
| Gemini 3 Flash | Google | 性价比高，GUI 理解好 |
| Doubao-Seed-1.8 | 字节 | 国内场景优化 |
| GPT-4o / 4o-mini | OpenAI | 通用多模态 |
| Qwen2.5-VL 系列 | 阿里 | 中文理解强 |
| MiniCPM-V 系列 | 面壁智能 | 端侧部署，离线可用 |
| Florence-2 | 微软 | 轻量级 UI 理解（0.23B） |

## 腾讯内部文章（KM）

| 标题 | 作者 | 日期 | 阅读量 |
|---|---|---|---|
| **万字长文：GRPO for GUI Agent** ⭐ | zishanshi | 2025-07 | 2126 |
| **从原理到实践：从0到1手搓GUI Agent** ⭐ | zishanshi | 2025-12 | 2385 |
| **模型驱动·多端落地：跨平台GUI Agent测试提效** ⭐ | kaelyezhang | 2026-01 | 3911 |
| **LLM下半场是"行动"：基于Pydantic AI+OmniParser** | aidenmo | 2026-01 | 621 |
| **GUI Agent：从"能跑"到"能用"的11场仗** | alisdonwang | 2026-06 | 17 |
| **给视觉感知加一道哨兵：YOLO浮层态检测** | leenjiang | 2026-03 | 148 |
| **Florence-2模型在GUI Agent中的微调实践** | leenjiang | 2026-01 | 165 |
| **GUI Agent精准定位进化之路** | kevinzhguo | 2025-11 | 273 |
| **端侧大模型崛起到GUI Agent** | tobiazhang | 2026-01 | 340 |
| **豆包手机GUI平替：Open-AutoGLM简析** | yangyychen | 2026-01 | 70 |
| **Online强化学习构建更鲁棒的GUI Agent** | wenhaowyu | 2025-08 | 279 |
| **Visual GUI Agent** | hanrycai | 2024-11 | 299 |
| **GUI Agent多步在线强化学习** | zhongpuwang | 2025-11 | 55 |
| **万字长文GUI AGENT实践与效果** | kangqin | 2025-11 | 102 |

## 工具链

| 工具 | 用途 |
|---|---|
| **pyautogui** | PC 端键鼠模拟（截图/点击/输入/滚动） |
| **playwright** | 浏览器自动化 |
| **ADB** | Android 手机控制（截图/触控） |
| **mss** | 高性能截图库 |
| **pyperclip** | 剪贴板操作（中文输入方案） |

## 学习路线建议

```
入门（4h）:
  1. 01_gui_agent_overview.md（1h）
  2. 02_base_models_and_platforms.md（45min）
  3. KM:649442 从0到1手搓（2h 动手）

进阶（4h）:
  4. 03_training_and_fine_tuning.md（1.5h）
  5. 05_grpo_gui_agent_633893.md（1h）
  6. GUI-R1 / Mobile-R1 论文（1.5h）

深入（4h）:
  7. 04_page_agent_deep_dive.md（1.5h）
  8. GUI Agents: A Survey 论文（2h）
  9. OmniParser 论文（30min）
```
