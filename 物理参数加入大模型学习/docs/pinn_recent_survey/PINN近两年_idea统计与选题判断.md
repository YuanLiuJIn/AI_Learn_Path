# PINN 近两年期刊论文介绍：解决什么问题、核心 idea 与尚存在的问题

检索区间：2024-09-27—2026-09-27。检索于 2026-09-27 开始，整理于 2026-09-28 完成；沿用检索时冻结的截止日。

本次按原有 24 篇样本重新组织，不新增文献：正文介绍 23 篇期刊论文，原样本中的 1 篇 AAAI 会议论文单列附录。保留原编号，便于与原始记录对应。

每篇统一回答三个问题：①解决什么问题；②核心 idea 是什么，并交代实际验证；③尚存在的问题。第三项区分已有证据的适用边界与本整理者提出的待验证问题，不能一概理解为作者承认的缺陷或已经证实的失败。

## 统计口径与证据边界

使用 Crossref 公开接口，12 组方向关键词，每组取相关性前 12 条。得到 144 条记录、110 个唯一 DOI，其中 44 篇有摘要。人工从可读摘要中选择 24 篇相关研究，覆盖方法改进与实际问题。原始记录和人工编码均保存在本目录。
这是一份有明确偏差的代表性样本盘点，不是系统综述、全量计量或随机抽样。定向关键词、相关性排序、摘要开放情况会影响类别占比；不能将以下百分比当作全领域热度。多数会议、arXiv 工作及无摘要的期刊论文尚未纳入内容编码。Crossref 的类型标记也不完全可靠，包含被标为 journal-article 的 AAAI 会议记录。
日期优先用 published-online，无则用 published；不是首次 arXiv 提交时间。刊出在此区间内不代表 idea 首创于此区间。2024 年仅有一个季度且检索偏向较新结果，不能据年份数推断增长速度。
24 篇均已阅读公开摘要；另对纹影、WF-PINNs 的出版商全文中方法及验证段落做了抽查；hidden physics 页面可读摘要，不能算全文精读。MDPI 三个代表页面返回 403，相关条目仅依据登记摘要。所有数值均为作者报告，未独立复现；未据本次检索核验仓库可用性。

## 样本统计

| 主类别 | 篇数 | 样本占比 |
|---|---:|---:|
| 优化与预条件 | 1 | 4.2% |
| 采样与权重 | 3 | 12.5% |
| 结构与物理表征 | 3 | 12.5% |
| 区域分解 | 3 | 12.5% |
| 物理可行性与约束 | 5 | 20.8% |
| 时间因果训练 | 1 | 4.2% |
| 迁移与跨工况 | 2 | 8.3% |
| 实测反演与数据融合 | 3 | 12.5% |
| 不确定性 | 2 | 8.3% |
| 评测与成本核算 | 1 | 4.2% |

年份分布：{2024: 1, 2025: 7, 2026: 16}。
验证证据：摘要明确包含真实测量/实验验证 7 篇；其余 17 篇归为数值/合成验证，或摘要仅明确该类验证。没有实测证据不等于已证明全文绝无实验。
每篇只计一个主类别，防止重复计数。许多工作跨多个方向，例如电池硬约束也涉及参数反演，SPIKAN 也涉及效率；主类是本次人工编码决定，不是出版商标签。

## 期刊论文逐篇清单

以下“解决什么问题”表示论文针对的困难，不代表已在所有场景中解决。“尚存在的问题”包含证据边界与整理者的研究判断；具体实验范围见逐篇介绍。

