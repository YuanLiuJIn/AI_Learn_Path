"""Search-R1 多目标奖励与 veRL 自定义奖励入口。

支持三组可复现实验：
- outcome：只使用最终答案奖励；
- outcome_efficiency：增加搜索成本、非法调用和重复查询惩罚；
- outcome_efficiency_prm：进一步接入真实的过程奖励分数。

PRM 分数必须由 ``extra_info.process_scores`` 提供，或由 ``PRM_ENDPOINT``
指向的服务实时返回。代码不会用启发式规则冒充过程奖励模型。
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, fields
from functools import lru_cache
from pathlib import Path
from statistics import fmean
from typing import Any, Mapping, Sequence

ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.IGNORECASE | re.DOTALL)
SEARCH_PATTERN = re.compile(r"<search>(.*?)</search>", re.IGNORECASE | re.DOTALL)
SEARCH_OPEN_PATTERN = re.compile(r"<search>", re.IGNORECASE)
SEARCH_CLOSE_PATTERN = re.compile(r"</search>", re.IGNORECASE)
THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)
SUPPORTED_VARIANTS = (
    "outcome",
    "outcome_efficiency",
    "outcome_efficiency_prm",
)
_VARIANT_DEFAULTS: dict[str, dict[str, Any]] = {
    "outcome": {},
    "outcome_efficiency": {
        "search_cost": 0.05,
        "invalid_search_penalty": 0.1,
        "duplicate_search_penalty": 0.05,
        "over_budget_penalty": 0.1,
    },
    "outcome_efficiency_prm": {
        "search_cost": 0.05,
        "invalid_search_penalty": 0.1,
        "duplicate_search_penalty": 0.05,
        "over_budget_penalty": 0.1,
        "prm_weight": 0.2,
    },
}


@dataclass(frozen=True)
class RewardConfig:
    """多目标奖励的权重与约束。"""

    outcome_weight: float = 1.0
    free_search_calls: int = 1
    search_cost: float = 0.0
    invalid_search_penalty: float = 0.0
    duplicate_search_penalty: float = 0.0
    max_search_calls: int = 4
    over_budget_penalty: float = 0.0
    prm_weight: float = 0.0
    prm_aggregation: str = "mean"
    prm_endpoint: str | None = None
    prm_timeout_seconds: float = 10.0
    prm_fail_open: bool = False

    def validate(self) -> None:
        nonnegative = (
            "outcome_weight",
            "free_search_calls",
            "search_cost",
            "invalid_search_penalty",
            "duplicate_search_penalty",
            "max_search_calls",
            "over_budget_penalty",
            "prm_weight",
            "prm_timeout_seconds",
        )
        for name in nonnegative:
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.prm_aggregation not in {"mean", "min", "last"}:
            raise ValueError("prm_aggregation must be one of: mean, min, last")


@dataclass(frozen=True)
class SearchStats:
    queries: tuple[str, ...]
    search_count: int
    attempt_count: int
    invalid_count: int
    duplicate_count: int


@dataclass(frozen=True)
class RewardBreakdown:
    total: float
    outcome_reward: float
    efficiency_reward: float
    process_reward: float
    accuracy: float
    answer_format_valid: float
    search_count: int
    invalid_search_count: int
    duplicate_search_count: int
    raw_prm_score: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize(text: Any) -> str:
    """使用 Unicode 兼容归一化，移除标点并折叠空白。"""

    normalized = unicodedata.normalize("NFKC", str(text)).casefold()
    normalized = "".join(
        " " if unicodedata.category(char).startswith(("P", "S")) else char
        for char in normalized
    )
    normalized = re.sub(r"\b(a|an|the)\b", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def extract_answer(text: str) -> str | None:
    """抽取最后一个答案块，避免中间草稿答案覆盖最终答案。"""

    matches = ANSWER_PATTERN.findall(text or "")
    return matches[-1].strip() if matches else None


def extract_targets(ground_truth: Any) -> list[str]:
    """兼容字符串、答案列表和 Search-R1 的 ``{"target": ...}`` 格式。"""

    value = ground_truth
    if isinstance(value, Mapping):
        for key in ("target", "answers", "answer", "ground_truth"):
            if key in value:
                value = value[key]
                break
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return [str(value)] if value is not None else []


def exact_match(prediction: str | None, ground_truth: Any) -> bool:
    if prediction is None:
        return False
    normalized_prediction = normalize(prediction)
    return any(
        normalized_prediction == normalize(target)
        for target in extract_targets(ground_truth)
    )


def analyze_search_calls(text: str) -> SearchStats:
    """统计合法、空、未闭合和重复的搜索调用。"""

    raw_queries = SEARCH_PATTERN.findall(text or "")
    queries = tuple(query.strip() for query in raw_queries if query.strip())
    empty_calls = len(raw_queries) - len(queries)
    unbalanced_tags = abs(
        len(SEARCH_OPEN_PATTERN.findall(text or ""))
        - len(SEARCH_CLOSE_PATTERN.findall(text or ""))
    )
    normalized_queries = [normalize(query) for query in queries]
    duplicate_count = len(normalized_queries) - len(set(normalized_queries))
    attempt_count = max(
        len(SEARCH_OPEN_PATTERN.findall(text or "")),
        len(SEARCH_CLOSE_PATTERN.findall(text or "")),
        len(raw_queries),
    )
    return SearchStats(
        queries=queries,
        search_count=len(queries),
        attempt_count=attempt_count,
        invalid_count=empty_calls + unbalanced_tags,
        duplicate_count=duplicate_count,
    )


def extract_process_steps(text: str) -> list[str]:
    """从轨迹中提取可交给 PRM 的推理步骤。"""

    think_steps = [step.strip() for step in THINK_PATTERN.findall(text or "") if step.strip()]
    if think_steps:
        return think_steps
    prefix = ANSWER_PATTERN.split(text or "", maxsplit=1)[0]
    prefix = SEARCH_PATTERN.sub(" ", prefix)
    return [line.strip() for line in prefix.splitlines() if line.strip()]


def _coerce_scores(value: Any) -> list[float]:
    if value is None:
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [float(score) for score in value]
    raise TypeError("PRM scores must be a number or a sequence of numbers")


def _request_prm_scores(
    endpoint: str,
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any],
    timeout_seconds: float,
) -> list[float]:
    payload = {
        "data_source": data_source,
        "trajectory": solution_str,
        "steps": extract_process_steps(solution_str),
        "ground_truth": ground_truth,
        "extra_info": dict(extra_info),
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PRM request failed: {exc}") from exc

    if isinstance(result, Mapping):
        result = result.get("scores", result.get("score"))
    scores = _coerce_scores(result)
    if not scores:
        raise RuntimeError("PRM response must contain a non-empty 'scores' or 'score'")
    return scores


def _aggregate_prm_scores(scores: Sequence[float], method: str) -> float:
    if not scores:
        raise ValueError("Cannot aggregate empty PRM scores")
    if method == "mean":
        value = fmean(scores)
    elif method == "min":
        value = min(scores)
    else:
        value = scores[-1]
    return max(0.0, min(1.0, float(value)))


def _resolve_prm_score(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any],
    config: RewardConfig,
) -> float | None:
    scores = _coerce_scores(
        extra_info.get("process_scores", extra_info.get("prm_scores"))
    )
    endpoint = config.prm_endpoint or os.getenv("PRM_ENDPOINT")
    if not scores and endpoint:
        scores = _request_prm_scores(
            endpoint,
            data_source,
            solution_str,
            ground_truth,
            extra_info,
            config.prm_timeout_seconds,
        )
    if not scores:
        if config.prm_fail_open:
            return None
        raise RuntimeError(
            "PRM reward is enabled, but no process scores are available. "
            "Provide extra_info.process_scores or set PRM_ENDPOINT."
        )
    return _aggregate_prm_scores(scores, config.prm_aggregation)


@lru_cache(maxsize=16)
def _load_reward_config_cached(
    variant: str,
    config_path: str | None,
    prm_endpoint: str | None,
    prm_fail_open: str | None,
) -> RewardConfig:
    if variant not in SUPPORTED_VARIANTS:
        raise ValueError(f"Unknown reward variant: {variant}")

    values = dict(_VARIANT_DEFAULTS[variant])
    if config_path:
        with Path(config_path).open("r", encoding="utf-8") as file:
            raw_config = json.load(file)
        if not isinstance(raw_config, Mapping):
            raise TypeError("Reward config root must be a JSON object")
        if variant in raw_config:
            overrides = raw_config[variant]
        elif any(name in raw_config for name in SUPPORTED_VARIANTS):
            raise KeyError(f"Reward config does not contain variant: {variant}")
        else:
            overrides = raw_config
        if not isinstance(overrides, Mapping):
            raise TypeError(f"Reward config for {variant} must be a JSON object")
        values.update(overrides)

    allowed = {field.name for field in fields(RewardConfig)}
    unknown = set(values) - allowed
    if unknown:
        raise ValueError(f"Unknown reward config fields: {sorted(unknown)}")
    if prm_endpoint:
        values["prm_endpoint"] = prm_endpoint
    if prm_fail_open is not None:
        values["prm_fail_open"] = prm_fail_open.lower() in {"1", "true", "yes"}

    config = RewardConfig(**values)
    config.validate()
    return config


def load_reward_config(
    variant: str,
    config_path: str | Path | None = None,
) -> RewardConfig:
    """读取消融配置；缓存结果，避免训练时逐轨迹重复访问磁盘。"""

    path_value = config_path or os.getenv("REWARD_CONFIG_PATH")
    return _load_reward_config_cached(
        variant,
        str(path_value) if path_value else None,
        os.getenv("PRM_ENDPOINT"),
        os.getenv("PRM_FAIL_OPEN"),
    )


def score_trajectory(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
    config: RewardConfig | None = None,
) -> RewardBreakdown:
    """计算一条 Agent 搜索轨迹的完整奖励拆分。"""

    config = config or RewardConfig()
    config.validate()
    info = extra_info or {}
    prediction = extract_answer(solution_str)
    accuracy = float(exact_match(prediction, ground_truth))
    search_stats = analyze_search_calls(solution_str)

    outcome_reward = config.outcome_weight * accuracy
    excess_calls = max(0, search_stats.search_count - config.free_search_calls)
    over_budget = max(0, search_stats.search_count - config.max_search_calls)
    efficiency_reward = -(
        config.search_cost * excess_calls
        + config.invalid_search_penalty * search_stats.invalid_count
        + config.duplicate_search_penalty * search_stats.duplicate_count
        + config.over_budget_penalty * over_budget
    )

    raw_prm_score: float | None = None
    process_reward = 0.0
    if config.prm_weight > 0:
        raw_prm_score = _resolve_prm_score(
            data_source,
            solution_str,
            ground_truth,
            info,
            config,
        )
        if raw_prm_score is not None:
            process_reward = config.prm_weight * raw_prm_score

    return RewardBreakdown(
        total=outcome_reward + efficiency_reward + process_reward,
        outcome_reward=outcome_reward,
        efficiency_reward=efficiency_reward,
        process_reward=process_reward,
        accuracy=accuracy,
        answer_format_valid=float(prediction is not None),
        search_count=search_stats.search_count,
        invalid_search_count=search_stats.invalid_count,
        duplicate_search_count=search_stats.duplicate_count,
        raw_prm_score=raw_prm_score,
    )


def _score_variant(
    variant: str,
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
) -> float:
    config = load_reward_config(variant)
    return score_trajectory(
        data_source,
        solution_str,
        ground_truth,
        extra_info,
        config,
    ).total


def reward_outcome(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
) -> float:
    return _score_variant("outcome", data_source, solution_str, ground_truth, extra_info)


def reward_outcome_efficiency(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
) -> float:
    return _score_variant(
        "outcome_efficiency", data_source, solution_str, ground_truth, extra_info
    )


def reward_outcome_efficiency_prm(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
) -> float:
    return _score_variant(
        "outcome_efficiency_prm",
        data_source,
        solution_str,
        ground_truth,
        extra_info,
    )


def compute_score(
    data_source: str,
    solution_str: str,
    ground_truth: Any,
    extra_info: Mapping[str, Any] | None = None,
) -> float:
    """veRL 默认入口；通过 ``REWARD_VARIANT`` 选择消融组。"""

    variant = os.getenv("REWARD_VARIANT", "outcome")
    return _score_variant(variant, data_source, solution_str, ground_truth, extra_info)


def reward_for_search(
    sample: Mapping[str, Any],
    model_output: str,
    config: RewardConfig | None = None,
) -> float:
    """兼容原脚手架的样本级调用方式。"""

    reward_metadata = sample.get("reward_model", {})
    ground_truth = (
        reward_metadata.get("ground_truth")
        if isinstance(reward_metadata, Mapping)
        else reward_metadata
    )
    return score_trajectory(
        str(sample.get("data_source", "search_qa")),
        model_output,
        ground_truth,
        sample.get("extra_info", {}),
        config,
    ).total


if __name__ == "__main__":
    demo_sample = {"reward_model": {"ground_truth": {"target": "Barack Obama"}}}
    demo_output = (
        "<think>I should verify the fact.</think>"
        "<search>US president in 2009</search>"
        "<answer>Barack Obama</answer>"
    )
    print(reward_for_search(demo_sample, demo_output, RewardConfig()))
