# Understanding Physics-Informed Neural Networks: Techniques, Applications, Trends, and Challenges
# 理解物理信息神经网络：技术、应用、趋势与挑战

> **原文出处**：Farea, A.; Yli-Harja, O.; Emmert-Streib, F. Understanding Physics-Informed Neural Networks: Techniques, Applications, Trends, and Challenges. *AI* **2024**, *5*, 1534–1557. https://doi.org/10.3390/ai5030074
> **译文说明**：双语段落级对照。公式、符号、软件名、参考文献条目保留原文；术语遵循 `00_术语表_PINN统一译法.md`。
> **翻译进度**：封面信息 + 摘要 + §1 引言 + §2 背景 + §3 方法学（开头）已完成；§3.1 起为后续批次。

---

## 封面信息 / Front Matter

**引文格式**

> Citation: Farea, A.; Yli-Harja, O.; Emmert-Streib, F. Understanding Physics-Informed Neural Networks: Techniques, Applications, Trends, and Challenges. AI 2024, 5, 1534–1557. https://doi.org/10.3390/ai5030074

> Academic Editor: Giovanni Diraco
> Received: 16 July 2024 / Revised: 7 August 2024 / Accepted: 19 August 2024 / Published: 29 August 2024
> Copyright: © 2024 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license.

**译**：学术编辑：Giovanni Diraco；收稿日期 2024 年 7 月 16 日；修回 2024 年 8 月 7 日；接收 2024 年 8 月 19 日；发表 2024 年 8 月 29 日。版权 © 2024 归作者所有。出版方：瑞士巴塞尔 MDPI。本文为开放获取论文，遵循 Creative Commons Attribution（CC BY）许可协议的条款与条件。

**文章类型**：Review（综述）

**题目**

> Understanding Physics-Informed Neural Networks: Techniques, Applications, Trends, and Challenges

**译**：理解物理信息神经网络：技术、应用、趋势与挑战

**作者与单位**

> Amer Farea 1,2, Olli Yli-Harja 1,3 and Frank Emmert-Streib 1,*

**译**：Amer Farea ^1,2^、Olli Yli-Harja ^1,3^、Frank Emmert-Streib ^1,\*^

> 1 Predictive Society and Data Analytics Lab, Faculty of Information Technology and Communication Sciences, Tampere University, 33720 Tampere, Finland; amer.farea@tuni.fi (A.F.); olli.yli-harja@tuni.fi (O.Y.-H.)
> 2 Faculty of Engineering and Information Technology, Taiz University, Taiz P.O. Box 6803, Yemen
> 3 Institute for Systems Biology, Seattle, WA 98195, USA
> \* Correspondence: frank.emmert-streib@tuni.fi

**译**：
1 芬兰坦佩雷大学 信息技术与通信科学学院 预测社会与数据分析实验室，33720 坦佩雷，芬兰；amer.farea@tuni.fi（A.F.）；olli.yli-harja@tuni.fi（O.Y.-H.）
2 也门塔伊兹大学 工程与信息技术学院，塔伊兹 P.O. Box 6803，也门
3 美国系统生物学研究所，西雅图 WA 98195，美国
\* 通信作者：frank.emmert-streib@tuni.fi

---

## 摘要 / Abstract

> Physics-informed neural networks (PINNs) represent a significant advancement at the intersection of machine learning and physical sciences, offering a powerful framework for solving complex problems governed by physical laws.

**译**：物理信息神经网络（PINNs）代表了机器学习与物理科学交叉领域的一项重要进展，为求解受物理定律支配的复杂问题提供了强有力的框架。

> This survey provides a comprehensive review of the current state of research on PINNs, highlighting their unique methodologies, applications, challenges, and future directions.

**译**：本综述对 PINNs 研究的当前状况进行了全面回顾，重点介绍其独特的方法学、应用、挑战与未来方向。

> We begin by introducing the fundamental concepts underlying neural networks and the motivation for integrating physics-based constraints. We then explore various PINN architectures and techniques for incorporating physical laws into neural network training, including approaches to solving partial differential equations (PDEs) and ordinary differential equations (ODEs).

**译**：我们首先介绍神经网络背后的基本概念，以及引入基于物理的约束的动机；随后探讨各类 PINN 架构，以及将物理定律融入神经网络训练的技术，包括求解偏微分方程（PDEs）与常微分方程（ODEs）的方法。

> Additionally, we discuss the primary challenges faced in developing and applying PINNs, such as computational complexity, data scarcity, and the integration of complex physical laws. Finally, we identify promising future research directions.

**译**：此外，我们讨论了开发与应用 PINNs 过程中面临的主要挑战，例如计算复杂度、数据稀缺，以及复杂物理定律的整合。最后，我们指出了若干有前景的未来研究方向。

> Overall, this survey seeks to provide a foundational understanding of PINNs within this rapidly evolving field.

**译**：总体而言，本综述旨在为这一快速演进的领域提供对 PINNs 的基础性理解。

**关键词 / Keywords**

> physics-informed neural networks; data-driven modeling; neural network architectures; inverse problems; ordinary differential equations; partial differential equations

**译**：物理信息神经网络；数据驱动建模；神经网络架构；逆问题；常微分方程；偏微分方程

---

## 1. Introduction / 1. 引言

> Neural networks (NNs), inspired by the biological structure of the human brain, have surged in popularity due to their ability to discern complex patterns and make predictions from data [1–3]. These models comprise interconnected nodes (neurons) organized into layers, each performing a simple mathematical operation. During a process known as training, NNs adjust their internal parameters to minimize the error between predicted and actual outputs, learning effectively from examples in a dataset. Over time, they have been successfully applied in fields such as computer vision, natural language processing, genetics, and cognitive science [4,5].

**译**：神经网络（NNs）受人类大脑生物结构的启发，因其能够从数据中辨识复杂模式并作出预测而迅速流行起来 [1–3]。这类模型由相互连接的节点（神经元）组成，节点按层组织，每个节点执行一次简单的数学运算。在被称为"训练"的过程中，神经网络调整其内部参数，以最小化预测输出与实际输出之间的误差，从而有效地从数据集中的样本进行学习。随着时间推移，它们已被成功应用于计算机视觉、自然语言处理、遗传学和认知科学等领域 [4,5]。

> Physics-informed neural networks (PINNs) are a specialized type of neural network that integrates physics principles into their learning process [6–8]. Unlike traditional NNs that rely solely on data, PINNs incorporate domain-specific knowledge and physical laws to enhance their predictive capabilities, particularly in scientific and engineering contexts. By combining data-driven learning with physics-based constraints, PINNs offer a robust framework for solving complex problems governed by partial differential equations (PDEs), ordinary differential equations (ODEs), and other mathematical formulations [9–11]. This fusion enables the efficient and accurate modeling of physical phenomena, making PINNs well-suited for tasks like simulating fluid dynamics, predicting material properties, and solving inverse problems [12,13].

**译**：物理信息神经网络（PINNs）是一类专门的神经网络，将物理原理整合进其学习过程 [6–8]。与仅依赖数据的传统神经网络不同，PINNs 融入领域特定的知识与物理定律以增强其预测能力，在科学与工程场景中尤为如此。通过将数据驱动学习与基于物理的约束相结合，PINNs 为求解由偏微分方程（PDEs）、常微分方程（ODEs）及其他数学形式所支配的复杂问题提供了稳健的框架 [9–11]。这种融合使得对物理现象的高效而准确的建模成为可能，使 PINNs 特别适合流体动力学模拟、材料属性预测和逆问题求解等任务 [12,13]。

> PINNs have emerged as a transformative approach at the intersection of machine learning and physical sciences, offering a novel paradigm for tackling complex problems governed by physical laws. By integrating principles from both fields, PINNs allow researchers to leverage the expressive power of NNs while adhering to fundamental physical constraints.

**译**：PINNs 已成为机器学习与物理科学交叉领域的一种变革性方法，为应对受物理定律支配的复杂问题提供了新的范式。通过整合两个学科的原理，PINNs 使研究者既能利用神经网络的表达能力，又能遵守基本的物理约束。

> Traditionally, machine learning and physics have operated independently, each addressing distinct challenges. Machine learning excels at uncovering complex patterns in data but often struggles to incorporate prior knowledge or enforce physical constraints [14,15]. Conversely, physics-based modeling, such as finite element methods or computational fluid dynamics, relies on explicit physical equations but may encounter scalability or generalization issues in complex real-world scenarios. PINNs bridge this gap by combining the flexibility of NNs with the rigor of physics principles [6].

**译**：传统上，机器学习与物理学各自独立发展，处理的是不同的问题。机器学习擅长发掘数据中的复杂模式，但往往难以融入先验知识或施加物理约束 [14,15]。反之，基于物理的建模方法（如有限元方法或计算流体力学）依赖显式的物理方程，但在复杂的真实场景中可能遭遇可扩展性或泛化性问题。PINNs 通过将神经网络的灵活性与物理原理的严谨性相结合，弥合了这一鸿沟 [6]。

> Embedding physical laws into the learning process, PINNs provide a powerful framework for solving forward and inverse problems across various domains, including fluid dynamics, material science, and quantum mechanics. This integration enhances predictive accuracy, offers insights into physical phenomena, and facilitates the discovery of new scientific principles [16–18].

**译**：通过将物理定律嵌入学习过程，PINNs 为跨多个领域求解正问题与逆问题提供了强有力的框架，涵盖流体动力学、材料科学和量子力学等。这种整合提升了预测精度，加深了对物理现象的洞察，并促进了新科学原理的发现 [16–18]。

> This paper is organized as follows: we start by providing background information (Section 2). Section 3 explores PINN architectures, techniques for integrating physical laws, and solving differential equations. In Section 5, we examine PINN applications. Section 6 discusses challenges and limitations. The Future Directions section (Section 7) outlines potential advances in algorithmic techniques, interdisciplinary collaborations, scalability, and addressing robustness issues. Finally, we provide concluding remarks in Section 8.

**译**：本文的组织结构如下：首先介绍背景信息（第 2 节）；第 3 节探讨 PINN 架构、整合物理定律的技术以及微分方程的求解；第 5 节考察 PINN 的应用；第 6 节讨论挑战与局限；未来方向部分（第 7 节）勾勒算法技术、跨学科协作、可扩展性以及稳健性问题的潜在进展；最后在第 8 节给出结论。

> **〔译者注〕** 原文此处遗漏了第 4 节（4. Utility of PINNs，PINNs 的用途），直接由第 3 节跳至第 5 节。译文忠实保留原文表述，不影响后续章节的编号。

---

## 2. Background / 2. 背景

> Neural networks, a subset of machine learning models [19], have achieved remarkable success in various applications, ranging from computer vision [20–22], speech recognition [23], and natural language processing [24–27] to material science, fluid mechanics [28], genetics [29], cognitive science [30], genomics [31], and infrastructural health monitoring [32]. These models consist of multiple layers of interconnected neurons that process and learn from vast amounts of data. Through training utilizing techniques such as back-propagation and gradient descent, NNs iteratively adjust their weights to minimize prediction errors, thereby improving their performance.

**译**：神经网络是机器学习模型的一个子集 [19]，已在多种应用中取得显著成功，从计算机视觉 [20–22]、语音识别 [23]、自然语言处理 [24–27]，到材料科学、流体力学 [28]、遗传学 [29]、认知科学 [30]、基因组学 [31] 以及基础设施健康监测 [32]。这类模型由多层相互连接的神经元构成，能够处理并从海量数据中学习。通过采用反向传播和梯度下降等技术进行训练，神经网络迭代地调整其权重以最小化预测误差，从而提升自身性能。

> Interestingly, the remarkable success of NNs in data-driven applications does not seamlessly extend to problems governed by complex physical laws. Many scientific and engineering problems, such as fluid dynamics, structural mechanics, and heat transfer, are described by PDEs that encapsulate the underlying physical principles. Unfortunately, traditional NNs do not inherently understand these physical principles but rely solely on data to learn accurate representations, and for this reason may produce physically inconsistent results. This limitation is particularly pronounced in scenarios where data are scarce or noisy.

**译**：有意思的是，神经网络在数据驱动应用中的显著成功并不能顺理成章地延伸到受复杂物理定律支配的问题上。许多科学与工程问题——例如流体动力学、结构力学和传热——都由封装了底层物理原理的偏微分方程来描述。遗憾的是，传统神经网络并不天然理解这些物理原理，而仅依赖数据去学习准确的表征，因此可能产生物理上不自洽的结果。在数据稀缺或含噪的场景中，这一局限尤为突出。

> To improve this shortcoming, PINNs have emerged as a powerful paradigm that integrates physical laws directly into the machine learning process. The core idea behind PINNs is to embed the governing equations of the physical system into the neural network's architecture or loss function. This is typically achieved by incorporating these equations into the loss function, which the network seeks to optimize during training. By doing so, PINNs ensure that the learned solutions not only fit the data but also adhere to the physical constraints imposed by the PDEs. This approach reduces the reliance on large datasets and leverages the strengths of both physics-based modeling and data-driven learning, resulting in models that are more accurate, generalizable, and interpretable.

**译**：为改善这一缺陷，PINNs 作为一种强有力的范式出现，将物理定律直接整合进机器学习过程。PINNs 的核心思想是把物理系统的控制方程嵌入神经网络的架构或损失函数之中。这通常通过将这些方程纳入损失函数来实现，网络在训练中即朝着优化该损失函数的方向进行。如此，PINNs 能够确保学习到的解不仅拟合数据，而且遵守 PDEs 所施加的物理约束。该方法降低了对大型数据集的依赖，并同时发挥基于物理建模与数据驱动学习两者的优势，从而得到更准确、更具泛化能力且更可解释的模型。

