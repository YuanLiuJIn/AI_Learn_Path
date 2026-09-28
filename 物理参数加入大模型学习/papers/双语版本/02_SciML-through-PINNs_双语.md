# Scientific Machine Learning Through Physics–Informed Neural Networks: Where we are and What's Next
# 通过物理信息神经网络实现的科学机器学习：我们处在何处，下一步是什么

> **原文出处**：Cuomo, S.; Schiano Di Cola, V.; Giampaolo, F.; Rozza, G.; Raissi, M.; Piccialli, F. Scientific Machine Learning Through Physics–Informed Neural Networks: Where we are and What's Next. *Journal of Scientific Computing* **2022**, *92*, 88. https://doi.org/10.1007/s10915-022-01939-z
> **译文说明**：双语段落级对照。公式、符号、软件名、参考文献条目保留原文；术语遵循 `00_术语表_PINN统一译法.md`。
> **翻译进度**：封面信息 + 摘要 + 关键词 + §1 引言 + §1.1（前半）已完成；§1.1 后半与 §1.2 起为后续批次。
> **篇幅提示**：全文 62 页、约 31,000 词，是四篇中最长的一篇。

---

## 封面信息 / Front Matter

**引文格式**

> Journal of Scientific Computing (2022) 92:88
> https://doi.org/10.1007/s10915-022-01939-z

> Received: 14 January 2022 / Revised: 6 July 2022 / Accepted: 6 July 2022 / Published online: 26 July 2022
> © The Author(s) 2022

**译**：收稿日期 2022 年 1 月 14 日；修回 2022 年 7 月 6 日；接收 2022 年 7 月 6 日；在线发表 2022 年 7 月 26 日。版权 © 作者所有，2022 年。

**题目**

> Scientific Machine Learning Through Physics–Informed Neural Networks: Where we are and What's Next

**译**：通过物理信息神经网络实现的科学机器学习：我们处在何处，下一步是什么

**作者**

> Salvatore Cuomo ^1^ · Vincenzo Schiano Di Cola ^2^ · Fabio Giampaolo ^1^ · Gianluigi Rozza ^3^ · Maziar Raissi ^4^ · Francesco Piccialli ^1^

**译**：Salvatore Cuomo ^1^ · Vincenzo Schiano Di Cola ^2^ · Fabio Giampaolo ^1^ · Gianluigi Rozza ^3^ · Maziar Raissi ^4^ · Francesco Piccialli ^1^

> S. Cuomo, V. Schiano, F. Giampaolo, G. Rozza and M. Raissi are contributed equally to this study.
> Corresponding author: Francesco Piccialli, francesco.piccialli@unina.it
> Extended author information available on the last page of the article.

**译**：S. Cuomo、V. Schiano、F. Giampaolo、G. Rozza 与 M. Raissi 对本研究的贡献相同。
通信作者：Francesco Piccialli，francesco.piccialli@unina.it
完整的作者单位信息见文末（原文最后一页）。

> **〔译者注〕** 原文的完整单位列表位于文末"Author information"页，PDF 文本提取中位置分散。已知通信作者邮箱域名 `unina.it` 为那不勒斯费德里科二世大学（University of Naples Federico II）；Maziar Raissi 为 PINN 原始论文第一作者。为避免臆测，此处不逐一标注单位，如需精确信息请对照原文 PDF 末页。

---

## 摘要 / Abstract

> Physics-Informed Neural Networks (PINN) are neural networks (NNs) that encode model equations, like Partial Differential Equations (PDE), as a component of the neural network itself. PINNs are nowadays used to solve PDEs, fractional equations, integral-differential equations, and stochastic PDEs. This novel methodology has arisen as a multi-task learning framework in which a NN must fit observed data while reducing a PDE residual.

**译**：物理信息神经网络（PINN）是一类神经网络（NNs），它把模型方程（例如偏微分方程 PDE）编码为神经网络自身的一个组成部分。如今 PINNs 已被用于求解 PDEs、分数阶方程、积分—微分方程以及随机 PDEs。这一新方法作为一种多任务学习框架而兴起：神经网络必须同时拟合观测数据并降低 PDE 残差。

> This article provides a comprehensive review of the literature on PINNs: while the primary goal of the study was to characterize these networks and their related advantages and disadvantages. The review also attempts to incorporate publications on a broader range of collocation-based physics informed neural networks, which stars form the vanilla PINN, as well as many other variants, such as physics-constrained neural networks (PCNN), variational hp-VPINN, and conservative PINN (CPINN).

