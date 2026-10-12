# ai4s 的地质归纳 · PPT 参考文件（补充版）

> **基准**：`ppt参考文档原版.md`（结构与本文件一致）
> **用途**：直接交付 PPT 制作 skill，生成「学术会议报告」用演示文稿
> **补充来源**
> 1. 本地文献底账 `docs/文献清单_地质+AI.md`（R1–R9 综述 / N1–N9 近期研究，含 DOI）
> 2. 本地方法底账 `docs/感知型基础模型_方向项目速查.md`（6 模块 / 7 方向 / 卷度热力图）
> 3. 原版成品 deck `汇报PPT/index.html`（28 页，已登记版式与文案可作行文口径）
> 4. 互联网检索 OpenAlex / Crossref / 公开检索页，检索日 2026-09-24
>
> **统计口径（全文统一，不得改写）**：Crossref 期刊图谱，窗口 2025-09-21 → 2026-09-21；83 种地质与地球科学期刊，池内 60,568 篇，严格判读 AI 相关 7,166 篇（11.8%），地质主体子集 2,099 篇。

---

## 〇 · 交付指令（给 PPT skill 的硬约束，先读）

### 0.1 风格与主题

| 项 | 值 |
|---|---|
| 风格 | **B · 瑞士国际主义**（栅格、左对齐、超大字 weight 200、细规则线） |
| 主题色 | **IKB 克莱因蓝**（`references/themes-swiss.md` 主题 1） |
| 版式 | 正文页必须从 `references/layouts-swiss.md` 的 **S01–S22** 选一个并写入 `data-layout`，不要自创 |
| 字体 | Inter / Helvetica Neue / Noto Sans SC 回退；正文 15–17px |
| 页数 | **19 页**（封面 1 + 目录 1 + 4 章节分隔 + 正文 11 + 收尾 1） |
| 硬禁 | 渐变、投影、圆角、多强调色、emoji、居中标题（分隔页除外） |

### 0.2 原版 deck 已登记的版式分配（选型可直接沿用）

| 原版页码 | 页面性质 | `data-layout` |
|---|---|---|
| P01 封面 | 封面 | `S01` |
| P02 定位主张 | 大字单句 | `S03` |
| P03 目录四栏 | 多栏并列 | `S19` |
| P05/P08/P12/P17/P22/P27 分隔与主张 | 章节分隔 / 大字 | `S03` |
| P04 口径四数 | 四数并排 | `S02` |
| P05 范式八条 | 条形占比组 | `S07` |
| P06 前提对照 | 双列对照 | `S05` |
| P09 三条改法 | 编号条目组 | `S21` |
| P10 预训练目标六格 | 卡格 / 密度图 | `S11` |
| P13 方向地图 | 排名条形 | `S13` |
| P14 通用模型三类 | 三栏并列 | `S11` |
| P15 判据四条 | 大字编号 | `S19` |
| P16 期刊出口三区 | 三栏并排 | `S15` |
| P17 分区×方向矩阵 | 矩阵表 | `S16` |
| P20 范式三跳 / P21 三层路线 | 三列递进 | `S17` / `S18` |

> `S02`、`S04`、`S08`、`S10`、`S12` 的具体形态以 `references/layouts-swiss.md` 为准；本文件只给「该页需要几栏/几格」的语义需求。

### 0.3 图片

原版 deck **未使用任何位图**（`images/` 为空），全部靠排版与数据可视化表达。本版保持一致：所有图表用 CSS 条形、矩阵、数字块实现，不引入配图。

### 0.4 页码与主题节奏

| 页 | 内容 | 主题 | 版式需求 |
|---|---|---|---|
| 01 | 封面 | dark | S01 · 封面 |
| 02 | 目录 Part1–4 | light | S19 · 四栏 |
| 03 | Part1 分隔 | dark | S03 · 大字 |
| 04 | Part1-1 地质 AI4S 的定义 | light | S05 · 双列对照 |
| 05 | Part1-2 五方向综述界定表 | light | S21 · 大表 |
| 06 | Part2 分隔 | dark | S03 · 大字 |
| 07 | Part2-1 数据环节对照表 | light | S21 · 大表 |
| 08 | Part2-2 训练环节对照表 | light | S21 · 大表 |
| 09 | Part2-3 评测环节对照表 | light | S21 · 大表 |
| 10 | Part3 分隔 | dark | S03 · 大字 |
| 11 | Part3-1 方向一 水文地质 | light | S20 · 左右分栏 |
| 12 | Part3-2 方向二 遥感填图 | light | S20 · 左右分栏 |
| 13 | Part3-3 方向三 地震学 | light | S20 · 左右分栏 |
| 14 | Part3-4 方向四 矿产勘查 | light | S20 · 左右分栏 |
| 15 | Part3-5 方向五 GEOAGI | light | S20 · 左右分栏 |
| 16 | Part4 分隔 | dark | S03 · 大字 |
| 17 | Part4-1 世界模型 | light | S17 · 三列递进 |
| 18 | Part4-2 Jev 判断模型 | light | S17 · 三列递进 |
| 19 | 收尾 MANIFESTO | dark | S01 变体 · 大字收束 |

---

## Part 1 · 综述：何为地质 + AI

### page1 · 我理解的地质 AI4S，以及学术界的界定

**标题**：地质 AI4S，是方法学而不是工具箱
**副标**：AI for Science · 不是 AI application

**1. 我的定义（第一人称，保留原话）**

> 我理解的地质 AI4S，是在地质问题的**数据处理、分析、多模态监视与检测**等环节中使用人工智能技术——但它成立的判据不是「用上了 AI」，而是**是否在地质约束下给出了可外推、可证伪、可决策的结论**。

**2. 与学术界界定逐条对照（表格）**

| 维度 | 学术界综述的界定 | 我的理解 |
|---|---|---|
| 范围 | 覆盖地球科学全领域，沿「数据—模型—算力—可信度」四条主线展开（R1） | 收敛到地质主体任务，剔除纯方法 / 纯计算机输出 |
| 目标 | 用 AI 解决**科学问题**中的反问题与预测问题，而非做工程替代 | 同。判据落在「科学结论」而非「系统上线」 |
| 核心矛盾 | 物理约束与可解释性、多模态融合、知识图谱化（R1、R5） | 稀疏观测下的反问题：观测有偏、标签昂贵、空间不自洽 |
| 成熟度 | 数据与算力已就位，**可信度**（不确定性、可解释）是真正瓶颈（R1） | 一致。UQ + XAI 已占 17.1%，是刚需而非加分项 |

