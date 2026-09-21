# 地质 + AI（AI4S）期刊图谱与近一年研究态势

> 整理日期：2026-09-21
> 检索窗口：2025-09-21 → 2026-09-21（当前时间向前 12 个月）
> 样本规模：83 种期刊，窗口内全部期刊论文 **60,568 篇**；判读出 AI 相关 **7,166 篇**，其中地质主体 **2,099 篇**
> 配套阅读：`文献清单_地质+AI.md`（单篇精读清单）、`感知型基础模型_方向项目速查.md`（基础模型模块速查）

说明：
- 本文是**态势普查**（面向"投哪里 / 做什么方向"），不是单篇精读；单篇细节见 `文献清单_地质+AI.md`。
- 所有计数均为**规则判读 + 去重**结果，绝对值为保守下限（原因见第六节）。
- 影响因子为第三方公开渠道值（JCR 2024/2025 版本混杂），**仅供排序参考**，投稿前请以当年 JCR 与中科院分区表为准。

---

## 一、数据来源与检索范围

| 项目 | 说明 |
|---|---|
| 主数据库 | **Crossref REST API**（`/works`、`/journals`，逐刊 ISSN 精确检索） |
| 辅助校验 | OpenAlex API（期刊 Source ID 解析与发文总量交叉校验；运行时共享 IP 日预算耗尽，未用于最终统计） |
| 影响因子来源 | LetPub、中科院分区公开页等第三方渠道 |
| 期刊范围 | **83 种**：地学 AI 专刊 + 地质学核心刊 + AI4S 综合顶刊 + 相邻领域（水文/岩土/遥感）主力刊 |
| 抓取方式 | **全量抓取**（非关键词抽样）：窗口内全部 `journal-article` 的 DOI、标题、摘要、发表日期、被引数 |
| AI 判定 | 本地正则严格判读 40+ 术语：machine/deep learning、neural network、artificial intelligence、CNN/GNN/U-Net、random forest、XGBoost、SVM、transformer、foundation model、LLM、PINN、neural operator、data-driven、self/semi-supervised、diffusion 等；并剔除 battery / cathode / tumor / protein 等非地学噪声词 |
| 去重 | DOI + 归一化标题双重去重 |
| 分类体系 | 12 类应用主题（互斥，标题加权投票 + 优先级仲裁）｜8 类方法维度（非互斥）｜10 个细分子方向（非互斥） |

**两个口径，注意区分：**

| 口径 | 篇数 | 用途 |
|---|---|---|
| 全样本 AI 相关 | **7,166**（占 60,568 的 11.8%） | 看"AI 在各刊的渗透率" |
| 地质主体子集 | **2,099** | 看"地质业务方向的结构占比"（剔除通用 AI 方法学、非地质目标遥感） |

---

## 二、期刊图谱：出版社 / 影响因子 / 分区 / AI 渗透率

### A 层：地质 + AI 的专业主战场（AI 论文占比 30%–95%）

| 期刊 | 出版社 / 主办 | IF（公开值） | 分区 | AI 论文 / 总数 | 占比 |
|---|---|---|---|---|---|
| **Artificial Intelligence for the Earth Systems** | AMS | 新刊，IF 待稳定 | — | 106 / 111 | **95.5%** |
| **JGR: Machine Learning and Computation** | AGU / Wiley | 新刊（2025 创刊） | — | 217 / 245 | **88.6%** |
| **Machine Learning: Science and Technology** | IOP | ≈4.5–5 | Q1/Q2 | 310 / 391 | **79.3%** |
| **Artificial Intelligence in Geosciences** | KeAi（中国） | ESCI，首个 IF 偏低 | — | 62 / 99 | **62.6%** |
| **Applied Computing and Geosciences** | Elsevier | CiteScore ≈4.0–4.5（无 JCR IF） | — | 50 / 109 | **45.9%** |
| **Nature Machine Intelligence** | Springer Nature | ≈23.9 | 1 区 TOP | 97 / 194 | 50.0% |
| **Patterns** | Cell Press | ≈7–8 | Q1 | 64 / 149 | 43.0% |
| **Data-Centric Engineering** | Cambridge Univ. Press | ≈4–5 | — | 23 / 40 | 57.5% |
| **Natural Resources Research** | Springer（**IAMG** 会刊） | ≈5.0–6.0 | 中科院 2 区 | 66 / 214 | **30.8%** |
| **Mathematical Geosciences** | Springer（**IAMG** 会刊） | ≈3.6 | 中科院 3 区 / JCR Q1 | 34 / 113 | **30.1%** |
| **Computers & Geosciences** | Elsevier | ≈4.4 | 中科院 3 区 | 50 / 174 | **28.7%** |
| **Nature Computational Science** | Springer Nature | ≈12–13 | 1 区 | 49 / 180 | 27.2% |
| **Environmental Modelling & Software** | Elsevier（iEMSs） | ≈4.2 | 2 区 | 101 / 386 | 26.2% |
| **The Innovation** | Cell Press / 中国科协 | ≈33 | 1 区 TOP | 34 / 337 | 10.1% |

