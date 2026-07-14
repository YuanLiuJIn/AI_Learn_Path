# 04. CPU/GPU 异构协同、有状态算子分布式化与 SQL-First

> 目标：理解多模态数据处理引擎的三个工程核心：异构计算、有状态算子、SQL-First。

## 1. 为什么多模态处理需要 CPU/GPU 异构协同？

多模态任务通常不是纯 GPU，也不是纯 CPU。

以图片 Embedding 为例：

```text
CPU：读文件、解码 JPEG、Resize、Normalize
GPU：跑图像 Encoder，生成 Embedding
CPU：后处理、写结果、写索引
```

以视频处理为例：

```text
CPU：视频解码、抽帧、音频提取
GPU：OCR/ASR/Caption/Embedding 模型推理
CPU：片段组织、元数据写入
```

如果调度不好，会出现：

```text
CPU 忙时 GPU 空等
GPU 忙时 CPU 空等
数据在 CPU 节点和 GPU 节点之间跨机传输
GPU 利用率低，整体吞吐差
```

## 2. 具体做法一：流水线 Overlap

传统串行方式：

```text
Batch 1: CPU 预处理 → GPU 推理 → CPU 后处理
Batch 2: CPU 预处理 → GPU 推理 → CPU 后处理
Batch 3: CPU 预处理 → GPU 推理 → CPU 后处理
```

这会导致 CPU/GPU 轮流等待。

优化后做流水线重叠：

```text
时间轴 →

CPU 预处理: Batch1 | Batch2 | Batch3 | Batch4
GPU 推理:          Batch1 | Batch2 | Batch3
CPU 后处理:                Batch1 | Batch2 | Batch3
```

核心思想：

> CPU 处理下一批数据时，GPU 同时推理上一批数据。

需要的机制：

```text
异步队列
批处理 batch
GPU stream
预处理/推理/后处理分阶段执行
背压控制
```

## 3. 具体做法二：Co-locate 协同调度

没有协同时：

```text
CPU 节点 A：图片解码
      ↓ 跨机传输
GPU 节点 B：模型推理
      ↓ 跨机传输
CPU 节点 C：后处理
```

问题：

```text
网络传输开销大
数据本地性差
延迟高
资源利用不稳定
```

Co-locate 的做法：

```text
同一节点内：
CPU 解码 → GPU 推理 → CPU 后处理
```

也就是尽量把上下游相关算子调度到同一台具备 CPU/GPU 的节点上。

## 4. 具体做法三：Batch、队列与背压

系统内部通常有多个队列：

```text
读取队列 → 预处理队列 → GPU 推理队列 → 后处理队列 → 写出队列
```

关键参数：

```text
batch size
CPU worker 数
GPU worker 数
队列长度
最大并发请求数
超时时间
```

背压机制：

```text
如果 GPU 队列满了，CPU 预处理要放慢
如果写出队列堵塞，前面的阶段也要限速
```

否则会导致：

```text
内存爆炸
请求超时
GPU 饥饿
吞吐抖动
```

## 5. 什么是有状态算子？

无状态算子：处理每条数据时不依赖其他数据。

```text
图片 Resize
文本小写化
图片格式转换
语言检测
人脸模糊
```

有状态算子：处理一条数据时，需要知道全局或历史状态。

```text
文本去重
相似文档聚类
全局排序
实体合并
图连通分量
子串去重
```

典型例子：文本去重。

```text
doc1: 大模型训练方法介绍
doc2: 大模型训练方法介绍       完全重复
doc3: 大模型的训练方法介绍     模糊重复
doc4: RAG 检索增强生成         不重复
```

要判断 doc2/doc3 是否重复，必须知道 doc1 的存在。

## 6. 有状态算子为什么难分布式化？

假设数据被切到不同机器：

```text
机器 A：doc1, doc3
机器 B：doc2, doc4
```

doc1 和 doc2 重复，但它们在不同机器上。

如果每台机器只看本地数据，就会漏掉跨分片重复。

难点：

```text
状态跨分片
结果要全局一致
通信成本高
数据倾斜明显
算法不能简单 map 并行
```

## 7. 有状态算子分布式化的通用方法

### 7.1 分治

先把问题拆成局部任务和全局合并任务。

```text
局部计算 fingerprint/signature
  ↓
按 signature 重分区
  ↓
同一候选集合内做精确判断
  ↓
全局合并重复簇
```

### 7.2 重分区

让可能相关的数据去同一个分区。

```text
hash(signature) % N → partition_id
```

这样相似文档尽量聚在同一个 worker。

### 7.3 并查集 / 连通分量

模糊去重经常形成图：

```text
doc1 —— doc2
doc2 —— doc7
doc5 —— doc8
```

最终要得到重复簇：

```text
{doc1, doc2, doc7}
{doc5, doc8}
```

这类问题常用并查集或分布式连通分量算法。

### 7.4 布隆过滤器

对于大规模重复判断，可以用布隆过滤器快速判断“可能出现过”。

```text
如果 Bloom Filter 说不存在 → 一定不存在
如果 Bloom Filter 说存在 → 可能存在，需要进一步确认
```

## 8. SQL-First 是什么？

SQL-First 的目标：

> 让用户直接用 SQL 调用 AI 能力，而不是写复杂 Python 工程代码。

例如：

```sql
SELECT
  id,
  AI_SUMMARIZE(content) AS summary,
  AI_CLASSIFY(content, ARRAY['技术', '产品', '运营']) AS category
FROM documents;
```

或者：

```sql
SELECT
  id,
  EMBED_TEXT(content) AS embedding
FROM chunks;
```

## 9. SQL-First 怎么实现？

SQL 引擎执行流程：

```text
SQL
  ↓
Parser：语法解析
  ↓
Logical Plan：逻辑计划
  ↓
Optimizer：优化器
  ↓
Physical Plan：物理计划
  ↓
Executor：执行
```

当 SQL 中出现 AI 函数：

```sql
AI_CLASSIFY(content)
```

系统会把它变成一个 AI 算子：

```text
TableScan
  ↓
Filter
  ↓
AI_CLASSIFY(content)
  ↓
Project
  ↓
Output
```

AI 算子底层通常调用模型网关或推理服务：

```text
SQL Executor
  ↓ batch 化
模型网关 / 推理服务
  ↓
模型结果
  ↓
变成 SQL 输出列
```

## 10. SQL-First 的工程关键点

### 10.1 Batch 化

不能一行调一次模型。

```text
错误：row1 → model, row2 → model, row3 → model
正确：[row1, row2, ..., rowN] → batch → model
```

### 10.2 异步并发

模型调用慢，需要多个 batch 并发执行。

```text
batch1 → model
batch2 → model
batch3 → model
```

### 10.3 成本感知优化

例如：

```sql
SELECT AI_SUMMARIZE(content)
FROM docs
WHERE category = 'AI';
```

优化器应该先过滤，再调用 AI：

```text
TableScan → Filter(category='AI') → AI_SUMMARIZE
```

而不是对全表先做 AI。

### 10.4 权限、审计与限流

AI 函数可能调用外部模型或昂贵资源，需要：

```text
权限校验
数据脱敏
调用审计
token 计量
超时控制
失败重试
限流熔断
```

## 11. 一句话总结

> CPU/GPU 异构协同解决多模态处理的吞吐问题；有状态算子分布式化解决大规模全局计算问题；SQL-First 解决 AI 能力进入现有数据分析体系的使用门槛问题。三者共同决定多模态数据处理引擎能否真正工程化落地。