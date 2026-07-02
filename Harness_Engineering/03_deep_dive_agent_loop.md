# Agent Loop 深度剖析：从 ReAct 到 Task Loop

> 本文目标：把 Agent Loop 从"论文里的公式"讲到"工程里的状态机"。
> 前置阅读：`harness_engineering_guide.md`（入门）、`harness_engineering_advanced.md`（进阶）。

## 0. 先建立直觉：什么是 Agent Loop？

Agent Loop 是 Harness 的核心执行循环，它回答的是：

> 用户一句话需求 → 模型思考 → 调工具 → 读结果 → 再思考 → 再调工具 → ... → 最终交付

最小形式只需要几行代码：

```python
while True:
    response = model.chat(messages)
    if response.has_tool_calls():
        for call in response.tool_calls:
            result = execute_tool(call.name, call.args)
            messages.append({"role": "tool", "content": result})
    else:
        return response.content  # 任务完成
```

这个循环看起来简单，但**真正的问题全在细节里**。

## 1. 历史脉络：三次迭代

| 阶段 | 代表工作 | 核心贡献 | 限制 |
|---|---|---|---|
| **1.0 推理+行动分离** | ReAct (2022) | 首次提出 Thought→Action→Observation 交替范式 | 没有工程化，只是 prompt 模式 |
| **2.0 工具调用标准化** | Function Calling / Toolformer (2023) | 模型学会何时调工具、调哪个、怎么吸收结果 | 工具执行在进程内，状态/恢复/安全全不管 |
| **3.0 生产级 Task Loop** | Anthropic Managed Agents / ADP (2025-2026) | 状态机驱动、异步执行、断点续跑、角色协作 | 仍在快速演化 |

### 1.1 ReAct：把推理和行动编织在一起

Yao et al. (2022) 的 ReAct 不是写了一段循环代码，而是**设计了一种 Prompt 模板**：

```text
Thought: 我需要先查一下用户的账户余额。
Action: query_database[SELECT balance FROM accounts WHERE user_id=42]
Observation: balance=1,230.50
Thought: 余额足够，可以执行转账。
Action: transfer[from=42, to=99, amount=500]
Observation: Transfer successful. Transaction ID: tx_8a3f.
Thought: 转账完成，通知用户。
Answer: 已成功转账 $500，当前余额 $730.50。
```

**关键洞察是**：模型不是在一个黑盒里做推理——把推理过程**显式化**成自然语言步骤，每一步的可观察输出又作为下一步的输入。这构成了 Agent Loop 的基本骨架。

### 1.2 Toolformer：让模型自己学会用工具

Schick et al. (2023) 的贡献不是"设计了一个 Agent Loop"，而是证明了**模型可以自学何时调用工具**。

核心方法：在训练语料里插入 API 调用标记，用自监督方式让模型学会在合适位置输出 `[API_search("query")] → result` 这种模式。关键设计：

- **采样 API call**：在文本中随机位置插入 `[API_name(input)]`，调用实际 API，把返回值接在后面
- **自监督过滤**：只保留"插入 API 后模型对后续 token 的困惑度降低"的样本
- **微调**：用过滤后的数据微调模型

这解决了"工具该什么时候用"的问题——但离生产还差很多。

### 1.3 进入生产：Task Loop 的七个工程要求

从 ReAct 到 Task Loop，差距是七个工程维度：

| 维度 | ReAct Demo | 生产级 Task Loop |
|---|---|---|
| 执行模型 | 同步、一次性 | 异步、可恢复、长运行 |
| 状态管理 | 全在上下文里 | 外部持久化 + 按需注入 |
| 错误处理 | 模型自己判断 | 系统级分类+重试+回滚 |
| 终止条件 | 模型说"完成了" | 硬性指标（测试通过/校验过）|
| 资源管控 | 无 | Token/步数/时间/成本预算 |
| 安全隔离 | 无 | 沙箱 + 权限 + 审批 |
| 可观测 | 无 | 全链路 trace + checkpoint |

## 2. 核心工程问题：逐个击破

### 2.1 上下文腐烂（Context Rot）

**问题**：Agent 运行几十步后，history 里塞满 tool result，关键指令被冲淡。

```
第 1 步: [系统指令清晰可见]
第 5 步: [系统指令仍在]
第 20 步: [中间过程淹没一切]
第 50 步: [Agent 忘了最初要干嘛]
```

**解法分层**：

1. **双消息轨**（参考 Hermes）：
```python
# messages：永久历史，保持不变
# api_messages：每次 API 调用前从 messages 临时构造
api_messages = deepcopy(messages)
# 剥离内部字段，注入临时记忆，清洗格式
for msg in api_messages:
    msg.pop("reasoning", None)
    msg.pop("finish_reason", None)
append_memory_context(api_messages[-1])
```

