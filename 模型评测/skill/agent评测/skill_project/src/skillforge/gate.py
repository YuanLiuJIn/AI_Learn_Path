"""门控层：多维 AND 判定 + 统计显著性检验。

朴素实现用硬阈值判定质量，会被 LLM 评测噪声误导
（同状态多次运行 pass_rate 会明显漂移）。本项目引入两个改进：

1. **多维 AND**：质量/触发/成本/延迟/回归任一不达标即丢弃（用 AND 而非加权和，
   防止"质量+10% 但 token 翻倍"蒙混过关）。
2. **统计显著性**：对 pass_rate 多次采样，用 bootstrap 置信区间判断提升是否显著，
   区分"真改进"与"运气波动"。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Mapping, Sequence

from .config import GateConfig
from .types import (
    EvalResult,
    GateAction,
    GateDecision,
    Split,
)


@dataclass
class GateContext:
    """门控输入：baseline 与 candidate 的各切分评测结果，及可选采样。"""

    baseline: Mapping[Split, EvalResult]
    candidate: Mapping[Split, EvalResult]
    # 多次采样得到的 dev pass_rate 序列（用于显著性检验）
    baseline_samples: Sequence[float] = ()
    candidate_samples: Sequence[float] = ()


def bootstrap_mean_diff_significant(
    a: Sequence[float],
    b: Sequence[float],
    confidence: float = 0.95,
    n_boot: int = 2000,
    seed: int = 42,
) -> tuple[bool, float]:
    """用 bootstrap 判断 b 的均值是否显著大于 a。

    返回 (是否显著提升, 置信区间下界)。无分布假设，纯标准库。
    """
    if len(a) < 2 or len(b) < 2:
        # 样本太少，退化为均值比较
        return sum(b) / len(b) > sum(a) / len(a), 0.0

    rng = random.Random(seed)
    diffs: list[float] = []
    la, lb = len(a), len(b)
    for _ in range(n_boot):
        sa = [a[rng.randrange(la)] for _ in range(la)]
        sb = [b[rng.randrange(lb)] for _ in range(lb)]
        diffs.append(sum(sb) / lb - sum(sa) / la)
    diffs.sort()
    alpha = (1.0 - confidence) / 2.0
    lower = diffs[int(alpha * n_boot)]
    return lower > 0.0, lower


class Gate:
    """多维 AND 门控。"""

    def __init__(self, config: GateConfig):
        self._cfg = config

    def decide(self, ctx: GateContext) -> GateDecision:
        reasons: list[str] = []
        dims: dict[str, bool] = {}

        dev_base = ctx.baseline.get(Split.DEV)
        dev_cand = ctx.candidate.get(Split.DEV)
        if dev_base is None or dev_cand is None:
            return GateDecision(
                GateAction.DISCARD,
                ("缺少 dev 评测结果，无法门控",),
                {},
            )

        # ---- 1. 质量 ----
        base_rate = dev_base.pass_rate
        cand_rate = dev_cand.pass_rate
        delta = cand_rate - base_rate
        quality_ok = delta >= self._cfg.min_delta
        reason = (
            f"quality: dev {base_rate:.3f} -> {cand_rate:.3f} "
            f"(delta {delta:+.3f}, min_delta {self._cfg.min_delta})"
        )
        if (
            quality_ok
            and self._cfg.significance_samples > 1
            and ctx.baseline_samples
            and ctx.candidate_samples
        ):
            sig_ok, lower = bootstrap_mean_diff_significant(
                ctx.baseline_samples,
                ctx.candidate_samples,
                self._cfg.confidence_level,
            )
            quality_ok = sig_ok
            reason += f"; significance: {sig_ok} (CI lower {lower:+.3f})"
        dims["quality"] = quality_ok
        reasons.append(reason)

        # ---- 2. 成本（token） ----
        base_tokens = max(1, dev_base.tokens)
        cand_tokens = dev_cand.tokens
        ratio = cand_tokens / base_tokens
        cost_ok = ratio <= 1.0 + self._cfg.max_token_increase
        dims["cost"] = cost_ok
        reasons.append(
            f"cost: tokens {base_tokens} -> {cand_tokens} "
            f"(x{ratio:.2f}, max {1 + self._cfg.max_token_increase:.2f})"
        )

        # ---- 3. 延迟 ----
        base_ms = max(1, dev_base.duration_ms)
        cand_ms = dev_cand.duration_ms
        lat_ratio = cand_ms / base_ms
        latency_ok = lat_ratio <= 1.0 + self._cfg.max_latency_increase
        dims["latency"] = latency_ok
        reasons.append(
            f"latency: {base_ms}ms -> {cand_ms}ms "
            f"(x{lat_ratio:.2f}, max {1 + self._cfg.max_latency_increase:.2f})"
        )

        # ---- 4. 回归 ----
        reg_base = ctx.baseline.get(Split.REGRESSION)
        reg_cand = ctx.candidate.get(Split.REGRESSION)
        if reg_base is not None and reg_cand is not None:
            reg_drop = reg_base.pass_rate - reg_cand.pass_rate
            regression_ok = reg_drop <= self._cfg.regression_tolerance
            dims["regression"] = regression_ok
            reasons.append(
                f"regression: {reg_base.pass_rate:.3f} -> {reg_cand.pass_rate:.3f} "
                f"(drop {reg_drop:+.3f}, tol {self._cfg.regression_tolerance})"
            )

        # ---- 5. 触发（若提供了 F1，见 metadata；此处占位，默认通过） ----
        dims["trigger"] = True
        reasons.append("trigger: 未采集 F1，默认通过")

        all_ok = all(dims.values())
        action = GateAction.KEEP if all_ok else GateAction.DISCARD
        return GateDecision(action, tuple(reasons), dims)
