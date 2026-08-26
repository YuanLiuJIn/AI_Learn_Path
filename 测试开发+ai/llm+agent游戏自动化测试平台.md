# UE 模式 AI 自动化测试平台（类 Acorn）

> 一份面向游戏质量保障的 AI 自动化测试平台设计与可运行原型。核心思想：测试代码与 UE 游戏源码之间，**不依赖截图/图像匹配**，而是通过开发期预留的测试/调试接口 + **自研 RPC 协议**交换**结构化状态**，把 Acorn AI 的"观察—执行—断言"工程闭环落地到虚幻引擎工作流。

---

## 0. 项目概览

### 0.1 背景与痛点
- 中大型游戏版本迭代快，QA 人力无法线性扩张；传统自动化脚本在 UI 改版、控件重命名后批量失效，维护成本超线性增长。
- 纯视觉（Airtest/Sikuli）与多模态 VLM 方案受分辨率、皮肤、遮挡、语言影响，难以保证工业级确定性。
- 通用 VLA/游戏 Agent 虽有探索能力，但在稳定性、可控性、结果验证上难以直接支撑生产级回归。

### 0.2 目标
构建一个**类 Acorn 的 AI 自动化测试平台**：用"结构化状态 + Agent 规划 + 受控执行 + 结果断言 + 经验沉淀"替代"让 AI 多点几次按钮"，让测试能力本身成为可复用、可验证、可持续演进的平台资产。

### 0.3 核心创新点（UE 原生路线）
1. **源码级 RPC 结构化状态**：通过 UE 现有预留接口读取 `player / inventory / equipment / shop` 等确定性状态，天然规避图像方案的脆弱性——这正是 Acorn 主张的"结构化状态 > 截图"。
2. **自研 RPC 双工协议**：测试侧与游戏侧用 WebSocket + JSON 契约通信，支持"调用—响应"与"事件流推送"双向通道，兼顾局外慢规划与战斗低延迟。
3. **规划/执行分离 + 经验复利**：LLM 只做任务规划与差异判断，高频动作下沉到受控执行链路；成功流程固化为 Skill，失败经验回流到记忆，越用越稳。

### 0.4 与 Acorn 的关系
本平台复刻 Acorn AI 的工程范式（观察/执行/断言三层闭环、Skill 复用、记忆系统、Web 工作台、缺陷闭环），并把其抽象能力**钉死在 UE 工作流上**：状态来自源码接口而非截图，动作经由 RPC 而非坐标点击，因此可靠性更高、接入更轻。

---

## 1. 设计哲学与核心技术取舍

| 维度 | 传统脚本 | 低语义视觉 | 多模态 VLM | VLA/Agent | **本平台（UE 原生）** |
|---|---|---|---|---|---|
| 状态来源 | 控件树/坐标 | 截图匹配 | 截图理解 | 截图理解 | **RPC 结构化状态** |
| 可靠性 | 高但脆弱 | 中 | 中低 | 中低 | **高（确定性）** |
| 维护成本 | 超线性 | 中 | 高（时延/成本） | 高 | **低（接口契约稳定）** |
| 跨版本 | 差 | 差 | 中 | 中 | **中高（适配差异字段）** |

**取舍原则**（与 Acorn 一致，但更激进地用 UE 接口消除图像依赖）：
- 保留传统脚本的精确性，但不依赖固定路径；
- 不让视觉匹配承担主执行闭环；
- 多模态模型只作辅助分析（异常解释），不作为唯一依据；
- 不赌 VLA 长期红利，先把当前工程闭环跑通。

---

## 2. 系统架构

```
┌─────────────────── 测试平台侧 (Python / Agent) ───────────────────┐
│                                                                     │
│  Web 工作台 ── 设备画面 | 结构化状态 | 日志 | Agent 对话 (四区一体)    │
│        │                                                            │
│  Agent 核心                                                          │
│   ├─ ContextBuilder (五层上下文：系统/工具/环境/记忆/对话)            │
│   ├─ Planner (LLM：目标→状态差异→动作序列)                          │
│   ├─ Judge (BinaryJudge：多源断言 PATH_HIT / FACT_COVERAGE)         │
│   ├─ Skill 引擎 (EvolutionLoop：成功流程自进化)                     │
│   └─ MemoryStore (失败原因/修正策略/成功路径 回流)                   │
│        │                                                            │
│  Game-RPC Client (WebSocket + JSON)  ←─── 自研 RPC 协议 ───┐        │
└───────────────────────────────────────────────────────────┼────────┘
                                                             │ 调用/响应
                                                             │ 事件流推送
┌──────────────────── 游戏侧 (UE4 / UE5，现有预留接口) ──────┼────────┐
│  ITestRPCSubsystem (开发期已预留，不修改源码即可调用)        │        │
│   ├─ State 接口：GetPlayer / GetInventory / GetEquipment / GetShop   │
│   ├─ Action 接口：Buy / Equip / BindQuickSlot / MoveTo              │
│   └─ Event 接口：Log / ErrorCode / StateChange 推送                │
│  业务 Gameplay (战斗/背包/商店/任务…)  ← 仅暴露接口，不改内部逻辑   │
└─────────────────────────────────────────────────────────────────────┘
```