**支撑文献（本次新增）**

- **R1** · Zhao Tianjie 等（51 位作者）, *Artificial intelligence for geoscience: Progress, challenges, and perspectives*, **The Innovation** 5(5): 100691, 2024. DOI `10.1016/j.xinn.2024.100691`
- **R5** · Hadid A., Chakraborty T., Busby D., *When geoscience meets generative AI and large language models*, **Expert Systems** 41(8): e13654, 2024. DOI `10.1111/exsy.13654`

**讲稿提示**：主动交代一件事——「地质 + AI」不是一门学科，是**两组方法学的交集**。把 AI 当工具箱，是汇报里最先要排除的误读。

---

### page2 · 各方向综述对自身领域的界定（表格）

**标题**：五个方向组，各自在解决什么问题
**副标**：列表格 · 方向 / 代表综述 / 领域问题定义 / 公认瓶颈

| 方向组 | 代表综述（含 DOI） | 综述对该领域问题的定义 | 综述自陈的瓶颈 |
|---|---|---|---|
| **① 水文地质 / 地下水 / 环境地球化学** | *Groundwater Level Modeling with Machine Learning: A Systematic Review and Meta-Analysis*, **Water** 14(6): 949, 2022 · `10.3390/w14060949`<br>*A Comprehensive Review of Conventional, ML and DL Models for Groundwater Level Forecasting*, **Applied Sciences** 13(4): 2743, 2023 · `10.3390/app13042743` | 地下水位与污染物运移的**时空外推**：从点观测插值到区域场，从历史序列推到未来 | 站点稀疏且分布不均；抽水—补给等人类活动是外生变量，模型难以分离；跨含水层迁移弱 |
| **② 遥感解译 / 岩性识别 / 智能填图** | R9 · Zhou G., Qian L., Gamba P., *Advances on Multimodal Remote Sensing Foundation Models for Earth Observation Downstream Tasks: A Survey*, **Remote Sensing** 17(21): 3532, 2025 · `10.3390/rs17213532` | 从像素到语义：地表覆盖、岩性单元、蚀变信息的**自动成因化表达** | 高质量标注稀缺；跨任务泛化弱；**缺统一评测**；标签与验证同源（用图件验证图件） |
| **③ 地震监测 / 震源参数 / 地震学** | R4 · Kubo H., Naoi M., Kano M., *Recent advances in earthquake seismology using machine learning*, **Earth, Planets and Space** 76: 36, 2024 · `10.1186/s40623-024-01982-0`<br>R2 · An Yu 等, *Deep learning based automatic seismic fault interpretation: A systematic review*, **Earth-Science Reviews** 243: 104509, 2023 · `10.1016/j.earscirev.2023.104509` | 四件事：地震目录构建、地震活动性分析、地震动预测、地壳形变分析 | 不平衡地震动数据影响训练；**「预报」被高估**——b 值只含有限信号，告警对阈值敏感 |
| **④ 矿产勘查 / 成矿预测** | R3 · Sun Kang 等, *A Review of Mineral Prospectivity Mapping Using Deep Learning*, **Minerals** 14(10): 1021, 2024 · `10.3390/min14101021`<br>R6 · Zuo R., Carranza E.J.M., *Machine Learning-Based Mapping for Mineral Exploration*, **Mathematical Geosciences** 55: 891–898, 2023 · `10.1007/s11004-023-10097-3` | 把多源勘查图层（地质、物探、化探、遥感）映射为**矿化概率图** | 数据预处理、数据增强、超参调优、精度评价四大环节均未标准化；**已知矿床极少且空间聚簇**，「未知」≠「负样本」 |
| **⑤ GEOAGI 地质通用模型**<br>A 语言知识型 / B 感知表征型 | R1 · `10.1016/j.xinn.2024.100691`<br>R9 · `10.3390/rs17213532`<br>N8 · Zhu Xiaoxia 等, *On the foundations of Earth foundation models*, **Communications Earth & Environment** 7, 2026 · `10.1038/s43247-025-03127.x` | A：把地学文献与图件知识压进语言模型，做检索、问答、抽取与编排<br>B：大规模自监督预训练得到统一表征，冻结后迁移下游 | A **不产生地质预测**，本质是懂地质的检索写作工具；B 是**目前唯一被实验证据支持的「通用」**，但**通用边界止于地表观测** |

**本地文献覆盖度自查（本次补充的核心判断）**

| 方向组 | 本地综述 | 本地近期研究 | 覆盖判断 |
|---|---|---|---|
| ① 水文地质 / 环境地球化学 | — | — | ⚠️ **本次新增 4 篇**，见 Part3 page1 |
| ② 遥感填图 | R9 | N5 | ✅ 充分 |
| ③ 地震学 | R2、R4、R7 | N1、N2、N3、N9 | ✅ 充分 |
| ④ 矿产勘查 | R3、R6 | N6、N7 | ✅ 充分 |
| ⑤ GEOAGI | R1、R5、R9 | N8 | ✅ 充分 |

**讲稿提示**：这张表本身就是一个结论——**五个方向组的综述都齐，说明这不是「新领域」，而是「已有共识的领域」**。被问「这方向有人做过吗」，直接翻这页。

---

## Part 2 · 差异：地质 AI4S 和传统人工智能的区别

### page1 · 数据选择与清洗环节的不同

**标题**：同一条流水线，两套完全不同的前提
**副标**：列表格 · 环节 / 人工智能的做法 / 地质 AI4S 的做法

| 环节 | 传统人工智能的做法 | 地质 AI4S 的做法 |
|---|---|---|
| **1. 数据来源** | 众包 + 网络爬取，规模优先，「数据越多越好」 | 单井 / 单次采集成本**百万级**；采样点位由道路、矿区、经费决定，**不由地质问题决定**。先要问清数据「是怎么被选出来的」 |
| **2. 标签性质** | 客观、可复核、可众包（ImageNet 式） | **解释性标签**：剖面断层画法、矿床类型都依赖专家判断，本身可被质疑；同一图件不同专家可给出不同标注 |
| **3. 样本平衡** | 负样本明确存在，可大规模构造 | 已知矿床极少且**空间聚簇**；「未知」不等于「负样本」——正解是 **PU 学习与异常检测**，不是补负样本 |
| **4. 多模态与尺度** | 图像 + 文本，尺度相对统一 | 光学 / SAR / DEM / 重力 / 磁法 / 地震 / 化探，**物理量不同、采样率差几个数量级**；跨传感器、跨分辨率必须显式适配 |
| **5. 数据关联** | 样本近似独立同分布，随机切分有效 | **托布勒地理学第一定律**：近处相似。同剖面相邻 patch 几乎重复；随机切分让测试集与训练集空间相邻，**信息泄漏 → AUC 虚高**。必须空间分块 CV、leave-location-out、按井切分 |