> **投稿提示**：A 层是"AI 方法创新"最容易中的地方，但**地质业务深度往往不足**；若要兼顾地质分量，优先 NRR / Mathematical Geosciences / Computers & Geosciences 这类 IAMG 系刊物。

### B 层：地质 / 地球科学核心与新锐刊（发文量集中）

| 期刊 | 出版社 / 主办 | IF（公开值） | 分区 | AI 论文 / 总数 | 占比 |
|---|---|---|---|---|---|
| **Remote Sensing** | MDPI | ≈4.3 | 2 区 | **1,745** / 4,013 | **43.5%** |
| **IEEE Trans. Geoscience and Remote Sensing** | IEEE | ≈8.6 | **1 区 TOP** | 404 / 2,137 | 18.9% |
| **IEEE JSTARS** | IEEE | ≈4.5–5 | 2 区 | 380 / 2,012 | 18.9% |
| **ISPRS J. Photogrammetry & Remote Sensing** | Elsevier（ISPRS） | ≈12 | 1 区 TOP | 100 / 511 | 19.6% |
| **Water Resources Research** | AGU / Wiley | ≈5.4 | 2 区 | 154 / 805 | 19.1% |
| **Journal of Hydrology** | Elsevier | ≈6.0–6.5 | 2 区 | 315 / 2,541 | 12.4% |
| **Hydrology and Earth System Sciences** | EGU（Copernicus） | ≈5.8 | 2 区 | 83 / 392 | 21.2% |
| **Earth System Science Data** | EGU | ≈11 | 1 区 | 106 / 428 | 24.8% |
| **Geoscientific Model Development** | EGU | ≈5.0 | 2 区 | 91 / 528 | 17.2% |
| **Natural Hazards and Earth System Sciences** | EGU | ≈4.5 | 3 区 | 59 / 289 | 20.4% |
| **Journal of Applied Geophysics** | Elsevier | ≈2.0–2.5 | 3 区 | 88 / 533 | 16.5% |
| **Frontiers in Earth Science** | Frontiers | ≈2.0–2.5 | 3–4 区 | 106 / 704 | 15.1% |
| **Earth's Future** | AGU / Wiley | ≈8.0 | 1–2 区 | 55 / 405 | 13.6% |
| **Seismological Research Letters** | SSA | ≈3.0 | 3 区 | 50 / 306 | 16.3% |
| **Earth and Space Science** | AGU / Wiley | ≈3.0 | 3 区 | 55 / 330 | 16.7% |
| **Geophysics** | SEG / GeoScienceWorld | ≈3.0 | 3 区 | 29 / 243 | 11.9% |
| **The Leading Edge** | SEG | ≈1.0–1.5 | 4 区 | 32 / 190 | 16.8% |
| **Interpretation** | SEG | ≈1.0–1.4 | 4 区 | 9 / 38 | 23.7% |
| **Geoscience Frontiers** | Elsevier / 中国地质大学（北京） | ≈8.9（另有来源报 12.7，存疑） | **1 区** | 29 / 204 | 14.2% |
| **Ore Geology Reviews** | Elsevier | ≈3.6 | 2 区 / JCR Q1 | 40 / 658 | 6.1% |
| **Journal of Geochemical Exploration** | Elsevier（AEG） | ≈3.4–4.2 | 2–3 区 | 10 / 239 | 4.2% |
| **Earth-Science Reviews** | Elsevier | ≈10–12 | 1 区 TOP | 11 / 324 | 3.4% |
| **Surveys in Geophysics** | Springer | ≈7.7 | 1–2 区 | 7 / 54 | 13.0% |
| **Engineering Geology** | Elsevier（IAEG 会刊） | ≈8.4 | **1 区 TOP** | 39 / 522 | 7.5% |
| **J. Rock Mechanics and Geotechnical Engineering** | 中科院武汉岩土所 / Elsevier | ≈9–10 | 1 区 | 67 / 921 | 7.3% |
| **Bulletin of Eng. Geology and the Environment** | Springer（IAEG） | ≈4.0 | 2–3 区 | 49 / 841 | 5.8% |
| **Landslides** | Springer（ICL） | ≈7.0 | 2 区 | 12 / 229 | 5.2% |
| **Petroleum Science** | Springer / 中国石油大学 | ≈6.0 | 1–2 区 | 65 / 708 | 9.2% |
| **JGR: Solid Earth** | AGU / Wiley | ≈3.9 | 2 区 | 40 / 647 | 6.2% |
| **Geophysical Research Letters** | AGU / Wiley | ≈4.6 | 2 区 | 144 / 2,175 | 6.6% |
| **Science China Earth Sciences** | 中国科技出版传媒 | ≈5.0 | 2 区 | 14 / 347 | 4.0% |
| **Journal of Earth Science** | 中国地质大学 / Springer | ≈3.5 | 2 区 | 9 / 221 | 4.1% |

