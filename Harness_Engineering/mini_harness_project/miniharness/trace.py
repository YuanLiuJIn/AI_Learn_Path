"""可观测性（Observability）层：把 Agent 每一步轨迹写成 JSONL。

好的 harness 必须能回答：Agent 第几步做了什么、调用了什么工具、
得到什么反馈、花了多少步。这是排查和改进的基础。
"""

import json
import time
from pathlib import Path


class Trace:
    def __init__(self, path: Path):
        self.path = Path(path)
        # 每次任务开始清空旧轨迹
        self.path.write_text("", encoding="utf-8")
        self.step = 0

    def log(self, event: str, **fields):
        self.step += 1 if event == "action" else 0
        record = {
            "ts": round(time.time(), 3),
            "event": event,
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def console(self, msg: str):
        """同时打印到终端，方便实时观察。"""
        print(msg)
