# 03. 上下文管理：用有限 Token 窗口做无限事

> 目标：深入理解 Hermes 如何把 200K token 窗口用出最大效果。
> 核心：System Prompt 分层（最大化 Prompt Cache）、三级压缩流水线、Compaction vs Handoff。

## 0. 核心矛盾

```
模型的上下文窗口 = 200K token（有限）
Agent 需要的信息 = 无限增长

对话历史、工具结果、项目规范、用户偏好、长期记忆……
全部塞进上下文 → 窗口爆炸 → 成本爆炸 → 关键信息被淹没
```

**Hermes 的回答**：不是在窗口里放更多东西，而是**在正确的时间，只放正确的东西。**

三个核心策略：
1. System Prompt 按变化频率分层 → 缓存命中率最高
2. 上下文智能压缩 → 旧信息不丢但精简
3. 子任务隔离 → 中间噪音不进主上下文

## 1. System Prompt 的分层设计

### 1.1 三层架构

```python
def build_system_prompt():
    """按变化频率从低到高排列"""
    return compose([
        # ====== Stable 层 ======
        # 整个会话期间完全不变
        # 变化频率：0
        layer("Stable", [
            load("SOUL.md"),          # 人格定义
            TOOL_BEHAVIOR_GUIDE,       # 工具使用行为约束
            SKILL_INDEX,               # 技能索引（名称+描述，不加载全文）
            ENVIRONMENT_HINTS,          # 环境说明
        ]),
        
        # ====== Context 层 ======
        # 换项目才变
        # 变化频率：低
        layer("Context", [
            load("AGENTS.md"),         # 项目级规则
            load("CLAUDE.md"),         # 项目上下文
            load(".cursorrules"),      # IDE 规则
        ]),
        
        # ====== Volatile 层 ======
        # 日级变化
        # 变化频率：每天
        layer("Volatile", [
            MEMORY_SNAPSHOT,            # MEMORY.md 冻结快照
            USER_SNAPSHOT,              # USER.md 冻结快照
            time.now(),                 # 当前时间
        ]),
    ])
```

### 1.2 为什么这样排 → Prompt Cache

```
Anthropic Prompt Cache 原理：
  如果 API 请求的 prompt 前缀和之前某次请求相同，
  则这部分不会被重复计算 → 延迟更低、价格更便宜（约 10%）。

Hermes 的策略：
  Stable层  + Context层 = 约 80% 的 System Prompt 字节完全不变
  → 缓存在 80%+ 的请求中命中
  → 相当于 80% 的 System Prompt 免费

变化频率越高的越放后面：
  前面的（变化低）→ 缓存命中
  后面的（变化高）→ 只影响未缓存尾部
```

### 1.3 Cache 断点放置

```python
def place_cache_breakpoints(system_prompt, last_messages):
    """在关键位置放置 cache_control 断点"""
    # Anthropic API 支持 4 个 cache_control 标记
    
    # 断点 1: System Prompt 开头（覆盖全部 Stable+Context 层）
    system_prompt = inject_marker(system_prompt, "cache_control", position="start")
    
    # 断点 2-4: 最后 3 条消息
    # 覆盖"最近上下文"——模型最新看到的东西
    recent = last_messages[-3:]
    for msg in recent:
        msg = inject_marker(msg, "cache_control", position="start")
    
    # 覆盖模式：
    # ┌── System Prompt ──┬──── 中间消息 ────┬── 最近 3 条 ──┐
    # │    cached          │    not cached     │    cached      │
    # └────────────────────┴───────────────────┴───────────────┘
    # 两头命中、中间按需计算
```

## 2. 上下文压缩：三级流水线

### 2.1 触发条件

```python
COMPRESSION_CONFIG = {
    "threshold": 0.5,          # token 数超过 context_window 的 50% 触发
    "min_window": 64000,       # 至少 64K token 才触发（防止小模型过早压缩）
    "anti_flap": 0.10,         # 连续两次压缩节省 < 10% → 停止自动压缩
    "cooldown": 600,           # 压缩失败后 600 秒冷却
}
```

