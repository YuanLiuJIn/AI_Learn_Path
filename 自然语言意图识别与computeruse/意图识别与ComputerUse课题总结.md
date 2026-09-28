# 面向不确定性自然语言指令的意图识别与 Computer Use 结构化执行

## 1. 课题概述

### 1.1 研究目标

本课题希望训练一个基于 Qwen 的语言模型，使其能够接受现实中可能存在以下问题的人类自然语言指令：

- 信息不完整；
- 表达模糊；
- 存在指代不明；
- 缺少必要参数；
- 依赖历史上下文；
- 与当前计算机界面状态不一致；
- 存在多个合理解释。

模型不应在不确定时擅自猜测并执行，而应当：

1. 识别用户意图；
2. 抽取已知参数；
3. 判断任务是否具备执行条件；
4. 找出缺失或歧义信息；
5. 向用户提出最少但必要的澄清问题；
6. 根据用户补充的信息更新任务状态；
7. 直到达到足够执行置信度后，输出格式严格、语义明确、可验证的 Computer Use 执行轨迹；
8. 执行动作后检查环境状态，并在失败时恢复、重新规划或再次询问用户。

### 1.2 推荐课题名称

中文：

> 面向不完整自然语言指令的主动澄清与结构化 Computer Use 执行轨迹生成

英文：

> Active Clarification and Structured Computer-Use Trajectory Generation under Incomplete Natural-Language Instructions

也可以进一步突出不确定性：

> Uncertainty-Aware Active Clarification for Reliable GUI Agents

### 1.3 课题的核心问题

传统的 GUI Agent 通常假设用户指令清晰、完整，并直接生成动作序列。但真实用户往往会说：

- “帮我把那个发给小王。”
- “订明天早上的票。”
- “把刚才那个文件打开。”
- “弄一个和上次差不多的会议。”
- “把这个删掉。”

这些指令通常不能直接执行。模型需要区分：

```text
可以安全执行
需要查询当前界面
需要利用历史上下文
需要向用户澄清
需要拒绝或请求确认
```

因此，该课题的重点不是单纯提高模型生成动作的能力，而是建立一种：

> 在不确定情况下知道自己还缺什么，并能够通过主动提问消除不确定性的能力。

---

## 2. 整体系统定义

建议将系统拆成以下模块：

```text
用户自然语言
    + 对话历史
    + 当前屏幕截图
    + DOM / Accessibility Tree
    + 当前应用状态
              ↓
        语义理解模块
              ↓
    意图、槽位、指代和风险分析
              ↓
        不确定性判断器
              ↓
       ┌──────┴──────┐
       ↓             ↓
  主动澄清       结构化任务计划
       ↓             ↓
 用户补充信息   GUI Grounding
                     ↓
             Computer Use 动作
                     ↓
                状态验证器
                     ↓
       成功 / 恢复 / 重新规划 / 再次询问
```

### 2.1 输入

模型输入可以包含：

- 用户当前指令；
- 多轮对话历史；
- 当前应用和窗口信息；
- 当前截图；
- Accessibility Tree；
- DOM 或网页结构；
- 可用工具列表；
- 已经执行的动作；
- 上一步动作后的环境观察结果；
- 用户权限和安全策略。

### 2.2 输出状态

模型至少应支持以下状态：

```text
ready              信息足够，可以执行
need_clarification 需要向用户询问
need_confirmation   高风险动作，需要用户确认
blocked             当前环境无法执行
completed           任务已经完成
failed              执行失败
recovering          正在尝试恢复
```

### 2.3 核心设计原则

1. **不确定时不强行猜测。**
2. **澄清问题必须针对真正缺失的信息。**
3. **一次尽可能询问多个相互独立的必填信息。**
4. **不要询问用户已经明确表达过的信息。**
5. **低风险且可以可靠推断的信息可以自动补全。**
6. **高风险动作即使置信度较高，也可以要求确认。**
7. **所有动作都应具有前置条件和预期结果。**
8. **动作完成后必须验证，而不是默认成功。**
9. **轨迹协议与具体坐标解耦。**
10. **语义模型负责决定做什么，GUI Grounding 模型负责决定屏幕上的哪个元素。**

---

## 3. 主动澄清任务的形式化定义

设用户输入为 \(u\)，对话历史为 \(h\)，环境状态为 \(s\)，任务目标为 \(g\)，模型对任务的候选解释为：

\[
P(g, z \mid u, h, s)
\]

其中 \(z\) 表示任务所需的槽位、参数、指代和约束。

当模型无法达到执行阈值时，不应直接产生动作，而应选择澄清问题 \(q\)：

\[
q^* = \arg\max_q \left[\text{InformationGain}(q) - \lambda \text{UserCost}(q)\right]
\]

当澄清后任务的执行置信度达到阈值 \(\tau\) 时，才进入执行阶段：

\[
\max_{g,z} P(g,z \mid u,h,s) \geq \tau
\]

这里的阈值不应固定不变，可以根据风险等级调整：

- 普通搜索：较低阈值；
- 文件移动：中等阈值；
- 删除文件、发送邮件、支付或提交表单：高阈值；
- 涉及不可逆或高风险操作：必须确认。

### 3.1 什么时候应该询问

以下情况应该主动询问：

- 必填槽位缺失；
- 关键指代无法解析；
- 存在两个以上可能目标；
- 当前界面无法确定用户所说对象；
- 用户请求与当前环境状态矛盾；
- 任务具有高风险或不可逆后果；
- 不同解释会导致不同的执行轨迹；
- 模型无法证明操作完成。

### 3.2 什么时候不应该询问

以下情况不应过度询问：

- 信息可以从当前页面可靠获取；
- 用户已经在历史对话中明确说明；
- 不同解释对结果没有实质影响；
- 任务是低风险、可撤销的操作；
- 模型只是不确定一个非关键细节，但可以在执行中观察确认。

目标不是让模型“永远询问”，而是让它做到：

> 该问时问，不该问时直接完成。

---

## 4. 结构化任务协议设计

建议使用 JSON Schema 或 Pydantic 定义统一的中间表示。模型不要直接输出无法解析的自由文本，也不要一开始就输出裸坐标。

### 4.1 需要澄清时的输出示例

```json
{
  "status": "need_clarification",
  "intent": "send_file",
  "confidence": 0.42,
  "slots": {
    "file": null,
    "recipient": null,
    "message": null
  },
  "missing_information": [
    "file",
    "recipient"
  ],
  "ambiguous_references": [
    {
      "phrase": "那个",
      "candidates": [
        "报告.pdf",
        "会议纪要.docx"
      ]
    },
    {
      "phrase": "小王",
      "candidates": [
        "王小明",
        "王丽"
      ]
    }
  ],
  "clarification_questions": [
    "你要发送哪个文件：报告.pdf 还是 会议纪要.docx？",
    "收件人是王小明还是王丽？"
  ],
  "risk": "medium"
}
```

### 4.2 信息充分时的输出示例

```json
{
  "status": "ready",
  "intent": "send_file",
  "confidence": 0.96,
  "slots": {
    "file": "报告.pdf",
    "recipient": "王小明",
    "message": "请查收"
  },
  "plan": [
    {
      "step_id": 1,
      "action": "open_app",
      "parameters": {
        "app": "file_manager"
      },
      "precondition": "file_manager_available",
      "expected_observation": "file_manager_opened"
    },
    {
      "step_id": 2,
      "action": "select",
      "target": {
        "semantic_role": "file",
        "name": "报告.pdf"
      },
      "precondition": "target_file_visible",
      "expected_observation": "file_selected"
    },
    {
      "step_id": 3,
      "action": "share",
      "target": {
        "semantic_role": "share_button"
      },
      "expected_observation": "share_dialog_opened"
    },
    {
      "step_id": 4,
      "action": "select",
      "target": {
        "semantic_role": "contact",
        "name": "王小明"
      },
      "expected_observation": "recipient_selected"
    },
    {
      "step_id": 5,
      "action": "type",
      "target": {
        "semantic_role": "message_box"
      },
      "parameters": {
        "text": "请查收"
      }
    },
    {
      "step_id": 6,
      "action": "send",
      "requires_confirmation": true,
      "expected_observation": "message_sent"
    }
  ],
  "verification": {
    "required": true,
    "success_condition": "message_sent"
  },
  "risk": "medium"
}
```

