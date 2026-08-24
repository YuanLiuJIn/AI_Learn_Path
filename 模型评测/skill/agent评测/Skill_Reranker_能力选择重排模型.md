# Tool & Skill 越来越多，Agent 怎么选才不出错？专用 Skill Reranker

> 来源文章：《Tool & Skill越来越多，Agent怎么选才不出错？Venus-Skill-Reranker来帮忙》（作者 victorweng）
> 核心成果：训练专用轻量重排模型 Venus-Skill-Reranker-v1（0.6B），同时具备 Tool Selection 与 Skill Routing 能力；6 个公开/自建基准上同规模全 SOTA，多数媲美 8B 通用重排模型。
> 注：文中 tRAG 平台、ai.woa.com 等内部调用入口已略去，保留方法论与实验结论。

---

## 一、背景：为什么需要面向 Agent 的能力选择 Reranker

### 1.1 LLM 直接做工具选择，三重困境
早期做法：把全部工具定义注入 Prompt 让 LLM 自选。能力扩张后问题凸显：
- **Token 爆炸**：工具越多，定义部分 token 爆炸式增长。
- **准确率断崖**：工具越多选得越不准（LLM 固有通病）。Anthropic 内部测试：可用工具超 30-50 个后正确率显著下降，Claude-Opus-4.5 在填充 50+ MCP 工具后选择准确率仅 79.5%。
- **成本高、不确定**：推理延迟与 token 成本不可接受；同输入因推理设置/上下文波动给出不同排序，对确定性生产系统不可忽略。

→ 结论：LLM 直接全量选择不合理，前置需要高效能力选择机制。

### 1.2 业界解法：延迟加载 + Tool Search Tool（及局限）
Claude Advanced Tool Use：
- **延迟声明**：`defer_loading: true` 标记大部分工具不默认加载，启动时只留 ~500 token 的 Tool Search Tool + 常驻核心工具。
- **按需搜索加载**：Agent 判断需要时调用 Tool Search Tool，返回 3-5 个工具引用注入上下文再最终选择。

Tool Search Tool 三种范式：
| 模式 | 原理 | 本质 |
|---|---|---|
| Regex | 正则匹配名称/描述 | 字符串模式 |
| BM25 | 词频-逆文档频率 | 关键词统计 |
| 自定义语义 | Embedding / Reranker / LLM | 通用语义相似度 |

Regex/BM25 是传统检索算法，能判字面相关但**无法理解「功能适配性」**。

整条链路三段各司其职：
| 环节 | 核心任务 | 输入规模 | 速度 | 精度 | 成本 |
|---|---|---|---|---|---|
| ① Embedding 召回 | 海量池找可能相关 | 数万~数十万 | 极快 | 召回为主 | 极低 |
| ② Reranker 精排（本工作） | 从召回候选排出正确顺序 | Top-K（≈20-50） | 快 | 精细排序 | 低 |
| ③ LLM 确认 | 基于精排结果裁决 | Top-3~5 | 慢 | 最强但可能波动 | 高 |

**Reranker 是核心连接环节**：这步做好，后续 LLM 确认的成本与错误率都显著下降。

### 1.3 Tool Selection 与 Skill Routing：同形式不同粒度
| 维度 | Tool Selection | Skill Routing |
|---|---|---|
| 候选对象 | 原子化工具函数 | 复合技能/能力模块 |
| 注册信息 | name+description+完整参数 schema | 通常仅 name+description |
| 粒度 | 细（单次 API 级） | 粗（封装多步逻辑） |
| 信息密度 | 较高（schema 提供结构信号） | 较低（仅靠描述文本） |
| 主要难点 | 功能近义工具细粒度区分 | 抽象意图与技能描述语义对齐 |

关键点：**两者 reranking 形式化定义完全一致**（query + 候选 → 排序）。

---

## 二、如何训练面向 Agent 能力选择的 Reranker

### 2.1 三大挑战
1. **候选信息异构**：Tool 有完整 schema，Skill 常只有 name+description，不同系统还可能带用例/约束/标签。模型需在不同丰富度输入都稳定。
2. **对精确指令敏感**：Reranker 输入不总是用户原始 query，更多是 Agent 将意图拆解后的步骤级精确指令。需同时处理「模糊原始 query」与「精确指令」两类输入。
3. **多语言泛化**：Skill 市场全球开发者创建，中/英/日混杂是常态。

### 2.2 数据策略：巧用 Tool 数据解 Skill 数据难题
Skill 数据构建训练三元组的问题：
- 开源大规模 Skill Routing 标注集缺失；
- 描述模糊宽泛、能力边界不清、易过度夸大；
- Ground Truth 歧义严重（一个 query 多个 Skill 都能做，标注不唯一）。

