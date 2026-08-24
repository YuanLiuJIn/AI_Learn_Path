"""优化目标抽象。

统一封装"被优化的对象"：一个 Skill 目录（SKILL.md + references/ + scripts/）。
支持读取、快照、原子写入、生成 unified diff，以及按突变层定位可改区域。
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from .types import MutationLayer

# Skill 目录内参与进化的文本文件扩展名（prose）
_PROSE_SUFFIXES = (".md", ".txt")


class SkillTargetError(Exception):
    """目标读取/写入异常。"""


@dataclass(frozen=True)
class Snapshot:
    """目标内容的不可变快照，用于生成 diff 与回滚。"""

    skill_md: str
    prose: dict[str, str]  # 相对路径 -> 内容

    @property
    def corpus(self) -> str:
        """SKILL.md + 所有 references/agents 文本的合并视图（供静态评测）。"""
        parts = [f"### SKILL.md ###\n{self.skill_md}"]
        for rel, text in sorted(self.prose.items()):
            parts.append(f"### {rel} ###\n{text}")
        return "\n\n".join(parts)


class SkillTarget:
    """一个可进化的 Skill 目录。

    只读入口提供内容，写入口在传入新内容后返回 diff，避免隐式副作用。
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.skill_md_path = self.path / "SKILL.md"

    # ------------------------------------------------------------------ #
    # 读取
    # ------------------------------------------------------------------ #

    def snapshot(self) -> Snapshot:
        if not self.skill_md_path.exists():
            raise SkillTargetError(f"SKILL.md 不存在: {self.skill_md_path}")
        skill_md = self.skill_md_path.read_text(encoding="utf-8")
        prose: dict[str, str] = {}
        for sub in ("references", "agents"):
            subdir = self.path / sub
            if subdir.is_dir():
                for f in sorted(subdir.rglob("*")):
                    if f.is_file() and f.suffix in _PROSE_SUFFIXES:
                        prose[str(f.relative_to(self.path))] = f.read_text(
                            encoding="utf-8"
                        )
        return Snapshot(skill_md=skill_md, prose=prose)

    def read_skill_md(self) -> str:
        return self.snapshot().skill_md

    # ------------------------------------------------------------------ #
    # 写入
    # ------------------------------------------------------------------ #

    def write_skill_md(self, new_content: str) -> str:
        """写回 SKILL.md 并返回 unified diff。"""
        old = self.skill_md_path.read_text(encoding="utf-8")
        self.skill_md_path.write_text(new_content, encoding="utf-8")
        return self._diff("SKILL.md", old, new_content)

    def write_prose(self, rel_path: str, new_content: str) -> str:
        """写回 references/agents 下的文本文件并返回 diff。"""
        target = (self.path / rel_path).resolve()
        if not str(target).startswith(str(self.path.resolve())):
            raise SkillTargetError(f"非法路径: {rel_path}")
        old = target.read_text(encoding="utf-8") if target.exists() else ""
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_content, encoding="utf-8")
        return self._diff(rel_path, old, new_content)

    @staticmethod
    def _diff(name: str, old: str, new: str) -> str:
        return "".join(
            difflib.unified_diff(
                old.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile=f"a/{name}",
                tofile=f"b/{name}",
            )
        )

    # ------------------------------------------------------------------ #
    # 分层突变定位
    # ------------------------------------------------------------------ #

    def locate_layer(self, layer: MutationLayer) -> tuple[str, ...]:
        """返回给定突变层可修改的区域标识，供 proposer 定位。"""
        if layer is MutationLayer.TRIGGER:
            # 触发层：frontmatter 的 description 字段
            return ("SKILL.md::frontmatter::description",)
        if layer is MutationLayer.BODY:
            return ("SKILL.md::body",)
        snap = self.snapshot()
        return tuple(f"{rel}::body" for rel in snap.prose)
