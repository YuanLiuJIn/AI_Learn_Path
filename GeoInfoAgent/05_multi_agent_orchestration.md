# 05. 多 Agent 协作编排

---

## 1. 架构模式：Planner → Worker Pool → Reviewer

```text
 Planner Agent
      ↓ 任务分解 + 分配
 ┌────────────────────────┐
 │      Worker Pool        │
 │  ┌────┐┌────┐┌────┐┌──┐│
 │  │W1  ││W2  ││W3  ││W4││  并行执行
 │  │CMA ││NASA││API ││RAG││
 │  └────┘└────┘└────┘└──┘│
 └──────────┬─────────────┘
            ↓ 结果汇总
      Data Fusion Layer
            ↓
      Reviewer Agent（质量审核）
            ↓
      Writer Agent（报告生成）
```

---

## 2. Planner Agent 实现

```python
class PlannerAgent:
    """任务分解与分配"""
    
    def plan(self, user_query):
        # 1. 实体 + 指标 + 时间识别
        entities = self.extract_entities(user_query)
        metrics = self.extract_metrics(user_query)
        timerange = self.extract_timerange(user_query)
        
        # 2. 生成任务列表
        tasks = []
        for entity in entities:
            for metric in metrics:
                task = {
                    "id": f"{entity}_{metric}",
                    "location": entity,
                    "metric": metric,
                    "timerange": timerange,
                    "source": self.route_source(entity, metric),
                }
                tasks.append(task)
        
        # 3. 优先级排序（最重要的先执行）
        tasks = self.prioritize(tasks)
        
        return tasks
    
    def route_source(self, entity, metric):
        """根据实体+指标选择最佳数据源"""
        # 中国城市 + 气象指标 → CMA GUI Agent
        # 全球 + 遥感指标 → NASA GUI Agent
        # 已有CSV数据 → SQL Agent
        # 历史报告 → RAG Agent
        source_priority = [
            ("SQL",    self.check_sql_availability),
            ("API",    self.check_api_availability),
            ("CMA_GUI", self.check_cma_coverage),
            ("NASA_GUI", lambda: True),
            ("RAG",    lambda: True),
        ]
        
        for source_name, checker in source_priority:
            if checker(entity, metric):
                return source_name
        
        return "RAG"  # 最终兜底
```

---

## 3. Worker Pool 并行执行

```python
import asyncio

class WorkerPool:
    """并行执行多个采集任务"""
    
    def __init__(self):
        self.workers = {
            "CMA_GUI":  CMA_GUI_Worker(),
            "NASA_GUI": NASA_GUI_Worker(),
            "API":      API_Worker(),
            "RAG":      RAG_Worker(),
            "SQL":      SQL_Worker(),
        }
    
    async def execute(self, tasks, max_concurrent=5):
        """并行执行任务，最大并发数 5"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_task(task):
            async with semaphore:
                worker = self.workers[task["source"]]
                try:
                    result = await worker.run(task)
                    return {"task": task, "result": result, "status": "done"}
                except Exception as e:
                    return {"task": task, "error": str(e), "status": "failed"}
        
        results = await asyncio.gather(*[run_task(t) for t in tasks])
        return self.merge_results(results)
    
    def merge_results(self, results):
        """合并结果，标注成功/失败/部分"""
        data = {}
        for r in results:
            key = f"{r['task']['location']}_{r['task']['metric']}"
            data[key] = r
        return data
```

---

## 4. 数据融合层

```python
class DataFusionLayer:
    """多源数据交叉验证（Search-P1 思路）"""
    
    def fuse(self, collected_data, expected_metrics):
        report = {"verified": [], "partial": [], "missing": [], "conflicts": []}
        
        for metric in expected_metrics:
            sources = self.get_sources_for_metric(collected_data, metric)
            
            if len(sources) == 0:
                report["missing"].append({"metric": metric, "reason": "无数据源返回"})
            
            elif len(sources) == 1:
                report["partial"].append({"metric": metric, "source": sources[0]})
            
            else:
                # 多源交叉验证
                consensus = self.check_consensus(sources)
                if consensus["consistent"]:
                    report["verified"].append(consensus)
                else:
                    report["conflicts"].append(consensus)
        
        return report
    
    def check_consensus(self, sources):
        """检查多源数据一致性"""
        values = [s["value"] for s in sources]
        avg = sum(values) / len(values)
        deviations = [abs(v - avg) / avg for v in values]
        
        consistent = all(d < 0.1 for d in deviations)  # <10% 偏差算一致
        
        return {
            "consistent": consistent,
            "values": values,
            "avg": avg,
            "max_deviation": max(deviations),
            "sources": [s["source"] for s in sources],
        }
```

---

## 5. Reviewer Agent

```python
class ReviewerAgent:
    """质量审核：完整性 + 合理性 + 交叉验证"""
    
    def review(self, fusion_report, original_query):
        issues = []
        
        # 1. 完整性检查
        if fusion_report["missing"]:
            issues.append(f"缺失数据：{len(fusion_report['missing'])} 项")
        
        # 2. 矛盾检查
        if fusion_report["conflicts"]:
            for c in fusion_report["conflicts"]:
                issues.append(f"数据矛盾：{c['metric']} 在多源间偏差 {c['max_deviation']:.1%}")
        
        # 3. 合理性检查（LLM）
        llm_review = self.llm_review(fusion_report, original_query)
        if llm_review["anomalies"]:
            issues.extend(llm_review["anomalies"])
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "recommendation": "建议补充数据源" if issues else "数据质量合格",
        }
```

---

## 6. Writer Agent

```python
class WriterAgent:
    """结构化报告生成"""
    
    def generate(self, fusion_report, review):
        prompt = f"""
基于以下数据生成地理信息汇总报告：

验证通过的数据：{fusion_report['verified']}
部分可用数据：{fusion_report['partial']}
缺失数据：{fusion_report['missing']}
数据矛盾：{fusion_report['conflicts']}
质量审核：{review}

报告要求：
1. 先用表格列出所有指标和数值，标注数据来源
2. 缺失数据和矛盾数据单独说明
3. 按地区/指标维度做简要分析
4. 给出数据可靠性的整体评价
"""
        return llm.invoke(prompt)
```
