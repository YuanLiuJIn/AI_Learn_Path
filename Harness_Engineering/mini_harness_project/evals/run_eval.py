"""批量评测：跑 tasks/ 下所有任务，统计 resolved rate（仿 SWE-bench）。

用法:
  python evals/run_eval.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from miniharness.agent import run_task


def main():
    tasks_dir = ROOT / "tasks"
    task_dirs = sorted(p for p in tasks_dir.iterdir() if (p / "task.json").exists())

    if not task_dirs:
        print("没有找到任务。请在 tasks/ 下创建任务目录。")
        return

    results = []
    for td in task_dirs:
        resolved = run_task(str(td))
        results.append((td.name, resolved))

    total = len(results)
    solved = sum(1 for _, r in results if r)

    print("\n================ 评测汇总 ================")
    for name, r in results:
        print(f"  {'PASS' if r else 'FAIL'}  {name}")
    print("-----------------------------------------")
    print(f"  Resolved Rate: {solved}/{total} = {solved / total:.1%}")
    print("=========================================")


if __name__ == "__main__":
    main()
