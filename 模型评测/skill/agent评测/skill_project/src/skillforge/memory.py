"""三层结构化记忆。

常见做法是扁平的结果日志（results.tsv + experiments.jsonl）。
本项目升级为三层结构化记忆（融合 AutoSkill 的终身学习与 SkillRL 的经验蒸馏）：

- TRACE   : 原始执行轨迹（诊断现场）
- LESSON  : 失败教训（结构化：什么改动 → 什么后果 → 为什么）
- PATTERN : 可复用成功模式（跨 skill 迁移，用于新 skill 冷启动）

存储为 UTF-8 JSONL，append 语义，天然支持增量与去重查询。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .config import MemoryConfig
from .types import MemoryEntry, MemoryLevel


class MemoryStore:
    """基于 JSONL 的三层记忆库。"""

    def __init__(self, config: MemoryConfig):
        self._cfg = config
        self._path = config.path or Path(".skillforge") / "memory.jsonl"

    # ------------------------------------------------------------------ #
    # 写入
    # ------------------------------------------------------------------ #

    def add(self, entry: MemoryEntry) -> None:
        if not self._cfg.enabled:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def add_lesson(
        self,
        skill_name: str,
        *,
        change: str,
        effect: str,
        cause: str,
        iteration: int = 0,
    ) -> None:
        """记录一条失败教训。"""
        self.add(
            MemoryEntry(
                level=MemoryLevel.LESSON,
                skill_name=skill_name,
                iteration=iteration,
                content={"change": change, "effect": effect, "cause": cause},
            )
        )

    def add_pattern(
        self,
        skill_name: str,
        *,
        pattern: str,
        context: str,
        iteration: int = 0,
    ) -> None:
        """记录一条可复用成功模式。"""
        self.add(
            MemoryEntry(
                level=MemoryLevel.PATTERN,
                skill_name=skill_name,
                iteration=iteration,
                content={"pattern": pattern, "context": context},
            )
        )

    # ------------------------------------------------------------------ #
    # 查询
    # ------------------------------------------------------------------ #

    def iter_entries(self) -> Iterable[MemoryEntry]:
        if not self._path.exists():
            return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                yield MemoryEntry(
                    level=MemoryLevel(raw["level"]),
                    skill_name=raw["skill_name"],
                    iteration=int(raw.get("iteration", 0)),
                    content=raw.get("content", {}),
                )
            except (KeyError, ValueError):
                continue

    def patterns(
        self, skill_name: str | None = None, limit: int | None = None
    ) -> list[MemoryEntry]:
        """检索可复用模式（默认跨 skill，用于冷启动注入）。"""
        out = [
            e
            for e in self.iter_entries()
            if e.level is MemoryLevel.PATTERN
            and (skill_name is None or e.skill_name == skill_name)
        ]
        limit = limit or self._cfg.max_patterns_injected
        return out[-limit:]

    def lessons(
        self, skill_name: str, limit: int = 10
    ) -> list[MemoryEntry]:
        """检索某 skill 的失败教训。"""
        return [
            e
            for e in self.iter_entries()
            if e.level is MemoryLevel.LESSON and e.skill_name == skill_name
        ][-limit:]

    def format_for_prompt(
        self, skill_name: str, limit: int | None = None
    ) -> str:
        """把可复用模式格式化为可注入 proposer 的文本（含 token 预算）。"""
        pats = self.patterns(skill_name=None, limit=limit)
        if not pats:
            return ""
        lines = ["## 历史可复用经验（跨 skill）"]
        for p in pats:
            c = p.content
            lines.append(
                f"- [{p.skill_name}] {c.get('pattern', '')} "
                f"(场景: {c.get('context', '')})"
            )
        return "\n".join(lines)