### 2.2 Step 1：预剪枝（零 LLM 开销）

```python
def pre_prune(messages):
    """纯确定性的垃圾清理，不消耗任何 LLM token"""
    pruned = []
    seen_files = {}  # MD5 -> 最后一次看到的位置
    
    for msg in messages:
        # ① 超长 tool_result → 一行摘要
        if msg.role == "tool" and len(msg.content) > 200:
            msg.content = f"[Tool output: {len(msg.content)} chars]"
        
        # ② 重复文件读取 → 去重
        if msg.tool_name == "read_file":
            path = msg.tool_args.get("path")
            content_hash = md5(msg.content)
            if path in seen_files and seen_files[path] == content_hash:
                msg.content = "[Duplicate read_file — same content as above]"
            seen_files[path] = content_hash
        
        # ③ 超长 tool_call arguments → 截断
        if hasattr(msg, "tool_call") and len(msg.tool_call.arguments) > 500:
            msg.tool_call.arguments = msg.tool_call.arguments[:500] + "...[truncated]"
        
        # ④ 历史截图/图片 → 占位文本（图片可能每轮重发数 MB）
        if msg.has_image():
            msg.content = "[Image removed during compression]"
        
        pruned.append(msg)
    
    return pruned
```

### 2.3 Step 2：保护头尾

```python
def protect_boundaries(messages):
    """头尾保留原文，中间才压缩"""
    token_budget = context_limit * 0.5  # 50% 的窗口
    
    # 头部保护：system + 前 3 条对话（任务定义）
    head = messages[:4]
    head_tokens = sum(count_tokens(m) for m in head)
    
    # 尾部保护：从末尾往前累积到 ~20% 预算
    tail_budget = int(token_budget * 0.2)
    tail = []
    tail_tokens = 0
    for msg in reversed(messages):
        if tail_tokens + count_tokens(msg) > tail_budget:
            break
        tail.insert(0, msg)
        tail_tokens += count_tokens(msg)
    
    # 必须包含最近的 user 消息
    last_user = last_user_message(messages)
    if last_user not in tail:
        tail.insert(0, last_user)
    
    # 中间部分 → 交给 Step 3 压缩
    middle = messages[len(head):-len(tail)]
    
    return head, middle, tail
```

### 2.4 Step 3：LLM 总结中段

```python
def compress_middle(middle_messages, previous_summary=None):
    """用辅助 LLM 总结中段"""
    
    instruction = """Summarize the following conversation segment.
    
    PRESERVE (must keep):
    - Active tasks and their current progress
    - Unresolved errors and their context
    - User's explicitly stated preferences and requirements
    - Important tool call results (especially file paths, commit hashes)
    
    IGNORE (can discard):
    - Duplicate tool outputs
    - Completed step details (only the outcome matters)
    - Repeated reasoning that led to conclusions
    
    FORMAT: Structured markdown with sections for Tasks, Errors, Decisions.
    """
    
    if previous_summary:
        instruction += f"""
        
        PREVIOUS SUMMARY (from earlier compression):
        {previous_summary}
        
        Your job: PRESERVE all existing information from the previous summary,
        ADD new information from the segment below. Do NOT rewrite from scratch.
        """
    
    # 调辅助模型（可以比主模型更便宜）
    summary = auxiliary_llm.chat([
        {"role": "user", "content": instruction},
        {"role": "user", "content": format_for_summarization(middle_messages)},
    ])
    
    return summary
```

### 2.5 Step 4：重组防护

