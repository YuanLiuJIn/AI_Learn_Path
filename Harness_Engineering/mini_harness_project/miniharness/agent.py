"""生命周期与编排（Lifecycle & Orchestration）层。

实现经典的 Reason -> Act -> Observe 循环（ReAct 范式）：
  1. 把 guides(AGENTS.md) + 工具说明 + 任务 组成上下文
  2. 让 LLM 产生一个动作（Reason + Act）
  3. 在沙箱里执行工具，得到反馈（Observe）
  4. 把反馈加回上下文，循环
  5. 用最终测试判定是否 RESOLVED（Verification）

这一层把其它所有 harness 组件粘合起来。
"""

import json
from pathlib import Path

from . import config
from .llm import build_llm
from .sandbox import Sandbox
from .sensors import run_tests
from .tools import ToolBox, tool_specs_text
from .trace import Trace


def _build_system_prompt(guides: str) -> str:
    return (
        guides
        + "\n\n## 可用工具\n"
        + tool_specs_text()
        + "\n\n## 输出要求\n"
        + '严格只输出一个 JSON：{"thought": "...", "tool": "工具名", "args": {...}}。'
        + "不要输出 JSON 以外的任何内容。"
    )


def run_task(task_dir: str) -> bool:
    task_dir = Path(task_dir)
    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    guides_path = task_dir.parent.parent / "AGENTS.md"
    guides = guides_path.read_text(encoding="utf-8") if guides_path.exists() else ""

    trace = Trace(task_dir / ".trace.jsonl")
    llm = build_llm()

    with Sandbox(task_dir) as sandbox:
        toolbox = ToolBox(sandbox, test_module=task.get("test_module", "test_solution"))

        system_prompt = _build_system_prompt(guides)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"任务: {task['description']}\n\n"
                f"当前文件:\n" + "\n".join(sandbox.list_files())
            )},
        ]

        trace.console(f"\n=== 任务: {task['name']} ===")

        for step in range(1, config.MAX_STEPS + 1):
            action = llm.act(messages)
            tool = action.get("tool", "")
            args = action.get("args", {})
            thought = action.get("thought", "")

            trace.log("action", step=step, thought=thought, tool=tool, args=args)
            trace.console(f"[步骤{step}] 想法: {thought} | 调用: {tool}({args})")

            if tool == "finish":
                trace.console("[结束] Agent 认为已完成")
                break

            observation = toolbox.call(tool, args)
            trace.log("observation", step=step, tool=tool, result=observation[:2000])
            preview = observation if len(observation) < 300 else observation[:300] + " ...(截断)"
            trace.console(f"        观察: {preview}")

            # 把动作与观察加回上下文，供下一步推理
            messages.append({"role": "assistant", "content": json.dumps(action, ensure_ascii=False)})
            messages.append({"role": "user", "content": "OBSERVATION: " + observation})
        else:
            trace.console("[结束] 达到最大步数上限")

        # 最终验证：在沙箱里跑一次测试判定是否真的解决
        final = run_tests(sandbox.work_dir, task.get("test_module", "test_solution"))
        resolved = final["passed"]
        trace.log("verdict", resolved=resolved, summary=final["summary"])
        trace.console(f"\n结果: {'RESOLVED' if resolved else 'UNRESOLVED'}")
        return resolved
