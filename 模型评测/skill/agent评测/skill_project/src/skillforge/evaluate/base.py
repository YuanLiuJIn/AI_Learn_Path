"""评测器抽象基类。

统一评测器接口，使静态评测（LocalEvaluator）与端到端评测（SandboxEvaluator）
可互换，供循环驱动按配置选择。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..target import SkillTarget
from ..types import EvalResult, GroundTruth, Split


class Evaluator(ABC):
    """对一个 skill 目标在给定数据切分上评测。"""

    name: str = "base"

    @abstractmethod
    def evaluate(
        self,
        target: SkillTarget,
        gt: GroundTruth,
        split: Split,
    ) -> EvalResult:
        """评测并返回汇总结果。"""

    def run_all(
        self, target: SkillTarget, gt: GroundTruth
    ) -> dict[Split, EvalResult]:
        """对所有切分评测，返回 {split: result}。"""
        return {s: self.evaluate(target, gt, s) for s in Split}
