"""门控与统计显著性测试。"""

from __future__ import annotations

from skillforge.config import GateConfig
from skillforge.gate import Gate, GateContext, bootstrap_mean_diff_significant
from skillforge.types import CaseResult, EvalResult, GateAction, Split


def _result(pass_rate: float, n: int = 10) -> EvalResult:
    passed = round(pass_rate * n)
    cases = tuple(
        CaseResult(case_id=f"c{i}", passed=i < passed) for i in range(n)
    )
    return EvalResult(split=Split.DEV, cases=cases)


def test_significant_detects_improvement():
    a = [0.5] * 20
    b = [0.8] * 20
    ok, lower = bootstrap_mean_diff_significant(a, b)
    assert ok
    assert lower > 0


def test_significant_rejects_noise():
    # 两组均值接近但波动大 → 不应判定显著
    a = [0.5, 0.6, 0.4, 0.55, 0.45] * 4
    b = [0.52, 0.58, 0.42, 0.53, 0.47] * 4
    ok, _ = bootstrap_mean_diff_significant(a, b)
    assert not ok


def test_gate_keeps_quality_improvement():
    gate = Gate(GateConfig(min_delta=0.02))
    base = _result(0.5)
    cand = _result(0.8)
    d = gate.decide(GateContext(baseline={Split.DEV: base}, candidate={Split.DEV: cand}))
    assert d.passed
    assert d.action is GateAction.KEEP


def test_gate_discards_regression():
    gate = Gate(GateConfig(min_delta=0.02))
    base = _result(0.8)
    cand = _result(0.85)
    # 质量提升了，但 regression 集大幅退化
    reg_base = EvalResult(Split.REGRESSION, cases=(CaseResult("r", True),))
    reg_cand = EvalResult(Split.REGRESSION, cases=(CaseResult("r", False),))
    d = gate.decide(
        GateContext(
            baseline={Split.DEV: base, Split.REGRESSION: reg_base},
            candidate={Split.DEV: cand, Split.REGRESSION: reg_cand},
        )
    )
    assert not d.passed
    assert d.dimensions["regression"] is False
