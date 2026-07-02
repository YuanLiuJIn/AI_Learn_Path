# 02. 底座模型与平台支持

> 目标：搞清楚用什么模型跑 GUI Agent、能不能在 PC 上跑、各平台（PC/手机/Web）的差异。
> 阅读时间：约 45 分钟。

## 1. 能在 PC 上跑吗？

**答案：能！PC 桌面恰恰是 GUI Agent 的核心场景。**

### PC 端可用的方式

```text
方式 1：Claude Computer Use（最成熟）
  → Anthropic 官方产品
  → 直接集成在 Claude Desktop App 中
  → 可以看屏幕、移动鼠标、点击、输入
  → 支持 macOS / Windows / Linux
  → 商业模式：按 token 付费

方式 2：Open-AutoGLM（开源免费）
  → 智谱开源，纯视觉方案
  → 通过 ADB 控制手机，通过键鼠模拟控制 PC
  → 可直接部署在本地

方式 3：UI-TARS Desktop（字节开源，34K Star）
  → 桌面端 GUI Agent
  → 支持 macOS / Windows
  → Apache 2.0 开源

方式 4：从零搭建（参考 KM:649442 文章）
  → 用 pyautogui + 多模态模型 API
  → 约 30 分钟搭建
  → 灵活度最高，但需要自己处理边缘情况

方式 5：browser-use（浏览器专用）
  → Python 库，一行代码让 AI 操作浏览器
  → 底层用 Playwright
```

### PC 端的技术要点

```python
# PC 端 GUI Agent 的关键挑战与解法

# 挑战 1：坐标归一化（不同分辨率屏幕）
def normalize_coordinates(x, y, screen_width, screen_height):
    """模型输出 0-1000 的相对坐标 → 转为实际像素"""
    actual_x = int(x / 1000 * screen_width)
    actual_y = int(y / 1000 * screen_height)
    return actual_x, actual_y

# 挑战 2：中文输入（pyautogui 不直接支持中文）
def type_chinese(text):
    """用剪贴板粘贴替代直接输入"""
    import pyperclip
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')

# 挑战 3：等待页面加载（不要盲目操作）
def smart_wait(screenshot_before, timeout=5):
    """比较前后截图判断页面是否变化"""
    for _ in range(timeout):
        time.sleep(1)
        screenshot_after = pyautogui.screenshot()
        if image_diff(screenshot_before, screenshot_after) > threshold:
            return True  # 页面变了
    return False  # 超时
```

## 2. 可用的底座模型

### 2.1 云端多模态模型（推荐入门）

| 模型 | 提供方 | GUI 理解能力 | 成本 | 适用场景 |
|---|---|---|---|---|
| **Claude Sonnet 4** | Anthropic | ⭐⭐⭐⭐⭐ | 高 | 复杂任务、长流程 |
| **Gemini 3 Flash** | Google | ⭐⭐⭐⭐ | 中低 | 快速原型、高并发 |
| **Doubao-Seed-1.8** | 字节跳动 | ⭐⭐⭐⭐ | 中低 | 国内场景优化 |
| **Qwen2.5-VL-72B** | 阿里 | ⭐⭐⭐⭐ | 中 | 中文理解强 |
| **GPT-4o** | OpenAI | ⭐⭐⭐⭐⭐ | 高 | 通用场景 |
| **GPT-4o-mini** | OpenAI | ⭐⭐⭐ | 低 | 简单任务、成本敏感 |

### 2.2 端侧模型（本地运行，隐私友好）

| 模型 | 参数量 | 硬件要求 | 特点 |
|---|---|---|---|
| **MiniCPM-V** | 2.4B-8B | 消费级 GPU / M 芯片 | 端侧部署，离线可用 |
| **Qwen2.5-VL-3B** | 3B | GTX 1060+ | GUI-R1 的基础模型 |
| **Florence-2** | 0.23B-0.77B | CPU 可跑 | 微软出品，轻量级 UI 理解 |
| **SmolVLM** | 2B | 低资源 | HuggingFace 出品，快速推理 |

### 2.3 模型选择建议

