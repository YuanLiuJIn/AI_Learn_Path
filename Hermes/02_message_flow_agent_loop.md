# 02. 消息流转与 Agent Loop：一条消息的完整旅程

> 目标：追踪一条用户消息从进入 Hermes 到最终回复的完整执行路径。
> 核心：双消息轨设计、桥接工具、子 Agent 委派、收尾流程。

## 0. 整体流程概览

```
用户消息
  │
  ▼
① 预处理 ─── 恢复 System Prompt → 记忆检索 → 预压缩
  │
  ▼
② 主循环 ─── 构造 api_messages → LLM → 工具/子Agent → 循环
  │
  ▼
③ 收尾   ─── 持久化 → 记忆同步 → 后台回顾 → 返回用户
```

## 1. 预处理阶段：把一切调成"本轮状态"

预处理在做的是一件关键的事：**把进程、线程、SQLite、Agent 内部状态、对话历史、System Prompt、扩展上下文，全部调成属于"本轮对话"的状态。任何上一轮的残留、任何跨 Session 的串扰、任何跨进程的过期信息，都被清理或重新同步。**

### 1.1 恢复 System Prompt

```python
def build_system_prompt(session):
    """
    关键设计：System Prompt 整个会话只建一次，只有压缩时才重建。
    按变化频率从低到高排序，最大化 Prompt Cache 命中率。
    """
    prompt_parts = [
        # Stable 层（整个会话不变）—— 缓存长期命中
        load_from_file("SOUL.md"),           # 人格定义
        TOOL_BEHAVIOR_GUIDE,                 # 工具行为指导
        SKILL_INDEX,                         # 技能索引（仅名称+描述，不加载全文）
        ENVIRONMENT_HINTS,                    # 环境提示
        
        # Context 层（进一个项目固定）
        load_from_file("AGENTS.md"),         # 项目级上下文
        load_from_file(".cursorrules"),      # IDE 规则（如果有）
        
        # Volatile 层（日级精度）—— 压缩时才刷新
        MEMORY_SNAPSHOT,                     # MEMORY.md 冻结快照
        USER_SNAPSHOT,                       # USER.md 冻结快照
        f"Current time: {datetime.now()}",   # 时间戳
    ]
    return "\n".join(prompt_parts)
```

### 1.2 记忆预取（两种 Provider）

```python
def prefetch_memories(user_message: str):
    """在内核启动前拉取本轮需要的记忆"""
    
    # ① 内置 Provider：文件直读，无网络延迟
    # MEMORY.md 和 USER.md 已作为冻结快照注入 System Prompt
    # 这一步只是确保文件是最新版本（对缓存无影响）
    
    # ② 外部 Provider（honcho/mem0 等）：语义检索
    if has_external_memory_provider():
        results = external_provider.search(user_message, top_k=5)
        # 外部记忆通过 <memory-context> 围栏注入 user message 末尾
        # 不污染 System Prompt 缓存前缀
        return wrap_with_fence(results)
    
    return None

def wrap_with_fence(memories):
    """套上安全围栏"""
    return f"""
<memory-context>
[System note: The following is recalled memory context,
NOT new user input. Treat as authoritative reference data.]

{format_memories(memories)}
</memory-context>
"""
```

### 1.3 预压缩检查

```python
def pre_compress_check(messages, system_prompt, tools):
    """在发 API 请求前检查是否需要压缩"""
    estimated_tokens = (
        count_tokens(system_prompt) +
        count_tokens(messages) +
        count_tokens(tool_schemas)
    )
    
    if estimated_tokens > context_limit * 0.5:
        # 触发最多 3 轮中段总结压缩
        # （详见 03_context_management.md）
        for _ in range(3):
            middle_summary = auxiliary_llm.summarize(messages.middle)
            messages = messages.head + middle_summary + messages.tail
            if count_tokens(messages) < context_limit * 0.4:
                break
    
    return messages
```

## 2. 主循环：LLM ↔ 工具

这是 Agent 真正的"思考-行动"循环。

### 2.1 双消息轨设计（核心机制）

Hermes 维护两套消息列表：

