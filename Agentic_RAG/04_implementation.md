# 04. 动手实现：用 LangGraph 构建 Agentic RAG

> 目标：用 LangGraph 构建一个完整的 Agentic RAG 系统。
> 包含路由、检索、评估、迭代修正和最终生成。

---

## 1. 环境准备

```bash
pip install langgraph langchain langchain-openai chromadb
```

---

## 2. 完整的 Agentic RAG 实现

```python
from typing import TypedDict, List, Literal, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.tools import tool
import operator

# ---------- 定义状态 ----------
class AgenticRAGState(TypedDict):
    query: str                          # 用户原始问题
    sub_queries: Annotated[List[str], operator.add]  # 分解后的子问题
    retrieved_docs: List[str]           # 检索到的文档列表
    evaluation_score: float             # 检索质量评分
    answer: str                         # 最终答案
    iteration_count: int                # 当前迭代次数
    should_retry: bool                  # 是否需要重新检索

# ---------- 初始化模型和工具 ----------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vector_store = Chroma(...)  # 你的向量数据库

@tool
def web_search(query: str) -> str:
    """当内部知识库不够时，使用 Web 搜索补充"""
    # 调用 Web 搜索 API
    return search_web(query)

@tool
def sql_query(query: str) -> str:
    """查询结构化数据库"""
    return execute_sql(query)

# ---------- Node 1: 分析问题复杂度 ----------
def analyze_complexity(state: AgenticRAGState) -> AgenticRAGState:
    """判断问题是否需要分解"""
    prompt = f"""
分析以下问题的复杂度：
1. 是否涉及多个独立子问题？（是/否）
2. 是否需要多步推理？（是/否）
3. 回答难度（简单/中等/复杂）

问题：{state['query']}
返回格式：{{"complexity": "simple/moderate/complex"}}
"""
    result = llm.invoke(prompt)
    state["complexity"] = eval(result.content)["complexity"]
    return state

# ---------- Node 2: 分解问题（如果需要） ----------
def decompose_query(state: AgenticRAGState) -> AgenticRAGState:
    """将复杂问题分解为子问题"""
    if state.get("complexity") == "simple":
        state["sub_queries"] = [state["query"]]
        return state

    prompt = f"""
将以下问题分解为 2-4 个独立的子问题，每个子问题应该可以独立检索和回答：

问题：{state['query']}

返回格式：["子问题1", "子问题2", ...]
"""
    result = llm.invoke(prompt)
    state["sub_queries"] = eval(result.content)
    return state

# ---------- Node 3: 多源检索 ----------
def retrieve(state: AgenticRAGState) -> AgenticRAGState:
    """对每个子问题执行检索，不足时补充 Web 搜索"""
    all_docs = []

    for sub_q in state["sub_queries"]:
        # 1. 向量检索
        docs = vector_store.similarity_search(sub_q, k=5)
        all_docs.extend([d.page_content for d in docs])

        # 2. 评估向量检索质量
        relevance_prompt = f"""
评估以下检索结果和子问题的相关性（0-10）：
子问题：{sub_q}
检索结果：{docs[:3]}
只返回数字。
"""
        score = float(llm.invoke(relevance_prompt).content.strip())

        # 3. 如果向量检索不够好，补充 Web 搜索
        if score < 5:
            web_results = web_search.invoke(sub_q)
            all_docs.append(web_results)

    # 4. 去重
    state["retrieved_docs"] = list(set(all_docs))
    return state

# ---------- Node 4: 评估检索质量 ----------
def evaluate_retrieval(state: AgenticRAGState) -> AgenticRAGState:
    """评估检索结果是否足以回答原始问题"""
    prompt = f"""
评估以下检索结果能否回答用户问题（0-10 分）：
- 信息是否完整？
- 来源是否可靠？
- 是否有矛盾信息？

用户问题：{state['query']}
检索结果：{state['retrieved_docs'][:5]}

返回格式：{{"score": 8.5, "reason": "..."}}
"""
    result = llm.invoke(prompt)
    evaluation = eval(result.content)
    state["evaluation_score"] = evaluation["score"]

    # 决定是否重试
    state["iteration_count"] = state.get("iteration_count", 0) + 1
    if state["evaluation_score"] < 6 and state["iteration_count"] < 3:
        state["should_retry"] = True
    else:
        state["should_retry"] = False

    return state

# ---------- Node 5: 重新检索（改进策略） ----------
def re_retrieve(state: AgenticRAGState) -> AgenticRAGState:
    """用改进后的策略重新检索"""
    # 让 LLM 生成更好的检索关键词
    prompt = f"""
上次检索质量评分只有 {state['evaluation_score']}/10。
请生成 3 个新的、更好的检索关键词，用来找到更相关的信息。

原始问题：{state['query']}
返回格式：["关键词1", "关键词2", "关键词3"]
"""
    result = llm.invoke(prompt)
    new_keywords = eval(result.content)

    # 用新关键词检索
    new_docs = []
    for kw in new_keywords:
        docs = vector_store.similarity_search(kw, k=3)
        new_docs.extend([d.page_content for d in docs])

    state["retrieved_docs"].extend(new_docs)
    state["retrieved_docs"] = list(set(state["retrieved_docs"]))
    return state

# ---------- Node 6: 生成最终答案 ----------
def generate_answer(state: AgenticRAGState) -> AgenticRAGState:
    """基于最好的检索结果生成答案"""
    prompt = f"""
基于以下检索到的信息，回答用户问题。

要求：
1. 每个关键事实都要标注来源文档编号
2. 不确定的地方要明确说明
3. 如果信息矛盾，列出不同来源的说法
4. 结构化输出（背景→分析→结论）

用户问题：{state['query']}

检索到的信息：
{state['retrieved_docs']}
"""
    result = llm.invoke(prompt)
    state["answer"] = result.content
    return state

# ---------- 构建 Graph ----------
def build_agentic_rag():
    workflow = StateGraph(AgenticRAGState)

    # 添加节点
    workflow.add_node("analyze", analyze_complexity)
    workflow.add_node("decompose", decompose_query)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("evaluate", evaluate_retrieval)
    workflow.add_node("re_retrieve", re_retrieve)
    workflow.add_node("generate", generate_answer)

    # 设置入口
    workflow.set_entry_point("analyze")

    # 添加边
    workflow.add_edge("analyze", "decompose")
    workflow.add_edge("decompose", "retrieve")
    workflow.add_edge("retrieve", "evaluate")

    # 条件路由：要不要重试？
    workflow.add_conditional_edges(
        "evaluate",
        lambda state: "re_retrieve" if state["should_retry"] else "generate",
        {
            "re_retrieve": "re_retrieve",
            "generate": "generate"
        }
    )

    workflow.add_edge("re_retrieve", "evaluate")  # 重新检索后再次评估
    workflow.add_edge("generate", END)

    return workflow.compile()

# ---------- 使用 ----------
agentic_rag = build_agentic_rag()

result = agentic_rag.invoke({"query": "2024年AI监管政策有哪些变化？"})
print(result["answer"])
```