### C 层：AI4S 综合性顶刊（高影响力成果出口）

| 期刊 | 出版社 | IF（公开值） | AI 论文 / 总数 | 占比 |
|---|---|---|---|---|
| **Nature Communications** | Springer Nature | ≈15.7 | 680 / 14,222 | 4.8% |
| **PNAS** | 美国科学院 | ≈9.4 | 286 / 4,872 | 5.9% |
| **Science Advances** | AAAS | ≈11.7 | 211 / 3,433 | 6.1% |
| **Science Bulletin** | Elsevier / CAS | ≈18–21 | 36 / 966 | 3.7% |
| **Nature Geoscience** | Springer Nature | ≈15–16 | 2 / 306 | 0.7% |

### 关键结构性结论

```
AI 渗透率梯度：
  地学 AI 专刊      50% – 95%   （AIES 95.5% / JGR-MLC 88.6% / MLST 79.3%）
  > 计算方法·遥感类  15% – 45%   （RS 43.5% / C&G 28.7% / EMS 26.2%）
  > 地质学核心刊      1% – 8%     （OGR 6.1% / JGE 4.2% / EPSL 0.8% / GCA 0.2%）
```

- **绝对发文量最大的出口**：Remote Sensing（1,745 篇）≫ Nature Communications（680）> IEEE TGRS（404）> IEEE JSTARS（380）。
- **传统地质顶刊 AI 化极慢**：Chemical Geology 0.9%、EPSL 0.8%、Geology 2.3%、Tectonophysics 0.6%、Mineralium Deposita 2.3%、GCA 0.2%。→ 说明 AI 地质工作**尚未进入主流岩石学/大地构造话语体系**，既是壁垒也是机会窗口。

---

## 三、近一年主要学术方向与频次统计

### 3.1 应用主题分布（地质主体子集 n = 2,099，互斥）

