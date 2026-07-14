# 09. 专业实战项目路线

> 目标：给出适合深入学习知识图谱的实战项目，从入门 Demo 到接近真实业务的专业项目。

## 项目一：医疗知识图谱问答系统

### 1. 项目目标

构建一个疾病、症状、药品、检查、科室之间的知识图谱，并支持自然语言问答。

示例问题：

```text
感冒有哪些症状？
阿司匹林可以缓解哪些症状？
糖尿病应该做哪些检查？
发热应该挂什么科？
哪些药物可能导致胃出血？
```

### 2. 图谱 Schema

```text
实体类型：
  Disease    疾病
  Symptom    症状
  Drug       药品
  Checkup    检查项
  Department 科室
  Food       食物

关系类型：
  Disease -[HAS_SYMPTOM]-> Symptom
  Disease -[TREATED_BY]-> Drug
  Disease -[NEEDS_CHECKUP]-> Checkup
  Disease -[BELONGS_TO]-> Department
  Drug -[HAS_SIDE_EFFECT]-> Symptom
  Disease -[AVOID_FOOD]-> Food
```

### 3. 技术栈

```text
Python
Neo4j
Cypher
规则模板 / LLM 抽取
FastAPI
简单前端或命令行问答
```

### 4. 学习点

```text
Schema 设计
实体和关系建模
Cypher 查询
自然语言问题分类
问题模板到 Cypher
图查询结果转自然语言回答
```

### 5. 进阶方向

```text
加入实体别名和实体对齐
加入药品禁忌和风险推理
加入 LLM 生成答案但必须引用图谱证据
加入 GraphRAG：图查询 + 文档检索混合回答
```

---

## 项目二：论文知识图谱与研究脉络分析

### 1. 项目目标

构建论文、作者、机构、方法、任务、数据集之间的知识图谱，用来分析一个研究方向的发展脉络。

示例问题：

```text
Transformer 之后有哪些关键论文？
哪些论文使用了对比学习？
某个作者主要研究哪些方向？
某个数据集被哪些论文使用？
某篇论文启发了哪些后续工作？
```

### 2. 图谱 Schema

```text
实体类型：
  Paper
  Author
  Institution
  Method
  Task
  Dataset
  Venue

关系类型：
  Paper -[WRITTEN_BY]-> Author
  Author -[AFFILIATED_WITH]-> Institution
  Paper -[PROPOSES]-> Method
  Paper -[EVALUATES_ON]-> Dataset
  Paper -[SOLVES]-> Task
  Paper -[CITES]-> Paper
  Paper -[PUBLISHED_IN]-> Venue
```

### 3. 数据来源

```text
arXiv 元数据
Semantic Scholar API
OpenAlex
本地论文 PDF
手工整理的论文列表
```

### 4. 学习点

```text
论文元数据解析
引用网络构建
实体对齐：作者重名、机构别名
社区发现：研究流派分析
路径分析：论文影响链
GraphRAG：基于论文图谱做综述问答
```

### 5. 专业价值

这个项目非常适合做个人 AI 学习站的“论文细读”支撑系统：

```text
论文不是孤立的文章，而是一个互相引用、继承、扩展的知识网络。
```

---

## 项目三：企业关系与风险传播图谱

### 1. 项目目标

构建企业、人员、股权、投资、供应链、风险事件之间的知识图谱，分析间接关系和风险传播路径。

示例问题：

```text
A 公司间接控制了哪些公司？
某风险事件可能影响哪些供应商？
某个人同时在哪些公司任职？
两家公司之间是否存在隐藏关联？
```

### 2. 图谱 Schema

```text
实体类型：
  Company
  Person
  Product
  Event
  Industry
  Region

关系类型：
  Company -[INVESTS_IN]-> Company
  Company -[CONTROLS]-> Company
  Person -[LEGAL_REPRESENTATIVE_OF]-> Company
  Person -[EXECUTIVE_OF]-> Company
  Company -[SUPPLIES_TO]-> Company
  Company -[HAS_RISK_EVENT]-> Event
  Company -[LOCATED_IN]-> Region
  Company -[BELONGS_TO]-> Industry
```

### 3. 学习点

