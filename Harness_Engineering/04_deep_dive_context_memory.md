# 上下文与记忆系统：Agent 的"工作记忆"与"长期记忆"

> 本文目标：深入理解 Harness 中上下文管理和记忆系统的工作原理与工程实现。
> 核心问题：有限的 token 窗口怎么高效组织？跨会话信息如何持久化？

## 0. 先建立直觉

Agent 面对的核心矛盾：

```
模型的上下文窗口 = 有限的 token 预算（如 200K）
但 Agent 需要的信息 = 无限增长（历史对话、工具结果、项目知识、用户偏好...）

解决之道：不是"什么都喂给模型"，
而是"在正确的时间，把正确的信息，以正确的形式，放进上下文"
```

类比：
- **上下文 = RAM**（工作记忆，当前任务需要的信息）
- **记忆系统 = 硬盘**（长期存储，需要时检索加载）
- **上下文压缩 = 虚拟内存**（RAM 满了就把部分内容 swap 到磁盘）

## 1. 上下文管理：把有限窗口用满有效信息

### 1.1 System Prompt 的分层设计（最大化 Prompt Cache 命中率）

现代 LLM API（如 Anthropic Claude）支持 **Prompt Cache**：如果 prompt 前缀不变，后续调用可以复用缓存，**大幅降低延迟和成本**。

因此，System Prompt 应**按变化频率从小到大排列**：

```text
┌─────────────────────────────────────────┐
│  Stable 层（整个会话不变）              │
│  - 人格定义（SOUL.md / 核心角色）        │
│  - 工具使用行为指导                      │
│  - 环境提示                              │
├─────────────────────────────────────────┤
│  Context 层（进一个项目就固定）          │
│  - AGENTS.md / CLAUDE.md / .cursorrules  │
│  - 项目架构说明                          │
│  - 编码规范                              │
├─────────────────────────────────────────┤
│  Volatile 层（会话级 / 日级精度）        │
│  - MEMORY.md 冻结快照（Agent 笔记）      │
│  - USER.md 冻结快照（用户画像）          │
│  - 当前时间戳                            │
└─────────────────────────────────────────┘
```

**关键设计**：
- Stable + Context 层字节级稳定 → Prompt Cache 持续命中
- Volatile 层只在必要时机刷新（不是每轮都重建）
- 整个会话只建一次 System Prompt，只有**压缩时才重建**

### 1.2 上下文压缩：三级流水线

```python
def compress(messages, threshold=0.5):
    """
    threshold: 达到 context_window 的 50% 触发
    """

    # ====== Step 1: 预剪枝（零 LLM 成本）====== 
    for msg in messages:
        # 超长 tool_result → 一行摘要
        if msg.role == "tool" and len(msg.content) > 200:
            msg.content = f"[Tool output: {len(msg.content)} chars, type={msg.tool_type}]"
        
        # MD5 去重：同一文件多次读取 → 只保留最近一份
        if msg.tool_name == "read_file":
            path = msg.tool_args["path"]
            if seen_files.get(path):
                msg.content = "[Duplicate read_file output — see most recent above]"
        
        # 历史截图/图片 → 占位文本
        if msg.has_image():
            msg.content = "[Image removed during compression]"

    # ====== Step 2: 保护头尾 ====== 
    # 头部：system + 前 3 条对话（任务定义和初始上下文）
    head = messages[:4]
    
    # 尾部：从末尾往前累加至 ~20% token 预算
    tail = []
    tail_tokens = 0
    budget = context_limit * threshold * 0.2
    for msg in reversed(messages):
        if tail_tokens + msg.token_count > budget:
            break
        tail.insert(0, msg)
        tail_tokens += msg.token_count
    
    # 必须包含最近的 user 消息
    if not any(m.role == "user" for m in tail):
        last_user = last_user_message(messages)
        tail.insert(0, last_user)

    # ====== Step 3: LLM 总结中段 ====== 
    middle = messages[len(head):-len(tail)]
    if not middle:
        return head + tail  # 没什么可压缩的
    
    summary = auxiliary_llm.summarize(middle, instruction="""
    保留以下关键信息：
    - 正在进行中的任务和进度
    - 尚未解决的错误
    - 用户明确表达的需求和偏好
    - 重要的工具调用结果
    忽略：
    - 重复的工具输出
    - 已完成的步骤细节
    """)

    # ====== Step 4: 重组防护 ====== 
    return [
        *head,
        {"role": "system", "content": f"[CONTEXT COMPACTION — REFERENCE ONLY]\n{summary}\n--- END OF CONTEXT SUMMARY ---"},
        *tail,
    ]
```

### 1.3 压缩防抖策略

```python
COMPRESSION_GUARD = {
    "min_window": 64000,     # 低于 64K token 不触发（大窗口时代防过早触发）
    "threshold": 0.5,        # 超过 50% 上下限触发
    "anti_flap": 0.10,       # 连续两次压缩节省 < 10% → 停止自动压缩
    "cooldown": 600,         # 压缩失败后 600 秒冷却
}
```

### 1.4 压缩 vs Handoff：两种交接策略

