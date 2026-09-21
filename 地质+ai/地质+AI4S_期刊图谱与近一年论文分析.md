# 地质 + AI4S 期刊图谱与近一年论文分析（2025-09-21 ~ 2026-09-21）

> 整理日期：2026-09-21
> 检索窗口：2025-09-21 → 2026-09-21（当前时间向前 12 个月）
> 样本规模：83 种期刊，窗口内全部期刊论文 60,568 篇；判读出 AI 相关 7,166 篇（11.8%），其中地质主体子集 2,099 篇
> 相关文档：`docs/文献清单_地质+AI.md`（单篇精读清单）、`docs/感知型基础模型_方向项目速查.md`（基础模型模块速查）、`docs/期刊与近一年研究态势_地质+AI.md`（态势普查 + 选题建议）

---

## 一、数据来源与检索范围

| 项目 | 说明 |
|---|---|
| 主数据库 | Crossref REST API（works/journals 端点，逐刊 ISSN 精确检索） |
| 辅助尝试 | OpenAlex API（已完成期刊 Source ID 解析与总量统计，但运行时共享 IP 日预算被耗尽，故仅用于交叉校验发文总量） |
| 影响因子来源 | 公开第三方渠道（LetPub、中科院分区公开页等），标注为 JCR 2024/2025 公开值，仅供参考，建议以 JCR 官方为准 |
| 时间窗口 | 发文日 `from-pub-date:2025-09-21, until-pub-date:2026-09-21`（当前时间向前 12 个月） |
| 期刊范围 | 83 种期刊（地学 AI 专刊 + 地质学核心刊 + AI4S 综合顶刊 + 相邻领域主力刊） |
| 抓取方式 | 全量抓取（非关键词抽样）：窗口内全部 `journal-article` 型论文 **60,568 篇**元数据（DOI、标题、摘要、日期、被引数） |
| AI 判定 | 本地正则严格判读 40+ 术语：machine/deep learning、neural network、AI、CNN/GNN/U-Net、random forest、XGBoost、transformer、foundation model、LLM、PINN、data-driven、self-supervised 等；并剔除 battery/cathode/tumor 等非地学噪声词 |
| 去重 | 按 DOI + 归一化标题双重去重 |
| 主题/方法分类 | 12 类应用主题（互斥，加权投票）+ 8 类方法维度 + 10 个细分子方向（均非互斥，可重叠计数） |

**核心口径**：浏览式全文样本中，AI 相关论文 **7,166 篇（占 11.8%）**；其中剔除"非地质主体的通用 AI 方法学 / 非地质目标遥感"后，得到**地质主体子集 2,099 篇**，下文方向统计以此为主口径。

---

## 二、期刊清单（名称 / 出版社机构 / 影响因子 / 分区）

### A. 地质 + AI 的专业主战场（AI 论文占比最高）

| 期刊 | 出版社 / 主办 | IF（公开值） | 分区 | 窗口内 AI 论文 / 总数 | 占比 |
|---|---|---|---|---|---|
| Artificial Intelligence for the Earth Systems | AMS（美国气象学会） | 较新，暂无稳定 IF | — | 106 / 111 | **95.5%** |
| Journal of Geophysical Research: Machine Learning and Computation | AGU / Wiley | 新刊（2025 创刊） | — | 217 / 245 | **88.6%** |
| Machine Learning: Science and Technology | IOP Publishing | ≈4.5–5 | Q2/Q1 | 310 / 391 | **79.3%** |
| Artificial Intelligence in Geosciences | KeAi（中国） | ESCI 收录，2025 获首个 IF；偏低 | — | 62 / 99 | **62.6%** |
| Applied Computing and Geosciences | Elsevier | CiteScore ≈4.0–4.5（无 JCR IF） | — | 50 / 109 | **45.9%** |
| Patterns | Cell Press | ≈7–8 | Q1 | 64 / 149 | 43.0% |
| Nature Machine Intelligence | Springer Nature | ≈23.9 | 中科院 1 区 TOP | 97 / 194 | 50.0% |
| Data-Centric Engineering | Cambridge Univ. Press | ≈4–5 | — | 23 / 40 | 57.5% |
| Mathematical Geosciences | Springer（IAMG 会刊） | ≈3.6 | 中科院 3 区 / JCR Q1 | 34 / 113 | **30.1%** |
| Natural Resources Research | Springer（IAMG 会刊） | ≈5.0–6.0 | 中科院 2 区 | 66 / 214 | **30.8%** |
| Computers & Geosciences | Elsevier | ≈4.4 | 中科院 3 区 | 50 / 174 | **28.7%** |
| Nature Computational Science | Springer Nature | ≈12–13 | 1 区 | 49 / 180 | 27.2% |
| Environmental Modelling & Software | Elsevier（iEMSs） | ≈4.2 | 2 区 | 101 / 386 | 26.2% |
| The Innovation | Cell Press / 中国科协 | ≈33 | 1 区 TOP | 34 / 337 | 10.1% |

