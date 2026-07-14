# 04. 图存储、图数据库与查询语言

> 目标：理解知识图谱如何存储和查询，包括 RDF Store、属性图数据库、SPARQL、Cypher。

## 1. 为什么需要图数据库？

知识图谱最常见的问题是关系和路径：

```text
A 和 B 之间有什么关系？
某个实体的两跳邻居有哪些？
哪些公司通过多层股权间接控制另一家公司？
某个疾病相关的症状、药品、检查项有哪些？
```

关系数据库也能做 join，但多跳关系会变成大量表连接：

```sql
SELECT ...
FROM relation r1
JOIN relation r2 ON r1.object = r2.subject
JOIN relation r3 ON r2.object = r3.subject
...
```

图数据库更擅长：

```text
邻居遍历
路径查询
多跳关系
图算法
关系模式匹配
```

## 2. 两类主流图存储

### 2.1 RDF Store / Triple Store

存储 RDF 三元组：

```text
(subject, predicate, object)
```

查询语言：SPARQL。

适合：

```text
语义网
开放知识库
本体推理
标准化数据交换
```

### 2.2 属性图数据库

存储节点、边、标签、属性。

```text
(:Person {name:'张三'})-[:WORKS_AT {since:2020}]->(:Company {name:'A公司'})
```

查询语言：Cypher、Gremlin、GQL。

适合：

```text
业务知识图谱
推荐
风控
路径分析
工程应用
```

## 3. RDF Store 如何存储？

最朴素的三元组表：

```text
subject | predicate | object
--------|-----------|--------
姚明    | 出生地     | 上海
姚明    | 效力球队   | 火箭队
火箭队  | 所属联盟   | NBA
```

为了加速查询，系统通常会建立多种排列索引：

```text
SPO
SOP
PSO
POS
OSP
OPS
```

这样无论查询条件给了 S/P/O 哪些字段，都能快速定位。

## 4. SPARQL 查询示例

查询“姚明效力过的球队”：

```sparql
SELECT ?team WHERE {
  :YaoMing :playedFor ?team .
}
```

查询“效力过 NBA 球队的人”：

```sparql
SELECT ?person ?team WHERE {
  ?person :playedFor ?team .
  ?team :belongsTo :NBA .
}
```

SPARQL 的核心是图模式匹配：

```text
用变量 ?x 写一个三元组模板，系统在图里找匹配结果。
```

## 5. 属性图如何存储？

属性图通常会存：

```text
节点表：node_id, labels, properties
边表：edge_id, src_id, dst_id, type, properties
邻接索引：node_id → outgoing/incoming edges
属性索引：label + property → node_id
```

关键是邻接访问：

```text
给定节点 A，快速找到 A 的所有出边和邻居。
```

这让路径查询比普通 join 更自然。

## 6. Cypher 查询示例

查询“姚明效力过的球队”：

```cypher
MATCH (:Person {name: '姚明'})-[:PLAYED_FOR]->(team:Team)
RETURN team.name
```

查询“两跳关系”：

```cypher
MATCH (p:Person {name: '姚明'})-[:PLAYED_FOR]->(team)-[:BELONGS_TO]->(league)
RETURN team.name, league.name
```

查询最短路径：

```cypher
MATCH p = shortestPath((a:Person {name:'A'})-[*..6]-(b:Person {name:'B'}))
RETURN p
```

## 7. 图查询的三类典型模式

### 7.1 邻居查询

```text
某实体的一跳/两跳邻居是什么？
```

例如：

```text
疾病 → 症状 / 药品 / 检查项 / 科室
```

### 7.2 路径查询

```text
A 和 B 之间通过什么路径相连？
```

例如：

```text
作者 A → 论文 P → 引用 → 论文 Q → 作者 B
```

### 7.3 子图模式匹配

```text
找满足某种结构模式的实体组合。
```

例如：

```text
公司 X 投资公司 Y，Y 的高管同时任职于公司 Z。
```

## 8. 图数据库的索引

常见索引：

```text
节点 ID 索引
标签索引
属性索引
全文索引
向量索引
邻接索引
关系类型索引
```

其中邻接索引是图数据库的核心能力之一。

## 9. 图查询优化

图查询也需要优化器。

例如：

```cypher
MATCH (p:Person)-[:WORKS_AT]->(c:Company {name:'A公司'})
RETURN p
```

可以先找公司节点，再沿入边找人。

如果反过来从所有 Person 开始遍历，会很慢。

优化器会考虑：

```text
起点选择
索引命中
边类型选择率
路径长度
中间结果大小
过滤条件顺序
```

## 10. 图数据库选型建议

| 场景 | 推荐方向 |
|---|---|
| 语义网、本体推理、标准交换 | RDF Store + SPARQL |
| 工程应用、路径分析、推荐、风控 | 属性图数据库 + Cypher/Gremlin |
| 超大规模分布式图 | 分布式图数据库 / 图计算框架 |
| 图算法分析 | 图计算框架或图数据库内置算法 |
| GraphRAG 原型 | 属性图数据库 + 向量检索 + LLM |

## 11. 一句话总结

> 图数据库的核心价值是高效存储和查询实体关系网络。RDF Store 适合标准语义和本体推理，属性图数据库适合工程开发和路径分析。SPARQL 更偏三元组模式匹配，Cypher 更贴近节点—边路径表达。