> The development of PINNs can be seen as part of a broader movement towards hybrid models that combine the deductive rigor of classical physics with the inductive power of machine learning. This fusion offers several advantages. First, it reduces the dependency on large datasets, as the physical laws provide a priori knowledge that guides the learning process. Second, it enhances the robustness and reliability of the models, ensuring that the predictions are physically consistent even in regions where data are sparse. Third, it opens up new avenues for solving inverse problems, where the goal is to infer unknown parameters or inputs from observed outputs, by leveraging both data and physical laws.

**译**：PINNs 的发展可被视为一场更广泛的运动的一部分——走向混合模型，把经典物理学的演绎严谨性与机器学习的归纳能力结合起来。这种融合带来若干优势。第一，它降低了对大型数据集的依赖，因为物理定律提供了引导学习过程的先验知识。第二，它增强了模型的稳健性与可靠性，确保即使在数据稀疏的区域，预测结果也在物理上自洽。第三，它为求解逆问题开辟了新途径——逆问题的目标是从观测到的输出反推未知参数或输入——其手段正是同时利用数据与物理定律。

---

## 3. Methodologies / 3. 方法学

> In this survey, we explore PINNs, focusing on their core methodologies and innovations. We review key applications across diverse fields, compare PINNs with traditional numerical methods, and discuss their advantages and challenges. We also examine recent trends and future directions, identifying potential areas for further research and application. This includes highlighting the benefits of PINNs over traditional methods and other machine learning approaches, as well as their limitations.

**译**：在本综述中，我们探讨 PINNs，聚焦其核心方法与创新之处。我们回顾跨不同领域的关键应用，将 PINNs 与传统数值方法进行比较，并讨论其优势与挑战。我们还考察近期趋势与未来方向，识别值得进一步研究与应用的潜在领域。这包括强调 PINNs 相对传统方法及其他机器学习方法的优势，同时也指出其局限。

**Related Work and Contribution / 相关工作与本文贡献**

> Previous reviews on PINNs can be found in [6,8,12,28,33,34]. However, these surveys are different in the follows ways. First, due to the origin of PINNs, many reviews focus on applications within physics, e.g., [6,12,28,35], and do not explore the full potential in general application domains. Second, reviews that do address non-physical applications focus only on one particular domain, e.g., [36–38]. Yet other reviews focus on bibliometric aspects of the literature about PINNs without going into methodological details [34] or provide only brief overviews [33,39]. In contrast, our survey provides a comprehensive yet balanced overview of the state-of-the-art research on PINNs.

**译**：关于 PINNs 的既有综述可见于 [6,8,12,28,33,34]。然而，这些综述在以下方面有所不同。第一，由于 PINNs 的学科起源，许多综述聚焦于物理学内部的应用，例如 [6,12,28,35]，并未探索其在一般应用领域中的全部潜力。第二，确实涉及非物理应用的综述又只聚焦于某一个特定领域，例如 [36–38]。还有一些综述关注 PINNs 文献的文献计量学层面，而未深入方法学细节 [34]，或者只提供简略概述 [33,39]。相比之下，本综述对 PINNs 的最新研究提供了全面而均衡的概览。

> Specifically, our survey covers fundamental concepts, including an introduction to NNs and the motivations behind integrating physics-based constraints; methodologies, detailing various architectures and techniques used in PINNs for solving differential equations and inverse problems; applications, reviewing the diverse uses of PINNs across scientific domains; challenges and limitations, analyzing issues such as computational complexity, data scarcity, and the integration of complex physical laws; and future directions, exploring promising research avenues and emerging trends.

**译**：具体而言，本综述涵盖：基本概念，包括神经网络简介以及引入基于物理约束的动机；方法学，详述 PINNs 中用于求解微分方程与逆问题的各类架构与技术；应用，回顾 PINNs 在各科学领域中的多样化使用；挑战与局限，分析计算复杂度、数据稀缺以及复杂物理定律整合等问题；以及未来方向，探索有前景的研究路径与新兴趋势。

### 3. 方法学正文

> Deep learning has become widely adopted in scientific and engineering fields due to its ability to model complex relationships in various data types without requiring users to understand the system's physical parameters. Despite its versatility and effectiveness, challenges such as insufficient training data, lack of interpretability, and disregard for physical laws persist. To address these issues, enhanced methods have been developed, including physics-informed deep learning [7,11,40–43]. In this section, we discuss the methodologies employed in various studies related to PINNs.

**译**：深度学习已在科学与工程领域被广泛采用，因为它能够对多种数据类型中的复杂关系进行建模，而无需使用者理解系统的物理参数。尽管深度学习具备通用性与有效性，训练数据不足、缺乏可解释性以及无视物理规律等挑战依然存在。为解决这些问题，人们发展出若干增强方法，其中包括物理信息深度学习 [7,11,40–43]。本节中，我们讨论与 PINNs 相关的各类研究所采用的方法学。

> Our aim is to provide an overview of the diverse approaches utilized in the development, implementation, and evaluation of PINNs across different domains. From the choice of neural network architectures to the integration of physics-based constraints, each methodology offers unique insights into the fusion of machine learning and physics. By examining the methodologies in detail, we aim to uncover commonalities, challenges, and opportunities within the burgeoning field of PINNs.

**译**：我们的目标是对不同领域中 PINNs 的开发、实现与评估所使用的多样化方法作一概览。从神经网络架构的选择到基于物理约束的整合，每一种方法学都为机器学习与物理学的融合提供了独特见解。通过细致考察这些方法学，我们希望揭示 PINNs 这一新兴领域内部的共性、挑战与机遇。

> The integration of prior knowledge into PINNs can be achieved through feature engineering, model construction, and regularization, as illustrated in Figure 1. The approach depends on the problem's nature and the type of neural network model being employed. By leveraging domain-specific knowledge and known physical principles, PINNs can achieve more accurate and interpretable predictions for various scientific and engineering applications.

**译**：先验知识可以通过特征工程、模型构建和正则化三种方式整合进 PINNs，如图 1 所示。具体采用哪种途径，取决于问题的性质以及所使用的神经网络模型类型。通过利用领域特定知识与已知的物理原理，PINNs 能够在各类科学与工程应用中实现更准确、更可解释的预测。

**图 1 题注**

> Figure 1. The general workflow for integrating prior knowledge into a neural network architecture to create a Physics-Informed Neural Network (PINN).

**译**：图 1. 将先验知识整合进神经网络架构、从而构建物理信息神经网络（PINN）的一般工作流程。

> **〔图 1 内容示意〕** 流程为：Define Problem（定义问题）→ Data Acquisition（数据获取）→ Pre-process Data（数据预处理）→ NN Model（神经网络模型）→ Cost Function（代价函数）→ Train Model（训练模型）→ Evaluation Model（评估模型）。其中两条支路汇入网络构建：Feature Engineering（特征工程）与 Model Construction（模型构建）；先验知识（Prior Knowledge）通过 Additional Cost/Regularization（附加代价 / 正则化）注入代价函数。

---

> Different types of knowledge representation can be integrated into PINNs architecture to enhance their effectiveness [33,44–46].

**译**：不同类型的知识表示可以整合进 PINN 的架构之中，以增强其有效性 [33,44–46]。

### 3.1. Feature Engineering / 3.1. 特征工程

> Feature engineering plays a crucial role in structured data representation, leveraging prior knowledge from shared parameters in source data to enhance understanding of target data. For example, in fluid dynamics, features such as velocity, pressure, and temperature can significantly improve model learning and generalization. Incorporating additional features through physics-driven approaches, such as simulations, physical constraints, and governing equations, can be highly beneficial. These enhance learning by adding features derived from known physics equations or principles to the input data, facilitating more effective learning and generalization [47].

**译**：特征工程在结构化数据表示中起着关键作用，它利用源数据中共享参数所携带的先验知识，来增进对目标数据的理解。例如在流体动力学中，速度、压力、温度等特征能够显著改善模型的学习与泛化。通过物理驱动的方式——如仿真、物理约束和控制方程——引入额外特征，可能大有裨益。这些做法把由已知物理方程或原理导出的特征加入输入数据，从而促进更有效的学习与泛化 [47]。

> Structured data representation can also be integrated into model construction by designing neural network architectures that account for the data's underlying structure. For instance, Convolutional Neural Networks (CNNs) are suitable for grid-structured data like images, while Graph Neural Networks (GNNs) are designed for graph-structured data. This involves creating network structures that mirror the physical characteristics of the system or the data's nature. Examples include task-specific autoencoders, recurrent cells, or physics-inspired convolution filters, as outlined in the next section.

**译**：结构化数据表示也可以通过设计顾及数据底层结构的神经网络架构，整合进模型构建之中。例如，卷积神经网络（CNNs）适合图像这类网格结构数据，而图神经网络（GNNs）则是为图结构数据设计的。这意味着创建能够映照系统物理特性或数据本质的网络结构，其例子包括任务专用的自编码器、循环单元，或受物理启发的卷积滤波器——下一节将对此展开说明。

> For problems involving temporal dependencies, feature engineering involves designing time-dependent features or incorporating lagged variables to capture temporal relationships. Domain-specific knowledge can guide feature selection. Recurrent Neural Networks (RNNs) are ideal for handling sequential data and modeling temporal evolution in PINNs. Regularization techniques like temporal smoothing ensure smooth transitions and consistency in predictions over time.

**译**：对于涉及时间依赖的问题，特征工程包括设计随时间变化的特征，或引入滞后变量以捕捉时间上的关联。领域特定知识可以指导特征选择。循环神经网络（RNNs）非常适合处理序列数据，并在 PINNs 中建模时间演化。诸如时间平滑之类的正则化技术，可确保预测随时间平滑过渡并保持一致性。

### 3.2. Model Construction / 3.2. 模型构建

> Neural networks include various architectures designed to integrate predefined cost functions into their learning process for accurate predictions. Their performance can be enhanced by incorporating prior knowledge to comply with physical constraints and governing laws when necessary. Several key architectures have emerged, each with distinct strengths [48].

**译**：神经网络包含多种架构，其设计目的是在学习过程中整合预定义的代价函数，以实现准确预测。在必要时，通过引入先验知识以符合物理约束与控制定律，可以提升其性能。目前已经出现了若干关键架构，各有其独特优势 [48]。

**Artificial Neural Networks (ANNs) / 人工神经网络（ANNs）**

> A fully connected neural network [49,50], often referred to as a dense ANN, consists of interconnected layers, where each neuron in one layer is linked to every neuron in the next layer [51,52]. Mathematically, the output y of a single layer is computed as the activation function f applied to the weighted sum z of the inputs x with corresponding weights W and biases b, represented as follows:

**译**：全连接神经网络 [49,50] 常被称为稠密 ANN，它由相互连接的层构成，其中某一层的每个神经元都与下一层的每个神经元相连 [51,52]。在数学上，单层的输出 y 由激活函数 f 作用于输入的加权和 z 得到，其中输入 x 对应权重 W 与偏置 b，表示如下：

```
z = Wx + b            (1)
y = f (z)             (2)
```

> In the context of multiple layers, denoted by n, the process is iterated for each layer. Specifically, for the i-th layer, the output y(i) is computed as follows:

**译**：在多层情形下（层数记为 n），该过程对每一层迭代进行。具体而言，第 i 层的输出 y^(i)^ 计算如下：

```
z^(i) = W^(i) y^(i−1) + b^(i)     (3)
y^(i) = f (z^(i))                 (4)
```

> where y(0) represents the input vector x, and W(i) and b(i) denote the weight matrix and bias vector of the i-th layer, respectively. This recursive computation through layers enables the network to capture complex relationships within the data.

**译**：其中 y^(0)^ 表示输入向量 x，W^(i)^ 与 b^(i)^ 分别表示第 i 层的权重矩阵与偏置向量。这种逐层递归计算使网络能够捕捉数据中的复杂关系。

> Moreover, during training, the network aims to minimize a predefined cost function J, often represented as the mean squared error (MSE) for regression problems or cross-entropy for classification tasks. For example, in the case of MSE, the cost function can be written as follows:

**译**：此外，在训练过程中，网络旨在最小化一个预定义的代价函数 J，在回归问题中通常取均方误差（MSE），在分类任务中则常用交叉熵。以 MSE 为例，代价函数可写为：

```
J(W, b) = (1/m) Σ_{i=1}^{m} (y_i − ŷ_i)^2      (5)
```

> where m is the number of training examples, yi represents the true output, and ŷi represents the predicted output. ANNs are often used in PINNs for their simplicity and effectiveness in learning complex relationships; see [53–58].

**译**：其中 m 是训练样本数，y_i 表示真实输出，ŷ_i 表示预测输出。由于结构简单且能有效学习复杂关系，ANNs 常被用于 PINNs 中；参见 [53–58]。

**Convolutional Neural Networks (CNNs) / 卷积神经网络（CNNs）**

> A CNN shares similarities with ANNs but includes convolution layers [59–61]. CNNs are particularly useful for problems involving grid-structured data, such as images or spatio-temporal data [59,62]. However, they can also accommodate numerical data with the utilization of a 1D CNN as the foundational model. The distinguishing characteristic of CNNs lies in their utilization of convolution filters, also known as kernels. These filters, square in shape, are applied to the input pixels through a process of convolution, traversing each square defined by a user-specified filter size and stride. By consistently employing the same filter across the input pixels, CNNs manage to maintain a concise set of hyperparameters [63].

