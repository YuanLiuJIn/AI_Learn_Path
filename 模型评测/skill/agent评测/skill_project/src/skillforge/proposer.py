"""候选生成层（搜索的"提出"半边）。

proposer 负责：读当前 skill 内容 + 失败 case + 历史经验，产出候选改动。
与"评测/门控"（验证半边）解耦，使搜索策略（贪心 / Beam）可替换。

借鉴 Meta-Harness：诊断必须基于真实失败 trace 做反事实推理，而非凭空猜测。
"""

from __future__ import annotations

import difflib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Sequence

from .llm import LLMBackend
from .target import SkillTarget
from .types import (
    CaseResult,
    Candidate,
    EvalResult,
    GroundTruth,
    MutationLayer,
    Split,
)


@dataclass
class ProposeContext:
    """提案所需的全部上下文。"""

    target: SkillTarget
    gt: GroundTruth
    baseline: Mapping[Split, EvalResult]
    layer: MutationLayer
    # 上一轮失败的 case（诊断依据）
    failed_cases: Sequence[CaseResult] = ()
    # 历史经验文本（跨 skill 可复用模式）
    memory_text: str = ""
    # 上一轮的候选描述（避免重复试同一个方向）
    history: Sequence[str] = ()


class Proposer(ABC):
    """候选生成器接口。"""

    name: str = "base"

    @abstractmethod
    def propose(self, ctx: ProposeContext, n: int = 1) -> list[Candidate]:
        """生成 n 个候选改动。"""


class LLMProposer(Proposer):
    """基于 LLM 的候选生成器：诊断失败 → 提出修改 → 输出新 SKILL.md。

    产出完整的新的 SKILL.md 文本，由调用方负责 diff 与分层约束。
    """

    name = "llm"

    def __init__(self, backend: LLMBackend):
        self._backend = backend

    def propose(self, ctx: ProposeContext, n: int = 1) -> list[Candidate]:
        candidates: list[Candidate] = []
        for i in range(n):
            content = self._generate_new_skill_md(ctx, i, n)
            old = ctx.target.read_skill_md()
            diff = self._diff(old, content)
            candidates.append(
                Candidate(
                    id=f"cand-{i}",
                    description=self._describe(ctx, i),
                    layer=ctx.layer,
                    diff=diff,
                    content=content,
                )
            )
        return candidates

    def _generate_new_skill_md(
        self, ctx: ProposeContext, idx: int, total: int
    ) -> str:
        prompt = self._build_prompt(ctx, idx, total)
        return self._backend.complete([{"role": "user", "content": prompt}])

    def _build_prompt(
        self, ctx: ProposeContext, idx: int, total: int
    ) -> str:
        current = ctx.target.read_skill_md()
        failures = "\n".join(
            f"- case {c.case_id}: {c.failed_assertions}"
            for c in ctx.failed_cases[:5]
        ) or "(无失败 case)"
        history = "\n".join(f"- {h}" for h in ctx.history[-5:]) or "(无)"

        layer_hint = {
            MutationLayer.TRIGGER: "只修改 frontmatter 的 description（触发词），不动正文",
            MutationLayer.BODY: "只修改正文指令（What You Do / Rules / Output Format）",
            MutationLayer.SCRIPT: "可修改 references/scripts 的辅助内容",
        }[ctx.layer]

        return f"""你是 skill 优化器。请根据失败用例，对下面的 SKILL.md 做**一次最小、原子**的修改。

## 优化层约束
{layer_hint}。一次只做一处改动，不要同时改多个东西。

## 当前 SKILL.md
```markdown
{current}
```

## 失败的用例（dev 集）
{failures}

## 历史经验
{ctx.memory_text or "(无)"}

## 已尝试过的方向（避免重复）
{history}

## 输出要求
直接输出修改后的**完整 SKILL.md 内容**（含 frontmatter），不要输出任何解释。
这是第 {idx + 1}/{total} 个候选，请给出与其它候选不同的思路。"""

    @staticmethod
    def _describe(ctx: ProposeContext, idx: int) -> str:
        if ctx.failed_cases:
            c = ctx.failed_cases[0]
            return f"针对 case {c.case_id} 的候选 {idx + 1}"
        return f"候选 {idx + 1}"

    @staticmethod
    def _diff(old: str, new: str) -> str:
        return "".join(
            difflib.unified_diff(
                old.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile="a/SKILL.md",
                tofile="b/SKILL.md",
            )
        )
