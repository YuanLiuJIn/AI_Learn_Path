# 让你的 Skill 可测可迭代：Agent Skill Benchmark 评测经验

> 来源文章：《让你的 Skill 可测可迭代 - Agent Skill Benchmark 评测经验》（作者 patrickzeng）
> 核心主题：如何为工程型 Agent Skill 设计可复现的 Benchmark，并扩展为通用 Agent Harness。
> 案例载体：一个承接「NX 编译、输出编译结果并总结错误」的工程 Skill（Methodology 与 NX 无关，可迁移到任意领域）。

---

## 〇、核心问题：为什么需要 Skill Benchmark

Agent 任务最终成功，可能有多种原因：
- 模型本来就会做；
- 任务本身太简单；
- prompt 写得足够直接；
- 运行时注入了额外上下文；
- Agent 没用 Skill，靠搜索文件猜到了答案，甚至 verifier 只查最终文件，过程被完全绕过也能过。

最危险的假象：**答案对了，但 Skill 没起作用**。

因此更适合工程 Skill 的判断标准是：

> **Skill 成功 = 任务结果正确 + Skill 被真实调用 + 关键动作被真实执行 + 产物可验证**

---

## 一、Skill 不该只描述知识，要约束行为路径

NX 编译 Skill 的目标不是「编译命令大全」，而是把 Agent 行为收敛到稳定路径：

1. 找到正确执行目录
2. 通过统一 runner 执行构建
3. 让 runner 输出结构化结果（primary_error / summary / highlights / raw_log_path）
4. 据此判断下一步：成功就停止；lint 交给规范修复；UT 交给测试流程；普通编译错误交给代码修复

可替换为任意领域：数据库迁移（migration dry-run）、前端构建（lint/typecheck/test）、安全扫描（scan + 风险等级 + 证据文件）、数据分析（固定 notebook pipeline + 指标摘要）。

**真正重要的不是领域，而是：Skill 一旦变成行为约束，就出现第二个问题——如何证明 Agent 真的按这条路径走了？**

---

## 二、受控对照思想的启发（来自 SkillBench）

关键实验思想：**评测 Skill 要做受控对照**，至少比较几种条件——
- 没有 Skill 时，模型自己能做到什么；
- 只给入口级说明时，是否足够；
- 给完整 Skill 集时，是否真的提升；
- 换 runtime / 模型时，结论是否仍成立；
- Skill 版本变化后，结果是否可复现。

研究型 benchmark 提供「对照实验」基础，但工程场景还需回答：Agent 是否真调用了 Skill？调用的是否目标 Skill？是否执行了关键命令？失败时归因为 Skill / task / verifier / runtime 哪一类？这次失败能否转成下一轮修改 Skill 的明确动作？——即需要「证据链」与「失败归因」，所以要做本地 Harness。

---

## 三、如何设计 Benchmark Tasks

不应从「需要多少题」开始，而应从 **Skill 的行为链路**开始（以编译为例）：

```
识别任务属于构建诊断 → 调用目标 Skill → 找到正确工作目录 → 执行统一 runner
→ 读取结构化输出 → 判断成功/失败 → 选择下一步处理路径 → 写出可验证答案
```

每个环节都可能成为 task 设计点。一个完整 task 是一组「可执行、可校验、可复盘」的信息包：

| 组成 | 内容 |
|---|---|
| Task 输入 | 任务说明（目标与限制）、环境与数据（代码/文件/配置） |
| 执行约束 | 执行 Profile（workflow / cwd / timeout）、目标 Skill（id / version / mode） |
| 过程证据 | Trace 要求（Skill 调用 / 工具执行）、Artifacts（answer / log / summary） |
| 结果验收 | 期望输出（schema / 关键字段）、Verifier（pass / fail / reward） |

### 3.1 先测「入口纪律」
确认 Agent 是否遵守基本规则：必须先跑 runner 而非先读大日志；必须在目标目录而非仓库根目录；必须输出结构化结果而非自然语言总结。Skill 的价值常在于**抑制坏习惯**，不只告诉新知识。

### 3.2 再测「正常路径」
成功路径任务：runner 返回成功，Agent 应停止，不继续找错、不路由到修复 Skill。防止 Agent 过度行动。

### 3.3 再测「失败分诊」
工程 Skill 常把问题分发到下一步能力。编译中 lint 失败→规范修复、UT 失败→测试修复、普通 C++ 错误→代码修复、配置/依赖问题→对应领域流程。这类 task 测的是 Skill 的**决策边界**。

### 3.4 加入「干扰项」和「反例」
真实环境会诱导 Agent：旧日志、过时 README 命令、显眼但非 primary 的 error、可伪造的最终答案、trace 里 echo 出来却没执行的命令文本。反例让 Benchmark 既测能力，也测**抗绕过能力**。

### 3.5 最后拉回真实目录
模拟 task 拆行为，但不能替代真实 task。要进入真实仓库、工具链、目录结构、产物路径。很多 Skill 模拟目录没问题，一进真实仓库就暴露：目录选错、runner 路径错、工具不可用、权限不一致、输出路径不稳、成功但 trace 缺失。
**原则：fixture task 拆行为，real task 证明行为能落地。**

