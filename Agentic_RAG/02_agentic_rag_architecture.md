# 02. Agentic RAG 架构设计

> 目标：深入理解 Agentic RAG 的架构模式、关键组件和设计原则。

---

## 1. 核心架构全景

```text
┌─────────────────────────────────────────────────────┐
│                  Agentic RAG 系统                     │
│                                                     │
│  用户问题: "2024年AI监管政策对比"                      │
│     ↓                                               │
│  ┌─────────────┐   ┌──────────────┐                 │
│  │ 路由器 Router│ → │ 规划 Planner  │                 │
│  │  判断复杂度  │   │  拆解子问题    │                 │
│  └─────────────┘   └──────┬───────┘                 │
│                           ↓                          │
│  ┌──────────────────────────────────────────┐       │
│  │               检索层                       │       │
│  │  ┌──────────┐ ┌────────┐ ┌────────────┐  │       │
│  │  │向量数据库 │ │Web搜索 │ │SQL/API查询  │  │       │
│  │  └──────────┘ └────────┘ └────────────┘  │       │
│  └────────────────────┬─────────────────────┘       │
│                       ↓                              │
│  ┌──────────────────────────────────────────┐       │
│  │              评估层                         │       │
│  │  相关性评分、事实核查、完整性检查            │       │
│  └────────────────────┬─────────────────────┘       │
│                       ↓                              │
│  ┌──────────────────────────────────────────┐       │
│  │              生成层                         │       │
│  │  综合所有子问题的答案，结构化输出            │       │
│  └──────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

---

## 2. Single-Agent 架构（最常用）

### 架构 A：路由式（Router）

```python
class RouterAgent:
    """根据问题复杂度路由到不同策略"""
    
    def route(self, query):
        complexity = self.llm.analyze(query)
        
        if complexity == "simple":
            return SimpleRAG(query)      # 传统单步检索
        elif complexity == "moderate":
            return DecomposeRAG(query)   # 分解成 2-3 个子问题
        elif complexity == "complex":
            return AgenticRAG(query)     # 完全 Agent 自主探索
```

### 架构 B：反思式（Reflective）

```text
Self-RAG (Asai et al., 2023) 的核心流程：

Step 1: 接收问题
  LLM 输出特殊 token：
    <RETRIEVE> ← "我需要检索"
    <NO_RETRIEVE> ← "不需要检索，直接回答"

Step 2: 检索（如果 Step 1 决定需要）
  从知识库检索相关文档

Step 3: 逐段评估
  对每个检索到的段落，LLM 输出：
    <ISREL> ← 这段相关
    <ISSUP> ← 这段支持答案
    <ISUSE> ← 这段有用

Step 4: 生成答案
  基于评估为"相关+有用+支持"的段落生成

Step 5: 自我验证
  对生成的每个事实输出：
    <FULLY_SUPPORTED> ← 有充分依据
    <PARTIALLY_SUPPORTED> ← 部分有依据
    <NO_SUPPORT> ← 没有依据 → 删除或标注不确定
```

### 架构 C：纠正式（Corrective）

```text
CRAG (Yan et al., 2024) 的核心流程：

Step 1: 检索
  从知识库检索相关文档

Step 2: 评估检索质量
  检索结果评估器打分：
    分数 > 0.7 → 置信度高，直接使用
    分数 0.3-0.7 → 置信度中，结合 Web 搜索补充
    分数 < 0.3 → 置信度低，完全改用 Web 搜索

Step 3: 知识精炼
  从检索结果中提取关键事实
  去重、去噪、结构化

Step 4: 生成 + 验证
  生成答案
  对答案中的每个声明进行事实核查
  不支持的声明自动修正
```

---

## 3. Multi-Agent 架构

```text
多 Agent 协作时的典型分工：

┌──────────────┐
│ Planner Agent │ ← 分析问题、拆解子任务、分配工作
└──────┬───────┘
       │
  ┌────┴────┬──────────────┐
  ▼         ▼              ▼
┌───────┐ ┌──────────┐ ┌──────────┐
│Search │ │ Database │ │  Web     │
│ Agent │ │  Agent   │ │  Agent   │
│向量检索│ │ SQL查询   │ │ 互联网搜索│
└───┬───┘ └────┬─────┘ └────┬─────┘
    │          │            │
    └──────────┼────────────┘
               ▼
       ┌──────────────┐
       │  Reviewer     │ ← 交叉验证各 Agent 的结果
       │  Agent        │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │  Writer       │ ← 综合所有结果、生成最终答案
       │  Agent        │
       └──────────────┘