| 排名 | 方向 | 篇数 | 占比 |
|---|---|---|---|
| 1 | 水文地质、地下水与环境地球化学 AI | 438 | **20.9%** |
| 2 | 地质遥感解译、**岩性识别与智能地质填图** | 318 | **15.2%** |
| 3 | **地震监测**、震源参数与地震学 AI | 295 | **14.1%** |
| 4 | **地质灾害**（滑坡 / 泥石流 / 地面沉降）易发性与风险评价 | 290 | **13.8%** |
| 5 | 地球动力学、深部结构与行星 / 固体地球模拟 | 221 | 10.5% |
| 6 | **矿产资源勘查与成矿预测**（含地球化学异常识别） | 146 | **7.0%** |
| 7 | 地震勘探 / 测井 / 储层地球物理智能处理与反演 | 97 | 4.6% |
| 8 | 地表过程、地貌演化与第四纪 / 沉积环境 | 93 | 4.4% |
| 9 | 地球化学分析、同位素与矿物学大数据 | 86 | 4.1% |
| 10 | 岩石力学、工程地质与岩土智能建模 | 72 | 3.4% |
| 11 | 沉积盆地、层序地层与油气地质 | 43 | 2.0% |

### 3.2 方法维度分布（非互斥，可重叠）

| 方法方向 | 地质主体（n=2,099） | 占比 | 全样本（n=7,166）占比 |
|---|---|---|---|
| 深度学习（CNN / GNN / U-Net / Transformer） | 970 | **46.2%** | 43.0% |
| 传统机器学习（RF / XGBoost / SVM / 集成 / 高斯过程） | 406 | **19.3%** | 15.2% |
| 可解释 AI 与不确定性量化（SHAP / XAI / UQ） | 359 | **17.1%** | 12.1% |
| 地学异构数据融合与多源联合反演 | 165 | 7.9% | 7.0% |
| 自监督 / 弱监督 / 小样本 / 迁移学习 | 150 | 7.1% | 7.8% |
| **物理信息神经网络 / 科学机器学习** | 124 | **5.9%** | 5.2% |
| **地质大模型 / 多模态 / 大语言模型** | 87 | **4.1%** | **9.5%** |
| 生成式模型（扩散 / GAN / 地统计模拟） | 75 | 3.6% | 4.1% |

> **值得注意的错位**：大模型类在全样本占 9.5%，在地质主体子集仅 4.1%。→ **地学大模型目前主要发表在方法类/综合顶刊，向真实地质业务（找矿、填图、灾害决策）渗透仍处于早期**。这正是"地质大模型"方向的机会。

### 3.3 细分子方向（地质主体，非互斥）

| 子方向 | 篇数 | 占比 | 拥挤度判断 |
|---|---|---|---|
| 滑坡易发性 / 位移预测 | 136 | 6.48% | 🔴 红海 |
| 矿产远景预测 / 找矿靶区圈定 | 61 | 2.91% | 🟡 较热 |
| 灾害·地震预警与实时监测 | 60 | 2.86% | 🟡 较热 |
| 地震波 / 剖面重建与去噪 | 51 | 2.43% | 🟡 较热 |
| 地震事件检测 / 相位拾取 / 预警 | 49 | 2.33% | 🟡 较热 |
| **地球化学异常检测与提取** | 28 | 1.33% | 🟢 有机会 |
| **岩性 / 岩相自动分类识别** | 26 | 1.24% | 🟢 有机会 |
| 虚拟测井 / 储层参数（孔渗）预测 | 14 | 0.67% | 🟢 有机会 |
| **断层 / 裂缝 / 构造要素智能识别** | 11 | 0.52% | 🟢 **洼地** |
| **智能地质填图（含露头自动化）** | 8 | 0.38% | 🟢 **洼地** |

**趋势判读 4 条：**

1. **深度学习已是默认范式**（46.2%），单靠"换个 CNN 提精度"不再构成创新。
2. **传统 ML 仍是表格型 / 小样本地学数据的主力**（19.3%）——地质数据天然小样本、异质、标签稀缺。
3. **可解释性与不确定性量化（17.1%）几乎追平传统 ML**，反映地学界对"AI 结论能否用于找矿与灾害决策"的核心焦虑；这是**最容易做出差异化的切口**。
4. **智能地质填图（0.38%）与断层智能识别（0.52%）是明显洼地**，属于高价值、低竞争的未开垦区。

---

## 四、代表性论文（含 DOI）

