# 方向三：论文 Battle 对比

> 面向有一定基础、想深入理解方法论差异的观众。

## 节目形式

```text
PPT + 对比动画 + 实验数据可视化
每期 15-25 分钟
```

## 风格要求

```text
每期设定一个具体场景："你遇到了这个问题，有两个解法"
不是"哪个更好"，而是"什么时候用哪个"
最后给出你的选择 + 理由
```

## Battle 清单

### Battle 1：RLHF vs DPO —— 哪种对齐方法更好？

```text
场景：你要训练一个助手模型，让它安全有用

Round 1：方法对比
  RLHF：训练 Reward Model → PPO 优化
  DPO：直接用偏好数据优化，不需要 Reward Model

Round 2：核心差异
  RLHF：需要维护一个独立的 Reward Model，训练复杂但灵活
  DPO：实现简单，但数据分布变了可能失效

Round 3：实验对比
  效果：DPO 在多数任务上接近甚至超过 RLHF
  稳定性：DPO 更稳定
  实现复杂度：DPO 远低于 RLHF

Round 4：选型建议
  如果你有现成的 Reward Model 或需要在线反馈 → RLHF
  如果你只有偏好数据集 → DPO
  90% 的场景 DPO 够用
```

### Battle 2：HNSW vs IVF-PQ —— 什么场景选什么向量索引？

```text
场景：你有 1 亿条向量需要检索，怎么建索引？

Round 1：方法对比
  HNSW：图索引，多层小世界图
  IVF-PQ：聚类倒排 + 乘积量化

Round 2：核心差异
  HNSW：召回高、延迟低、内存占用高
  IVF-PQ：内存占用低、适合超大规模

Round 3：实验对比
  百万级：HNSW 更好
  亿级：IVF-PQ 更省内存
  十亿级：DiskANN 或 IVF-PQ

Round 4：选型建议
  内存充足 + 千万级以下 → HNSW
  内存紧张 + 亿级以上 → IVF-PQ
  十亿级以上 → DiskANN
```

### Battle 3：CLIP vs BLIP-2 —— 多模态表示的两种路线

```text
场景：你要做一个文本搜图片的系统

Round 1：方法对比
  CLIP：对比学习，图文双塔
  BLIP-2：冻结图像编码器 + Q-Former + LLM

Round 2：核心差异
  CLIP：擅长检索和 zero-shot 分类
  BLIP-2：擅长理解和生成

Round 3：实验对比
  检索速度：CLIP 更快（双塔可预计算）
  理解能力：BLIP-2 更强
  多任务：BLIP-2 更灵活

Round 4：选型建议
  纯检索 → CLIP
  需要理解 + 生成 → BLIP-2
  混合场景 → CLIP 召回 + 多模态模型理解
```

### Battle 4：GraphRAG vs 文本 RAG —— 什么时候需要图？

```text
场景：你有 100 篇技术文档，要做问答系统

Round 1：方法对比
  文本 RAG：chunk → 向量检索 → 生成
  GraphRAG：实体关系抽取 → 建图 → 社区摘要 → 生成

Round 2：核心差异
  文本 RAG：适合局部事实问答
  GraphRAG：适合全局总结和多跳关系

Round 3：实验对比
  事实问答：文本 RAG 不差
  全局总结：GraphRAG 明显更好
  成本：GraphRAG 更高

Round 4：选型建议
  简单事实问答 → 文本 RAG
  需要全局理解 → GraphRAG
  预算有限 → 文本 RAG 起步，按需加 GraphRAG
```

### Battle 5：LoRA vs Full Fine-tuning —— 什么场景需要全量微调？

```text
场景：你要在 1000 条数据上微调一个 7B 模型

Round 1：方法对比
  LoRA：冻结原有权重，只训练两个小矩阵
  Full Fine-tuning：更新所有参数

Round 2：核心差异
  LoRA：显存友好，训练快，但能力上限受限
  Full Fine-tuning：能力上限高，但显存和计算成本高

Round 3：实验对比
  小数据集（< 1 万）：LoRA 和全量微调差距不大
  大数据集（> 10 万）：全量微调可能更好
  新领域：LoRA 可能需要更高 rank

Round 4：选型建议
  个人/小团队 → LoRA
  有充足算力 + 需要极致效果 → 全量微调
  90% 场景 LoRA 够用
```

### Battle 6：TransE vs RotatE —— 知识图谱嵌入的进化

```text
场景：你要做知识图谱链接预测

Round 1：方法对比
  TransE：head + relation ≈ tail（平移）
  RotatE：head ⊙ relation ≈ tail（复数旋转）

Round 2：核心差异
  TransE：简单，但不擅长对称/反对称/组合关系
  RotatE：能表达更多关系模式

Round 3：实验对比
  一对一关系：两者差不多
  对称关系：RotatE 更好
  组合关系：RotatE 明显更好

Round 4：选型建议
  简单图谱 + 快速实验 → TransE
  复杂关系 → RotatE
```

### Battle 7：BM25 vs Dense Retrieval —— 关键词 vs 语义

```text
场景：你要做一个 RAG 系统的检索模块

Round 1：方法对比
  BM25：基于词频和逆文档频率
  Dense：基于 Embedding 向量相似度

Round 2：核心差异
  BM25：精确匹配强，语义理解弱
  Dense：语义理解强，精确匹配弱

Round 3：实验对比
  错误码/专有名词：BM25 更好
  近义表达/跨语言：Dense 更好
  混合检索（BM25 + Dense）：通常最好

Round 4：选型建议
  永远不要只用一个，工业系统必须混合
  BM25 负责精确匹配，Dense 负责语义召回
```

### Battle 8：Self-RAG vs CRAG —— 检索质量自检的两种思路

```text
场景：你的 RAG 系统检索结果有时不相关

Round 1：方法对比
  Self-RAG：生成时判断是否需要检索、结果是否足够
  CRAG：检索后评估质量，不好就修正

Round 2：核心差异
  Self-RAG：模型自己决定"要不要搜""搜得够不够"
  CRAG：独立的评估器判断"搜得好不好"

Round 3：实验对比
  灵活性：Self-RAG 更灵活
  实现复杂度：CRAG 更简单
  效果：各有优劣

Round 4：选型建议
  想最小改动 → CRAG（插拔式）
  想彻底优化 → Self-RAG
```

## 每期通用结构

```text
0-2 分钟：场景设定 —— "你遇到了这个问题，有两个解法"
2-5 分钟：方法 A 的核心 trick（一张图讲清楚）
5-8 分钟：方法 B 的核心 trick（一张图讲清楚）
8-14 分钟：实验对比（并排展示关键指标，解释"为什么会有这个差异"）
14-18 分钟：各自的优势和软肋
18-22 分钟：选型建议（什么场景用哪个，给出你的选择）
22-25 分钟：总结卡片
```

## 视觉素材清单

```text
每期准备：
  1 张场景设定图（"你遇到了这个问题"）
  1 张方法 A 的核心 trick 图
  1 张方法 B 的核心 trick 图
  1 组并排实验对比图
  1 张选型决策树
  1 张总结卡片
```