### B. 地质 / 地球科学核心与新锐刊（发文量集中）

| 期刊 | 出版社 / 主办 | IF（公开值） | 分区 | AI 论文 / 总数 | 占比 |
|---|---|---|---|---|---|
| IEEE Trans. Geoscience and Remote Sensing | IEEE | ≈8.6 | 中科院 1 区 TOP | 404 / 2,137 | 18.9% |
| Remote Sensing | MDPI | ≈4.3 | 中科院 2 区 | **1,745** / 4,013 | **43.5%** |
| IEEE JSTARS | IEEE | ≈4.5–5 | 2 区 | 380 / 2,012 | 18.9% |
| ISPRS J. Photogrammetry & Remote Sensing | Elsevier（ISPRS） | ≈12 | 1 区 TOP | 100 / 511 | 19.6% |
| Geoscience Frontiers | Elsevier / 中国地质大学（北京） | 约 8.9（另有来源报 12.7，存疑） | 1 区 | 29 / 204 | 14.2% |
| Ore Geology Reviews | Elsevier | ≈3.6 | 2 区 / JCR Q1 | 40 / 658 | 6.1% |
| Journal of Geochemical Exploration | Elsevier（AEG） | ≈3.4–4.2 | 2–3 区 | 10 / 239 | 4.2% |
| Journal of Applied Geophysics | Elsevier | ≈2.0–2.5 | 3 区 | 88 / 533 | 16.5% |
| Geophysics | SEG / GeoScienceWorld | ≈3.0 | 3 区 | 29 / 243 | 11.9% |
| Interpretation | SEG | ≈1.0–1.4 | 4 区 | 9 / 38 | 23.7% |
| The Leading Edge | SEG | ≈1.0–1.5 | 4 区 | 32 / 190 | 16.8% |
| Earth-Science Reviews | Elsevier | ≈10–12 | 1 区 TOP | 11 / 324 | 3.4% |
| Surveys in Geophysics | Springer | ≈7.7 | 1–2 区 | 7 / 54 | 13.0% |
| Engineering Geology | Elsevier（IAEG 会刊） | ≈8.4 | 1 区 TOP | 39 / 522 | 7.5% |
| Frontiers in Earth Science | Frontiers | ≈2.0–2.5 | 3–4 区 | 106 / 704 | 15.1% |
| Journal of Rock Mechanics and Geotechnical Engineering | 中科院武汉岩土所 / Elsevier | ≈9–10 | 1 区 | 67 / 921 | 7.3% |
| Water Resources Research | AGU / Wiley | ≈5.4 | 2 区 | 154 / 805 | 19.1% |
| Journal of Hydrology | Elsevier | ≈6.0–6.5 | 2 区 | 315 / 2,541 | 12.4% |
| Hydrology and Earth System Sciences | EGU（Copernicus） | ≈5.8 | 2 区 | 83 / 392 | 21.2% |
| Earth System Science Data | EGU | ≈11 | 1 区 | 106 / 428 | 24.8% |
| Geoscientific Model Development | EGU | ≈5.0 | 2 区 | 91 / 528 | 17.2% |
| Seismological Research Letters | SSA | ≈3.0 | 3 区 | 50 / 306 | 16.3% |
| JGR: Solid Earth / GRL / Earth's Future / ESS | AGU / Wiley | 3.9 / 4.6 / 8.0 / 3.0 | 2–3 区 | 40 / 144 / 55 / 55 | 6.2% / 6.6% / 13.6% / 16.7% |
| Petroleum Science | Springer / 中国石油大学 | ≈6.0 | 1–2 区 | 65 / 708 | 9.2% |
| Science China Earth Sciences、Journal of Earth Science | 中国科技出版传媒、中国地质大学 / Springer | ≈5.0 / ≈3.5 | 2 区 | 14 / 9 | 4.0% / 4.1% |
| Natural Hazards and Earth System Sciences | EGU | ≈4.5 | 3 区 | 59 / 289 | 20.4% |
| Bulletin of Engineering Geology and the Environment | Springer（IAEG） | ≈4.0 | 2–3 区 | 49 / 841 | 5.8% |
| Landslides | Springer（ICL） | ≈7.0 | 2 区 | 12 / 229 | 5.2% |

