# 03. 关键机制：Self-RAG / CRAG / Adaptive RAG

> 目标：深入理解 Agentic RAG 中最重要的三种技术机制。
> Self-RAG 解决"要不要检索"；CRAG 解决"检索坏了怎么办"；Adaptive RAG 解决"不同问题用不同策略"。

---

## 1. Self-RAG：模型自己决定"是否需要检索"

### 核心思路

传统 RAG 无脑检索——每个问题都搜一下。但有些问题根本不需要检索：

```text
"今天星期几？"         ← 不需要检索
"1+1=？"               ← 不需要检索
"2024年中国GDP增速？"   ← 需要检索
"请翻译这句话"          ← 不一定需要
```

Self-RAG 让模型在生成过程中自主决定"要不要检索"和"检索结果好不好"。

### 关键技术

Self-RAG 训练模型输出特殊的"反思 token"：

```text
<RETRIEVE>  ← "我需要检索知识库"
<NO_RETRIEVE> ← "不需要检索，直接回答"

检索完成后对每个段落：
<ISREL>  ← "这个段落和问题相关"
<ISSUP>  ← "这个段落支持我的答案"
<ISUSE>  ← "这个段落有用"

生成答案后：
<FULLY_SUPPORTED>  ← "这句话有充分依据"
<PARTIALLY_SUPPORTED> ← "这句话部分有依据"
<NO_SUPPORT> ← "这句话没有依据 → 删除或标注"
```

### 伪代码

```python
class SelfRAG:
    def generate(self, query):
        """Self-RAG 的生成流程"""
        output_tokens = []

        for token in self.llm.stream(query):
            if token == "<RETRIEVE>":
                # 模型决定需要检索了
                docs = self.retrieve(query)
                output_tokens.append(f"[检索到 {len(docs)} 条文档]")
                
                for doc in docs:
                    relevance = self.reflection_model.evaluate(doc, query)
                    if relevance == "<ISREL>":
                        output_tokens.append(doc.content)

            elif token == "<NO_RETRIEVE>":
                # 不需要检索，继续生成
                continue

            elif token in ["<FULLY_SUPPORTED>", "<PARTIALLY_SUPPORTED>"]:
                # 前面生成的句子有依据，继续
                continue

            elif token == "<NO_SUPPORT>":
                # 前面生成的句子没有依据，删除
                output_tokens = self.remove_last_sentence(output_tokens)
                continue

            else:
                output_tokens.append(token)

        return "".join(output_tokens)
```

---

## 2. CRAG（Corrective RAG）：检索坏了就修

### 核心思路

CRAG 的关键洞察：**检索可能失败，不能盲目信任检索结果。**

```text
问题："量子计算对密码学的影响"

检索返回 5 个文档：
  A：讲量子计算的物理学原理 → 不相关
  B：讲区块链 → 不相关
  C：讲密码学基础 → 部分相关，但没提量子
  D：讲量子密码学 → 高度相关！
  E：讲AI安全 → 完全不相关

传统 RAG：把 5 个文档全给到 LLM → 噪音污染
CRAG：先评估质量，只保留高质量文档，不够就外部补充
```

### 检索质量评估器

