# 01. Hermes 概述与架构全景

> 目标：建立对 Hermes 的整体认知——它是什么、解决什么问题、核心架构如何。
> 阅读时间：约 1 小时。

## 1. Hermes 是什么？

### 一句话定义

> Hermes = 一个**长寿命、会自我进化**的 AI Agent 系统。

和传统 ChatBot 的本质区别：

| | 传统 ChatBot | Hermes Agent |
|---|---|---|
| 记忆 | 无（每次对话从零开始） | 跨会话持久化，越用越懂你 |
| 学习 | 无 | 内置自学习闭环（Background Review + Curator） |
| 生命周期 | 无状态函数调用 | 长期运行的"助手进程" |
| 技能 | 全由开发者写死 | Agent 可以**自己创建新技能** |

### 核心问题

Hermes 要解决的根本问题是：

> 让一个 Agent 能跨会话、跨平台、持续地陪着用户工作，并在陪伴过程中**越来越懂你**。

不是"每次对话都是一次全新的开始"，而是"一个熟悉的助手，每次都记得你上次教它的东西"。

### 出身

Hermes-Agent 来自 **Nous Research**（开源 AI 研究组织，以发布高质量的微调模型闻名）。内网版在此基础上做了企业级适配。

## 2. 为什么需要"长寿命 Agent"？

### 2.1 单次对话的局限

```
传统模式：
  用户: 帮我查一下日志
  Agent: [查完了] 结果是 XXX
  --- 对话结束，Agent 失忆 ---
  用户: 上次那个问题又出现了
  Agent: 哪个问题？（从头问起）
```

### 2.2 长寿命 Agent 的价值

```
Hermes 模式：
  用户: 我是广告投放后端，负责一致性模块，代码在 /data/workspace/xxx
  Agent: [记住用户画像]
  
  用户: 帮我查这个创意的消息推送链路，dcid=44444
  Agent: 需要查消息中心日志 → 查 API 消费日志 → 给结论
  [后台自动把排查流程沉淀为 Skill]
  
  --- 新对话 ---
  用户: dcid=55555，同样的问题
  Agent: [自动调出上次的排查 Skill] 查日志 → 查 API → 结论
  （不再需要用户重新描述排查步骤）
```

**这就是"越用越懂你"的核心价值**——Agent 在后台默默从每次交互中学习。

## 3. 核心哲学

Hermes 的设计贯穿三条哲学原则：

### 原则 1：同步内核，异步外壳

```
┌──── 同步内核（实时、确定） ────┐
│  主线 Agent Loop               │
│  每一步都等待 LLM 返回           │
│  用户实时看到进度                │
└────────────────────────────────┘
          ▲            │
          │            ▼
┌──── 异步外壳（后台、无感） ────┐
│  6 种前端、25+ 模型 Provider    │
│  20+ 消息平台（企微/飞书/Slack） │
│  60+ 工具（全部插件化）          │
└────────────────────────────────┘
```

- **同步内核**：用户看到的部分——消息进来、Agent 思考、调工具、回复。每一步都是同步的
- **异步外壳**：用户看不到的部分——Gateway 处理多平台消息、记忆后台沉淀、技能后台更新

### 原则 2：主线 + 暗线

```
主线（用户可见）：
  用户消息 → Agent 思考 → 工具调用 → 回复
  这是你直接交互的部分

暗线（用户无感）：
  Background Review → 写记忆 → 建技能
  Curator → 清理过时技能 → 合并重复技能
  这是 Agent 在"偷偷学习"的部分
```

**这个设计哲学非常有意思**：Agent 不是在你教它的时候学习，而是在每次对话**结束后**悄悄复盘。

### 原则 3：越用越懂你，但不是无限制增长

Hermes 刻意对记忆容量做了限制（MEMORY.md 2200 字符 + USER.md 1375 字符 ≈ 1300 tokens）。

这不是技术限制，而是**工程权衡**：

```
无限制记忆 → System Prompt 不断膨胀 → 缓存失效 → 成本爆炸
有限记忆 + 优先级管理 → System Prompt 字节级稳定 → 缓存长期命中
```

## 4. 三段式架构全景