**代价要说清**：换成空间分块后，**精度数字一定会掉**——掉的这部分才是虚高，不是模型变差。

---

### page2 · 训练环节的不同

**标题**：从「刷分」到可证伪的推断
**副标**：列表格 · 环节 / 人工智能的做法 / 地质 AI4S 的做法

| 环节 | 传统人工智能的做法 | 地质 AI4S 的做法 |
|---|---|---|
| **1. baseline / SOTA 的选择** | 与前一名模型比，榜单分数说话；SOTA 是目标 | SOTA 是**下限不是目标**。基线要包含**地质方法本身的基线**（克里金、地质统计、专家人工解译），先证明「打得过传统地质方法」再谈超越前一版网络 |
| **2. 损失函数的设计** | 交叉熵 / MSE 为主，单目标优化 | **数据项 + 物理残差**：PDE 残差、守恒律、边界条件当正则项；同时输出**校准过的概率**而不是一个点估计。PINN / SciML 在全样本占 5.9% |
| **3. 预训练目标**（本次补充） | 掩码重建、对比学习；目标函数决定模型上限 | 掩码 / 对比 / 对齐已做烂，**物理残差是唯一还有大空间的一格**；要往「表征预测」（JEPA 式潜变量预测）走，而不是继续拼重建像素 |
| **4. 适配方式**（本次补充） | 全量微调为主，算力换性能 | **冻结骨干 + 轻量适配**：权重公开后冻结约 97% 参数、只训回归头即可迁移（参见 N2），单卡可复现，是个人研究者最现实的入口 |
| **5. 不确定性输出**（本次补充） | 多数只给点估计，置信度靠 softmax | 必须给**后验或误差条**：没有不确定性的反演结果无法进入决策流程。校准曲线、可靠性图、Molchan 图是验收标准 |

**行业现状（支撑数据）**：地质主体子集 n = 2,099，同一篇论文可命中多项——深度学习 46.2%、传统 ML 19.3%、**XAI + UQ 17.1%**、融合 7.9%、自监督 7.1%、PINN/SciML 5.9%、Geo-LLM 4.1%、生成式 3.6%。

> **直读结论**：CNN / GNN / Transformer 已不是创新点；**SHAP、XAI、UQ 是本领域的刚需**；大模型类在地质主体子集只有 4.1%，仍集中在方法类出口。

---

### page3 · 评测环节的不同

**标题**：不仅要知道它准，还要知道它为什么准、准在哪个物理量上

**1. 传统 AI 的评测观**

> 一直提到的「黑盒」问题，在 CV / NLP 里可以用留出集 + 榜单消化掉——因为任务边界清楚、标签客观、分布可控。

**2. 地质 AI4S 的评测观（原稿保留）**

> 需要**解释性高的模块设计**，需要**有区分度的评测集设计**；不仅要准，还要知道**它为什么准，准在哪个物理量上**。

**3. 四条可检查的评测替代方案（本次补充）**

| 替代方案 | 做法 | 检查什么 |
|---|---|---|
| **空间分块验证** | 留出整块空间单元、留下整口井，而非随机切分 | 分数是否还存在；掉的幅度即虚高幅度 |
| **物理一致性诊断** | 守恒量诊断、功率谱、外推区是否出现非物理图案 | 模型学的是过程还是纹理 |
| **概率校准评估** | 校准曲线、可靠性图、Molchan 图 | 说 80% 把握是否真有 80% 命中 |
| **专家盲测** | 与地质学家的独立判断对照 | 一致性究竟有多高 |

**4. 明确不要用的指标**

随机切分下的 AUC / IoU / R²——在空间自相关数据上系统性虚高，**换区即掉**，不具备可迁移性证据。

---

## Part 3 · 地质 AI4S 的方向剖析

> **选刊口径**：入中科院 / JCR 一区、二区、三区，2025-09-21 ~ 2026-09-21 区间，按标题与关键词划分方向。

---

### page1 · 方向一：水文地质、地下水与环境地球化学 AI

> 该方向在地质主体子集占 **20.9%，是当前最热**；但本地文献底账**空缺**，以下 5 篇为本次检索新增。

**参考的文献简读**

| 文献 | 类型 | 核心方法 / 内容 |
|---|---|---|
| *Groundwater Level Modeling with Machine Learning: A Systematic Review and Meta-Analysis*, **Water** 14(6): 949, 2022 · `10.3390/w14060949` | 系统综述 | 对地下水位 ML 建模做系统性梳理与元分析，归纳算法族、输入变量与评价口径 |
| *A Comprehensive Review of Conventional, ML and DL Models for Groundwater Level Forecasting*, **Applied Sciences** 13(4): 2743, 2023 · `10.3390/app13042743` | 综述 | 横向对比传统水文模型、机器学习与深度学习在地下水水位预报上的表现 |
| *Rapid groundwater decline and some cases of recovery in aquifers globally*, **Nature** 625, 2024 · `10.1038/s41586-023-06879-8` | 实证研究 | 全球含水层尺度地下水位变化评估，提供区域级背景场与人类干预效应证据 |
| *Arsenic and other geogenic contaminants in global groundwater*, **Nature Reviews Earth & Environment** 5, 2024 · `10.1038/s43017-024-00519-z` | 综述 | 全球地下水地质成因污染物（砷等）分布规律与驱动机制 |
| *Coupling Deep Learning and Physically Based Hydrological Models for Monthly Streamflow Predictions*, **Water Resources Research** 60, 2024 · `10.1029/2023wr035618` | 方法研究 | 深度学习与物理水文模型**耦合**，是「数据项 + 物理约束」路线的典型落地 |

**解决什么问题**