**关键约束**：游戏侧接口由开发在 Gameplay 层预留（如 `UTestRPCSubsystem`），平台侧**仅按契约调用，不修改游戏源码**。这保证平台与游戏版本解耦——版本升级只需适配字段映射。

---

## 3. 自研 RPC 协议设计（核心）

### 3.1 传输与编码
- **传输**：WebSocket（长连接，支持双向：请求—响应 + 服务端主动推送事件流）。
- **编码**：UTF-8 JSON。
- **端口约定**：游戏侧在 `ws://<game_host>:<rpc_port>/testrpc` 暴露服务。

### 3.2 消息信封
```json
// 请求
{ "id": "req-001", "method": "state.get_player", "params": {} }
// 响应（成功）
{ "id": "req-001", "result": { "currency": 13200, "bag_free_slots": 8, "current_page": "shop" } }
// 响应（失败）
{ "id": "req-001", "error": { "code": -32001, "message": "player not in shop" } }
// 事件推送（服务端→测试侧，无需请求）
{ "id": "evt-0001", "method": "event.state_change", "params": { "field": "health", "from": 100, "to": 72 } }
```

### 3.3 接口契约（游戏侧需实现）
```text
State（观察层）
  state.get_player()      → { currency, bag_free_slots, current_page, health, position }
  state.get_inventory()   → [ { item_id, name, count } ]
  state.get_equipment()   → { primary_weapon, secondary_weapon, quick_slot_1..n }
  state.get_shop()        → { available, items: [ { item_id, name, price, stock } ] }

Action（执行层）
  action.buy(item_id, count)        → { ok, new_currency, txn_id }
  action.equip(slot, item_id)       → { ok, equipped }
  action.bind_quickslot(slot, item_id) → { ok, bound }
  action.move_to(target, distance)  → { ok, arrived }

Event（事件流）
  event.log(msg)              → 客户端/服务端日志
  event.error(code, ctx)      → 错误码与上下文
  event.state_change(field)   → 状态变更（战斗低延迟关键）
```

### 3.4 错误码约定
```text
-32000  通用错误
-32001  前置条件不满足（如不在商店页）
-32002  资源不足（金币/库存）
-32003  目标不可交互（距离过远/被遮挡）
-32004  背包满
```

### 3.5 安全与权限
- 仅测试构建（Test/Development 配置）启用 RPC 服务，Shipping 构建关闭。
- 可加简单 token 校验，防止误连生产环境。

---

## 4. 核心闭环：观察 / 执行 / 断言

以"战前准备 case"为例：购买并装备 RX-4 突击步枪，补足 T3 治疗药剂×3、5.56mm AP 弹药×120，绑定快捷栏。

### 4.1 观察层（结构化状态，非截图）
```json
{
  "player":   { "currency": 13200, "bag_free_slots": 8, "current_page": "shop" },
  "equipment":{ "primary_weapon": null, "quick_slot_1": null },
  "inventory":[
    { "item_id": "med_t3",   "name": "T3 治疗药剂", "count": 1 },
    { "item_id": "ammo_556_ap","name": "5.56mm AP 弹药", "count": 40 }
  ],
  "shop": { "available": true, "items": [
    { "item_id": "wp_rx4", "name": "RX-4 突击步枪", "price": 6500, "stock": 3 },
    { "item_id": "med_t3", "name": "T3 治疗药剂", "price": 300, "stock": 12 },
    { "item_id": "ammo_556_ap", "name": "5.56mm AP 弹药", "price": 8, "stock": 500 }
  ]},
  "target_case": { "weapon": "RX-4 突击步枪", "min_potion_count": 3, "min_ammo_count": 120, "required_slot": "primary_weapon" }
}
```
Agent 基于该状态得出差异：缺 RX-4、缺 2 药剂、缺 80 弹药、主武器槽空 → 进入执行。

