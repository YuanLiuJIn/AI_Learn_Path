# 多模态模型（MLLM / VLM）评测：标准、评测集、方法与论文项目

> 整理时间：2026-07。覆盖图像理解、文档/OCR、视频理解、多模态推理、幻觉与安全。

---

## 一、评测标准（能力维度）

| 维度 | 说明 | 代表评测集 |
|---|---|---|
| 感知（Perception） | 物体存在/计数/颜色/位置/OCR | MME、MMBench、SEED-Bench、BLINK |
| 认知与推理（Cognition） | 图文联合推理、常识、代码/数学 | MMMU、MathVista、MMMU-Pro |
| 学科知识 | 大学级多学科 | MMMU、CMMMU（中文） |
| 文档 / OCR / 图表 | 富文本图像理解 | OCRBench、DocVQA、ChartQA、InfographicVQA |
| 视频理解 | 时序、长视频、事件 | Video-MME、MVBench、LongVideoBench、EgoSchema |
| 定位 / Grounding | 指代表达、框回归 | RefCOCO、Visual Genome |
| 幻觉 | 物体幻觉、语言先验压制视觉 | POPE、HallusionBench、MMHal-Bench |
| 综合能力（开放式） | 复合能力、开放生成 | MM-Vet、MMBench、LLaVA-Bench |
| 真视觉依赖性 | 剔除「不看图也能答」的题 | MMStar |
| 多模态 Agent / GUI | 屏幕理解与操作 | ScreenSpot、OSWorld、WebArena-Visual |

**核心方法论问题**：很多 MLLM benchmark 存在「**视觉冗余**」——纯文本 LLM 也能答对。MMStar 系统性揭示了这一点，是评测岗必须理解的坑。

---

## 二、热门评测集与论文

### 综合理解
| 评测集 | 论文 | 要点 |
|---|---|---|
| **MMMU** | arXiv:2311.16502 | 大学级 6 大学科 30 领域，1.15 万题，含图表/乐谱/化学式；事实标准 |
| **MMMU-Pro** | arXiv:2409.02813 | 加强版：10 选项 + 纯截图输入（vision-only），大幅去除文本捷径 |
| **MME** | arXiv:2306.13394 | 14 个感知/认知子任务，Yes/No 判定，简单稳定 |
| **MMBench** | arXiv:2307.06281 | 层次化能力分类 + **CircularEval**（循环打乱选项，抗随机猜） |
| **SEED-Bench** | arXiv:2307.16125 | 19K 单选题，覆盖图像与视频 12 维度 |
| **MM-Vet** | arXiv:2308.02490 | 6 种核心能力的组合，开放式回答 + LLM 打分 |
| **MMStar** | arXiv:2403.20330 | 精选 1500 道**真正依赖视觉**的题，并提出污染度指标 |
| **BLINK** | arXiv:2404.12390 | 人类"一眼"能答但模型很差的核心视觉感知任务 |

### 推理 / 数学 / 文档
- **MathVista** arXiv:2310.02255 — 视觉数学推理，最常被引用
- **MathVerse** arXiv:2403.14624 — 拆解图/文信息量，判断模型是否真看图
- **OCRBench** arXiv:2305.07895（LVLM OCR 能力）
- **DocVQA / ChartQA / AI2D / InfographicVQA** — 文档与图表理解经典组合

### 视频
- **Video-MME** arXiv:2405.21075（CVPR 2025）— 首个全谱系视频 MLLM 评测，短/中/长视频 + 字幕/音频消融
- **MVBench** arXiv:2311.17005 — 20 个时序理解任务
- **LongVideoBench** / **EgoSchema** arXiv:2308.09126 — 长视频与长时序推理
- **Video-MMMU**（ACL 2026）— 从视频中"获取知识"的学习增益（performance gain）指标，评测范式创新

### 幻觉与可信
- **POPE** arXiv:2305.10355 — 轮询式提问检测物体幻觉，指标 Accuracy/F1/Yes-ratio；**必读**
- **HallusionBench** arXiv:2310.14566（CVPR'24）— 区分「语言幻觉」与「视觉错觉」
- **MMHal-Bench** — 开放式回答的幻觉打分
- **CHAIR** — 早期 image captioning 幻觉指标

### 中文 / 本土
- **CMMMU**、**MMBench-CN**、**CCBench**、**MME-RealWorld**

---

## 三、评测方法与指标

### 3.1 打分方式
- **选择题**：Accuracy；MMBench 的 **CircularEval**（选项循环移位 N 次，全对才算对）显著降低瞎猜收益
- **Yes/No 判定**（MME、POPE）：Accuracy + F1 + **Yes-ratio**（检测模型的"讨好性"偏置）
- **开放式回答**（MM-Vet、MMHal）：GPT-4/GPT-4V as judge，给出 0-1 连续分
- **Grounding**：IoU@0.5、Acc@IoU
- **生成式 caption**：CIDEr、SPICE、CLIPScore（老指标，已逐渐被 judge 替代）

### 3.2 关键陷阱（评测岗核心竞争力）
1. **视觉冗余**：需做「纯文本消融」——去掉图片后模型准确率，若接近原分数说明题目无效
2. **选项偏置**：模型偏好某个位置/字母，用 CircularEval 或选项打乱验证
3. **Prompt 敏感性**：不同模板分数差几个点，必须统一模板并公开
4. **答案抽取**：多模态模型输出格式散乱，抽取器质量直接影响分数，需报告抽取失败率
5. **数据污染**：MMStar 提出用「LLM-only 分数」与「多模态增益」间接衡量污染

---

## 四、开源框架与项目

| 项目 | 说明 |
|---|---|
| **VLMEvalKit**（open-compass/VLMEvalKit）| **首选**。70+ 多模态 benchmark 一键评测，支持主流开源/API 模型，配套 HF 榜单 |
| **OpenCompass** | 与 VLMEvalKit 同源，统一调度 |
| **lmms-eval**（EvalAI/LMMs-Lab）| 另一主流多模态评测框架，与 harness 风格一致 |
| **MMMU 官方 repo** | 数据与评测脚本 |
| **Video-MME / MVBench 官方 repo** | 视频评测参考实现 |
| **POPE / HallusionBench repo** | 幻觉评测脚本 |
| **OpenVLM Leaderboard**（HuggingFace）| 权威多模态排行榜 |

---

## 五、精读论文清单

1. **MMMU**（2311.16502）→ **MMMU-Pro**（2409.02813）
2. **MMStar: Are We on the Right Way for Evaluating LMMs?**（2403.20330）— 评测方法论批判，**最推荐**
3. **MMBench**（2307.06281）— CircularEval 设计思想
4. **POPE**（2305.10355）与 **HallusionBench**（2310.14566）
5. **MathVista**（2310.02255）/ **MathVerse**（2403.14624）
6. **Video-MME**（2405.21075）
7. **MME**（2306.13394）、**MM-Vet**（2308.02490）
8. **BLINK**（2404.12390）

---

## 六、动手任务建议

1. 用 VLMEvalKit 评测 Qwen2.5-VL / InternVL 在 MMBench + MMMU + POPE 上的表现，复现官方分数；
2. 做「纯文本消融实验」：对某个 benchmark 去图后评测，量化视觉冗余比例；
3. 实现 CircularEval，对比普通 Accuracy 的差距；
4. 自建一个中文垂类多模态评测集（如票据/图表 100 题），含标注规范并接入 VLMEvalKit。