> 按方向排列，括号内为 Crossref 被引数（截至检索时，近期论文被引偏低属正常）。

### ① 矿产预测与地球化学异常

- *Recent advances and future research directions in deep learning as applied to geochemical mapping*（26）｜2025-11｜*Earth-Science Reviews*｜https://doi.org/10.1016/j.earscirev.2025.105209
- *A semi-supervised approach for mineral prospectivity mapping via weighted positive-unlabeled learning and TPE*｜2025-10｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2025.106783
- *Mineral prospectivity mapping for multi-source geoscience data: A novel unsupervised deep learning method*｜2025-11｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2025.106866
- *Three-dimensional mineral prospectivity mapping using a residual CNN with lightweight attention mechanisms*｜2025-10｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2025.106797
- *Metallogenic prediction based on multi-source remote sensing and machine learning: A case of lithium ore in Jiajika, China*｜2025-10｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2025.106813
- *A metric-learning enhanced variational autoencoder for unsupervised detection of geochemical anomalies in the Hatu gold belt, Xinjiang*｜2025-12｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2025.107017
- *The high-efficiency data integration approach for Pakistan mineral resources using multimodal large language models*｜2026-06｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2026.107294

### ② 地震监测与地震学 AI

- *Integrating artificial intelligence and geophysical insights for earthquake forecasting: A cross-disciplinary review*｜2025-11｜*Earth-Science Reviews*｜https://doi.org/10.1016/j.earscirev.2025.105232
- *A Generative Foundation Model for an All-in-One Seismic Processing Framework*｜2025-11-05｜*Surveys in Geophysics*｜https://doi.org/10.1007/s10712-025-09912-9
- *Real-Time Processing of Distributed Acoustic Sensing Data for Earthquake Monitoring Operations*｜2026-03-27｜*Seismological Research Letters*｜https://doi.org/10.1785/0220250208
- *An ML-Enhanced Earthquake Catalog for the 2024 MW Event*｜2025-12｜*JGR: Solid Earth*｜https://doi.org/10.1029/2025JB032792
- *Earthquake prediction using machine learning perspectives in Himalayan seismic belt and its surroundings*｜2025-11｜*J. Asian Earth Sciences*｜https://doi.org/10.1016/j.jseaes.2025.106764

### ③ 岩性识别与智能地质填图

- *Geological information-driven deep learning for lithology identification from well logs*｜2025-09-25｜*Frontiers in Earth Science*｜https://doi.org/10.3389/feart.2025.1662760
- *A data-driven method for intelligent lithology identification in coal mines based on drilling parameters*｜2025-12｜*Engineering Geology*｜https://doi.org/10.1016/j.enggeo.2025.108448
- *A dual attention-based deep learning model for lithology identification while drilling*｜2026-02｜*J. Rock Mechanics and Geotechnical Engineering*｜https://doi.org/10.1016/j.jrmge.2025.03.051
- *Causal-Graph Lithology Classifier: Synergizing causal inference with GNNs for high-accuracy rock classification in well logs*｜2025-10｜*Marine and Petroleum Geology*｜https://doi.org/10.1016/j.marpetgeo.2025.107452
- *Interpretable regional-scale geological mapping using a contrastive graph attention network for multimodal data fusion*｜2026-02｜*Engineering Geology*｜https://doi.org/10.1016/j.enggeo.2025.108508
- *SCLRAD: Semi-supervised contrastive learning using random replacement of adjacent depths for lithology identification*｜2025-10｜*J. Applied Geophysics*｜https://doi.org/10.1016/j.jappgeo.2025.105795
- *Method of Convolutional Neural Networks for Lithological Classification Using Multisource Remote Sensing Data*｜2025-12-22｜*Remote Sensing*｜https://doi.org/10.3390/rs18010029

### ④ 地质灾害（滑坡 / 沉降）易发性

