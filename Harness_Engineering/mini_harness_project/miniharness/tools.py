"""工具接口与协议（Tool Interface）层。

这里定义"为 Agent 设计"的工具——注意 Anthropic 的经验：
工具应为 Agent 设计，而不是直接把给人用的 API 丢给它。
所以每个工具都有：清晰的名字、参数、给模型看的描述、结构化返回。
"""

from .sandbox import Sandbox
from .sensors import run_tests


# 给模型看的工具说明（会拼进 system prompt）。保持简洁、明确。
TOOL_SPECS = [
    {"name": "list_files", "args": [], "desc": "列出项目中所有文件路径。"},
    {"name": "read_file", "args": ["path"], "desc": "读取指定文件的完整内容。"},
    {"name": "write_file", "args": ["path", "content"],
     "desc": "用 content 覆盖写入 path（写完整文件内容）。禁止写 test_*.py。"},
    {"name": "run_tests", "args": [], "desc": "运行测试，返回是否通过及输出摘要。"},
    {"name": "finish", "args": [], "desc": "认为修复完成时调用，结束本次任务。"},
]


def tool_specs_text() -> str:
    lines = []
    for t in TOOL_SPECS:
        args = ", ".join(t["args"]) if t["args"] else "无"
        lines.append(f'- {t["name"]}(args: {args}): {t["desc"]}')
    return "\n".join(lines)


class ToolBox:
    """把工具调用分发到沙箱/传感器，并施加治理约束。"""

    def __init__(self, sandbox: Sandbox, test_module: str):
        self.sandbox = sandbox
        self.test_module = test_module

    def call(self, tool: str, args: dict) -> str:
        args = args or {}
        if tool == "list_files":
            return "\n".join(self.sandbox.list_files())

        if tool == "read_file":
            return self.sandbox.read_file(args["path"])

        if tool == "write_file":
            path = args["path"]
            # 治理边界：禁止修改测试文件（对应 AGENTS.md 的硬性约束）
            name = path.replace("\\", "/").split("/")[-1]
            if name.startswith("test_"):
                return "REJECTED: 禁止修改测试文件。请修改源代码。"
            self.sandbox.write_file(path, args["content"])
            return f"OK: 已写入 {path}"

        if tool == "run_tests":
            result = run_tests(self.sandbox.work_dir, self.test_module)
            return result["summary"]

        if tool == "finish":
            return "FINISH"

        return f"ERROR: 未知工具 {tool}"
