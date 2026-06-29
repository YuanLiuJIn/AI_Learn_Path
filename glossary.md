# 术语表 Glossary

本表收纳本学习项目中出现过的专业名词，按主题归类，给出一句话解释，并标注详细出处章节。遇到不熟悉的名词先查这里，再回到对应章节深入。

约定：`P1` = `Part1_learning_basic`，`P2` = `Part2_network_architecture`。

---

## 1. 机器学习基础

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| 监督学习 (Supervised Learning) | 用带标准答案（标签）的数据训练模型 | P1/01 |
| 无监督学习 (Unsupervised Learning) | 没有标签，让模型自己发现数据结构 | P1/01 |
| 强化学习 (Reinforcement Learning) | 智能体与环境交互、靠奖励学习策略 | P1/01 |
| 训练集 / 验证集 / 测试集 | 分别用于训练参数 / 调超参选模型 / 最终评估泛化 | P1/01 |
| 过拟合 (Overfitting) | 把训练数据噪声也记住，训练好但泛化差 | P1/01 |
| 欠拟合 (Underfitting) | 模型太简单，连训练集都学不好 | P1/01 |
| 泛化能力 (Generalization) | 模型在没见过的新数据上也表现好 | P1/01 |
| 偏差-方差权衡 (Bias-Variance Tradeoff) | 简单模型偏差高、复杂模型方差高，需平衡 | P1/01 |
| 数据泄漏 (Data Leakage) | 训练用了真实预测时拿不到的信息，导致指标虚高 | P1/01 |
| 特征工程 (Feature Engineering) | 对原始数据做清洗、编码、构造特征 | P1/01 |
| benchmark (基准测试) | 用公开标准任务统一比较不同模型能力 | P1/01 |
| benchmark 污染 (Contamination) | 测试数据混进训练集，相当于“背过题” | P1/01 |

### 评估指标

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| Accuracy (准确率) | 预测对的样本占比 | P1/01 |
| Precision (精确率) | 预测为正的里面有多少真的是正 | P1/01 |
| Recall (召回率) | 真实为正的里面有多少被找出来 | P1/01 |
| F1 | Precision 和 Recall 的调和平均 | P1/01 |
| ROC-AUC | 衡量模型排序正负样本的能力 | P1/01 |
| MSE / RMSE / MAE | 回归误差指标，RMSE 与标签同单位，MAE 更鲁棒 | P1/01,02 |
| R² | 模型解释了多少数据方差 | P1/01 |
| Perplexity (困惑度) | 语言模型预测下一个 token 的不确定性，越低越好 | P1/01 |
| BLEU / ROUGE | 机器翻译、摘要常用的文本生成评估指标 | P1/01 |

---

## 2. 线性模型与优化

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| 线性回归 (Linear Regression) | 用 `y = Xw + b` 拟合连续值 | P1/02 |
| 逻辑回归 (Logistic Regression) | 线性计算后接 sigmoid，用于分类 | P1/02 |
| sigmoid | 把任意实数压到 0~1，可当概率 | P1/02 |
| Softmax | 把多个分数转成和为 1 的多类概率 | P1/05 |
| MSE (均方误差) | 回归常用损失，对大误差更敏感 | P1/02 |
| 交叉熵 (Cross Entropy) | 分类常用损失，惩罚“给正确类低概率” | P1/02 |
| 最小二乘法 | 直接解出使 MSE 最小的参数 | P1/02 |
| 梯度下降 (Gradient Descent) | 沿负梯度方向一步步降低损失 | P1/02 |
| 学习率 (Learning Rate) | 每次参数更新的步长 | P1/02 |
| L1 / L2 正则化 | 在损失里加权重惩罚，控制过拟合 | P1/02 |
| 特征缩放 (Feature Scaling) | 标准化/归一化让特征尺度相近 | P1/02 |

---

