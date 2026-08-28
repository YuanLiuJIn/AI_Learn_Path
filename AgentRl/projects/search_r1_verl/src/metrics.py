"""Agentic-Search 离线评测指标与 JSONL 流水线。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence

from .reward import (
    RewardConfig,
    analyze_search_calls,
    load_reward_config,
    score_trajectory,
)


def _lookup(record: Mapping[str, Any], key: str, default: Any = None) -> Any:
    if key in record:
        return record[key]
    extra_info = record.get("extra_info", {})
    if isinstance(extra_info, Mapping):
        return extra_info.get(key, default)
    return default


def _ground_truth(record: Mapping[str, Any]) -> Any:
    if "ground_truth" in record:
        return record["ground_truth"]
    reward_model = record.get("reward_model", {})
    if isinstance(reward_model, Mapping):
        return reward_model.get("ground_truth")
    return None


def _solution(record: Mapping[str, Any]) -> str:
    for key in ("output", "solution_str", "response", "model_output"):
        if key in record:
            return str(record[key])
    raise KeyError("Each record must contain output, solution_str, response, or model_output")


def tool_call_rationality(
    solution_str: str,
    requires_search: bool | None = None,
    max_search_calls: int = 4,
    search_relevance: Sequence[float | bool] | None = None,
) -> tuple[float | None, dict[str, float]]:
    """计算可审计的工具调用合理率。

    该指标只聚合可观察项：格式有效性、查询去重、预算遵循、搜索必要性标签，
    以及可选的人工/模型相关性标签。没有搜索也没有必要性标签时返回 ``None``，
    避免把“不调用工具”错误记为满分。
    """

    stats = analyze_search_calls(solution_str)
    components: dict[str, float] = {}

    if stats.attempt_count > 0:
        components["syntax_validity"] = stats.search_count / max(
            1, stats.search_count + stats.invalid_count
        )
    if stats.search_count > 0:
        components["non_redundancy"] = (
            stats.search_count - stats.duplicate_count
        ) / stats.search_count
        components["budget_compliance"] = min(
            1.0, max_search_calls / stats.search_count
        )
    if requires_search is not None:
        components["necessity_alignment"] = float(
            (requires_search and stats.search_count > 0)
            or (not requires_search and stats.search_count == 0)
        )
    if search_relevance is not None and stats.search_count > 0:
        relevance = [float(value) for value in search_relevance[: stats.search_count]]
        if relevance:
            components["query_relevance"] = fmean(relevance)

    if not components:
        return None, {}
    return fmean(components.values()), components


def evaluate_record(
    record: Mapping[str, Any],
    config: RewardConfig,
    max_search_calls: int | None = None,
) -> dict[str, Any]:
    solution_str = _solution(record)
    ground_truth = _ground_truth(record)
    data_source = str(record.get("data_source", "search_qa"))
    extra_info = dict(record.get("extra_info", {}) or {})
    if "process_scores" in record:
        extra_info["process_scores"] = record["process_scores"]

    breakdown = score_trajectory(
        data_source,
        solution_str,
        ground_truth,
        extra_info,
        config,
    )
    budget = int(max_search_calls or _lookup(record, "max_search_calls", config.max_search_calls))
    rationality, components = tool_call_rationality(
        solution_str,
        requires_search=_lookup(record, "requires_search"),
        max_search_calls=budget,
        search_relevance=_lookup(record, "search_relevance"),
    )
    stats = analyze_search_calls(solution_str)

    result = {
        "id": str(record.get("id", _lookup(record, "index", ""))),
        "accuracy": breakdown.accuracy,
        "answer_format_valid": breakdown.answer_format_valid,
        "search_count": breakdown.search_count,
        "invalid_search_count": breakdown.invalid_search_count,
        "duplicate_search_count": breakdown.duplicate_search_count,
        "over_budget": float(stats.search_count > budget),
        "tool_call_rationality": rationality,
        "reward": breakdown.total,
        "outcome_reward": breakdown.outcome_reward,
        "efficiency_reward": breakdown.efficiency_reward,
        "process_reward": breakdown.process_reward,
        "raw_prm_score": breakdown.raw_prm_score,
    }
    result.update({f"rationality_{key}": value for key, value in components.items()})
    return result


def summarize(details: Sequence[Mapping[str, Any]]) -> dict[str, float | int]:
    if not details:
        raise ValueError("Cannot summarize an empty evaluation set")

    def mean(key: str) -> float:
        return fmean(float(row[key]) for row in details)

    rationality_values = [
        float(row["tool_call_rationality"])
        for row in details
        if row.get("tool_call_rationality") is not None
    ]
    prm_values = [
        float(row["raw_prm_score"])
        for row in details
        if row.get("raw_prm_score") is not None
    ]
    total_searches = sum(int(row["search_count"]) for row in details)
    total_duplicates = sum(int(row["duplicate_search_count"]) for row in details)

    return {
        "samples": len(details),
        "accuracy": mean("accuracy"),
        "answer_format_rate": mean("answer_format_valid"),
        "avg_search_turns": mean("search_count"),
        "tool_call_rationality": fmean(rationality_values) if rationality_values else 0.0,
        "rationality_coverage": len(rationality_values) / len(details),
        "invalid_tool_call_rate": sum(
            int(row["invalid_search_count"]) > 0 for row in details
        )
        / len(details),
        "duplicate_query_rate": total_duplicates / max(1, total_searches),
        "over_budget_rate": mean("over_budget"),
        "mean_reward": mean("reward"),
        "mean_outcome_reward": mean("outcome_reward"),
        "mean_efficiency_reward": mean("efficiency_reward"),
        "mean_process_reward": mean("process_reward"),
        "mean_prm_score": fmean(prm_values) if prm_values else 0.0,
        "prm_coverage": len(prm_values) / len(details),
    }


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return records


def evaluate_records(
    records: Iterable[Mapping[str, Any]],
    config: RewardConfig,
    max_search_calls: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, float | int]]:
    details = [evaluate_record(record, config, max_search_calls) for record in records]
    return details, summarize(details)


def write_results(
    output_dir: str | Path,
    details: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)
    fieldnames = sorted({key for row in details for key in row})
    with (destination / "details.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(details)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Agentic-Search trajectories")
    parser.add_argument("--input", required=True, help="JSONL model outputs")
    parser.add_argument("--output-dir", required=True, help="Directory for summary.json/details.csv")
    parser.add_argument("--variant", choices=("outcome", "outcome_efficiency", "outcome_efficiency_prm"), default="outcome_efficiency")
    parser.add_argument("--reward-config", default=None, help="Reward ablation JSON file")
    parser.add_argument("--max-search-calls", type=int, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_reward_config(args.variant, args.reward_config)
    details, summary = evaluate_records(
        load_jsonl(args.input),
        config,
        args.max_search_calls,
    )
    write_results(args.output_dir, details, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
