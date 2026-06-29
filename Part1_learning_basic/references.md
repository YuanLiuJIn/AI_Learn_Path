# 参考资料

本文件收集 Part1 推荐教材、论文、课程、文档和开源项目。优先选择经典、长期有效、被广泛引用的资料。

## 0. 数学基础

- Gilbert Strang, *Introduction to Linear Algebra*。
  - 线性代数经典教材，适合补向量、矩阵、特征值等概念。
- Marc Peter Deisenroth, A. Aldo Faisal, Cheng Soon Ong, *Mathematics for Machine Learning*。
  - 专门面向机器学习的数学基础教材。
- Stanford CS229 Linear Algebra and Probability Review Notes。
  - 适合快速复习机器学习常用数学。
- 3Blue1Brown: Essence of Linear Algebra。
  - 非常适合建立直观理解。

## 1. 机器学习基础

### 教材

- Tom Mitchell, *Machine Learning*, 1997。
  - 经典机器学习教材，适合理解基本定义和学习理论。
- Christopher Bishop, *Pattern Recognition and Machine Learning*, 2006。
  - 偏概率视角，数学更系统。
- Kevin Murphy, *Machine Learning: A Probabilistic Perspective*, 2012。
  - 内容全面，适合进阶。
- Kevin Murphy, *Probabilistic Machine Learning: An Introduction*, 2022。
  - 新版概率机器学习教材。
- Trevor Hastie, Robert Tibshirani, Jerome Friedman, *The Elements of Statistical Learning*, 2009。
  - 统计学习经典教材，适合树模型、集成学习、正则化等主题。
- Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, *An Introduction to Statistical Learning*。
  - 比 ESL 更易读，适合入门。

### 课程与讲义

- Stanford CS229: Machine Learning, Andrew Ng。
- Caltech Learning From Data, Yaser Abu-Mostafa。
- scikit-learn User Guide。

## 2. 决策树与 CART

### 经典资料

- Leo Breiman, Jerome Friedman, Richard Olshen, Charles Stone, *Classification and Regression Trees*, 1984。
  - CART 源头教材。
- Quinlan, “Induction of Decision Trees”, 1986。
  - ID3 决策树经典论文。
- Quinlan, C4.5: Programs for Machine Learning, 1993。

### 文档

- scikit-learn Decision Trees documentation。

## 3. 随机森林、GBDT 与集成学习

### 论文

- Leo Breiman, “Random Forests”, *Machine Learning*, 2001。
- Yoav Freund, Robert Schapire, “A Decision-Theoretic Generalization of On-Line Learning and an Application to Boosting”, 1997。
- Jerome Friedman, “Greedy Function Approximation: A Gradient Boosting Machine”, 2001。
- Tianqi Chen, Carlos Guestrin, “XGBoost: A Scalable Tree Boosting System”, KDD 2016。

### 项目与文档

- scikit-learn Ensemble Methods。
- XGBoost official documentation。
- LightGBM official documentation。
- CatBoost official documentation。

## 4. 深度学习基础

### 教材

- Ian Goodfellow, Yoshua Bengio, Aaron Courville, *Deep Learning*, 2016。
  - 深度学习经典教材。
- Aston Zhang, Zachary Lipton, Mu Li, Alex Smola, *Dive into Deep Learning*。
  - 动手学习深度学习，代码友好。
- Michael Nielsen, *Neural Networks and Deep Learning*。
  - 对反向传播解释非常友好。

### 课程

- Stanford CS231n: Convolutional Neural Networks for Visual Recognition。
- Stanford CS224n: Natural Language Processing with Deep Learning。
- fast.ai Practical Deep Learning for Coders。

## 5. GPU 与 CUDA

### 官方资料

- NVIDIA CUDA C Programming Guide。
- NVIDIA CUDA Best Practices Guide。
- NVIDIA cuDNN documentation。
- NVIDIA developer blog: CUDA optimization articles。

### 建议学习重点

- GPU execution model。
- memory hierarchy。
- warp、block、grid。
- shared memory。
- memory coalescing。
- mixed precision。

Part1 不要求深入写 CUDA kernel，但要理解这些概念对深度学习性能的影响。

## 6. PyTorch

### 官方资料

- PyTorch Official Tutorials。
- PyTorch Documentation: Tensor, Autograd, torch.nn, torch.optim, DataLoader。
- PyTorch CUDA semantics。

### 进阶项目

- Hugging Face Transformers。
- Hugging Face Accelerate。
- PyTorch Lightning。
- nanoGPT by Andrej Karpathy。
- minGPT by Andrej Karpathy。

`nanoGPT` 和 `minGPT` 更适合后续语言模型阶段，不建议在 Part1 一开始就深入。

## 7. 后续大模型方向预告

Part1 完成后，建议进入以下方向：

1. 网络结构：CNN、RNN、Attention、Transformer。
2. 内容生成：VAE、GAN、Diffusion。
3. 语言模型：n-gram、word2vec、seq2seq、Transformer、GPT。
4. 强化学习：MDP、Q-learning、Policy Gradient、PPO、RLHF。
5. 大模型工程：tokenizer、预训练、微调、推理加速、分布式训练。

## 8. 阅读顺序建议

如果只读几份核心资料，建议按这个顺序：

1. *An Introduction to Statistical Learning*：打机器学习基础。
2. scikit-learn User Guide：边学边实践。
3. CART / Random Forest / GBDT 相关章节和论文摘要。
4. *Dive into Deep Learning*：进入深度学习。
5. PyTorch Official Tutorials：掌握工程实现。
6. NVIDIA CUDA introduction：理解 GPU 基础。

## 9. 不建议一开始做的事

- 一上来读大模型论文，不补机器学习基础。
- 只跑现成 notebook，不理解损失和指标。
- 直接微调大模型，却不知道数据泄漏和验证集是什么。
- 只追模型结构，不会排查 shape、dtype、device。
- 只看视频，不做实验。

## 10. 推荐学习输出

每学完一章，至少产出一种材料：

- 一页笔记。
- 一段可运行代码。
- 一个小实验。
- 一个概念解释。
- 一张流程图。

学习大模型最重要的不是“看过多少资料”，而是能不能把概念变成可验证的实验。