### 4.3 轨迹协议的推荐字段

- `status`：当前任务状态；
- `intent`：标准化意图；
- `confidence`：整体执行置信度；
- `slots`：任务参数；
- `missing_information`：缺失信息；
- `ambiguous_references`：歧义指代；
- `assumptions`：模型做出的假设；
- `clarification_questions`：向用户提出的问题；
- `plan`：高层结构化执行计划；
- `action`：动作类型；
- `target`：语义目标，不优先使用坐标；
- `parameters`：动作参数；
- `precondition`：动作前提；
- `expected_observation`：预期观察结果；
- `requires_confirmation`：是否需要用户确认；
- `risk`：风险等级；
- `rollback`：失败或撤销方案；
- `verification`：完成条件。

---

## 5. 相关论文、数据集和开源项目

### 5.1 Mind2Web

论文：**Mind2Web: Towards a Generalist Agent for the Web**

- 论文：https://arxiv.org/abs/2306.06070
- 项目：https://osu-nlp-group.github.io/Mind2Web/
- 代码：https://github.com/OSU-NLP-Group/Mind2Web
- 多模态数据：https://huggingface.co/datasets/osunlp/Multimodal-Mind2Web

主要内容：

- 真实网页上的自然语言任务；
- HTML、DOM、截图和操作轨迹；
- Click、Hover、Type、Select 等动作；
- 跨任务、跨网站和跨领域泛化。

适合用于：网页任务理解、元素选择、操作轨迹生成和网页 Agent 预训练。

局限：原始指令通常相对明确，对残缺指令、歧义指令和主动澄清关注不够。

### 5.2 OSWorld

论文：**OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments**

- 论文：https://arxiv.org/abs/2404.07972
- 代码：https://github.com/xlang-ai/OSWorld
- 项目主页：http://osworld-v1.xlang.ai/

主要内容：

- 浏览器和桌面应用；
- 文件系统操作；
- 多应用协作；
- 鼠标、键盘、滚动、拖拽和快捷键；
- 真实计算机环境中的任务完成评测；
- 通过环境最终状态判断任务是否完成。

适合用于：端到端 Computer Use 训练、执行验证、失败恢复和 RL 环境。

### 5.3 WebArena

论文：**WebArena: A Realistic Web Environment for Building Autonomous Agents**

- 项目主页：https://webarena.dev/
- 代码：https://github.com/web-arena-x/webarena

主要内容：

- 真实感网页环境；
- 信息检索和网页导航；
- 表单填写；
- 长程多步骤任务；
- 多网站交互。

适合用于：网页 Agent、长期规划、上下文理解和执行状态评估。

### 5.4 SeeClick

论文：**SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents**

- 论文：https://aclanthology.org/2024.acl-long.505/
- 代码：https://github.com/njucckevin/SeeClick

主要内容：

- 基于 Qwen-VL 的 GUI 视觉定位；
- 自然语言指令和屏幕截图输入；
- 输出目标元素的点击点或边界框；
- ScreenSpot 基准覆盖移动端、桌面端和网页端。

适合用于：从语义目标到屏幕元素的 grounding。

### 5.5 GUI-Actor

论文：**GUI-Actor: Coordinate-Free Visual Grounding for GUI Agents**

- 论文：https://arxiv.org/abs/2506.03143
- 代码：https://github.com/microsoft/GUI-Actor

主要内容：

- 坐标无关的视觉 GUI 定位；
- 通过视觉模型定位目标区域；
- 可以生成多个候选区域；
- 可以结合 verifier 对候选区域进行筛选。

适合用于：将语义计划中的目标映射为当前屏幕上的具体 GUI 元素。

### 5.6 AgentBench

论文：**AgentBench: Evaluating LLMs as Agents**

- 论文：https://arxiv.org/abs/2308.03688
- 代码：https://github.com/THUDM/AgentBench

包含：

- 操作系统任务；
- 数据库任务；
- 知识图谱任务；
- 网页浏览和购物；
- 工具使用和函数调用任务。

适合用于：参考通用 Agent 的任务设计、环境交互和评测方法。

### 5.7 ReAct

论文：**ReAct: Synergizing Reasoning and Acting in Language Models**

- 论文：https://arxiv.org/abs/2210.03629

核心循环：

```text
Reasoning → Action → Observation → Reasoning → Action
```

适合参考规划、执行和观察的循环机制。但生产环境中不建议将自由形式的推理文本直接作为执行协议，应使用单独的结构化字段。

### 5.8 Toolformer、API-Bank、ToolBench

这些工作关注：

- 选择什么工具；
- 什么时候调用工具；
- 如何抽取工具参数；
- 如何利用工具返回结果。

可迁移到 GUI 工具调用，例如：

```json
{
  "tool": "click",
  "target": {
    "semantic_role": "settings_button"
  }
}
```

### 5.9 Outlines

项目：https://github.com/dottxt-ai/outlines

Outlines 支持：

- JSON Schema；
- Pydantic；
- 枚举；
- 正则表达式；
- Grammar constrained decoding；
- 函数参数结构化生成。

适合用于保证轨迹输出符合固定协议。需要注意：结构化约束只能保证格式正确，不能保证任务理解正确，语义正确仍然需要训练数据、验证器和执行环境反馈。

### 5.10 Qwen-Agent

项目：https://github.com/QwenLM/Qwen-Agent

可以参考其：

- 工具调用；
- Function Calling；
- 代码解释器；
- Agent 工作流；
- 结构化输出。

---

## 6. 数据集设计

现有 Mind2Web、OSWorld 和 WebArena 可以提供基础任务与执行轨迹，但如果要研究“主动澄清直到有把握”，还需要构造新的不确定性数据。

### 6.1 指令类型

建议构造以下类型：

1. **信息完整**
   - “打开浏览器，搜索北京到上海的高铁票。”
2. **缺少必填参数**
   - “帮我订一张票。”
3. **存在歧义指代**
   - “把那个文件发给小王。”
4. **时间表达模糊**
   - “订明天早上的票。”
5. **依赖历史上下文**
   - “按照上次的设置再来一次。”
6. **多个候选目标**
   - 当前页面存在多个同名按钮或文件。
7. **界面状态不一致**
   - 用户要求点击设置，但当前窗口没有设置入口。
8. **高风险操作**
   - 删除、发送、支付、提交、发布。
9. **错误前提**
   - 用户要求打开一个当前不存在的文件。
10. **不合理或不可执行任务**
   - 当前权限不足或应用不支持该操作。

### 6.2 每个样本建议包含

```text
用户原始指令
对话历史
当前界面状态
环境可见元素
标准意图
槽位标注
缺失槽位
歧义候选
风险等级
正确澄清问题
是否需要确认
标准执行计划
动作前置条件
预期观察结果
失败恢复方案
最终任务状态
```

### 6.3 对话轨迹样本

一个完整样本可以是：