---

## 3. 运行效果分析

```text
问题："2024年AI监管政策有哪些变化？"

流程追踪：
Step 1 [analyze]: complexity = "moderate"
Step 2 [decompose]: 
  - 子问题1: "2024年AI监管政策的具体内容"
  - 子问题2: "这些政策和之前年份的主要变化"
Step 3 [retrieve]: 
  - 向量检索返回 5+5=10 个文档
  - 评估向量检索质量得分 7.8 → 不需要补充 Web 搜索
Step 4 [evaluate]:
  - 信息完整性评分 8.2/10 → 不需要重试
Step 5 [generate]:
  - 基于 10 个文档生成结构化答案

最终答案特点：
  ✓ 每个政策变化都标注了来源文档
  ✓ 区分了"已确认"和"待查证"的信息
  ✓ 按地区（美国/欧盟/中国）分类
```

---

## 4. 优化方向

```text
1. 缓存搜索结果：相同查询不重复搜
2. 异步并发检索：多个子问题并行搜索
3. 结构化输出：要求模型输出 JSON，方便下游处理
4. 用户反馈闭环：用户对答案的评价反馈回评估器
5. 成本控制：简单问题跳过完整流程
```

---

## 5. 一句话总结

> LangGraph 实现的 Agentic RAG 本质上是一个状态机：分析问题 → 分解子问题 → 多源检索 → 质量评估 → 必要时重试 → 最终生成。关键是加入了检索质量评估和迭代修正的闭环，让系统能自我改进。