**译**：CNN 与 ANN 有相似之处，但包含卷积层 [59–61]。CNN 对涉及网格结构数据的问题尤为有用，例如图像或时空数据 [59,62]。不过，使用一维 CNN 作为基础模型时，它们同样可以处理数值数据。CNN 的显著特征在于其对卷积滤波器（又称卷积核）的使用。这些滤波器呈方形，通过卷积过程作用于输入像素，按照用户指定的滤波器尺寸与步长逐块遍历。由于在输入像素上始终使用同一个滤波器，CNN 得以维持一套精简的超参数 [63]。

> A convolutional layer consists of multiple kernels that generate feature maps. Each neuron in a feature map is connected to a localized region (receptive field) in the previous layer. To obtain a feature map, the input is convolved with a kernel, followed by applying a nonlinear activation function [60]. Mathematically, the feature value zl i,j,k at position (i, j) in the k-th feature map of the l-th layer is computed as follows:

**译**：一个卷积层包含多个卷积核，用以生成特征图。特征图中的每个神经元连接到前一层的一个局部区域（感受野）。要得到一个特征图，需将输入与某个卷积核做卷积，随后施加非线性激活函数 [60]。在数学上，第 l 层第 k 个特征图中位置 (i, j) 处的特征值 z^(l)_{i,j,k} 计算如下：

```
z^(l)_{i,j,k} = (w^(l)_k)^T x^(l)_{i,j} + b^(l)_k      (6)
```

> where wl k is the k-th filter's weight vector, bl k is its bias, and xl i,j is the input patch at (i, j). Following the convolution operation, an activation function a(·) is applied elementwise to introduce non-linearity:

**译**：其中 w^(l)_k 是第 k 个滤波器的权重向量，b^(l)_k 是其偏置，x^(l)_{i,j} 是 (i, j) 处的输入图块。卷积运算之后，逐元素施加激活函数 a(·) 以引入非线性：

```
a^(l)_{i,j,k} = a( z^(l)_{i,j,k} )      (7)
```

> Subsequently, pooling layers are often employed to downsample the feature maps obtained from the convolutional layers, reducing dimensionality while preserving important information. A common pooling operation is max pooling, where the maximum value within a local region is retained.

**译**：随后，通常使用池化层对卷积层得到的特征图进行下采样，在降低维度的同时保留重要信息。一种常见的池化操作是最大池化，即保留局部区域内的最大值。

```
y^(l)_{i,j,k} = pool( a^(l)_{m,n,k} ),  ∀(m, n) ∈ R_{i,j}      (8)
```

> where (m, n) represents the local neighborhood around (i, j), and Ri,j is the region of the input map being pooled. Common pooling operations include average pooling and max pooling.

**译**：其中 (m, n) 表示 (i, j) 周围的局部邻域，R_{i,j} 是被池化的输入图区域。常见的池化操作包括平均池化与最大池化。

> In CNNs, the training process typically involves minimizing a loss function Ltotal, which combines a standard loss function Lstd with a regularization term to prevent overfitting. This regularization term can include weight decay or dropout, among others. The total loss function is defined as follows:

**译**：在 CNN 中，训练过程通常包括最小化损失函数 L_total，它由一个标准损失函数 L_std 与一个防止过拟合的正则化项组合而成。该正则化项可以包含权重衰减、随机失活（dropout）等。总损失函数定义如下：

```
L_total = L_std + λ L_reg        (9)
```

> where λ is a hyperparameter controlling the regularization strength. This integrated approach allows for CNNs to effectively learn complex features from grid-structured data while mitigating the risk of overfitting during the training phase. In PINNs, CNNs can be employed when the problem involves spatial or spatio-temporal dependencies, see [41,64–70].

**译**：其中 λ 是控制正则化强度的超参数。这种整合式做法使 CNN 能够从网格结构数据中有效学习复杂特征，同时在训练阶段降低过拟合风险。在 PINNs 中，当问题涉及空间依赖或时空依赖时，可以采用 CNN，参见 [41,64–70]。

**Recurrent Neural Networks (RNNs) / 循环神经网络（RNNs）**

> RNNs are designed for handling time-series data [71,72]. This capability stems from the recursive arrangement of their hidden layers,

**译**：RNN 是为处理时间序列数据而设计的 [71,72]。这一能力源于其隐层的递归式排布，

> enabling them not only to generate outputs at specific time points but also to transmit hidden states to subsequent layers. Depending on the RNN variant, outputs at each time step may also be relayed forward. Conceptually, RNNs can be thought of as multiple instances of a standard ANN, with each instance communicating information to its successor [73–75]. This adaptation empowers RNNs to model data across individual time steps and the interconnections among them.

**译**：这使它们不仅能够在特定时间点生成输出，还能把隐状态传递给后续层。视 RNN 变体不同，每个时间步的输出也可能向前传递。从概念上讲，RNN 可被视为标准 ANN 的多个实例，每个实例把信息传递给其后继者 [73–75]。这一改造使 RNN 能够对各个时间步上的数据以及它们之间的相互关联进行建模。

> RNN architectures can vary to suit different problem types. Structurally, RNNs may operate in one-to-one, one-to-many, many-to-one, or many-to-many configurations [76,77]. A notable application of the many-to-many RNN structure is found in machine translation tasks. For instance, in a translation scenario, the encoder component of the network receives input words in English, while the decoder component generates corresponding translated words in French.

**译**：RNN 架构可以变化以适配不同问题类型。在结构上，RNN 可以按一对一、一对多、多对一或多对多等配置运行 [76,77]。多对多 RNN 结构的一个典型应用见于机器翻译任务。例如在翻译场景中，网络的编码器部分接收英文输入词，解码器部分则生成对应的法语译词。

> In dynamical systems, governing equations often describe the system's behavior over time, frequently taking the form of differential equations. These equations represent a valuable source of prior knowledge. RNNs are designed to handle sequential data by maintaining an internal state or memory of past inputs. Mathematically, a recurrent neural network can be represented as follows:

**译**：在动力系统中，控制方程往往描述系统随时间的行为，且常常以微分方程的形式出现。这些方程是宝贵的先验知识来源。RNN 通过维护内部状态或对既往输入的记忆来处理序列数据。在数学上，循环神经网络可表示如下：

```
h_t = f (W_hh h_{t−1} + W_xh x_t + b_h)
y_t = g (W_hy h_t + b_y)                       (10)
```

> where ht is the hidden state at time t; xt is the input at time t; Whh, Wxh, Why are weight matrices; bh and by are bias vectors; f is the activation function for the hidden layer; and g is the activation function for the output layer.

**译**：其中 h_t 为 t 时刻的隐状态；x_t 为 t 时刻的输入；W_hh、W_xh、W_hy 为权重矩阵；b_h 与 b_y 为偏置向量；f 为隐层的激活函数；g 为输出层的激活函数。

> For a given sequence of inputs X = (x1, x2, . . ., xT), the output sequence Y = (y1, y2, . . ., yT) is obtained by iterating the above equations through time steps t = 1, 2, . . . , T. The training of RNNs involves optimizing a cost function J that measures the discrepancy between the predicted outputs and the actual outputs. One common choice for the cost function is the mean squared error:

**译**：对于给定输入序列 X = (x₁, x₂, …, x_T)，通过在时间步 t = 1, 2, …, T 上迭代上述方程，可得到输出序列 Y = (y₁, y₂, …, y_T)。RNN 的训练涉及优化一个代价函数 J，用以度量预测输出与实际输出之间的差异。一种常见的代价函数选择是均方误差：

```
J = (1/T) Σ_{t=1}^{T} ‖ y_t − ŷ_t ‖²          (11)
```

> where ŷt is the target output at time t. In PINNs, RNNs can be employed for solving time-dependent problems governed by ODEs, such as predicting the behavior of dynamic systems over time; see [78–83].

**译**：其中 ŷ_t 是 t 时刻的目标输出。在 PINNs 中，RNN 可用于求解由 ODEs 支配的时间依赖问题，例如预测动态系统随时间的演化行为；参见 [78–83]。

**Graph Neural Networks (GNNs) / 图神经网络（GNNs）**

> Deep learning models primarily focus on structured data like images and text [84,85]. However, data with irregular structures necessitate alternative processing methods. To tackle this challenge, GNNs have been developed, with Graph Convolutional Networks (GCNs) emerging as a prominent variant [84,86,87]. GCNs leverage the graph Fourier transform to extract features from graphs, similar to how CNNs utilize channels. They employ graph filters parameterized by the eigenvalues of a graph Laplacian matrix for feature extraction. The output layer of a GCN varies based on the task at hand; for node classification, a fully connected layer is often used.

**译**：深度学习模型主要关注图像、文本这类结构化数据 [84,85]。然而，结构不规则的数据需要另辟处理途径。为应对这一挑战，人们提出了 GNN，其中图卷积网络（GCNs）成为最突出的一类变体 [84,86,87]。GCN 借助图傅里叶变换从图中提取特征，其作用类似于 CNN 利用通道的方式。它们采用由图拉普拉斯矩阵特征值参数化的图滤波器来进行特征提取。GCN 的输出层随具体任务而变化；对于节点分类，通常使用一个全连接层。

> The mathematical representation of GCNs can involve the following steps: GCNs may utilize a Fourier-like transformation to extract features from graph-structured data. The graph Fourier transform of a signal x on a graph G can be defined as follows:

**译**：GCN 的数学表述可包含以下步骤：GCN 可以利用类似傅里叶的变换从图结构数据中提取特征。图 G 上信号 x 的图傅里叶变换可定义如下：

```
x̂ = U^T x                                    (12)
```

> where U is the matrix of eigenvectors of the graph Laplacian matrix. Then, the GCNs employ graph filters parameterized by the eigenvalues of the graph Laplacian matrix. Given a graph signal x and a filter θ, the filtered signal x̃ is computed as follows:

**译**：其中 U 是图拉普拉斯矩阵的特征向量构成的矩阵。随后，GCN 采用由图拉普拉斯矩阵特征值参数化的图滤波器。给定图信号 x 与滤波器 θ，滤波后的信号 x̃ 计算如下：

```
x̃ = θ(Λ) x = U θ(Λ) U^T x                    (13)
```

> where Λ is the diagonal matrix of eigenvalues of the graph Laplacian matrix. The output layer of a GCN depends on the specific task. For example, for node classification, a fully connected layer followed by a softmax function can be used. The output y is computed as follows:

**译**：其中 Λ 是图拉普拉斯矩阵特征值构成的对角矩阵。GCN 的输出层取决于具体任务。例如对于节点分类，可采用一个全连接层再接 softmax 函数。输出 y 计算如下：

```
y = softmax(W x̃ + b)                          (14)
```

> where W is the weight matrix and b is the bias vector. The cost function for training a GCN depends on the specific task and can be formulated accordingly. For example, for node classification, a common choice is the cross-entropy loss function:

**译**：其中 W 是权重矩阵，b 是偏置向量。训练 GCN 的代价函数取决于具体任务，可相应地构造。例如对于节点分类，常见的选择是交叉熵损失函数：

```
J(θ) = − Σ_{i=1}^{N} Σ_{k=1}^{K} y_{i,k} log( ŷ_{i,k} )      (15)
```

> where N is the number of nodes, K is the number of classes, yi,k is the true label for node i and class k, and ŷi,k is the predicted probability of node i belonging to class k. In the context of PINNs, GNNs can be used to model complex physical systems characterized by interconnected components, such as molecular dynamics simulations or social network analysis; see [85,88–92].

**译**：其中 N 是节点数，K 是类别数，y_{i,k} 是节点 i 在类别 k 上的真实标签，ŷ_{i,k} 是节点 i 属于类别 k 的预测概率。在 PINNs 的语境中，GNN 可用于对由相互连接的部件构成的复杂物理系统建模，例如分子动力学模拟或社交网络分析；参见 [85,88–92]。

**Attention Mechanisms / 注意力机制**

> Attention mechanisms allow for neural networks (NNs) to focus on specific parts of the input data, enabling them to weigh the importance of different features dynamically [93,94]. Mathematically, attention mechanisms can be represented as follows: consider a neural network f with parameter θ, and let x represent the input data. The attention mechanism A(x) assigns weights to different parts of the input, allowing for the network to focus on the most relevant information. This attention mechanism can be formulated as follows:

**译**：注意力机制使神经网络能够聚焦于输入数据的特定部分，从而动态地权衡不同特征的重要性 [93,94]。在数学上，注意力机制可表示如下：考虑一个参数为 θ 的神经网络 f，令 x 表示输入数据。注意力机制 A(x) 为输入的不同部分分配权重，使网络能够聚焦于最相关的信息。该注意力机制可表述为：

```
A(x) = softmax( W_a · ReLU( W_x · x + b_x ) + b_a )      (16)
```

> where Wx, bx, Wa, and ba are learnable parameters, and softmax is the softmax function. The attention-weighted input x̃ is then computed as the element-wise product of the attention weights and the input:

**译**：其中 W_x、b_x、W_a、b_a 是可学习参数，softmax 即 softmax 函数。随后，注意力加权输入 x̃ 由注意力权重与输入逐元素相乘得到：

```
x̃ = A(x) ⊙ x                                   (17)
```

> The attention-weighted input x̃ is then passed through the neural network f to obtain the output y:

**译**：注意力加权输入 x̃ 随后通过神经网络 f，得到输出 y：

```
y = f ( x̃ ; θ)                                 (18)
```

> Finally, the cost function J of the PINN, which incorporates the attention mechanism, can be defined as follows:

**译**：最后，纳入注意力机制的 PINN 的代价函数 J 可定义如下：

```
J(θ) = (1/N) Σ_{i=1}^{N} L(y_i, ŷ_i) + λ R(θ)      (19)
```