| 原编号 | 发表时间与期刊 | 论文 | 解决什么问题 | 核心 idea：具体怎么做 | 尚存在的问题 | 验证证据 |
|---:|---|---|---|---|---|---|
| 01 | 2025-9-11；Physics of Fluids | [A matrix preconditioning framework for physics-informed neural networks based on the adjoint method](https://doi.org/10.1063/5.0285013) | 多尺度和高雷诺数问题中，PDE 系统病态使卷积式 PINN 收敛缓慢甚至失败。 | 用自动微分和矩阵染色求 PDE Jacobian，经不完全 LU 分解构造预条件器，缩放残差；伴随法处理梯度。 | 属于卷积式 PICNN 框架；要把预条件器构建时间和内存计入，不能只比较迭代数。 | 数值/合成 |
| 03 | 2026-4-7；Machine Learning: Science and Technology | [Self-adaptive weighting and sampling for physics-informed neural networks](https://doi.org/10.1088/2632-2153/ae556e) | 快速变化区域配点不足，各点收敛速度不均；只改采样或只改权重效果不稳定。 | 联合自适应采样和点权重：关注解快速变化区域，同时平衡各点的收敛速度。 | 需要同预算消融：只采样、只加权、联合、固定基线；论文摘要未证明所有 PDE 均有效。 | 数值/合成 |
| 04 | 2026-1-6；Physica Scripta | [Antiderivative-enhanced adaptive sampling algorithm for physics-informed neural networks](https://doi.org/10.1088/1402-4896/ae30b5) | 只依靠残差选点难以兼顾导数表达，陡梯度及高阶导数相关问题难学。 | 残差驱动采样结合反导数近似层，改善函数及导数的表达。 | 同时改变结构与采样，必须用消融拆分贡献；这些不是工程实测。 | 数值/合成 |
| 05 | 2025-9-22；Machine Learning: Science and Technology | [SPIKANs: separable physics-informed Kolmogorov–Arnold networks](https://doi.org/10.1088/2632-2153/ae05af) | 高维问题的配点规模迅速增长，普通 PIKAN 训练速度慢、计算成本高。 | SPIKANs 用分离变量思路，每个维度一个 KAN，降低高维配点训练开销。 | KAN 本身不是物理定律；低秩或可分离假设是否适合目标问题需验证。 | 数值/合成 |
| 06 | 2026-8-24；Physics of Fluids | [Physics-informed graph Laplacian-augmented Kolmogorov–Arnold networks](https://doi.org/10.1063/5.0341290) | 不规则血管几何中，几何表示、神经近似与 PDE 残差离散难以协调。 | 统一有限元表示中的图连接、KAN 系数参数化和 Galerkin 残差。 | 血管几何测试不等于临床验证；常规 PINN 在部分几何上的误差更低，不能说全面胜出。 | 数值/合成 |
| 07 | 2026-5-19；International Journal of Structural Stability and Dynamics | [Modal Physics-Informed Neural Networks for Forward and Inverse Structural Vibration Problems](https://doi.org/10.1142/s021945542750355x) | 结构振动具有高频响应和高维状态，普通 PINN 受谱偏置影响且训练开销大。 | 模态分解降低结构动力学维度，结合 Fourier 特征处理高频响应。 | 经典模态假设对强非线性、接触问题可能不足；误差和加速限于所测配置。 | 包含实测 |
| 08 | 2025-5-4；Mathematics | [Progressive Domain Decomposition for Efficient Training of Physics-Informed Neural Network](https://doi.org/10.3390/math13091515) | 不同区域学习难度不同，统一训练会在已学好的区域继续消耗计算资源。 | 根据残差动态分区，逐步训练并保存已达到要求的局部模型。 | 分区和冻结阈值也是超参数，需检查界面误差和总体耗时。 | 数值/合成 |
| 09 | 2026-6-25；Communications in Computational Physics | [ADD-PINN: Adaptive Domain Decomposition Based Physics Informed Neural Networks via Spatial Clustering](https://doi.org/10.4208/cicp.oa-2025-0132) | 人工分区依赖经验，子域接口条件复杂，固定分区难适应训练中的误差分布。 | 空间聚类自动分块，梯度信息调节跨域交换，用图优化处理子域调整。 | 接口和调度有额外成本；不应只和未经调优的单网络比较。 | 数值/合成 |
| 10 | 2026-7-17；Machine Learning: Science and Technology | [AB-PINNs: adaptive-basis physics-informed neural networks for residual-driven domain decomposition](https://doi.org/10.1088/2632-2153/ae8638) | 单网络或静态分区难以同时表达全局大尺度结构与局部细尺度特征。 | 全局网络学大尺度、局部网络学细节；子域可移动，并在高残差区新增子域。 | 类似自适应网格细化的资源分配；需比较经典 AMR 或成熟数值求解器。 | 数值/合成 |
| 11 | 2026-5-21；World Electric Vehicle Journal | [Physics-Informed Neural Networks with Hard Constraints for Axial Temperature Distribution Estimation of Lithium-Ion Batteries](https://doi.org/10.3390/wevj17050275) | 集总模型忽略电池内部温度梯度，软边界约束难准确满足换热边界。 | 用距离函数将 Robin 边界嵌入解空间，结合电热耦合残差。 | 硬约束仅针对指定数学边界；错误换热系数或热模型仍可造成系统误差。 | 包含实测 |
| 12 | 2026-9-14；ACS Omega | [Physics-Informed Neural Networks with Mass Conservation Constraints for Predicting Particle Sedimentation in Non-Newtonian Suspensions](https://doi.org/10.1021/acsomega.6c08067) | 沉降监测点稀疏，长时间外推易出现固相总量漂移，早期快速变化也难捕捉。 | 局部沉降 PDE 加全局质量约束；逐渐提高守恒权重，并用对数时间映射解析早期快速变化。 | 留一工况不能直接当作任意参数 OOD；经验方程与实际工况适配仍需检查。 | 包含实测 |
| 13 | 2026-7-11；Communications Physics | [Enforcing hidden physics in physics-informed neural networks](https://doi.org/10.1038/s42005-026-02743-z) | 仅拟合 PDE 残差仍可能产生违反不可逆过程方向性的非物理解。 | 给已有 PDE 残差补上不可逆性正则，排除低残差但物理不合理的解。 | 这是补充已知物理先验，不是从数据自动发现新规律；不应对可逆过程错误加入单调性。 | 数值/合成 |
| 14 | 2026-9-22；Machine Learning: Science and Technology | [Two-stage projection physics-informed neural networks for preserving conservation laws](https://doi.org/10.1088/2632-2153/aeab20) | 局部 PDE 残差较小，仍可能出现全局不变量漂移。 | 先训练普通 PINN，推理时将输出投影到选定不变量流形。 | 摘要明确：守恒违反显著减少但预测误差变化很小；未建立长期稳定性或一般性。 | 数值/合成 |
| 15 | 2025-11-18；Scientific Reports | [WF-PINNs: solving forward and inverse problems of burgers equation with steep gradients using weak-form physics-informed neural networks](https://doi.org/10.1038/s41598-025-24427-4) | Burgers 陡梯度或激波附近训练不稳定，初始条件与黏度反演困难。 | 弱式积分残差、熵条件和逆问题双网络一致性联合训练。 | 弱式、熵方法并非近两年才出现；黏性/无黏性问题的熵式须逐式核对，不能直接照搬。 | 数值/合成 |
| 16 | 2025-9-30；International Journal of Wavelets, Multiresolution and Information Processing | [Cross-time causal physics-informed neural networks for dynamic time-dependent problems](https://doi.org/10.1142/s0219691325500316) | 时间分区内部仍可能忽略先后依赖，跨段解的衔接与一致性难以维持。 | 重叠时间分区；区内软因果权重，区间传递先前解，重叠区加一致性损失。 | 这里的因果指时间推进依赖，不是干预因果推断；需测跨段误差累积。 | 数值/合成 |
| 17 | 2026-3-2；Geophysical Prospecting | [Multichannel Wavefield Reconstruction With Physics‐Informed Neural Networks and Transfer Learning](https://doi.org/10.1111/1365-2478.70149) | 地震观测道稀疏且含噪；对每个炮集从零训练重建网络成本过高。 | 先训练一个炮集，再微调到相邻炮集，复用波场重建网络。 | 这是特定数据集上的迁移结果，不是任意介质泛化；需计首个模型训练成本。 | 包含实测 |
| 18 | 2026-5-26；Mathematics | [Physics-Informed Neural Networks with Transfer Learning for Tunnel Seepage Prediction Using Sparse Measurements](https://doi.org/10.3390/math14111846) | 隧道渗流测点有限，边界条件、测点布局及几何变化共同影响预测和迁移效果。 | 硬边界、自动权重调优、传感器布设分析与跨隧道几何迁移。 | 摘要强调理想条件；未据此认定使用真实隧道现场实测。 | 数值/合成 |
| 19 | 2026-1-17；Journal of Geodesy | [Physics-informed neural networks for geoid modeling](https://doi.org/10.1007/s00190-025-02017-6) | 地面与航空重力数据异质、分布不均，稀疏条件下难兼顾全局与局部建模精度。 | CNN 提取地面/航空重力多尺度特征，MLP 预测扰动位，加入 Laplace 与重力关系约束。 | 不同地区数据分布与观测误差可能不同；需地区独立验证。 | 包含实测 |
| 20 | 2026-7-10；Experiments in Fluids | [Quantitative schlieren with physics-informed neural networks](https://doi.org/10.1007/s00348-026-04268-1) | 普通纹影图像缺少亮度到密度梯度的标定，难以恢复有确定尺度的定量密度场。 | 将纹影图像强度到密度梯度的标定因子作为未知量；激波跳跃条件消除尺度歧义。 | 全文指出部分权重需手调；实验 SBLI 约 1 小时/A100，未等于实时反演。 | 包含实测 |
| 21 | 2026-7-20；International Journal of Numerical Methods for Heat &amp; Fluid Flow | [Modified-inverse physics informed neural networks for determination of orthotropic thermal conductivities](https://doi.org/10.1108/hff-03-2026-0324) | 温度观测稀疏时，三维多参数导热反演易不稳定，参数识别和计算效率受限。 | 改进 inverse-PINN，结合有限差分伪梯度优化，联合识别各向异性导热参数。 | 多参数可辨识性依赖激励和传感器；仅低温度误差不足以证明参数正确。 | 包含实测 |
| 22 | 2025-9-15；SIAM/ASA Journal on Uncertainty Quantification | [Scalable Bayesian Physics-Informed Kolmogorov-Arnold Networks](https://doi.org/10.1137/25m1729253) | 含噪大数据下贝叶斯网络推断成本高；KAN 的梯度型采样仍可能低效。 | Chebyshev KAN + dropout Tikhonov 集合 Kalman 反演 + 活跃子空间，降低贝叶斯推断成本。 | 近似推断的区间需验证覆盖率；不等于解决方程错设。 | 数值/合成 |
| 23 | 2024-11；AIAA Journal | [Flight Dynamic Uncertainty Quantification Modeling Using Physics-Informed Neural Networks](https://doi.org/10.2514/1.j063992) | 极端飞行状态下气动效应强非线性，确定性 PINN 预测缺少可信程度估计。 | 三类集成方法为气动系数和传播轨迹提供置信区间。 | 明确是仿真验证，不是实机飞行；集成成本与 OOD 校准必须计入。 | 数值/合成 |
| 24 | 2026-9-24；Applied Sciences | [Operator-Budget Evaluation of Residual-Adaptive Sampling in Physics-Informed Neural Networks](https://doi.org/10.3390/app16199508) | 按相同优化步数比较会漏计自适应采样的维护成本，难判断收益是否仅来自额外计算。 | 将训练残差和采样分布维护的额外残差调用统一计账，按计算预算比较方法。 | 不能只按训练步数比较；作者未确立所有问题上的普遍优势。 | 数值/合成 |

## 期刊论文逐篇介绍

### 01. A matrix preconditioning framework for physics-informed neural networks based on the adjoint method

**期刊与时间：** Physics of Fluids，2025-9-11。
**论文链接：** [DOI: 10.1063/5.0285013](https://doi.org/10.1063/5.0285013)。
**研究方向：** 优化与预条件。

**解决什么问题**

多尺度和高雷诺数问题中，PDE 系统病态使卷积式 PINN 收敛缓慢甚至失败。

**核心 idea 是什么**

用自动微分和矩阵染色求 PDE Jacobian，经不完全 LU 分解构造预条件器，缩放残差；伴随法处理梯度。

实际验证：多尺度及高雷诺数数值问题。 验证类型：数值或合成验证。

**尚存在的问题**

属于卷积式 PICNN 框架；要把预条件器构建时间和内存计入，不能只比较迭代数。

### 03. Self-adaptive weighting and sampling for physics-informed neural networks

**期刊与时间：** Machine Learning: Science and Technology，2026-4-7。
**论文链接：** [DOI: 10.1088/2632-2153/ae556e](https://doi.org/10.1088/2632-2153/ae556e)。
**研究方向：** 采样与权重。

**解决什么问题**

快速变化区域配点不足，各点收敛速度不均；只改采样或只改权重效果不稳定。

**核心 idea 是什么**

联合自适应采样和点权重：关注解快速变化区域，同时平衡各点的收敛速度。

实际验证：多组 PDE 数值实验；单独采样或加权的收益依赖问题。 验证类型：数值或合成验证。

**尚存在的问题**

需要同预算消融：只采样、只加权、联合、固定基线；论文摘要未证明所有 PDE 均有效。

### 04. Antiderivative-enhanced adaptive sampling algorithm for physics-informed neural networks

**期刊与时间：** Physica Scripta，2026-1-6。
**论文链接：** [DOI: 10.1088/1402-4896/ae30b5](https://doi.org/10.1088/1402-4896/ae30b5)。
**研究方向：** 采样与权重。

**解决什么问题**

只依靠残差选点难以兼顾导数表达，陡梯度及高阶导数相关问题难学。

**核心 idea 是什么**

残差驱动采样结合反导数近似层，改善函数及导数的表达。

实际验证：Burgers、Allen–Cahn、波动方程、二维 Poisson 数值测试。 验证类型：数值或合成验证。

**尚存在的问题**

同时改变结构与采样，必须用消融拆分贡献；这些不是工程实测。

### 05. SPIKANs: separable physics-informed Kolmogorov–Arnold networks

**期刊与时间：** Machine Learning: Science and Technology，2025-9-22。
**论文链接：** [DOI: 10.1088/2632-2153/ae05af](https://doi.org/10.1088/2632-2153/ae05af)。
**研究方向：** 结构与物理表征。

**解决什么问题**

高维问题的配点规模迅速增长，普通 PIKAN 训练速度慢、计算成本高。

**核心 idea 是什么**

SPIKANs 用分离变量思路，每个维度一个 KAN，降低高维配点训练开销。

实际验证：高维 PDE 基准，对比 PIKAN。 验证类型：数值或合成验证。

**尚存在的问题**

KAN 本身不是物理定律；低秩或可分离假设是否适合目标问题需验证。

### 06. Physics-informed graph Laplacian-augmented Kolmogorov–Arnold networks

**期刊与时间：** Physics of Fluids，2026-8-24。
**论文链接：** [DOI: 10.1063/5.0341290](https://doi.org/10.1063/5.0341290)。
**研究方向：** 结构与物理表征。

**解决什么问题**

不规则血管几何中，几何表示、神经近似与 PDE 残差离散难以协调。

**核心 idea 是什么**

统一有限元表示中的图连接、KAN 系数参数化和 Galerkin 残差。

实际验证：二维血管几何的稳态不可压 Navier–Stokes，包含分叉和狭窄等。 验证类型：数值或合成验证。

**尚存在的问题**

血管几何测试不等于临床验证；常规 PINN 在部分几何上的误差更低，不能说全面胜出。

### 07. Modal Physics-Informed Neural Networks for Forward and Inverse Structural Vibration Problems

**期刊与时间：** International Journal of Structural Stability and Dynamics，2026-5-19。
**论文链接：** [DOI: 10.1142/s021945542750355x](https://doi.org/10.1142/s021945542750355x)。
**研究方向：** 结构与物理表征。

**解决什么问题**

结构振动具有高频响应和高维状态，普通 PINN 受谱偏置影响且训练开销大。

**核心 idea 是什么**

模态分解降低结构动力学维度，结合 Fourier 特征处理高频响应。

实际验证：数值梁/桁架；铝悬臂梁加速度传感器实验。摘要报告五传感器下识别误差 4.3%。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

经典模态假设对强非线性、接触问题可能不足；误差和加速限于所测配置。

### 08. Progressive Domain Decomposition for Efficient Training of Physics-Informed Neural Network

**期刊与时间：** Mathematics，2025-5-4。
**论文链接：** [DOI: 10.3390/math13091515](https://doi.org/10.3390/math13091515)。
**研究方向：** 区域分解。

**解决什么问题**

不同区域学习难度不同，统一训练会在已学好的区域继续消耗计算资源。

**核心 idea 是什么**

根据残差动态分区，逐步训练并保存已达到要求的局部模型。

实际验证：复杂 PDE 数值实验。 验证类型：数值或合成验证。

**尚存在的问题**

分区和冻结阈值也是超参数，需检查界面误差和总体耗时。

### 09. ADD-PINN: Adaptive Domain Decomposition Based Physics Informed Neural Networks via Spatial Clustering

**期刊与时间：** Communications in Computational Physics，2026-6-25。
**论文链接：** [DOI: 10.4208/cicp.oa-2025-0132](https://doi.org/10.4208/cicp.oa-2025-0132)。
**研究方向：** 区域分解。

**解决什么问题**

人工分区依赖经验，子域接口条件复杂，固定分区难适应训练中的误差分布。

**核心 idea 是什么**

空间聚类自动分块，梯度信息调节跨域交换，用图优化处理子域调整。

实际验证：PDE 数值案例，对比 XPINN，并分析运行时瓶颈。 验证类型：数值或合成验证。

**尚存在的问题**

接口和调度有额外成本；不应只和未经调优的单网络比较。

### 10. AB-PINNs: adaptive-basis physics-informed neural networks for residual-driven domain decomposition

**期刊与时间：** Machine Learning: Science and Technology，2026-7-17。
**论文链接：** [DOI: 10.1088/2632-2153/ae8638](https://doi.org/10.1088/2632-2153/ae8638)。
**研究方向：** 区域分解。

**解决什么问题**

单网络或静态分区难以同时表达全局大尺度结构与局部细尺度特征。

**核心 idea 是什么**

全局网络学大尺度、局部网络学细节；子域可移动，并在高残差区新增子域。

实际验证：多尺度微分方程，比较标准 PINN 和静态分解。 验证类型：数值或合成验证。

**尚存在的问题**

类似自适应网格细化的资源分配；需比较经典 AMR 或成熟数值求解器。

### 11. Physics-Informed Neural Networks with Hard Constraints for Axial Temperature Distribution Estimation of Lithium-Ion Batteries

**期刊与时间：** World Electric Vehicle Journal，2026-5-21。
**论文链接：** [DOI: 10.3390/wevj17050275](https://doi.org/10.3390/wevj17050275)。
**研究方向：** 物理可行性与约束。

**解决什么问题**

集总模型忽略电池内部温度梯度，软边界约束难准确满足换热边界。

**核心 idea 是什么**

用距离函数将 Robin 边界嵌入解空间，结合电热耦合残差。

实际验证：18650 电池 1C–4C 放电测温实验，摘要报告 MAE 小于 0.34°C。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

硬约束仅针对指定数学边界；错误换热系数或热模型仍可造成系统误差。

### 12. Physics-Informed Neural Networks with Mass Conservation Constraints for Predicting Particle Sedimentation in Non-Newtonian Suspensions

**期刊与时间：** ACS Omega，2026-9-14。
**论文链接：** [DOI: 10.1021/acsomega.6c08067](https://doi.org/10.1021/acsomega.6c08067)。
**研究方向：** 物理可行性与约束。

**解决什么问题**

沉降监测点稀疏，长时间外推易出现固相总量漂移，早期快速变化也难捕捉。

**核心 idea 是什么**

局部沉降 PDE 加全局质量约束；逐渐提高守恒权重，并用对数时间映射解析早期快速变化。

实际验证：多工况台架实验，九点超声厚度观测；摘要报告全局 RMSE 3.71 mm 和留一验证。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

留一工况不能直接当作任意参数 OOD；经验方程与实际工况适配仍需检查。

### 13. Enforcing hidden physics in physics-informed neural networks

**期刊与时间：** Communications Physics，2026-7-11。
**论文链接：** [DOI: 10.1038/s42005-026-02743-z](https://doi.org/10.1038/s42005-026-02743-z)。
**研究方向：** 物理可行性与约束。

**解决什么问题**

仅拟合 PDE 残差仍可能产生违反不可逆过程方向性的非物理解。

**核心 idea 是什么**

给已有 PDE 残差补上不可逆性正则，排除低残差但物理不合理的解。

实际验证：行波、燃烧、融冰、腐蚀、裂纹生长等基准。 验证类型：数值或合成验证。

**尚存在的问题**

这是补充已知物理先验，不是从数据自动发现新规律；不应对可逆过程错误加入单调性。

### 14. Two-stage projection physics-informed neural networks for preserving conservation laws

**期刊与时间：** Machine Learning: Science and Technology，2026-9-22。
**论文链接：** [DOI: 10.1088/2632-2153/aeab20](https://doi.org/10.1088/2632-2153/aeab20)。
**研究方向：** 物理可行性与约束。

**解决什么问题**

局部 PDE 残差较小，仍可能出现全局不变量漂移。

**核心 idea 是什么**

先训练普通 PINN，推理时将输出投影到选定不变量流形。

实际验证：KdV、非线性 Schrödinger、守均值 Kuramoto–Sivashinsky，单位时间区间。 验证类型：数值或合成验证。

**尚存在的问题**

摘要明确：守恒违反显著减少但预测误差变化很小；未建立长期稳定性或一般性。

### 15. WF-PINNs: solving forward and inverse problems of burgers equation with steep gradients using weak-form physics-informed neural networks

**期刊与时间：** Scientific Reports，2025-11-18。
**论文链接：** [DOI: 10.1038/s41598-025-24427-4](https://doi.org/10.1038/s41598-025-24427-4)。
**研究方向：** 物理可行性与约束。

**解决什么问题**

Burgers 陡梯度或激波附近训练不稳定，初始条件与黏度反演困难。

**核心 idea 是什么**

弱式积分残差、熵条件和逆问题双网络一致性联合训练。

实际验证：Burgers 陡梯度、初始条件及黏度反演，参考解生成观测。 验证类型：数值或合成验证。

**尚存在的问题**

弱式、熵方法并非近两年才出现；黏性/无黏性问题的熵式须逐式核对，不能直接照搬。

### 16. Cross-time causal physics-informed neural networks for dynamic time-dependent problems

**期刊与时间：** International Journal of Wavelets, Multiresolution and Information Processing，2025-9-30。
**论文链接：** [DOI: 10.1142/s0219691325500316](https://doi.org/10.1142/s0219691325500316)。
**研究方向：** 时间因果训练。

**解决什么问题**

时间分区内部仍可能忽略先后依赖，跨段解的衔接与一致性难以维持。

**核心 idea 是什么**

重叠时间分区；区内软因果权重，区间传递先前解，重叠区加一致性损失。

实际验证：Allen–Cahn 与 KdV 数值求解。 验证类型：数值或合成验证。

**尚存在的问题**

这里的因果指时间推进依赖，不是干预因果推断；需测跨段误差累积。

### 17. Multichannel Wavefield Reconstruction With Physics‐Informed Neural Networks and Transfer Learning

**期刊与时间：** Geophysical Prospecting，2026-3-2。
**论文链接：** [DOI: 10.1111/1365-2478.70149](https://doi.org/10.1111/1365-2478.70149)。
**研究方向：** 迁移与跨工况。

**解决什么问题**

地震观测道稀疏且含噪；对每个炮集从零训练重建网络成本过高。

**核心 idea 是什么**

先训练一个炮集，再微调到相邻炮集，复用波场重建网络。

实际验证：Mississippi streamer 实测地震数据；摘要报告单炮重建成本为逐炮重训的 0.76%。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

这是特定数据集上的迁移结果，不是任意介质泛化；需计首个模型训练成本。

### 18. Physics-Informed Neural Networks with Transfer Learning for Tunnel Seepage Prediction Using Sparse Measurements

**期刊与时间：** Mathematics，2026-5-26。
**论文链接：** [DOI: 10.3390/math14111846](https://doi.org/10.3390/math14111846)。
**研究方向：** 迁移与跨工况。

**解决什么问题**

隧道渗流测点有限，边界条件、测点布局及几何变化共同影响预测和迁移效果。

**核心 idea 是什么**

硬边界、自动权重调优、传感器布设分析与跨隧道几何迁移。

实际验证：132 种几何配置，有限元参考；12 个精心布设测点在理想设置优于 100 个随机点。 验证类型：数值或合成验证。

**尚存在的问题**

摘要强调理想条件；未据此认定使用真实隧道现场实测。

### 19. Physics-informed neural networks for geoid modeling

**期刊与时间：** Journal of Geodesy，2026-1-17。
**论文链接：** [DOI: 10.1007/s00190-025-02017-6](https://doi.org/10.1007/s00190-025-02017-6)。
**研究方向：** 实测反演与数据融合。

**解决什么问题**

地面与航空重力数据异质、分布不均，稀疏条件下难兼顾全局与局部建模精度。

**核心 idea 是什么**

CNN 提取地面/航空重力多尺度特征，MLP 预测扰动位，加入 Laplace 与重力关系约束。

实际验证：Colorado 大地水准面实验，对照 GSVS17 GNSS/水准数据，摘要报告 STD 2.1 cm。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

不同地区数据分布与观测误差可能不同；需地区独立验证。

### 20. Quantitative schlieren with physics-informed neural networks

**期刊与时间：** Experiments in Fluids，2026-7-10。
**论文链接：** [DOI: 10.1007/s00348-026-04268-1](https://doi.org/10.1007/s00348-026-04268-1)。
**研究方向：** 实测反演与数据融合。

**解决什么问题**

普通纹影图像缺少亮度到密度梯度的标定，难以恢复有确定尺度的定量密度场。

**核心 idea 是什么**

将纹影图像强度到密度梯度的标定因子作为未知量；激波跳跃条件消除尺度歧义。

实际验证：数值翼型、Mach 2 风洞 SBLI 与独立 BOS 对照，以及历史弹丸图像。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

全文指出部分权重需手调；实验 SBLI 约 1 小时/A100，未等于实时反演。

### 21. Modified-inverse physics informed neural networks for determination of orthotropic thermal conductivities

**期刊与时间：** International Journal of Numerical Methods for Heat &amp; Fluid Flow，2026-7-20。
**论文链接：** [DOI: 10.1108/hff-03-2026-0324](https://doi.org/10.1108/hff-03-2026-0324)。
**研究方向：** 实测反演与数据融合。

**解决什么问题**

温度观测稀疏时，三维多参数导热反演易不稳定，参数识别和计算效率受限。

**核心 idea 是什么**

改进 inverse-PINN，结合有限差分伪梯度优化，联合识别各向异性导热参数。

实际验证：AISI 304 不锈钢、软包电池热实验，以及二维/三维合成测试。 验证类型：摘要明确包含实测或实验。

**尚存在的问题**

多参数可辨识性依赖激励和传感器；仅低温度误差不足以证明参数正确。

### 22. Scalable Bayesian Physics-Informed Kolmogorov-Arnold Networks

**期刊与时间：** SIAM/ASA Journal on Uncertainty Quantification，2025-9-15。
**论文链接：** [DOI: 10.1137/25m1729253](https://doi.org/10.1137/25m1729253)。
**研究方向：** 不确定性。

**解决什么问题**

含噪大数据下贝叶斯网络推断成本高；KAN 的梯度型采样仍可能低效。

**核心 idea 是什么**

Chebyshev KAN + dropout Tikhonov 集合 Kalman 反演 + 活跃子空间，降低贝叶斯推断成本。

实际验证：不同数据规模和噪声水平测试，对比 HMC。 验证类型：数值或合成验证。

**尚存在的问题**

近似推断的区间需验证覆盖率；不等于解决方程错设。

### 23. Flight Dynamic Uncertainty Quantification Modeling Using Physics-Informed Neural Networks

**期刊与时间：** AIAA Journal，2024-11。
**论文链接：** [DOI: 10.2514/1.j063992](https://doi.org/10.2514/1.j063992)。
**研究方向：** 不确定性。

**解决什么问题**

极端飞行状态下气动效应强非线性，确定性 PINN 预测缺少可信程度估计。

**核心 idea 是什么**

三类集成方法为气动系数和传播轨迹提供置信区间。

实际验证：仿真 F16，最多训练 100 个 PINN，并在六自由度仿真传播轨迹。 验证类型：数值或合成验证。

**尚存在的问题**

明确是仿真验证，不是实机飞行；集成成本与 OOD 校准必须计入。

### 24. Operator-Budget Evaluation of Residual-Adaptive Sampling in Physics-Informed Neural Networks

**期刊与时间：** Applied Sciences，2026-9-24。
**论文链接：** [DOI: 10.3390/app16199508](https://doi.org/10.3390/app16199508)。
**研究方向：** 评测与成本核算。

**解决什么问题**

按相同优化步数比较会漏计自适应采样的维护成本，难判断收益是否仅来自额外计算。

**核心 idea 是什么**

将训练残差和采样分布维护的额外残差调用统一计账，按计算预算比较方法。

实际验证：多 PDE 数值评测；讨论缓存复用、均匀混合与实现开销。 验证类型：数值或合成验证。

**尚存在的问题**

不能只按训练步数比较；作者未确立所有问题上的普遍优势。

## 附录：原样本中的会议论文

以下论文发表于 AAAI 会议论文集，不计入上述 23 篇期刊论文；为保留原样本的完整性，仍按相同格式介绍。

### 02. Number Theoretic Accelerated Learning of Physics-Informed Neural Networks

**会议论文集与时间：** Proceedings of the AAAI Conference on Artificial Intelligence，2025-4-11。
**论文链接：** [DOI: 10.1609/aaai.v39i1.32040](https://doi.org/10.1609/aaai.v39i1.32040)。
**研究方向：** 采样与权重。

**解决什么问题**

有限配点引入离散误差，常规采样需要较多点才能达到目标精度。

**核心 idea 是什么**

用数论中的优良格点与周期化技巧减少配点离散误差。

实际验证：作者摘要报告在测试中使用少 2–7 倍的配点达到有竞争力的性能。 验证类型：数值或合成验证。

**尚存在的问题**

配点减少不直接等于端到端加速；实际边界与几何需满足适用条件。

## 精选五篇对比表

按原编号 03、04、07、08、24 的顺序排列；内容取自上文对应条目，未新增文献。验证范围写在“核心 idea”括号内，便于区分已验证结论与整理者判断。

| 发表时间与期刊 | 解决什么问题 | 核心 idea | 尚存在的问题 |
|---|---|---|---|
| 2026-4-7；Machine Learning: Science and Technology | 解快速变化区域配点不足，各点收敛速度不均；只改采样或只改权重时收益不稳定。 | 采样与点权重联合自适应：在解变化快处加密配点，同时按各点收敛速度调整残差权重（多组 PDE 数值验证）。 | 缺同预算消融（只采样／只加权／联合／固定基线），无法拆分两者各自贡献；摘要未证明对所有 PDE 均有效；无实测。 |
| 2026-1-6；Physica Scripta | 仅凭残差选点难以兼顾导数精度，陡梯度与高阶导数相关问题难学。 | 残差驱动采样叠加反导数近似层，同时改善函数与导数的表达能力（Burgers、Allen–Cahn、波动方程、二维 Poisson 数值测试）。 | 结构与采样两处同时改动，必须用消融拆分贡献；仅为数值验证，非工程实测。 |
| 2026-5-19；International Journal of Structural Stability and Dynamics | 结构振动响应高频、状态维度高，普通 PINN 受谱偏置影响且训练开销大。 | 模态分解降低结构动力学维度，配合 Fourier 特征处理高频响应（数值梁/桁架，以及铝悬臂梁加速度传感器实验，五传感器下识别误差 4.3%）。 | 经典模态假设对强非线性、接触类问题可能不足；误差与加速结论限于所测配置，不可外推。 |
| 2025-5-4；Mathematics | 不同区域学习难度不同，统一训练会在已学好的区域继续消耗计算资源。 | 依据残差动态分区，逐步训练并冻结已达标的子域模型（复杂 PDE 数值实验）。 | 分区方式与冻结阈值本身也是超参数；需报告界面误差与总体耗时，否则收益可能被分区与调度开销抵消。 |
| 2026-9-24；Applied Sciences | 按相同优化步数比较会漏计自适应采样的维护成本，难以判断收益是否只来自额外计算。 | 将训练残差与采样分布维护的额外残差调用统一计账，按计算预算而非训练步数比较方法（多 PDE 数值评测，并讨论缓存复用、均匀混合与实现开销）。 | 作者未确立所有问题上的普遍优势；结论仍限于所测数值问题，未涉及实测工况。 |

## 结合当前研究目标的判断

当前目标是让模型利用物理参数和规律进行跨工况预测。单方程 PINN 求解精度提高，不等于通用物理理解增强；多数方法论文改变的是优化问题或数值表示，而非学到可以迁移的世界模型。
1. 优先考虑“先验错误时如何识别并降低错误约束”。同一骨干比较纯数据、正确物理、错误物理、可调权重、已知动力学加残差。现有自适应权重主要解决训练平衡，不能直接证明能识别错误物理。检索到的不确定性研究也不能直接替代模型错设研究；仍需补充专门检索来确认新颖性。
2. 优先考虑“跨物理参数与跨传感器布局泛化”。用完整工况隔离训练/测试，留出黏度、换热系数、质量等参数区间；比较重训、微调与参数条件化的一次训练。迁移效率和 OOD 正确性是不同结论。
3. 有图像数据时，考虑“视觉观测到物理状态/参数的可辨识反演”。纹影案例表明，需要观测模型与物理锚点来消除尺度歧义；不能默认 VLM 从单张图像就能识别质量或摩擦。可把物理反演作为世界模型的状态估计环节。
4. 若只做 KAN/Transformer 替换 MLP，再加入注意力或动态权重，需要强消融才能归因。结构替换本身不足以支持“学会物理”的结论。

## 最低限度实验对照

- 固定数据、网络容量、调参预算，报告至少多个随机种子。先在小实验确认可复现，再扩大。
- 强基线包括调优后的标准 PINN、同输入的纯数据模型，以及适用的 FEM/FDM/谱方法；逆问题还应比较传统参数估计。
- 报告真实解误差、参数误差、物理约束违反、时间外推与参数 OOD；不能只报告训练残差。
- 计入采样、自动微分、预训练、微调和后处理成本；单次求解与多次摊销成本分开。
- 实测需独立设备/批次/工况验证；仿真合成传感器数据应明确标注。

## 可追溯文件

- `crossref_candidates.json`：144 条原始候选元数据，保留检索词。
- `selected_24_annotated.json`：24 篇人工分类、日期、摘要与解读。
- `sources/`：获取成功的出版商页面及提取文字。
- `../../_tools/pinn_recent_search.ps1`：可重复执行的检索脚本。