| | 上下文压缩 (Compaction) | 结构化交接 (Handoff) |
|---|---|---|
| 机制 | 同一会话内对早期对话做摘要 | 清空历史，用结构化文档传递状态 |
| 连续性 | 好（思维连续） | 差（重新来过） |
| 错误传播 | 高（错误可能以摘要形式保留） | 低（干净 slate，无"思维惯性"） |
| 适用 | 短-中任务、上下文尚可 | 长任务、多阶段、需要"重启" |

**Handoff 文档示例**（Anthropic 模式）：

```json
{
  "session_id": "abc123",
  "reason": "context_reset",
  "completed_features": [
    {"id": "feat-login", "git_commit": "a1b2c3d", "tests": "pass", "deployed": false}
  ],
  "current_feature": "feat-dashboard",
  "known_issues": [
    {"description": "DatePicker 在 Safari 下样式异常", "severity": "low"}
  ],
  "technical_decisions": [
    {"what": "状态管理选用 Zustand 而非 Redux", "why": "减少样板代码"}
  ],
  "next_steps": ["实现 dashboard 数据查询", "编写仪表盘单元测试"],
  "test_commands": ["npm test -- --coverage"],
  "important_files": ["src/components/Dashboard.tsx", "src/api/dashboard.ts"]
}
```

## 2. 记忆系统：从"一次性对话"到"越用越懂你"

### 2.1 记忆的本质问题

```
问题 1 — 存什么：    与"这次对话"无关的长期知识
                      （用户偏好、项目约定、历史经验）

问题 2 — 何时存：    判断哪些信息未来有价值
                      （不是所有对话都值得记忆）

问题 3 — 怎么取：    检索时要准确、相关、不过量
                      （取不到关键记忆或取出无关旧信息都是失败）

问题 4 — 如何更新：  记忆会过期，需要版本管理和遗忘机制

问题 5 — 安全可信：  不能跨用户/项目污染记忆
```

### 2.2 双通路记忆注入架构

参考 Hermes 的实践，记忆通过两条路径注入上下文：

**路径 A：内置层 → System Prompt（快照式，保缓存命中）**

```python
class BuiltinMemoryProvider:
    """将 MEMORY.md / USER.md 以冻结快照注入 System Prompt"""
    MAX_MEMORY_CHARS = 2200    # ~1300 tokens
    MAX_USER_CHARS = 1375
    
    def inject(self, system_prompt):
        memory = self.load("MEMORY.md")
        user = self.load("USER.md")
        
        # 去重
        memory = self.dedup(memory)
        
        # 安全扫描
        if self.threat_scan(memory) == "dangerous":
            memory = "[BLOCKED: suspicious content detected]"
        
        # 渲染为 System Prompt 片段（保持不变直到压缩）
        snapshot = f"""
═══════════════════════════════════════════
MEMORY (your personal notes) [{len(memory)}/{self.MAX_MEMORY_CHARS} chars]
═══════════════════════════════════════════
{memory}
═══════════════════════════════════════════
USER PROFILE [{len(user)}/{self.MAX_USER_CHARS} chars]
═══════════════════════════════════════════
{user}
"""
        return system_prompt + snapshot
    
    def write(self, content):
        """写入时实时落盘，但不刷新 System Prompt 快照"""
        atomic_write("MEMORY.md", content)  # rename + 文件锁
        # 当前会话不刷新！只有压缩时才重建 System Prompt
    
    def refresh_snapshot(self):
        """仅压缩时调用，重新加载文件并重建快照"""
        return self.inject(self.base_system_prompt)
```

**路径 B：外部 Provider → User Message（围栏式，不污染缓存）**

```python
class ExternalMemoryProvider:
    """通过 <memory-context> 围栏注入到当前轮 user message 末尾"""
    
    def inject(self, current_user_message, query):
        # 从外部 provider 检索相关记忆（honcho, mem0, 向量数据库...）
        memories = self.provider.search(query, top_k=5)
        
        if not memories:
            return current_user_message
        
        # 安全清洗
        memories = self.sanitize(memories)  # 去污染
        
        # 套上围栏
        block = f"""
<memory-context>
[System note: The following is recalled memory context, 
NOT new user input. Treat as authoritative reference data.]

{chr(10).join(f'- {m}' for m in memories)}
</memory-context>
"""
        return current_user_message + block
    
    def sanitize(self, memories):
        """防止 provider 被攻击后预先包好假围栏"""
        for m in memories:
            m = m.replace("<memory-context>", "")
            m = m.replace("</memory-context>", "")
        return memories
```

### 2.3 自进化闭环：Background Review + Curator

这是 Hermes 最具特色的设计——Agent 不自知地自我进化。

