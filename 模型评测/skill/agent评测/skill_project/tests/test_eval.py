"""评测器测试（含 UTF-8 处理验证）。"""

from __future__ import annotations

from pathlib import Path

from skillforge.evaluate import LocalEvaluator
from skillforge.gt import load_gt
from skillforge.target import SkillTarget
from skillforge.types import Split

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "examples" / "hello-skill"


def test_local_eval_dev_baseline():
    target = SkillTarget(SKILL)
    gt = load_gt(SKILL / "evals.json")
    ev = LocalEvaluator()
    r = ev.evaluate(target, gt, Split.DEV)
    # 4 条 dev：case_1、case_2 通过，case_3（缺 security）、case_4（缺 example）失败
    assert r.total == 4
    assert r.passed == 2
    assert r.pass_rate == 0.5


def test_local_eval_regression_all_pass():
    target = SkillTarget(SKILL)
    gt = load_gt(SKILL / "evals.json")
    ev = LocalEvaluator()
    r = ev.evaluate(target, gt, Split.REGRESSION)
    assert r.pass_rate == 1.0


def test_utf8_em_dash_is_read():
    # SKILL.md 含 em dash "—"，验证 UTF-8 读取不崩
    target = SkillTarget(SKILL)
    snap = target.snapshot()
    assert "—" in snap.skill_md
