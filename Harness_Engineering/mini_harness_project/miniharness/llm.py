"""LLM 抽象层。

Agent = Model + Harness。这里是"Model"接口，刻意做得很薄。
提供两种实现：
- ScriptedLLM：脚本化假模型，无需 API Key，让你看清 harness 闭环。
- OpenAICompatLLM：调用任意 OpenAI 兼容接口（标准库 urllib，无需第三方包）。

两者都实现同一个方法：act(messages) -> {"thought","tool","args"}
"""

import json
import re
import urllib.request


class BaseLLM:
    def act(self, messages: list[dict]) -> dict:
        raise NotImplementedError


def _extract_json(text: str) -> dict:
    """从模型输出里尽量提取一个 JSON 动作对象。"""
    text = text.strip()
    # 去掉 ```json ... ``` 包裹
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            text = brace.group(0)
    return json.loads(text)


class ScriptedLLM(BaseLLM):
    """按固定剧本走的假模型，针对示例修复任务。

    真实场景中，这些决策由大模型生成；这里写死是为了在没有模型时
    也能端到端演示 harness 的完整闭环。
    """

    def __init__(self):
        self.calls = 0

    @staticmethod
    def _last_observation(messages: list[dict]) -> str:
        for m in reversed(messages):
            if m["role"] == "user" and m["content"].startswith("OBSERVATION:"):
                return m["content"][len("OBSERVATION:"):].strip()
        return ""

    def act(self, messages: list[dict]) -> dict:
        self.calls += 1
        step = self.calls

        if step == 1:
            return {"thought": "先看看有哪些文件", "tool": "list_files", "args": {}}
        if step == 2:
            return {"thought": "读源代码理解问题", "tool": "read_file",
                    "args": {"path": "solution.py"}}
        if step == 3:
            return {"thought": "先跑测试看失败情况", "tool": "run_tests", "args": {}}
        if step == 4:
            # 基于读到的源码做一次针对性修复（演示：把 append(i) 改为 append(str(i))）
            src = ""
            for m in messages:
                if m["role"] == "user" and "def fizzbuzz" in m["content"]:
                    src = m["content"].split("OBSERVATION:")[-1].strip()
            fixed = src.replace("result.append(i)", "result.append(str(i))")
            if not fixed or "def fizzbuzz" not in fixed:
                # 兜底：写入已知正确版本
                fixed = _KNOWN_GOOD_FIZZBUZZ
            return {"thought": "把整数转成字符串再追加", "tool": "write_file",
                    "args": {"path": "solution.py", "content": fixed}}
        if step == 5:
            return {"thought": "验证修复", "tool": "run_tests", "args": {}}
        return {"thought": "完成", "tool": "finish", "args": {}}


_KNOWN_GOOD_FIZZBUZZ = '''def fizzbuzz(n):
    result = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
'''


class OpenAICompatLLM(BaseLLM):
    """调用 OpenAI 兼容的 /chat/completions 接口（仅用标准库）。"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def act(self, messages: list[dict]) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        try:
            return _extract_json(content)
        except Exception:
            # 模型没按格式输出时，安全兜底为结束，避免死循环
            return {"thought": f"无法解析输出: {content[:120]}", "tool": "finish", "args": {}}


def build_llm():
    from . import config
    kind = config.get_llm_kind()
    if kind == "openai":
        cfg = config.get_openai_config()
        if not cfg["api_key"]:
            raise RuntimeError("MINIHARNESS_LLM=openai 但未设置 OPENAI_API_KEY")
        return OpenAICompatLLM(cfg["api_key"], cfg["base_url"], cfg["model"])
    return ScriptedLLM()
