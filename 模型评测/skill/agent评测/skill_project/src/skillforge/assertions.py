"""断言执行引擎。

程序类断言（6 种）针对"文本上下文"（静态 skill 内容或沙箱产物）判定；
LLM 类断言（2 种）由上层评测器注入 LLM 判定器执行。
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Callable

from .types import Assertion, AssertionType, LLM_ASSERTIONS


class AssertionError_(Exception):
    """断言本身配置错误（区别于断言未通过）。"""


def evaluate(
    assertion: Assertion,
    text: str,
    *,
    judge: Callable[[Assertion, str], tuple[bool, str]] | None = None,
    artifacts_dir: Path | None = None,
) -> tuple[bool, str]:
    """对文本上下文执行单条断言，返回 (是否通过, 说明)。

    参数
    ----
    text:
        被判定对象的文本视图。静态评测时为 skill corpus；沙箱评测时为执行产物。
    judge:
        LLM 二元判定器（仅 LLM 类断言需要）。缺失时 LLM 断言直接失败。
    artifacts_dir:
        沙箱执行产物目录（供 FILE_EXISTS / SCRIPT_CHECK / JSON_SCHEMA 使用）。
    """
    at = assertion.type

    if at is AssertionType.CONTAINS:
        # 关键词匹配不区分大小写，与 regex 的 re.IGNORECASE 对齐
        ok = assertion.value.lower() in text.lower()
        return ok, f"contains {assertion.value!r} -> {ok}"

    if at is AssertionType.NOT_CONTAINS:
        ok = assertion.value.lower() not in text.lower()
        return ok, f"not_contains {assertion.value!r} -> {ok}"

    if at is AssertionType.REGEX:
        try:
            ok = re.search(assertion.value, text, re.IGNORECASE) is not None
        except re.error as e:
            raise AssertionError_(f"非法正则 {assertion.value!r}: {e}") from e
        return ok, f"regex {assertion.value!r} -> {ok}"

    if at is AssertionType.FILE_EXISTS:
        ok = bool(artifacts_dir) and (artifacts_dir / assertion.value).exists()
        return ok, f"file_exists {assertion.value!r} -> {ok}"

    if at is AssertionType.JSON_SCHEMA:
        return _check_json_schema(assertion, artifacts_dir)

    if at is AssertionType.SCRIPT_CHECK:
        return _run_script_check(assertion, artifacts_dir)

    if at in LLM_ASSERTIONS:
        if judge is None:
            return False, f"{at.value} 需要 LLM 判定器，但未提供"
        return judge(assertion, text)

    raise AssertionError_(f"未知断言类型: {at!r}")


def _check_json_schema(
    assertion: Assertion, artifacts_dir: Path | None
) -> tuple[bool, str]:
    if not artifacts_dir:
        return False, "JSON_SCHEMA 需要 artifacts_dir"
    target = artifacts_dir / assertion.value
    if not target.exists():
        return False, f"JSON 产物不存在: {assertion.value}"

    schema = assertion.params.get("schema")
    if schema is None:
        # 无 schema 时仅校验是否为合法 JSON
        try:
            json.loads(target.read_text(encoding="utf-8"))
            return True, "合法 JSON"
        except json.JSONDecodeError as e:
            return False, f"非法 JSON: {e}"

    # 依赖 jsonschema（可选）。未安装时降级为浅校验。
    try:
        import jsonschema  # type: ignore
    except ImportError:
        try:
            json.loads(target.read_text(encoding="utf-8"))
            return True, "无 jsonschema 依赖，仅浅校验为合法 JSON"
        except json.JSONDecodeError as e:
            return False, f"非法 JSON: {e}"

    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        jsonschema.validate(data, schema)
        return True, "满足 schema"
    except (json.JSONDecodeError, jsonschema.ValidationError) as e:  # type: ignore
        return False, f"schema 校验失败: {e}"


def _run_script_check(
    assertion: Assertion, artifacts_dir: Path | None
) -> tuple[bool, str]:
    script = assertion.params.get("script")
    if not script:
        # 允许把 value 当作可执行 shell 命令
        script = assertion.value
    if not artifacts_dir:
        return False, "SCRIPT_CHECK 需要 artifacts_dir"

    try:
        proc = subprocess.run(
            script,
            shell=True,
            cwd=artifacts_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok = proc.returncode == 0
        detail = (proc.stdout or proc.stderr).strip()[:200]
        return ok, f"script exit={proc.returncode} {detail}"
    except subprocess.TimeoutExpired:
        return False, "script 超时"
    except Exception as e:  # noqa: BLE001
        return False, f"script 执行异常: {e}"