- *A proposed method for landslide detection based on transfer learning and graph neural network*（64，全场最高）｜2025-11｜*Geoscience Frontiers*｜https://doi.org/10.1016/j.gsf.2025.102171
- *Review article: Deep learning for potential landslide identification: data, models, applications, challenges, and opportunities*（21）｜2026-01-26｜*NHESS*｜https://doi.org/10.5194/nhess-26-487-2026
- *Exploring the dynamic impact of urbanization on landslide susceptibility in Sichuan Province using an explainable XGBoost model*（20）｜2025-10｜*Engineering Geology*｜https://doi.org/10.1016/j.enggeo.2025.108372
- *Region similarity assessment for empowering physics-informed transfer learning-based landslide susceptibility mapping*（18）｜2026-09｜*JRMGE*｜https://doi.org/10.1016/j.jrmge.2025.06.030
- *Uncertainty-aware ensemble learning and dynamic threshold optimization for landslide susceptibility mapping*｜2026-01｜*Computers & Geosciences*｜https://doi.org/10.1016/j.cageo.2025.106042
- *Flood Susceptibility Mapping Using Machine Learning and Geospatial-Sentinel-1 SAR Integration*｜2025-10-17｜*Remote Sensing*｜https://doi.org/10.3390/rs17203471

### ⑤ 物理信息神经网络 / 科学机器学习

- *Physics-informed neural networks enhanced by data augmentation: a novel framework for robust soil moisture estimation*（19）｜2025-12｜*J. of Hydrology*｜https://doi.org/10.1016/j.jhydrol.2025.134320
- *Physics-informed neural network for elastic–plastic mesh-free modelling of tunnelling-induced deformation*｜2025-10-18｜*Acta Geotechnica*｜https://doi.org/10.1007/s11440-025-02788-4
- *An Efficient Multi-Physics GPT-PINN Framework for Predicting Reactive Solute Transport in Parameterized Groundwater Systems*｜2026-02-04｜*GRL*｜https://doi.org/10.1029/2025GL120217
- *EFKAN: A KAN-integrated neural operator for efficient magnetotelluric forward modeling*｜2026-02｜*Computers & Geosciences*｜https://doi.org/10.1016/j.cageo.2025.106052
- *Uncertainty quantification of surrogate models using conformal prediction*｜2026-02-01｜*ML: Science and Technology*｜https://doi.org/10.1088/2632-2153/ae2e7b
- *Ambient Noise Full Waveform Inversion With Neural Operators*｜2025-10-29｜*JGR: Solid Earth*｜https://doi.org/10.1029/2025JB031624
- *GeoFWI: A Large Velocity Model Data Set for Benchmarking FWI Using Deep Learning*｜2026-03-06｜*JGR: Machine Learning and Computation*｜https://doi.org/10.1029/2025JH001037

### ⑥ 地质大模型 / 多模态 / LLM

- *Prithvi-EO-2.0: A Versatile Multitemporal Foundation Model for Earth Observation Applications*（66）｜2026｜*IEEE TGRS*｜https://doi.org/10.1109/TGRS.2025.3642610
- *A Billion-Scale Foundation Model for Remote Sensing Images*（85）｜2026｜*IEEE JSTARS*｜https://doi.org/10.1109/JSTARS.2025.3631311
- *A Generative Foundation Model for an All-in-One Seismic Processing Framework*｜2025-11-05｜*Surveys in Geophysics*｜https://doi.org/10.1007/s10712-025-09912-9
- *Generative AI with prompt engineering ... Enhancing predictive slope stability modelling*｜2025-11｜*Geoscience Frontiers*｜https://doi.org/10.1016/j.gsf.2025.102163
- *The Destination Earth digital twin for climate change adaptation*（13）｜2026-04-14｜*GMD*｜https://doi.org/10.5194/gmd-19-2821-2026
- *Using multimodal large language models for mineral resources data integration*｜2026-06｜*Ore Geology Reviews*｜https://doi.org/10.1016/j.oregeorev.2026.107294
- *On the foundations of Earth foundation models*｜2026｜*Communications Earth & Environment*｜https://doi.org/10.1038/s43247-025-03127-x（见 `文献清单_地质+AI.md` N8）

### ⑦ 水文地质与环境地球化学