## 3. 树模型与集成学习

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| 决策树 (Decision Tree) | 用一系列问题把样本分到叶子节点 | P1/03 |
| CART | 二叉分裂、能分类也能回归的经典树算法 | P1/03 |
| 基尼指数 (Gini) | 衡量节点不纯度，CART 分类常用 | P1/03 |
| 熵 / 信息增益 | 衡量混乱程度，ID3/C4.5 分裂依据 | P1/03 |
| 剪枝 (Pruning) | 删掉对泛化无益的分支，减少过拟合 | P1/03 |
| Bagging | 多模型并行训练取平均，降低方差 | P1/04 |
| Boosting | 多模型串行训练、逐步修正错误，降低偏差 | P1/04 |
| 随机森林 (Random Forest) | Bagging + 决策树 + 特征随机 | P1/04 |
| GBDT | 梯度提升树，后一棵拟合前面的负梯度 | P1/04 |
| XGBoost / LightGBM / CatBoost | GBDT 的高性能工程实现 | P1/04 |
| Stacking | 用一个模型学习多个模型的输出 | P1/04 |

---

## 4. 深度学习基础

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| 神经元 (Neuron) | 先线性加权 `Wx+b` 再过激活函数 | P1/05 |
| 输入层 / 隐藏层 / 输出层 | 数据入口 / 中间加工层 / 输出答案层 | P1/05 |
| 张量 (Tensor) | 多维数组，深度学习的基本数据结构 | P1/05,07 |
| 前向传播 (Forward) | 用当前参数算出预测 | P1/05 |
| 反向传播 (Backward) | 用链式法则算出每个参数的梯度 | P1/05 |
| 激活函数 (Activation) | 提供非线性，让多层有意义 | P1/05 |
| ReLU | `max(0,x)`，隐藏层默认激活 | P1/05 |
| GELU / SiLU(Swish) | 平滑激活，Transformer/现代网络常用 | P1/05 |
| Tanh | 输出 -1~1 的激活，RNN 常用 | P1/05 |
| 优化器 (Optimizer) | 根据梯度更新参数的算法 | P1/05 |
| SGD / Momentum | 随机梯度下降 / 加动量减少震荡 | P1/05 |
| Adam / AdamW | 自适应优化器，AdamW 解耦 weight decay，大模型常用 | P1/05 |
| 梯度消失 / 爆炸 | 反向传播梯度变得过小 / 过大 | P1/05 |
| Batch Normalization | 对 batch 维度归一化，常用于 CNN | P1/05 |
| Layer Normalization | 对特征维度归一化，常用于 Transformer | P1/05 |
| RMSNorm | LayerNorm 的简化变体，大模型常用 | P1/05 |
| Dropout | 训练时随机丢弃神经元，防过拟合 | P1/05 |
| weight decay | 权重衰减，相当于 L2 正则 | P1/05 |
| MLP | 多层全连接网络 | P1/05 |
| epoch / batch / step | 看完整训练集一遍 / 一小批样本 / 更新一次参数 | P1/07 |

---

## 5. GPU 与 CUDA

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| GPU | 擅长大规模并行计算的硬件 | P1/06 |
| CUDA | NVIDIA 的 GPU 通用计算平台与编程模型 | P1/06 |
| cuDNN / cuBLAS | 深度学习常用的 GPU 高性能库 | P1/06 |
| Grid / Block / Thread | CUDA 的三级线程组织结构 | P1/06 |
| SIMT | 单指令多线程，很多线程跑同一指令处理不同数据 | P1/06 |
| 显存 (VRAM) | GPU 自己的内存，存参数/梯度/激活等 | P1/06 |
| OOM (Out of Memory) | 显存不够导致的报错 | P1/06 |
| 混合精度 (Mixed Precision) | 用 16 位为主计算，省显存提速 | P1/06 |
| float32 / float16 / bfloat16 | 常见数值精度，bf16 范围大、大模型常用 | P1/06 |
| 梯度累积 (Gradient Accumulation) | 多个小 batch 攒梯度再更新，等效大 batch | P1/06 |
| 梯度检查点 (Gradient Checkpointing) | 反向时重算激活以省显存 | P1/06 |
| 数据并行 / 张量并行 / 流水线并行 | 多卡训练的不同拆分方式 | P1/06 |
| ZeRO | 把参数/梯度/优化器状态切片到多卡，省显存 | P1/06 |
| FLOPS | 每秒浮点运算次数，衡量算力 | P1/06 |