### C. AI4S 综合性顶刊（地学 AI 高影响力成果出口）

- **Nature Communications**（Springer Nature，≈15.7，1 区 TOP，680 篇 / 4.8%）
- **Science Advances**（AAAS，≈11.7，1 区 TOP，211 篇 / 6.1%）
- **PNAS**（美国科学院，≈9.4，1 区，286 篇 / 5.9%）
- **Nature Machine Intelligence**（≈23.9，97 篇 / 50%）
- **Nature Computational Science**
- **Nature Geoscience**（≈15–16，仅 2 篇）
- **Nature Reviews Earth & Environment**
- **Patterns**（Cell Press）
- **Science Bulletin**（≈18–21）

### 结论

AI 渗透率呈明显梯度 —— **地学 AI 专刊（50%–95%）≫ 遥感 / 计算方法类（20%–45%）≫ 传统地质学核心刊（1%–8%）**，如 Chemical Geology 0.9%、EPSL 0.8%、Geology 2.3%、Tectonophysics 0.6%、Mineralium Deposita 2.3%。

发文绝对量最大出口是 **Remote Sensing（1,745 篇）** 与 **Nature Communications（680 篇）**。

---

## 三、近一年主要学术方向与频次统计

### 3.1 应用主题分布（地质主体子集 n = 2,099，互斥）

| 排名 | 方向 | 论文数 | 占比 |
|---|---|---|---|
| 1 | 水文地质、地下水与环境地球化学 AI | 438 | **20.9%** |
| 2 | 地质遥感解译、岩性识别与智能地质填图 | 318 | **15.2%** |
| 3 | 地震监测、震源参数与地震学 AI | 295 | **14.1%** |
| 4 | 地质灾害（滑坡 / 泥石流 / 地面沉降）易发性与风险评价 | 290 | **13.8%** |
| 5 | 地球动力学、深部结构与行星 / 固体地球模拟 | 221 | 10.5% |
| 6 | 矿产资源勘查与成矿预测（含地球化学异常识别） | 146 | **7.0%** |
| 7 | 地震勘探 / 测井 / 储层地球物理智能处理与反演 | 97 | 4.6% |
| 8 | 地表过程、地貌演化与第四纪 / 沉积环境 | 93 | 4.4% |
| 9 | 地球化学分析、同位素与矿物学大数据 | 86 | 4.1% |
| 10 | 岩石力学、工程地质与岩土智能建模 | 72 | 3.4% |
| 11 | 沉积盆地、层序地层与油气地质 | 43 | 2.0% |

### 3.2 方法维度分布（n = 2,099，非互斥可重叠）

| 方法方向 | 篇数 | 占比 | 全样本口径（n = 7,166） |
|---|---|---|---|
| 深度学习（CNN / GNN / U-Net / Transformer） | 970 | **46.2%** | 43.0% |
| 传统机器学习（RF / XGBoost / SVM / 集成 / 高斯过程） | 406 | **19.3%** | 15.2% |
| 可解释 AI 与不确定性量化（SHAP / XAI / UQ） | 359 | **17.1%** | 12.1% |
| 地学异构数据融合与多源联合反演 | 165 | 7.9% | 7.0% |
| 自监督 / 弱监督 / 小样本与迁移学习 | 150 | 7.1% | 7.8% |
| 物理信息神经网络 / 科学机器学习 | 124 | **5.9%** | 5.2% |
| 地质大模型 / 多模态 / 大语言模型 | 87 | **4.1%** | **9.5%** |
| 生成式模型（扩散 / GAN / 地统计模拟） | 75 | 3.6% | 4.1% |

