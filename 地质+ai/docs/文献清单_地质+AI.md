# 地质 + AI（AI4S）文献清单

> 整理范围：人工智能/机器学习/深度学习在地球科学与地质领域的应用
> 覆盖方向：地球科学AI总论、地震学与地震预测、矿产勘查与远景预测（MPM）、遥感地质与岩性填图、岩石矿物智能识别、地震资料处理与成像、地球/遥感基础模型
> 整理日期：2026-09-11
> 本地目录：`docs\综述\`（综述类）、`docs\近期研究\`（2024–2026 近期高影响力研究）

说明：
- 「已下载」表示 PDF 已保存到本地对应分类文件夹；「链接获取」表示受出版商订阅/反爬限制未能自动下载，清单中给出了 DOI 与正文地址，可在校园网/机构账号下获取。
- 开放获取（Open Access）论文已优先选取。

---

## 一、综述（Reviews）

### R1. Artificial intelligence for geoscience: Progress, challenges, and perspectives
- **中文题名**：人工智能在地球科学中的应用：进展、挑战与展望
- **作者**：Tianjie Zhao, Sheng Wang, Chaojun Ouyang, Min Chen, … , Jiancheng Shi, Lizhe Wang（共 51 位作者，多单位合作）
- **年份**：2024
- **期刊**：*The Innovation*, 5(5): 100691（Cell Press / Elsevier）
- **核心方法/内容**：系统综述 AI 在地球科学全领域的进展与挑战，涵盖深度学习、遥感大模型、物理约束与可解释 AI、知识图谱、多模态融合；从「数据—模型—算力—可信度」角度提出发展方向。被引约 299 次（Crossref），是本领域最具代表性的总论性综述之一。
- **获取链接**：DOI https://doi.org/10.1016/j.xinn.2024.100691 ｜ 正文 https://www.cell.com/innovation/fulltext/S2666-6758(24)00129-2
- **本地文件**：`综述\2024_TheInnovation_人工智能地学应用进展挑战展望.pdf` ✅已下载

### R2. Current state and future directions for deep learning based automatic seismic fault interpretation: A systematic review
- **中文题名**：基于深度学习的自动化地震断层解释：现状与未来方向（系统综述）
- **作者**：Yu An, Haiwen Du, Siteng Ma, Yingjie Niu, Dairui Liu, Jing Wang, Yuhan Du, Conrad Childs, John Walsh, Ruihai Dong
- **年份**：2023
- **期刊**：*Earth-Science Reviews*, 243: 104509（Elsevier，地学顶级综述期刊）
- **核心方法/内容**：系统回顾 2012–2022 年基于深度学习的自动化地震断层解释文献（CNN、U-Net、GAN、Transformer、多尺度与多任务学习等），提出研究问题框架与未来方向。被引约 54 次。
- **获取链接**：DOI https://doi.org/10.1016/j.earscirev.2023.104509
- **获取状态**：链接获取（Elsevier 订阅；建议校园网访问）

### R3. A Review of Mineral Prospectivity Mapping Using Deep Learning
- **中文题名**：基于深度学习的矿产远景预测综述
- **作者**：Kang Sun, Yansi Chen, Guoshuai Geng, Zongyue Lu, Wei Zhang, Zhihong Song, Jiyun Guan, Yang Zhao, Zhaonian Zhang
- **年份**：2024
- **期刊**：*Minerals*, 14(10): 1021（MDPI，CC BY 开放获取）
- **核心方法/内容**：回顾深度学习（CNN/RNN/自编码器/GAN 等）在矿产远景预测（MPM）中的应用，重点剖析数据预处理、数据增强、超参数调优、精度评价四大挑战并给出建议。被引约 48 次。
- **获取链接**：DOI https://doi.org/10.3390/min14101021 ｜ PDF https://www.mdpi.com/2075-163X/14/10/1021/pdf
- **本地文件**：`综述\2024_Minerals_基于深度学习的矿产远景预测综述.pdf` ✅已下载

### R4. Recent advances in earthquake seismology using machine learning
- **中文题名**：机器学习在地震学中的近期进展
- **作者**：Hirokazu Kubo, Makoto Naoi, Masayuki Kano
- **年份**：2024
- **期刊**：*Earth, Planets and Space*, 76: 36（SpringerOpen，CC BY 开放获取）
- **核心方法/内容**：从四方面综述 ML 进展：①地震目录构建（事件检测/分类、震相拾取、相似波形搜索、震源机制）②地震活动性分析 ③地震动预测 ④地壳形变分析；并讨论不平衡地震动数据的影响与应对。
- **获取链接**：DOI https://doi.org/10.1186/s40623-024-01982-0 ｜ PDF https://earth-planets-space.springeropen.com/counter/pdf/10.1186/s40623-024-01982-0
- **本地文件**：`综述\2024_EPS_机器学习地震学进展综述.pdf` ✅已下载

### R5. When geoscience meets generative AI and large language models: Foundations, trends, and future challenges
- **中文题名**：当地球科学遇生成式 AI 与大语言模型：基础、趋势与未来挑战
- **作者**：Amer Hadid, Tanujit Chakraborty, Daniel Busby
- **年份**：2024
- **期刊**：*Expert Systems*, 41(8): e13654（Wiley）；预印本 arXiv:2402.03349
- **核心方法/内容**：综述生成式 AI（GAN、物理信息神经网络 PINNs、GPT 类模型）在地学中的应用：数据生成/增强、超分辨率、全色锐化、去雾、修复、地表变化监测；讨论物理可解释性、可信度与滥用风险。
- **获取链接**：DOI https://doi.org/10.1111/exsy.13654 ｜ 预印本 https://arxiv.org/abs/2402.03349
- **本地文件**：`综述\2024_ExpertSystems_地球科学生成式AI与大模型综述.pdf` ✅已下载

### R6. Machine Learning-Based Mapping for Mineral Exploration
- **中文题名**：面向矿产勘查的机器学习填图
- **作者**：Renguang Zuo, Emmanuel John M. Carranza
- **年份**：2023
- **期刊**：*Mathematical Geosciences*, 55: 891–898（Springer）
- **核心方法/内容**：简要综述矿产勘查中的前沿 ML 算法：随机森林（RF）、卷积神经网络（CNN）、图卷积网络（GCN），及其在找矿预测填图中的应用与展望（Zuo 团队为该方向权威）。
- **获取链接**：DOI https://doi.org/10.1007/s11004-023-10097-3
- **本地文件**：`综述\2023_MathGeosci_机器学习矿产勘查填图.pdf` ✅已下载

### R7. Deep Learning in Earthquake Engineering: A Comprehensive Review
- **中文题名**：深度学习在地震工程中的应用：综述
- **作者**：Yazhou Xie
- **年份**：2024
- **期刊**：arXiv:2405.09021（后发表于 *ASCE-ASME Journal of Risk and Uncertainty in Engineering Systems*, 2025）
- **核心方法/内容**：综述 DL 在地震工程中的典型应用：结构地震响应预测、结构损伤/健康监测识别、震害评估、地震动记录选取与合成。
- **获取链接**：https://arxiv.org/abs/2405.09021
- **本地文件**：`综述\2024_arXiv_深度学习地震工程综述.pdf` ✅已下载

### R8. 基于深度学习的岩石矿物智能识别研究进展与发展趋势
- **作者**：见期刊原文
- **年份**：2025
- **期刊**：*成都理工大学学报（自然科学版）*, 52(1)
- **核心方法/内容**：系统分析基于深度学习的岩石矿物图像识别最新进展，重点讨论矿物重构、矿物分类、矿物分割三大任务及数据集与网络结构选择。
- **获取链接**：DOI https://doi.org/10.3969/j.issn.1671-9727.2025.01.05
- **获取状态**：链接获取（中文期刊，建议经 CNKI / 期刊官网下载）

### R9. Advances on Multimodal Remote Sensing Foundation Models for Earth Observation Downstream Tasks: A Survey
- **中文题名**：面向地球观测下游任务的多模态遥感基础模型研究进展综述
- **作者**：Guoqing Zhou, Lihuang Qian, Paolo Gamba
- **年份**：2025
- **期刊**：*Remote Sensing*, 17(21): 3532（MDPI，CC BY 开放获取）
- **核心方法/内容**：综述「视觉—X」（语言、音频、位置）多模态遥感基础模型的关键技术、多模态预训练数据集，并按骨干网络与跨模态交互方式分类；总结高质量数据稀缺、跨任务泛化弱、缺统一评测、安全性不足等五大挑战。被引约 18 次。
- **获取链接**：DOI https://doi.org/10.3390/rs17213532 ｜ PDF https://www.mdpi.com/2072-4292/17/21/3532/pdf
- **本地文件**：`综述\2025_RemoteSensing_多模态遥感基础模型综述.pdf` ✅已下载

---

## 二、近期研究（2024–2026 高影响力）

### N1. Machine learning predicts meter-scale laboratory earthquakes
- **中文题名**：机器学习预测米尺度实验室地震
- **作者**：Reiju Norisugi, Yoshihiro Kaneko, Bertrand Rouet-Leduc
- **年份**：2025
- **期刊**：*Nature Communications*, 16: 9593（Nature 系列，CC BY-NC-ND）
- **核心方法/内容**：对米尺度岩石摩擦实验的声发射（AE）目录构建「事件网络表示」，用随机森林/深度学习在主震前数十秒至毫秒预测破坏时间（类比天然地震的数十月至数十年）；结合速率—状态摩擦数值模型解释其追踪的是蠕滑区剪应力演化。
- **获取链接**：DOI https://doi.org/10.1038/s41467-025-64542-4 ｜ PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC12575727
- **本地文件**：`近期研究\2025_NatComms_机器学习预测米尺度实验室地震.pdf` ✅已下载

### N2. Generalizable deep learning models for predicting laboratory earthquakes
- **中文题名**：用于预测实验室地震的可泛化深度学习模型
- **作者**：Chonglang Wang, Kaiwen Xia, Wei Yao, Chris Marone
- **年份**：2025
- **期刊**：*Communications Earth & Environment*, 6: 219（Nature Portfolio，CC BY-NC-ND）
- **核心方法/内容**：提出 Decoder-only 时序卷积网络（TCN）+ 迁移学习策略（冻结约 97% 解码器、仅微调回归头），实现跨双轴与双直剪（DDS）实验构型、不同滑动速率下的破坏时间与剪应力预测。
- **获取链接**：DOI https://doi.org/10.1038/s43247-025-02200-9
- **本地文件**：`近期研究\2025_CommsEarthEnv_可泛化深度学习预测实验室地震.pdf` ✅已下载

### N3. Machine Learning Predicts Earthquakes in the Continuum Model of a Rate-And-State Fault With Frictional Heterogeneities
- **中文题名**：机器学习在含摩擦非均质性的速率—状态断层连续模型中预测地震
- **作者**：Reiju Norisugi, Yoshihiro Kaneko, Bertrand Rouet-Leduc
- **年份**：2024
- **期刊**：*Geophysical Research Letters*, 51(9): e2024GL108655（AGU）
- **核心方法/内容**：对速率—状态摩擦断层连续模型生成的合成地震目录，构造「多重网络表示」输入特征训练 ML，模型可在数十年至数分钟尺度预测距主震时间，为实验室地震可预测性提供物理解释。
- **获取链接**：DOI https://doi.org/10.1029/2024GL108655
- **本地文件**：`近期研究\2024_GRL_机器学习预测速率状态断层地震.pdf` ✅已下载

### N4. Deep learning for high-resolution seismic imaging
- **中文题名**：面向高分辨率地震成像的深度学习
- **作者**：Liyun Ma, Liguo Han, Qiang Feng
- **年份**：2024
- **期刊**：*Scientific Reports*, 14（Nature Portfolio，CC BY）
- **核心方法/内容**：提出 Transformer 与 CNN 结合、并用自适应空间特征融合（ASFF）增强的框架，将地震数据直接映射为反射率模型，实现无需后处理的高分辨率成像；以 RMSE、相关系数、SSIM 评价并做噪声鲁棒性实验。
- **获取链接**：DOI https://doi.org/10.1038/s41598-024-61251-8 ｜ PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC11070416
- **本地文件**：`近期研究\2024_SciRep_深度学习高分辨率地震成像.pdf` ✅已下载

### N5. A Novel Sample Generation Method for Deep Learning Lithological Mapping with Airborne TASI Hyperspectral Data in Northern Liuyuan, Gansu, China
- **中文题名**：基于机载 TASI 高光谱数据的新型样本生成方法用于深度学习岩性填图（中国甘肃北柳园）
- **作者**：Huize Liu, Ke Wu, Dandan Zhou, Ying Xu
- **年份**：2024
- **期刊**：*Remote Sensing*, 16(15): 2852（MDPI，CC BY）
- **核心方法/内容**：提出「多岩性光谱样本选择」（MLS3）样本生成方法以缓解高质量样本稀缺；联合 2D-CNN、HybridSN、MSRN、SSRN、SPRN 五种模型做高光谱岩性填图，SPRN 精度达 84.03%，总体精度较其他采样方法提升 2.25%–6.96%。
- **获取链接**：DOI https://doi.org/10.3390/rs16152852 ｜ PDF https://www.mdpi.com/2072-4292/16/15/2852/pdf
- **本地文件**：`近期研究\2024_RemoteSensing_深度学习岩性填图样本生成.pdf` ✅已下载

### N6. Ensemble machine learning strategies for mineral prospectivity mapping under data scarcity
- **中文题名**：数据稀缺条件下的矿产远景预测集成机器学习策略
- **作者**：Poorya Amirajlo, Hossein Hassani, Amin Beiranvand Pour, Narges Habibkhah
- **年份**：2026
- **期刊**：*Scientific Reports*, 16（Nature Portfolio）
- **核心方法/内容**：面向标记数据稀缺与类别不平衡问题，评估 LightGBM+AdaBoost、SVM+高斯朴素贝叶斯两种集成配置，比较网格/随机/贝叶斯三种调参策略与 SMOTE；强调概率校准与可复现性优于边际精度提升（AUC 0.90–0.95，伊朗 Dehaq 铅锌矿区）。
- **获取链接**：DOI https://doi.org/10.1038/s41598-026-40125-1 ｜ PMC https://pmc.ncbi.nlm.nih.gov/articles/PMC12996581
- **本地文件**：`近期研究\2026_SciRep_数据稀缺下集成机器学习矿产预测.pdf` ✅已下载

### N7. An explainable semi-supervised deep learning framework for mineral prospectivity mapping: DEEP-SEAM v1.0
- **中文题名**：面向矿产远景预测的可解释半监督深度学习框架 DEEP-SEAM v1.0
- **作者**：Zijing Luo, Ehsan Farahbakhsh, Stephen Hore, R. Dietmar Müller
- **年份**：2026
- **期刊**：*Geoscientific Model Development (GMD)*, 19: 2593（Copernicus，开放获取；预印本 10.5194/egusphere-2025-3283）
- **核心方法/内容**：面向稀土（REE）矿产勘查，提出半监督异常检测深度模型 DevNet，利用少量正样本+大量未标注样本建立多源勘查数据到矿化概率的映射；引入 SHAP 事后解释提升可解释性（南澳北 Curnamona 省）。
- **获取链接**：DOI https://doi.org/10.5194/gmd-19-2593-2026 ｜ PDF https://gmd.copernicus.org/articles/19/2593/2026/gmd-19-2593-2026.pdf
- **本地文件**：`近期研究\2026_GMD_DEEP-SEAM可解释半监督矿产预测.pdf` ✅已下载

### N8. On the foundations of Earth foundation models
- **中文题名**：论地球基础模型的构建基础
- **作者**：Xiaoxia Zhu, Zhitong Xiong, Yi Wang, Adam J. Stewart, Konrad Heidler, Yuanyuan Wang, Zhenghang Yuan, Thomas Dujardin, Qingsong Xu, Yilei Shi
- **年份**：2026
- **期刊**：*Communications Earth & Environment*, 7（Nature Portfolio，CC BY）
- **核心方法/内容**：提出理想地球基础模型应具备的 11 项关键特征，讨论能效自适应微调、对抗防御、可解释性等新兴方向，并给出模型有效使用建议与标准化评估标准。
- **获取链接**：DOI https://doi.org/10.1038/s43247-025-03127-x
- **本地文件**：`近期研究\2026_CommsEarthEnv_地球基础模型十一个重要特征.pdf` ✅已下载

### N9. Probabilistic and Alarm-Based Evaluation of a b-Value-Driven Deep Learning Earthquake Forecasting Model
- **中文题名**：基于 b 值的深度学习地震预报模型的概率与告警式评估
- **作者**：Kohler, Li 等（详见 arXiv 原文）
- **年份**：2026
- **期刊**：arXiv:2603.03079（预印本）
- **核心方法/内容**：以概率与告警（alarm-based）双指标体系，评估利用 b 值时空演化信息的深度学习地震预报模型；表明 b 值时空变化包含有限但持续的预报信号，为预报模型的严格评估提供范式。
- **获取链接**：https://arxiv.org/abs/2603.03079
- **本地文件**：`近期研究\2026_arXiv_b值深度学习地震预报概率评估.pdf` ✅已下载

---

## 三、研究方向覆盖对照

| 研究方向 | 综述 | 近期研究 |
|---|---|---|
| AI4S / 地学总论 | R1、R5、R9 | N8 |
| 地震学与地震预测 | R4、R7 | N1、N2、N3、N9 |
| 矿产勘查与远景预测（MPM） | R3、R6 | N6、N7 |
| 遥感地质 / 岩性填图 | R3、R9 | N5 |
| 岩石矿物智能识别 | R8 | N5 |
| 地震资料处理 / 成像 / 断层解释 | R2、R7 | N4 |
| 基础模型 / 大模型 | R1、R5、R9 | N8 |

---

## 四、本地目录结构

```
docs/
├── 文献清单_地质+AI.md                # 本清单
├── 综述/                              # 综述类（7 篇已下载 PDF）
│   ├── 2023_MathGeosci_机器学习矿产勘查填图.pdf
│   ├── 2024_arXiv_深度学习地震工程综述.pdf
│   ├── 2024_EPS_机器学习地震学进展综述.pdf
│   ├── 2024_ExpertSystems_地球科学生成式AI与大模型综述.pdf
│   ├── 2024_Minerals_基于深度学习的矿产远景预测综述.pdf
│   ├── 2024_TheInnovation_人工智能地学应用进展挑战展望.pdf
│   └── 2025_RemoteSensing_多模态遥感基础模型综述.pdf
└── 近期研究/                          # 2024–2026 高影响力研究（9 篇已下载 PDF）
    ├── 2024_GRL_机器学习预测速率状态断层地震.pdf
    ├── 2024_RemoteSensing_深度学习岩性填图样本生成.pdf
    ├── 2024_SciRep_深度学习高分辨率地震成像.pdf
    ├── 2025_CommsEarthEnv_可泛化深度学习预测实验室地震.pdf
    ├── 2025_NatComms_机器学习预测米尺度实验室地震.pdf
    ├── 2026_arXiv_b值深度学习地震预报概率评估.pdf
    ├── 2026_CommsEarthEnv_地球基础模型十一个重要特征.pdf
    ├── 2026_GMD_DEEP-SEAM可解释半监督矿产预测.pdf
    └── 2026_SciRep_数据稀缺下集成机器学习矿产预测.pdf
```

**小结**：共整理 18 篇文献（综述 9 篇、近期研究 9 篇），其中 16 篇已成功下载全文 PDF（R2、R8 因订阅/中文库限制仅提供链接）。
