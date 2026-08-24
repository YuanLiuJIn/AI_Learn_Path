"""进化循环驱动（8 阶段）。

Setup → [Review → Propose → Apply → Verify → Gate → Log] → Loop-Control
集成 Beam Search：每轮生成 K 个候选，保留通过门控且质量最优者作为新起点。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Mapping

from .config import EvolutionConfig
from .evaluate.base import Evaluator
from .gate import Gate, GateContext
from .gitops import GitWorkspace
from .memory import MemoryStore
from .proposer import Proposer, ProposeContext
from .target import SkillTarget
from .types import (
    EvalResult,
    GateAction,
    GroundTruth,
    MemoryLevel,
    MemoryEntry,
    MutationLayer,
    Split,
)


@dataclass
class EvolutionReport:
    """一次进化运行的结果报告。"""

    iterations: int
    baseline_pass_rate: float
    final_pass_rate: float
    kept: int = 0
    discarded: int = 0
    best_content: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def improvement(self) -> float:
        return self.final_pass_rate - self.baseline_pass_rate


class EvolutionLoop:
    """驱动 8 阶段进化循环。"""

    def __init__(
        self,
        config: EvolutionConfig,
        target: SkillTarget,
        gt: GroundTruth,
        evaluator: Evaluator,
        proposer: Proposer,
        gate: Gate,
        *,
        memory: MemoryStore | None = None,
        git: GitWorkspace | None = None,
    ):
        self._cfg = config
        self._target = target
        self._gt = gt
        self._evaluator = evaluator
        self._proposer = proposer
        self._gate = gate
        self._memory = memory or MemoryStore(config.memory)
        self._git = git

    # ------------------------------------------------------------------ #

    def run(self) -> EvolutionReport:
        skill_name = self._target.path.name

        # ---- Phase 0: baseline ----
        baseline = self._evaluator.run_all(self._target, self._gt)
        base_rate = baseline.get(Split.DEV, _empty()).pass_rate
        best_rate = base_rate
        best_content = self._target.read_skill_md()
        history: list[str] = []

        if self._git is not None:
            self._git.ensure_initialized()

        # ---- Phase 1-8: loop ----
        layer = MutationLayer.TRIGGER
        plateau = 0
        kept = 0
        discarded = 0
        notes: list[str] = []

        for it in range(self._cfg.search.max_iterations):
            memory_text = self._memory.format_for_prompt(skill_name)

            # Phase 1 (Review) + Phase 2/3 (Propose)
            failed = baseline[Split.DEV].failed_cases
            ctx = ProposeContext(
                target=self._target,
                gt=self._gt,
                baseline=baseline,
                layer=layer,
                failed_cases=failed,
                memory_text=memory_text,
                history=tuple(history),
            )
            try:
                candidates = self._proposer.propose(
                    ctx, n=self._cfg.search.beam_width
                )
            except RuntimeError as e:
                # 无 LLM 后端：无法 propose，提前结束并报告 baseline
                notes.append(f"停止于第 {it} 轮：{e}")
                break

            round_best_rate = best_rate
            round_kept = 0

            for cand in candidates:
                # Phase 4 (Apply) + Phase 5 (Verify)
                self._target.write_skill_md(cand.content)
                results = self._evaluator.run_all(self._target, self._gt)

                # Phase 6 (Gate)
                decision = self._gate.decide(
                    GateContext(baseline=baseline, candidate=results)
                )

                if decision.passed:
                    round_kept += 1
                    kept += 1
                    rate = results[Split.DEV].pass_rate
                    if rate > round_best_rate:
                        round_best_rate = rate
                        best_rate = rate
                        best_content = cand.content
                    history.append(cand.description)
                    if self._git is not None:
                        self._git.snapshot(f"keep: {cand.description}")
                    self._memory.add_pattern(
                        skill_name,
                        pattern=cand.description,
                        context="通过门控",
                        iteration=it,
                    )
                else:
                    discarded += 1
                    # 回滚本次改动
                    self._target.write_skill_md(best_content)
                    self._memory.add_lesson(
                        skill_name,
                        change=cand.description,
                        effect="; ".join(decision.reasons),
                        cause="门控不通过",
                        iteration=it,
                    )

            # Phase 8 (Loop control)
            if round_kept > 0:
                plateau = 0
            else:
                plateau += 1
                if plateau >= self._cfg.search.plateau_threshold:
                    if layer is MutationLayer.TRIGGER:
                        layer = MutationLayer.BODY
                        notes.append(f"第 {it} 轮触发层 plateau，升至 BODY 层")
                    elif layer is MutationLayer.BODY:
                        layer = MutationLayer.SCRIPT
                        notes.append(f"第 {it} 轮 BODY 层 plateau，升至 SCRIPT 层")
                    else:
                        notes.append(f"第 {it} 轮三层均 plateau，终止")
                        break
                    plateau = 0

            baseline = {
                s: self._evaluator.evaluate(self._target, self._gt, s)
                for s in Split
            }

        # 收敛到 best
        self._target.write_skill_md(best_content)

        return EvolutionReport(
            iterations=len(history),
            baseline_pass_rate=base_rate,
            final_pass_rate=best_rate,
            kept=kept,
            discarded=discarded,
            best_content=best_content,
            notes=notes,
        )


def _empty() -> EvalResult:
    return EvalResult(split=Split.DEV, cases=())