**译**：本文对 PINN 相关文献作了全面综述：研究的主要目标是刻画这类网络及其相关的优势与劣势。综述还力图纳入范围更广的基于配点的物理信息神经网络文献——其中包括作为起点的原版 PINN（vanilla PINN），以及许多其他变体，例如物理约束神经网络（PCNN）、变分 hp-VPINN 与守恒 PINN（CPINN）。

> The study indicates that most research has focused on customizing the PINN through different activation functions, gradient optimization techniques, neural network structures, and loss function structures. Despite the wide range of applications for which PINNs have been used, by demonstrating their ability to be more feasible in some contexts than classical numerical techniques like Finite Element Method (FEM), advancements are still possible, most notably theoretical issues that remain unresolved.

**译**：研究表明，多数研究聚焦于通过不同的激活函数、梯度优化技术、神经网络结构与损失函数结构来定制 PINN。尽管 PINNs 已应用于广泛场景，并证明在某些情形下比有限元方法（FEM）等经典数值技术更具可行性，但仍有进步空间，其中最突出的是尚未解决的理论问题。

**关键词 / Keywords**

> Physics–Informed Neural Networks · Scientific Machine Learning · Deep Neural Networks · Nonlinear equations · Numerical methods · Partial Differential Equations · Uncertainty

**译**：物理信息神经网络 · 科学机器学习 · 深度神经网络 · 非线性方程 · 数值方法 · 偏微分方程 · 不确定性

---

## 1. Introduction / 1. 引言

> Deep neural networks have succeeded in tasks such as computer vision, natural language processing, and game theory. Deep Learning (DL) has transformed how categorization, pattern recognition, and regression tasks are performed across various application domains. Deep neural networks are increasingly being used to tackle classical applied mathematics problems such as partial differential equations (PDEs) utilizing machine learning and artificial intelligence approaches. Due to, for example, significant nonlinearities, convection dominance, or shocks, some PDEs are notoriously difficult to solve using standard numerical approaches. Deep learning has recently emerged as a new paradigm of scientific computing thanks to neural networks' universal approximation and great expressivity. Recent studies have shown deep learning to be a promising method for building meta-models for fast predictions of dynamic systems. In particular, NNs have proven to represent the underlying nonlinear input-output relationship in complex systems. Unfortunately, dealing with such high dimensional-complex systems are not exempt from the curse of dimensionality, which Bellman first described in the context of optimal control problems [15]. However, machine learning-based algorithms are promising for solving PDEs [19]. Indeed, Blechschmidt and Ernst [19] consider machine learning-based PDE solution approaches will continue to be an important study subject in the next years as deep learning develops in methodological, theoretical, and algorithmic developments.

**译**：深度神经网络已在计算机视觉、自然语言处理与博弈论等任务中取得成功。深度学习（DL）改变了各类应用领域中分类、模式识别与回归任务的执行方式。利用机器学习与人工智能方法，深度神经网络正越来越多地被用于攻克偏微分方程（PDEs）等经典应用数学问题。由于存在显著的强非线性、对流占优或激波等现象，某些 PDEs 用标准数值方法求解是出了名的困难。得益于神经网络的通用逼近能力与强大的表达能力，深度学习近来已成为科学计算的一种新范式。近期研究表明，深度学习是构建元模型（meta-model）以实现动力系统快速预测的一种有前景的方法。尤其是，神经网络已被证明能够表征复杂系统中潜在的非线性输入—输出关系。遗憾的是，处理这类高维复杂系统并不能免于"维数灾难"，Bellman 最早在最优控制问题的语境中描述了这一现象 [15]。不过，基于机器学习的算法在求解 PDEs 方面前景可期 [19]。事实上，Blechschmidt 与 Ernst [19] 认为，随着深度学习在方法学、理论与算法层面不断发展，基于机器学习的 PDE 求解途径在今后若干年内仍将是一个重要研究课题。

> Simple neural network models, such as MLPs with few hidden layers, were used in early work for solving differential equations [89]. Modern methods, based on NN techniques, take advantage of optimization frameworks and auto-differentiation, like Berg and Nyström [16] that suggested a unified deep neural network technique for estimating PDE solutions. Furthermore, it is envisioned that DNN will be able to create an interpretable hybrid Earth system model based on neural networks for Earth and climate sciences [68].

**译**：早期求解微分方程的工作使用的是一些简单的神经网络模型，例如仅含少数隐层的 MLP [89]。基于神经网络技术的现代方法则利用了优化框架与自动微分，例如 Berg 与 Nyström [16] 提出了一种用于估计 PDE 解的统一深度神经网络技术。此外，人们还设想深度神经网络能够为地球与气候科学构建一个基于神经网络、可解释的混合地球系统模型 [68]。