```text
用户：帮我把那个发给小王。

模型：你要发送哪个文件？当前有“报告.pdf”和“会议纪要.docx”。另外，收件人是王小明还是王丽？

用户：发报告给王小明。

模型：已确认文件为“报告.pdf”，收件人为“王小明”。我将打开分享窗口并准备发送，发送前需要你确认。

用户：确认。

模型：执行发送并验证发送成功。
```

注意：训练数据中应该包含错误的模型回答作为负样本，例如：

```text
直接选择第一个文件并发送给第一个小王。
```

这类样本应被标记为错误，因为模型在不确定时进行了无依据猜测。

---

## 7. Qwen 的训练路线

### 7.1 阶段一：SFT

第一阶段训练模型学会统一协议和基本行为。

训练样本应覆盖：

- 完整指令到结构化计划；
- 缺失信息到澄清问题；
- 模糊指令到候选解释；
- 指代不明到主动确认；
- 高风险任务到二次确认；
- 当前页面不匹配到停止执行；
- 动作失败到恢复或重新规划；
- 任务完成到状态验证。

训练输入：

```text
用户指令
+ 对话历史
+ 当前 UI 状态
+ 可用工具
+ 已执行动作
+ 最新环境观察
```

训练输出：

```text
结构化意图
+ 置信度
+ 槽位
+ 缺失信息
+ 澄清问题或执行计划
+ 验证条件
```

建议优先使用 LoRA / QLoRA 完成第一版验证，再考虑全参数微调。

### 7.2 阶段二：偏好优化

构造成对样本：

#### 正确澄清 vs 强行猜测

```text
A：检测到两个同名文件，询问用户选择。
B：默认选择第一个文件并发送。
```

偏好 A。

#### 必要澄清 vs 过度澄清

```text
A：当前页面可以唯一确定目标，直接执行。
B：再次询问用户已经明确说明的信息。
```

偏好 A。

#### 高质量计划 vs 无验证轨迹

```text
A：每一步包含目标、前置条件和预期观察。
B：只输出 click、type 等动作，没有验证条件。
```

偏好 A。

可以考虑：

- DPO；
- ORPO；
- SimPO；
- KTO；
- 基于规则和环境结果生成偏好数据。

### 7.3 阶段三：环境交互和 RL

让模型在网页或桌面环境中真实执行任务，根据环境结果提供奖励。

奖励可以定义为：

\[
R = R_{task} + \lambda_1 R_{clarify} + \lambda_2 R_{format} + \lambda_3 R_{grounding} + \lambda_4 R_{verify} - \lambda_5 R_{wrong} - \lambda_6 R_{unsafe} - \lambda_7 R_{cost}
\]

其中：

- \(R_{task}\)：最终任务成功；
- \(R_{clarify}\)：澄清是否必要且有效；
- \(R_{format}\)：输出协议是否合法；
- \(R_{grounding}\)：是否定位到正确 GUI 元素；
- \(R_{verify}\)：是否正确验证结果；
- \(R_{wrong}\)：错误动作惩罚；
- \(R_{unsafe}\)：高风险误操作惩罚；
- \(R_{cost}\)：动作次数、时间和用户交互成本。

最重要的是避免奖励模型鼓励以下行为：

- 永远询问用户；
- 永远不询问用户；
- 为了得到成功率而绕过用户确认；
- 为了格式正确而输出虚假的高置信度。

---

## 8. 评测指标

### 8.1 语义理解

- Intent Accuracy；
- Slot F1；
- Missing Slot Recall；
- Ambiguity Detection Accuracy；
- Reference Resolution Accuracy；
- Risk Classification Accuracy。

### 8.2 主动澄清

- 必要澄清准确率；
- 不必要澄清率；
- 澄清问题有效率；
- 单任务平均澄清轮数；
- 澄清后执行成功率；
- 用户信息获取量；
- 澄清问题的最小性。

建议重点定义：

```text
Appropriate Clarification Rate
```

它同时考虑：

- 该澄清时是否澄清；
- 不该澄清时是否直接执行。

### 8.3 结构化输出

- JSON Valid Rate；
- Schema Valid Rate；
- Action Valid Rate；
- Tool Parameter Accuracy；
- 轨迹可执行率；
- 轨迹冗余率。

### 8.4 GUI Grounding

- Element Grounding Accuracy；
- Click Success Rate；
- ScreenSpot Accuracy；
- Target IoU；
- Coordinate Error；
- 多候选目标选择准确率。

### 8.5 端到端执行

- Task Success Rate；
- Step Success Rate；
- Average Action Count；
- Recovery Success Rate；
- Human Intervention Rate；
- Unsafe Action Rate；
- 任务完成时间；
- 用户满意度。

---

## 9. 推荐的系统技术栈

```text
Qwen2.5/3 或 Qwen-VL
        ↓
结构化意图和槽位解析
        ↓
JSON Schema / Pydantic / Outlines
        ↓
主动澄清和风险判断
        ↓
高层任务规划
        ↓
SeeClick / GUI-Actor / Qwen-VL
        ↓
GUI Grounding
        ↓
Playwright / pyautogui / OSWorld Interface
        ↓
鼠标键盘和应用操作
        ↓
截图 / DOM / Accessibility Tree / 应用状态
        ↓
状态验证器
        ↓
成功、恢复、重新规划或再次澄清
```

推荐的最小原型组合：

- 模型：Qwen2.5 或 Qwen3；
- 训练：Transformers + PEFT + TRL；
- 结构化输出：Pydantic + JSON Schema，必要时使用 Outlines；
- 网页执行：Playwright；
- 桌面环境：OSWorld；
- GUI 定位：SeeClick 或 GUI-Actor；
- 轨迹记录：JSONL；
- 评测：任务成功率、澄清准确率和错误动作率。

---

## 10. 推荐的研究实验设计

### 实验一：是否能够识别缺失信息

比较：

- 基础 Qwen；
- SFT 后的 Qwen；
- SFT + 不确定性数据；
- SFT + 偏好优化。

任务：给出完整、残缺和模糊指令，测试模型是否正确输出 `ready` 或 `need_clarification`。

### 实验二：澄清问题质量

评价：

- 是否询问了必要信息；
- 是否避免询问冗余信息；
- 用户回答后能否更新任务状态；
- 澄清轮数是否足够少。

### 实验三：结构化轨迹生成

比较：

- 自由文本轨迹；
- JSON 输出；
- JSON Schema constrained decoding；
- 带前置条件和预期观察的轨迹协议。

### 实验四：GUI Grounding

评价：

- 语义目标是否正确；
- 是否能定位当前界面元素；
- 多个同名控件时是否选择正确；
- 屏幕布局变化后是否仍然有效。

### 实验五：端到端执行

在 OSWorld、WebArena 或自建 Playwright 环境中比较：

- 直接执行；
- 先澄清再执行；
- 先澄清 + 执行验证；
- 先澄清 + 执行验证 + 失败恢复。

重点比较：

- 任务成功率；
- 错误动作率；
- 用户询问次数；
- 任务耗时；
- 高风险操作安全性。

---

## 11. 分阶段落地计划

### 第一阶段：纯文本主动澄清

先不接 GUI，仅研究：

```text
用户指令 → 意图、槽位、缺失信息、澄清问题
```

目标：验证 Qwen 能否判断何时应该问用户。

### 第二阶段：结构化计划生成

加入：

- 工具列表；
- 固定 JSON 协议；
- 高层动作计划；
- 前置条件和验证条件。

目标：验证输出是否可以被下游执行器解析。

### 第三阶段：网页 Computer Use

使用 Playwright 和网页任务：

- 搜索；
- 登录后的页面操作；
- 表单填写；
- 文件下载和上传；
- 多步骤网页任务。

目标：验证语义计划能否转化为成功的网页轨迹。

### 第四阶段：GUI Grounding

加入屏幕截图、DOM 和 Accessibility Tree，并接入 SeeClick 或 GUI-Actor。