> where N is the number of data points, L is the loss function, ŷi is the ground truth label, and λ is the regularization parameter. The term R(θ) represents the regularization term, which penalizes large values of the network parameters θ to prevent overfitting. In PINNs, attention mechanisms can enhance performance by selectively attending to relevant spatial or temporal features, particularly in problems with large or high-dimensional input spaces; see [95–99].

**译**：其中 N 是数据点数量，L 是损失函数，ŷ_i 是真实标签，λ 是正则化参数。R(θ) 项表示正则化项，它惩罚网络参数 θ 的过大取值以防止过拟合。在 PINNs 中，注意力机制通过有选择地关注相关的空间或时间特征来提升性能，在输入空间较大或维度较高的问题中尤为有效；参见 [95–99]。

**Generative models / 生成模型**

> Deep neural networks can be categorized into discriminative [100] and generative models [101] based on their function. Discriminative models predict the target variable given input variables, while generative models model the conditional probability of observable variables given the target. Two prominent generative models are variational autoencoders (VAEs) [102] and generative adversarial networks (GANs) [103]. Mathematically, a VAE can be represented as follows: Let X represent the input data, Z represent the latent space, and θ represent the parameters of the VAE. The encoder qθ(Z|X) maps input data to the latent space distribution, and the decoder pθ(X|Z) reconstructs the input data from the latent space. The objective is to maximize the evidence lower bound (ELBO) given by

**译**：深度神经网络按功能可分为判别模型 [100] 与生成模型 [101]。判别模型在给定输入变量时预测目标变量，而生成模型则对给定目标时可观测变量的条件概率进行建模。两种突出的生成模型是变分自编码器（VAEs）[102] 与生成对抗网络（GANs）[103]。在数学上，VAE 可表示如下：令 X 表示输入数据，Z 表示隐空间，θ 表示 VAE 的参数。编码器 q_θ(Z|X) 把输入数据映射到隐空间分布，解码器 p_θ(X|Z) 则从隐空间重构输入数据。其目标是最大化如下证据下界（ELBO）：

```
L(θ) = E_{qθ(Z|X)} [ log pθ(X|Z) ] − KL( qθ(Z|X) ‖ p(Z) )      (20)
```

> where p(Z) is the prior distribution over the latent space and KL denotes the Kullback–Leibler divergence. A GAN can be represented as follows: In a GAN, a generator network G produces samples from a prior distribution pdata(X), and a discriminator network D distinguishes between real and generated samples. The objective of the generator is to minimize the following cost function:

**译**：其中 p(Z) 是隐空间上的先验分布，KL 表示 Kullback–Leibler 散度。GAN 可表示如下：在 GAN 中，生成器网络 G 从先验分布 p_data(X) 中产生样本，判别器网络 D 则区分真实样本与生成样本。生成器的目标是最小化如下代价函数：

```
min_G max_D V(D, G) = E_{X∼pdata(X)}[ log D(X) ] + E_{Z∼p(Z)}[ log(1 − D(G(Z))) ]      (21)
```

> where V(D, G) represents the value function of the minimax game. In PINNs, autoencoders or VAEs can be employed to learn compact representations of physical systems, enabling efficient modeling and simulation for tasks such as data denoising, feature extraction, or uncertainty estimation; see [40,104–107]. Each of the preceding architectures offers unique advantages and is suited to different types of physical problems.

**译**：其中 V(D, G) 表示极小极大博弈的值函数。在 PINNs 中，可以采用自编码器或 VAE 学习物理系统的紧凑表示，从而为数据去噪、特征提取或不确定性估计等任务提供高效的建模与仿真；参见 [40,104–107]。上述各类架构各有独特优势，适用于不同类型的物理问题。

### 3.3. Incorporating Physical Laws as an Additional Cost Function / 3.3. 把物理定律作为附加代价函数引入

> At the current state of PINN research, the methods discussed in this section are widely used to embed physical laws into neural networks. This ensures the resulting models are not only data-driven but also physically consistent and interpretable. Incorporating physical laws into PINNs is crucial for ensuring that models accurately reflect underlying principles. Various techniques integrate these laws into the loss function, allowing for neural networks to capture intricate relationships while staying true to fundamental principles.

**译**：在 PINN 研究的当前阶段，本节所讨论的方法被广泛用于将物理定律嵌入神经网络。这确保了所得模型不仅由数据驱动，而且在物理上自洽且可解释。把物理定律引入 PINNs 对于保证模型准确反映底层原理至关重要。已有多种技术将这些定律整合进损失函数，使神经网络在忠实于基本原理的同时，能够捕捉错综复杂的关系。

> The most frequent functional form of the loss is the Mean Squared Error (MSE) [7]; the p-norm is also used [108]. In this context, the cost function may include data fidelity and physics regularization terms that penalize deviations from known physical laws during training [109]. Alternatively, it might impose physical constraints based on conservation laws or constitutive relations as equality or inequality constraints on the neural network's output, ensuring that the predictions are physically plausible [110]. Additionally, the cost function can serve as a regularization term in the training objective to enforce physical consistency, penalizing deviations from physical laws while promoting smoothness and stability in the learned solutions [111,112].

**译**：损失最常见的函数形式是均方误差（MSE）[7]，p-范数也有使用 [108]。在此语境下，代价函数可以包含数据保真项与物理正则化项，在训练中惩罚对已知物理定律的偏离 [109]。另一种做法是，基于守恒律或本构关系，把物理约束作为等式或不等式约束施加在神经网络输出上，以确保预测在物理上合理 [110]。此外，代价函数还可以在训练目标中充当正则化项以强制物理一致性，在惩罚偏离物理定律的同时促进所求解的平滑性与稳定性 [111,112]。

> Recent research has shown the feasibility of incorporating structured prior information into data-efficient and physics-informed learning systems. For instance, Gaussian process regression has been used to create tailored functional representations for specific linear operators, enabling precise solution inference and uncertainty assessments in mathematical physics [7,44,113].

**译**：近期研究表明，把结构化的先验信息引入数据高效且物理信息驱动的学习系统是可行的。例如，高斯过程回归已被用于为特定线性算子构造量身定制的函数表示，从而在数学物理中实现精确的解推断与不确定性评估 [7,44,113]。

> The pioneering framework introduced by [7] incorporated physical laws into neural network learning processes, specifically for solving nonlinear PDEs in both forward and inverse problems. This integration of differential equations into the loss functions of a neural network guides the training process using physical constraints. Building on this foundation, Raissi et al. introduced a deep learning framework called Hidden Fluid Mechanics (HFM), extending the concept of PINNs to complex systems governed by coupled and nonlinear PDEs [114]. These early contributions demonstrated the efficacy of PINNs in addressing forward and inverse problems, paving the way for broader adoption and further innovation. Subsequent research has advanced PINNs' capabilities, include developing adaptive activation functions and multi-fidelity approaches to address PDE stiffness and improve

**译**：文献 [7] 提出的开创性框架把物理定律引入神经网络的学习过程，专门用于求解正问题与逆问题中的非线性 PDEs。这种把微分方程整合进神经网络损失函数的做法，以物理约束引导训练过程。在此基础上，Raissi 等人提出了名为隐式流体力学（Hidden Fluid Mechanics, HFM）的深度学习框架，把 PINN 的概念推广到由耦合非线性 PDEs 支配的复杂系统 [114]。这些早期贡献证明了 PINNs 在应对正问题与逆问题上的效力，为其更广泛的采用与后续创新铺平了道路。后续研究进一步提升了 PINNs 的能力，包括发展自适应激活函数与多保真度方法，以应对 PDE 的刚性问题并改善

> convergence rates [115]. Methods incorporating physical equations into deep learning model loss functions, such as those introduced by [41], enable training without labeled data, providing accurate predictions while respecting problem constraints and quantifying predictive uncertainty across diverse scenarios.

**译**：收敛速率 [115]。将物理方程纳入深度学习模型损失函数的方法（例如文献 [41] 所提出的方法），使得无需标注数据即可训练，在遵守问题约束的同时给出准确预测，并能在多种场景下量化预测不确定性。

> Hybrid Approaches combine elements of multiple techniques [6,34], such as physics-based loss functions and constraint-based methods, to simultaneously enforce physical constraints and data-driven objectives. Leveraging the complementary strengths of different techniques, hybrid approaches offer a versatile and effective framework for incorporating physical laws into PINNs.

**译**：混合方法（Hybrid Approaches）把多种技术的要素结合起来 [6,34]，例如基于物理的损失函数与基于约束的方法，以同时施加物理约束并实现数据驱动的目标。借助不同技术之间互补的优势，混合方法为把物理定律引入 PINNs 提供了一个通用而有效的框架。

> Furthermore, advancements in optimization techniques, including physics-informed stochastic gradient descent and adaptive learning rates, have contributed to the robustness and efficiency of PINNs. In this context, Yang et al. [116] introduced the Bayesian physics-informed neural network (B-PINN), which integrates Bayesian neural networks (BNNs) [117] and PINNs to tackle both forward and inverse nonlinear problems involving PDEs and noisy data. B-PINNs leverage physical principles and noisy measurements within a Bayesian framework to provide predictions and evaluate uncertainty. Unlike PINNs, B-PINNs offer more accurate predictions and are better equipped to manage significant levels of noise by addressing overfitting.

**译**：此外，优化技术的进步——包括物理信息随机梯度下降与自适应学习率——也提升了 PINNs 的稳健性与效率。在这一方向上，Yang 等人 [116] 提出了贝叶斯物理信息神经网络（B-PINN），它把贝叶斯神经网络（BNNs）[117] 与 PINNs 结合起来，用于处理涉及 PDEs 与含噪数据的正、逆非线性问题。B-PINNs 在贝叶斯框架内利用物理原理与含噪测量，既给出预测也评估不确定性。与 PINNs 不同，B-PINNs 的预测更准确，并且通过应对过拟合，能更好地处理较强的噪声。

> A systematic comparison between Hamiltonian Monte Carlo (HMC) [118] and variational inference (VI) [119] indicates a preference for HMC for posterior estimation. Furthermore, the substitution of the BNN in the prior with a truncated Karhunen–Loève (KL) expansion combined with HMC or a deep normalizing flow (DNF) model [120] shows potential but lacks scalability for high-dimensional problems.

**译**：对哈密顿蒙特卡洛（HMC）[118] 与变分推断（VI）[119] 的系统比较表明，在后验估计方面 HMC 更受青睐。此外，用截断的 Karhunen–Loève（KL）展开替代先验中的 BNN，并与 HMC 或深度归一化流（DNF）模型 [120] 相结合，显示出潜力，但在高维问题中缺乏可扩展性。

---

## 4. Utility of PINNs / 4. PINNs 的用途

> Differential equations are essential for understanding the dynamic behaviors of physical systems, as they describe how variables change relative to each other and enable predictions about future behavior. However, real-world systems often face challenges due to partially known differential equations:

**译**：微分方程对于理解物理系统的动态行为至关重要，因为它们描述了各变量之间如何相对变化，并使得对未来行为作出预测成为可能。然而，现实世界的系统常常因微分方程仅有部分已知而面临挑战：

> 1. **Unknown Parameters**: For example, in wind engineering [121], the equations of fluid dynamics are established, but coefficients related to turbulent flow are uncertain.

**译**：1. **未知参数**：例如在风工程中 [121]，流体动力学方程已经确立，但与湍流相关的系数并不确定。

> 2. **Unknown Functional Forms**: In chemical engineering [122,123], the exact form of rate equations can be unclear due to uncertainties in reaction pathways.

**译**：2. **未知函数形式**：在化学工程中 [122,123]，由于反应路径存在不确定性，速率方程的确切形式可能并不清楚。

> 3. **Unknown Forms and Parameters**: In battery state modeling [123,124], equivalent circuit models partially capture the current–voltage relationship, and key parameters like resistance and capacitance are unknown.

**译**：3. **未知形式与未知参数**：在电池状态建模中 [123,124]，等效电路模型只能部分刻画电流—电压关系，而电阻、电容等关键参数是未知的。

> This partial knowledge hinders our understanding and control of these systems, making it essential to infer unknown components from observed data, a process known as system identification. This helps in predicting system states, informing control strategies, and enabling theoretical analysis. Recently, Zhang et al. [125] proposed a strategy using PINN and symbolic regression to discover an unknown mathematical model in a system of ODEs. Though focused on Alzheimer's disease modeling, their approach shows potential for general equation discovery.

**译**：这种部分已知的状况妨碍了我们对这些系统的理解与控制，因此必须从观测数据中推断未知成分，这一过程被称为系统辨识。它有助于预测系统状态、为控制策略提供依据，并支持理论分析。近期，Zhang 等人 [125] 提出了一种策略，利用 PINN 与符号回归来发现一个 ODE 系统中的未知数学模型。虽然他们的工作聚焦于阿尔茨海默病建模，但该方法在一般性的方程发现方面显示出潜力。

> For solving differential equations using PINNs as shown below, various approaches exist. The overall process is illustrated in Figure 2, where the residuals of the differential equations are integrated into the loss function to enhance the accuracy of the neural network model. Here, ϵ denotes the acceptable margin of loss.

**译**：如下文所示，使用 PINNs 求解微分方程存在多种途径。整体流程如图 2 所示，其中微分方程的残差被整合进损失函数，以提升神经网络模型的精度。此处 ϵ 表示可接受的损失容限。

**图 2 题注**

> Figure 2. The process depicted involves integrating the residuals of the differential equations (DEs) with dynamics N() into the loss function to improve the accuracy of the neural network (NN) model. Here, ϵ represents the acceptable margin of loss. In this context, the primary role of the neural network is to identify the optimal parameters that minimize the specified loss function while adhering to the initial and boundary conditions. Meanwhile, the supplementary cost function ensures that the constraints of the ODEs/PDEs are met, representing the physical information aspect of the neural network.

