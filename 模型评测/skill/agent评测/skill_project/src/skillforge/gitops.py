"""git 隔离工作区。

用独立 git 仓库承载实验提交，使每次候选改动可审计、可回滚，
且不污染业务项目。所有操作通过 subprocess 调用 git（避免额外依赖）。
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(Exception):
    """git 操作失败。"""


class GitWorkspace:
    """轻量 git 工作区封装。"""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        cmd = ["git", "-C", str(self.root), *args]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8"
        )
        if check and proc.returncode != 0:
            raise GitError(
                f"git {' '.join(args)} 失败: {proc.stderr.strip()}"
            )
        return proc

    # ------------------------------------------------------------------ #

    def ensure_initialized(self) -> None:
        """初始化仓库并确保有 baseline 提交。"""
        if not (self.root / ".git").exists():
            self._run("init", "-q")
            self._run("config", "user.email", "skillforge@local")
            self._run("config", "user.name", "skillforge")
        if not self._has_commits():
            self._run("add", "-A")
            self._run("commit", "-q", "-m", "baseline")

    def _has_commits(self) -> bool:
        proc = self._run("rev-parse", "--verify", "HEAD", check=False)
        return proc.returncode == 0

    # ------------------------------------------------------------------ #

    def snapshot(self, message: str) -> None:
        """把当前工作区状态提交为一个快照。"""
        self._run("add", "-A")
        self._run("commit", "-q", "--allow-empty", "-m", message)

    def rollback(self) -> None:
        """回滚工作区到上一个快照（丢弃最近一次提交）。"""
        if self._has_commits():
            self._run("reset", "--hard", "HEAD~1")
        else:
            self._run("reset", "--hard", "HEAD")

    def current_hash(self) -> str:
        proc = self._run("rev-parse", "--short", "HEAD", check=False)
        return proc.stdout.strip() if proc.returncode == 0 else ""

    def is_clean(self) -> bool:
        proc = self._run("status", "--porcelain", check=False)
        return proc.stdout.strip() == ""