目标：验证语义目标到具体屏幕元素的映射。

### 第五阶段：真实计算机环境

接入 OSWorld，测试：

- 跨应用任务；
- 文件系统任务；
- 桌面应用任务；
- 状态验证和失败恢复。

### 第六阶段：偏好优化与 RL

利用执行结果自动生成：

- 成功轨迹；
- 错误轨迹；
- 过度澄清轨迹；
- 不足澄清轨迹；
- 不安全轨迹。

逐步进行 DPO、在线优化和环境 RL。

---

## 12. 可能的创新点

### 创新点一：面向不确定性任务的主动澄清协议

现有 GUI Agent 多数重点是“如何执行”，而本课题重点研究：

> 在什么时候不能执行，以及如何用最少的问题把任务变成可执行状态。

### 创新点二：语义计划和具体 GUI 动作解耦

将：

```text
做什么
```

与：

```text
屏幕上点击哪里
```

分离，减少模型直接生成坐标造成的错误。

### 创新点三：带预期观察的可验证轨迹

每一个动作都包含：

- 前置条件；
- 动作目标；
- 预期结果；
- 失败恢复方案。

这比只有 `click`、`type` 的轨迹更适合真实计算机环境。

### 创新点四：面向主动澄清的专门数据集

构造包含：

- 残缺指令；
- 模糊指令；
- 多候选指代；
- 高风险任务；
- 环境不一致；
- 多轮澄清轨迹

的数据集，可作为论文和开源项目的核心贡献。

### 创新点五：澄清行为和执行行为的联合奖励

不要只奖励任务完成，还要奖励：

- 必要时澄清；
- 不必要时不澄清；
- 正确判断自身不确定性；
- 减少错误动作和安全风险。

---

## 13. 需要特别避免的问题

### 13.1 只追求 JSON 格式正确

JSON 合法不代表语义正确。必须结合环境状态和最终任务结果评测。

### 13.2 让一个模型负责所有事情

不建议初期让 Qwen 同时完成：

- 意图理解；
- 规划；
- 元素定位；
- 坐标预测；
- 鼠标键盘控制；
- 执行验证。

建议模块化，并逐步联合训练。

### 13.3 只使用成功轨迹

如果训练数据中没有“什么时候应该停下来询问”的负样本，模型很容易学会盲目执行。

### 13.4 把模型置信度当成真实概率

模型输出的 `confidence` 不能天然视为可靠概率，需要通过校准集进行：

- ECE；
- Brier Score；
- Reliability Diagram；
- 风险阈值分析。

### 13.5 用“永远询问”规避错误

如果模型在任何任务上都问用户，虽然错误动作会减少，但系统不可用。因此必须同时惩罚：

- 强行猜测；
- 无必要澄清。

### 13.6 忽视高风险操作

删除、支付、发送、发布、提交等操作应采用更高阈值，必要时加入显式确认。

---

## 14. 最终建议

建议把第一版研究目标收敛为：

> 给定自然语言指令、对话历史和当前 UI 状态，训练 Qwen 判断任务是否可执行；若不可执行，生成最小且有效的澄清问题；若可执行，则输出带置信度、前置条件、预期观察和验证条件的结构化 GUI 执行计划。

第一版不要直接从大规模 RL 开始，而应按以下顺序推进：

```text
主动澄清数据集
    ↓
Qwen SFT
    ↓
JSON Schema 结构化输出
    ↓
Playwright 小型网页环境
    ↓
执行结果验证
    ↓
偏好优化
    ↓
OSWorld / WebArena
    ↓
Computer Use RL
```

最值得优先实现的最小闭环是：

```text
用户输入
    ↓
判断是否缺信息
    ↓
需要时提问
    ↓
用户回答
    ↓
生成结构化计划
    ↓
执行一个低风险 GUI 动作
    ↓
观察结果并验证
```

只要这个闭环能够在一组可复现的模糊任务上稳定工作，就已经具备继续扩展到完整 GUI Agent 和 Computer Use 系统的基础。

---

# 15. 近两年文献筛选与研究空白

## 15.1 筛选范围和说明

本文将“最近两年”暂按 **2024 年 9 月至 2026 年 9 月**处理。2026 年论文中有相当一部分是 arXiv 预印本、技术报告或尚未正式发表的工作，正式写论文时需要再次核对版本、会议和实验结果。

文献筛选围绕两个核心问题：

```text
A. 用户指令不完整或模糊时，模型能否正确识别意图、缺失信息和不确定性，并主动询问？

B. 意图明确后，模型能否在真实 GUI / Computer Use 环境中可靠、可验证、安全地完成任务？
```

综合文献后的初步结论是：

> 近两年研究分别推进了“意图/任务状态表示”和“GUI 执行能力”，但将不确定性意图识别、主动澄清和 Computer Use 端到端结合起来的工作仍然很少。

这正是本课题可以切入的位置。

---

## 15.2 第一部分：意图识别、任务状态与主动澄清

### 15.2.1 AREAs-Lab：交互式需求澄清

论文：**AREAs-Lab: An Interactive Environment for AI-driven Requirement Elicitation for AI Systems**

- arXiv：https://arxiv.org/abs/2608.28979
- 发表信息：Findings of EMNLP 2026

#### 核心 idea

AREAs-Lab 将需求澄清建模为交互式需求获取过程：用户一开始只给出不完整需求，助手分析任务背景，然后通过有针对性的问题逐步揭示用户的隐含意图。

```text
不完整需求 → 识别缺失约束 → 提出澄清问题 → 用户补充 → 可执行需求
```

论文构造了公开数据集上的合成任务、不完整需求、用户模拟器和交互式评测。

#### 解决的问题

- 传统意图识别通常假设输入完整；
- 普通 LLM 容易直接猜测用户真实需求；
- 只评价最终回答，无法评价澄清过程；
- 人工测试主动澄清系统成本高。

#### 仍然存在的问题

1. 主要面向 AI 系统需求获取，不等价于 GUI 执行任务；
2. 依赖合成用户和合成需求，与真实用户表达仍有差距；
3. 关注需求是否被澄清清楚，不是澄清后能否在真实环境中成功执行；
4. 信息增益、用户负担和任务风险之间缺少统一决策模型；
5. 对错误指代、历史记忆冲突和环境状态变化研究不足。

#### 对本课题的启发

借鉴“完整目标—不完整目标—模拟用户—交互评测”的数据构造方式，但将最终目标改为：

```text
用户目标 → 可执行 GUI 计划 → 环境执行成功
```

---

### 15.2.2 SAGE：带状态约束和拒答能力的任务型对话评测

论文：**SAGE: State-Grounded, Abstention-Aware Evaluation of Task-Oriented Dialogue Agents**

- arXiv：https://arxiv.org/abs/2609.00434

#### 核心 idea

SAGE 将每轮对话转换成相对于工作流状态的原子化检查项，并在证据不足时允许评测器拒答，而不是强行评分：

```text
当前状态 → 本轮回复应改变的状态 → 逐项验证 → 证据不足则拒答
```

#### 解决的问题

- LLM-as-a-judge 容易只评价回复是否流畅；
- 流畅回复可能没有推进任务状态；
- 整体评分难以定位具体槽位或步骤错误；
- 评测器在证据不足时也会强行判断。

#### 仍然存在的问题

1. 主要是评测框架，不是主动澄清策略；
2. 对开放域 GUI 状态、截图和 Accessibility Tree 覆盖不足；
3. 工作流规范需要提前定义，难以覆盖开放任务；
4. 用户真实目标是否满足仍难自动判断；
5. 多轮澄清的最优问题选择没有完整解决。

#### 对本课题的启发