1. **点观测 → 区域场的外推**：地下水位与污染物浓度是点位测量，业务需要的却是区域分布图与未来趋势。
2. **人—自然耦合系统**：抽水、灌溉、水库调度是外生变量，纯数据模型难以分离气候信号与人类活动信号——这正是「物理模型 + 深度学习耦合」要解决的问题。
3. **背景场与异常判别**：全球尺度评估（Nature 2024）与地质成因污染分布（NREE 2024）为异常检测提供了先验，缓解「无真值」困境。

**还卡在哪**

- **站点稀疏且分布不均**：监测井多沿道路与开发区布设，与地质问题无关，训练集天然有偏。
- **外生变量不可观测**：抽水量、灌溉量长期缺测，模型只能学代理变量，跨区域迁移时失效。
- **跨含水层迁移弱**：不同含水层介质结构差异大，一个模型难以覆盖；换盆地即掉分。
- **与地灾/水文的边界模糊**：该方向 20.9% 的高占比中包含大量纯环境工程论文，做方向占比统计时需剔除，否则会高估地质 AI 的真实体量。

---

### page2 · 方向二：地质遥感解译、岩性识别与智能地质填图

> 该方向占 **15.2%**；本地覆盖充分（R9、N5、R3）。

**参考的文献简读**

| 文献 | 类型 | 核心方法 / 内容 |
|---|---|---|
| R9 · *Advances on Multimodal Remote Sensing Foundation Models for Earth Observation Downstream Tasks: A Survey*, **Remote Sensing** 17(21): 3532, 2025 · `10.3390/rs17213532` | 综述 | 综述「视觉—X」（语言、音频、位置）多模态遥感基础模型的关键技术、预训练数据集，按骨干网络与跨模态交互方式分类；总结五大挑战 |
| N5 · Liu Huize 等, *A Novel Sample Generation Method for Deep Learning Lithological Mapping with Airborne TASI Hyperspectral Data in Northern Liuyuan, Gansu, China*, **Remote Sensing** 16(15): 2852, 2024 · `10.3390/rs16152852` | 实证研究 | 提出「多岩性光谱样本选择」（MLS3）样本生成方法缓解样本稀缺；联合 2D-CNN、HybridSN、MSRN、SSRN、SPRN 五种模型，SPRN 精度 84.03%，总体精度较其他采样方法提升 2.25%–6.96%（甘肃北柳园，机载 TASI 高光谱） |
| R3 · *A Review of Mineral Prospectivity Mapping Using Deep Learning*, **Minerals** 14(10): 1021, 2024 · `10.3390/min14101021` | 综述 | 数据增强与样本构造部分同样适用于填图类任务 |

**解决什么问题**

1. **把专家解译变成可复现流程**：岩性单元与蚀变信息提取依赖专家经验，模型化后可批量、可复核。
2. **高光谱 / 多光谱的样本稀缺**：N5 的 MLS3 正是针对「高质量标注样本极少」这一核心约束提出的样本生成方案——**创新落在数据层，而不是网络结构**。
3. **多传感器统一表征**：从「每个传感器训一个模型」转向「一个模型适配多传感器」（DOFA 式动态波长自适应）。

**还卡在哪**

- **标签与验证同源**：标签取自地质图，验证再用同类图件，形成「**用图件验证图件**」的循环——精度再高也不能证明对地下的判断成立。
- **地表通用 ≠ 地下通用**：B 类感知表征模型学的是地表纹理与光谱统计，**不认识岩性成因**。
- **缺统一评测**：R9 明确指出缺统一划分协议与评测基准，跨论文数字不可比。
- **高光谱数据获取成本高**：机载 TASI 一类数据本身昂贵，样本生成方法虽缓解标注问题，但没解决数据源问题。

---

### page3 · 方向三：地震监测、震源参数与地震学 AI

> 该方向占 **14.1%**；本地覆盖最充分（R2、R4、R7 + N1、N2、N3、N9，共 7 篇）。

**参考的文献简读**

| 文献 | 类型 | 核心方法 / 内容 |
|---|---|---|
| R4 · Kubo, Naoi, Kano, *Recent advances in earthquake seismology using machine learning*, **Earth, Planets and Space** 76: 36, 2024 · `10.1186/s40623-024-01982-0` | 综述 | 四方面进展：①地震目录构建（事件检测/分类、震相拾取、相似波形搜索、震源机制）②地震活动性分析 ③地震动预测 ④地壳形变分析；讨论不平衡地震动数据的影响 |
| R2 · An Yu 等, *Deep learning based automatic seismic fault interpretation: A systematic review*, **Earth-Science Reviews** 243: 104509, 2023 · `10.1016/j.earscirev.2023.104509` | 系统综述 | 回顾 2012–2022 年自动化断层解释（CNN、U-Net、GAN、Transformer、多尺度与多任务学习），提出研究问题框架 |
| R7 · Xie Yazhou, *Deep Learning in Earthquake Engineering: A Comprehensive Review*, arXiv:2405.09021, 2024 | 综述 | 结构地震响应预测、结构损伤监测识别、震害评估、地震动记录选取与合成 |
| N1 · Norisugi, Kaneko, Rouet-Leduc, *Machine learning predicts meter-scale laboratory earthquakes*, **Nature Communications** 16: 9593, 2025 · `10.1038/s41467-025-64542-4` | 实证研究 | 对米尺度岩石摩擦实验的声发射目录构建「事件网络表示」，在主震前数十秒至毫秒预测破坏时间；结合速率—状态摩擦数值模型解释其追踪的是蠕滑区剪应力演化 |
| N2 · Wang Chonglang 等, *Generalizable deep learning models for predicting laboratory earthquakes*, **Communications Earth & Environment** 6: 219, 2025 · `10.1038/s43247-025-02200-9` | 方法研究 | Decoder-only 时序卷积网络 + 迁移学习（**冻结约 97% 解码器、仅微调回归头**），跨双轴与双直剪构型、不同滑动速率下预测破坏时间与剪应力 |
| N3 · Norisugi, Kaneko, Rouet-Leduc, *ML Predicts Earthquakes in the Continuum Model of a Rate-And-State Fault With Frictional Heterogeneities*, **GRL** 51(9): e2024GL108655, 2024 · `10.1029/2024GL108655` | 方法研究 | 合成地震目录上构造「多重网络表示」输入特征，可在数十年至数分钟尺度预测距主震时间 |
| N9 · Kohler, Li 等, *Probabilistic and Alarm-Based Evaluation of a b-Value-Driven Deep Learning Earthquake Forecasting Model*, arXiv:2603.03079, 2026 | 方法研究 | 以**概率 + 告警**双指标评估 b 值驱动的深度学习预报模型；表明 b 值时空变化含有限但持续的预报信号 |

