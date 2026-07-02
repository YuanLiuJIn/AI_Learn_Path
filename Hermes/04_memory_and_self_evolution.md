# 04. 记忆与自进化：Hermes 最独特的差异化能力

> 目标：深入理解 Hermes 如何做到"越用越懂你"——双通路记忆注入、Background Review 暗线、Curator 知识生命周期管理。
> 这是 Hermes 区别于其他 Agent 系统的核心能力。

## 0. 核心问题

```
传统 ChatBot：
  每次对话 = 全新的 Agent = 什么都不记得

理想 Agent：
  上次教过怎么排查日志 → 今天自动调用
  上次说过偏好简短回复 → 今天自动调整
  上次踩过某个工具坑 → 今天自动避开

这不是"更聪明的模型"，而是"有记忆的系统"。
```

## 1. 双通路记忆架构总览

Hermes 的记忆不是"一个数据库存所有东西"，而是精心设计的两条注入路径：

```
┌─────────────────────────────────────────────────┐
│                  记忆系统                        │
│                                                 │
│  路径 A：内置层 → System Prompt                  │
│  ┌─────────────────────────────────────┐        │
│  │ MEMORY.md (Agent 笔记, 2200 字符)    │        │
│  │ USER.md   (用户画像, 1375 字符)      │        │
│  │                                     │        │
│  │ → 会话开始时拍成冻结快照               │        │
│  │ → 注入 System Prompt 的 Volatile 层   │        │
│  │ → 会话中写入不刷新快照（保缓存命中）    │        │
│  │ → 仅在压缩时重建                      │        │
│  └─────────────────────────────────────┘        │
│                                                 │
│  路径 B：外部 Provider → User Message            │
│  ┌─────────────────────────────────────┐        │
│  │ honcho / mem0 / 自定义 Provider       │        │
│  │                                     │        │
│  │ → 每轮对话前语义检索                   │        │
│  │ → 套上 <memory-context> 围栏          │        │
│  │ → 追加到当前 user message 末尾         │        │
│  │ → 不持久化、不污染 System Prompt 缓存   │        │
│  └─────────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
```

## 2. 路径 A：内置记忆层（保缓存 + 快照式）

### 2.1 设计原理

```python
class BuiltinMemory:
    """内置记忆的核心设计：快照式注入 + 延迟刷新"""
    
    MAX_MEMORY_CHARS = 2200     # Agent 笔记
    MAX_USER_CHARS = 1375       # 用户画像
    # 限额是字符数而不是 token 数 → 跨模型时不用重新换算
    
    def __init__(self):
        self.memory_path = "~/.hermes/memories/MEMORY.md"
        self.user_path = "~/.hermes/memories/USER.md"
        self.snapshot = None  # 当前会话的冻结快照
    
    # ====== 会话启动时 ======
    def load_snapshot(self):
        """读文件 → 去重 → 安全扫描 → 拍快照 → 注入 System Prompt"""
        memory_entries = self._read_entries(self.memory_path)
        user_entries = self._read_entries(self.user_path)
        
        # 去重：同一句话不重复存
        memory_entries = list(dict.fromkeys(memory_entries))
        user_entries = list(dict.fromkeys(user_entries))
        
        # 安全扫描（strict 模式：Prompt 注入/代码注入/不可见 Unicode）
        memory_entries = self._threat_scan(memory_entries)
        user_entries = self._threat_scan(user_entries)
        
        # 拍快照（冻结！会话期间不再变化）
        self.snapshot = {
            "memory": "\n§\n".join(memory_entries),  # § 作 entry 分隔符
            "user": "\n§\n".join(user_entries),
        }
    
    def render_for_system_prompt(self):
        """渲染为 System Prompt 片段"""
        return f"""
═══════════════════════════════════════════
MEMORY (your personal notes) [{len(self.snapshot['memory'])}/{self.MAX_MEMORY_CHARS} chars]
═══════════════════════════════════════════
{self.snapshot['memory']}

═══════════════════════════════════════════
USER PROFILE [{len(self.snapshot['user'])}/{self.MAX_USER_CHARS} chars]
═══════════════════════════════════════════
{self.snapshot['user']}
"""
    
    # ====== 会话进行中 ======
    def write_memory(self, content):
        """实时写盘，但绝不刷新快照！"""
        # 原子写入（rename + 文件锁）
        atomic_write(self.memory_path, content)
        # 不调用 self.load_snapshot()！
        # System Prompt 保持原状 → Prompt Cache 持续命中
    
    # ====== 压缩时 ======
    def refresh_snapshot(self):
        """仅在上下文压缩时调用，重建快照"""
        self.load_snapshot()
        # 此时缓存必然失效（System Prompt 变了）
        # 正好一并刷新记忆快照
```