---

## 四、从单 Skill 到通用 Agent Harness

临时脚本的痛点：任务多难组织、同 task 跑不同 skill mode 难控变量、换模型/runtime 难复用、verifier/trace/artifact 难统一、结果难汇总归因、Skill 版本难冻结。

### 4.1 三段架构
```
配置层（Task Registry / Dataset / Validation Set）
  → 编排层（Run Orchestrator）
    → 执行层（Workflow Adapter 准备工作区/选 cwd；Runtime Adapter 注入 Skill/启动 Agent/收集 Trace）
      → Agent Runtime + 真实工具链/沙盒
        → 评测层（Verifier 判结果；Trace Gate 判过程；归一化结果 + 失败归因 + 优化 backlog）
```

**关键点是解耦**：Task 不绑定某 Runtime，Runtime 不写死某任务类型。

### 4.2 三层输入拆分
- **Task**：单任务元信息（输入环境、说明、期望产物、verifier、难度、目标 Skill、执行 profile）。
- **Dataset**：一组相关任务（如构建分诊集、UT 修复集、代码生成集），代表能力范围。
- **Validation Set**：一次实验配方（哪些 task、哪些模型/runtime/skill mode、重复几次、超时）。

### 4.3 两类 Adapter
- **Workflow Adapter**：任务语义——准备工作区、选工作目录、注入环境变量、定义 verifier flow、声明关键 artifact。
- **Runtime Adapter**：Agent 运行时——启动 Agent、注入 Skill、选模型、收集 stdout/stderr、拉取 trace、归一化工具调用。

### 4.4 Verifier 只判结果，Trace Gate 判过程
- **Verifier**：answer 文件存在？字段正确？主要错误匹配？下一步 skill 正确？
- **Trace Gate**：目标 Skill 是否被调用？关键命令是否真执行？runner summary 是否由本次运行产生？有无伪造/绕过迹象？
- 两层不混：Verifier 问「结果对不对」，Trace Gate 问「是否按预期路径得到」。
- 可出现「Verifier 通过但 Trace Gate 失败」——说明模型猜对了，但 Skill 未被证明有效。

### 4.5 Artifact 是调试入口
每次 run 留存：原始工作区、Agent 输出、verifier 结果、normalized result、trace summary、原始 trace、runner summary、关键日志。失败可归因：Skill 未注入 / 注入未调用 / 调用未执行 / 执行未落盘 / 落盘字段错 / verifier 过宽 / trace gate 过松 / task 不稳定。

### 4.6 闭环：从运行到下一轮迭代
```
运行 Validation Set → 收集证据 → 失败归因（Skill/task/verifier/runtime）
→ 定向修改（Skill 文本/runner/adapter/task）→ 回归验证（同 task 复跑）
```

---

## 五、为什么不直接用开源 SkillBench

SkillBench 价值在提供研究范式（把 Skill 当实验变量观察 Agent 表现变化），但工程落地需额外解决：
1. **真实工程动作**：依赖真实仓库目录、构建命令、环境变量、权限、白名单，需 real workflow 而非通用沙盒。
2. **Runtime 适配**：同一 Skill 在不同 Runtime 表现不同（有的当上下文注入、有的原生工具调用、有的裁上下文导致 Skill 没被看到）。需本地 runtime adapter 做 materialization / trace 收集 / 归一化 / fallback。
3. **过程可信**：研究 benchmark 核心看 deterministic verifier 的 pass/fail；工程还需 Trace Gate 把 trajectory 从分析材料升级为质量门禁。
4. **反作弊/反假阳性**：Agent 没调目标 Skill、命令只出现在非执行参数、runner summary 伪造、task 工作区残留本地 Skill、trace 不足证关键动作——这些需变成 gate 和 regression test。

---

## 六、可复用的方法论（八步）

1. 写清楚 Skill 的**行为契约**（该做什么、先做什么、不能做什么、关键产物）。
2. 把行为契约**拆成 task**（每 task 只测一个关键决策点：入口/目录/命令/产物/路由/边界/异常）。
3. 设计 **skill mode 对照**（至少含无 Skill 基线，再按场景加入口级/目标/完整 Skill 集）。
4. 把 task 组织成 dataset，实验组织成 validation set（别让 benchmark 变成临时脚本）。
5. 写 verifier，但**不只信 verifier**（加 Trace Gate）。
6. 留下 **artifact**（每次失败能追到 workspace/answer/trace/log/runner summary/verifier 结果）。
7. 加入 **real workflow**（只要 Skill 依赖真实工具链，必须有真实目录评测）。
8. 把失败归因**变成下一轮迭代**（改 Skill / task / verifier / adapter / runner）。

---

## 七、结语

一个真正可用的 Skill 至少含三部分：**行为契约 + 执行载体（runner/工具/脚本/模板/references）+ 评测体系**。

> 没有 Benchmark 的 Skill，容易停留在「看起来有道理」。有了 Benchmark，Skill 才开始变成工程资产。

最值得优先建立的 habit：**写 Skill 的同时，同步设计它的 Benchmark。**
