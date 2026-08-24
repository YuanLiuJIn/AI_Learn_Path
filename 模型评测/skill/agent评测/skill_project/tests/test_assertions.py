"""断言执行引擎测试。"""

from __future__ import annotations

from skillforge.assertions import evaluate
from skillforge.types import Assertion, AssertionType


def test_contains():
    a = Assertion(AssertionType.CONTAINS, "hello")
    ok, _ = evaluate(a, "hello world")
    assert ok
    ok, _ = evaluate(a, "goodbye")
    assert not ok


def test_not_contains():
    a = Assertion(AssertionType.NOT_CONTAINS, "secret")
    ok, _ = evaluate(a, "public info")
    assert ok
    ok, _ = evaluate(a, "the secret is out")
    assert not ok


def test_regex():
    a = Assertion(AssertionType.REGEX, r"line\s*\d+")
    ok, _ = evaluate(a, "see line 42")
    assert ok
    ok, _ = evaluate(a, "no numbers here")
    assert not ok


def test_llm_assertion_needs_judge():
    a = Assertion(AssertionType.PATH_HIT, "refs/x.md")
    ok, reason = evaluate(a, "text", judge=None)
    assert not ok
    assert "LLM" in reason
