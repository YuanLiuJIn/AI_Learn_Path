"""命令行入口。

用法示例::

    # 只评测 baseline（无需 LLM）
    skillforge eval --skill examples/hello-skill --gt examples/hello-skill/evals.json

    # 完整进化（需要 LLM 后端）
    skillforge evolve --skill examples/hello-skill --gt examples/hello-skill/evals.json \\
        --max-iterations 5 --beam-width 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import EvolutionConfig
from .evaluate import LLMSkillRunner, LocalEvaluator, SandboxEvaluator
from .gate import Gate
from .gitops import GitWorkspace
from .gt import load_gt
from .llm import BinaryJudge, LLMBackend, NullBackend
from .loop import EvolutionLoop
from .memory import MemoryStore
from .proposer import LLMProposer
from .target import SkillTarget


def _build_backend() -> LLMBackend:
    """尝试从环境变量构造后端；未配置则返回 NullBackend。"""
    # 支持 EVOLVER_LLM_URL（OpenAI 兼容接口）——留待用户实现具体适配
    return NullBackend()


def _build_evaluator(cfg: EvolutionConfig, backend: LLMBackend):
    if cfg.eval.sandbox:
        runner = LLMSkillRunner(backend)
        judge = BinaryJudge(backend)
        return SandboxEvaluator(runner, judge, cfg.eval.sandbox_timeout_seconds)
    return LocalEvaluator(BinaryJudge(backend))


def _load_config(args: argparse.Namespace) -> EvolutionConfig:
    if args.config:
        cfg = EvolutionConfig.from_json(args.config)
    else:
        cfg = EvolutionConfig()
    if args.skill:
        cfg.skill_path = Path(args.skill)
    if args.gt:
        cfg.gt_path = Path(args.gt)
    if args.max_iterations is not None:
        cfg.search.max_iterations = args.max_iterations
    if args.beam_width is not None:
        cfg.search.beam_width = args.beam_width
    if args.workspace:
        cfg.workspace = Path(args.workspace)
    return cfg


def cmd_eval(args: argparse.Namespace) -> int:
    cfg = _load_config(args)
    target = SkillTarget(cfg.skill_path)
    gt = load_gt(cfg.gt_path)
    backend = _build_backend()
    evaluator = _build_evaluator(cfg, backend)

    results = evaluator.run_all(target, gt)
    for split, r in results.items():
        print(
            f"[{split.value}] pass_rate={r.pass_rate:.3f} "
            f"({r.passed}/{r.total})"
        )
        for c in r.failed_cases:
            print(f"  - {c.case_id}: {c.failed_assertions}")
    return 0


def cmd_evolve(args: argparse.Namespace) -> int:
    cfg = _load_config(args)
    if cfg.skill_path is None or cfg.gt_path is None:
        print("错误：evolve 需要 --skill 与 --gt", file=sys.stderr)
        return 2

    target = SkillTarget(cfg.skill_path)
    gt = load_gt(cfg.gt_path)
    backend = _build_backend()
    evaluator = _build_evaluator(cfg, backend)
    gate = Gate(cfg.gate)
    proposer = LLMProposer(backend)
    memory = MemoryStore(cfg.memory)
    git = (
        GitWorkspace(cfg.workspace or Path(".skillforge") / "ws")
        if args.git
        else None
    )

    loop = EvolutionLoop(
        cfg, target, gt, evaluator, proposer, gate, memory=memory, git=git
    )
    report = loop.run()

    print(f"baseline pass_rate = {report.baseline_pass_rate:.3f}")
    print(f"final    pass_rate = {report.final_pass_rate:.3f}")
    print(f"improvement        = {report.improvement:+.3f}")
    print(f"kept={report.kept} discarded={report.discarded}")
    for note in report.notes:
        print(f"[note] {note}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="SkillForge —— 更整洁的 Skill 自进化引擎",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--skill", help="目标 skill 目录")
        p.add_argument("--gt", help="GT JSON 文件")
        p.add_argument("--config", help="配置文件（JSON）")
        p.add_argument("--workspace", help="工作区目录")
        p.add_argument("--max-iterations", type=int)
        p.add_argument("--beam-width", type=int)

    p_eval = sub.add_parser("eval", help="只评测 baseline")
    _add_common(p_eval)

    p_evolve = sub.add_parser("evolve", help="完整进化循环")
    _add_common(p_evolve)
    p_evolve.add_argument(
        "--git", action="store_true", help="启用 git 隔离工作区"
    )

    args = parser.parse_args(argv)
    if args.command == "eval":
        return cmd_eval(args)
    if args.command == "evolve":
        return cmd_evolve(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
