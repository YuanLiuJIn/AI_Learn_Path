# MiniHarness：一个最小但完整的 Coding Agent Harness（学习项目）

> 本项目用来**动手学习 Harness Engineering**。配套阅读：上级目录 `../harness_engineering_guide.md`（入门）、`../harness_engineering_advanced.md`（进阶系统设计）。
>
> 核心理念：`Agent = Model + Harness`。本项目刻意把“模型”做得很薄（甚至可以是一个脚本化假模型），把重点全放在 **Harness（模型之外的一切）** 上，让你看清真正决定可靠性的工程组件。

## 你将亲手实现的 6 个 Harness 组件

对照 2026 年 Harness 综述的 ETCLOVG 七层，本项目覆盖其中核心几层：

| 本项目模块 | 作用 | 对应 ETCLOVG 层 |
|---|---|---|
| `AGENTS.md` | 前馈引导（Guides）：告诉 Agent 规则 | 上下文管理 |
| `miniharness/tools.py` | 为 Agent 设计的工具接口 | 工具接口与协议 |
| `miniharness/sandbox.py` | 隔离的临时工作区，改坏了不影响原文件 | 执行环境与沙箱 |
| `miniharness/sensors.py` | 跑测试，把结果反馈给 Agent（Sensors）| 验证 |
| `miniharness/agent.py` | Reason→Act→Observe 编排循环 | 生命周期与编排 |
| `miniharness/trace.py` | 记录每一步轨迹、成本 | 可观测性 |
| `evals/run_eval.py` | 批量跑任务，算 resolved rate | 验证 |

## 快速开始（无需 API Key）

项目内置一个 `ScriptedLLM`（脚本化假模型），默认即可端到端跑通，看清整个 harness 闭环：

```bash
cd Harness_Engineering/mini_harness_project
python run.py --task tasks/fizzbuzz
```

你会看到 Agent 一步步：列文件 → 读代码 → 写修复 → 跑测试 → 完成，最后输出是否 `RESOLVED`。
轨迹会写到 `tasks/fizzbuzz/.trace.jsonl`。

## 接入真实大模型（学习的关键一步）

设置环境变量后改用真实 LLM（任意 OpenAI 兼容接口）：

```bash
# PowerShell
$env:MINIHARNESS_LLM = "openai"
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"   # 或你的兼容网关
$env:OPENAI_MODEL = "gpt-4o-mini"
python run.py --task tasks/fizzbuzz
```

此时模型自己决定调用哪个工具、怎么修代码。**对比脚本化模型和真实模型的差异，就是理解 harness 的最好方式。**

## 批量评测（resolved rate）

```bash
python evals/run_eval.py
```

它会跑 `tasks/` 下所有任务，统计有多少个被解决（仿 SWE-bench 的 resolved rate）。

## 推荐的学习路线（边改边学）

1. **跑通**：先用 ScriptedLLM 跑一遍，读 `trace.jsonl`，理解 Reason-Act-Observe 循环。
2. **加工具**：在 `tools.py` 里加一个新工具（比如 `search(keyword)`），看 Agent 能否用上。
3. **强化 sensor**：让 `sensors.py` 不只返回“失败”，而是把失败的具体断言摘要给 Agent（好 sensor 要“告诉下一步怎么改”）。
4. **改 guides**：修改 `AGENTS.md`，观察对真实 LLM 行为的影响。
5. **加治理**：给 `write_file` 加权限边界（禁止改 `test_*.py`），体会 Governance 层。
6. **加任务**：在 `tasks/` 下新建一个有 bug 的小任务，扩充你的“私有 benchmark”。

### 进阶：把它升级成一个小型 Task Loop 系统

读完 `../harness_engineering_advanced.md` 后，按下表逐项升级本项目，每加一块就回看进阶篇对应章节：

| 升级项 | 做什么 | 对应进阶篇章节 |
|---|---|---|
| 状态机 | 把 `agent.py` 的简单循环改成 INIT→EXEC→QA→FIXING→DONE | Task Loop |
| Checkpoint | 加 `save_checkpoint` + 断点续跑，状态写出模型 | Checkpoint/幂等 |
| 幂等性 | 给会重放的动作加 idempotency key | Checkpoint/幂等 |
| 独立 Evaluator | 加一个 LLM-as-judge 评审，替代“模型自评” | 三 Agent 架构 |
| 可观测性 | 在 `trace.py` 加 Heartbeat 与 token 预算统计 | Heartbeat/Watchdog |

## 目录结构

```text
mini_harness_project/
  README.md                 本文件
  AGENTS.md                 前馈引导（Guides）
  requirements.txt          依赖（核心零第三方依赖）
  run.py                    入口：跑单个任务
  miniharness/
    __init__.py
    config.py               配置与 LLM 选择
    llm.py                  LLM 抽象 + ScriptedLLM + OpenAI 兼容
    tools.py                Agent 可用工具
    sandbox.py              隔离执行环境
    sensors.py              测试反馈（验证）
    agent.py                编排循环
    trace.py                可观测性
  tasks/
    fizzbuzz/
      solution.py           带 bug 的代码
      test_solution.py      判定用例（unittest，标准库）
      task.json             任务定义
  evals/
    run_eval.py             批量评测 + resolved rate
```

## 设计要点说明

- **零第三方依赖即可运行**：测试用标准库 `unittest`，LLM 调用用标准库 `urllib`，所以默认模式开箱即用。
- **ScriptedLLM 是教学占位**：它按预设剧本走，让你在没有模型时也能看清 harness 机制；真实学习时请切换到真实 LLM。
- **沙箱保护**：Agent 只在临时副本里操作，原始任务文件不会被改坏，可反复实验。