```
┌──────────────────────────────────────────────────────┐
│                    Hermes Agent                       │
│                                                      │
│  ┌─────────────── 同步内核 ───────────────┐          │
│  │                                        │          │
│  │  ① 构 Prompt (System + Context + Memory) │        │
│  │       ↓                                │          │
│  │  ② 调 LLM (模型决策)                    │          │
│  │       ↓                                │          │
│  │  ③ 派工具 (60+ 工具/子Agent委派)         │          │
│  │       ↓                                │          │
│  │  ④ 记会话 (SQLite 持久化)               │          │
│  │       ↓                                │          │
│  │  ⑤ 压上下文 (超限则压缩)                 │          │
│  │                                        │          │
│  │  循环 ②-⑤ 直到任务完成或超限             │          │
│  └────────────────────────────────────────┘          │
│                                                      │
│  ┌─────────────── 异步外壳 ───────────────┐          │
│  │  • 6 种前端：CLI / TUI / Web / Gateway │          │
│  │  • 25+ Provider：OpenAI/Claude/Venus…  │          │
│  │  • 20+ 消息平台：企微/飞书/Slack…       │          │
│  │  • 插件体系：全部解耦，核心不感知差异    │          │
│  └────────────────────────────────────────┘          │
│                                                      │
│  ┌────────────── 自学习闭环 ──────────────┐          │
│  │                                        │          │
│  │  Background Review (每 N 轮异步)        │          │
│  │    ├─ fork 影子 Agent                  │          │
│  │    ├─ 回看对话 → 写 MEMORY.md           │          │
│  │    ├─ 提炼流程 → 创建 SKILL.md          │          │
│  │    └─ 只允许 memory + skills 工具       │          │
│  │                                        │          │
│  │  Curator (周级定时)                     │          │
│  │    ├─ 状态流转（active→stale→archived） │          │
│  │    ├─ 伞状合并（合并零散 Skill）         │          │
│  │    └─ 跑前快照 + dry-run 安全兜底       │          │
│  └────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────┘
```

### 内核五步骤详解

```python
# Hermes 的同步内核伪代码
def run_conversation(user_message: str) -> str:
    """一条消息到一条回复的完整流程"""
    
    # ① 构 Prompt
    system_prompt = build_system_prompt()  # Stable+Context+Volatile 分层
    memory_context = retrieve_memories(user_message)  # 检索相关记忆
    context = assemble(system_prompt, history, memory_context)
    
    # 预压缩检查
    if estimate_tokens(context) > threshold:
        context = compress(context)
    
    # ② 主循环（LLM ↔ 工具）
    while not done:
        # 构造 api_messages（双消息轨）
        api_messages = prepare_api_messages(messages)
        
        # 调用 LLM
        response = llm.chat(api_messages, tools=available_tools)
        
        if response.is_text():
            # 纯文本 → 退出循环，进入收尾
            final_answer = response.content
            done = True
        elif response.has_tool_calls():
            for tool_call in response.tool_calls:
                if tool_call.name == "delegate_task":
                    # 子 Agent 委派
                    result = spawn_subagent(tool_call.args)
                else:
                    # 安全检查
                    guardrail.check(tool_call)
                    # 执行工具
                    result = execute_tool(tool_call)
                # 结果回填（写入 messages，不写入 api_messages）
                messages.append({"role": "tool", "content": result})
    
    # ③ 收尾
    persist_session(messages)        # 写入 SQLite
    sync_memory(final_answer)        # 同步记忆
    trigger_background_review()      # 后台异步复盘
    
    return final_answer
```

## 5. 与 OpenClaw 的初步对比（预览）

| 维度 | OpenClaw | Hermes |
|---|---|---|
| 定位 | 连接一切，多 Agent 协作 | 会自我进化的个人助手 |
| 哲学 | 工具多、生态广、让模型有更多选择 | 学习闭环、越用越懂你 |
| 记忆 | 插件化，手动配置 | 双通路自动持久化 + 自进化 |
| 技能 | 用户/Skill-creator 显式编写 | Agent 可**自主创建**新技能 |
| 多 Agent | 强项（spawn/send/团队） | 可行但官方建议单 Agent |

详细对比见 `06_hermes_vs_openclaw.md`。

## 6. 关键设计决策一览

| 设计决策 | 为什么这样做 | 代价 |
|---|---|---|
| 双消息轨 | 保持 messages 干净，api_messages 临时加工 | 每次 API 调用多一次拷贝 |
| 记忆快照不实时刷新 | 保证 System Prompt 字节级稳定 → 缓存命中 | 新记忆在当前会话不立即生效 |
| Background Review 用 fork Agent | 隔离学习过程，不污染主线 | 额外的 LLM 调用成本 |
| 记忆容量硬限制 | 保缓存、防 System Prompt 膨胀 | 旧知识会被覆盖 |
| 压缩创建新 Session | 历史完整保留、可追溯 | 父子链管理复杂度 |

## 7. 一句话总结

> Hermes = 一个带自学习能力的个人 AI 助手。它不是"每次对话从零开始"的 ChatBot，而是在后台默默复盘、积累经验、更新技能的"长期陪伴型" Agent。核心架构是"同步内核（主线对话）+ 异步外壳（多平台接入）+ 自学习闭环（暗线复盘）"。

## 8. 下一步

阅读 `02_message_flow_agent_loop.md` —— 理解一条用户消息在 Hermes 内部如何从头走到尾。
