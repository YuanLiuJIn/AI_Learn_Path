"""静态评测器（文档体检）。

断言直接针对 skill 的文本 corpus 判定（"SKILL.md 里是否写了 security 这个词"）。
优点是零依赖、可复现；缺点是测的是"文档"，不是"能力"。
"""

from __future__ import annotations

from ..assertions import evaluate
from ..llm import BinaryJudge
from ..target import SkillTarget
from ..types import CaseResult, EvalResult, GroundTruth, Split
from .base import Evaluator


class LocalEvaluator(Evaluator):
    """静态文本评测器。"""

    name = "local"

    def __init__(self, judge: BinaryJudge | None = None):
        self._judge = judge

    def evaluate(
        self, target: SkillTarget, gt: GroundTruth, split: Split
    ) -> EvalResult:
        corpus = target.snapshot().corpus
        results: list[CaseResult] = []
        for case in gt.by_split(split):
            results.append(self._eval_case(case, corpus))
        return EvalResult(split=split, cases=tuple(results))

    def _eval_case(self, case, corpus: str) -> CaseResult:
        failed: list[str] = []
        for assertion in case.assertions:
            ok, reason = evaluate(
                assertion, corpus, judge=self._judge.judge if self._judge else None
            )
            if not ok:
                failed.append(reason)
        return CaseResult(
            case_id=case.id,
            passed=not failed,
            failed_assertions=tuple(failed),
        )