```text
多跳路径查询
最短路径
间接控制链
风险路径解释
中心性分析
社区发现
图算法与业务规则结合
```

### 4. 示例 Cypher

```cypher
MATCH path = (a:Company {name:'A公司'})-[:INVESTS_IN|CONTROLS*1..4]->(b:Company)
RETURN path
```

### 5. 进阶方向

```text
加入时间维度：关系何时开始、何时结束
加入风险评分模型
加入图神经网络做风险预测
加入 GraphRAG 自动生成风险分析报告
```

---

## 项目四：电商商品知识图谱与推荐系统

### 1. 项目目标

构建商品、品牌、类目、属性、用户行为之间的图谱，用于语义搜索和推荐解释。

示例问题：

```text
和这款手机相似的商品有哪些？
适合学生党的轻薄本有哪些？
为什么推荐这个商品？
某品牌下有哪些高性价比产品？
```

### 2. 图谱 Schema

```text
实体类型：
  Product
  Brand
  Category
  Attribute
  User
  Review

关系类型：
  Product -[BELONGS_TO]-> Category
  Product -[MADE_BY]-> Brand
  Product -[HAS_ATTRIBUTE]-> Attribute
  User -[VIEWED]-> Product
  User -[BOUGHT]-> Product
  User -[LIKES]-> Category
  Product -[SIMILAR_TO]-> Product
```

### 3. 学习点

```text
属性图建模
用户行为图
相似商品路径
基于图的推荐解释
图算法：PageRank、Personalized PageRank、社区发现
图谱 + 向量混合召回
```

---

## 项目五：GraphRAG 文档知识库

### 1. 项目目标

给一批技术文档或学习笔记，自动抽取实体和关系，构建知识图谱，并支持复杂问答。

示例问题：

```text
RAG、Agent 和知识图谱之间是什么关系？
哪些文章都提到了实体对齐？
多模态检索和知识图谱在哪些地方可以结合？
这个知识库中有哪些主要主题社区？
```

### 2. 系统架构

```text
文档集合
  ↓
文本切分
  ↓
实体与关系抽取
  ↓
实体对齐
  ↓
构建图谱
  ↓
社区发现
  ↓
社区摘要
  ↓
GraphRAG 问答
```

### 3. 技术栈

```text
Python
LLM 结构化抽取
Neo4j / NetworkX
向量数据库或本地向量索引
Rerank 模型
FastAPI / Streamlit
```

### 4. 学习点

```text
LLM 抽取控制
Schema 约束
图谱和向量检索融合
社区摘要
局部问答与全局问答
答案引用和证据链
```

---

## 推荐最终项目：AI 学习知识图谱 + GraphRAG

最适合你当前学习路线的综合项目：

> 把自己的 AI 学习笔记、论文细读、多模态检索、Agent、RAG、Hermes 等内容构建成个人 AI 学习知识图谱。

### Schema 示例

```text
实体类型：
  Concept       概念
  Paper         论文
  Method        方法
  Project       项目
  Module        学习模块
  Author        作者
  Dataset       数据集

关系类型：
  Concept -[PART_OF]-> Module
  Paper -[PROPOSES]-> Method
  Method -[USED_IN]-> Project
  Concept -[RELATED_TO]-> Concept
  Paper -[CITES]-> Paper
  Module -[CONTAINS]-> Concept
  Method -[SOLVES]-> Problem
```

### 可以实现的问题

```text
Transformer 和 Attention 是什么关系？
RAG 和 GraphRAG 的区别是什么？
Agentic RAG 涉及哪些核心概念？
多模态检索依赖哪些底层技术？
哪些论文支撑了知识图谱嵌入？
给我生成一条从 RAG 到 GraphRAG 的学习路径。
```

### 项目价值

```text
个人学习可视化
论文脉络管理
知识问答
学习路径推荐
面试项目展示
GraphRAG 实战
```

## 一句话总结

> 如果只是入门，先做医疗知识图谱问答；如果想结合自己的长期学习，最推荐做“AI 学习知识图谱 + GraphRAG”。它既能覆盖实体抽取、图数据库、图查询、GraphRAG，又能沉淀成一个长期可迭代的个人专业项目。