---

## 6. PyTorch

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| `torch.Tensor` | PyTorch 的张量，可上 GPU、可求梯度 | P1/07 |
| autograd | 自动求导引擎，`loss.backward()` 背后机制 | P1/07 |
| `nn.Module` | 所有模型的基类，管理层与参数 | P1/07 |
| `Dataset` / `DataLoader` | 定义如何取数据 / 批量加载打乱 | P1/07 |
| `optimizer.zero_grad()` | 清空上一步梯度，防止累加 | P1/07 |
| `model.train()` / `eval()` | 切换训练/评估模式，影响 Dropout、BN | P1/07 |
| `state_dict` | 模型参数字典，推荐用它保存模型 | P1/07 |
| shape / dtype / device | 形状 / 数据类型 / 所在设备，常见报错来源 | P1/07 |

---

## 7. 数学基础

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| 向量 / 矩阵 / 张量 | 1 维 / 2 维 / 更高维的数字数组 | P1/09 |
| 矩阵乘法 | 本质是加权求和，神经网络层的核心运算 | P1/09 |
| 均值 / 方差 / 标准差 | 平均水平 / 波动程度 / 波动的同单位度量 | P1/09 |
| 期望 (Expectation) | 长期平均结果 | P1/09 |
| 概率分布 (Distribution) | 描述数据取值的可能性 | P1/09 |
| 分布偏移 (Distribution Shift) | 训练与使用场景数据分布不一致 | P1/09 |
| 最大似然 (MLE) | 调参数让已观测数据看起来最合理 | P1/09 |
| 链式法则 (Chain Rule) | 复合函数求导规则，反向传播的数学基础 | P1/09 |

---

## 8. 网络结构（Part2 涉及，先建立印象）

| 名词 | 一句话解释 | 出处 |
|---|---|---|
| CNN (卷积神经网络) | 用卷积核提取局部空间特征，擅长图像 | P2/01 |
| 卷积核 / 感受野 | 滑动的小权重窗口 / 一个输出能“看到”的输入范围 | P2/01 |
| 池化 (Pooling) | 下采样，缩小特征图、保留主要信息 | P2/01 |
| RNN (循环神经网络) | 带隐藏状态、按时间步处理序列 | P2/02 |
| LSTM / GRU | 带门控机制、缓解长程依赖遗忘的 RNN | P2/03 |
| 语言模型 (Language Model) | 预测下一个 token 的模型 | P2/04 |
| Seq2Seq | 编码器-解码器结构，用于翻译等序列转换 | P2/05 |
| Attention (注意力机制) | 解码时动态关注输入中相关部分 | P2/06 |
| ResNet / 残差连接 | 用 `x + F(x)` 跳跃连接训练很深的网络 | P2/08 |
| Transformer | 完全基于注意力的网络，现代大模型基础 | P2/09 |
| Self-Attention | 序列内部元素互相计算注意力 | P2/09 |
| Multi-Head Attention | 多组注意力并行，关注不同子空间 | P2/09 |
| Positional Encoding | 给 Transformer 注入位置信息 | P2/09 |

---

## 9. 大模型方向预告（后续阶段）

| 名词 | 一句话解释 |
|---|---|
| Token / Tokenization | 文本切分成的最小单元 / 切分过程 |
| Embedding | 把 token 映射成稠密向量 |
| Pre-training / Fine-tuning | 预训练 / 在下游任务上微调 |
| RLHF | 基于人类反馈的强化学习对齐 |
| KV Cache | 推理时缓存注意力的键值，加速生成 |
| VAE / GAN / Diffusion | 三类主流生成模型 |

---

> 维护原则：每当新章节引入新名词，就回填到本表对应分类，保持一处可查。
