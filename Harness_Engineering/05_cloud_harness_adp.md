# 云端 Harness：ADP 的设计实践

> 本文目标：以腾讯云 ADP 智能体平台为案例，展示 Harness Engineering 在云端企业级场景的设计考量。
> 核心问题：当 Agent 从"程序员本机的 CLI"变成"云上的托管服务"，架构要做什么改变？

## 0. 先建立直觉：客户端 vs 云端 Harness

业界最早的 Agent Harness（Claude Code、Codex CLI）把全部能力打包在一个容器/CLI 里：

```
┌──────── 客户端 Agent 容器 ────────┐
│  Agent Loop                        │
│  Memory（SQLite）                  │
│  Sandbox（同一个容器里跑命令）       │
│  Tools（进程内直接执行）            │
└────────────────────────────────────┘
```

这在个人开发机上工作良好，但进入生产级场景立刻暴露出问题。

### 客户端的六大痛点（来自 Anthropic Managed Agents 论文）

| 痛点 | 原因 | 后果 |
|---|---|---|
| **容器变成"宠物"** | 状态/harness/执行环境全在一个容器里 | 容器不能随便销毁，只能小心维护 |
| **失败恢复困难** | 任务历史和状态都在容器内部 | 容器崩溃 = 状态丢失，新进程无法接管 |
| **调试风险高** | 工程师排障需进入用户容器 | 容器里有用户代码/数据，安全合规风险 |
| **安全边界模糊** | 代码/执行环境/凭证都在同一个容器 | Prompt injection 可读到环境变量/token |
| **扩展性差** | 每个 session 绑定一个容器 | 即使没任务也要启动容器，延迟高 |
| **Harness 难演进** | harness 和容器/session 强绑定 | 上下文管理策略升级牵动底层环境 |

## 1. ADP 的方案：云端解耦设计

### 1.1 核心设计思路

```
ADP 把每一层都拆成独立服务：

┌──────────────────────────────────────────┐
│  用户/API 请求                            │
└──────────────┬───────────────────────────┘
               ▼
┌──────────────────────────────────────────┐
│  Agent Loop（独立服务，可弹性扩缩）        │
│  - 状态机驱动执行                         │
│  - 异步化设计（AGUI 事件协议）             │
│  - 断线重连、过程恢复                     │
└──────┬──────────┬──────────┬─────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌──────────────┐
│  Memory  │ │ Tools  │ │  Sandbox     │
│ (独立存储)│ │(独立服务)│ │ (AGS Cube)   │
└──────────┘ └────────┘ └──────────────┘
```

解耦前与解耦后的对比：

| 维度 | 解耦前（客户端） | 解耦后（云端 ADP） |
|---|---|---|
| **恢复能力** | Agent Loop/Session/Memory/Sandbox 同容器，挂了就丢 | Session & Memory 独立持久化，崩溃后通过 SessionId 重读历史继续 |
| **安全边界** | 代码/凭证/用户数据混在一起 | Sandbox 只隔离执行，凭证放 Vault/Proxy 中，敏感信息不进执行环境 |
| **扩展性** | 每 session 绑定一个容器 | 各组件独立扩缩，只执行时才创建 Sandbox |
| **运维复杂度** | 容器变"宠物"，排障需侵入 | Sandbox 可重建可替换，问题更易隔离 |
| **演进能力** | 升级模型/harness 牵动底层 | 通过稳定接口连接，策略独立升级 |

### 1.2 Agent Loop：任务驱动的自动续跑

ADP 的 Agent Loop 不是简单的"调模型→执行→回填→再调"循环。

```python
class ADP_AgentLoop:
    """ADP 的状态机驱动 Agent Loop"""
    
    def run(self, session_id, user_message):
        # 1. 恢复或创建 Session
        session = SessionManager.get_or_create(session_id)
        
        # 2. 进入状态机
        state = StateMachine(session.last_state or State.INIT)
        
        while state != State.DONE and state != State.FAILED:
            # 3. 构建上下文（注入 Memory + Todo + Progress）
            context = self.build_context(session, state)
            
            # 4. 模型决策
            response = self.llm.chat(context)
            
            # 5. 工具调用处理
            if response.has_tool_calls():
                for call in response.tool_calls:
                    if call.name == "AgentTool":  # 委派子 Agent
                        result = self.spawn_subagent(call.args)
                    else:
                        result = self.tool_service.execute(call)
                    session.append_tool_result(call, result)
                
                # 6. Checkpoint 检查
                if session.should_checkpoint():
                    session.save_checkpoint()
                
                # 7. 续跑判定
                if session.is_long_running():
                    # 任务未完成 → 挂起，异步续跑
                    self.schedule_continuation(session)
                    return {"status": "running", "session_id": session.id}
            
            # 8. 状态转移
            state = state.next(response)
        
        return {"status": "done", "result": response.content}
```