- *Using unsupervised ML and PMF models to drive groundwater chemistry and associated health risks in a coal-mining rural region*（43）｜2025-11｜*J. of Hydrology*｜https://doi.org/10.1016/j.jhydrol.2025.133691
- *Identification of Key Factors Driving Dissolved Oxygen in Riparian Aquifers Through DL-Assisted Global Sensitivity Analysis*｜2026-01-30｜*Water Resources Research*｜https://doi.org/10.1029/2025WR041884
- *From RNNs to Transformers: benchmarking deep learning architectures for hydrologic prediction*｜2025-12-01｜*HESS*｜https://doi.org/10.5194/hess-29-6811-2025
- *Unveiling the limits of deep learning models in hydrological extrapolation tasks*（41）｜2025-11-03｜*HESS*｜https://doi.org/10.5194/hess-29-5871-2025

---

## 五、选题与投稿建议（基于统计的直接推论）

| 目标 | 建议 |
|---|---|
| 想做**高价值低竞争**方向 | 智能地质填图（0.38%）、断层/裂缝智能识别（0.52%）、虚拟测井与储层参数（0.67%） |
| 想在**红海中差异化** | 滑坡易发性（6.48%）已高度拥挤 → 必须叠加**可解释性 / 不确定性量化 / 物理约束**才有区分度 |
| 想投**地质主体认可度高**的刊 | Geoscience Frontiers、Engineering Geology、JRMGE、Ore Geology Reviews、NRR（既认 AI 又认地质） |
| 想做**大模型**且要地质落地 | 切入点：矿产多模态数据整合（已有 OGR 案例）、地震处理一体化工件流（Surveys in Geophysics）、地球基础模型评测基准 |
| 想提高**方法可信度** | 可解释 AI + UQ 占比已达 17.1%，几乎是审稿默认要求；PINN / 神经算子（5.9%）是"物理约束"的通行写法 |

---

## 六、方法局限（务必知悉）

1. **召回下限问题**：60,568 篇中**仅 27,095 篇（45%）在 Crossref 中有摘要存档**（Elsevier / Springer 部分刊物不提供）。在"有摘要"样本中，题+摘判读命中率 16.9%，仅题名判读命中率 7.7%，比值 **2.20**。据此校正，**窗口内真实 AI 相关论文约 1.06 万篇量级**（实测 7,166 篇为保守下限），真实渗透率约 17% 而非 11.8%。→ **占比结构不受影响，绝对数应理解为下限**。
2. **分类为规则式判读**：主题为互斥（加权投票 + 优先级仲裁），方法与子方向非互斥重复计数，故三者之和不等于总量。
3. **未覆盖来源**：未纳入 CNKI / 万方中文期刊、arXiv / SSRN 预印本、会议论文（SEG / AAPG / EGU 年会），因此**未统计国内中文地学期刊的 AI 工作**。
4. **影响因子口径**：第三方渠道存在版本差异（部分为 2025 发布版、部分为 2026 更新版），冲突值已标注"存疑"。
5. **时效性**：2026 年 9 月为不完整月份，且部分刊物存在 online-first 与正式刊期的时间差。

---

## 七、本目录结构

```
地质+ai/
├── 汇报.md                                   # （待填）
└── docs/
    ├── 文献清单_地质+AI.md                    # 单篇精读清单（综述 9 + 近期研究 9）
    ├── 感知型基础模型_方向项目速查.md          # 基础模型 6 模块 × 7 方向速查
    ├── 期刊与近一年研究态势_地质+AI.md         # ← 本文档（态势普查 / 投稿与选题参考）
    ├── 综述/                                 # PDF
    └── 近期研究/                             # PDF
```

**一句话总结**：近一年地质 AI 呈现「**方法侧深度学习已饱和、可解释与物理约束快速上升、大模型尚未真正落地地质业务、智能填图与断层识别仍是洼地**」的格局；发文主战场在 Remote Sensing 与 IEEE 遥感系，而地质业务深度最高的出口集中在 IAMG 系（NRR / Mathematical Geosciences）与 Elsevier 地质工程系（Engineering Geology / JRMGE / OGR）。
