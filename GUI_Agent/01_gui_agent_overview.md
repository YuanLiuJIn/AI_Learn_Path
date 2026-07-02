# 01. GUI Agent 概述与工作原理

> 目标：理解 GUI Agent 是什么、和 API Agent 的本质区别、核心工作原理。
> 阅读时间：约 1 小时。

## 0. 一句话定义

> GUI Agent = 通过"看屏幕截图 + 理解语义 + 模拟键鼠操作"来自动化图形界面的 AI 智能体。

## 1. 它和 API Agent 有什么本质区别？

```
API Agent（传统）:
  用户说"帮我订咖啡馆附近的酒店"
  → Agent 调用 Booking.com 的搜索 API
  → 拿到 JSON 结果
  → 调用预订 API
  → 完成

  前提：Booking.com 必须有这套 API，而且你要有权限！

GUI Agent（新范式）:
  用户说"帮我订咖啡馆附近的酒店"
  → Agent 截屏看当前桌面
  → 识别出浏览器图标、点击打开
  → 在地址栏输入 booking.com
  → 看到搜索框、输入文字
  → 看到结果列表、点击第一个
  → 一路点选完成预订

  前提：只要有图形界面就能操作！不需要任何 API！
```

### 对比表格

| 维度 | API Agent | GUI Agent |
|---|---|---|
| **依赖** | 必须有 API | 只要有 GUI 界面 |
| **准确率** | 高（结构化数据） | 中-高（受视觉识别影响） |
| **灵活性** | 低（受 API 能力限制） | 高（人能操作的它都能操作） |
| **维护成本** | API 不变就行 | UI 改版不影响（语义理解） |
| **速度** | 快（毫秒级） | 慢（秒级，需要截图+推理） |
| **成本** | 低（一次 API 调用） | 高（每步都要调多模态模型） |
| **适用** | 有标准 API 的场景 | 老旧系统、内部系统、没有 API 的场景 |

### 什么时候选 GUI Agent？

```
✅ 系统没有 API（内部老系统、遗留软件）
✅ API 权限申请困难（跨部门、跨公司）
✅ UI 经常变化（靠语义理解自适应）
✅ 需要模拟真实用户行为（测试/安全扫描）
✅ 跨应用协作（Excel→PPT→微信）

❌ 有成熟 API → 优先用 API Agent（更快更便宜）
❌ 追求极致速度 → 不适合（每步都要截图+推理）
```

## 2. 核心工作原理：四大模块

```
┌────────────────────────────────────────────────┐
│                  GUI Agent                      │
│                                                │
│  ┌───────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ 1.感知系统 │→│ 2.推理系统│→│ 3.执行系统   │ │
│  │ (看屏幕)   │  │ (想下一步)│  │ (点按钮/输入)│ │
│  └───────────┘  └──────────┘  └─────────────┘ │
│        ↑                            │          │
│        └──────── 4.记忆系统 ────────┘          │
│           (记住操作历史、避免死循环)            │
└────────────────────────────────────────────────┘
```

### 模块 1：感知系统（Perception）——"屏幕长什么样？"

这是 GUI Agent 区别于 API Agent 的核心。

```python
# 感知系统的三种主流方案

# 方案 A：纯截图（最通用，任何平台都能用）
screenshot = pyautogui.screenshot()
elements = multimodal_model.identify(screenshot)
# → "左上角有一个搜索框，中间有5个搜索结果，右下角有'下一页'按钮"

# 方案 B：DOM 文本化（Web 专用，更快更准）
# 把网页 DOM 结构转为文本，配合可交互元素的编号
dom_text = """
[1] <button> 登录 </button>
[2] <input> 搜索框 placeholder="请输入关键词" </input>
[3] <a> 帮助中心 </a>
[4] <div> 最新活动：全场8折 </div>
"""
# 模型只需要输出 "click [2]" 就能定位，无需坐标计算

# 方案 C：OmniParser（微软方案，结构化 UI 理解）
# 对截图做目标检测 → 输出每个元素的 bounding box + 语义标签
parsed = omni_parser.parse(screenshot)
# → [
#   {id: 1, type: "button", text: "提交", box: [x1,y1,x2,y2]},
#   {id: 2, type: "input", text: "姓名", box: [x1,y1,x2,y2]},
# ]
```

### 模块 2：推理系统（Reasoning）——"下一步该做什么？"

```python
def reasoning_step(screenshot, task, history):
    """多模态模型根据当前截图和任务目标，推理下一步操作"""
    
    prompt = f"""你是一个 GUI 操作助手。

当前任务: {task}

已完成的操作:
{format_history(history)}

请根据当前截图，决定下一步操作。输出格式:
<think>你的推理过程（为什么要做这个操作）</think>
<action>{"click"|"type"|"scroll"|"hotkey"|"wait"|"finished"}</action>
<params>具体参数（坐标/文本/按键）</params>
"""
    
    response = multimodal_model.chat(
        messages=[{"role": "user", "content": prompt}],
        images=[screenshot],  # ← 关键：把截图也传给模型
    )
    
    return parse_action(response)
```

**为什么必须用多模态模型？**

