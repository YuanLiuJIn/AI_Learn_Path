"""跑一次真实实验的完整示例。

演示从 baseline 评测到自主进化的完整流程：用 hello-skill（code-review-helper）
作为实验对象，让 LLM 诊断"缺少 security / example 维度"并自动改写 SKILL.md。

用法（PowerShell）::

    $env:SKILLFORGE_BASE_URL="https://api.openai.com/v1"
    $env:SKILLFORGE_API_KEY="sk-xxx"
    $env:SKILLFORGE_MODEL="gpt-4o-mini"
    py examples/run_experiment.py

支持任意 OpenAI 兼容服务（DeepSeek / 通义 / 混元 / vLLM / Ollama 等）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# 让脚本可直接运行（不依赖 pip install -e）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from skillforge.config import EvolutionConfig  # noqa: E402
from skillforge.evaluate import LocalEvaluator  # noqa: E402
from skillforge.gate import Gate  # noqa: E402
from skillforge.gt import load_gt  # noqa: E402
from skillforge.llm import (  # noqa: E402
    BinaryJudge,
    NullBackend,
    OpenAICompatibleBackend,
)
from skillforge.loop import EvolutionLoop  # noqa: E402
from skillforge.memory import MemoryStore  # noqa: E402
from skillforge.proposer import LLMProposer  # noqa: E402
from skillforge.target import SkillTarget  # noqa: E402


def build_backend() -> OpenAICompatibleBackend | NullBackend:
    base_url = os.environ.get("SKILLFORGE_BASE_URL") or os.environ.get(
        "OPENAI_BASE_URL"
    )
    api_key = (
        os.environ.get("SKILLFORGE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    )
    model = (
        os.environ.get("SKILLFORGE_MODEL")
        or os.environ.get("OPENAI_MODEL")
        or "gpt-4o-mini"
    )
    if base_url:
        return OpenAICompatibleBackend(base_url, api_key, model)
    return NullBackend()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skill_dir = root / "examples" / "hello-skill"
    gt_path = skill_dir / "evals.json"

    backend = build_backend()
    if isinstance(backend, NullBackend):
        print(
            "未配置 LLM 后端。请设置环境变量：\n"
            "  SKILLFORGE_BASE_URL / SKILLFORGE_API_KEY / SKILLFORGE_MODEL"
        )
        return 1

    print(f"LLM 后端: model={backend.model} base_url={backend.base_url}")

    target = SkillTarget(skill_dir)
    gt = load_gt(gt_path)
    evaluator = LocalEvaluator(BinaryJudge(backend))
    gate = Gate(EvolutionConfig().gate)
    proposer = LLMProposer(backend)
    memory = MemoryStore(EvolutionConfig().memory)

    # ---- 1. baseline ----
    print("\n=== baseline 评测 ===")
    baseline = evaluator.run_all(target, gt)
    for split, r in baseline.items():
        print(f"[{split.value}] pass_rate={r.pass_rate:.3f} ({r.passed}/{r.total})")
        for c in r.failed_cases:
            print(f"  - {c.case_id}: {c.failed_assertions}")

    # ---- 2. evolve ----
    print("\n=== 开始进化 ===")
    cfg = EvolutionConfig(skill_path=skill_dir, gt_path=gt_path)
    cfg.search.max_iterations = int(os.environ.get("SKILLFORGE_MAX_ITERS", "5"))
    cfg.search.beam_width = int(os.environ.get("SKILLFORGE_BEAM_WIDTH", "1"))
    loop = EvolutionLoop(
        cfg, target, gt, evaluator, proposer, gate, memory=memory
    )
    report = loop.run()

    # ---- 3. 结果 ----
    print("\n=== 进化结果 ===")
    print(
        f"baseline {report.baseline_pass_rate:.3f} -> final "
        f"{report.final_pass_rate:.3f} "
        f"(improvement {report.improvement:+.3f})"
    )
    print(f"kept={report.kept} discarded={report.discarded}")
    for note in report.notes:
        print(f"[note] {note}")

    # ---- 4. 进化后的 SKILL.md ----
    print("\n=== 进化后的 SKILL.md ===")
    print(target.read_skill_md())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