### 2.2 为什么"不立即刷新 System Prompt"？

```
┌─ 如果每次写入记忆都刷新 System Prompt ────────┐
│                                                 │
│  会话 A: System Prompt v1 ─► Cache 命中          │
│  写入新记忆 → System Prompt v2 ─► Cache MISS！   │
│  下一轮 → System Prompt v2 ─► Cache 命中         │
│  写入新记忆 → System Prompt v3 ─► Cache MISS！   │
│  下一轮 → System Prompt v3 ─► Cache 命中         │
│                                                 │
│  结果：频繁的 Cache Miss → 延迟变高、成本变高     │
└─────────────────────────────────────────────────┘

┌─ Hermes 的延迟刷新策略 ─────────────────────────┐
│                                                 │
│  会话 A: System Prompt v1 ─► Cache 始终命中！    │
│  写入新记忆 → 只写磁盘（不影响 System Prompt）    │
│  写入新记忆 → 只写磁盘                           │
│  ... (100 轮后)                                 │
│  上下文压缩触发 → System Prompt v101 ─► 唯一一次 Miss│
│  → 新会话：System Prompt v101 ─► Cache 命中      │
│                                                 │
│  结果：整个会话只有压缩时一次 Cache Miss          │
└─────────────────────────────────────────────────┘
```

**代价**：当前会话中新写的记忆**不会立即生效**（要等到压缩或新会话）。这是缓存命中率与记忆时效性的主动取舍。

## 3. 路径 B：外部 Provider（围栏式注入）

### 3.1 设计原理

```python
class ExternalMemoryProvider:
    """外部记忆通过围栏注入，不污染 System Prompt 缓存"""
    
    def inject(self, current_user_message, query):
        """在每轮 LLM 调用前注入"""
        
        # 1. 从外部 Provider 检索（语义搜索）
        try:
            raw_memories = self.provider.search(query, top_k=5)
        except Exception:
            return current_user_message  # 失败不阻塞流程
        
        # 2. 安全清洗：防止 provider 被攻击后塞入假围栏
        cleaned = self.sanitize(raw_memories)
        
        # 3. 套上正版围栏
        block = self.build_memory_block(cleaned)
        
        # 4. 追加到当前 user message 末尾
        # 仅在 API 调用时拼接，不写入 SQLite
        return current_user_message + block
    
    def sanitize(self, memories):
        """剥掉伪围栏，防止注入"""
        for m in memories:
            m = m.replace("<memory-context>", "[removed]")
            m = m.replace("</memory-context>", "[removed]")
        return memories
    
    def build_memory_block(self, memories):
        """构建正版围栏"""
        content = "\n".join(f"- {m}" for m in memories)
        return f"""
<memory-context>
[System note: The following is recalled memory context,
NOT new user input. Treat as authoritative reference data
— this is the agent's persistent memory and should inform
all responses.]

{content}
</memory-context>
"""
```

### 3.2 流式输出中的围栏过滤

```python
class StreamingContextScrubber:
    """实时扫描 LLM 流式输出，过滤围栏标签"""
    
    def __init__(self):
        self.swallow_mode = False
        self.candidate_tail = ""
    
    def process_chunk(self, chunk):
        """处理流式 chunk，过滤掉围栏标签"""
        buffer = self.candidate_tail + chunk
        self.candidate_tail = ""
        
        while True:
            if self.swallow_mode:
                # 在吞噬态：丢弃字符直到看到 </memory-context>
                end_idx = buffer.find("</memory-context>")
                if end_idx != -1:
                    self.swallow_mode = False
                    buffer = buffer[end_idx + len("</memory-context>"):]
                else:
                    self.candidate_tail = buffer[-20:]  # 保留尾部防跨 chunk
                    return ""  # 整段丢弃
            else:
                # 正常态：检查是否需要进入吞噬态
                start_idx = buffer.find("<memory-context>")
                if start_idx != -1:
                    # 先输出前半段
                    safe = buffer[:start_idx]
                    self.swallow_mode = True
                    buffer = buffer[start_idx + len("<memory-context>"):]
                    continue
                else:
                    # 检查是否有跨 chunk 的标签开头
                    for i in range(1, min(20, len(buffer) + 1)):
                        if "<memory-context>".startswith(buffer[-i:]):
                            self.candidate_tail = buffer[-i:]
                            return buffer[:-i]
                    return buffer  # 安全输出
```