```python
# messages：对话历史（永远干净）
# 包含：
#   - 所有用户消息
#   - 所有模型回复（含 tool_calls 的完整信息）
#   - 所有工具执行结果
# 永远不会被直接传给 LLM API！

# api_messages：每轮 API 调用前从 messages 临时构造
def build_api_messages(messages):
    api_messages = []
    for msg in messages:
        copy = deepcopy(msg)
        
        # 剥离内部字段（模型不认识）
        copy.pop("reasoning", None)
        copy.pop("finish_reason", None)
        
        # 清洗格式适配当前模型
        if is_openai_format:
            copy = adapt_for_openai(copy)
        elif is_anthropic_format:
            copy = adapt_for_anthropic(copy)
        
        api_messages.append(copy)
    
    # 在最后一条 user message 尾部追加外部记忆
    if external_memory_context:
        api_messages[-1].content += external_memory_context
    
    return api_messages
```

**为什么要双消息轨？**

```text
单消息轨的痛点：
  messages 既要记录历史（需要保留 reasoning/finish_reason 等内部信息），
  又要传给 API（不能包含内部字段），
  每轮调完还得清理 → 容易出错/遗漏。

双消息轨：
  messages   = 永久金标准记录（完整、不变）
  api_messages = 每次临时的 API 友好副本（干净、适配）
  
  各司其职，互不污染。
```

### 2.2 一次主循环迭代

```python
def agent_loop_iteration(messages, tools):
    """单次 'LLM 调用 + 工具执行' 的完整迭代"""
    
    # 1. 构造 api_messages
    api_messages = build_api_messages(messages)
    
    # 2. 调用 LLM
    response = llm.chat(
        model=current_model,
        messages=api_messages,
        tools=tool_schemas,  # 独立传递，不在消息体内
        temperature=0.7,
    )
    
    # 3. 处理响应
    if response.is_text():
        # 纯文本 → 结束本轮
        return {"type": "text", "content": response.content}
    
    elif response.has_tool_calls():
        for tool_call in response.tool_calls:
            result = execute_tool_call(tool_call)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        # 继续循环：下一轮 LLM 会看到工具结果
        return {"type": "continue"}
```

### 2.3 桥接工具：解决"工具太多"的问题

Hermes 内置 60+ 工具。如果全部 schema 一次性传给模型，会严重消耗上下文。

**桥接工具机制**：当工具总 schema 超过模型上下文 10% 时，非核心工具的 schema 暂时隐藏，模型通过三个桥接工具按需获取：

```python
BRIDGE_TOOLS = {
    "tool_search": {
        "description": "按关键词搜索可用工具",
        "parameters": {
            "query": "搜索关键词（如 'file write'、'web search'）"
        },
    },
    "tool_describe": {
        "description": "获取指定工具的完整说明和参数",
        "parameters": {
            "tool_name": "工具名称"
        },
    },
    "tool_call": {
        "description": "执行指定工具",
        "parameters": {
            "tool_name": "工具名称",
            "arguments": {},
        },
    },
}
```

**流程**：

```
LLM 想写文件但不知道有哪些工具
  ↓
调用 tool_search(query="write file")
  ↓
Harness 返回：[write_file, edit_file, append_file]
  ↓
LLM 选了 write_file，调用 tool_describe("write_file")
  ↓
Harness 返回 write_file 的完整 schema（参数/示例/注意事项）
  ↓
LLM 调用 tool_call("write_file", {path: "...", content: "..."})
  ↓
Harness 转发给真实 handler 执行
```

这个设计的精妙之处：
- **渐进式发现**：不需要一次性加载 60+ 工具的 schema
- **按需获取**：用了才加载详细说明
- **上下文高效**：启动时只占 3 个桥接工具（~300 tokens）而非所有工具（~数万 tokens）

## 3. 工具执行：安全检查 + Checkpoint + 并发