```
纯文本模型：看到 "请点击'提交'按钮"
  → 它不知道'提交'按钮在屏幕上的什么位置
  → 无法输出 (x, y) 坐标

多模态模型：同时看到文字指令 + 屏幕截图
  → 在截图上找到写着"提交"的按钮
  → 输出准确的坐标
```

### 模块 3：执行系统（Action）——"把决策变成操作"

```python
class ActionExecutor:
    """支持的 GUI 操作类型"""
    
    ACTIONS = {
        "click": lambda x, y: pyautogui.click(x, y),
        "double_click": lambda x, y: pyautogui.doubleClick(x, y),
        "right_click": lambda x, y: pyautogui.rightClick(x, y),
        "type": lambda text: paste_text(text),  # 用粘贴避免中文问题
        "hotkey": lambda *keys: pyautogui.hotkey(*keys),
        "scroll": lambda dx, dy: pyautogui.scroll(dy),
        "drag": lambda x1, y1, x2, y2: pyautogui.drag(x2-x1, y2-y1),
        "screenshot": lambda: pyautogui.screenshot(),
        "wait": lambda seconds: time.sleep(seconds),
    }
    
    @staticmethod
    def paste_text(text):
        """用剪贴板粘贴中文（pyautogui 不支持中文输入）"""
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
```

### 模块 4：记忆系统（Memory）——"别重复做已经做过的事"

```python
class ShortTermMemory:
    """防止死循环：记住已经做过的操作"""
    
    def __init__(self):
        self.action_history = []  # [(action_type, params, screenshot_hash), ...]
        self.completed_inputs = set()  # 已完成的输入操作
    
    def is_repeat_action(self, action, current_screenshot_hash):
        """检测是否在重复同样的操作（死循环标志）"""
        recent = self.action_history[-5:]
        same_actions = [
            a for a in recent
            if a["action"] == action.type 
            and a["screenshot_hash"] == current_screenshot_hash
        ]
        return len(same_actions) >= 3  # 连续 3 次同屏同操作 = 卡住了
    
    def was_input_completed(self, field_name, value):
        """检测输入是否已经完成过"""
        key = f"{field_name}:{value}"
        if key in self.completed_inputs:
            return True
        self.completed_inputs.add(key)
        return False
```

## 3. 感知-决策-执行循环

```python
def gui_agent_loop(task: str, max_steps: int = 100):
    """GUI Agent 的主循环"""
    memory = ShortTermMemory()
    executor = ActionExecutor()
    history = []
    
    for step in range(max_steps):
        # 1. 感知：截取当前屏幕
        screenshot = executor.ACTIONS["screenshot"]()
        screenshot_hash = md5(screenshot)
        
        # 2. 记忆检查：是不是在死循环？
        if memory.is_repeat_action(last_action, screenshot_hash):
            print(f"⚠️ 检测到死循环！尝试切换策略")
            # 可以尝试 scroll、wait、或返回上一步
        
        # 3. 推理：让多模态模型决定下一步
        action = reasoning_step(
            screenshot=screenshot,
            task=task,
            history=format_history(history),
        )
        
        # 4. 执行
        if action.type == "finished":
            print(f"✅ 任务完成！共 {step} 步")
            return True
        
        result = executor.execute(action)
        history.append({"step": step, "action": action, "screenshot_hash": screenshot_hash})
    
    print(f"❌ 达到最大步数 {max_steps}，任务未完成")
    return False
```

## 4. 两种技术路线

| | 截图识别方案 | DOM 文本化方案 |
|---|---|---|
| **原理** | 截屏 → 多模态模型理解像素 | 提取 DOM → 文本化 → 文本模型理解结构 |
| **代表项目** | Claude Computer Use、UI-TARS、Open-AutoGLM | **Page-Agent（阿里）**、browser-use |
| **优点** | 通用（任何界面都行）、不依赖前端改造 | 更快、更便宜、元素定位精准（不需要坐标推理） |
| **缺点** | 慢（每步都要截图+推理）、贵（每次调多模态模型）、坐标可能不准 | 仅限 Web、DOM 过深会超 token |
| **适用** | 桌面应用、混合场景 | 纯 Web 页面 |

## 5. 经典论文与项目脉络

```
2018-2022：传统 RPA + 脚本自动化（UIPath、Selenium）
2023    ：LLM 出现 → 自然语言→操作数据 的映射（Mind2Web）
2024    ：多模态模型成熟 → 纯视觉方案成为可能
         ├─ OmniParser（微软）：截图→结构化 UI 元素
         ├─ OS-Copilot：操作系统级 Agent
         └─ Claude Computer Use：商业产品落地
2025    ：RL 训练让 GUI Agent 从"能跑"到"能用"
         ├─ GUI-R1：GRPO 统一训练框架
         ├─ Mobile-R1：三阶段 RL 训练手机 Agent
         └─ 阿里 Page-Agent：纯前端方案（DOM 文本化）
2026    ：端侧普及 + 企业落地
         ├─ 豆包手机 / AutoGLM 出圈
         └─ 各大厂内部大规模应用
```

## 6. 一句话总结

> GUI Agent = 多模态模型（眼睛 + 大脑）+ 键鼠模拟（手）+ 记忆系统（不重复犯错）。它不依赖 API，只要是看得见的界面就能操作，**是把 AI 从"聊天工具"升级为"真正能帮你干活的操作员"的关键一步**。
