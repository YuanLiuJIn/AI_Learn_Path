"""SkillForge —— 一个自研的、整洁、集成度高的 Skill 自进化引擎。

核心设计亮点：

1. **端到端沙箱评测**：不只做"文档体检"（静态断言），还能在隔离环境中真正
   执行 skill、校验真实产物与行为（借鉴 Voyager 的环境反馈思想）。
2. **Beam Search 搜索**：从单链贪心升级为并行多候选搜索，避免局部最优。
3. **统计显著性门控**：用置信区间替代硬阈值，缓解 LLM 评测噪声。
4. **三层结构化记忆**：raw trace → failure lessons → reusable patterns，
   跨 skill 复用经验（借鉴 AutoSkill 的终身学习与 SkillRL 的经验蒸馏）。
5. **跨平台 UTF-8**：所有文件 IO 显式声明 UTF-8，Windows/Linux/macOS 一致。
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