```python
class RetrievalEvaluator:
    """CRAG 的检索质量评估器"""
    
    def evaluate(self, query, retrieved_docs):
        """评估每条文档的相关性"""
        scores = []
        for doc in retrieved_docs:
            score = self.llm_score_relevance(
                query=query,
                document=doc,
                prompt="""
                评估这个文档和问题的相关性（0-10）：
                10: 完美匹配
                7-9: 高度相关
                4-6: 部分相关
                1-3: 弱相关
                0: 完全不相关
                """
            )
            scores.append(score)
        return scores

    def decide_action(self, avg_score):
        """根据平均分决定下一步"""
        if avg_score >= 7:
            return "use_directly"    # 直接用
        elif avg_score >= 4:
            return "supplement"       # 补充 Web 搜索
        else:
            return "discard_and_web"  # 完全改用 Web 搜索

class CorrectiveRAG:
    def answer(self, query):
        # 1. 检索
        docs = vector_db.search(query, top_k=10)
        
        # 2. 评估检索质量
        evaluator = RetrievalEvaluator()
        scores = evaluator.evaluate(query, docs)
        
        # 3. 根据平均分决定策略
        avg_score = sum(scores) / len(scores)
        action = evaluator.decide_action(avg_score)
        
        if action == "use_directly":
            # 保留高分文档
            good_docs = [d for d, s in zip(docs, scores) if s >= 7]
            return self.generate_answer(query, good_docs)
        
        elif action == "supplement":
            # 补充 Web 搜索
            web_results = web_search(query)
            all_docs = docs + web_results
            return self.generate_answer(query, all_docs)
        
        else:
            # 完全改用 Web 搜索
            web_results = web_search(query)
            return self.generate_answer(query, web_results)
    
    def generate_answer(self, query, docs):
        # 4. 知识精炼
        refined = self.extract_key_facts(docs)
        
        # 5. 生成答案
        answer = self.llm.generate(f"""
        基于以下事实回答问题：
        
        问题：{query}
        可用的知识：{refined}
        
        要求：每个事实标注来源
        """)
        
        # 6. 事实核查
        verified = self.fact_check(answer, refined)
        
        return verified
```

---

## 3. Adaptive RAG：不同复杂度用不同策略

### 核心思路

```text
不是所有问题都应该走完整 Agentic RAG 流程。

简单问题："今天天气怎么样？"
  → 直接回答或一次检索即可
  → 走完整 Agentic RAG 浪费时间

复杂问题："对比 2024 年和 2025 年 AI 监管政策的变化"
  → 需要多步检索 + 分解子问题 + 验证
  → 值得走完整 Agentic RAG
```

### 复杂度自适应分类器

```python
class ComplexityRouter:
    """根据问题复杂度路由到不同策略"""
    
    def classify(self, query):
        """判断问题的复杂度级别"""
        features = {
            "length": len(query.split()),
            "has_comparison": any(w in query for w in ["对比", "比较", "vs", "区别"]),
            "has_temporal": any(w in query for w in ["2024", "2025", "去年", "今年"]),
            "has_multi_entity": self.count_entities(query) > 2,
            "has_causality": any(w in query for w in ["为什么", "原因", "导致"]),
        }
        
        score = sum(features.values())
        
        if score <= 1:
            return "simple"      # 简单问题：单次检索或直接回答
        elif score <= 3:
            return "moderate"    # 中等复杂：分解为 2-3 个子问题
        else:
            return "complex"     # 复杂：完全 Agentic RAG

    def route(self, query):
        complexity = self.classify(query)
        
        if complexity == "simple":
            # 方案 1：单次检索或直接回答
            return self.simple_rag(query)
        
        elif complexity == "moderate":
            # 方案 2：拆解为子问题，每个子问题用 Self-RAG
            sub_queries = self.decompose(query)
            answers = [self.self_rag(sub_q) for sub_q in sub_queries]
            return self.synthesize(answers)
        
        else:
            # 方案 3：完整 Agentic RAG 流程
            return self.full_agentic_rag(query)
```

---

## 4. 三者的关系和应用场景

```text
Self-RAG：
  解决"要不要检索"和"检索质量好不好"的问题
  适合：中等复杂度的单步查询
  例："2024年全球GDP增长率是多少？"

CRAG：
  解决"检索失败了怎么办"的问题
  适合：对准确性要求极高的场景
  例：医疗诊断、法律咨询、金融分析

Adaptive RAG：
  解决"不同问题用不同策略"的成本优化问题
  适合：生产系统，处理大量不同复杂度的问题
  例：企业知识库问答系统

三者可以组合：
  先 Adaptive RAG 判断复杂度
  → 简单问题直接回答
  → 中等问题用 Self-RAG
  → 复杂问题用 CRAG + Agentic 多步检索
```

---

## 5. 一句话总结

```text
Self-RAG  = 模型会说"我需要查资料"和"查到的资料不对"
CRAG     = 检索失败时自动换策略、换数据源
Adaptive RAG = 简单问题快速过，复杂问题深度查，成本最优
```
