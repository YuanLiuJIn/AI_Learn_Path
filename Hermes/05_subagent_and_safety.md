# 05. 子 Agent 委派与安全体系设计

> 目标：深入理解 Hermes 的 Subagent 委派机制与多层安全防线。
> 核心：为什么需要子 Agent、leaf vs orchestrator、三级安全体系。

## 0. 为什么需要子 Agent？

### 单 Agent 的三大瓶颈

```
瓶颈 1：上下文污染
  搜索 100 个文件、读 50 个 JSON 的中间结果全部塞进 history
  → 主 Agent 的注意力被淹没 → 推理质量雪崩

瓶颈 2：不能并行
  天然串行，A 做完才能做 B
  → 大范围代码搜索必须逐个来

瓶颈 3：角色混淆
  调研 + 编码 + 审查全由一个 Agent 承担
  → 思维定式、自评失真
```

### Hermes 的解法

> 把委派做成一个**纯函数工具调用**：主 Agent 调用 `delegate_task`，Harness 创建隔离的子 Agent，执行完后只向主 Agent 返回摘要。

## 1. 委派流程

### 1.1 delegate_task 和其他工具一样

```python
# delegate_task 是注册在 ToolRegistry 里的普通工具
# 模型的 tool_call 只是 trigger，真正的执行在 harness 里

TOOL_SCHEMA = {
    "name": "delegate_task",
    "description": "Delegate a self-contained task to a sub-agent.",
    "parameters": {
        "goal": "Clear goal description for the sub-agent",
        "context": "Relevant context (facts, file paths, constraints)",
        "role": "leaf (default, execution-only) or orchestrator (can delegate further)",
        "tools": ["read_file", "search_code", "run_test"],
    },
}
```

### 1.2 完整委派流程

```
父 Agent
  │
  ├─ 1. 构建子 Agent
  │    ├─ 继承父的 credentials / provider / model
  │    ├─ 生成独立 system prompt（只聚焦子任务）
  │    ├─ 计算 effective_toolsets（父子交集，最小权限）
  │    ├─ 强制剥离 leaf 禁用工具集（delegation/memory/clarify/execute_code）
  │    └─ 分配唯一 subagent_id（sa-{index}-{uuid8}）
  │
  ├─ 2. 提交到 ThreadPoolExecutor（最大 8 worker）
  │
  ├─ 3. 子 Agent 独立运行
  │    ├─ 独立 messages 列表（不继承父的 history）
  │    ├─ 独立 iteration_budget（默认 50 次 API 调用）
  │    ├─ 通过 progress_callback 实时汇报工具调用
  │    └─ 完成后生成 summary
  │
  └─ 4. 父 Agent 收到 summary
       ├─ 作为 tool_result 注入父的 messages
       ├─ 刷新 progress 显示
       └─ 继续主循环
```

### 1.3 代码实现

```python
def build_child_agent(goal, context, tools, role="leaf"):
    """构建隔离的子 Agent"""
    
    child = Agent()
    
    # 继承父的能力
    child.credentials = parent.credentials
    child.provider = parent.provider
    child.model = parent.model
    
    # 生成独立 System Prompt（只聚焦当前子任务）
    child.system_prompt = f"""You are a sub-agent with a single task.

GOAL: {goal}

CONTEXT:
{context}

RULES:
- Focus ONLY on the goal above
- Return a structured summary when done
- Do not ask for clarification — use your best judgment
- Tool calls are limited to: {', '.join(tools)}
"""
    
    # 最小权限：父子工具集取交集
    child.tools = intersect(parent.tools, requested_tools)
    
    # 角色限制
    if role == "leaf":
        # 纯执行单元，禁止派生/记忆/澄清/执行代码
        child.disabled_tools.update({
            "delegate_task",    # 不能套娃
            "memory_add",       # 不能写记忆
            "memory_replace",
            "clarify",          # 不能问用户
            "execute_code",     # 不能执行代码
        })
    elif role == "orchestrator":
        # 可以再委派，但有深度限制
        child.max_delegation_depth = parent.max_delegation_depth - 1
    
    # 分配独立 ID
    child.id = f"sa-{parent.child_count}-{uuid8()}"
    child.parent_id = parent.id
    
    return child
```

## 2. 角色分级：Leaf vs Orchestrator