**译**：图 2. 图中所示过程将带有动力学 N() 的微分方程（DEs）残差整合进损失函数，以提升神经网络（NN）模型的精度。此处 ϵ 表示可接受的损失容限。在这一框架下，神经网络的主要作用是找出使指定损失函数最小化的最优参数，同时遵守初始条件与边界条件；而附加的代价函数则确保 ODEs/PDEs 的约束得到满足，这正是神经网络中"物理信息"的体现。

> **〔图 2 内容示意〕** 输入 x⃗、t 经隐层（Hidden Layers）得到输出 ŷ；由 ŷ 计算 ∂/∂t、∂/∂x，构成 DE 残差并与 NN 残差一并进入 PINN 损失；损失小于 ϵ 则判定为 Done（完成），否则返回继续训练。图示为 YES/NO 两条分支。

### 4.1. Solving PDEs and ODEs with PINNs / 4.1. 用 PINNs 求解 PDEs 与 ODEs

> Physics-Informed Neural Networks (PINNs) offer a robust framework for solving Partial Differential Equations (PDEs) and Ordinary Differential Equations (ODEs), essential in modeling physical phenomena across various scientific and engineering domains. Several approaches exist for solving these equations with PINNs:

**译**：物理信息神经网络（PINNs）为求解偏微分方程（PDEs）与常微分方程（ODEs）提供了稳健的框架，而这两类方程在跨多个科学与工程领域对物理现象建模时不可或缺。用 PINNs 求解这些方程有多种途径：

> 1. **Finite Difference Methods**: These discretize the spatial and temporal domains of PDEs and ODEs into a grid, approximating derivatives using finite differences. PINNs are trained to learn the solution directly from data at these grid points, leveraging neural networks' flexibility and scalability [126].

**译**：1. **有限差分方法**：将 PDEs 与 ODEs 的空间域与时间域离散为网格，用有限差分近似导数。PINNs 被训练为直接在这些网格点上的数据中学习解，从而发挥神经网络的灵活性与可扩展性 [126]。

> 2. **Collocation Method**: This method enforces differential equations at discrete collocation points throughout the domain. PINNs minimize the residual of the PDEs or ODEs at these points, approximating the solution while satisfying the equations [127].

**译**：2. **配点法**：该方法在整个域内的一系列离散配点上强制满足微分方程。PINNs 在这些点上最小化 PDEs 或 ODEs 的残差，在满足方程的同时逼近解 [127]。

> 3. **Boundary Integral Methods**: These represent the solution to PDEs as an integral over the domain's boundary, reducing dimensionality and simplifying the numerical solution. PINNs trained to learn the boundary integral can solve PDEs with reduced computational cost and memory requirements [128].

**译**：3. **边界积分方法**：将 PDEs 的解表示为沿域边界的一个积分，从而降低维度并简化数值求解。被训练去学习边界积分的 PINNs 能够以更低的计算成本与内存需求求解 PDEs [128]。

> 4. **Deep Galerkin Methods**: These seek to minimize the residual of PDEs or ODEs over the entire domain. PINNs are trained to solve the equations in a strong sense by incorporating physical principles directly into the loss function [129].

**译**：4. **Deep Galerkin 方法**：其目标是在整个域上最小化 PDEs 或 ODEs 的残差。PINNs 通过把物理原理直接纳入损失函数，以强形式求解方程 [129]。

> 5. **Time-Stepping Methods**: These discretize the temporal domain of time-dependent PDEs and ODEs into time steps, evolving the solution forward using iterative updates. PINNs learn the time evolution of the solution directly from data, utilizing neural networks' parallelism and scalability [130].

**译**：5. **时间步进方法**：把时间依赖的 PDEs 与 ODEs 的时间域离散为若干时间步，通过迭代更新使解向前演化。PINNs 直接从数据中学习解的时间演化，利用神经网络的并行性与可扩展性 [130]。

> These approaches collectively provide versatile and efficient means of solving PDEs and ODEs with PINNs, enabling the development of accurate and scalable models for a broad spectrum of scientific and engineering applications.

**译**：这些途径共同为用 PINNs 求解 PDEs 与 ODEs 提供了通用而高效的手段，使人们能够为广泛的科学与工程应用开发准确且可扩展的模型。

### 4.2. Inverse Problems / 4.2. 逆问题

> Inverse problems occur in scientific and engineering disciplines when determining input parameters or conditions that result in specific observed behaviors or outputs. These problems are challenging because they require inferring hidden quantities from limited and noisy data [8,12].

**译**：在科学与工程学科中，当需要确定能够产生特定观测行为或输出的输入参数或条件时，就会出现逆问题。这类问题之所以困难，是因为它们要求从有限且含噪的数据中推断出隐藏的量 [8,12]。

**Regularization / 正则化**

> Such techniques are commonly used in inverse problems to impose constraints on the solution space and prevent overfitting. PINNs can be trained to minimize the discrepancy between predicted and observed data while simultaneously enforcing regularization constraints that ensure the solution remains physically plausible [111]. By incorporating prior knowledge about the underlying physics into the regularization process, PINNs can produce solutions that are both accurate and consistent with known physical principles [109].

**译**：此类技术常用于逆问题中，用于对解的搜索空间施加约束并防止过拟合。可以训练 PINNs 在最小化预测数据与观测数据之间差异的同时，强制施加正则化约束，以确保解在物理上仍然合理 [111]。通过把关于底层物理的先验知识引入正则化过程，PINNs 能够给出既准确又与已知物理原理相一致的解 [109]。

> Usually, regularization techniques in inverse problems are represented using an optimization framework. To give an example, let x represent the unknown parameter vector we aim to estimate, and let yobs represent the observed data. In inverse problems, we typically have a model that relates the parameters x to the observed data ypred through a function F, i.e., ypred = F(x). A basic formulation of the inverse problem is to find the parameter vector x that minimizes the discrepancy between the observed and predicted data. This can be represented as follows:

**译**：通常，逆问题中的正则化技术用优化框架来表示。举例来说，令 x 表示我们想要估计的未知参数向量，y_obs 表示观测数据。在逆问题中，我们通常有一个模型，通过函数 F 把参数 x 与观测数据 y_pred 联系起来，即 y_pred = F(x)。逆问题的一个基本表述是：寻找使观测数据与预测数据之间差异最小的参数向量 x。这可表示如下：

```
min_x ‖ y_obs − F(x) ‖²          (22)
```

> Regularization techniques add a penalty term to the objective function to control the complexity of the solution and prevent overfitting. This penalty term typically depends on some measure of the complexity of the parameter vector x, denoted as Ω(x). A common form of regularization is Tikhonov regularization (also known as ridge regression), where the objective function becomes

**译**：正则化技术向目标函数中添加一个惩罚项，用以控制解的复杂度并防止过拟合。该惩罚项通常取决于对参数向量 x 复杂度的某种度量，记作 Ω(x)。一种常见的正则化形式是 Tikhonov 正则化（又称岭回归），此时目标函数变为

```
min_x ‖ y_obs − F(x) ‖² + λ‖ Ω(x) ‖²          (23)
```

> Here, λ is a regularization parameter that controls the trade-off between fitting the data and the complexity of the solution. The term ‖Ω(x)‖² represents a measure of the norm of the parameter vector x, which could be the L2-norm or another norm depending on the specific regularization technique used. In the context of PINNs, the regularization term Ω(x) could incorporate prior knowledge about the physical principles governing the problem.

**译**：这里 λ 是正则化参数，控制拟合数据与解复杂度之间的权衡。‖Ω(x)‖² 项表示参数向量 x 的范数度量，它可以是 L2 范数，也可以是其他范数，取决于所选用的具体正则化技术。在 PINNs 的语境中，正则化项 Ω(x) 可以纳入关于支配该问题的物理原理的先验知识。

**Bayesian inference / 贝叶斯推断**

> Such methods provide a probabilistic framework for solving inverse problems by estimating the posterior distribution of input parameters based on observed data [116]. This posterior distribution, p(θ|D), can be approximated using PINNs, which train a neural network to map input parameters to the posterior distribution [117]. Mathematically, we express this as follows:

**译**：此类方法提供了一个概率框架，通过基于观测数据估计输入参数的后验分布来求解逆问题 [116]。该后验分布 p(θ|D) 可以用 PINNs 来近似——做法是训练一个神经网络，把输入参数映射到后验分布 [117]。在数学上，我们表示如下：

```
p(θ|D) = p(D|θ) · p(θ) / p(D)          (24)
```

> where p(θ|D) is the posterior distribution of the parameters given the data, p(D|θ) is the likelihood function, representing the probability of observing the data given the parameters, and p(θ) is the prior distribution, representing our initial belief about the parameters before observing any data. The network's output, p̂(θ|D), approximates the true posterior distribution.

**译**：其中 p(θ|D) 是给定数据时参数的后验分布；p(D|θ) 是似然函数，表示在给定参数的情况下观测到该数据的概率；p(θ) 是先验分布，表示我们在观测任何数据之前对参数的初始信念。网络的输出 p̂(θ|D) 用于近似真实的后验分布。

> By incorporating physics-based priors, which encode known physical laws or constraints, PINNs enhance the accuracy and reliability of parameter estimates, even with limited and noisy data. This approach leverages domain knowledge during the inference process, producing more accurate results.

**译**：通过引入基于物理的先验——即编码了已知物理定律或约束的先验——PINNs 即使在数据有限且含噪的情况下也能提升参数估计的准确性与可靠性。该方法在推断过程中利用了领域知识，从而产生更准确的结果。

**Data assimilation / 数据同化**

> By employing data assimilation techniques, observational data can be combined with numerical models to produce optimal estimates of the state variables and parameters of a dynamical system [112]. PINNs can be used to assimilate observational data into physics-based models, effectively constraining the model predictions to be consistent with the observed data.

**译**：借助数据同化技术，可以把观测数据与数值模型结合起来，从而对动力系统的状态变量与参数作出最优估计 [112]。PINNs 可用于把观测数据同化进基于物理的模型，从而有效约束模型预测使其与观测数据保持一致。

> A basic mathematical representation for using data assimilation in inverse problems is formulated as follows: let yobs denote the observed data, x represent the unknown state or parameters to be estimated, and y(x) denote the model predictions given the state or parameters x. In data assimilation, the goal is to find the optimal estimate xest that minimizes the discrepancy between the observed data and the model predictions, often subject to additional constraints or regularization terms. This can be formulated as an optimization problem, typically solved using optimization techniques such as variational methods or Bayesian inference.

**译**：在逆问题中使用数据同化的一个基本数学表述如下：令 y_obs 表示观测数据，x 表示待估计的未知状态或参数，y(x) 表示在给定状态或参数 x 时的模型预测。在数据同化中，目标是找到最优估计 x_est，使观测数据与模型预测之间的差异最小，且往往还受额外的约束或正则化项限制。这可表述为一个优化问题，通常用变分法或贝叶斯推断等优化技术求解。

> A common approach is to define a cost function that measures the misfit between the observed data and the model predictions, along with any additional regularization terms. The optimal estimate xest is then obtained by minimizing this cost function:

**译**：一种常见做法是定义一个代价函数，用以度量观测数据与模型预测之间的失配，并加上任何额外的正则化项。最优估计 x_est 随后通过最小化该代价函数得到：

```
x_est = arg min_x J(x)          (25)
```

> where J(x) is the cost function, often defined as the sum of a data misfit term and a regularization term:

**译**：其中 J(x) 是代价函数，通常定义为一个数据失配项与一个正则化项之和：

```
J(x) = J_data(x) + J_reg(x)          (26)
```

> The data misfit term, Jdata(x), quantifies the mismatch between the observed data and the model predictions:

**译**：数据失配项 J_data(x) 量化观测数据与模型预测之间的不匹配程度：

```
J_data(x) = ‖ y_obs − y(x) ‖²          (27)
```

> The regularization term, Jreg(x), imposes additional constraints or penalties to ensure the solution is stable or adheres to prior knowledge:

**译**：正则化项 J_reg(x) 施加额外的约束或惩罚，以确保解是稳定的、或符合先验知识：

```
J_reg(x) = regularization_function(x)          (28)
```

> The specific choice of regularization function depends on the problem and the desired properties of the solution.

**译**：正则化函数的具体选择取决于问题本身以及所期望的解的性质。

**Multi-physics methods / 多物理场方法**

> In many inverse problems, the underlying physical processes are governed by multiple interacting phenomena, making the problem inherently multiphysics [7,12,43,129]. PINNs can couple multiple physics-based models to solve the inverse problem in a unified framework. This involves incorporating multiple physics-based models into a system of coupled PDEs. By leveraging the expressive power of neural networks, PINNs can simultaneously estimate multiple input parameters or conditions from observed data, even in complex and highly coupled systems.

**译**：在许多逆问题中，底层的物理过程受多个相互作用的现象支配，使问题本质上成为多物理场问题 [7,12,43,129]。PINNs 可以把多个基于物理的模型耦合起来，在统一框架内求解逆问题。这涉及将多个基于物理的模型整合为一个耦合 PDEs 系统。借助神经网络的表达能力，PINNs 能够从观测数据中同时估计多个输入参数或条件，即使在复杂且高度耦合的系统中也是如此。

> The mathematical representation of multi-physics coupling using PINNs involves incorporating multiple physics-based models into a unified framework. Let fi(ui, x) denote the governing equation for the i-th physical process, where ui represents the solution variable associated with that process and x denotes the spatial coordinates. The multi-physics coupling is achieved by simultaneously solving the following system of coupled PDEs:

