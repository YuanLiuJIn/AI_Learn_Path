"""GT 加载与校验测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from skillforge.gt import GTError, load_gt
from skillforge.types import Split

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "examples" / "hello-skill" / "evals.json"


def test_load_gt_splits():
    gt = load_gt(EVALS)
    assert len(gt) == 8
    assert len(gt.dev) == 4
    assert len(gt.holdout) == 2
    assert len(gt.regression) == 2


def test_assertion_parsing():
    gt = load_gt(EVALS)
    case3 = next(c for c in gt.dev if c.id == "case_3")
    types = {a.type.value for a in case3.assertions}
    assert types == {"contains", "not_contains"}


def test_missing_prompt_raises():
    with pytest.raises(GTError):
        from skillforge.gt import from_dict

        from_dict({"evals": [{"assertions": [{"type": "contains", "value": "x"}]}]})


def test_bad_split_raises():
    from skillforge.gt import from_dict

    with pytest.raises(GTError):
        from_dict(
            {
                "evals": [
                    {
                        "prompt": "hi",
                        "split": "nope",
                        "assertions": [{"type": "contains", "value": "x"}],
                    }
                ]
            }
        )