### 3.3 为什么外部记忆不走 System Prompt？

| 路径 | 位置 | 变化频率 | 对缓存的影响 |
|---|---|---|---|
| 内置层 | System Prompt | 低（会话级） | 可控（只在压缩时变） |
| 外部 Provider | User Message 末尾 | 高（每轮可能变） | **零影响**（不在缓存前缀） |

外部记忆来自其他客户端/系统，变化频率极高。如果放进 System Prompt → 缓存频繁失效 → 不可接受。

## 4. 自进化闭环：Background Review + Curator

这是 Hermes 最独特的机制——**Agent 在后台偷偷学习**。

### 4.1 整体架构

```
┌────────────── 主线（用户可见，秒级） ──────────┐
│  用户消息 → Agent Loop → 回复                   │
│            └→ 实时写入 SessionDB（持久化层）     │
└────────────────────┬───────────────────────────┘
                     │ 计数器达阈值
                     ▼
┌── 暗线 1：Background Review（事件触发，分钟级）──┐
│  fork 受限 Review Agent                         │
│  评审本轮对话 → 决定写什么到 MEMORY.md/SKILL.md  │
└─────────────────────────────────────────────────┘
                     │ 独立于主线，定时触发
                     ▼
┌── 暗线 2：Curator（周级，资源空闲时）───────────┐
│  扫描所有 Skill → 归档过时 → 合并重复 → 整理     │
└─────────────────────────────────────────────────┘
```

### 4.2 Background Review 的触发机制

```python
class ReviewTrigger:
    """计数器触发，而非每轮都触发"""
    
    # 记忆审查计数器
    turns_since_memory_review = 0
    MEMORY_REVIEW_INTERVAL = 10  # 每 10 轮用户消息
    
    # 技能审查计数器
    iters_since_skill_review = 0
    SKILL_REVIEW_INTERVAL = 10  # 每 10 次工具调用迭代
    
    def on_user_message(self):
        self.turns_since_memory_review += 1
        if self.turns_since_memory_review >= self.MEMORY_REVIEW_INTERVAL:
            self.trigger_memory_review()
            self.turns_since_memory_review = 0
    
    def on_tool_iteration(self):
        self.iters_since_skill_review += 1
        if self.iters_since_skill_review >= self.SKILL_REVIEW_INTERVAL:
            self.trigger_skill_review()
            self.iters_since_skill_review = 0
    
    # 注意：用户中途打断的 turn 不计数
    # 只有完整完成的 turn 才累加
```

### 4.3 Review Agent 的执行

```python
def spawn_review_agent(conversation_history):
    """fork 一个受限的 Review Agent"""
    
    # 1. 构建 Review Agent（继承父的凭据/provider，但工具严格受限）
    review_agent = Agent()
    review_agent.credentials = parent.credentials
    review_agent.provider = parent.provider
    
    # 2. 工具白名单：只放行 memory 和 skills
    review_whitelist = {
        "memory_add", "memory_replace", "memory_remove",
        "skill_create", "skill_update", "skill_view",
        "skills_list",
    }
    
    # 3. 安全限制
    review_agent.skip_memory = True   # 不向外部 Provider 写入
    review_agent.auto_deny = True     # 所有操作自动拒绝（不需要交互确认）
    
    # 4. 喂入对话历史 + 审查策略提示词
    review_prompt = """Review the conversation above and update TWO things:

**Memory**: 
- Save user preferences, facts, work context
- Save important technical decisions and constraints
- Do NOT save temporary information or conversation turns

**Skills**:
- Update existing umbrella skills rather than creating new ones
- Only create a new skill if there's truly a NEW pattern
- Skills should be: reusable workflow descriptions (what to do, how to check)

Tool permissions: memory (add/replace/remove), skills (create/update/view)
"""
    
    review_agent.run([
        {"role": "user", "content": review_prompt},
        {"role": "user", "content": f"<conversation>\n{conversation_history}\n</conversation>"},
    ])
```