**解决什么问题**

1. **目录构建自动化**：震相拾取、事件检测与分类从人工转向模型，样本量提升几个数量级（R4）。
2. **断层解释效率**：三维地震数据体的人工解释耗时以月计，自动化后进入可迭代流程（R2）。
3. **可预测性的物理检验**：N1/N3 用速率—状态摩擦模型给机器学习结果提供物理解释，把「预测准了」推进到「为什么准」。
4. **评测范式**：N9 用概率 + 告警双指标，为「预报类」模型提供了严格评估范式，避免用单一准确率自证。

**还卡在哪**

- **跨尺度外推**：实验室破裂实验与天然断层**差数个数量级**；「追踪剪应力演化」目前属**事后解释**，外推能力未被验证。
- **「预报」被高估**：b 值只含**有限**信号；告警式指标对阈值敏感，换阈值结论就变。
- **合成数据 ≠ 真实地下**：N3 在连续模型上成立，不代表野外可用。
- **一区难进**：地震学主场在三区（SRL / NHESS），想进一区需靠物理机理或 Nature 系综合刊。

---

### page4 · 方向四：矿产资源勘查与成矿预测

> 该方向占 **7.0%**；本地覆盖充分（R3、R6 + N6、N7）。

**参考的文献简读**

| 文献 | 类型 | 核心方法 / 内容 |
|---|---|---|
| R3 · Sun Kang 等, *A Review of Mineral Prospectivity Mapping Using Deep Learning*, **Minerals** 14(10): 1021, 2024 · `10.3390/min14101021` | 综述 | 回顾 CNN/RNN/自编码器/GAN 在 MPM 中的应用，重点剖析数据预处理、数据增强、超参调优、精度评价四大挑战 |
| R6 · Zuo R., Carranza E.J.M., *Machine Learning-Based Mapping for Mineral Exploration*, **Mathematical Geosciences** 55: 891–898, 2023 · `10.1007/s11004-023-10097-3` | 综述 | 前沿算法：随机森林、卷积神经网络、**图卷积网络（GCN）**及其在找矿预测填图中的应用（Zuo 团队为该方向权威） |
| N6 · Amirajlo 等, *Ensemble machine learning strategies for mineral prospectivity mapping under data scarcity*, **Scientific Reports** 16, 2026 · `10.1038/s41598-026-40125-1` | 方法研究 | 面向标记稀缺与类别不平衡，评估 LightGBM+AdaBoost、SVM+高斯朴素贝叶斯两种集成配置，比较网格/随机/贝叶斯三种调参与 SMOTE；强调**概率校准与可复现性优于边际精度提升**（AUC 0.90–0.95，伊朗 Dehaq 铅锌矿区） |
| N7 · Luo Zijing 等, *An explainable semi-supervised deep learning framework for mineral prospectivity mapping: DEEP-SEAM v1.0*, **GMD** 19: 2593, 2026 · `10.5194/gmd-19-2593-2026` | 方法研究 | 面向稀土（REE）勘查，提出半监督异常检测深度模型 DevNet：少量正样本 + 大量未标注样本建立多源勘查数据到矿化概率的映射；引入 **SHAP** 事后解释（南澳北 Curnamona 省） |

**解决什么问题**

1. **正负样本问题**：N7 的**半监督异常检测**与 N6 的**类别不平衡集成**，是针对「已知矿床极少、未知≠负样本」这一本领域最核心约束的两条正解路线。
2. **从分数到概率**：N6 明确把**概率校准**抬到比边际精度更重要的位置——这是与「刷 AUC」路线的分水岭。
3. **可解释性落地**：N7 用 SHAP 把深度模型输出归因到具体勘查图层，让结果可被地质学家质询。
4. **多源信息融合**：R6 的 GCN 把地质单元关系作为图结构建模，是「地质知识进网络」的一种形态。

**还卡在哪**

- **无真值可依**：无监督化探异常没有真值，**阈值任选、结论不可复核**；「异常即矿」本身是待验证的前提，不是结论。
- **空间聚簇 + 随机切分**：该方向大量论文仍用随机切分，指标虚高。
- **可解释 ≠ 因果**：SHAP / 归因图给的是**贡献度**，不是因果证据。
- **三区主场**：OGR / JGE / NRR 是主要出口，目标一区得分要靠地质发现而非方法增量。

---

### page5 · 方向五：GEOAGI 地质通用模型

> 该类在地质主体子集占 **4.1%**，但在含方法刊与综合顶刊的全样本中占 **9.5%**——**仍集中在方法类出口，不是地质出口**。

**1. LLM 类（A · 语言知识型）**

| 文献 / 项目 | 时间 | 内容 |
|---|---|---|
| GeoGalactica | 2024-01 | 30B 参数地质大模型，证明领域语料可以撑起一个大模型 |
| 元古 | 2024-12 | 62 万余条数据、全国产算力训练，把「数据—算力」自主性摆上台面 |
| GeoGPT | 2025-04-27 开放 | 面向全球地学家的开源大模型，A 类第一个标志性出口 |
| Autonomous GIS 议程 | 2025-09-12 | 提出自主 GIS 研究议程，把「编排」单列成一个方向 |
| OneStrata | 2026-07-03 | 以 11 颗金钉子标定全球年代地层，知识组织能力的公开检验 |
| AI-GeoMapping / AI-OreSeeking | 2026-09-11 | 全球首发，B 类表征与 C 类业务系统同时出现在议程里 |
| R5 · `10.1111/exsy.13654` | 2024 | 综述生成式 AI（GAN、PINN、GPT 类）在地学中的应用：数据生成/增强、超分辨率、全色锐化、去雾、修复、地表变化监测 |

> **边界**：A 类**不产生地质预测**，本质是懂地质的检索写作工具。

**2. 感知表征类（B · Earth Foundation Model）**

| 文献 / 项目 | 内容 |
|---|---|
| N8 · *On the foundations of Earth foundation models*, **Comms. Earth & Environment** 7, 2026 · `10.1038/s43247-025-03127.x` | 提出理想地球基础模型应具备的 **11 项关键特征**，讨论能效自适应微调、对抗防御、可解释性，并给出标准化评估标准 |
| R9 · `10.3390/rs17213532` | 多模态遥感基础模型的分类体系与五大挑战（数据稀缺、跨任务泛化弱、缺统一评测、安全性不足等） |
| Aurora · TerraMind · Prithvi-EO-2.0 · DOFA · Clay | 代表模型：大气 / 多模态 / 时序 / 多传感器自适应 / 遥感专用 |

