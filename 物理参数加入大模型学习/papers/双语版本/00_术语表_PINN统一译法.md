# PINN 文献统一术语表（中英对照）

> 用途：保证四篇论文译文用词一致。凡本表已收录的词，所有译文一律按此表翻译；
> 未收录的专业名词（算法名、模型名、软件名）**保留英文原文**。
> 最后更新：2026-09-27

## 一、核心概念

| English | 中文统一译法 | 备注 |
|:---|:---|:---|
| physics-informed neural network (PINN) | 物理信息神经网络 | 缩写 PINN 保留不译 |
| physics-informed machine learning (PIML) | 物理信息机器学习 | |
| scientific machine learning (SciML) | 科学机器学习 | |
| physics-guided / physics-encoded NN | 物理引导 / 物理编码神经网络 | |
| governing equations | 控制方程 | 不译作“主导方程” |
| physical law / physical constraint | 物理定律 / 物理约束 | |
| prior knowledge | 先验知识 | |
| inductive bias | 归纳偏置 | |
| observational bias | 观测偏置 | |
| learning bias | 学习偏置 | |
| residual | 残差 | PDE 残差 = PDE residual |
| soft penalty / soft constraint | 软惩罚 / 软约束 | |
| hard constraint | 硬约束 | |
| collocation points | 配点 | 不译作“并置点” |
| automatic differentiation | 自动微分 | |
| mesh-free / grid-free | 无网格 | |
| spectral bias | 频谱偏置 | 亦作“频率偏差”，本表统一用“频谱偏置” |

## 二、问题类型

| English | 中文统一译法 | 备注 |
|:---|:---|:---|
| forward problem | 正问题 | |
| inverse problem | 逆问题 | |
| parameter estimation | 参数估计 | |
| system identification | 系统辨识 | |
| data assimilation | 数据同化 | |
| uncertainty quantification (UQ) | 不确定性量化 | |
| aleatoric uncertainty | 偶然不确定性 | 数据固有噪声 |
| epistemic uncertainty | 认知不确定性 | 模型/数据不足导致 |
| gappy / sparse data | 缺失数据 / 稀疏数据 | gappy data 译“有缺口的观测数据” |
| data scarcity | 数据稀缺 | |
| ill-posed | 不适定的 | |

## 三、方程与数值方法

| English | 中文统一译法 | 备注 |
|:---|:---|:---|
| ordinary differential equation (ODE) | 常微分方程 | |
| partial differential equation (PDE) | 偏微分方程 | |
| initial condition / boundary condition (IC/BC) | 初始条件 / 边界条件 | |
| conservation law | 守恒律 | |
| symmetry / equivariance | 对称性 / 等变性 | |
| finite element method (FEM) | 有限元方法 | |
| finite volume method (FVM) | 有限体积法 | |
| finite difference method | 有限差分法 | |
| spectral method | 谱方法 | |
| Runge–Kutta | Runge–Kutta 法 | 人名方法保留原文 |
| domain decomposition | 区域分解 | |
| time-stepping | 时间步进 | |
| Deep Galerkin method | Deep Galerkin 方法 | 保留原文 |
| Monte Carlo | 蒙特卡洛 | |
| surrogate model | 代理模型 | |
| reduced-order model | 降阶模型 | |
| operator learning (DeepONet, FNO) | 算子学习（DeepONet、FNO） | 模型名保留原文 |
| stochastic / fractional-order PDE | 随机 / 分数阶 PDE | |

## 四、网络与方法

| English | 中文统一译法 | 备注 |
|:---|:---|:---|
| feed-forward neural network (FNN) | 前馈神经网络 | |
| convolutional neural network (CNN) | 卷积神经网络 | |
| recurrent neural network (RNN) | 循环神经网络 | |
| long short-term memory (LSTM) | 长短期记忆网络 | |
| graph neural network (GNN) | 图神经网络 | |
| autoencoder / variational autoencoder (VAE) | 自编码器 / 变分自编码器 | |
| generative adversarial network (GAN) | 生成对抗网络 | |
| transformer / attention | Transformer / 注意力机制 | |
| activation function | 激活函数 | |
| backpropagation | 反向传播 | |
| gradient descent | 梯度下降 | |
| overfitting / underfitting | 过拟合 / 欠拟合 | |
| regularization / dropout | 正则化 / 随机失活 | |
| transfer learning | 迁移学习 | |
| weight initialization | 权重初始化 | |
| hyperparameter | 超参数 | |
| loss function | 损失函数 | |
| convergence rate | 收敛速率 | |

## 五、应用领域

| English | 中文统一译法 | 备注 |
|:---|:---|:---|
| fluid dynamics | 流体动力学 | |
| computational fluid dynamics (CFD) | 计算流体力学 | |
| turbulence | 湍流 | |
| Navier–Stokes equations | Navier–Stokes 方程 | 保留原文 |
| Schrödinger equation | 薛定谔方程 | |
| Allen–Cahn equation | Allen–Cahn 方程 | 保留原文 |
| Korteweg–de Vries (KdV) equation | Korteweg–de Vries（KdV）方程 | 保留原文 |
| materials science | 材料科学 | |
| structural health monitoring | 结构健康监测 | |
| geophysics / seismic tomography | 地球物理 / 地震层析成像 | |
| oncology / tumour growth | 肿瘤学 / 肿瘤生长 | |
| digital twin | 数字孪生 | |
| lithium-ion battery state of health (SOH) | 锂离子电池健康状态 | |

## 六、易错译法对照

| 英文 | ✗ 常见错译 | ✓ 正确译法 |
|:---|:---|:---|
| residual | 剩余 | 残差 |
| loss landscape | 损失景观 | 损失曲面/损失地形 |
| physics-informed | 物理通知的 | 物理信息的 |
| informed by data | 被数据通知 | 由数据驱动/受数据约束 |
| state of the art | 艺术状态 | 最新水平（缩写 SOTA 可保留） |
| train a network | 训练一张网 | 训练一个网络 |
| highlight | 高亮 | 强调/指出 |
| leverage | 杠杆 | 利用 |
| robust | 鲁棒的 | 稳健的（“鲁棒性”可保留） |
| interpretability | 可解释性 | 可解释性（保持一致，不混用“可诠释性”） |

## 七、一律保留英文原文的内容

- 软件与框架：PyTorch、TensorFlow、DeepXDE、NeuroDiffEq、PyDens、NeuralPDE、GPyTorch、JAX、PINNtomo
- 基准数据集名、比赛名、机构与基金编号
- 参考文献条目（作者、期刊名、卷期页码、DOI）
- 数学符号与公式本体
- 图表编号（Figure 1 / Table 1 → 图 1 / 表 1，题注译出）