```
入门体验：
  用 Gemini 3 Flash（便宜 + GUI 理解不错）或 Claude Sonnet 4（最好但贵）
  → 调用 API，无需 GPU

精度优先：
  用 Claude Sonnet 4 或 GPT-4o
  → 复杂任务、长流程场景

成本优先：
  用 GPT-4o-mini 或 Gemini 3 Flash
  → 简单操作、高并发场景

隐私优先：
  用 MiniCPM-V 或 Qwen2.5-VL-3B 本地部署
  → 处理敏感数据的内部系统

手机端：
  用 MiniCPM-V → 端侧推理、离线可用
```

## 3. GUI Agent 的三端对比

### 3.1 PC 桌面端

```
┌──────── PC 桌面端 GUI Agent ────────┐
│                                      │
│  输入：任务指令（自然语言）            │
│  感知：定时截屏（pyautogui/mss）      │
│  模型：多模态大模型（理解截图）        │
│  执行：pyautogui/win32api（操控键鼠） │
│                                      │
│  优势：算力强、模型选择多、开源工具多  │
│  劣势：需要安装运行环境               │
│                                      │
│  代表项目：                            │
│  - Claude Computer Use（商业）        │
│  - UI-TARS Desktop（开源，34K Star）  │
│  - 从零搭建（pyautogui + 模型 API）   │
└──────────────────────────────────────┘
```

### 3.2 手机端

```
┌──────── 手机端 GUI Agent ────────────┐
│                                      │
│  输入：语音/文字指令                   │
│  感知：ADB 截屏 + 无障碍服务           │
│  模型：端侧模型（MiniCPM-V）或云端    │
│  执行：ADB shell input（模拟触控）     │
│                                      │
│  优势：随时随地、语音交互               │
│  劣势：屏幕小、识别难度高              │
│                                      │
│  代表项目：                            │
│  - 豆包手机（字节，商业产品）          │
│  - Open-AutoGLM（智谱，开源）          │
│  - Mobile-R1（学术论文）              │
└──────────────────────────────────────┘
```

### 3.3 Web 浏览器端

```
┌──────── Web 浏览器端 GUI Agent ──────┐
│                                      │
│  输入：自然语言指令                    │
│  感知：页面截图 或 DOM 文本化          │
│  模型：纯文本模型 或 多模态模型        │
│  执行：Playwright / Puppeteer / JS   │
│                                      │
│  优势：DOM 文本化更快更准、跨平台      │
│  劣势：仅限 Web                       │
│                                      │
│  代表项目：                            │
│  - Page-Agent（阿里，纯前端 JS 方案）  │
│  - browser-use（Python 库）           │
│  - Playwright MCP Server             │
└──────────────────────────────────────┘
```

## 4. 感知方案深度对比

```
┌─────────────────────────────────────────────────┐
│  截屏识别方案                                    │
│  ────────────                                   │
│  原理：截图 → 多模态模型 → 识别元素 → 输出坐标    │
│                                                │
│  工具链：pyautogui + Claude/Gemini API          │
│  优点：完全通用，任何界面都能用                  │
│  缺点：每步 ~1-3 秒延迟 + $0.01-0.05 成本       │
│  代表：Claude Computer Use、UI-TARS             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  DOM 文本化方案                                  │
│  ────────────                                   │
│  原理：提取 DOM → 编号 → 文本模型 → 输出编号     │
│                                                │
│  工具链：JS inject + GPT/Claude API             │
│  优点：快（~0.5秒）、准（不需要猜坐标）、便宜     │
│  缺点：仅限 Web，DOM 太深会超 token              │
│  代表：Page-Agent（阿里）                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  结构化解析方案（OmniParser）                     │
│  ──────────────────────────                     │
│  原理：目标检测模型 → 输出 bounding box → LLM    │
│                                                │
│  工具链：OmniParser + 多模态模型                  │
│  优点：兼顾通用性和准确性（先检测后推理）          │
│  缺点：多一步推理，略慢                          │
│  代表：微软 OmniParser                          │
└─────────────────────────────────────────────────┘
```

## 5. 一句话总结

> GUI Agent 能在 PC 上跑，实际 PC 恰恰是核心场景。底座模型从云端巨无霸（Claude/GPT-4o）到端侧小模型（MiniCPM-V）都有，选型取决于成本/精度/隐私的平衡。三端（PC/手机/Web）的技术栈不同，但核心思想一致：**感知 → 推理 → 执行**。