> Nowadays, the literature does not have a clear nomenclature for integrating previous knowledge of a physical phenomenon with deep learning. 'Physics-informed,' 'physicsbased,' 'physics-guided,' and 'theory-guided' are often some used terms. Kim et al [80] developed the overall taxonomy of what they called informed deep learning, followed by a literature review in the field of dynamical systems. Their taxonomy is organized into three conceptual stages: (i) what kind of deep neural network is used, (ii) how physical knowledge is represented, and (iii) how physical information is integrated. Inspired by their work, we will investigate PINNs, a 2017 framework, and demonstrate how neural network features are used, how physical information is supplied, and what physical problems have been solved in the literature.

**译**：如今，文献中对于"如何把物理现象的既有知识与深度学习相结合"尚无统一的命名法。"物理信息的（physics-informed）""基于物理的（physics-based）""物理引导的（physics-guided）""理论引导的（theory-guided）"都是常被使用的说法。Kim 等人 [80] 为他们所称的"informed deep learning"（有知深度学习）建立了总体分类体系，并在动力系统领域做了文献回顾。其分类体系按三个概念阶段组织：(i) 使用何种深度神经网络；(ii) 物理知识如何被表示；(iii) 物理信息如何被整合。受其工作启发，我们将考察 PINNs——一个 2017 年的框架——并阐明文献中如何使用神经网络特性、如何提供物理信息，以及已解决了哪些物理问题。

### 1.1. What the PINNs are / 1.1. PINNs 是什么

> Physics–Informed Neural Networks (PINNs) are a scientific machine learning technique used to solve problems involving Partial Differential Equations (PDEs). PINNs approximate PDE solutions by training a neural network to minimize a loss function; it includes terms reflecting the initial and boundary conditions along the space-time domain's boundary and the PDE residual at selected points in the domain (called collocation point). PINNs are deep-learning networks that, given an input point in the integration domain, produce an estimated solution in that point of a differential equation after training. Incorporating a residual network that encodes the governing physics equations is a significant novelty with PINNs.

**译**：物理信息神经网络（PINNs）是一种用于求解涉及偏微分方程（PDEs）问题的科学机器学习技术。PINNs 通过训练一个神经网络来最小化损失函数，从而逼近 PDE 的解；该损失函数包含若干项，分别反映沿时空域边界上的初始条件与边界条件，以及域内选定点（称为配点，collocation point）上的 PDE 残差。PINNs 是深度学习网络：训练完成后，给定积分域内的一个输入点，它就能给出该点处微分方程的估计解。引入一个编码了控制物理方程的残差网络，是 PINNs 的一项重大创新。

> The basic concept behind PINN training is that it can be thought of as an unsupervised strategy that does not require labelled data, such as results from prior simulations or experiments. The PINN algorithm is essentially a mesh-free technique that finds PDE solutions by converting the problem of directly solving the governing equations into a loss function optimization problem. It works by integrating the mathematical model into the network and reinforcing the loss function with a residual term from the governing equation, which acts as a penalizing term to restrict the space of acceptable solutions.

**译**：PINN 训练背后的基本思想是：它可以被视为一种无监督策略，不需要标注数据（例如来自先前仿真或实验的结果）。PINN 算法本质上是一种无网格技术，它把"直接求解控制方程"的问题转化为损失函数优化问题，从而求得 PDE 的解。其做法是把数学模型整合进网络，并用来自控制方程的残差项强化损失函数——该残差项充当惩罚项，用以限制可接受解的范围。

> PINNs take into account the underlying PDE, i.e. the physics of the problem, rather than attempting to deduce the solution based solely on data, i.e. by fitting a neural network to a set of state-value pairs. The idea of creating physics-informed learning machines that employ systematically structured prior knowledge about the solution can be traced back to earlier research by Owhadi [125], which revealed the promising technique of leveraging such prior knowledge. Raissi et al [141,142] used Gaussian process regression to construct representations of linear operator functionals, accurately inferring the solution and providing uncertainty estimates for a variety of physical problems; this was then extended in [140,145].

**译**：PINNs 会考虑底层的 PDE，也就是问题的物理机制，而不是试图仅凭数据去推演解（例如把一个神经网络拟合到一组状态—取值对上）。构造"物理信息学习机器"、使其利用关于解的系统化结构化先验知识这一想法，可追溯到 Owhadi 更早的研究 [125]，该研究揭示了利用此类先验知识这一有前景的技术。Raissi 等人 [141,142] 使用高斯过程回归来构造线性算子泛函的表示，为多种物理问题准确地推断解并给出不确定性估计；这一工作随后在 [140,145] 中得到扩展。

<!-- 后续批次：1.1 节续（PINNs 的起源与变体，原文页码 3 中后段）起 -->
