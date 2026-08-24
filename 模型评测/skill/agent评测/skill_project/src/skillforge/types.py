"""核心数据类型定义。

所有跨模块共享的数据结构集中在此，避免各模块自行拼 dict
导致的隐式契约与字段漂移。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

# --------------------------------------------------------------------------- #
# 数据切分
# --------------------------------------------------------------------------- #


class Split(str, Enum):
    """GT 用例的切分，用于防过拟合与防退化。"""

    DEV = "dev"              # 优化目标，喂给搜索器
    HOLDOUT = "holdout"      # 盲测，绝不喂给搜索器（防背答案）
    REGRESSION = "regression"  # 回归守卫（防能力退化）


# --------------------------------------------------------------------------- #
# 断言
# --------------------------------------------------------------------------- #


class AssertionType(str, Enum):
    """8 种断言：6 种程序直接判定 + 2 种需 LLM 语义判定。"""

    CONTAINS = "contains"          # 文本/产物包含子串
    NOT_CONTAINS = "not_contains"  # 文本/产物不包含子串
    REGEX = "regex"                # 正则匹配
    FILE_EXISTS = "file_exists"    # 产物文件存在
    JSON_SCHEMA = "json_schema"    # 产物 JSON 满足 schema
    SCRIPT_CHECK = "script_check"  # 自定义脚本判定（返回 exit code 0 为通过）
    PATH_HIT = "path_hit"          # [LLM] 命中了正确的知识/工具路径
    FACT_COVERAGE = "fact_coverage"  # [LLM] 覆盖了关键事实


# 需要 LLM 语义判定的断言类型
LLM_ASSERTIONS: frozenset[AssertionType] = frozenset(
    {AssertionType.PATH_HIT, AssertionType.FACT_COVERAGE}
)


@dataclass(frozen=True)
class Assertion:
    """单条断言。value 的含义随 type 不同而变化。"""

    type: AssertionType
    value: str
    description: str = ""
    # 额外参数：如 JSON_SCHEMA 的 schema、SCRIPT_CHECK 的脚本路径等
    params: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": self.type.value, "value": self.value}
        if self.description:
            d["description"] = self.description
        if self.params:
            d.update(self.params)
        return d

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "Assertion":
        known = {"type", "value", "description"}
        params = {k: v for k, v in raw.items() if k not in known}
        return cls(
            type=AssertionType(raw["type"]),
            value=str(raw["value"]),
            description=str(raw.get("description", "")),
            params=params,
        )


# --------------------------------------------------------------------------- #
# GT
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TestCase:
    """一条 ground-truth 用例。"""

    id: str
    prompt: str
    assertions: tuple[Assertion, ...]
    split: Split = Split.DEV
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_program_only(self) -> bool:
        return all(a.type not in LLM_ASSERTIONS for a in self.assertions)


@dataclass(frozen=True)
class GroundTruth:
    """完整的 GT 集。"""

    cases: tuple[TestCase, ...]

    def by_split(self, split: Split) -> tuple[TestCase, ...]:
        return tuple(c for c in self.cases if c.split is split)

    @property
    def dev(self) -> tuple[TestCase, ...]:
        return self.by_split(Split.DEV)

    @property
    def holdout(self) -> tuple[TestCase, ...]:
        return self.by_split(Split.HOLDOUT)

    @property
    def regression(self) -> tuple[TestCase, ...]:
        return self.by_split(Split.REGRESSION)

    def __len__(self) -> int:
        return len(self.cases)


# --------------------------------------------------------------------------- #
# 评测结果
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CaseResult:
    """单条用例的评测结果。"""

    case_id: str
    passed: bool
    failed_assertions: tuple[str, ...] = ()
    # 可选的执行轨迹（用于诊断）：tool 调用 / 输出 / 中间状态
    trace: Mapping[str, Any] = field(default_factory=dict)
    tokens: int = 0
    duration_ms: int = 0


@dataclass(frozen=True)
class EvalResult:
    """一次评测的汇总结果。"""

    split: Split
    cases: tuple[CaseResult, ...]
    # 附加指标（token、延迟等），用于门控的成本/延迟维度
    tokens: int = 0
    duration_ms: int = 0

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.cases if c.passed)

    @property
    def pass_rate(self) -> float:
        if not self.cases:
            return 1.0
        return self.passed / self.total

    @property
    def failed_cases(self) -> tuple[CaseResult, ...]:
        return tuple(c for c in self.cases if not c.passed)


# --------------------------------------------------------------------------- #
# 搜索 / 突变
# --------------------------------------------------------------------------- #


class MutationLayer(str, Enum):
    """分层突变：从最便宜到最贵。"""

    TRIGGER = "trigger"   # 描述/触发词
    BODY = "body"         # 正文指令
    SCRIPT = "script"     # 辅助脚本 / references


@dataclass(frozen=True)
class Candidate:
    """一次候选改动。"""

    id: str
    description: str
    layer: MutationLayer
    # 改动前后内容的 patch（unified diff 文本，供 git/审计）
    diff: str
    # 改动后的 skill 内容快照（用于评测器读取）
    content: str
    eval_results: Mapping[Split, EvalResult] = field(default_factory=dict)

    @property
    def dev_pass_rate(self) -> float:
        r = self.eval_results.get(Split.DEV)
        return r.pass_rate if r else 0.0


# --------------------------------------------------------------------------- #
# 门控
# --------------------------------------------------------------------------- #


class GateAction(str, Enum):
    KEEP = "keep"
    DISCARD = "discard"
    REVERT = "revert"


class GateDimension(str, Enum):
    QUALITY = "quality"      # 质量（dev pass_rate 提升）
    TRIGGER = "trigger"      # 触发 F1 容忍
    COST = "cost"            # token 成本上限
    LATENCY = "latency"      # 延迟上限
    REGRESSION = "regression"  # 回归容忍


@dataclass(frozen=True)
class GateDecision:
    """门控决策结果。"""

    action: GateAction
    # 每个维度的判定说明（含数值），便于审计
    reasons: tuple[str, ...] = ()
    dimensions: Mapping[str, bool] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.action is GateAction.KEEP


# --------------------------------------------------------------------------- #
# 记忆
# --------------------------------------------------------------------------- #


class MemoryLevel(str, Enum):
    """三层记忆：从原始到可复用。"""

    TRACE = "trace"        # 原始执行轨迹
    LESSON = "lesson"      # 失败教训（结构化：什么改动→什么后果）
    PATTERN = "pattern"    # 可复用成功模式（跨 skill 迁移）


@dataclass(frozen=True)
class MemoryEntry:
    """一条记忆记录。"""

    level: MemoryLevel
    skill_name: str
    content: Mapping[str, Any]
    iteration: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "skill_name": self.skill_name,
            "iteration": self.iteration,
            "content": self.content,
        }
