# 01. 系统架构设计

---

## 1. 系统全景

```text
┌─────────────────────────────────────────────────────┐
│                  用户查询                             │
│  "汇总北京、上海、广州过去一周的降水和气温数据"         │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Planner Agent（调度中心）                │
│                                                     │
│  输入：用户自然语言查询                                │
│  输出：{ tasks: [{city, metric, timerange, source}] } │
│                                                     │
│  ① 实体识别 → 城市？指标？时间？                        │
│  ② 数据源路由 → API / GUI Agent / RAG 检索            │
│  ③ 任务分配 → 并行 Worker Pool                       │
└────────┬────────────────────┬───────────────────────┘
         ↓                    ↓
┌─────────────────────┐  ┌──────────────────────┐
│  GUI Agent 采集组    │  │  Agentic RAG 检索组   │
│  （无 API 数据源）    │  │  （知识库+Web搜索）    │
│                     │  │                       │
│  Worker 1: CMA 气象站│  │  Worker 4: 知识库检索  │
│    DOM文本化 + 表单  │  │   向量搜索 + BGE      │
│                     │  │                       │
│  Worker 2: 卫星数据  │  │  Worker 5: Web 搜索   │
│    截图识别 + 地图   │  │   Tavily API          │
│                     │  │                       │
│  Worker 3: 天气API  │  │  质量评估(Self-RAG)   │
│    直接HTTP调用     │  │  自动修正(CRAG)        │
└────────┬────────────┘  └──────────┬─────────────┘
         ↓                          ↓
┌─────────────────────────────────────────────────────┐
│              数据融合层（Search-P1 思路）              │
│                                                     │
│  ① 自洽性检查：同一城市不同来源数据是否一致？            │
│  ② 对齐性检查：数据是否符合专家知识的预期？             │
│  ③ 完整性检查：所有请求维度都覆盖了吗？                 │
│  ④ 软性评分：部分缺失也给可用性评估                     │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Reviewer Agent（质量审核）                │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Writer Agent（报告生成）                  │
└─────────────────────────────────────────────────────┘
```

---

## 2. 数据源路由决策

```text
Planner Agent 的数据源路由逻辑：

查询中包含的地点/指标 → 查数据源注册表

数据源注册表示例：
┌──────────────┬──────────┬────────────────────────┐
│ 数据源        │ 是否有API │ Agent 类型              │
├──────────────┼──────────┼────────────────────────┤
│ CMA 气象数据   │ 否       │ GUI Agent (DOM)         │
│ NASA 卫星数据  │ 否       │ GUI Agent (截图+地图)    │
│ OpenWeather   │ 是       │ API Agent               │
│ 本地知识库     │ -        │ RAG Agent (向量搜索)    │
│ 历史CSV数据    │ -        │ SQL Agent               │
│ Web 搜索       │ -        │ Search Agent (Tavily)   │
└──────────────┴──────────┴────────────────────────┘
```

---

## 3. Planner Agent 的 Prompt 设计

```text
你是地理信息汇总平台的调度 Agent。

用户查询：{user_query}

你的任务：
1. 识别查询中涉及的地理实体（城市、区域、站点）
2. 识别查询中涉及的指标（降水、气温、风速等）
3. 识别时间范围
4. 为每个(实体, 指标, 时间)组合选择最佳数据源

数据源：
- CMA 气象平台（无API，需要 GUI Agent）：地面气象观测数据
- NASA 数据（无API，需要 GUI Agent）：卫星遥感数据  
- OpenWeather API：实时天气数据
- 本地知识库（RAG）：历史报告和分析文档
- 结构化数据库（SQL）：已有CSV数据

输出格式：
{
  "tasks": [
    {
      "location": "北京",
      "metric": "降水",
      "timerange": "2026-07-01~2026-07-07",
      "source": "CMA_GUI",
      "priority": 1
    }
  ]
}
```

---

## 4. 状态定义

```python
from typing import TypedDict, List, Optional
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    PARTIAL = "partial"

class DataTask(TypedDict):
    id: str
    location: str
    metric: str
    timerange: str
    source: str        # CMA_GUI / NASA_GUI / API / RAG / SQL
    status: TaskStatus
    result: Optional[dict]

class GeoInfoState(TypedDict):
    query: str                           # 用户原始查询
    tasks: List[DataTask]                # Planner 分配的任务列表
    collected_data: dict                 # 各 Worker 采集的原始数据
    fusion_report: dict                  # 数据融合 + 交叉验证结果
    quality_review: str                  # Reviewer 的审核意见
    final_report: str                    # 最终报告
    error_log: List[str]                 # 错误日志
```

---

## 5. 数据流图

```text
用户查询 → Planner拆解 → Task列表
                            ↓
                    ┌────并行执行────┐
                    ↓    ↓    ↓    ↓
                  GUI  GUI  API  RAG
                    ↓    ↓    ↓    ↓
                    └────结果汇总────┘
                            ↓
                      数据融合层
                     (自洽性+对齐性)
                            ↓
                      Reviewer审核
                     (完整性+合理性)
                            ↓
                      Writer生成报告
                     (表格+图表+文字)
```