**B 类的五个环节（原版 deck 口径，可直接复用）**

1. **输入**：海量无标注影像——光学、SAR、DEM、时序，不需要任何标签。
2. **自监督预训练**：掩码重建、对比学习、时序对比——**目标函数里没有地质标签**。
3. **通用表征**：得到一套公开权重，把任意影像压成可复用的特征表示。
4. **迁移方式**：冻结探测（只训线性头）或 LoRA / Adapter 轻量适配。
5. **下游任务**：地物分类、变化检测、灾害痕迹识别、形变与蚀变信息提取。

> **冻结线性探测是验证表征质量的硬证据**：骨干完全不动还能达标，才说明表征本身有用。但它学的是**地表纹理与光谱统计**，不认识岩性成因——**地表通用，不等于地下通用**。

**3. 三类「通用」必须分开讲（原稿最容易被误读的一点）**

| 类别 | 定义 | 代表 | 成立条件 |
|---|---|---|---|
| **A · KNOWLEDGE** 语言知识型 | 把地学文献与图件知识压进语言模型，做检索、问答、抽取与编排 | GeoGPT · 元古 · OneStrata · 葱岭·智寻 | **不产生地质预测**，本质是懂地质的检索写作工具 |
| **B · REPRESENTATION** 感知表征型 | 大规模自监督预训练得到统一表征，冻结后迁移下游 | Aurora · TerraMind · Prithvi-EO-2.0 · DOFA · Clay | **目前唯一被实验证据支持的「通用」** |
| **C · WORKFLOW** 业务系统型 | 把 A、B 与数值模拟串成工作流，做流程编排与人机协同 | AI-GeoMapping · Autonomous GIS · Destination Earth | 能力上限由下两层决定；多为工程发布，**部分不入期刊统计** |

**「通用」的三道门槛**：**广泛预训练**（覆盖多任务多模态）、**超越单任务**（不是某个任务的专用网络）、**有迁移适配证据**（冻结或轻量适配即可达标）。**目前只有 B 类同时满足。**

**还卡在哪**

- **通用边界止于地表**：地下没有真值、没有共享坐标系；Prithvi-EO-2.0 一类覆盖的是地表观测。
- **C 类难以计量**：工程发布类成果不进入 Crossref 统计，做国内外对比时必须手工补充。
- **评测体系刚起步**：缺统一划分协议、诊断指标与泄漏审计（N8 的核心呼吁）。

---

## Part 4 · 对齐：最新 AI 技术能否融入地质 + AI

### page1 · 世界模型：功能，以及地质论文在拿它做什么

**标题**：从「判别式拟合」到「如果我做 X，会发生什么」
**副标**：JEPA · What-if · 可干预

**1. 世界模型是什么（功能定义）**

| 概念 | 一句话定义 | 关键机制 |
|---|---|---|
| **JEPA**（Joint-Embedding Predictive Architecture） | **在表征空间预测未来**：不重建像素，只预测被预测变量的表示 | 避开把算力花在雨滴纹理上；源头为 I-JEPA（arXiv:2301.08243），已有 3D-JEPA（2409.15803）、VL-JEPA（2512.10942）等跨模态拓展 |
| **World Model** | 引入 **action** 才能回答 what-if | 水库蓄水、注采、开挖——**地质本就在做这些提问** |
| **Decision Model** | 输出**带校准概率的类型化判断** | 走「判断」而非「生成」：结构即契约，输出不越出 schema |

> **三者的分工，比任何一个产品本身都更值得注意**：JEPA 管世界怎么演化，世界模型管干预的后果，决策模型管此刻该判什么。

**2. 地质论文目前拿它做什么（现状，分三类）**

| 路线 | 地质侧代表 | 在做的事 |
|---|---|---|
| **A. 物理代理场**（最接近世界模型） | GraphCast（Science 2023）、Pangu-Weather（Nature 2023）、**NeuralGCM（Nature 2024）**、Aurora（Nature 2025） | 用神经网络替代数值模式做快速预报；其中**只有 NeuralGCM 保留了传统动力核心、ML 只学未解析过程**，是真正的混合模型。GraphCast / Pangu 的「物理性」来自训练数据（再分析场本身是物理模型产物），**不是来自损失函数** |
| **B. 可微正演 → 反演闭环** | Devito、Deepwave、PyLops 提供可微正演算子；N4 走端到端成像；Ambient Noise FWI 用神经算子替代正演 | 把「正演 → 反演 → 不确定性 → 决策」做成**可微闭环**：d = F(m) 可微可批量 → 反演加物理残差与先验正则 → 输出后验 → 决定下一个钻孔打在哪（主动采样、贝叶斯实验设计） |
| **C. 生成式条件模拟** | GAN / 扩散模型做地质体与储层建模 | 生成符合条件数据的地质实现，本质是**地质统计模拟的神经化**，而非因果意义上的世界模型 |

**3. 能否融入地质？——可执行的三层融合路线**

| 层级 | 做什么 | 具体动作 | 验收指标 |
|---|---|---|---|
| **LAYER 01 · 短期** | 表层替换：把预训练目标从「重建 / 判别」换成**表征预测** | 在连续场上做 JEPA 式潜变量预测，下游迁移到稀疏地质目标（岩性、矿化、断层） | M-JEPA 协议：冻结骨干 + 两个对照组 + 物理诊断（**CKA · 功率谱 · FSS**） |
| **LAYER 02 · 中期** | 中层升级：给模型加「动作」，做 **Action-Conditioned Surrogate** | 不需要人工标注干预数据，**把自然发生的地质状态变化本身当作 action 监督**：开采前后的 InSAR 时序、地震前后的应力/孔压场、剥蚀前后的地貌 | what-if 推演能否支持决策 |
| **LAYER 03 · 长期** | 深层重构：从「预测器」走向可交互的**科学推理伙伴** | 三条线索合并：JEPA 表征 + 冻结迁移｜物理残差 / 可微正演做硬约束｜LLM 与多模态做地质知识与跨源证据的组织层 | 表征 + 物理 + 知识三层可分工协同 |

> **顺序不能颠倒**：没有 B 类感知层把地质数据压成向量，决策层在地质里就没有接口——**感知层是决策层落地的前置条件**。