### 4.4 三种审查策略

```python
REVIEW_STRATEGIES = {
    "memory_only": """
        Review the conversation above and consider saving to memory if appropriate.
        Look for:
        - User's role, responsibilities, work context
        - User's communication preferences and style
        - Important technical constraints or environment facts
        - Common troubleshooting patterns the user follows
        """,
    
    "skill_only": """
        Review the conversation above and update the skill library.
        Priority:
        1. Update existing umbrella skills with new insights
        2. Update any skills loaded during this conversation
        3. Only create a new skill if absolutely necessary
        """,
    
    "combined": """
        Review the conversation above and update two things:
        **Memory**: Save user facts/preferences
        **Skills**: Update or create skills based on patterns observed
        """,
}
```

### 4.5 生成示例

```
Background Review 执行后生成的 SKILL.md 示例：

┌────────── .hermes/skills/ ──────────┐
│  my-skill/                          │
│  ├── SKILL.md        ← 主文件（必须）│
│  ├── references/                    │
│  │   └── api.md      ← 参考文档      │
│  ├── templates/                     │
│  │   └── config.yaml ← 输出模板      │
│  └── scripts/                       │
│      └── validate.py ← 可执行脚本    │
└─────────────────────────────────────┘
```

## 5. Curator：知识的生命周期管理

Background Review 负责"产生"知识；Curator 负责"管理"知识。

### 5.1 触发条件

```python
class CuratorScheduler:
    """懒触发：等资源空闲时才运行"""
    
    STATIC_GATE_DAYS = 7          # 至少每 7 天
    IDLE_HOURS = 2                 # Agent 空闲 ≥ 2 小时
    FIRST_RUN_DELAY = True         # 首次不立刻跑，等满一个间隔
    
    def should_run(self):
        if self.last_run is None and self.FIRST_RUN_DELAY:
            return False  # 首次安装后不立刻跑
        
        days_since_last = (now() - self.last_run).days
        if days_since_last < self.STATIC_GATE_DAYS:
            return False  # 还没到 7 天
        
        if agent_idle_time() < self.IDLE_HOURS * 3600:
            return False  # Agent 还在忙
        
        return True  # 双闸门都通过，可以运行
```

### 5.2 核心功能 1：时间维度状态流转

```python
# 纯规则驱动的状态机，不消耗 LLM token
SKILL_STATE_RULES = {
    "active": {
        "unused_days": 30,
        "next_state": "stale",
        "auto_renew": True,  # 被重新使用 → 恢复 active
    },
    "stale": {
        "unused_days": 90,
        "next_state": "archived",
        "auto_renew": True,  # 被重新使用 → 恢复 active
    },
    "archived": {
        # 终点状态，不可自动恢复
        # 移入 .archive/ 目录
    },
}

def run_state_transitions(skills):
    for skill in skills:
        days_unused = (now() - skill.last_used).days
        rule = SKILL_STATE_RULES[skill.state]
        
        if days_unused > rule["unused_days"]:
            skill.state = rule["next_state"]
            
            if skill.state == "archived":
                shutil.move(skill.path, f".archive/{skill.name}")
                log(f"Archived skill '{skill.name}' (unused for {days_unused} days)")
```

### 5.3 核心功能 2："伞状合并"（LLM 驱动）

Background Review 一次只看一轮对话 → 容易产生窄而碎的 Skill。
Curator 扫描所有 Skill → 把相似的合并成通用"伞状 Skill"。

```python
def consolidate_skills(skills):
    """合并碎片化的 Skill"""
    
    # 1. 收集所有 Agent 创建的 Skill
    report = agent_created_report(skills)
    # report 包含：skill 名称、创建时间、使用频率、描述
    
    # 2. Fork 独立 Agent 做合并分析
    plan = llm.analyze(report, instruction="""
    Analyze these skills and propose consolidation:
    
    For skill clusters (similar purpose/domain):
    1. MERGE into existing umbrella skill (if one exists)
    2. CREATE new umbrella skill (for new clusters)
    3. DEMOTE to references/templates/scripts sub-files
    
    Output structured YAML:
    ```yaml
    consolidations:
      - action: merge
        umbrella: server-debug
        skills: [server-debug-apache, server-debug-nginx, server-debug-express]
        reason: "All share the same workflow: check logs → check status → check config → restart"
      
      - action: create
        umbrella: db-migration
        skills: [db-migration-check, db-migration-rollback]
        reason: "New domain cluster with reusable workflow"
    ```
    """)
    
    return plan
```

