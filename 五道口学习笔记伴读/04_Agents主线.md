# 04 · Agents 主线（伴读）

> 对应原始库：`agents/`（129 文件）。
> Agents = 让 LLM 通过"上下文 + 工具 + 记忆 + 多步推理"完成复杂任务。本伴读按"原子能力 → 系统"的顺序组织，避免一上来就读最花哨的 Multi-Agents。

## 0. 一个 Agent 由什么组成

```
                  ┌─────────────┐
   用户输入 ──────▶│ Context      │  把任务/历史/工具描述组装成 prompt
                  │ Engineering  │
                  └──────┬──────┘
                         ▼
                  ┌─────────────┐
                  │ LLM (推理)   │  reasoning-planning / tree_search
                  └──────┬──────┘
                         ▼
              ┌──────────┼──────────┐
              ▼          ▼           ▼
         Tools/MCP    Memory/RAG   Multi-Agents
         (行动)       (记忆)        (协作)
```

## 1. 学习动线（严格顺序）

### 1.1 提示词基础 → `agents/prompts/`
- 先懂 prompt 怎么写，后面所有 agent 都是"精心构造的 prompt + 循环"。

### 1.2 上下文工程 → `agents/context-engineering/`（21 文件，2024-2025 核心范式）
- **Context Engineering = 动态地把正确的信息放进上下文窗口**。比"写个好 prompt"更系统：何时检索、何时压缩、何时丢弃。
- 这是 Agent 效果的上限决定者（上下文里没信息，模型再强也没用）。

### 1.3 检索与记忆 → `agents/rag/` + `agents/memory-rag/`
- `rag/`：检索增强生成（向量库、召回、重排）。
- `memory-rag/`：长期记忆机制（让 agent 跨会话记住东西）。
- 区别：RAG 是"临时查资料"，Memory 是"长期记住用户/历史"。

### 1.4 工具与协议 → `agents/tools/` + `agents/mcp-skills/`
- `tools/`：让 LLM 调用函数（function calling）。
- `mcp-skills/`：**MCP（Model Context Protocol）**——把工具/数据源标准化成可插拔的服务，agent 按需连接。这是 2024-2025 的工具生态标准。

### 1.5 推理与搜索 → `agents/reasoning-planning/` + `agents/tree_search/`
- `reasoning-planning/`：CoT、计划-执行、ReAct 等推理范式。
- `tree_search/`：把决策建模成树，用搜索（MCTS 等）找最优路径（连回 `01` 的 search-based 范式、AlphaGo 思路）。

### 1.6 多智能体 → `agents/Multi-Agents/`
- 多个 agent 分工协作（如 planner + coder + reviewer）。
- 注意：多 agent 不是银弹，通信开销和一致性是难点。

### 1.7 框架与项目 → `agents/langchain-graph/`、`开源项目/`、`app/`、`self-evolving/`、`research_papers/`
- `langchain-graph/`：用 LangGraph 等框架把上面能力编排成图（节点=步骤，边=流转）。
- `self-evolving/`：agent 自我进化（连回你的 `AgentEvolve/`、`AgentRl/`）。
- `research_papers/`：相关论文。

## 2. 关键范式对照

| 范式 | 一句话 | 库内位置 |
|---|---|---|
| ReAct | 推理(Reason) + 行动(Act) 交替 | `reasoning-planning` |
| Plan-and-Execute | 先规划再分步执行 | `reasoning-planning` |
| RAG | 先检索再生成 | `rag` |
| MCP | 工具/数据标准化接入 | `mcp-skills` |
| Tree Search | 决策树搜索最优 | `tree_search` |
| Multi-Agent | 多角色协作 | `Multi-Agents` |

## 3. 和你其他文件夹的关系

- `Agent系统设计/`、`Agentic_RAG/`、`GUI_Agent/`、`Harness_Engineering/`、`Hermes/`：都是 Agent 主题的不同切面，可与本主线对照读。
- `AgentEvolve/`：self-evolving 的深入版。
- `AgentRl/` + 本伴读 `03`：Agent 通过 RL 变强的后训练手段。

## 4. 在原始库里的阅读落点（精确路径）

`agents/prompts/` → `agents/context-engineering/` → `agents/rag/` + `memory-rag/` → `agents/tools/` + `mcp-skills/` → `agents/reasoning-planning/` + `tree_search/` → `agents/Multi-Agents/` → `agents/langchain-graph/` + `开源项目/` + `self-evolving/`

另：`agents/Modern Agents.pptx` 是 up 主整理的总览幻灯片，适合在读完一轮后回顾。

## 验收

- [ ] 能画出 Agent 的组成图（context → LLM → tools/memory/multi-agent）
- [ ] 能解释 Context Engineering 与"写 prompt"的区别
- [ ] 能区分 RAG（临时检索）与 Memory（长期记忆）
- [ ] 能说清 MCP 解决什么问题
- [ ] 能讲清 ReAct / Plan-and-Execute / Tree Search 的差异
- [ ] 理解多 agent 的通信开销难点