**4. 三条边界（必须一起讲，否则会显得盲目乐观）**

- **边界一 · 领域差异**：视频与机器人世界的连续场预测，误差几个数量级地优于离散 token 预测；但地质目标是**稀疏的、带噪的、多解的**——指标好看不等于地质可用。
- **边界二 · 物理约束**：JEPA 至今**没有在各领域都经过充分验证的干预有效性方案**；物理残差项因此不能省——它是模型在无标签处学习物理一致性的唯一接口。
- **边界三 · 基本功**：2024 年可解释性与不确定性量化占 **17.1%**，几乎追平传统机器学习；在稀疏观测下给出**可信区间**，比再涨一个准确率点更有价值。

---

### page2 · Jev 模型：功能，以及它可以落在哪些地质方向

**标题**：它不生成文字，它给判断
**副标**：System One · 类型化输出 · 毫秒级

**1. Jev 是什么（功能定义，本次检索补充）**

| 项 | 内容 |
|---|---|
| 开发方 | **TypeSafe AI** |
| 发布时间 | 2026 年 9 月，官方定位为其**第一个 System One 模型** |
| 命名/理念 | 借《思考，快与慢》：LLM 被视为 **System 2**（慢、深、逐 token 推理），Jev 要做 **System 1**（快速判定） |
| 核心特点 | **不生成文字**。传入一段**状态（state）**+ 若干**带类型的问题**，返回**代码可直接使用的判断结果** |
| 三种机制 | **Choice / Score / Noul**——把自然语言转为带类型的判断与概率 |
| 适用场景 | **分类、评分、路由（routing）**；配「置信度路由」工作流 |
| 明确不适合 | 对话与内容生成——「它不陪你聊天，也不替你写文章」 |

**2. 与地质 AI 的接口在哪里（推断，非已有论文结论）**

> ⚠️ **重要限定**：Jev 2026-09 才发布，**目前没有地质领域的公开论文**。以下为按能力对齐得出的候选方向，汇报时应明确标注为「可迁移假设」。

| 地质任务 | 对应机制 | 为什么契合 |
|---|---|---|
| **岩性 / 矿物类型判定** | Choice | 输入光谱或图像特征状态，输出「属于哪一类」的**闭集判断**，天然不需要生成文本 |
| **勘查靶区打分** | Score | 多源勘查图层作为 state，输出 0–1 概率分数；与本领域「矿化概率图」的产物形态一致 |
| **解释方案路由** | routing | 断层解释、井震标定常有多解，按置信度**路由**到「直接采纳 / 人工复核 / 重新采集」三档 |
| **数据质量分流** | routing | 采集端即时判定哪些剖面/井段需要重测，替代离线批处理 |
| **结构化抽取** | Choice | 从报告图件中抽取带 schema 的地质要素，**结构即契约**，输出不越界 |

**3. 为什么这个概念对地质有价值**

1. **它把「判断」和「生成」分开**——地质产物本来就多为**类型化判断**（这是哪类岩、有没有矿、能不能打），而不是自由文本。
2. **输出可被代码直接消费**：判断结果带类型与概率，可**直接进入工作流**，不需要再解析自然语言。
3. **它与世界模型互补**：世界模型回答「如果我做 X 会怎样」，Jev 一类判断模型回答「此刻该判什么」。

**4. 必须交代的风险**

- **不可追溯的高置信度本身就是风险**：只给概率、不给理由的模型，在地质决策里无法通过评审。
- **缺少一手实验证据**：Jev 的公开信息以官方与社区评测为主，**尚无论文级验证**，不应作为方法主体写进地质论文。
- **它的强项是「快」，不是「对」**：地质决策错一次的成本是百万级钻探，**速度收益远小于判断错误的风险**——合理的用法是先当复核加速器，不当最终裁决者。

**5. 汇报时的一句话结论**

> 世界模型与 Jev 代表的是**两种不同的技术信号**：世界模型说「预测的形态要换」，Jev 说「判断的形态要换」。对地质而言，**前者有可落地的接口，后者目前只有可借鉴的形态**。

---

### 收尾页 · MANIFESTO

**标题（超大字）**：在稀疏观测下，做**可证伪**的推断。

**副文**：本质问题不是「AI 能不能给岩石分类」，而是能不能给出**外推得动、物理说得通、不确定性下可决策**的结论。

**三条 TAKEAWAYS**

| # | 内容 |
|---|---|
| **01** | **三条边界要写进方法里**：解释性数据、空间 + 物理双约束、以独立地质证据与概率可靠性为准绳——不是口号，而是三个可检查的环节。 |
| **02** | **落地形态是分层通用，不是「一个模型包打天下」**：冻结骨干 + 轻量适配是个人研究者最现实的入口；感知层是决策层落地的前置条件。 |
| **03** | **换的是范式，不是名词**：判别式拟合确实退居其次，真正的形态是——连续代理场学动力学 → 迁移到稀疏地质目标 → 支持 what-if 推演与决策。 |

**页脚**：汇报人 · 地质 + AI　｜　2026.09　｜　→ 完 · 谢谢，欢迎讨论

---

## 附录 A · 文献总表（含 DOI，可直接复制进参考文献页）

### A.1 综述（R 系列）

| 编号 | 文献 | 出处 | DOI |
|---|---|---|---|
| R1 | Artificial intelligence for geoscience: Progress, challenges, and perspectives | The Innovation 5(5):100691, 2024 | `10.1016/j.xinn.2024.100691` |
| R2 | Deep learning based automatic seismic fault interpretation: A systematic review | Earth-Science Reviews 243:104509, 2023 | `10.1016/j.earscirev.2023.104509` |
| R3 | A Review of Mineral Prospectivity Mapping Using Deep Learning | Minerals 14(10):1021, 2024 | `10.3390/min14101021` |
| R4 | Recent advances in earthquake seismology using machine learning | Earth, Planets and Space 76:36, 2024 | `10.1186/s40623-024-01982-0` |
| R5 | When geoscience meets generative AI and large language models | Expert Systems 41(8):e13654, 2024 | `10.1111/exsy.13654` |
| R6 | Machine Learning-Based Mapping for Mineral Exploration | Mathematical Geosciences 55:891–898, 2023 | `10.1007/s11004-023-10097-3` |
| R7 | Deep Learning in Earthquake Engineering: A Comprehensive Review | arXiv:2405.09021, 2024 | — |
| R8 | 基于深度学习的岩石矿物智能识别研究进展与发展趋势 | 成都理工大学学报（自然科学版）52(1), 2025 | `10.3969/j.issn.1671-9727.2025.01.05` |
| R9 | Multimodal Remote Sensing Foundation Models for Earth Observation Downstream Tasks: A Survey | Remote Sensing 17(21):3532, 2025 | `10.3390/rs17213532` |