```
┌─────────────────┐
│   父 Agent       │
│   (depth = 0)   │
└────────┬─────────┘
         │ delegate_task
    ┌────┴────┐
    │         │
┌───▼───┐ ┌───▼────────┐
│ Leaf  │ │Orchestrator│
│d=1    │ │   d=1      │
│纯执行  │ │ 可再派发    │
└───────┘ └─────┬──────┘
                │ delegate_task
           ┌────▼────┐
           │  Leaf   │
           │  d=2    │
           └─────────┘
```

| 角色 | 能力 | 限制 |
|---|---|---|
| **leaf**（默认） | 纯执行单元 | 禁用 delegate_task / memory / clarify / execute_code — 不能套娃、不能越权 |
| **orchestrator** | 可以再委派 | depth 上限=1（只允许一级委派），需调用方显式传入 `role="orchestrator"` |

**设计原因**：默认 leaf 是安全原则——"你只能做我让你做的事，不能擅自把任务再拆给别人"。

## 3. 可靠性保障

### 3.1 心跳保活

```python
class Heartbeat:
    """防止父 Agent 在等待子 Agent 时被 Gateway 误杀"""
    
    INTERVAL = 30  # 30 秒
    
    def keep_alive(self):
        while self.child_running:
            self.touch_activity_timestamp()
            # 对 Gateway 层：父 Agent 持续"活跃"
            # 不会因为 "太久没响应" 被强制终止
            time.sleep(self.INTERVAL)
```

### 3.2 超时兜底

```python
CHILD_TIMEOUT = 600  # 10 分钟

def run_child_with_timeout(child, timeout=CHILD_TIMEOUT):
    """子 Agent 超时后自动中断"""
    
    future = executor.submit(child.run)
    
    try:
        result = future.result(timeout=timeout)
        return result
    except TimeoutError:
        # 记录诊断日志
        diagnostic = {
            "last_tool_call": child.last_tool_call,
            "iteration": child.iteration_count,
            "stuck_at": child.current_phase,
            "timestamp": now(),
        }
        log_diagnostic(diagnostic)
        
        # 中断子 Agent
        child.interrupt()
        
        return {"status": "timeout", "diagnostic": diagnostic}
```

### 3.3 Ctrl+C 级联中断

```python
def handle_parent_interrupt(signal):
    """用户 Ctrl+C → 中断传播到所有子 Agent"""
    
    parent.interrupt_requested = True
    
    # 级联中断所有正在运行的子 Agent
    for child in parent.running_children:
        child.interrupt()
    
    # 不留下僵尸进程
    # 父退出 → 所有子自动跟随
```

## 4. 安全体系：三层防线

### 4.1 第一层：Skill 安装扫描

安装外部 Skill 前必须通过静态代码扫描：

```python
class SkillScanner:
    """按威胁类别分级检测，按来源分级处置"""
    
    THREAT_PATTERNS = {
        "exfiltration": [  # 数据窃取
            r"curl.*\$KEY", r"wget.*\$TOKEN", r"~/.ssh", r"~/.aws",
        ],
        "injection": [     # 提示词注入
            r"(?i)ignore\s+previous", r"DAN\s+mode", r"泄露\s*system\s*prompt",
        ],
        "destructive": [   # 破坏性操作
            r"rm\s+-rf\s+/", r"mkfs", r"/dev/sda",
        ],
        "persistence": [   # 持久化后门
            r"crontab", r"\.bashrc", r"authorized_keys", r"systemd",
        ],
        "reverse_shell": [ # 反向 Shell
            r"nc\s+-e\s+/bin/sh", r"bash\s+-i\s+>&",
        ],
        "supply_chain": [  # 供应链攻击
            r"curl.*\|.*bash", r"pip\s+install.*&&", r"git\s+clone.*&&",
        ],
        "obfuscation": [   # 代码混淆
            r"base64\s+-d\s*\|", r"eval\(", r"exec\(",
        ],
        "credential": [    # 凭证暴露
            r"ghp_[a-zA-Z0-9]{36}", r"sk-[a-zA-Z0-9]{32,}", r"AKIA[A-Z0-9]{16}",
        ],
    }
    
    # 按来源分级处置
    INSTALL_POLICY = {
        "builtin":   {"safe": "allow", "caution": "allow", "dangerous": "allow"},
        "trusted":   {"safe": "allow", "caution": "allow", "dangerous": "block"},
        "community": {"safe": "allow", "caution": "block", "dangerous": "block"},
        "agent-created": {"safe": "allow", "caution": "allow", "dangerous": "confirm"},
    }
    
    # 结构检查
    MAX_FILES = 50
    MAX_TOTAL_SIZE = 1_048_576   # 1 MB
    MAX_FILE_SIZE = 262_144      # 256 KB
    FORBIDDEN_EXTENSIONS = {".exe", ".bin", ".so", ".dll", ".pyc"}
    
    # 不可见 Unicode 检测
    INVISIBLE_CHARS = {
        "\u200b", "\u200c", "\u200d", "\ufeff",  # 零宽字符
        "\u200e", "\u200f",                      # 方向标记
    }
```