### 4.2 执行层（目标差异 → 动作）
- 不跑固定脚本，而由 Planner 按差异生成动作：`buy(wp_rx4,1) → buy(med_t3,2) → buy(ammo_556_ap,80) → equip(primary_weapon, wp_rx4) → bind_quickslot(1, med_t3)`。
- 每个动作经 RPC 执行后**回读状态**校验，避免"点了没生效"才发现。
- 原子工具通过 `Game-RPC Client` 暴露为 MCP 风格工具，供 Agent Function Calling。

### 4.3 断言层（Judge，多源证据）
| 断言维度 | 观察数据 | 通过条件 |
|---|---|---|
| 装备断言 | 结构化装备状态 + 截图 | RX-4 已装备主武器槽 |
| 补给断言 | 背包 + UI | 药剂≥3，已入快捷栏 |
| 弹药断言 | 背包 + 配置表 | 弹药≥120 且与武器匹配 |
| 交易断言 | 货币变化 + 交易日志 | 扣款合理、购买成功 |
| 流程断言 | 执行轨迹 + 状态回流 | 购买/装备/配置均完成 |
| 异常断言 | 客户端/服务端日志 | 无关键错误码 |

### 4.4 智能失败反馈（四层）
```json
{ "step_id": 3, "status": "failed",
  "L1_事实": { "action": "equip", "target": "wp_rx4", "error": "target not interactable" },
  "L2_分析": { "has_item": true, "in_shop_page": true, "distance_to_slot": 320 },
  "L3_建议": [ { "type": "insert_step_before", "step": "open_bag", "confidence": 0.91 } ],
  "L4_辅助": { "nearby": ["BagUI"], "recent_ok": ["buy_rx4"] } }
```

---

## 5. 能力复用：Skill 与记忆

### 5.1 Skill 引擎（自进化）
复用 `skillforge` 内核的 `EvolutionLoop + LLMProposer`：一次成功流程（商店购买→装备→绑快捷栏）被固化为可迁移 Skill；后续同类 case 直接复用，跨游戏只需适配字段映射。

### 5.2 记忆系统（经验复利）
复用 `MemoryStore` + `TEST_MEMORY.md`：失败原因（如"背包满""距离过远"）、修正策略（"插入 move_to""先开背包"）、成功路径统一回流。下一次相似场景带着历史经验执行，不再从零试错。

### 5.3 跨游戏复用
游戏 A 首次打通流程成本最高；沉淀为 Skill + 记忆后，游戏 B 只需适配控件映射/字段清洗/物品映射等差异部分——把"重新做一套自动化"变成"复用已有能力 + 差异适配"。

---

## 6. 战斗场景：低延迟执行与策略热更新

- **规划/执行分离**：LLM 在规划层理解战斗目标、生成策略；局内高频判断（血量阈值、补给时机、索敌转向）下沉到**受控执行链路 / 规则策略引擎**，避免普通 LLM 数秒时延错过窗口。
- **策略热更新**：阈值、优先级、流程组合放入可快速重载的策略层（JSON/YAML），无需重新编译打包即可进入下一轮验证。
- **事件驱动**：游戏侧通过 `event.state_change` 高频推送战斗状态，测试侧规则引擎毫秒级决策并回发动作 RPC。

---

## 7. 平台层：Web 工作台与缺陷闭环

- **Web 工作台（四区一体）**：设备画面 + 结构化状态面板 + 过程日志 + Agent 对话，让自然语言测试任务不再是黑箱，过程可观察、可追踪、可验证、可回放。
- **缺陷闭环**：任务失败时沉淀问题标题、严重等级、时间线、复现步骤、期望/实际对比、实例级证据，并与测试任务/设备/版本关联，可直接转研发问题。

---

## 8. 技术栈

| 层级 | 技术选型 |
|---|---|
| 测试侧语言 | Python 3.10+ |
| LLM 后端 | OpenAI 兼容接口（可接 GPT / 混元 / 本地 vLLM / Ollama） |
| Agent 内核 | skillforge（LLMBackend / BinaryJudge / MemoryStore / EvolutionLoop） |
| RPC 客户端 | WebSocket (asyncio + json)，自研 `GameRPCClient` |
| Web 平台 | FastAPI + WebSocket + 轻量前端（React/Vue 或纯 HTML） |
| 持久化 | SQLite（记忆、缺陷、执行轨迹） |
| 游戏侧 | UE4/UE5，现有预留 `ITestRPCSubsystem`（C++/BP 已实现，平台不改源码） |

---

## 9. 工程结构与目录（建议）