**译**：用 PINNs 表示多物理场耦合的数学形式，就是把多个基于物理的模型纳入一个统一框架。令 f_i(u_i, x) 表示第 i 个物理过程的控制方程，其中 u_i 表示与该过程相关的求解变量，x 表示空间坐标。多物理场耦合通过同时求解如下耦合 PDEs 系统来实现：

```
∂u₁/∂t = f₁(u₁, x) + Σ_{j=2}^{N} γ₁ⱼ · g₁ⱼ(uⱼ, x)
∂u₂/∂t = f₂(u₂, x) + Σ_{j=1}^{N} γ₂ⱼ · g₂ⱼ(uⱼ, x)
         ...
∂u_N/∂t = f_N(u_N, x) + Σ_{j=1}^{N−1} γ_Nⱼ · g_Nⱼ(uⱼ, x)          (29)
```

> where N is the number of coupled physics processes, γij represents the coupling coefficients, and gij(uj, x) describes the influence of the solution variable uj from the j-th physics process on the i-th process. By leveraging the expressive power of neural networks, PINNs provide a flexible and efficient framework for solving such multi-physics problems.

**译**：其中 N 是耦合物理过程的个数，γ_ij 表示耦合系数，g_ij(u_j, x) 描述第 j 个物理过程的求解变量 u_j 对第 i 个过程的影响。借助神经网络的表达能力，PINNs 为求解此类多物理场问题提供了灵活而高效的框架。

**Model Calibration and Uncertainty Quantification / 模型标定与不确定性量化**

> Inverse problems often require not only estimating the input parameters but also quantifying uncertainty in the estimated solution. PINNs can be trained to produce not only point estimates of the input parameters but also probability distributions that quantify uncertainty in the estimated solution. By incorporating physics-based priors and regularization constraints into the training process, PINNs can produce more reliable estimates of the input parameters and a more accurate quantification of uncertainty in the estimated solution.

**译**：逆问题往往不仅要求估计输入参数，还要求量化所估计的解中的不确定性。可以训练 PINNs 不仅给出输入参数的点估计，还给出量化所估计解中不确定性的概率分布。通过把基于物理的先验与正则化约束引入训练过程，PINNs 能够给出更可靠的输入参数估计，以及对所估计解中不确定性更准确的量化。

> Let y denote the observed data or measurements, m the parameters of the model to be estimated, f(m) the forward model which maps parameters to predicted data, e the error or noise in the observations, and u the uncertainty associated with the estimated parameters. Then, in a mathematical form, the model calibration and uncertainty quantification problem can be represented as follows:

**译**：令 y 表示观测数据或测量值，m 表示待估计的模型参数，f(m) 表示把参数映射到预测数据的前向模型，e 表示观测中的误差或噪声，u 表示与所估计参数相关的不确定性。于是，在数学形式上，模型标定与不确定性量化问题可表示如下：

```
1. Forward Model:        y = f(m) + e                (30)
2. Parameter Estimation: m̂ = arg min_m ‖ y − f(m) ‖²   (31)
3. Uncertainty Quantification: u = F(m)              (32)
```

> where ‖·‖ denotes a norm, such as the Euclidean norm, and F(·) represents a function that quantifies uncertainty in the estimated parameters often through techniques like Bayesian inference or Monte Carlo methods.

**译**：其中 ‖·‖ 表示某种范数，例如欧几里得范数；F(·) 表示一个用于量化所估计参数不确定性的函数，通常借助贝叶斯推断或蒙特卡洛方法等技术实现。

### 4.3. Domain Decomposition / 4.3. 区域分解

> The incorporation of domain decomposition techniques represents another critical advancement in the evolution of PINNs. By partitioning the physical domain into smaller subdomains, these techniques facilitate parallel training and improve scalability, making it feasible to apply PINNs to large-scale problems.

**译**：引入区域分解技术是 PINNs 演进过程中的另一项关键进展。通过把物理区域划分为更小的子区域，这些技术便于并行训练并提升可扩展性，从而使 PINNs 应用于大规模问题成为可能。

> The introduction of neural operators, such as DeepONet [131], has further extended the PINN framework by enabling the learning of mappings between function spaces, thus allowing for the solution of families of PDEs rather than individual instances. The work discusses the potential of NNs in approximating nonlinear operators and proposes Deep Operator Networks (DeepONets) as a method to achieve accurate and efficient learning from relatively small datasets.

**译**：神经算子（例如 DeepONet [131]）的引入进一步扩展了 PINN 框架，使学习函数空间之间的映射成为可能，从而能够求解一整族 PDEs 而非单个实例。该工作讨论了神经网络在逼近非线性算子方面的潜力，并提出深度算子网络（DeepONets）作为一种能够从相对较小的数据集中实现准确高效学习的方法。

> DeepONets consist of two sub-networks: one for encoding input functions and another for encoding output function locations. Through systematic simulations of dynamic systems and PDEs, it is demonstrated that DeepONets significantly reduce generalization errors compared to fully connected networks. Theoretical analyses also reveal the dependence of approximation errors on the number of sensors and input function type, with computational results showing high-order error convergence rates, including polynomial rates and exponential convergence with respect to the training dataset size.

**译**：DeepONet 由两个子网络构成：一个用于编码输入函数，另一个用于编码输出函数的位置。通过对动力系统与 PDEs 的系统性仿真表明，与全连接网络相比，DeepONets 显著降低了泛化误差。理论分析还揭示了逼近误差对传感器数量与输入函数类型的依赖关系，数值结果显示其误差收敛具有高阶速率，包括多项式速率，以及随训练数据集规模变化的指数收敛。

---

## 5. Applications / 5. 应用

> PINNs have shown remarkable potential across a spectrum of scientific and engineering disciplines. In this section, we highlight some applications from fluid dynamics, material science, quantum mechanics, and other fields. Table 1 shows an overview where the columns highlight different features. We would like to note that we also included PINNs for more general equations (GEs) such as models for predicting energy states [132,133] or drug responses [134,135].

**译**：PINNs 已在一系列科学与工程学科中展现出显著潜力。本节中，我们重点介绍流体动力学、材料科学、量子力学及其他领域的一些应用。表 1 给出了概览，其中各列突出不同的特征。需要说明的是，我们也纳入了用于更一般方程（GEs）的 PINN 研究，例如预测能态 [132,133] 或药物反应 [134,135] 的模型。

**表 1** 

> Table 1. The application of PINN for tackling Forward Solution (FS) and Parameter Estimation (PE) in various contexts involving Ordinary Differential Equations (ODEs), Partial Differential Equations (PDEs), and Generalized Equations (GEs).

**译**：表 1. PINN 在涉及常微分方程（ODEs）、偏微分方程（PDEs）与广义方程（GEs）的各种场景中用于处理正问题求解（FS）与参数估计（PE）的应用情况。

| 应用领域 | 文献 | FS（正问题） | PE（参数估计） | ODEs | PDEs | GEs |
|:---|:---|:--:|:--:|:--:|:--:|:--:|
| **流体动力学** | [7] | ✓ | ✓ | – | ✓ | – |
| | [43] | ✓ | ✓ | – | ✓ | – |
| | [42] | ✓ | – | – | ✓ | – |
| | [114] | – | ✓ | – | ✓ | – |
| **材料科学** | [132] | ✓ | – | – | – | ✓ |
| | [133] | ✓ | ✓ | – | – | ✓ |
| | [136] | – | ✓ | – | ✓ | – |
| **结构系统** | [137] | ✓ | ✓ | – | ✓ | – |
| | [43] | ✓ | ✓ | – | ✓ | – |
| | [138] | ✓ | – | – | ✓ | – |
| | [139] | – | ✓ | – | ✓ | – |
| **量子力学** | [7] | ✓ | ✓ | – | ✓ | – |
| | [140] | ✓ | – | ✓ | ✓ | – |
| | [141] | ✓ | – | – | ✓ | – |
| **地球物理** | [142] | ✓ | – | – | ✓ | – |
| | [143] | – | ✓ | – | ✓ | – |
| **能源系统** | [121] | ✓ | – | – | – | ✓ |
| | [123] | – | ✓ | – | ✓ | – |
| | [144] | – | ✓ | ✓ | – | – |
| **肿瘤学** | [145] | ✓ | – | ✓ | – | – |
| | [134] | ✓ | – | – | – | ✓ |
| | [135] | ✓ | – | – | – | ✓ |
| | [146] | – | ✓ | ✓ | – | – |

### 5.1. Fluid Dynamics / 5.1. 流体动力学

> In fluid dynamics, a branch of physics examining fluid behavior under diverse conditions, PINNs have emerged as a robust tool for simulating and analyzing fluid phenomena [7,28,42,43,114]. Exploring applications in simulating turbulent flows, optimizing aerodynamic designs, predicting fluid-structure interactions, and more, PINNs amalgamate data-driven learning with physics-based modeling, offering a promising avenue for addressing complex fluid dynamics issues and advancing our understanding of fluid flow behavior.

**译**：流体动力学是物理学中研究流体在多种条件下行为的分支；在这一领域中，PINNs 已成为模拟与分析流体现象的稳健工具 [7,28,42,43,114]。从湍流模拟、气动设计优化，到流固耦合预测等应用，PINNs 把数据驱动学习与基于物理的建模融为一体，为解决复杂的流体动力学问题、深化我们对流体流动行为的理解提供了一条有前景的路径。

### 5.2. Material Science / 5.2. 材料科学

> Moreover, material science [132,133,136], a multidisciplinary field probing material properties, structures, and behaviors, benefits greatly from PINNs. With applications in predicting material properties, optimizing material compositions and structures, and designing novel materials, PINNs accelerate material discovery and development. Combining data-driven learning with physics-based modeling, PINNs pave the way for innovations in material science, fostering advancements in manufacturing, electronics, energy storage, and healthcare.

**译**：此外，材料科学 [132,133,136] 作为一个探究材料属性、结构与行为的多学科领域，也从 PINNs 中获益良多。PINNs 应用于材料属性预测、材料成分与结构优化以及新材料设计，加速了材料的发现与开发。通过将数据驱动学习与基于物理的建模相结合，PINNs 为材料科学的创新铺平道路，推动制造业、电子、储能与医疗健康领域的进步。

### 5.3. Structural Systems / 5.3. 结构系统

> In structural systems, PINNs are applied to predict stress and strain distributions in complex structures [137], such as bridges, buildings, and mechanical components, under various loading conditions [43]. They also facilitate the detection and quantification of structural damage by interpreting sensor data and solving inverse problems. Within material science, PINNs enable the simulation of material behavior across different scales, from the atomic to the macroscopic levels, supporting the design of advanced materials with tailored properties [139]. They are also instrumental in studying phase transitions and microstructural evolution in materials, providing insights into processes like solidification and grain growth [138].

**译**：在结构系统中，PINNs 被用于预测复杂结构（如桥梁、建筑和机械部件）在多种载荷条件下的应力与应变分布 [137,43]。它们还通过解读传感器数据并求解逆问题，帮助检测与量化结构损伤。在材料科学中，PINNs 能够模拟材料从原子尺度到宏观尺度的跨尺度行为，支持具有定制性能的先进材料设计 [139]。它们在研究材料的相变与微观结构演化方面同样发挥了重要作用，为凝固、晶粒生长等过程提供了洞见 [138]。

### 5.4. Quantum Mechanics / 5.4. 量子力学

> In the realm of quantum mechanics, which elucidates phenomena at the atomic and subatomic levels, PINNs offer a valuable means to simulate and analyze quantum mechanical systems [7,140,141]. Enabling the simulation and analysis of complex quantum systems, PINNs facilitate the study of intricate quantum phenomena and the development of quantum technologies. From simulating quantum systems to predicting quantum properties, PINNs, through their fusion of data-driven learning and physics-based modeling, contribute significantly to the comprehension and utilization of quantum mechanics, driving innovations in quantum computing, cryptography, and sensing.

**译**：在量子力学领域——它阐明原子与亚原子尺度上的现象——PINNs 提供了模拟与分析量子力学系统的宝贵手段 [7,140,141]。PINNs 使复杂量子系统的模拟与分析成为可能，从而促进了对深奥量子现象的研究与量子技术的发展。从模拟量子系统到预测量子属性，PINNs 通过融合数据驱动学习与基于物理的建模，为理解和利用量子力学作出了重要贡献，推动量子计算、密码学与量子传感领域的创新。

### 5.5. Geophysics and Biomedical Engineering / 5.5. 地球物理与生物医学工程

> In geophysics, PINNs assist in interpreting seismic data to infer subsurface properties, aiding in oil and gas exploration and earthquake hazard assessment [143]. They are also used to model groundwater flow and contaminant transport, which support the management of water resources and environmental remediation efforts [142]. In biomedical engineering, PINNs are employed to simulate blood flow and cardiac mechanics, thereby contributing to the understanding and treatment of cardiovascular diseases [147]. Additionally, they are used to model tumor growth and spread, offering tools for predicting cancer progression and optimizing treatment strategies [148].

**译**：在地球物理中，PINNs 协助解读地震数据以推断地下属性，为油气勘探与地震灾害评估提供支持 [143]。它们也被用于对地下水流与污染物迁移建模，从而支撑水资源管理与环境修复工作 [142]。在生物医学工程中，PINNs 被用于模拟血流与心脏力学，从而有助于理解与治疗心血管疾病 [147]。此外，它们还被用于对肿瘤生长与扩散建模，为预测癌症进展和优化治疗策略提供工具 [148]。

