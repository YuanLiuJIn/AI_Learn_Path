# 06. Agent 设计模式在 UE5 测试 Agent 中的落地方案

> 基于"Agent = 上下文 × 工具 × 循环"的设计框架，将核心设计模式落地到 UE5 自动化测试 Agent。

## 改进点一：上下文分区

### 改进方案

将 Prompt 拆成五层：

```text
Zone 1：系统区（完全固定，100% Cache）
  角色：UE5 游戏自动化测试 Agent
  规则：必须使用 JSON DSL、必须先规划测试点再生成 JSON
       每个 step 必须包含 timeout、禁止跳过核心断言
  JSON Schema 定义（固定不变）
  约 3-5K tokens

Zone 2：工具区（半固定）
  Action 类型摘要（16 种操作按分类展示）
  按需展开详情（只加载当前场景需要的 Action）
  约 0.5K tokens（摘要模式）

Zone 3：环境区（准静态）
  当前平台、画质档位、可用地图列表、可用 Actor 列表
  约 2-3K tokens

Zone 4：记忆区（长期持久）
  用户偏好、项目特殊行为（quirk）、历史失败模式
  约 1-2K tokens（相关性注入）

Zone 5：对话区（高度动态）
  当前任务需求、已生成的 BDD/测试点、历史步骤（压缩后）
  约 10-30K tokens
```

### 实现要点

```python
class ContextBuilder:
    def build_context(self, task, memory_results, history):
        # Zone 1-2：固定（Cache 友好）
        context = [self.system_zone, self.tool_zone_summary]

        # Zone 3：环境（会话内稳定）
        context.append(self.collect_environment())

        # Zone 4：记忆（相关性注入）
        context.append(self.format_memory(memory_results))

        # Zone 5：对话（动态，放最后）
        context.append(task)
        context.append(history)

        return context
```

**关键**：把稳定的放前面，动态的放后面。

---

## 改进点二：渐进式 Action 发现

```text
第一层：Action 分类摘要（始终在上下文，约 0.3K tokens）
  环境类：load_level, reset_world
  角色类：move_to, interact, attack
  UI 类：click_ui, assert_ui_visible
  状态类：wait_state, assert_quest_state
  性能类：start_perf_capture

第二层：按需展开详情
  根据测试场景，只加载该场景需要的 Action 详情
  例如副本测试：load_level, move_to, interact,
               wait_state, assert_quest_state
  约 1-2K tokens（而非全部 16 种的 5K+）
```

---

## 改进点三：智能失败反馈（四层结构）

```json
{
  "step_id": 6,
  "status": "failed",

  "Level 1：错误事实": {
    "action": "interact",
    "target": "RewardChest",
    "error": "Target not interactable"
  },

  "Level 2：详细分析": {
    "target_exists": true,
    "target_interactable": false,
    "player_distance": 320,
    "required_distance": 150,
    "diagnosis": "玩家距离目标过远"
  },

  "Level 3：修复建议": [
    {
      "type": "insert_step_before",
      "suggested_step": {
        "action": "move_to",
        "params": {"target": "RewardChest", "distance_lte": 120}
      },
      "confidence": 0.91
    }
  ],

  "Level 4：辅助信息": {
    "nearby_actors": ["DungeonGate", "HealthPickup"],
    "player_state": {"health": 85},
    "recent_successful_steps": ["Step 4-5"]
  }
}
```

---

## 改进点四：循环检测升级（三层）

```text
层 1：同操作重复检测
  同一操作 + 同一状态 ≥ 3 次 → 警告

层 2：操作序列模式检测
  最近 10 个操作形成重复模式 → 判定循环

层 3：无进展检测
  最近 5 步游戏状态完全一样 → 死锁
```

---

## 改进点五：Memory 跨会话复用

```text
TEST_MEMORY.md 记录：

失败模式：
  - "RewardChest not interactable"
    → 根因：距离过远
    → 修复：插入 move_to 步骤

项目特殊行为：
  - Dungeon_001 宝箱在 Boss 死后 1.5s 才可交互
    → 建议增加 wait_state

每次测试开始前，检索相关记忆注入上下文。
```

---

## 改进点六：结果智能裁剪

```text
UE 日志裁剪规则：
  1. 保留开头 10 行
  2. 保留结尾 10 行
  3. 提取中间所有 Error/Warning/Crash 行
  4. 明确标注省略了多少行

效果：几千行日志压缩到几十行，关键信息不丢失。
```

---

## 实现优先级

```text
P0（立即做，投入产出比最高）：
  上下文分区 + 智能失败反馈 + 结果裁剪

P1（本周做）：
  Memory 跨会话 + 循环检测升级

P2（下迭代）：
  渐进式 Action 发现
```

## 一句话总结

> 把 Agent 设计模式落到 UE5 测试 Agent 上，核心六件事：上下文分区让 Cache 高效，渐进式 Action 减少 Token 浪费，四层失败反馈让 AI 能自己诊断修复，三层循环检测避免死循环，Memory 跨会话让 Agent 越用越聪明，结果裁剪防止上下文被日志撑爆。