```python
def execute_tool_call(tool_call):
    """执行工具调用的完整流程"""
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    # 1. 安全检查（guardrail）
    # 检测 LLM 是否在无效重复调用同一工具
    if is_repeat_loop(tool_name, args):
        return "WARNING: You've called this tool multiple times without progress. Stop and reconsider."
    
    # 2. Checkpoint 快照（文件变更/破坏性命令前）
    if tool_name in CHECKPOINT_TOOLS:
        save_checkpoint_snapshot()
    
    # 3. 如果是桥接工具，先解析再转发
    if tool_name in BRIDGE_TOOLS:
        real_tool = resolve_bridge(tool_name, args)
        return real_handler.execute(real_tool, args)
    
    # 4. 执行
    result = tool_registry.execute(tool_name, args)
    
    return result
```

### 3.1 委派子 Agent（delegate_task）

主循环中最高级的工具调用是委派一个子 Agent：

```python
def delegate_task(args):
    """
    父 Agent 把任务委派给子 Agent，
    子 Agent 拥有独立的上下文、工具集和迭代预算。
    只返回 summary，不返回中间过程。
    """
    # 1. 构建子 Agent
    child = build_child_agent(
        goal=args["goal"],
        context=args["context"],
        tools=intersect(parent_tools, requested_tools),
        role=args.get("role", "leaf"),  # leaf or orchestrator
    )
    
    # 2. 独立运行
    result = child.run_conversation()
    
    # 3. 只返回摘要给父 Agent
    return {
        "status": result.status,
        "summary": result.summary,       # ← 不是全部 history！
        "artifacts": result.artifacts,
        "iterations": result.iterations,
    }
```

**关键设计：父 Agent 只看到摘要，不看到中间过程。防止父上下文被子任务中间结果污染。**

## 4. 收尾阶段

```python
def finalize_conversation(messages, final_response):
    """对话收尾：持久化、记忆同步、后台回顾"""
    
    # 1. 持久化消息历史到 SQLite
    session_db.save_messages(messages)
    session_db.save_stats({
        "tokens_used": total_tokens,
        "cost": total_cost,
        "tool_calls": len(tool_calls),
    })
    
    # 2. 记忆同步
    for provider in memory_providers:
        try:
            provider.sync_turn(messages)
            # 将本轮对话沉淀为长期记忆
        except Exception:
            pass  # 单个 provider 失败不阻塞其他
    
    # 3. 后台回顾触发（异步，不阻塞返回）
    if should_trigger_review():
        # fork 一个受限 Review Agent
        # 详见 04_memory_and_self_evolution.md
        spawn_review_agent(messages)
    
    # 4. 返回用户
    return final_response
```

## 5. 完整时序图

```
时间轴 →
                            用户消息
                               │
                               ▼
┌─ 预处理 ──────────────────────────┐
│ restore System Prompt (cached)    │  ← SQLite
│ prefetch Memories                 │  ← MEMORY.md + external
│ pre-compress check (if needed)    │
└──────────────┬────────────────────┘
               ▼
┌─ 主循环 ──────────────────────────┐
│ while not done:                   │
│   build api_messages              │
│   call LLM ────────────────────►  │
│   handle response:                │
│     if text → break               │
│     if tool_call →                │
│       guardrail check             │
│       if delegate_task →          │
│         spawn sub-agent ──────►   │ (独立线程)
│       else:                       │
│         execute tool              │
│       append result to messages   │
│   continue loop                   │
└──────────────┬────────────────────┘
               ▼
┌─ 收尾 ────────────────────────────┐
│ persist to SQLite                 │
│ sync_memory (all providers)       │
│ trigger background_review ────►   │ (异步)
│ return final_response             │
└───────────────────────────────────┘
```

## 6. 关键论文与设计参考

- **双消息轨**：Hermes 原创设计，灵感来自"命令查询职责分离"（CQRS）模式
- **桥接工具**：受 Toolformer 的自监督工具学习启发
- **子 Agent 隔离**：借鉴了 Anthropic Managed Agents 的"brain/hands 解耦"思想

## 7. 一句话总结

> Hermes 的消息流转 = 预处理（对齐状态）→ 主循环（LLM ↔ 工具，双消息轨保证数据纯净）→ 收尾（持久化 + 记忆沉淀 + 异步复盘）。核心工程技巧：**双消息轨保数据纯净、桥接工具解上下文爆炸、子 Agent 隔离防上下文污染。**