Tool 数据优势：
| 维度 | Tool 数据 | Skill 数据 |
|---|---|---|
| 注册信息完整度 | name+description+完整 schema | 仅 name+description |
| 功能边界 | 高（schema 天然约束） | 低（重叠严重） |
| Ground Truth | 强（一次调用对应一个工具） | 弱（多 Skill 都能完成同意图） |
| 开源参考集 | 有（ToolRet/ToolBench 等） | 无 |

→ 策略：**主要用高质量 Tool 数据训练**（~20 万条），利用 Tool/Skill reranking 同质性泛化到 Skill 场景。

### 2.3 训练数据构建（差异化核心：多模板 + 指令）
- **多模板工具文档**：同一条 (query, candidates, labels) 用多种信息丰富度模板生成样本（极简 name+一行描述 → 完整含参数定义与元信息）。好处：鲁棒性↑、隐式覆盖 Skill 稀疏描述场景、对抗过拟合（逼模型学深层语义而非表层）。
- **指令构造**：每条原始 query 配一条精确 instruction（Agent 翻译后的步骤级指令），样本从 (query, candidates) → ranking 变为 (query, instruction, candidates) → ranking。直接应对挑战二。

### 2.4 训练方法
- **基座选择 Qwen3-0.6B**：参数量小推理快、具备指令遵循能力、中+多语言扎实（对比 jina-reranker-v3-0.6B listwise 慢、bge-reranker-v2-m3-0.5B 无指令能力）。
- **微调方式 Instruction Tuning**（而非常规 SFT）：
  - SFT：(query, candidates)→ranking，决策依赖表层文本匹配，query 模糊时所有「沾边」候选都得高分，无法区分字面相关与功能匹配。
  - Instruction Tuning：(instruction, query, candidates)→ranking，通过 instruction 获得明确任务意图约束（动作类型、参数需求），从功能层面精准定位匹配候选。
- **训练设置**：SWIFT 框架；Listwise Ranking 范式 + listwise + label smoothing pointwise 损失；LoRA 微调优于全量；验证集损失早停。
- **后处理**：不同 checkpoint 做 Slerp Merging 得最终模型。

---

## 三、实验表现

### 3.1 评估基准
- 工具检索：ToolBench（清华/OpenBMB，1100）、BFCL（UC Berkeley Gorilla，1053）、Tool-BeHonest（样本级指令，350）。
- 技能检索：SRA-Bench（5400 query/~26K 池）、SkillRouter-Bench（阿里达摩院，75 query/~80K 池，数据集级指令）、Vedas Skills 市场评测集（108 query/~500 池）。
- Skill 基准因大池无法全量入 Reranker，先 qwen3-embedding-0.6b 召回 Top-20 再公平比较。
- 指标：MRR@k、nDCG@k、Recall@k（越接近 1 越好）。
- 基线：Qwen3-8B/4B/0.6B、bge-reranker-v2-minicpm/2-m3、SkillRouter-Reranker-0.6B、Venus-Reranker-v1。

### 3.2 结果摘要
- **综合**：6 个集 4 第一、2 第二；同规模（Venus-Reranker-v1/Qwen3-0.6B/SkillRouter-Reranker/bge-m3）全 SOTA；多数基准媲美甚至超过 Qwen3-8B。
- **带指令场景优势最显著**：Tool-BeHonest nDCG@5 比 Qwen3-8B 高 5.47%，SkillRouter-Bench nDCG@10 高 2.26%——验证 Instruction Tuning 有效。
- **跨场景泛化**：主要用 Tool 数据训练，却在 3 个 Skill 基准分获第 1/并列第 1/第 2。与专用 SkillRouter-Reranker 对比 NDCG@k：SRA-Bench +6.97%、SkillRouter-Bench +3.68%、Vedas +1.02%。

### 3.3 示例结论
在 SRA-Bench 某编码任务上，Qwen3-Reranker-0.6B 把「与 Ground Truth 描述接近的无效工具」排到前面，Venus-Skill-Reranker-v1 正确排到 Ground Truth——体现其理解 query 本质需求并路由合适 Skill 的能力。

---

## 四、总结与展望
- 训练数据重心在 Tool，Skill 侧潜力未释放——下一步补高质量 Skill 训练数据做 Tool+Skill 混合训练。
- Skill 评测基准质量参差、常需人工介入，构建合适基准是值得方向。
- 受困于 Skill Description 质量，如何为 Skill 构建适合 Routing 的文本描述是开放问题（本文初步验证 Name+Description+LLM-Enriched Skill Summary 潜力大）。

---

## 五、对 Agent 工程的可迁移要点
1. 海量 Tool/Skill 下，**召回→专用 Reranker 精排→LLM 确认**三段式是工程标配，Reranker 是降低端到端成本与错误率的关键桥。
2. 重排模型应**专为 Agent 场景训练**而非用通用 Reranker——通用模型依赖字面、近义工具易误判。
3. **Instruction Tuning + 多模板**是提升「功能适配性」与「指令遵循」的两大杠杆。
4. **用高质量 Tool 数据训练再泛化到 Skill** 是绕过 Skill 数据标注难题的实用策略。