```

---

## 4. 分阶段 Agentic RAG 的实现

参考 LangGraph 和 LlamaIndex 的架构，一般实现为以下几个节点：

```python
from typing import TypedDict, Literal

class AgenticRAGState(TypedDict):
    query: str                # 用户原始问题
    sub_queries: list[str]    # 分解后的子问题
    retrieved_docs: list      # 检索到的文档
    evaluation: dict          # 检索质量评估
    answer: str               # 最终答案
    confidence: float         # 置信度
    iterations: int           # 已迭代次数

def agentic_rag_graph():

    # Node 1: 分析问题
    def analyze_query(state):
        """判断问题复杂度，决定是否需要分解"""
        query = state["query"]
        analysis = llm.analyze(f"""
        分析以下问题的复杂度：
        1. 是否涉及多个子问题？
        2. 是否需要多步推理？
        3. 回答这个问题需要哪些信息？
        
        问题：{query}
        """)
        return {"analysis": analysis}

    # Node 2: 分解问题（如果需要）
    def decompose_query(state):
        """将复杂问题拆为子问题"""
        if state["analysis"]["complexity"] == "simple":
            return {"sub_queries": [state["query"]]}
        
        sub_queries = llm.generate(
            f"将以下问题分解为 2-5 个独立的子问题：{state['query']}"
        )
        return {"sub_queries": sub_queries}

    # Node 3: 检索（对每个子问题）
    def retrieve(state):
        """对每个子问题执行检索"""
        all_docs = []
        for sub_q in state["sub_queries"]:
            # 先用向量检索
            docs = vector_store.search(sub_q, top_k=5)
            all_docs.extend(docs)
            
            # 如果向量检索质量不够，补充 Web 搜索
            if self.evaluate_quality(docs) < 0.5:
                web_docs = web_search(sub_q)
                all_docs.extend(web_docs)
        
        # 去重、重排序
        all_docs = self.deduplicate_and_rerank(all_docs)
        return {"retrieved_docs": all_docs}

    # Node 4: 评估检索质量
    def evaluate_retrieval(state):
        """判断检索结果是否足够"""
        docs = state["retrieved_docs"]
        
        # 评估每条文档的相关性
        relevance = llm.evaluate(
            f"问题：{state['query']}\n检索到的文档：{docs}",
            criteria=["相关性", "完整性", "时效性"]
        )
        
        if relevance["score"] < 0.6 and state["iterations"] < 3:
            # 质量不够，重新检索（用不同策略）
            return {"evaluation": relevance, "should_retry": True}
        
        return {"evaluation": relevance, "should_retry": False}

    # Node 5: 生成答案
    def generate_answer(state):
        """基于检索结果生成答案"""
        prompt = f"""
        基于以下检索到的文档，回答问题。
        如果文档不充分，请明确指出哪些信息缺失。
        
        问题：{state['query']}
        文档：{state['retrieved_docs']}
        
        要求：
        1. 每个事实都要标注来源
        2. 不确定的地方要标注
        3. 按结构组织（背景/分析/结论）
        """
        answer = llm.generate(prompt)
        return {"answer": answer}

    # 路由：要不要重试？
    def should_retry(state):
        if state.get("should_retry") and state["iterations"] < 3:
            return "retrieve"  # 返回检索节点
        return "generate"      # 进入生成节点
```

---

## 5. 关键设计原则

```text
原则 1：检索质量评估是核心
  不能"搜到什么用什么"
  要有判断"搜得好不好"的能力
  不好就换策略

原则 2：多工具、多源检索
  只依赖向量搜索不够
  Web 搜索、SQL 查询、API 调用都是合法工具

原则 3：迭代而非一步到位
  接受"第一次搜得不好"的现实
  允许 Agent 多轮迭代直到满意

原则 4：自我验证（Hallucination Guard）
  对生成答案中的每个事实进行来源标注
  无法验证的声明要明确标注"不确定"

原则 5：成本可控
  简单问题用简单策略（不启动完整 Agent）
  设置最大迭代次数防止死循环
  缓存热门查询结果
```

---

## 6. 一句话总结

> Agentic RAG 的架构本质上是"把检索策略从硬编码升级为可自主决策的 Agent Loop"。核心组件包括：问题分析器、检索路由、多工具/多源检索、检索质量评估器、答案生成器和自我验证器。Single-Agent 适合大多数场景，Multi-Agent 适合超复杂、多领域交叉的查询。
