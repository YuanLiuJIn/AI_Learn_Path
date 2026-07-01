# 03 手写 Agent 从入门到放弃（番外）

> 本章是“番外”：用最少的代码把一个 LLM Agent 从零搭出来，体会它的能力边界与坑。它与 `Harness_Engineering/` 强相关——理解了 Agent 的脆弱，才明白为什么需要 Harness。

## 1. 什么是 Agent

普通用法：你问一句，模型答一句。**Agent**：给模型一个目标和一组工具，让它**自己循环**：思考 → 调用工具 → 看结果 → 再思考，直到完成任务。

```text
普通 LLM：  输入 -> 输出（一次性）
Agent：     目标 -> [思考->行动->观察]循环 -> 完成
```

## 2. 一句话直觉

> Agent = 一个会“自言自语 + 动手用工具”的 LLM。它把大任务拆成小步，每步决定“用哪个工具、传什么参数”，再根据工具返回继续。

## 3. 最小 Agent：ReAct 范式

ReAct（Reason + Act，Part2/Harness 都提过）是最经典的 Agent 循环：

```text
Thought：我需要先查一下天气
Action： weather(city="北京")
Observation：北京 晴 25℃
Thought：已经知道了，可以回答
Action： finish("北京今天晴，25℃")
```

## 4. 从零手写一个 Agent（核心代码）

```python
import json

TOOLS = {
    "calculator": lambda expr: str(eval(expr)),         # 计算
    "weather": lambda city: f"{city} 晴 25℃",           # 假装查天气
}

SYSTEM = """你是一个会用工具的 Agent。每步只输出一个 JSON：
{"thought": "...", "action": "工具名或finish", "args": "参数"}
可用工具：calculator(数学表达式)、weather(城市名)。
完成时 action 用 "finish"，args 填最终答案。"""

def run_agent(llm, question, max_steps=6):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    for _ in range(max_steps):
        reply = llm(messages)                 # LLM 返回一段 JSON
        step = json.loads(reply)
        if step["action"] == "finish":
            return step["args"]               # 任务完成
        tool = TOOLS.get(step["action"])
        obs = tool(step["args"]) if tool else "未知工具"
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": f"Observation: {obs}"})
    return "达到步数上限，未完成"
```

短任务里它工作得不错。问题在后面。

## 5. “从入门到放弃”：手写 Agent 会撞的墙

这正是标题的含义——朴素 Agent 在真实任务中很快崩溃：

```text
1. 输出格式不稳：LLM 偶尔不输出合法 JSON，解析就崩
2. 死循环：反复调同一个工具，或在两个状态间震荡
3. 幻觉工具/参数：调用不存在的工具，或传错参数
4. 无长期记忆：步数一多，早期目标被淹没（context rot）
5. 错误不恢复：工具报错后还在错误路径上一条道走到黑
6. 无终止判断：没做完就说"完成了"，或做完了还在瞎忙
7. 不可控/不可审计：出了问题不知道哪一步开始跑偏
```

你会发现：**让 Agent 跑起来很容易，让它可靠地完成复杂任务极难。**

## 6. 从“放弃”到“工程化”：这就是 Harness

这些坑没有一个能靠“把 prompt 写得更好”根治。解决之道是把约束、状态、反馈做成模型外部的确定性系统——也就是 Harness Engineering：

```text
输出不稳   -> 用结构化输出/函数调用 + 解析失败兜底
死循环     -> 步数/时间上限、循环检测（Watchdog）
幻觉工具   -> 工具 schema 校验、白名单
无记忆     -> 外部状态/progress file，每步只注入必要信息
不恢复     -> 错误分类 + 重试/回滚
无终止判断 -> 用测试/校验等客观信号判定完成
不可审计   -> trace 记录每步
```

> 详见 `Harness_Engineering/harness_engineering_guide.md` 与可运行项目 `mini_harness_project/`——那里把本章遇到的每个坑都做了工程化处理。

## 7. 现实中的 Agent 框架

```text
LangChain / LangGraph：链与图式编排
AutoGen：               多 Agent 对话
OpenHands：             coding agent 控制台
（但请记住：框架解决"怎么搭"，可靠性仍取决于 Harness 设计）
```

## 经典论文与开源项目

- Yao et al., "ReAct: Synergizing Reasoning and Acting", 2022。
- Schick et al., "Toolformer", 2023。
- Shinn et al., "Reflexion", 2023（让 Agent 反思错误）。
- GitHub: `langchain-ai/langchain`、`microsoft/autogen`、`OpenHands/OpenHands`。

## 本章小结

手写一个 ReAct Agent 只需几十行，但它在真实任务中会因格式不稳、死循环、幻觉、无记忆、不恢复、不可审计而“从入门到放弃”。这些问题不是模型不聪明，而是缺少外部控制系统——这正是 Harness Engineering 的用武之地，也是本章与 Harness 专题的衔接点。