### A.2 近期高影响力研究（N 系列）

| 编号 | 文献 | 出处 | DOI |
|---|---|---|---|
| N1 | Machine learning predicts meter-scale laboratory earthquakes | Nature Communications 16:9593, 2025 | `10.1038/s41467-025-64542-4` |
| N2 | Generalizable deep learning models for predicting laboratory earthquakes | Communications Earth & Environment 6:219, 2025 | `10.1038/s43247-025-02200-9` |
| N3 | ML Predicts Earthquakes in a Rate-And-State Fault With Frictional Heterogeneities | GRL 51(9):e2024GL108655, 2024 | `10.1029/2024GL108655` |
| N4 | Deep learning for high-resolution seismic imaging | Scientific Reports 14, 2024 | `10.1038/s41598-024-61251-8` |
| N5 | A Novel Sample Generation Method for DL Lithological Mapping (TASI, 甘肃北柳园) | Remote Sensing 16(15):2852, 2024 | `10.3390/rs16152852` |
| N6 | Ensemble ML strategies for mineral prospectivity mapping under data scarcity | Scientific Reports 16, 2026 | `10.1038/s41598-026-40125-1` |
| N7 | DEEP-SEAM v1.0: explainable semi-supervised DL for MPM | GMD 19:2593, 2026 | `10.5194/gmd-19-2593-2026` |
| N8 | On the foundations of Earth foundation models | Communications Earth & Environment 7, 2026 | `10.1038/s43247-025-03127.x` |
| N9 | Probabilistic and Alarm-Based Evaluation of a b-Value-Driven DL Earthquake Forecasting Model | arXiv:2603.03079, 2026 | — |

### A.3 本次新增（方向一 + 世界模型）

| 用途 | 文献 | 出处 | DOI |
|---|---|---|---|
| 方向一 | Groundwater Level Modeling with ML: A Systematic Review and Meta-Analysis | Water 14(6):949, 2022 | `10.3390/w14060949` |
| 方向一 | A Comprehensive Review of Conventional, ML and DL Models for GWL Forecasting | Applied Sciences 13(4):2743, 2023 | `10.3390/app13042743` |
| 方向一 | Rapid groundwater decline and some cases of recovery in aquifers globally | Nature 625, 2024 | `10.1038/s41586-023-06879-8` |
| 方向一 | Arsenic and other geogenic contaminants in global groundwater | Nature Reviews Earth & Environment 5, 2024 | `10.1038/s43017-024-00519-z` |
| 方向一 / 物理耦合 | Coupling Deep Learning and Physically Based Hydrological Models | Water Resources Research 60, 2024 | `10.1029/2023wr035618` |
| Part4 / JEPA | Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-JEPA) | arXiv, 2023 | `10.48550/arXiv.2301.08243` |
| Part4 / JEPA | 3D-JEPA: A Joint Embedding Predictive Architecture for 3D SSL | arXiv, 2024 | `10.48550/arXiv.2409.15803` |
| Part4 / JEPA | VL-JEPA: Joint Embedding Predictive Architecture for Vision-language | arXiv, 2025 | `10.48550/arXiv.2512.10942` |

### A.4 期刊出口对照（用于 Part3 投稿策略，如需可作附页）

- **一区 · 11 刊 · 16.9%**（1,000/5,907）：Nature Machine Intelligence AI 占比 50.0%、Patterns 43.0%；但**分区高 ≠ AI 友好**——Geology 2.3%、EPSL 0.8%。
- **二区 · 12 刊 · 23.7%**（3,046/12,858）：Remote Sensing 1,745 篇（43.5%）居首；水文三刊合计 552 篇、JSTARS 380 篇。**二区承接的 AI 论文是一区的 3 倍**，是 AI 落地的绝对主战场。
- **三区 · 7 刊 · 17.6%**（416/2,362）：Mathematical Geosciences 30.1%、Computers & Geosciences 28.7%、Geophysics 11.9%；门槛高、审稿人懂物理。
- **口径边界**：小计只含**同时给出 AI 数与总篇数**的期刊；Nature Communications、Science Advances、PNAS 等未给分母者**未计入**，故 **21.1% 是偏乐观的上界**。

---

## 附录 B · 风险提示与交付自检

### B.1 引用风险

1. **撤稿核验**：地震「预报 / 预测」类论文是高撤稿风险区，凡引用 2024 年后的高精度预报结论，**投用前用 Crossref + Retraction Watch 逐条核验撤稿状态**，不要依赖二手综述的转述。
2. **检索陷阱**：检索时用 **geoscience / earth science** 而非 **geology**——后者会返回大量无关且零被引的论文；同时用被引量做初筛。本次新增文献均已按此口径筛选。
3. **预印本标注**：R7、N9、以及三个 JEPA 条目为 arXiv 预印本，PPT 上需标注「预印本，未经同行评审」。

### B.2 口径风险（不要在 PPT 上省掉的话）

- **21.1% 是上界**，不是实测值；口径边界必须与数字同页出现。
- **方向占比与分区×方向的交叉**：现有数据**没有「每刊 × 每方向」的交叉统计**，Part3 中任何分区×方向的分配都是**估算值，不可单独摘引**。
- **同一篇论文可命中多个方法标签**，方法范式百分比**非互斥、加起来不等于 100%**。
- **C 类业务系统成果不进入 Crossref 统计**，做国内外对比时必须手工补充。

### B.3 生成后自检清单

- [ ] 19 页，每页都有 `data-layout` 且取值在 S01–S22 内
- [ ] 主题节奏：分隔页 dark、正文页 light，无连续三页同主题
- [ ] 无渐变 / 投影 / 圆角 / 多强调色 / emoji
- [ ] 所有数字与本文档「统计口径」一致，未被改写
- [ ] 表格页行数 ≤ 8，超出则拆页
- [ ] 参考文献页使用附录 A 的 DOI 原文，未改写期刊卷期
- [ ] 预印本已在页面上标注
- [ ] 分隔页大字为 weight 200，未加粗变形