将其状态差分思想用于训练和评测：

```text
澄清前状态 → 澄清问题 → 用户回答 → 新状态
```

评价模型是否真的消除了一个关键歧义，而不是只生成语言上合理的问题。

---

### 15.2.3 Hear2Act：从语音中的隐含意图到下一步行动

论文：**Hear2Act: Benchmarking When Prosody Should Change What an Assistant Does**

- arXiv：https://arxiv.org/abs/2608.19515

#### 核心 idea

Hear2Act 研究同样文字在不同语气、停顿和韵律下可能表达不同隐含担忧，而这些信息应该改变助手的下一步行动。

```text
相同文字 + 不同韵律 → 不同用户状态 → 不同最优行动
```

显式加入中间状态表示后，行动选择明显改善。

#### 解决的问题

- 只看文字会丢失语气中的任务相关信息；
- 意图识别和行动决策之间存在表示断裂；
- 模型可能识别出用户担忧，却没有改变后续行动。

#### 仍然存在的问题

1. 重点是语音韵律，不是残缺文本和 GUI 状态；
2. 场景数量有限，尚未覆盖复杂 Computer Use 工作流；
3. 用户隐含状态标注成本较高；
4. 尚未系统研究不确定性阈值和主动澄清；
5. 多模态不确定性融合后的责任边界仍不清晰。

#### 对本课题的启发

模型内部应显式维护中间状态，而不是从原始话语直接生成动作：

```json
{
  "user_goal": "send_file",
  "missing_slots": ["file", "recipient"],
  "next_action": "ask_clarification"
}
```

---

### 15.2.4 Learning to Reason and Use Tools through Unsupervised Fine-Tuning

论文：**Learning to Reason and Use Tools through Unsupervised Fine-Tuning in Task-Oriented Dialog Systems**

- arXiv：https://arxiv.org/abs/2608.30426

#### 核心 idea

该工作将 ReAct 式推理和工具使用引入任务型对话，通过模型生成轨迹、自动质量筛选和迭代式自训练构造训练数据。

```text
生成推理和工具轨迹 → 自动筛选 → 无监督微调 → 继续生成更好的轨迹
```

#### 解决的问题

- 任务型对话需要外部知识和工具；
- 人工标注完整推理—工具调用轨迹成本高；
- 只训练最终回复不足以学习查询和行动。

#### 仍然存在的问题

1. 工具轨迹质量依赖自动评判器，错误可能被自训练放大；
2. 主要在任务型对话上验证，与视觉 GUI 环境有距离；
3. 对什么时候不应调用工具、什么时候应询问用户讨论不足；
4. 多候选解释之间的风险决策没有解决；
5. 自然语言推理过程不等同于真实可校准的不确定性。

#### 对本课题的启发

可以用于构造 Qwen 的工具调用和主动澄清轨迹，但筛选器必须同时检查工具参数、缺失澄清、无依据假设和最终环境状态。

---

### 15.2.5 多意图和显式任务状态表示

近两年工作还出现共同趋势：不再把复杂请求当成一个整体意图，而是拆分成多个意图、类型化任务和依赖关系。例如：

- **A Task-Oriented Multi-Agent Framework for Complex Wearable Health Analysis**（2026）：将复合请求拆为多个意图和有依赖关系的类型化任务；
- **SAGE**：将对话动作映射为工作流状态差分；
- **Hear2Act**：用显式中间状态承接隐含用户担忧。

共同抽象为：

```text
原始自然语言 → 多个意图 / 槽位 / 约束 → 依赖关系和任务状态 → 工具或下一步行动
```

#### 解决的问题

- 复杂请求容易遗漏子任务；
- 单一整体意图无法表示不同子任务的证据；
- 多意图之间的顺序和依赖关系容易丢失。

#### 仍然存在的问题

- 多意图拆分不等于知道何时需要澄清；
- 子任务之间可能共享实体和上下文；
- 一个子任务的歧义可能阻塞整个任务，也可能只影响局部；
- 尚未形成面向 GUI 执行的统一中间表示；
- 任务状态和屏幕状态之间的对齐仍是难点。

#### 适合转化为你的研究问题

> 对于包含多个子意图的 GUI 请求，模型能否只询问阻塞执行的最小信息，而不是重新询问整个任务？

---

### 15.2.6 意图识别方向的综合判断

| 研究趋势 | 代表性 idea | 已解决的问题 | 仍未解决的问题 |
|---|---|---|---|
| 需求澄清 | 交互式逐步获取隐藏需求 | 不完整需求可以通过多轮问答补全 | 与真实工具执行、GUI 状态结合不足 |
| 状态感知对话 | 用状态差分评价每轮回复 | 能发现“语言合理但没有推进任务” | 复杂视觉状态和开放任务难表示 |
| 隐含意图 | 将语气或中间状态用于行动选择 | 证明隐含状态需要传给决策模块 | 多模态不确定性和澄清策略不足 |
| 多意图拆分 | 将复合请求拆为类型化任务 | 减少任务遗漏并表达依赖关系 | 子任务歧义的局部澄清仍缺方法 |
| 工具增强对话 | ReAct 和自训练工具轨迹 | 提升外部知识查询和工具调用 | 自动生成轨迹存在错误传播和幻觉 |
| 自动评测 | 符号规则、NLI 和 LLM 级联验证 | 降低只靠 LLM judge 的风险 | 用户目标和任务安全仍难评估 |

### 15.2.7 意图识别方向最值得做的空白

#### 空白 A：主动澄清的执行闭环不足

现有研究通常评价意图准确率、槽位 F1 和对话质量，但很少评价澄清后是否真正完成 Computer Use 任务。

#### 空白 B：缺少环境感知的不确定性定义

自然语言可能明确，但当前屏幕存在两个目标；也可能指令模糊，但当前页面只有一个可行目标。因此不确定性应为：

\[
U = f(\text{语言歧义}, \text{候选目标数}, \text{环境状态}, \text{风险}, \text{任务后果})
\]

而不是只由语言模型 token 概率决定。

#### 空白 C：澄清成本没有和风险统一建模

搜索网页和发送邮件不应使用同一个置信度阈值。

#### 空白 D：澄清问题的“最小性”缺乏标准

好的模型不应问“请重新完整描述需求”，而应问“当前有两个文件，应该发送哪一个？”

#### 空白 E：意图状态和 GUI 状态之间缺少统一协议

当前意图识别、槽位填充、GUI grounding、动作执行通常分开评测，缺少统一的：

```text
意图 → 缺失信息 → 澄清 → 目标元素 → 动作 → 验证
```

协议和基准。

---

## 15.3 第二部分：Computer Use / GUI Agent

### 15.3.1 OSWorld 2.0：长程、真实世界 Computer Use

论文：**OSWorld 2.0: Benchmarking Computer Use Agents on Long-Horizon Real-World Tasks**

- arXiv：https://arxiv.org/abs/2606.29537
- 项目：https://os-world.github.io/

#### 核心 idea

OSWorld 2.0 将评测从短任务扩展到更接近真实工作的端到端流程：任务可能需要数百次工具调用，涉及跨来源信息整合、隐式状态推断、动态网页、流式交互和视觉空间精度，并提供安全报告。

#### 解决的问题

- 传统短任务和单步 grounding 过于乐观；
- 最终结果之外的长程约束容易被忽略；
- Agent 在简单操作上看似成功，但无法完成真实办公工作流。

#### 仍然存在的问题

1. 执行成本高，难以大规模用于 RL；
2. 失败原因仍需要复杂人工或 LLM 分析；
3. 任务覆盖不可能代表全部真实软件；
4. 对“何时询问用户”没有专门的澄清标注；
5. 最终成功率不能完整描述中间状态是否安全。

