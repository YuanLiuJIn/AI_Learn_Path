"""LLM 后端抽象与二元判定器。

常见的做法是把 LLM 调用散落在多个文件（claude/codex/opencode/http 各写一套）。
本项目统一为单一 ``LLMBackend`` 接口，方便接入任意推理后端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from .types import Assertion, AssertionType

_UTF8 = "utf-8"


class LLMBackend(ABC):
    """统一的 LLM 后端接口。"""

    name: str = "base"

    @abstractmethod
    def complete(
        self, messages: Sequence[dict[str, str]], **kwargs: Any
    ) -> str:
        """给定对话消息，返回模型补全文本。"""

    def estimate_tokens(self, text: str) -> int:
        """粗估 token 数（门控成本维度）。默认按约 4 字符/token。"""
        return max(1, len(text) // 4)


class NullBackend(LLMBackend):
    """无真实 LLM 时的占位后端：调用即抛错，提示接入真实后端。"""

    name = "null"

    def complete(
        self, messages: Sequence[dict[str, str]], **kwargs: Any
    ) -> str:
        raise RuntimeError(
            "未配置 LLM 后端。LLM 类断言（path_hit/fact_coverage）、"
            "诊断与修改阶段需要真实后端。"
        )


class BinaryJudge:
    """二元 LLM 判定器，用于 path_hit / fact_coverage 等语义断言。

    采用"先让模型只回答 YES/NO 并给出理由"的严格格式，避免自由发挥。
    """

    YES = "YES"
    NO = "NO"

    def __init__(self, backend: LLMBackend):
        self._backend = backend

    def judge(self, assertion: Assertion, text: str) -> tuple[bool, str]:
        prompt = self._build_prompt(assertion, text)
        try:
            raw = self._backend.complete(
                [{"role": "user", "content": prompt}]
            )
        except RuntimeError as e:
            return False, f"LLM 后端不可用: {e}"
        return self._parse(raw, assertion.type)

    def _build_prompt(self, assertion: Assertion, text: str) -> str:
        if assertion.type is AssertionType.PATH_HIT:
            question = (
                f"根据下面的 skill 内容，判断用户问题是否应该命中路径 "
                f"{assertion.value!r}。"
            )
        else:  # FACT_COVERAGE
            question = (
                f"根据下面的 skill 内容，判断它是否覆盖了关键事实："
                f"{assertion.value!r}。"
            )
        return (
            f"{question}\n"
            f"请只回答 YES 或 NO，然后换行写一句理由。\n\n"
            f"--- skill 内容 ---\n{text}"
        )

    def _parse(self, raw: str, atype: AssertionType) -> tuple[bool, str]:
        first = raw.strip().splitlines()[0].strip().upper() if raw.strip() else ""
        ok = first.startswith(self.YES)
        return ok, f"judge({atype.value}) -> {raw.strip()[:60]}"
