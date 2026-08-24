"""Ground-Truth 加载与校验。

支持两种 JSON 结构：``{"evals": [...]}`` 与 ``{"cases": [...]}``，
并做 schema 校验，失败时给出可读的错误信息（而非裸 traceback）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .types import Assertion, GroundTruth, Split, TestCase


class GTError(Exception):
    """GT 文件格式错误。"""


def load_gt(path: str | Path) -> GroundTruth:
    """从 JSON 文件加载 GT。"""
    p = Path(path)
    if not p.exists():
        raise GTError(f"GT 文件不存在: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise GTError(f"GT 不是合法 JSON: {e}") from e
    return from_dict(data)


def from_dict(data: Mapping[str, Any]) -> GroundTruth:
    raw_cases = data.get("evals", data.get("cases"))
    if not isinstance(raw_cases, list):
        raise GTError("GT 缺少 'evals' 或 'cases' 列表")

    cases: list[TestCase] = []
    for i, c in enumerate(raw_cases):
        if not isinstance(c, Mapping):
            raise GTError(f"第 {i} 条用例不是对象: {c!r}")
        cases.append(_parse_case(c, i))
    return GroundTruth(tuple(cases))


def _parse_case(raw: Mapping[str, Any], idx: int) -> TestCase:
    prompt = raw.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise GTError(f"第 {idx} 条用例缺少 'prompt'")

    raw_assertions = raw.get("assertions")
    if not isinstance(raw_assertions, list) or not raw_assertions:
        raise GTError(f"第 {idx} 条用例缺少非空 'assertions'")

    assertions = tuple(_parse_assertion(a, idx) for a in raw_assertions)

    split_raw = raw.get("split", "dev")
    try:
        split = Split(split_raw)
    except ValueError as e:
        raise GTError(
            f"第 {idx} 条用例的 split 非法: {split_raw!r}"
        ) from e

    case_id = str(raw.get("id", f"case_{idx}"))
    return TestCase(
        id=case_id,
        prompt=prompt,
        assertions=assertions,
        split=split,
        metadata=dict(raw.get("metadata", {})),
    )


def _parse_assertion(raw: Any, case_idx: int) -> Assertion:
    if not isinstance(raw, Mapping) or "type" not in raw or "value" not in raw:
        raise GTError(
            f"第 {case_idx} 条用例的断言缺少 'type'/'value': {raw!r}"
        )
    try:
        return Assertion.from_dict(raw)
    except (ValueError, KeyError) as e:
        raise GTError(f"第 {case_idx} 条用例的断言非法: {e}") from e