> 注：大模型类在全样本中的占比（9.5%）显著高于地质主体子集（4.1%），说明**地学大模型 / LLM 工作目前多发于方法类与综合顶刊，向地质主体业务渗透仍处早期**。

### 3.3 细分子方向（n = 2,099，非互斥）

| 子方向 | 篇数 | 占比 |
|---|---|---|
| 滑坡易发性 / 位移预测 | 136 | 6.48% |
| 矿产远景预测 / 找矿靶区圈定 | 61 | 2.91% |
| 灾害 · 地震预警大模型与实时监测 | 60 | 2.86% |
| 地震波 / 剖面重建与去噪 | 51 | 2.43% |
| 地震事件检测 / 相位拾取 / 预警 | 49 | 2.33% |
| 地球化学异常检测与提取 | 28 | 1.33% |
| 岩性 / 岩相自动分类识别 | 26 | 1.24% |
| 虚拟测井 / 储层参数（孔渗）预测 | 14 | 0.67% |
| 断层 / 裂缝 / 构造要素智能识别 | 11 | 0.52% |
| 智能地质填图（含露头自动化） | 8 | 0.38% |

**趋势判读**：深度学习已成默认范式；传统 ML 仍是表格型 / 小样本地学数据主力；**可解释性与不确定性量化（17%）的占比几乎追平传统 ML**，反映地学界对"AI 结论能否用于找矿与灾害决策"的核心焦虑；**智能地质填图（0.38%）与断层智能识别（0.52%）仍是明显洼地，属于高价值低竞争方向**。

---

## 四、代表性论文（标题 / 时间 / 期刊）

### ① 矿产预测与地球化学异常

- *Recent advances and future research directions in deep learning as applied to geochemical mapping*｜2025-11｜Earth-Science Reviews（26 次被引，该刊最高）
- *A semi-supervised approach for mineral prospectivity mapping via weighted positive-unlabeled learning and TPE*｜2025-10｜Ore Geology Reviews
- *Mineral prospectivity mapping for multi-source geoscience data: A novel unsupervised deep learning method*｜2025-11｜Ore Geology Reviews
- *Three-dimensional mineral prospectivity mapping using a residual CNN with lightweight attention*｜2025-10｜Ore Geology Reviews
- *A metric-learning enhanced variational autoencoder for unsupervised detection of geochemical anomalies in the Hatu gold belt, Xinjiang*｜2025-12｜Ore Geology Reviews
- *The high-efficiency data integration approach for Pakistan mineral resources using multimodal large language models*｜2026-06｜Ore Geology Reviews

### ② 地震监测与地震学 AI

- *Integrating artificial intelligence and geophysical insights for earthquake forecasting: A cross-disciplinary review*｜2025-11｜Earth-Science Reviews
- *A Generative Foundation Model for an All-in-One Seismic Processing Framework*｜2025-11-05｜Surveys in Geophysics
- *Real-Time Processing of Distributed Acoustic Sensing Data for Earthquake Monitoring Operations*｜2026-03-27｜Seismological Research Letters
- *An ML-Enhanced Earthquake Catalog for the 2024 MW …*｜2025-12｜JGR: Solid Earth
- *Ambient Noise Full Waveform Inversion With Neural Operators*｜2025-10-29｜JGR: Solid Earth
- *GeoFWI: A Large Velocity Model Data Set for Benchmarking FWI Using Deep Learning*｜2026-03-06｜JGR: Machine Learning and Computation

### ③ 岩性识别与智能地质填图