2. **上下文压缩**（三级策略）：
```python
def compress_context(messages, threshold=0.5):
    """当 token 数超 context_window 的 50% 时触发"""
    # Step 1: 预剪枝（零 LLM 成本）
    # - 超长 tool_result → 一行摘要
    # - MD5 去重：同一文件多次 read_file 只留最近一份
    # - 截断超长 tool_call arguments
    # - 历史截图/图片 → 占位文本

    # Step 2: 保护头尾
    # - 头部：保留 system + 前 3 条对话（任务定义）
    # - 尾部：从末尾往前累加 token 直到 ~20% 预算

    # Step 3: LLM 总结中段
    # 中间部分 → 辅助模型生成结构化摘要
    # 第二次以后压缩：要求"保留+追加"而非重写

    # Step 4: 重组防护
    # 摘要前加 [CONTEXT COMPACTION — REFERENCE ONLY] 防模型误读
```

3. **子任务隔离**（Fork Agent）：
```python
def delegate_subtask(goal, context):
    # 子 Agent 拥有：
    # - 独立 messages（不继承父的 history）
    # - 独立迭代预算（默认 50 次 API 调用）
    # - 裁剪后的工具集（最小权限）
    # 只向父 Agent 传回 summary，中间过程不污染父上下文
    child = build_child_agent(goal=goal, tools=subset)
    result = child.run()
    return result.summary  # 不是全部 history！
```

### 2.2 "何时停止"：终止条件设计

模型说"完成了"不能作为唯一终止条件。

```python
class TerminationPolicy:
    """确定性终止判定 """
    MAX_STEPS = 200
    MAX_TOKENS = 10_000_000
    MAX_CLOCK_TIME = 3600 * 4  # 4小时
    
    def should_stop(self, state):
        if state.steps > self.MAX_STEPS:
            return StopReason.BUDGET_EXCEEDED, "步数超限"
        if state.tokens_used > self.MAX_TOKENS:
            return StopReason.BUDGET_EXCEEDED, "Token 超限"
        if elapsed(state.start_time) > self.MAX_CLOCK_TIME:
            return StopReason.TIMEOUT, "超时"
        
        # 硬性验证（不由模型判断）
        if state.phase == "CODING" and not all_tests_pass():
            return StopReason.NOT_READY, "测试未通过"
        if state.phase == "DEPLOY" and not all_checks_pass():
            return StopReason.NOT_READY, "部署检查未通过"
        
        # 模型自报完成 + 验证通过
        if state.model_claims_done and state.verification_passed:
            return StopReason.DONE, "任务完成"
        
        return StopReason.CONTINUE, None
```

关键：**编码任务以测试全过为准，UI 以 Playwright 清单通过为准，数据任务以校验查询通过为准。**

### 2.3 "中间断了怎么办"：任务状态机 + Checkpoint

```
       ┌─────────┐
       │  INIT   │
       └────┬────┘
            ▼
       ┌─────────┐
       │PLANNING │ ◄── 模型拆任务、出计划
       └────┬────┘
            ▼
       ┌─────────┐
  ┌───►│EXECUTING│◄──── Checkpoint 在这里周期性保存
  │    └────┬────┘
  │         ▼
  │    ┌─────────┐
  │    │   QA    │ ◄── 独立验证（不靠模型自评）
  │    └────┬────┘
  │         ├── 通过 ──────────► DONE
  │         ├── 小问题 ────────► FIXING
  │         │    └── 修完 ────► EXECUTING（循环）
  │         └── 高危 ──────────► HUMAN_REVIEW
  │                                  │
  │                             人批准/拒绝
  └──────────────────────────────────┘
```

**Checkpoint 设计核心**：

```python
def save_checkpoint(task):
    """模型对 Checkpoint 零感知——存/取/注入全是 harness 硬编码逻辑"""
    snapshot = {
        "task_id": task.id,
        "state": task.state,           # INIT/EXECUTING/QA...
        "current_step": task.step_idx,
        "plan": task.plan,             # 任务计划
        "completed_features": [
            {"id": "f1", "git_commit": "a1b2c3d", "tests": "pass"},
        ],
        "budget": {
            "tokens_used": 3_200_000,
            "tokens_max": 10_000_000,
        },
        "timestamp": time.time(),
    }
    db.put(f"checkpoint:{task.id}", json.dumps(snapshot))


def start_or_resume(task_id, goal):
    cp = db.get(f"checkpoint:{task_id}")
    if cp:
        task = deserialize(cp)
        # 给模型注入："你之前完成了 Sprint 1-3，现在从 Sprint 4 开始"
        inject_progress_context(task)
        return task
    return Task(goal=goal)


def inject_progress_context(task):
    """只注入模型当下需要的，不是全部 dump"""
    context = f"""## 任务进度
已完成: {task.completed_features}
当前步骤: {task.current_step}
下一步: {task.plan.next()}
## 不要重复已完成的工作"""
    return context
```

**与上下文压缩的本质区别**：