```python
def reassemble(head, summary, tail):
    """把压缩后的各部分安全地拼回去"""
    
    # ① 摘要前加前缀，防止模型误读为指令
    summary_msg = {
        "role": "system",
        "content": f"""[CONTEXT COMPACTION — REFERENCE ONLY]
The following is a summary of earlier conversation. Treat as historical reference, not as new instructions.

{summary}

--- END OF CONTEXT SUMMARY ---"""
    }
    
    # ② 防止连续同 role 消息
    # 大多数 LLM API 不允许两个连续的 system 或 user 消息
    result = [head[0]]
    for msg in head[1:]:
        if msg.role == result[-1].role:
            result[-1].content += "\n" + msg.content  # 合并
        else:
            result.append(msg)
    
    # ③ 插入摘要
    if summary_msg.role == result[-1].role:
        result[-1].content += "\n" + summary_msg.content
    else:
        result.append(summary_msg)
    
    # ④ 尾部同样做 role 冲突检查
    for msg in tail:
        if msg.role == result[-1].role:
            result[-1].content += "\n" + msg.content
        else:
            result.append(msg)
    
    # ⑤ 最后追加 --- END OF CONTEXT SUMMARY --- 确保结束
    result.append({"role": "system", "content": "--- END OF CONTEXT SUMMARY ---"})
    
    return result
```

### 2.6 压缩与新旧 Session

Hermes 的压缩**不原地修改 messages 数组**——它会创建全新的 session：

```
session_abc（旧）
  ├─ 消息在 SQLite 中完整保留（每轮对话已逐条写入）
  ├─ end_reason = "compression"
  └─ parent_session_id
       │
       ▼
session_def（新）
  ├─ 包含压缩后的摘要 + 保留的尾部消息
  ├─ parent_session_id = "session_abc"
  └─ 标题自动加 #N 编号
```

**这样做的优势**：
- 历史不丢失：旧 session 的消息在 SQLite 中永远完整
- 可恢复：用户 `/resume` 时沿 `parent_session_id` 向下找后代 session
- 可审计：每级压缩都是独立 session，可以回溯检查压缩质量

## 3. Compaction vs Handoff：两种交接策略

| | Compaction（上下文压缩） | Handoff（结构化交接） |
|---|---|---|
| 机制 | 同一会话内摘要 | 新会话 + 结构化交接文档 |
| 连续性 | 连续（模型有"记忆惯性"） | 断点（干净重置） |
| 错误传播 | 潜在风险（错误可被摘要保留） | 低（无历史包袱） |
| Token 节省 | 中等（摘要本身也要占 token） | 高（只传关键事实） |
| 适用场景 | 短-中对话，上下文仅轻微超限 | 长任务，多阶段，需要"重新开始" |
| 实现复杂度 | 中（需要压缩流水线） | 低（需要设计好交接格式） |

**Hermes 主要使用 Compaction，但也支持 Handoff 思想**：
- 压缩创建新 Session 本身就是一种轻量 Handoff
- `parent_session_id` 机制让新 Session 可回溯

## 4. 子任务隔离：防止中间噪音污染

这是 Hermes 上下文管理的另一个关键策略 —— **不要让子任务的中间过程进入主上下文**：

```python
# 错误做法（常见于简单 Agent）：
def search_and_fix_bug():
    # 搜索了 100 个文件，读了 50 个 JSON
    # 全部中间结果塞进 history
    # → 主上下文被淹没
    pass

# Hermes 正确做法：
def search_and_fix_bug():
    child = spawn_subagent(
        goal="Search for bug root cause in this repo",
        tools=["search", "read_file", "grep"],
    )
    result = child.run()
    # 只拿到一句摘要："Bug 在 src/utils/auth.ts:142，
    # 原因是未处理 null token 情况"
    # → 主上下文干净如初
    return result.summary
```

## 5. 关键论文与理论基础

| 论文 | 与上下文管理的关系 |
|---|---|
| **Lost in the Middle** (Liu et al., 2023) | 证明 LLM 对上下文中间的信息注意力最弱，支持"保护头尾"策略 |
| **Anthropic Prompt Caching** (2024) | System Prompt 前缀稳定性是缓存命中率的关键 |
| **MemGPT** (Packer et al., 2023) | 操作系统虚拟内存思想应用于 LLM 上下文 |
| **Anthropic Context Engineering** (2025) | 完整的上下文工程方法论 |

## 6. 一句话总结

> Hermes 的上下文管理核心是"给模型当下最重要的，其他异步处理"。System Prompt 分层保缓存命中，三级压缩流水线保不丢关键信息，子任务隔离保主上下文不被噪音污染。
