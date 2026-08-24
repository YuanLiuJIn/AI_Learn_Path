# SkillForge 架构设计

## 1. 设计哲学

四条原则贯穿全部代码：

1. **类型即契约**：跨模块共享的数据结构集中在 `types.py`（dataclass + enum），
   杜绝各模块自行拼 dict 导致的字段漂移与隐式契约。
2. **程序掌握控制流，LLM 只做单点生成**：门控、回滚、升层这些"决策"由程序
   决定（可审计、可复现），LLM 只在 propose 阶段做"诊断 + 修改"。
3. **读写分离、副作用显式**：`target.py` 的写操作返回 diff，评测器只读，
   候选的"应用/回滚"由循环驱动显式管理，避免隐式副作用。
4. **可插拔后端**：评测器（local/sandbox）、LLM（任意后端）、runner 均为接口，
   便于替换与扩展。

## 2. 分层架构

```
表示层    cli.py ──────────────── 命令解析、参数装配
─────────────────────────────────────────────────
应用层    loop.py ──────────────── 8 阶段循环、Beam 集成、升层/停止控制
─────────────────────────────────────────────────
能力层    proposer.py  evaluate/  gate.py  memory.py  gitops.py
          (提出)       (验证)     (门控)   (记忆)     (隔离)
─────────────────────────────────────────────────
基础层    target.py  gt.py  assertions.py  types.py  config.py  llm.py
```

依赖方向自上而下，上层依赖下层，下层不感知上层。

## 3. 核心模块

### 3.1 target.py —— 优化目标抽象
`SkillTarget` 封装一个 Skill 目录。关键设计：
- `snapshot()` 返回不可变的 `Snapshot`（SKILL.md + prose），供评测器读取。
- `write_skill_md()` / `write_prose()` 返回 unified diff，写操作显式化。
- `locate_layer()` 把突变层（TRIGGER/BODY/SCRIPT）映射到可改区域。

### 3.2 evaluate/ —— 评测层（本项目的核心改进）
- `LocalEvaluator`：静态"文档体检"，断言针对 skill 文本 corpus。
- `SandboxEvaluator`：端到端"能力验证"，断言针对 skill **执行产物**（借鉴
  Voyager 的环境反馈思想）。通过可插拔的 `SkillRunner` 在隔离目录执行 skill。

两者实现同一 `Evaluator` 接口，由配置决定用哪个。

### 3.3 gate.py —— 门控 + 统计显著性
- 多维 AND：质量/触发/成本/延迟/回归，任一不达标即 DISCARD。
- `bootstrap_mean_diff_significant()`：对 dev pass_rate 多次采样，用 bootstrap
  置信区间判断提升是否显著，区分"真改进"与"运气波动"（治 LLM 评测噪声）。

### 3.4 memory.py —— 三层结构化记忆
`TRACE（原始） → LESSON（失败教训） → PATTERN（可复用模式）`，JSONL append
存储。`format_for_prompt()` 把可复用模式注入 proposer（含 token 预算），实现
跨 skill 冷启动（借鉴 AutoSkill 终身学习 + SkillRL 经验蒸馏）。

### 3.5 proposer.py —— 候选生成
`LLMProposer` 读当前 skill + 失败 case + 历史经验，让 LLM 做"反事实诊断 +
最小原子修改"，输出新 SKILL.md。`ProposeContext` 显式携带全部上下文，
支持 Beam（一次生成 n 个候选）。

### 3.6 loop.py —— 循环驱动
8 阶段：Setup → Review → Propose → Apply → Verify → Gate → Log → Loop-Control。
集成 Beam（每轮 K 候选，保留质量最优者）与升层策略（plateau 后 TRIGGER→BODY→SCRIPT）。

## 4. 数据流

```
GT(evals.json) ─┐
                ├─→ LocalEvaluator/SandboxEvaluator ─→ EvalResult ─→ Gate ─→ GateDecision
SkillTarget ────┘                                              │
     ▲                                                         ▼
     │  write_skill_md(diff)                          keep / discard
     │                                                     │
     └────────── LLMProposer ←── ProposeContext ───────────┘
                  (含失败 case + 历史经验)
```

## 5. 关键设计决策

| 决策 | 理由 |
|---|---|
| 用 `types.py` 统一类型 | 散落的 dict 契约难维护、易漂移 |
| 评测器接口化（local/sandbox） | 支持"文档体检"与"能力验证"两种范式 |
| 门控加 bootstrap 显著性 | 硬阈值会被 LLM 噪声误导 |
| 三层记忆 + 跨 skill 注入 | 扁平日志式记忆无法复用 |
| 强类型 dataclass 配置 | 裸键值配置难以校验 |
| 显式 UTF-8 | 隐式默认编码在 Windows 上崩溃 |
| 按职责分包 | 平铺脚本难以导航 |

## 6. 已知边界与后续扩展

- `LLMProposer` 与 `LLMSkillRunner` 需要接入真实 `LLMBackend`（当前为 `NullBackend`）。
- 触发 F1 维度当前为占位（需接入触发评测数据）。
- 后续可扩展：多 Agent 工作流目标（`WorkflowTarget`）、外部依赖持续适配
  （ContDa 思路）、轻量 Reranker 内层（SAGE/SkillRL 思路）。