```
┌────────── 主线（实时） ──────────┐
│  用户对话 → Agent 回复           │
└──────────────┬───────────────────┘
               │ 计数器达阈值 + turn 正常完成
               ▼
┌──────── 暗线 1：Background Review ────────┐
│ fork 受限 Review Agent（只能操作 memory + skills）│
│ 回看刚结束的对话 → 自主决定：                   │
│   - 是否把用户偏好写入 MEMORY.md？             │
│   - 是否从本次交互提炼成 Skill？                │
│   - 是否更新已有 Skill？                        │
└──────────────────────────────────────────────┘
               │ 独立于主线的定时调度
               ▼
┌──────── 暗线 2：Curator（周级） ────────────┐
│ 知识的生命周期管理：                           │
│   - active（活跃） ──30天没用──▶ stale（陈旧） │
│   - stale ──90天没用──▶ archived（归档）       │
│   - 合并零散 Skill → "伞状 Skill"              │
└──────────────────────────────────────────────┘
```

**Background Review 的三种策略提示词**：

| 审查类型 | 作用 | 核心提示 |
|---|---|---|
| MEMORY_REVIEW | 提取用户偏好/事实 | "review the conversation above and consider saving to memory if appropriate" |
| SKILL_REVIEW | 提炼可复用流程 | "update the skill library. Prefer updating existing umbrella skills over creating new ones" |
| COMBINED_REVIEW | 同时做上面两件事 | "review and update two things: Memory and Skills" |

**触发机制**：
- 记忆审查：每 10 轮完整用户消息触发一次
- 技能审查：每 10 次工具调用迭代触发一次
- 用户中途打断的 turn 不计入

### 2.4 Curator：记忆的生命周期

不是 Background Review 产出了就完事——随着时间推移，记忆会碎片化。

```python
class Curator:
    """知识的生命周期管理（周级运行）"""
    
    STATE_RULES = {
        "active":  {"unused_days": 30,  "next": "stale"},    # 30天没用→陈旧
        "stale":   {"unused_days": 90,  "next": "archived"}, # 90天没用→归档
        "archived": None,                                      # 不可自动恢复
    }
    
    def run(self, skills_dir):
        # 1. 状态流转（纯规则，不调 LLM）
        for skill in self.list_skills(skills_dir):
            days_unused = (now() - skill.last_used).days
            new_state = self.transition(skill.state, days_unused)
            if new_state != skill.state:
                skill.state = new_state
                if new_state == "archived":
                    shutil.move(skill.path, f".archive/{skill.name}")
        
        # 2. 伞状合并（调 LLM 评审）
        # Background Review 每次只看一轮对话，容易产生窄而碎的 Skill
        # Curator 扫所有 Skill，把相似的合并成"伞状 Skill"
        report = self.list_agent_created_skills()
        consolidation_plan = llm.analyze(report, instruction="""
        扫描以下技能列表，按前缀簇分组：
        - MERGE 已有伞状 Skill：如果碎片能被现有伞状 Skill 吸收
        - CREATE 新伞状 Skill：如果出现新的技能簇
        - DEMOTE：窄技能降级为 references/templates 子文件
        """)
```

**安全兜底**：

```python
# 跑前自动快照
backup_dir = f".backups/{datetime.now().isoformat()}"
shutil.copytree("skills/", backup_dir)

# dry-run 模式
hermes curator run --dry-run  # 只生成 REPORT.md，不做实际变更
```

## 3. ADP 的云端记忆架构

腾讯云 ADP 平台提出了云端解耦的四层记忆架构：

```
┌──────────────────────────────────┐
│  Layer 4: 长期记忆（跨会话）     │
│  - 用户偏好、反馈风格、项目背景   │
│  - 按用户维度跨 Session 召回     │
│  - 异步增量提取（不阻塞主链路）   │
├──────────────────────────────────┤
│  Layer 3: Session Memory        │
│  - 会话级智能压缩（后台异步）     │
│  - 已就绪的摘要直接消费（毫秒级） │
├──────────────────────────────────┤
│  Layer 2: 同步压缩               │
│  - 在线压缩对话历史              │
│  - 保留关键信息                  │
├──────────────────────────────────┤
│  Layer 1: 基础上下文（Part/Message/Session）│
│  - Part 为最小语义单元            │
│  - 完整保留多模态消息流           │
└──────────────────────────────────┘
```

核心设计原则：
- **提取与召回解耦**：写入异步增量提取，读取由 Agent 按需主动召回
- **全链路可溯源**：命中结果保留来源会话、run ID 等元信息
- **多租户隔离**：Memory Resource 作为顶层租户单元

## 4. 关键论文

| 论文 | 贡献 |
|---|---|
| **Lost in the Middle** (Liu et al., 2023) | 模型注意力呈 U 型曲线——上下文中间信息最容易被忽略 |
| **MemGPT** (Packer et al., 2023) | 把操作系统虚拟内存思想引入 LLM 上下文管理 |
| **RAPTOR** (Sarthi et al., 2024) | 树状摘要结构，分层检索 |
| **Anthropic Context Engineering** (2025) | System Prompt 分层 + Prompt Cache 策略 |

## 5. 一句话总结

> 上下文管理是"有限窗口里的信息组织学"，记忆系统是"知识的生长与新陈代谢"。核心原则：**把变化频率低的信息放前面（保缓存），把不紧急的信息异步处理（不阻塞），把确定性约束放代码不放 prompt（保可靠）。**