#### 对本课题的启发

需要评测长程上下文保持、中途新信息处理、隐式状态恢复、是否猜测而不是提问，以及是否进行最终验证。

---

### 15.3.2 OSWorld-Pro：过程级 Computer Use 评测

论文：**OSWorld-Pro: Process-based Evaluation for Computer Use Agents**

- arXiv：https://arxiv.org/abs/2609.24890

#### 核心 idea

OSWorld-Pro 将长任务拆成有顺序依赖的子目标，通过人工标注和 LLM judge 评估每个子目标是否完成，而不仅仅看最终结果。

```text
长任务 → 依赖子目标 → 逐步判断进度、错误类型和无关动作
```

#### 解决的问题

- 终态评测无法说明在哪一步失败；
- 相同最终失败可能来自输入、定位、规划或验证错误；
- 过程分解有利于训练数据生成。

#### 仍然存在的问题

1. 过程评分依赖标注和评判器质量；
2. 过程完成不一定代表最终产物正确；
3. 对用户意图是否正确理解覆盖不足；
4. 没有把“应该主动询问”作为核心过程事件；
5. 子目标划分本身可能带来评测偏差。

#### 对本课题的启发

应把主动澄清作为合法且必要的过程动作：

```text
ask_clarification → receive_answer → update_state
```

不能把所有非 GUI 动作都当作浪费。

---

### 15.3.3 KNOWS：从搜索到知识组织和可交付产物

论文：**The Hard Part Comes After Search: Benchmarking Web Agents on Synthesizing, Organizing, and Displaying Knowledge**

- arXiv：https://arxiv.org/abs/2609.30604
- 项目：https://alexgill321.github.io/KNOWS-benchmark/

#### 核心 idea

KNOWS 不只要求搜索信息，还要求 Agent 从多个来源获取、综合和组织知识，并在网页软件中制作文档、演示文稿或表格，生成可交付 artifact。

#### 解决的问题

- 传统网页 Agent 常只需找到一个答案；
- 真实办公任务需要检索、推理、组织、排版和 GUI 操作；
- 局部步骤完成不代表最终产物可用。

#### 仍然存在的问题

- 复杂任务最终成功率仍低；
- 视觉错误可能使整个产物不可用；
- 长程任务中状态和约束容易丢失；
- 未专门研究不完整指令下的交互澄清；
- LLM 评估最终 artifact 仍有主观性。

#### 对本课题的启发

“直到有把握再执行”应同时要求目标、输入材料、产物格式、工具可用性、风险和验证条件明确。

---

### 15.3.4 Jev-Mobile：高层 VLM 规划和低层轻量执行解耦

论文：**Jev-Mobile: Jev as an Executor for Mobile GUI Agents**

- arXiv：https://arxiv.org/abs/2609.30186

#### 核心 idea

Jev-Mobile 不让昂贵 VLM 每一步都重新规划，而是由 VLM 低频生成局部目标，再让轻量模型基于 Accessibility Tree 高频选择具体动作。

```text
VLM 生成局部目标 → Accessibility Tree 提供动作空间 → 轻量模型选择动作
```

#### 解决的问题

- 每一步都调用大型 VLM，延迟和成本高；
- 低层重复动作不需要完整推理；
- 视觉规划与结构化执行混合导致效率低。

#### 仍然存在的问题

1. 高层局部目标错误会被低层持续放大；
2. Accessibility Tree 不一定完整或可靠；
3. 对截图中的非结构化视觉元素支持有限；
4. 何时重新请求 VLM 规划仍是关键问题；
5. 没有直接解决用户指令歧义。

#### 对本课题的启发

主动澄清应放在低频高层决策阶段，避免低层执行器擅自解释模糊指令。

---

### 15.3.5 GUI-SD-v2：从自蒸馏到多轮 GUI 交互

论文：**Learn How to Act from Your Own Interactions: On-Policy Self-Distillation for GUI Agents**

- arXiv：https://arxiv.org/abs/2609.27307

#### 核心 idea

GUI-SD-v2 将 on-policy self-distillation 从单步 GUI grounding 扩展到多轮 GUI 交互，选择性蒸馏当前推理、动作决策和对后续任务有用的记忆。

#### 解决的问题

- 单步 grounding 训练不能覆盖多轮任务；
- GUI Agent 需要保存任务相关记忆；
- 普通自蒸馏教师不一定正确使用特权信息。

#### 仍然存在的问题

1. 特权教师信息在部署时不可用；
2. 记忆蒸馏不等于知道哪些信息应向用户确认；
3. 主要关注动作成功率，未系统评价澄清和拒绝；
4. 依赖高质量 rollout 和教师模型；
5. 长程错误恢复和风险控制未完全解决。

#### 对本课题的启发

可把“正确澄清轨迹”作为特权教师信号，训练模型学习哪些字段必需、哪些候选存在歧义、什么时候不能继续动作。

---

### 15.3.6 GUI-Actor 与 SeeClick：GUI grounding 的坐标和候选目标

相关论文：

- **SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents**（ACL 2024）
  - https://aclanthology.org/2024.acl-long.505/
- **GUI-Actor: Coordinate-Free Visual Grounding for GUI Agents**（2025）
  - https://arxiv.org/abs/2506.03143

#### 核心 idea

```text
自然语言目标 + 截图 → 屏幕目标元素 / 点击位置 / 候选区域
```

GUI-Actor 进一步减少对文本坐标生成的依赖，使用视觉 grounding 和候选区域验证。

#### 解决的问题

- 模型理解“点击设置”，但不知道设置按钮在哪里；
- 坐标文本对分辨率和布局敏感；
- 小元素、相似元素和复杂布局容易定位失败。

#### 仍然存在的问题

1. grounding 正确不代表任务意图正确；
2. 多个合理候选仍需要上游澄清或状态推理；
3. 动态内容、遮挡、动画和非标准控件仍不稳定；
4. grounding 置信度和端到端成功率不总是一致；
5. 许多基准仍为单步或短任务。

#### 对本课题的启发

主动澄清还应发生在 GUI grounding 阶段：

```text
语言目标 → 两个屏幕候选 → 判断存在歧义 → 向用户询问具体候选
```

---

### 15.3.7 Argus：Computer Use 的不确定性量化

论文：**Uncertainty Quantification for Computer-Use Agents: A Benchmark across Vision-Language Models and GUI Grounding Datasets**

- arXiv：https://arxiv.org/abs/2606.25760

#### 核心 idea

Argus 比较 logit、采样一致性、hidden state、attention、密度估计、verbalized confidence 和 conformal prediction 等 GUI grounding 不确定性方法。

主要启发是：不确定性排序在同一个模型的不同数据集之间可能较稳定，但跨模型、跨接口时会明显退化。

#### 解决的问题

- GUI Agent 需要知道点击是否可靠；
- 置信度可以用于拒绝、重试和安全区域；
- 不能只依赖模型口头输出的 confidence。

#### 仍然存在的问题

1. 主要是单步 grounding，不是完整任务级不确定性；
2. 不确定性不能直接说明应该问用户什么；
3. 校准结果依赖模型和界面；
4. 多步误差累积和任务风险尚未统一；
5. 置信度高但语义目标错误的情况仍存在。

#### 对本课题的启发

至少区分三种置信度：

```text
语言意图置信度：理解用户想做什么吗？
目标定位置信度：知道屏幕上哪个元素吗？
执行结果置信度：确认动作真的成功了吗？
```

---

### 15.3.8 ComponentBench、GUI-Primitives 和 Desktop-Delta Bench：诊断中间能力

相关工作：

- **ComponentBench: Diagnosing Component-Level Failures in Computer-Use Agents**
  - https://arxiv.org/abs/2608.18307