### 5.4 安全兜底

```python
class CuratorGuard:
    """即使 Curator 出错，也要保证用户能恢复"""
    
    def pre_run_backup(self):
        """每次真实运行前，自动打快照"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f".backups/skills_{timestamp}"
        shutil.copytree("~/.hermes/skills/", backup_dir)
    
    def dry_run(self):
        """预览模式：只生成 REPORT.md，不做实际变更"""
        plan = self.analyze()
        with open("REPORT.md", "w") as f:
            f.write("# Curator Dry Run Report\n\n")
            f.write(f"## Skills to Archive ({len(plan.archivals)})\n")
            for a in plan.archivals:
                f.write(f"- {a.name}: unused for {a.days} days\n")
            f.write(f"\n## Skills to Consolidate ({len(plan.consolidations)})\n")
            for c in plan.consolidations:
                f.write(f"- {c.action}: {c.description}\n")
        print(f"Dry run complete. See REPORT.md. Run without --dry-run to apply.")
```

## 6. 安全体系：记忆的防线

记忆是 Hermes 最敏感的部分——它注入 System Prompt，跨会话持久化，一旦被污染影响极大。

```python
class MemoryGuard:
    """三道安全防线"""
    
    # 防线 1：写入时威胁扫描
    def scan_on_write(self, content):
        threats = [
            r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",  # 提示词注入
            r"(?i)you\s+are\s+now\s+DAN",                                   # 角色劫持
            r"curl.*\|.*(?:bash|sh|python)",                                 # 代码注入
            r"(?:ghp_|sk-|AKIA)[a-zA-Z0-9]{20,}",                           # 凭证泄露
            r"零宽空格|\u200b|\u200d|\ufeff",                                # 不可见 Unicode
        ]
        for pattern in threats:
            if re.search(pattern, content):
                raise ThreatDetected(f"Blocked by pattern: {pattern}")
    
    # 防线 2：加载时二次扫描
    def scan_on_load(self, entries):
        clean = []
        for entry in entries:
            try:
                self.scan_on_write(entry)
                clean.append(entry)
            except ThreatDetected as e:
                clean.append(f"[BLOCKED: {e.pattern_name}]")
                # 实时状态保留原文，用户可通过 memory(action=read) 看到并手动清理
        return clean
    
    # 防线 3：外部 drift 检测
    def check_external_drift(self):
        """检查磁盘文件是否被外部进程（patch 工具、shell 脚本）修改过"""
        on_disk = self._read_raw("MEMORY.md")
        if is_corrupted(on_disk):
            backup_path = f"MEMORY.md.bak.{int(time.time())}"
            shutil.move("MEMORY.md", backup_path)
            raise DriftDetected(f"Corrupted memory file. Saved backup to {backup_path}")
```

## 7. 局限性

| 局限 | 说明 |
|---|---|
| **"保量不保质"** | 长对话下 Background Review 可能抓不住重点，生成的 Skill 不够精炼 |
| **模型依赖** | 自进化质量完全取决于底层模型能力（弱模型生成的 Skill 可能不可用） |
| **触发频率有限** | 记忆审查每 10 轮触发一次，技能审查每 10 次工具迭代触发一次 |
| **记忆容量偏小** | 总计 ~1300 tokens，长期使用后旧知识会被覆盖 |

Hermes 团队对这些局限有清晰认知：**记忆容量是容量 vs 成本的主动取舍，不是实现缺陷。**

## 8. 一句总结

> 记忆系统 = 双通路注入（内置层保缓存 + 外部 Provider 灵活检索）。自进化闭环 = Background Review（暗线复盘） + Curator（知识清理合并）。核心哲学：**让 Agent 偷感很重地在后台学习，用户可以无感地享受到一个越来越懂自己的助手。**
