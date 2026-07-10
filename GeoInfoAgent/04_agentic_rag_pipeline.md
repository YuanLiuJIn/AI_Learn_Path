# 04. Agentic RAG 检索引擎设计

---

## 1. Pipeline 架构

```text
用户查询 → Query Router → Multi-Source Retriever
                                ↓
                          Self-RAG Evaluator
                                ↓
                         ┌── 够好了？──┐
                         ↓             ↓
                        是             否
                         ↓             ↓
                      Generator    CRAG Corrector
                                      ↓
                                  重新检索
                                      ↓
                              再次 Evaluator
```

---

## 2. Query Router：复杂度判断

```python
class QueryRouter:
    """简单查询 → 单次检索，复杂查询 → 分解 + 多轮"""
    
    def route(self, query):
        prompt = f"""分析查询复杂度：
        
查询：{query}

判断维度：
1. 是否涉及多个地点/实体？（多地点+1分）
2. 是否涉及多个指标/维度？（多指标+1分）
3. 是否需要跨时间段对比？（跨时间+1分）
4. 是否需要多源数据交叉验证？（多方验证+1分）

返回格式：{{"complexity": "simple|moderate|complex", "score": 0-4}}
"""
        result = llm.invoke(prompt)
        complexity = json.loads(result)["complexity"]
        return {
            "simple":   SimpleRAGStrategy(),
            "moderate": DecomposeRAGStrategy(),
            "complex":  FullAgenticRAGStrategy(),
        }[complexity]
```

---

## 3. 多源检索引擎

```python
class MultiSourceRetriever:
    """向量搜索 + BM25 + Web搜索 + SQL查询"""
    
    def __init__(self):
        self.vector_store = ChromaDB(embedding=BGE())
        self.bm25_index = BM25Okapi()
        self.web_search = TavilyClient()
        self.sql_db = PostgreSQL()
    
    def retrieve(self, query, sub_queries=None):
        results = []
        
        for sub_q in (sub_queries or [query]):
            # 1. 向量语义搜索
            vector_results = self.vector_store.similarity_search(sub_q, k=5)
            
            # 2. BM25 关键词搜索
            bm25_results = self.bm25_index.search(sub_q, k=3)
            
            # 3. 融合去重（RRF: Reciprocal Rank Fusion）
            fused = self.rrf_fuse(vector_results, bm25_results)
            
            # 4. 质量评估 → 不足则补充 Web 搜索
            if self.evaluate_quality(fused, sub_q) < 0.6:
                web_results = self.web_search.search(sub_q)
                fused.extend(web_results)
            
            results.append(fused)
        
        return results
    
    def rrf_fuse(self, results_a, results_b, k=60):
        """倒数排名融合"""
        scores = {}
        for rank, doc in enumerate(results_a):
            scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
        for rank, doc in enumerate(results_b):
            scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
```

---

## 4. Self-RAG 评估器

```python
class SelfRAGEvaluator:
    """自主评估检索质量"""
    
    def evaluate(self, query, retrieved_docs):
        prompt = f"""评估以下检索结果：
        
查询：{query}
检索结果：{retrieved_docs[:5]}

评估维度（每个0-10分）：
1. 相关性：结果和查询的语义匹配度
2. 完整性：是否覆盖了查询的所有方面
3. 可靠性：来源是否权威、数据是否可追溯
4. 时效性：数据时间是否在查询范围内

返回：{{"relevance": 8, "completeness": 6, "reliability": 9, "timeliness": 7}}
"""
        scores = json.loads(llm.invoke(prompt))
        avg_score = sum(scores.values()) / len(scores)
        return {"scores": scores, "avg": avg_score, "needs_improvement": avg_score < 6}
```

---

## 5. CRAG 修正器

```python
class CRAGCorrector:
    """检索不足时自动修正策略"""
    
    def correct(self, query, retrieved_docs, evaluation):
        if not evaluation["needs_improvement"]:
            return retrieved_docs
        
        # 根据短板决定修正策略
        if evaluation["scores"]["completeness"] < 5:
            # 分解为更细粒度的子查询
            sub_queries = self.decompose_query(query)
            strategy = "decompose"
        
        elif evaluation["scores"]["relevance"] < 5:
            # 换关键词重搜
            new_keywords = self.generate_better_keywords(query)
            strategy = "re_keyword"
        
        elif evaluation["scores"]["timeliness"] < 5:
            # 限定时间范围重搜
            strategy = "time_constrained"
        
        additional_docs = self.re_retrieve(query, strategy)
        return retrieved_docs + additional_docs
    
    def generate_better_keywords(self, failed_query):
        """让 LLM 生成更好的搜索关键词"""
        prompt = f"""以下查询的检索效果不好，请生成3个更好的搜索关键词：
原查询：{failed_query}
返回：["关键词1", "关键词2", "关键词3"]
"""
        return json.loads(llm.invoke(prompt))
```

---

## 6. 来源追溯

```python
class CitationTracer:
    """每个数据点标注来源、检索时间、置信度"""
    
    def trace(self, answer, retrieved_docs):
        cited_answer = []
        for sentence in answer.split("。"):
            # 找到支持这句话的文档
            supporting_docs = self.find_supporting_docs(sentence, retrieved_docs)
            
            if supporting_docs:
                citation = f"[来源: {supporting_docs[0].source}, "
                citation += f"检索时间: {supporting_docs[0].retrieved_at}, "
                citation += f"置信度: {supporting_docs[0].confidence:.0%}]"
                cited_answer.append(f"{sentence}({citation})")
            else:
                cited_answer.append(f"{sentence}(⚠️ 未找到来源依据)")
        
        return "。".join(cited_answer)
```