```
ue-ai-test-platform/
├── game_rpc/                 # 游戏侧 RPC 契约与客户端
│   ├── protocol.py           # 消息信封 / 错误码 / 接口契约定义
│   ├── client.py             # GameRPCClient (WebSocket 双工)
│   └── mock_server.py        # 简历 demo：模拟 UE ITestRPC 的 mock 游戏端
├── agent/
│   ├── context.py            # 五层上下文 ContextBuilder
│   ├── planner.py            # LLM 规划：目标→差异→动作
│   ├── loop.py               # 观察-执行-断言主循环
│   ├── battle.py             # 低延迟规则策略引擎 + 策略热更新
│   └── judge.py              # 多源断言 (复用 skillforge BinaryJudge)
├── core/                     # 复用 skillforge 内核
│   ├── llm.py                # LLMBackend / BinaryJudge
│   ├── memory.py             # MemoryStore
│   └── evolution.py          # EvolutionLoop / LLMProposer
├── web/                      # 工作台 + 缺陷闭环
│   ├── app.py                # FastAPI 服务
│   └── static/               # 四区一体前端
├── cases/                    # 测试用例（战前准备 / 资源采集 / 战斗补给…）
└── README.md
```

---

## 10. 最小可运行 Demo（简历展示用）

**目标**：不依赖真实 UE 工程，用 `mock_server.py` 模拟 `ITestRPCSubsystem`，跑通完整闭环，证明架构成立。

**演示 case（战前准备）**：
1. 平台启动 `mock_server` 模拟一个处于商店页、金币 13200、缺 RX-4/药剂/弹药的角色。
2. Agent 经 RPC 读取结构化状态 → 规划差异动作 → 逐条执行 → 回读校验。
3. Judge 对装备/补给/弹药/交易/异常五维断言，输出 PASS。
4. 成功路径写入 Skill，失败分支（如临时模拟"背包满"）写入记忆，下次自动规避。
5. Web 工作台展示四区一体与缺陷闭环。

**价值**：用最小成本证明"结构化状态 + Agent + RPC"闭环可行，可直接作为作品集演示视频/截图。

---

## 11. 实施路线 / 里程碑

| 阶段 | 内容 | 产出 |
|---|---|---|
| M0 | 复用 skillforge 内核（断言/记忆/进化） | 内核可用 |
| M1 | 自研 RPC 协议 + `GameRPCClient` + `mock_server` | 观察层跑通 |
| M2 | 执行层原子工具 + 观察-执行-断言 Loop | 战前准备 case 跑通 |
| M3 | Skill 沉淀 + 记忆回流 | 同类 case 复用 |
| M4 | Web 工作台 + 缺陷闭环 | 平台可视化 |
| M5 | 战斗低延迟策略引擎 + 策略热更新 | 动态场景覆盖 |

---

## 12. 与 Acorn / 传统方案对比总结

- 相对**传统脚本**：本平台精确但由 Agent 动态规划，版本变化只改字段映射，不批量失效。
- 相对**视觉/VLM 方案**：本平台用 RPC 结构化状态，确定性高、成本低、可验证。
- 相对 **Acorn（通用）**：本平台把抽象能力钉在 UE 工作流上，借源码接口获得更高可靠性，接入更轻。

---

## 13. 简历亮点（Key Achievements，可直接引用）

- 设计并实现一套**面向 UE 游戏的 AI 自动化测试平台**，以"观察—执行—断言"工程闭环替代脆弱的脚本/图像方案，复刻 Acorn AI 范式并落地到虚幻引擎工作流。
- 设计**自研 RPC 双工协议**（WebSocket + JSON），通过 UE 现有预留接口读写结构化游戏状态，实现测试侧与游戏侧解耦、跨版本零侵入接入。
- 引入 **LLM 规划 / 低延迟执行分离**架构，将战斗高频决策下沉到规则策略引擎并支持策略热更新，兼顾稳定性与时延。
- 构建 **Skill 自进化 + 记忆回流**机制，使成功流程与失败经验持续沉淀，跨游戏/跨 case 复用，显著降低长期维护成本。
- 搭建 **Web 工作台与缺陷闭环**，实现执行过程可观察、结果可验证、缺陷可回溯，统一测试/研发信息链。

---

## 14. 风险与边界

- **接入前提**：依赖游戏侧已预留 `ITestRPC` 类接口；若完全没有预留接口，需降级为控制台/控制台变量方案或（次优）图像辅助。
- **契约维护**：接口字段随版本变更需同步契约文档；建议用 schema 校验 + 版本号。
- **战斗实时性**：纯 LLM 规划无法满足毫秒级战斗决策，本平台以规则引擎兜底，LLM 仅做策略层。
- **适用范围**：最擅长局外流程（商店/背包/任务/配置）与中低频战斗；超高频 FPS 操作仍需游戏内原生自动化补充。