```
压缩：仍在同一会话内，把早期对话总结成摘要
      ↳ 问题：错误可能以摘要形式继续污染
     
Checkpoint：把状态写出模型、交给系统保存，新会话只注入必要片段
      ↳ 优势：重新来过，没有"思维惯性"
```

### 2.4 错误分类与恢复

不要把所有错误字符串塞回上下文让模型自行判断。

```python
class ErrorCategory:
    TEMPORARY = "A"     # 超时、限流 → 指数退避重试
    RETRYABLE = "B"     # 写中间状态失败 → 回滚到上个 checkpoint
    SECURITY = "C"      # 越权访问 → 直接 fail + 触发人工
    LOGIC = "D"         # 代码 bug → 生成详细描述交给修复模块

def handle_error(error):
    cat = classify(error)
    if cat == ErrorCategory.TEMPORARY:
        for attempt in range(3):
            try:
                return retry_with_backoff(attempt)
            except:
                continue
        raise PermanentError("重试耗尽")
    
    elif cat == ErrorCategory.RETRYABLE:
        rollback_to_last_checkpoint()
    
    elif cat == ErrorCategory.SECURITY:
        notify_human(f"安全拦截: {error}")
        raise SecurityViolation(error)
    
    elif cat == ErrorCategory.LOGIC:
        # 生成结构化错误描述，而不是原始错误字符串
        bug_report = {
            "type": "test_failure",
            "test": "test_user_login",
            "error": str(error),
            "likely_cause": "未处理密码为空的边界情况",
        }
        # 交给 Generator 修复
        return generator.fix(bug_report)
```

### 2.5 工具编排与并发安全

```python
# 工具策略表
TOOL_POLICIES = {
    "read_file":    Policy(risk="low",  mutation=False, concurrent=True),
    "search_code":  Policy(risk="low",  mutation=False, concurrent=True),
    "write_file":   Policy(risk="high", mutation=True,  concurrent=False,
                           lock_key=lambda args: args["path"]),
    "run_shell":    Policy(risk="high", mutation=True,  concurrent=False,
                           requires_approval=True),
    "delete_file":  Policy(risk="critical", mutation=True, requires_approval=True),
}

def dispatch_tool_call(agent, tool_name, args):
    policy = TOOL_POLICIES[tool_name]
    
    # 权限检查
    if not policy.allowed_for(agent.role):
        raise SecurityError(f"{agent.role} 不能使用 {tool_name}")
    
    # 并发控制（写操作加锁）
    if policy.mutation:
        lock_key = policy.lock_key(args) if policy.lock_key else tool_name
        if not acquire_lock(lock_key, timeout=30):
            raise TemporaryError("资源被占用，稍后重试")
    
    # 审批流程
    if policy.requires_approval:
        request_approval(tool_name, args)
    
    return execute(tool_name, args)
```

## 3. 三种 Agent Loop 范式对比

| 范式 | 代表 | 适用场景 | 核心特点 |
|---|---|---|---|
| **ReAct** | LangChain Agent | 短任务（几步内完成） | Thought→Action→Observation 交替 |
| **Plan-and-Execute** | BabyAGI, AutoGPT | 可预先规划的任务 | 先出计划 → 按计划逐步执行 |
| **Task Loop (状态机)** | Anthropic, ADP | 长任务、生产级 | 显式状态机 + checkpoint + 独立验证 |

**什么时候用哪种？**

```
ReAct：        查询知识库、简单数据分析（3-5 步内完成）
Plan-and-Execute：调研报告、多步骤分析（步骤可提前规划）
Task Loop：    修改代码仓库、长周期项目（跨 session、需恢复）
```

## 4. 关键论文与参考实现

### 必读论文
- **ReAct** (Yao et al., 2022). "Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629
- **Toolformer** (Schick et al., 2023). "Language Models Can Teach Themselves to Use Tools." arXiv:2302.04761
- **SWE-agent** (Yang et al., 2024). "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering."

### 工程参考
- Anthropic. "Effective harnesses for long-running agents" — 长任务 Agent 设计
- Anthropic. "Scaling Managed Agents: Decoupling the brain from the hands" — 解耦架构
- OpenAI. "The next evolution of the Agents SDK" — Agent 原语设计
- LangChain. "Building LangGraph: Designing an Agent Runtime from first principles"

### 开源代码
- `mini_harness_project/miniharness/agent.py` — 本项目的最小实现
- `github.com/OpenHands/OpenHands` — 完整的 Agent Loop + Sandbox
- `github.com/SWE-agent/SWE-agent` — ACI (Agent-Computer Interface) 设计

## 5. 一句话总结

> Agent Loop 不是"调模型→拿结果"的简单循环，而是**状态机 + 检查点 + 错误恢复 + 资源管控 + 独立验证**的生产级执行引擎。从 ReAct 到 Task Loop，本质是把"让模型自己管自己"逐步替换成"确定性外壳管不确定性内核"。
