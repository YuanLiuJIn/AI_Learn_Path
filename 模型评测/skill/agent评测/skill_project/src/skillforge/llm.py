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


class OpenAICompatibleBackend(LLMBackend):
    """OpenAI 兼容的 ``chat/completions`` 后端。

    支持所有提供 OpenAI 兼容接口的服务（OpenAI / DeepSeek / 通义 / 混元 /
    vLLM / Ollama 等）。零第三方依赖，用标准库 ``urllib`` 实现。

    参数
    ----
    base_url:
        服务的 ``/v1`` 地址，例如 ``https://api.openai.com/v1`` 或
        ``http://localhost:11434/v1``（Ollama）。
    api_key:
        API key；本地服务（Ollama/vLLM）可传空字符串。
    model:
        模型名。
    """

    name = "openai"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 120,
        temperature: float = 0.2,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature

    def complete(
        self, messages: Sequence[dict[str, str]], **kwargs: Any
    ) -> str:
        import json
        import urllib.error
        import urllib.request

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": kwargs.get("temperature", self.temperature),
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"LLM 请求失败 ({e.code}): {detail}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"LLM 连接失败: {e.reason}") from e

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"LLM 响应格式异常: {body!r}") from e


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
