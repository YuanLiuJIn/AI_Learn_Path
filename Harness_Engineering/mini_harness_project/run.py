"""MiniHarness 入口：运行单个任务。

用法:
  python run.py --task tasks/fizzbuzz
"""

import argparse
import sys
from pathlib import Path

# 确保能 import 到 miniharness 包
sys.path.insert(0, str(Path(__file__).parent))

from miniharness.agent import run_task


def main():
    parser = argparse.ArgumentParser(description="MiniHarness: 运行一个 coding agent 任务")
    parser.add_argument("--task", required=True, help="任务目录，如 tasks/fizzbuzz")
    args = parser.parse_args()

    resolved = run_task(args.task)
    sys.exit(0 if resolved else 1)


if __name__ == "__main__":
    main()
