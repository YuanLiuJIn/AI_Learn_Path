"""执行环境与沙箱（Execution Environment）层。

把任务目录复制到一个临时工作区，Agent 的所有读写都在副本里进行，
这样：
1. 原始任务文件不会被改坏，可反复实验；
2. 多个任务之间互相隔离。

真实世界里这一层会用 Docker / git worktree / 受限文件系统等实现，
原理一致：给 Agent 一个可隔离、可丢弃、可重置的运行空间。
"""

import shutil
import tempfile
from pathlib import Path


class Sandbox:
    def __init__(self, task_dir: Path):
        self.task_dir = Path(task_dir)
        self.work_dir: Path | None = None

    def __enter__(self) -> "Sandbox":
        tmp = tempfile.mkdtemp(prefix="miniharness_")
        self.work_dir = Path(tmp) / self.task_dir.name
        shutil.copytree(self.task_dir, self.work_dir)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.work_dir and self.work_dir.parent.exists():
            shutil.rmtree(self.work_dir.parent, ignore_errors=True)

    # ---- 受控的文件访问（治理边界可在此加强）----

    def _resolve(self, rel_path: str) -> Path:
        p = (self.work_dir / rel_path).resolve()
        # 防止路径逃逸出沙箱
        if self.work_dir.resolve() not in p.parents and p != self.work_dir.resolve():
            raise ValueError(f"路径越界，禁止访问沙箱外: {rel_path}")
        return p

    def list_files(self) -> list[str]:
        return sorted(
            str(p.relative_to(self.work_dir))
            for p in self.work_dir.rglob("*")
            if p.is_file() and not p.name.startswith(".")
        )

    def read_file(self, rel_path: str) -> str:
        return self._resolve(rel_path).read_text(encoding="utf-8")

    def write_file(self, rel_path: str, content: str) -> None:
        target = self._resolve(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
