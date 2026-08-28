#!/usr/bin/env python3
"""比较三组 Reward 消融训练产生的离线轨迹。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.metrics import evaluate_records, load_jsonl
from src.reward import SUPPORTED_VARIANTS, load_reward_config


def parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must use VARIANT=PATH")
    variant, path = value.split("=", 1)
    if variant not in SUPPORTED_VARIANTS:
        raise argparse.ArgumentTypeError(
            f"Unknown variant {variant!r}; choose from {SUPPORTED_VARIANTS}"
        )
    return variant, Path(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Agentic-Search reward ablations")
    parser.add_argument("--run", action="append", type=parse_run, required=True, help="VARIANT=outputs.jsonl; repeat for each run")
    parser.add_argument("--reward-config", default=str(PROJECT_ROOT / "configs" / "reward_ablation.json"))
    parser.add_argument("--output-dir", required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summaries: list[dict[str, Any]] = []
    for variant, path in args.run:
        _, summary = evaluate_records(
            load_jsonl(path),
            load_reward_config(variant, args.reward_config),
        )
        summaries.append({"variant": variant, "input": str(path), **summary})

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "ablation_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summaries, file, ensure_ascii=False, indent=2)
    fieldnames = list(summaries[0])
    with (output_dir / "ablation_summary.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)

    columns = ("variant", "accuracy", "avg_search_turns", "tool_call_rationality", "mean_reward")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in summaries:
        print(" | ".join(str(row[column]) for column in columns))


if __name__ == "__main__":
    main()
