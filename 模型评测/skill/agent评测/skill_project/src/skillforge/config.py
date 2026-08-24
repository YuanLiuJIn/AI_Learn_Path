"""配置管理。

用强类型 dataclass 替代散落在 markdown 文件里的裸键值配置，
支持从 JSON/YAML 加载与默认值合并。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Mapping


@dataclass
class GateConfig:
    """多维 AND 门控阈值。"""

    # 质量：dev pass_rate 相对 baseline 的最小提升（delta）
    min_delta: float = 0.02
    # 触发：触发 F1 的容忍区间
    trigger_tolerance: float = 0.05
    # 成本：token 相对 baseline 的最大增幅
    max_token_increase: float = 0.20
    # 延迟：相对 baseline 的最大增幅
    max_latency_increase: float = 0.20
    # 回归：regression 集 pass_rate 的容忍下降
    regression_tolerance: float = 0.05
    # 统计显著性：LLM 评测多次采样次数（>=1 关闭显著性检验）
    significance_samples: int = 3
    # 显著性置信水平
    confidence_level: float = 0.95


@dataclass
class EvalConfig:
    """三层评测配置。"""

    # L1 快速门卫：结构/安全扫描，挂了直接丢弃
    l1_enabled: bool = True
    # L2 dev 评测：是否跑全量
    l2_enabled: bool = True
    # L3 严格评测：每 N 轮触发一次（holdout + regression + 盲 A/B）
    l3_every_n: int = 5
    # 是否启用端到端沙箱评测（能力验证），而非仅静态断言
    sandbox: bool = False
    sandbox_timeout_seconds: int = 30


@dataclass
class SearchConfig:
    """搜索策略配置。"""

    max_iterations: int = 20
    # Beam width：>1 时启用 Beam Search（并行多候选）
    beam_width: int = 1
    # 每轮每个分支生成的候选数
    candidates_per_step: int = 1
    # 连续无提升 N 轮后升层（突变层升级）
    plateau_threshold: int = 3
    # 连续 discard 次数达到该值触发激进策略
    aggressive_after_discards: int = 5


@dataclass
class MemoryConfig:
    """记忆层配置。"""

    enabled: bool = True
    # 存储路径（默认在工作区 .skillforge/memory.jsonl）
    path: Path | None = None
    # 检索时最多注入的 pattern 数（token 预算）
    max_patterns_injected: int = 5


@dataclass
class EvolutionConfig:
    """总配置。"""

    gate: GateConfig = field(default_factory=GateConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    # 目标 skill 路径
    skill_path: Path | None = None
    # GT 文件路径
    gt_path: Path | None = None
    # 工作区目录（git 隔离）
    workspace: Path | None = None

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "EvolutionConfig":
        cfg = cls()
        for section in ("gate", "eval", "search", "memory"):
            if section in raw:
                sub = getattr(cfg, section)
                for k, v in raw[section].items():
                    if hasattr(sub, k):
                        setattr(sub, k, v)
        for k in ("skill_path", "gt_path", "workspace"):
            if k in raw and raw[k]:
                setattr(cfg, k, Path(raw[k]))
        return cfg

    @classmethod
    def from_json(cls, path: str | Path) -> "EvolutionConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        def _dump(cfg: object) -> dict[str, Any]:
            return {
                f.name: getattr(cfg, f.name)
                for f in fields(cfg)  # type: ignore[arg-type]
            }

        return {
            "gate": _dump(self.gate),
            "eval": _dump(self.eval),
            "search": _dump(self.search),
            "memory": _dump(self.memory),
            "skill_path": str(self.skill_path) if self.skill_path else None,
            "gt_path": str(self.gt_path) if self.gt_path else None,
            "workspace": str(self.workspace) if self.workspace else None,
        }

    def replace(self, **changes: Any) -> "EvolutionConfig":
        return replace(self, **changes)
