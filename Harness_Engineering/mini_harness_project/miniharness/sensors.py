"""验证 / 反馈（Verification & Sensors）层。

在沙箱里跑测试，把结果结构化地反馈给 Agent。

关键 harness 原则：好的 sensor 不只说"失败了"，还要尽量告诉 Agent
"哪里失败、可能怎么改"。这里我们把 unittest 的输出摘要返回，
你可以在学习中进一步增强它（例如解析具体断言、定位行号）。
"""

import subprocess
import sys
from pathlib import Path


def run_tests(work_dir: Path, test_module: str = "test_solution") -> dict:
    """在 work_dir 下用标准库 unittest 跑测试。

    返回:
      {"passed": bool, "summary": str}
    """
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", test_module, "-v"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    passed = proc.returncode == 0

    # 把输出压缩成对 Agent 友好的摘要（取最后若干行，通常含 FAIL/OK 与断言信息）
    lines = [ln for ln in output.splitlines() if ln.strip()]
    tail = "\n".join(lines[-15:]) if lines else "(no output)"
    summary = ("ALL TESTS PASSED\n" if passed else "TESTS FAILED\n") + tail
    return {"passed": passed, "summary": summary}