- *Geological information-driven deep learning for lithology identification from well logs*｜2025-09-25｜Frontiers in Earth Science
- *A data-driven method for intelligent lithology identification in coal mines based on drilling parameters*｜2025-12｜Engineering Geology
- *A dual attention-based deep learning model for lithology identification while drilling*｜2026-02｜J. Rock Mechanics and Geotechnical Engineering
- *Causal-Graph Lithology Classifier: Synergizing causal inference with GNNs for rock classification in well logs*｜2025-10｜Marine and Petroleum Geology
- *Interpretable regional-scale geological mapping using a contrastive graph attention network for multimodal data fusion*｜2026-02｜Engineering Geology
- *SCLRAD: Semi-supervised contrastive learning using random replacement of adjacent depths for lithology identification*｜2025-10｜J. Applied Geophysics

### ④ 地质灾害易发性与滑坡

- *A proposed method for landslide detection based on transfer learning and graph neural network*｜2025-11｜Geoscience Frontiers（64 次被引，全场最高）
- *Review article: Deep learning for potential landslide identification: data, models, applications, challenges*｜2026-01-26｜NHESS
- *Exploring the dynamic impact of urbanization on landslide susceptibility in Sichuan Province using an explainable XGBoost model*｜2025-10｜Engineering Geology
- *Region similarity assessment for empowering physics-informed transfer learning-based landslide susceptibility mapping*｜2026-09｜JRMGE
- *Uncertainty-aware ensemble learning and dynamic threshold optimization for landslide susceptibility mapping*｜2026-01｜Computers & Geosciences

### ⑤ 物理信息神经网络 / 科学机器学习

- *Physics-informed neural networks enhanced by data augmentation: robust soil moisture estimation*｜2025-12｜J. of Hydrology
- *Physics-informed neural network for elastic–plastic mesh-free modelling of tunnelling-induced deformation*｜2025-10-18｜Acta Geotechnica
- *An Efficient Multi-Physics GPT-PINN Framework for Predicting Reactive Solute Transport in Parameterized Groundwater Systems*｜2026-02-04｜GRL
- *EFKAN: A KAN-integrated neural operator for efficient magnetotelluric forward modeling*｜2026-02｜Computers & Geosciences
- *Uncertainty quantification of surrogate models using conformal prediction*｜2026-02-01｜ML: Science and Technology

### ⑥ 地质大模型 / 多模态 / LLM

- *Prithvi-EO-2.0: A Versatile Multitemporal Foundation Model for Earth Observation Applications*｜2026｜IEEE TGRS
- *A Billion-Scale Foundation Model for Remote Sensing Images*｜2026｜IEEE JSTARS
- *A Generative Foundation Model for an All-in-One Seismic Processing Framework*｜2025-11-05｜Surveys in Geophysics
- *Generative AI with prompt engineering ... Enhancing predictive slope stability modelling*｜2025-11｜Geoscience Frontiers
- *The Destination Earth digital twin for climate change adaptation*｜2026-04-14｜Geoscientific Model Development
- *Using multimodal large language models for mineral resources data integration*｜2026-06｜Ore Geology Reviews

---

## 五、方法说明与已知局限（重要）

1. **召回下限问题**：60,568 篇中仅 27,095 篇（45%）在 Crossref 中有摘要存档（Elsevier / Springer 部分不提供）。在"有摘要"样本中，题+摘判读命中率 16.9%，仅题名判读命中率 7.7%，比值 **2.20**。据此校正，**窗口内真实 AI 相关论文约 10,600 篇量级**（实测 7,166 篇为保守下限），占比约 17% 而非 11.8%。各项占比结构不受影响，绝对数请按此理解。
2. **分类为规则式判读**：主题采用加权投票 + 优先级仲裁，互斥；方法与子方向为非互斥重复计数，二者之和不等于总量。
3. **未覆盖来源**：未纳入 CNKI / 万方中文期刊、arXiv / SSRN 预印本、会议论文（如 SEG / AAPG / EGU 年会），因此未收录国内中文地学期刊的 AI 工作。
4. **影响因子口径**：第三方公开渠道存在版本差异（部分标注为 2025 发布版，部分为 2026 更新版），已对冲突值标注"存疑"，建议以当年 JCR 与中科院分区表为准。
5. **临时文件**：分析过程中的临时目录 `_tmp_geoai/` 内文件已全部删除，仅剩空目录壳，可直接 `Remove-Item` 清理（删除命令需授权执行，未能自动完成）。