- **GUI-Primitives: Diagnosing Spatial Reasoning Failures in Vision-Language GUI Grounding**
  - https://arxiv.org/abs/2608.21832
- **Desktop-Delta Bench: Do Computer-Use Models Understand Desktop GUI Transitions?**
  - https://arxiv.org/abs/2607.26041

#### 共同 idea

将复杂 Computer Use 拆成可诊断的中间能力：

```text
组件交互、空间关系理解、前后状态变化、动作类型识别、状态验证、上下文控制
```

#### 解决的问题

- 端到端失败无法解释；
- 相同任务成功率可能掩盖不同能力结构；
- 需要知道模型是不会看、不会选、不会操作，还是不会验证。

#### 仍然存在的问题

- 中间基准与真实长程任务仍有差距；
- 单项能力提升不一定带来整体成功率提升；
- 多个中间错误之间存在相互作用；
- 主动澄清尚未被作为基础能力系统诊断。

#### 对本课题的启发

增加新的中间层基准：

```text
Ambiguous Instruction → Ask / Act / Confirm / Refuse
```

---

### 15.3.9 ScaleCUA、ENVS 和自主评测：用可验证环境训练 Computer Use

相关工作：

- **SCALECUA: Scaling Computer Use Agents with Verifiable Task Synthesis and Efficient Online RL**
  - https://arxiv.org/abs/2607.11185
- **ENVS: Environment-Native Verified Search for Long-Horizon GUI Agents**
  - https://arxiv.org/abs/2606.22948
- **Reinforcement Learning for Computer-Use Agents with Autonomous Evaluation**
  - https://arxiv.org/abs/2606.24515

#### 共同 idea

```text
任务自动生成 → 环境 rollout → 程序验证 / VLM 评估 / 分支搜索 → 成功和失败轨迹 → SFT 或 RL
```

#### 解决的问题

- 高质量 GUI 轨迹稀缺；
- 桌面环境奖励难以手工定义；
- 在线 RL 成本高；
- 静态演示难以学习失败恢复。

#### 仍然存在的问题

1. 自动评判器错误会污染奖励；
2. 任务合成可能产生模板化或不真实任务；
3. 只优化最终成功率可能鼓励绕过澄清和安全确认；
4. GUI 环境与真实应用有分布差异；
5. 主动询问用户的奖励难以由环境自动给出。

#### 对本课题的启发

RL 动作空间应显式包含：

```text
完成任务、向用户澄清、安全拒绝 / 请求确认
```

“向用户澄清”不能简单视为任务未完成，应根据它是否减少真实不确定性来奖励。

---

### 15.3.10 StateAct、混合 GUI+CLI 和工具路由

相关工作：

- **StateAct: Program State, before Pixels, for Long-Horizon Computer-Use Agents**
  - https://arxiv.org/abs/2607.22798
- **Screenshots or Tools? Eliciting Tool Use and Managing Multimodal Context in Hybrid GUI-MCP Computer-Use Agents**
  - https://arxiv.org/abs/2608.03327
- **CUA-Universe: A Scalable and Dynamic Environment for Hybrid GUI+CLI Agents**
  - https://arxiv.org/abs/2609.05374

#### 共同 idea

真实计算机任务不应强制所有操作都通过截图和鼠标完成，Agent 需要在截图、Accessibility Tree、DOM、CLI、API/MCP 和程序状态之间路由。

#### 解决的问题

- 纯截图会丢失文件、DOM 和应用后端真实状态；
- 全部使用 GUI 操作成本高、轨迹长；
- 有工具不代表模型会选择工具；
- 视觉交互和程序化操作各有适用场景。

#### 仍然存在的问题

1. 程序状态不一定可访问；
2. API / CLI 工具可能具有更高权限和更大安全风险；
3. 工具选择错误本身也是意图理解失败；
4. GUI、CLI、API 结果之间的状态一致性仍需验证；
5. 用户可能明确要求在界面中操作，不能简单绕过 GUI。

#### 对本课题的启发

主动澄清有时不仅询问“做什么”，也询问“如何做”，但只有在工具选择会影响用户目标、记录或风险时才询问。

---

### 15.3.11 技能、记忆和轨迹复用

相关工作：

- **Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents**
  - https://arxiv.org/abs/2609.17653
  - https://github.com/ZJU-REAL/EvoSkill-GUI
- **EchoPath: Execution-Level Replayable Memory for GUI Agents**
  - https://arxiv.org/abs/2609.16635
- **VISUALSKILL: Multimodal Skills for Computer-Use Agents**
  - https://arxiv.org/abs/2606.18448

#### 共同 idea

将成功 GUI 轨迹提炼为带适用条件、视觉证据、参数、失败案例和验证条件的可复用技能或记忆。

#### 解决的问题

- 每次从零规划效率低；
- 原始轨迹过长、噪声大；
- 经验不能复用会提高在线学习成本；
- 复杂 GUI 操作需要程序性知识和视觉证据。

#### 仍然存在的问题

1. 相似任务不代表当前状态可安全复用；
2. 旧技能可能携带过时的界面假设；
3. 技能检索错误会导致连续错误动作；
4. 记忆系统需要不确定性和冲突管理；
5. 复用技能前是否应该确认尚无统一原则。

#### 对本课题的启发

可把澄清结果纳入技能记忆，例如用户偏好、联系人映射和高风险确认策略，发展长期个性化意图消歧。

---

### 15.3.12 CAVEAT、ERPBench 和安全方向

相关工作：

- **CAVEAT: Towards Robust Computer-Use Agents in Incentive-Misaligned Environments**
  - https://arxiv.org/abs/2609.27273
- **ERPBench: A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software**
  - https://arxiv.org/abs/2609.17885
- **MobileWorldSafety: Benchmarking GUI Agent Safety Against Environmental Injection Attacks in Android Apps**
  - https://arxiv.org/abs/2608.17659

#### 共同 idea

将 Computer Use 从“能否完成”扩展为：

```text
是否保持用户目标
是否被环境诱导
是否修改了正确的持久化状态
是否在攻击内容下仍然安全
```

#### 解决的问题

- Agent 可能被网页推荐、默认选项或界面话术诱导；
- 界面显示成功不代表数据库状态正确；
- 截图中的恶意文本可能改变模型行为；
- 最终任务成功不代表用户利益和安全得到保护。

#### 仍然存在的问题

1. 安全评测和正常任务成功评测仍然分离；
2. 用户意图本身不清楚时，安全策略更加困难；
3. “询问用户”也可能被恶意环境内容诱导；
4. 高风险操作确认协议和权限管理仍不统一；
5. 用户目标的长期保持和偏好冲突缺少统一表示。

#### 对本课题的启发

主动澄清模块不能只做槽位填充，还必须承担安全职责：

```text
用户目标不清楚 → 澄清
环境试图改变用户目标 → 提醒并确认
操作不可逆 → 二次确认
当前状态无法验证 → 停止，不声称成功
```

---

## 15.4 两个方向的综合比较

| 维度 | 意图识别 / 主动澄清 | Computer Use / GUI Agent |
|---|---|---|
| 研究对象 | 用户说了什么、缺了什么、是否有歧义 | Agent 如何在真实界面中完成目标 |
| 典型输入 | 文本、对话、语音、用户偏好 | 截图、DOM、Accessibility Tree、程序状态、工具结果 |
| 典型输出 | 意图、槽位、状态、澄清问题 | GUI 动作、工具调用、轨迹、验证结果 |
| 主要指标 | Intent Accuracy、Slot F1、澄清准确率 | Task Success、Step Success、Grounding、Recovery |
| 当前优点 | 有较成熟的任务型对话和状态表示 | 有较丰富的环境、基准和执行轨迹 |
| 当前不足 | 很少连接真实 GUI 执行 | 很少系统研究模糊指令和主动询问 |
| 共同难点 | 多轮状态、置信度、风险 | 长程状态、验证、失败恢复、安全 |
| 最关键的连接 | 判断何时可以执行 | 执行前、执行中和执行后验证 |