**关键差异**：

1. **异步执行**：不要求客户端一直连着。Agent 在后台跑，客户端通过 session_id 轮询进度
2. **AGUI 事件协议**：流式回传状态和结果，支持断线重连
3. **任务驱动续跑**：不是"跑一轮就结束"，而是围绕任务状态持续推进

### 1.3 Sandbox：基于 AGS Cube 的安全沙箱

```python
# ADP Sandbox 的关键设计

class AGSSandbox:
    """内核级强隔离 + 极速启动 + 自动暂停/恢复"""
    
    def create(self, session_id):
        # 1. 基于 AGS Cube 创建独立 Guest OS 实例
        # 2. 100ms 级冷启动（镜像预热）
        instance = AGS.create_instance(
            image="agent-runtime:v2",
            isolation="kernel",  # 内核级隔离
            network="restricted",
        )
        
        # 3. 凭证零落地
        # 环境变量里的只是占位符，真凭证在可信域
        instance.set_env("API_KEY", "PLACEHOLDER_ONLY")
        # 真实调用通过 proxy 转发，沙箱内进程拿不到真值
        
        return instance
    
    def pause_resume(self, instance):
        """空闲超 5 分钟自动暂停，调用时自动恢复"""
        # 进程级快照：恢复时进程/内存/依赖原样保留
        # 不消耗计算资源但保持状态
        if instance.idle_time > 300:
            instance.pause()  # 进程快照保存
    
    def cleanup(self, instance):
        """长期不使用自动销毁，workspace 数据打包到 COS"""
        if instance.idle_time > 86400:  # 24h
            workspace_data = instance.pack_workspace()
            COS.upload(f"workspace/{session_id}", workspace_data)
            instance.destroy()
    
    def restore(self, session_id):
        """新 session 自动从 COS 恢复 workspace"""
        data = COS.download(f"workspace/{session_id}")
        instance = AGS.create_instance(data)
        return instance
```

**Sandbox 设计四原则**：
- 默认隔离、最小权限
- 动作可追踪
- 失败可恢复
- 不把 Agent 的手脚绑死

### 1.4 Tools：从进程内嵌到独立服务

ADP 做的最独特的设计是 **HTTP-as-Boundary**——把工具执行从 Agent 进程里抽离成独立 HTTP 服务：

```python
# 传统做法（LangChain/进程内）：
@tool
def read_file(path):  # 直接定义在 Agent 进程里
    return open(path).read()

# ADP 做法（工具执行独立服务）：
# Agent 通过 HTTP 调用工具服务
POST https://codetool.internal/execute
{
  "tool": "read_file",
  "args": {"path": "/workspace/src/app.ts"},
  "session_id": "sess_abc123"
}

# 工具服务独立于 Agent Loop：
# - 独立扩缩容
# - 独立安全策略
# - 独立升级
# - 多个 Agent 框架共享同一套工具
```

这带来的好处：
- **跨语言**：Agent 可以用任何语言，通过 HTTP 调同一套工具
- **跨部署**：工具服务独立扩缩/升级/安全策略
- **可复用**：多个 Agent 框架共享同一套工具实现

**并发安全：Read-before-Write + mtime 防覆盖**

```python
class FileStateCache:
    """工具执行层的并发安全契约"""
    
    def read(self, path):
        content = open(path).read()
        stat = os.stat(path)
        self.cache[path] = {
            "content": content,
            "mtime": stat.st_mtime,
            "size": stat.st_size,
        }
        return content
    
    def write(self, path, content):
        # 强制 Read-before-Write：必须先读过才能写
        if path not in self.cache:
            raise SecurityError(f"Must read '{path}' before writing")
        
        # mtime 防覆盖：读过之后文件被人改过 → 拒绝
        current_mtime = os.stat(path).st_mtime
        if current_mtime != self.cache[path]["mtime"]:
            raise ConcurrentModificationError(
                f"File '{path}' was modified externally since last read"
            )
        
        # 执行写入
        atomic_write(path, content)
        
        # 更新缓存
        self.cache[path]["mtime"] = os.stat(path).st_mtime
```