### 4.2 第二层：Background Review 双重白名单

Review Agent 运行在用户不可见的后台线程，安全问题尤其关键：

```python
def build_review_guard():
    """两层独立防线"""
    
    # 防线 1：Prompt 层
    # "你只能调用 memory 和 skill 管理工具"
    SYSTEM_PROMPT = """You are a background review agent.
Your ONLY allowed actions are:
- Read/write to MEMORY.md and USER.md (memory tools)
- Create, update, or archive skill files (skill_manage tools)
All other tool calls will be REJECTED at runtime."""
    
    # 防线 2：Runtime 层（thread-local 白名单）
    # 即使模型"绕过"了 Prompt 约束，运行时仍会拒绝
    REVIEW_WHITELIST = frozenset({
        "memory_add", "memory_replace", "memory_remove", "memory_read",
        "skill_create", "skill_update", "skill_list", "skill_view",
    })
    
    def enforce_whitelist(tool_name):
        if tool_name not in REVIEW_WHITELIST:
            return f"ERROR: '{tool_name}' is not available to review agents. Allowed: {REVIEW_WHITELIST}"
    
    # 额外隔离
    review_agent.skip_memory = True  # 不向外部 Provider 写入
    # 防止 review harness prompt 被当成真实用户对话灌入外部记忆命名空间
    
    return review_agent
```

### 4.3 第三层：沙箱隔离

```python
# 子 Agent 的多层隔离保证

隔离维度：
  ✅ 独立 Session ID — 与父 Agent 完全分离
  ✅ 独立 messages 列表 — 不继承父的 history
  ✅ 独立 iteration_budget — 50 次 API 调用上限
  ✅ 裁剪工具集 — 父子交集 + 角色限制
  ✅ 凭证继承 — 但受工具白名单约束
  ✅ 进度隔离 — 通过 progress_callback 单向汇报
  ✅ 结果隔离 — 只回传 summary，中间过程不回传
```

## 5. 安全清单（部署前必查）

在 Hermes 部署到生产前，需要逐一检查的安全项：

```text
□ 关闭全用户访问
  GATEWAY_ALLOW_ALL_USERS=false
  调试期间可开放，生产必须限制

□ 谨慎使用 YOLO 模式
  HERMES_YOLO=true  → 自动批准所有命令，不弹确认
  仅调试用，生产禁用

□ 保护记忆文件权限
  ~/.hermes/memories/MEMORY.md 和 USER.md 是普通文本
  注意服务器文件权限，避免被其他用户读取

□ 限制 Gateway 用户
  GATEWAY_ALLOWED_USERS=你的企微ID

□ 审查安装的 Skill 来源
  优先 builtin + trusted，谨慎 community
```

## 6. 关键时刻回顾

```
子 Agent 委派 = 纯函数调用式隔离
   → 不污染父上下文
   → 最小权限（工具交集 + 角色限制）
   → 超时 + 心跳 + 级联中断三层保障

安全体系 = 三层防线
   → Skill 静态扫描（按来源分级处置）
   → Review Agent 双重白名单（Prompt + Runtime）
   → 子 Agent 完整隔离
```

## 7. 一句话总结

> 子 Agent 委派的精妙之处在于把复杂任务分解成**隔离、可恢复、可超时的独立执行单元**，而安全体系的核心哲学是**"信任但要验证"**——Prompt 层告诉模型不能做什么，Runtime 层确保即使模型"忘了"也不能做。