### 5.6. Energy Systems / 5.6. 能源系统

> In the field of energy systems, PINNs aid in simulating electrochemical processes in batteries, contributing to the development of more efficient and durable energy storage systems [123]. They are also used to model and optimize the performance of renewable energy systems, such as wind turbines [121] and power grid systems [144].

**译**：在能源系统领域，PINNs 协助模拟电池中的电化学过程，为开发更高效、更耐用的储能系统作出贡献 [123]。它们还被用于建模与优化可再生能源系统的性能，例如风力发电机 [121] 与电网系统 [144]。

### 5.7. Oncology / 5.7. 肿瘤学

> The use of PINNs in cancer research has also shown significant promise. PINNs integrate physical laws and domain knowledge into models, which is particularly useful for understanding complex biological systems like cancer. They have been employed to model tumor growth by solving PDEs, providing accurate predictions of tumor behavior and enabling personalized treatment planning by estimating key parameters [145]. In drug response optimization [134,135], PINNs predict the pharmacokinetics and pharmacodynamics of anticancer drugs, helping to optimize dosing regimens and maximize therapeutic efficacy. For tumor-immune system interactions [146], PINNs model the dynamics of immune cell infiltration and the effects of immunotherapies, aiding in the design of new treatment strategies.

**译**：PINNs 在癌症研究中的应用也展现出显著前景。PINNs 把物理定律与领域知识整合进模型，这对理解癌症这类复杂生物系统尤为有用。它们已被用于通过求解 PDEs 来对肿瘤生长建模，既能准确预测肿瘤行为，又能通过估计关键参数实现个性化治疗方案规划 [145]。在药物反应优化方面 [134,135]，PINNs 预测抗癌药物的药代动力学与药效动力学，帮助优化给药方案并最大化疗效。在肿瘤—免疫系统相互作用方面 [146]，PINNs 对免疫细胞浸润的动态过程以及免疫疗法的效果建模，有助于设计新的治疗策略。

---

## 6. Challenges and Limitations / 6. 挑战与局限

> Although PINNs have promising capabilities, there are also challenges and limitations. In this section, we discuss some of the key challenges and constraints associated with the development and application of PINNs. These include data scarcity, computational complexity, integration of complex physical laws, and issues related to generalization and robustness.

**译**：尽管 PINNs 能力前景可观，但它同样存在挑战与局限。本节讨论与 PINNs 开发及应用相关的一些关键挑战与约束，包括数据稀缺、计算复杂度、复杂物理定律的整合，以及与泛化性和稳健性相关的问题。

### 6.1. Data-Related Issues / 6.1. 数据相关问题

> PINNs merge data-driven learning with physics-based modeling but face challenges with data availability, quality, and diversity, impacting model performance and reliability. Data scarcity limits the training of NNs, especially in underrepresented regions, leading to less accurate models. Data quality issues, such as noise and biases, also affect predictive

**译**：PINNs 把数据驱动学习与基于物理的建模融合在一起，但在数据的可获得性、质量与多样性方面面临挑战，这些问题会影响模型的性能与可靠性。数据稀缺限制了神经网络的训练，在样本代表性不足的区域尤其如此，导致模型精度下降。数据质量问题（例如噪声与偏置）同样影响预测

> accuracy. Imbalanced data skew model training, while data heterogeneity requires robust preprocessing to ensure compatibility. Limited input ranges hinder extrapolation, and data biases affect generalization, necessitating meticulous data collection. Data interpretability remains challenging in high-dimensional spaces.

**译**：精度。数据不平衡会使模型训练产生偏斜，而数据异构性则要求稳健的预处理以保证兼容性。输入范围有限会妨碍外推，数据偏置会影响泛化，因此必须细致地进行数据采集。在高维空间中，数据的可解释性依然是个难题。

> Integrating PINNs with traditional NNs can mitigate these issues by functioning as an unsupervised method, eliminating the need for labeled data, and converting PDE problems into loss function optimization. The PINN algorithm embeds the mathematical model in the network, incorporating a residual term from the governing equation to constrain the solution space.

**译**：把 PINNs 与传统神经网络相结合可以缓解这些问题：PINNs 可作为一种无监督方法运作，无需标注数据，并把 PDE 问题转化为损失函数优化问题。PINN 算法把数学模型嵌入网络之中，引入来自控制方程的残差项以约束解的搜索空间。

### 6.2. Computational Challenges / 6.2. 计算挑战

> Large datasets pose significant computational challenges for PINNs, including high dimensionality, leading to an explosion of parameters and computational complexity, which requires substantial resources and can cause overfitting and slow convergence. Numerical instabilities often arise when solving PDEs or ODEs, particularly in stiff or ill-conditioned systems, necessitating careful numerical methods and regularization techniques. Scalability is another major issue, with memory limitations, communication overhead, and computational bottlenecks requiring distributed training and parallel computing. Hyperparameter tuning is complex and time-consuming, involving numerous parameters like network architecture and learning rates. Training times are considerable, especially for large datasets or complex problems, highlighting the need for more efficient algorithms. Additionally, interpretability is challenging, necessitating methods to understand and visualize predictions.

**译**：大型数据集给 PINNs 带来显著的计算挑战，其中包括高维问题——它导致参数规模与计算复杂度爆炸，既需要大量资源，又可能引发过拟合与收敛缓慢。在求解 PDEs 或 ODEs 时，数值不稳定性经常出现，在刚性或病态系统中尤为如此，因此需要审慎的数值方法与正则化技术。可扩展性是另一个主要问题：内存限制、通信开销与计算瓶颈都要求分布式训练与并行计算。超参数调优复杂且耗时，涉及网络架构、学习率等众多参数。训练时间相当可观，在大数据集或复杂问题上尤其明显，这凸显了发展更高效算法的必要性。此外，可解释性也是一大难题，需要相应方法来理解和可视化预测结果。

> Addressing these challenges requires advances in machine learning, numerical analysis, parallel computing, and domain-specific knowledge. Developing scalable algorithms, optimizing numerical methods, and leveraging hardware acceleration can help overcome these challenges and unlock the full potential of PINNs for complex scientific and engineering problems. We would like to emphasize that such extensions are only meaningful if the performance of the PINN is improved. That means, in all cases, appropriate testing needs to be conducted to ensure quality, robustness, and reproducibility of the results.

**译**：应对这些挑战需要在机器学习、数值分析、并行计算以及领域特定知识等方面取得进展。开发可扩展的算法、优化数值方法并利用硬件加速，有助于克服这些挑战，释放 PINNs 在复杂科学与工程问题上的全部潜力。我们要强调，这类扩展只有在 PINN 的性能确实得到提升时才有意义。这意味着在任何情况下都需要进行恰当的测试，以确保结果的质量、稳健性与可复现性。

### 6.3. Integration of Complex Physics / 6.3. 复杂物理的整合

> PINNs offer a promising framework for integrating complex physical laws into machine learning models, but several challenges need to be addressed for accuracy and reliability. Capturing nonlinear and multiscale phenomena is crucial, as many physical systems exhibit interactions across multiple spatial and temporal scales. Additionally, incorporating robust probabilistic modeling techniques is essential to handle uncertainty and variability due to factors like measurement noise and environmental fluctuations. Some physical systems exhibit chaotic or stochastic behavior, requiring specialized techniques like stochastic differential equations or probabilistic inference. Complex boundary conditions, such as non-homogeneous or time-varying conditions, must be accurately incorporated into PINN models for stability and accuracy. Multi-physics coupling, involving interactions between different physical domains, also presents a challenge and requires integrated models. Lastly, domain-specific knowledge is essential for identifying relevant physical principles, equations, parameters, and boundary conditions, guiding the development of accurate PINN models.

**译**：PINNs 为把复杂物理定律整合进机器学习模型提供了有前景的框架，但要在准确性与可靠性上达标，仍须解决若干挑战。捕捉非线性与多尺度现象至关重要，因为许多物理系统会在多个空间与时间尺度上表现出相互作用。此外，引入稳健的概率建模技术对于处理由测量噪声、环境波动等因素造成的不确定性与变异性必不可少。某些物理系统表现出混沌或随机行为，需要随机微分方程或概率推断等专门技术。复杂边界条件（例如非齐次条件或随时间变化的条件）必须被准确地纳入 PINN 模型，以保证稳定性与精度。涉及不同物理域之间相互作用的多物理场耦合同样构成挑战，需要一体化模型。最后，领域特定知识对于识别相关的物理原理、方程、参数与边界条件至关重要，它引导着准确 PINN 模型的开发。

> Overcoming these challenges necessitates a multidisciplinary approach of combining advances in machine learning, numerical methods, and domain expertise, enabling the development of reliable models for complex physical systems.

**译**：要克服这些挑战，必须采取多学科协同的路径，把机器学习、数值方法与领域专长的进展结合起来，从而为复杂物理系统开发出可靠的模型。

### 6.4. Generalization and Robustness / 6.4. 泛化性与稳健性

> Generalization and robustness are crucial for the performance and reliability of PINNs. Generalization ensures accurate predictions on unseen data, while robustness maintains performance despite perturbations and uncertainties in input data. Achieving these involves overcoming several challenges. Overfitting, where the model memorizes training data instead of learning general patterns, can be addressed with techniques like regularization, dropout, and data augmentation. Conversely, underfitting, where the model is too simplistic to capture data patterns, requires more complex architectures and additional training data. Domain shift, where training and test data distributions differ, can degrade performance and is mitigated through domain adaptation and transfer learning. Out-of-distribution (OOD) detection is essential for identifying unreliable predictions, especially in critical applications, and involves methods like uncertainty estimation and anomaly detection. Transfer learning and domain adaptation enhance generalization by leveraging knowledge from related domains or tasks.

**译**：泛化性与稳健性对 PINNs 的性能与可靠性至关重要。泛化性确保模型在未见过的数据上仍能准确预测，稳健性则保证在输入数据存在扰动与不确定性时性能不下降。要做到这两点，必须克服若干挑战。过拟合——模型记住训练数据而非学到一般性模式——可通过正则化、随机失活（dropout）与数据增强等技术来应对。反之，欠拟合——模型过于简单以致无法捕捉数据模式——则需要更复杂的架构与更多训练数据。域偏移，即训练数据与测试数据分布不一致，会削弱性能，可通过域适应与迁移学习加以缓解。分布外（OOD）检测对于识别不可靠的预测至关重要，在关键应用中尤为如此，其手段包括不确定性估计与异常检测。迁移学习与域适应通过利用相关领域或任务的知识来提升泛化能力。

> Addressing these challenges requires algorithmic improvements, model regularization, data augmentation, and domain-specific expertise, ultimately enhancing the reliability, performance, and safety of PINN models across various applications.

**译**：应对这些挑战需要算法改进、模型正则化、数据增强以及领域专长，最终提升 PINN 模型在各类应用中的可靠性、性能与安全性。

---

## 7. Future Directions / 7. 未来方向

> As PINNs continue to evolve, several exciting directions for future research and development emerge. In this section, we explore some of the potential future directions for advancing the field of PINNs.

**译**：随着 PINNs 持续演进，若干令人振奋的未来研究与开发方向正逐步显现。本节探讨推进 PINN 领域发展的一些潜在未来方向。

### 7.1. Algorithmic Advancements / 7.1. 算法进展

> Algorithmic advancements in neural networks (NNs) are crucial for the evolution and enhancement of Physics-Informed Neural Networks (PINNs). Key breakthroughs include novel training algorithms tailored to NNs, improving efficiency, scalability, and efficacy. Adaptive learning rate schedules optimize stability and convergence, especially with non-uniform gradients or noisy data. Advanced regularization techniques, incorporating domain-specific knowledge, enhance generalization and robustness. Uncertainty quantification methods improve prediction reliability, particularly in data-scarce environments. Self-supervised and semi-supervised learning with unlabeled or partially labeled data boost performance and generalization. Model compression and pruning streamline NN complexity, making them suitable for resource-constrained settings. Addressing adversarial robustness through robust optimization and defense mechanisms strengthens NNs against attacks, which is crucial for safety-critical applications.

**译**：神经网络的算法进展对物理信息神经网络（PINNs）的演进与提升至关重要。关键突破包括为神经网络量身定制的新型训练算法，以改善效率、可扩展性与有效性。自适应学习率调度可优化稳定性与收敛性，在梯度不均匀或数据含噪的场景中尤其有效。融入领域特定知识的高级正则化技术能提升泛化性与稳健性。不确定性量化方法可改善预测的可靠性，在数据稀缺的环境中尤为明显。利用无标签或部分标注数据的自监督与半监督学习，可提升性能与泛化能力。模型压缩与剪枝可简化神经网络复杂度，使其适用于资源受限的环境。通过稳健优化与防御机制来提升对抗稳健性，可增强神经网络抵御攻击的能力，这对安全攸关的应用至关重要。

> These advancements enhance PINNs' capabilities across scientific and engineering domains. By combining algorithmic innovation with domain-specific expertise, one can unlock new avenues for innovation and discovery with PINNs.

**译**：这些进展能在科学与工程各领域中增强 PINNs 的能力。把算法创新与领域专长结合起来，人们就能借助 PINNs 开辟创新与发现的新途径。

### 7.2. Interdisciplinary Collaborations / 7.2. 跨学科协作

> Interdisciplinary collaborations are crucial for advancing PINNs, fostering the exchange of ideas and collective problem-solving. These partnerships hold significant potential in various areas:

**译**：跨学科协作对推进 PINNs 至关重要，它能促进思想交流与协同解决问题。这类合作关系在多个领域都蕴含巨大潜力：