### 1.5 安全体系：三级分层权限

```
┌──────────────────────────────┐
│  企业级（Enterprise）        │
│  - 可使用的模型列表           │
│  - 网络出口策略               │
│  - 数据驻留区域               │
├──────────────────────────────┤
│  空间级（Workspace）          │
│  - 工具白名单                 │
│  - 存储配额                   │
│  - 成员角色与权限             │
├──────────────────────────────┤
│  应用级（Application/Agent）  │
│  - AgentType 能力边界         │
│  - MCP 连接白名单             │
│  - 执行环境配置               │
└──────────────────────────────┘
```

多 Agent 安全设计：
- **AgentType 工具隔离**：Explore 禁止 Edit/Write，Verification 只读
- **Fresh Subagent 零上下文**：新 Agent 不自动继承主会话全部上下文
- **凭证不落地沙箱**：真实凭证只在可信域

### 1.6 可观测性：全链路 Transcript

```python
class Transcript:
    """完整的执行轨迹"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.entries = []  # 每一步的完整记录
    
    def record_llm_call(self, messages, response, tokens, cost):
        self.entries.append({
            "type": "llm_call",
            "timestamp": now(),
            "model": response.model,
            "input_tokens": tokens.input,
            "output_tokens": tokens.output,
            "cost": cost,
        })
    
    def record_tool_call(self, tool_name, args, result, duration):
        self.entries.append({
            "type": "tool_call",
            "tool": tool_name,
            "args": args,
            "result_summary": summarize(result, max_chars=500),
            "duration_ms": duration,
        })
    
    def record_error(self, error, context):
        self.entries.append({
            "type": "error",
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
        })
    
    def to_replay(self):
        """生成可回放的完整轨迹（用于调试/审计/评估）"""
        return json.dumps(self.entries)
```

## 2. ADP 的使用模式

### 模式 1：智能工作台（开箱即用）

面向 Agent 使用者，在 ADP 控制台配置 Agent → 发布 → 使用。无需编程。

### 模式 2：Claw 模式（API 集成）

面向开发者，分两种集成方式：

**方式 A：只集成对话 API**（最简单）

```
企业业务系统 --HTTP--> ADP 对话接口
                          │
                   ADP 平台管理 Agent 配置/技能/MCP/提示词/发布
```

适用于：企业没计划自建平台，只想把 Agent 嵌入业务系统。

**方式 B：全部 API 集成**（最灵活）

```
企业自有平台 --配置端 API--> ADP 管控面（创建/配置/发布 Agent）
企业自有平台 --运行时 API--> ADP 数据面（对话/执行）
```

适用于：企业要开发自己的智能体平台，需要把 Agent 创建/配置/发布能力集成进自身产品。

## 3. 与其他 Harness 的对比

| | Claude Code CLI | ADP 云端 | Hermes | OpenClaw |
|---|---|---|---|---|
| 部署形态 | 本地容器 | 云端服务 | 本地 + Gateway | 本地 + Gateway |
| Agent Loop | 进程内同步 | 异步状态机 | 同步内核 | 同步 |
| 记忆 | 无内置 | 四层记忆架构 | 双通路自进化 | 插件化手动配置 |
| 沙箱 | 同容器 | 独立 AGS Cube | 子 Agent 隔离 | Git worktree |
| 多 Agent | Subagent | Subagent + Agent Team(WIP) | delegate_task + Kanban | spawn/send |
| 适用场景 | 个人开发 | 企业级平台 | 个人长期助手 | 多 Agent 协作 |

## 4. 一句话总结

> 云端 Harness 的本质是把 Agent 的"大脑"（Agent Loop）、"手"（Tools）、"记忆"（Memory）、"安全笼"（Sandbox）全部解耦成独立可伸缩的云服务——让 Agent 从"程序员本机的一次性脚本"变成"企业级的托管智能体平台"。

## 5. 参考

- Anthropic. "Scaling Managed Agents: Decoupling the brain from the hands" (2025)
- ADP 产品文档: https://adp.cloud.tencent.com/adp/
- ADP API 文档: https://cloud.tencent.com/document/product/1759
