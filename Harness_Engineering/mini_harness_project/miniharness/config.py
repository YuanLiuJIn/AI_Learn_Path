"""配置：选择使用哪种 LLM，以及读取相关环境变量。

通过环境变量 MINIHARNESS_LLM 选择：
- "scripted"（默认）：脚本化假模型，无需 API Key，用于看清 harness 闭环
- "openai"：任意 OpenAI 兼容接口（需要 OPENAI_API_KEY 等）
"""

import os


def get_llm_kind() -> str:
    return os.environ.get("MINIHARNESS_LLM", "scripted").lower()


def get_openai_config() -> dict:
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    }


# Agent 单次任务最多走多少步，防止死循环（这是 harness 的一种约束/治理）
MAX_STEPS = int(os.environ.get("MINIHARNESS_MAX_STEPS", "12"))
