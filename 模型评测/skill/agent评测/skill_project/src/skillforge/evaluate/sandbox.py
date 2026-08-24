"""端到端沙箱评测器（能力验证）。

核心改进点（借鉴 Voyager 的环境反馈思想）：不满足于"文档里写了什么"，
而是在隔离目录里真正"执行" skill，对**执行产物**做断言。

skill 本质是给 LLM 的指令文本，因此"执行"需要一个 runner（LLM agent）。
runner 抽象为可插拔接口，用户可接入 Claude Code 或自定义 agent 框架；
纯文本 LLM 后端则退化为"给定 skill + 用户问题，直接生成响应"的简化执行。
"""

from __future__ import annotations

import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..assertions import evaluate
from ..llm import BinaryJudge, LLMBackend
from ..target import SkillTarget
from ..types import CaseResult, EvalResult, GroundTruth, Split
from .base import Evaluator


@dataclass(frozen=True)
class SandboxOutcome:
    """一次 skill 执行的结果。"""

    output: str                      # 执行后的响应文本（供 contains/regex 判定）
    artifacts_dir: Path              # 产物目录（供 file_exists/schema/script 判定）
    tokens: int = 0
    duration_ms: int = 0


class SkillRunner(ABC):
    """在隔离环境中"执行" skill 的代理。"""

    name: str = "base"

    @abstractmethod
    def run(
        self, skill_corpus: str, prompt: str, workdir: Path
    ) -> SandboxOutcome:
        """给定 skill 内容与用户问题，在 workdir 里执行并返回结果。"""


class LLMSkillRunner(SkillRunner):
    """基于纯文本 LLM 的简化 runner。

    将 skill 内容 + 用户问题拼成一条消息，让模型扮演执行 agent 输出响应。
    不涉及真实工具调用；适合验证"skill 指令能否诱导正确回答"这类能力。
    """

    name = "llm"

    def __init__(self, backend: LLMBackend):
        self._backend = backend

    def run(
        self, skill_corpus: str, prompt: str, workdir: Path
    ) -> SandboxOutcome:
        start = time.monotonic()
        messages = [
            {
                "role": "system",
                "content": (
                    "你是按照下面 skill 指令工作的 agent。请严格遵循 skill 的"
                    "要求回答问题，并尽可能给出符合其输出格式的结果。\n\n"
                    f"{skill_corpus}"
                ),
            },
            {"role": "user", "content": prompt},
        ]
        output = self._backend.complete(messages)
        duration = int((time.monotonic() - start) * 1000)
        return SandboxOutcome(
            output=output,
            artifacts_dir=workdir,
            tokens=self._backend.estimate_tokens(skill_corpus + prompt + output),
            duration_ms=duration,
        )


class SandboxEvaluator(Evaluator):
    """端到端评测器：对 skill 的执行产物做断言。

    contains / regex 针对**执行输出**判定；file_exists / json_schema /
    script_check 针对**产物目录**判定。
    """

    name = "sandbox"

    def __init__(
        self,
        runner: SkillRunner,
        judge: BinaryJudge | None = None,
        timeout_seconds: int = 30,
    ):
        self._runner = runner
        self._judge = judge
        self._timeout = timeout_seconds

    def evaluate(
        self, target: SkillTarget, gt: GroundTruth, split: Split
    ) -> EvalResult:
        corpus = target.snapshot().corpus
        results: list[CaseResult] = []
        with tempfile.TemporaryDirectory(prefix="skillforge-sandbox-") as td:
            base = Path(td)
            for case in gt.by_split(split):
                results.append(self._eval_case(case, corpus, base))
        total_tokens = sum(r.tokens for r in results)
        total_ms = sum(r.duration_ms for r in results)
        return EvalResult(
            split=split,
            cases=tuple(results),
            tokens=total_tokens,
            duration_ms=total_ms,
        )

    def _eval_case(
        self, case, corpus: str, base: Path
    ) -> CaseResult:
        workdir = base / case.id
        workdir.mkdir(parents=True, exist_ok=True)
        outcome = self._runner.run(corpus, case.prompt, workdir)

        failed: list[str] = []
        for assertion in case.assertions:
            ok, reason = evaluate(
                assertion,
                outcome.output,
                judge=self._judge.judge if self._judge else None,
                artifacts_dir=outcome.artifacts_dir,
            )
            if not ok:
                failed.append(reason)

        # 保存执行产物，供 trace 诊断
        trace = {
            "output": outcome.output,
            "artifacts_dir": str(outcome.artifacts_dir),
        }
        return CaseResult(
            case_id=case.id,
            passed=not failed,
            failed_assertions=tuple(failed),
            trace=trace,
            tokens=outcome.tokens,
            duration_ms=outcome.duration_ms,
        )