---

## 15.5 由文献提炼出的统一研究框架

```text
1. Intent Parsing
   识别意图、子意图、槽位、约束和风险

2. Uncertainty Diagnosis
   判断语言歧义、候选目标、环境矛盾和执行风险

3. Active Clarification
   选择能最大幅度减少不确定性的最小问题

4. Computer Use Planning
   生成结构化目标、工具路由、GUI 动作和预期状态

5. Verified Execution
   执行、观察、验证、恢复，必要时再次询问
```

建议统一维护以下状态：

```json
{
  "user_goal": {},
  "subgoals": [],
  "slots": {},
  "constraints": [],
  "candidate_interpretations": [],
  "candidate_gui_targets": [],
  "missing_information": [],
  "risk": "low|medium|high",
  "execution_confidence": 0.0,
  "status": "ready|need_clarification|need_confirmation|blocked|executing|completed|failed",
  "plan": [],
  "observations": [],
  "verification": {}
}
```

### 15.5.1 三层不确定性

```text
语言层： “把那个发给小王”中的“那个”和“小王”是什么？
感知层： 屏幕上有两个相似按钮，哪个是目标？
执行层： 点击后界面变化不明确，动作是否真的成功？
```

对应处理方式：

```text
语言层 → 向用户澄清
感知层 → 获取更多 UI 证据或向用户展示候选
执行层 → 观察、验证、重试或回滚
```

### 15.5.2 不要用一个 confidence 解决所有问题

推荐至少区分：

```json
{
  "intent_confidence": 0.91,
  "slot_confidence": 0.64,
  "target_confidence": 0.48,
  "execution_confidence": 0.00,
  "calibrated": false
}
```

最终决策应为：

\[
\text{Ask} = f(U_{language}, U_{perception}, U_{execution}, Risk, UserCost)
\]

而不是简单地执行 `confidence < 0.5`。

---

## 15.6 最值得形成论文的研究问题

### Research Question 1：什么时候应该主动澄清？

给定用户指令、对话历史和当前 GUI 状态，模型能否区分：

```text
直接执行 / 向用户澄清 / 请求确认 / 拒绝执行
```

### Research Question 2：如何选择最小澄清问题？

给定多个缺失槽位，模型应该优先询问哪个问题，才能最大化后续任务成功率并最小化用户负担？

### Research Question 3：如何把 GUI 候选目标反馈给意图模型？

当 grounding 模型发现多个候选目标时，上层模型能否基于候选集生成自然、具体的澄清问题？

### Research Question 4：澄清是否真正提高 Computer Use 成功率？

比较：

```text
直接执行
先澄清再执行
先澄清 + 状态验证
先澄清 + 验证 + 失败恢复
```

### Research Question 5：如何训练模型在不确定时不幻觉式执行？

构造偏好对：

```text
正确：发现两个文件，询问用户
错误：默认选择第一个文件
```

研究 SFT、DPO、GRPO/RLVR 对强行猜测、过度澄清、虚假高置信度和未验证声称完成的影响。

### Research Question 6：如何把主动澄清纳入 Computer Use RL？

动作空间除 `click`、`type`、`scroll`、`hotkey` 外，还应加入：

```text
ask_clarification
request_confirmation
observe_more
verify
abort
```

奖励同时考虑最终完成、澄清必要性、问题是否命中缺失信息、用户交互成本、错误动作和验证可靠性。

---

## 15.7 推荐的文献分层

### 第一层：必须精读

#### 意图识别 / 主动澄清

1. AREAs-Lab：交互式需求澄清；
2. SAGE：状态感知、可拒答的任务型对话评测；
3. Hear2Act：隐含状态到行动的中间表示；
4. Learning to Reason and Use Tools through Unsupervised Fine-Tuning：任务型对话中的推理和工具使用。

#### Computer Use

1. OSWorld 2.0：长程真实 Computer Use；
2. OSWorld-Pro：过程级评测；
3. KNOWS：知识综合和可交付产物；
4. Jev-Mobile：高层规划和低层执行解耦；
5. Argus：Computer Use 不确定性量化；
6. GUI-Actor / SeeClick：GUI grounding；
7. ScaleCUA / ENVS：可验证任务合成和 RL；
8. StateAct：程序状态和 GUI 混合执行；
9. CAVEAT / ERPBench：用户目标保持和安全执行。

### 第二层：用于扩展系统设计

- GUI-SD-v2：多轮交互和自蒸馏；
- EvoSkill-GUI：技能反思和演化；
- EchoPath：轨迹记忆和可重放技能；
- VISUALSKILL：多模态技能；
- ComponentBench：组件级诊断；
- GUI-Primitives：空间关系诊断；
- Desktop-Delta Bench：状态转移和验证；
- CUA-Universe：GUI 与 CLI 混合环境；
- MobileWorldSafety：环境注入攻击。

### 第三层：基础背景

- Mind2Web；
- WebArena；
- OSWorld 1.0；
- AgentBench；
- ReAct；
- Toolformer、ToolBench、API-Bank；
- Outlines；
- Qwen-Agent。

---

## 15.8 文献阅读记录模板

正式阅读时建议为每篇论文维护以下字段：

| 字段 | 记录内容 |
|---|---|
| 论文标题 | 完整标题和链接 |
| 年份 / 状态 | 会议、期刊、arXiv 或技术报告 |
| 研究方向 | 意图、澄清、grounding、规划、执行、验证、安全 |
| 输入 | 文本、对话、截图、DOM、A11y、工具结果 |
| 输出 | 意图、槽位、问题、动作、轨迹、状态 |
| 核心 idea | 方法最核心的一个机制 |
| 解决的问题 | 论文解决的具体瓶颈 |
| 数据 / 环境 | 数据集、模拟器、真实设备或桌面环境 |
| 指标 | 主要评测指标 |
| 主要结果 | 只记录可核对的结果 |
| 局限 | 作者明确承认或实验暴露的问题 |
| 与本课题关系 | 可直接借鉴、只能参考或存在冲突 |
| 可复现实验 | 代码、模型、数据和环境是否开源 |
| 可延伸 idea | 能否转化为自己的研究问题 |

---

## 15.9 当前最清晰的研究定位

综合近两年文献，建议不要把课题笼统命名为“意图识别 + Computer Use”。更准确的研究定位是：

> **面向不完整和歧义用户指令的风险感知主动澄清与可验证 Computer Use Agent**

英文：

> **Risk-Aware Active Clarification and Verified Computer Use Agents for Incomplete and Ambiguous User Instructions**

系统创新链条：

```text
残缺 / 模糊指令
    ↓
意图和槽位解析
    ↓
语言、感知、执行三层不确定性诊断
    ↓
最小信息增益澄清
    ↓
用户确认后的结构化计划
    ↓
GUI / CLI / API 工具路由
    ↓
动作执行和状态验证
    ↓
失败恢复、再规划或继续询问
```

最核心的科学假设是：

> 如果模型能够显式表示缺失槽位、候选解释、GUI 候选目标和任务风险，并通过主动澄清降低这些不确定性，那么它在长程 Computer Use 任务中的错误动作率和不安全执行率将低于直接执行模型，同时保持较高的任务完成率和较低的用户交互成本。

这一区域同时连接了意图识别、任务型对话、不确定性估计、GUI grounding、Computer Use、强化学习和安全 Agent，具有较清晰的论文切入点。