> - **Physics and Machine Learning**: Physicists provide insights into physical principles, while machine learning specialists develop and optimize algorithms.
> - **Engineering and Data Science**: Engineers contribute domain-specific knowledge in fields like fluid dynamics and structural mechanics, while data scientists handle data preprocessing, feature engineering, and model refinement.
> - **Medicine and Healthcare**: Medical researchers and healthcare professionals work with machine learning experts to improve personalized medicine, disease diagnosis, and healthcare optimization using PINNs.
> - **Climate Science and Environmental Engineering**: Climate scientists and environmental engineers collaborate with machine learning researchers to address climate change, environmental sustainability, and natural disaster mitigation.
> - **Materials Science, Nanotechnology, Robotics, and Autonomous Systems**: In materials science, PINNs aid in discovering and optimizing new materials. In robotics, they enhance autonomous systems and control strategies.

**译**：
- **物理学与机器学习**：物理学家提供对物理原理的洞见，机器学习专家则开发并优化算法。
- **工程学与数据科学**：工程师贡献流体动力学、结构力学等领域的领域知识，数据科学家负责数据预处理、特征工程与模型精调。
- **医学与医疗健康**：医学研究者与医疗从业者同机器学习专家合作，利用 PINNs 改进个性化医疗、疾病诊断与医疗优化。
- **气候科学与环境工程**：气候科学家与环境工程师同机器学习研究者协作，应对气候变化、环境可持续性与自然灾害缓解问题。
- **材料科学、纳米技术、机器人与自主系统**：在材料科学中，PINNs 有助于发现与优化新材料；在机器人领域，它们增强了自主系统与控制策略。

> These interdisciplinary efforts leverage synergies, advancing innovation and knowledge across diverse fields.

**译**：这些跨学科努力利用协同效应，推动多个领域的创新与知识进步。

### 7.3. Enhancements in Interpretability / 7.3. 可解释性的提升

> Interpretability is crucial for NNs and PINNs, providing insights and fostering trust in their predictions, especially in scientific and engineering fields where transparency is essential. As PINNs find diverse applications, enhancing interpretability becomes vital. Key strategies include the following:

**译**：可解释性对神经网络和 PINNs 都至关重要，它能提供洞见并培育对其预测的信任，在强调透明度的科学与工程领域尤其如此。随着 PINNs 被应用于越来越多样的场景，提升可解释性变得尤为关键。主要策略包括：

> - **Explainable Model Architectures**: Use of sparse NNs and decision trees to clarify relationships between inputs and predictions.
> - **Feature Importance Analysis**: Techniques like feature attribution and sensitivity analysis identify influential features and how input changes affect predictions.
> - **Visualization Techniques**: Saliency maps and activation maximization help users understand model behavior and reasoning.
> - **Rule Extraction and Symbolic Reasoning**: Provide concise representations of learned relationships for better comprehension.
> - **Domain-Specific Interpretability**: Tailored to specific scientific and engineering contexts for relevant insights.
> - **Model-Agnostic Techniques**: Surrogate models and global explanation methods facilitate understanding across different model types.

**译**：
- **可解释的模型架构**：使用稀疏神经网络与决策树来阐明输入与预测之间的关系。
- **特征重要性分析**：特征归因、敏感性分析等技术可识别有影响力的特征，以及输入变化如何影响预测。
- **可视化技术**：显著性图（saliency map）与激活最大化有助于用户理解模型的行为与推理过程。
- **规则抽取与符号推理**：为学到的关系提供简洁表示，以便更好理解。
- **领域特定的可解释性**：针对具体科学与工程语境量身定制，以给出切题的洞见。
- **模型无关技术**：代理模型与全局解释方法使理解不同模型类型成为可能。

> Enhancing interpretability in PINNs improves model transparency, reliability, and usability in real-world scenarios. It simplifies model understanding and debugging, allowing users to gain deeper insights into underlying physics and data relationships, driving scientific discovery and engineering innovation.

**译**：提升 PINNs 的可解释性可改善模型在真实场景中的透明度、可靠性与可用性。它简化了模型的理解与调试，使用户能够更深入地洞察底层物理与数据关系，从而推动科学发现与工程创新。

### 7.4. Digital Twins / 7.4. 数字孪生

> Another promising application of PINNs is in digital twin research [149,150]. In this context, PINNs can be used for the parameter estimation of complex systems, providing models for problems in manufacturing, oncology, and economics. However, an extension is needed to enable online learning, allowing for continuous updates of parameters as new data become available over time. This extension bears similarities to meta-learning because two different forms of learning—inner learning for the PINN and outer learning for the updates—need to be simultaneously optimized.

**译**：PINNs 另一个有前景的应用方向是数字孪生研究 [149,150]。在这一语境中，PINNs 可用于复杂系统的参数估计，为制造业、肿瘤学和经济学中的问题提供模型。然而，还需要做一项扩展以支持在线学习，使参数能够随新数据随时间到来而持续更新。该扩展与元学习有相似之处，因为两种不同形式的学习——PINN 自身的内层学习与用于更新的外层学习——需要被同时优化。

### 7.5. Large-Scale and Real-Time Applications / 7.5. 大规模与实时应用

> Large-scale and real-time applications open new possibilities for PINNs, offering solutions to intricate problems. To fully utilize PINNs across scientific research, engineering design, and industry, improvements in scalability, efficiency, and deployment are crucial. Key strategies include developing scalable algorithms and architectures for large datasets, integrating with high-performance computing (HPC) for faster simulations, deploying in real-time decision support systems, incorporating online learning for adaptability, leveraging edge computing for localized inference, and ensuring robustness for safety-critical contexts.

**译**：大规模与实时应用为 PINNs 开辟了新的可能性，为复杂问题提供解决途径。要在科学研究、工程设计与工业界充分利用 PINNs，提升可扩展性、效率与部署能力至关重要。主要策略包括：为大型数据集开发可扩展的算法与架构；与高性能计算（HPC）集成以实现更快的仿真；部署到实时决策支持系统中；引入在线学习以增强适应性；利用边缘计算实现本地化推断；以及为安全攸关场景确保稳健性。

> Focusing on these applications allows us to address complex challenges and foster innovation, highlighting the need for advancements in scalability, efficiency, and reliability to realize their full potential.

**译**：聚焦这些应用使我们能够应对复杂挑战并促进创新，同时也凸显了在可扩展性、效率与可靠性方面取得进展、以充分发挥其潜力的必要性。

---

## 8. Conclusions / 8. 结论

> PINNs have emerged as a powerful framework for integrating physics-based modeling with data-driven learning that enable us to tackle complex scientific and engineering problems across diverse domains. In this survey, we explore the principles, applications, challenges, and future directions of PINNs, highlighting their potential to revolutionize scientific discovery, engineering design, and industrial innovation.

**译**：PINNs 已成为一个强有力的框架，把基于物理的建模与数据驱动学习结合起来，使我们能够应对跨多个领域的复杂科学与工程问题。在本综述中，我们探讨了 PINNs 的原理、应用、挑战与未来方向，强调了它在革新科学发现、工程设计与工业创新方面的潜力。

> The applications of PINNs span a wide range of domains, including fluid dynamics, material science, quantum mechanics, medicine, and climate research, demonstrating their versatility and effectiveness in addressing complex problems. Looking ahead, the future of PINNs is promising, with exciting opportunities for innovation and discovery across a wide range of scientific and engineering domains. However,

**译**：PINNs 的应用横跨广泛领域，包括流体动力学、材料科学、量子力学、医学与气候研究，展示了其在处理复杂问题上的通用性与有效性。展望未来，PINNs 前景可期，在广泛的科学与工程领域中蕴含着令人振奋的创新与发现机遇。然而，

> further work is needed to develop systematic methods for optimizing network architectures for specific problems. Additionally, creating a taxonomy of approaches to different dynamic systems would facilitate easier application by others. Finally, extending PINNs into an online learning paradigm would enable their applicability in digital twin research.

**译**：仍需要开展进一步工作，以发展针对特定问题优化网络架构的系统性方法。此外，为面向不同动力系统的各类方法建立一套分类体系，将便于他人更容易地应用。最后，把 PINNs 扩展为在线学习范式，将使其可应用于数字孪生研究。

---

## 作者贡献与声明 / Author Contributions & Statements

> **Author Contributions**: Conceptualization, A.F. and F.E.-S.; methodology, A.F. and F.E.-S.; writing—original draft preparation, A.F.; writing—review and editing, A.F., O.Y.-H., and F.E.-S. All authors have read and agreed to the published version of the manuscript.

**译**：**作者贡献**：概念构思，A.F. 与 F.E.-S.；方法学，A.F. 与 F.E.-S.；撰写初稿，A.F.；撰写—评审与编辑，A.F.、O.Y.-H. 与 F.E.-S.。所有作者均已阅读并同意稿件的出版版本。

> **Funding**: This research received no external funding.

**译**：**资助**：本研究未获得外部资助。

> **Informed Consent Statement**: Not applicable.

**译**：**知情同意声明**：不适用。

> **Data Availability Statement**: Not applicable.

**译**：**数据可用性声明**：不适用。

> **Conflicts of Interest**: The authors declare no conflicts of interest.

**译**：**利益冲突**：作者声明无利益冲突。

---

## 参考文献 / References

> **【译者说明】** 按翻译约定，参考文献条目整体保留英文原文，不作翻译（避免作者姓名、期刊名、卷期页码在转写中出错）。完整条目共 150 条，原样存于：

- 原文提取（段落版）：`papers\_source_text\Understanding PINNs Techniques, Applications, Trends, and Challenges.txt`
- 原文提取（原始版式版）：同目录下 `.raw.txt` 文件

**本领域最关键的 8 条**（供快速定位，均为原文条目编号）：

| 编号 | 文献 | 为什么重要 |
|:--|:---|:---|
| [6] | Cuomo, S. 等. Scientific machine learning through physics–informed neural networks: Where we are and what's next. *J. Sci. Comput.* 2022, 92, 88. | 四篇中第 2 篇，最系统的 PINN 综述 |
| [7] | Raissi, M.; Perdikaris, P.; Karniadakis, G.E. Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *J. Comput. Phys.* 2019, 378, 686–707. | 四篇中第 3 篇，PINN 原始论文 |
| [8] | Karniadakis, G.E. 等. Physics-informed machine learning. *Nat. Rev. Phys.* 2021, 3, 422–440. | 四篇中第 4 篇，思想纲领 |
| [43] | Jagtap, A.D.; Kharazmi, E.; Karniadakis, G.E. Conservative physics-informed neural networks on discrete domains for conservation laws. *CMAME* 2020, 365, 113028. | 守恒律 + 区域分解（cPINN） |
| [114] | Raissi, M.; Yazdani, A.; Karniadakis, G.E. Hidden fluid mechanics（HFM） | 用 PINN 从流动可视化数据中反推速度/压力场 |
| [116] | Yang, L.; Meng, X.; Karniadakis, G.E. B-PINNs: Bayesian physics-informed neural networks | 不确定性量化的标准做法 |
| [131] | Lu, L.; Jin, P.; Pang, G.; Zhang, Z.; Karniadakis, G.E. DeepONet | 算子学习，从"解一个方程"到"解一族方程" |
| [125] | Zhang 等. 用 PINN + 符号回归发现 ODE 系统中的未知数学模型（阿尔茨海默病建模） | **方程发现**，与"物理参数进入模型"的方向最接近 |

---

## 全文速览（译者整理）

### 这篇综述的骨架

```
1 引言 ── 为什么要把物理塞进神经网络
2 背景 ── NN 的局限（数据依赖、物理不自洽）
3 方法学 ← 全文最重的技术部分
   3.1 特征工程（把物理做成输入特征）
   3.2 模型构建（ANN / CNN / RNN / GNN / 注意力 / 生成模型，式 1–21）
   3.3 物理定律作附加代价函数（软约束、正则化、B-PINN，式未编号）
4 用途 ← 与"参数"最相关
   4.1 求解 PDE/ODE（有限差分 / 配点 / 边界积分 / Deep Galerkin / 时间步进）
   4.2 逆问题（正则化 / 贝叶斯推断 / 数据同化 / 多物理场 / 模型标定+UQ，式 22–32）
   4.3 区域分解（并行训练 + DeepONet 算子学习）
5 应用（表 1 汇总：流体 / 材料 / 结构 / 量子 / 地球物理 / 能源 / 肿瘤）
6 挑战（数据 / 计算 / 复杂物理整合 / 泛化与稳健）
7 未来方向（算法 / 跨学科 / 可解释性 / 数字孪生 / 大规模实时）
8 结论
```

### 三条最值得记住的结论

1. **物理进入网络的三种位置**：输入特征（特征工程）、网络结构（模型构建）、损失函数（附加代价）。这是全文的方法学主干，也是判断任何"物理+AI"工作创新点的坐标系。
2. **逆问题是 PINN 最扎实的战场**：§4.2 把逆问题拆成五条路线（正则化、贝叶斯、数据同化、多物理场、标定+UQ），其中"未知参数 → 用观测反推"正是"物理参数进入模型学习"的核心接口。
3. **作者自陈的三个待办**：网络架构的系统化优化方法、面向不同动力系统的方法分类体系、扩展为在线学习（对应数字孪生）。

> **〔译者提醒〕** 原文 §4.2 中"未知函数形式"这一挑战（§4 开头第 2 点，化学工程速率方程）与"方程发现"（文献 [125]、[18]）是本文最接近"让模型自己学出物理规律"的部分，建议结合第 3 篇（Raissi 2019）§4「PDE 的数据驱动发现」一起读。

---

**翻译完成度：全文 100%（封面 → 8. 结论 → 声明；参考文献按约定保留原文）**

