
> 感谢在这里相遇。这会是一个长周期不断更新的陪伴式成长系列（预期一年，2025-9月至2026-9月），我们一起走向深入、走向专业，跟 AI 一起进化。It will be a long long journey.

- 计划长周期更新的三个系列（如无意外，一月至少2期）
    - Modern Agents
    - Agentic RL Post-training
    - LLMs 基础/训练扩充、丰富与系统化；
- up 更愿意在整个漫长的更新里，跟各位同学、老师分享的是，一般性、相对底层的概念、原理与方法，预期是不会很快过时的内容；
    - 预期能做到，足够的 general，足够的 principled；
- 大概一年左右的时间，也就是到 2026 年国庆的时候，开始整理形成一本书（modern agents）；
    - 用核心公式串联起 modern AI 的原理及应用；
- 更新的优先级：基本概念/原理 > 一些通用/实用的技术/工具 > 应用/项目
    - 希望可以做到原理理解先行；

# modern_genai_bilibili (roadmap & landscape & highlights)

## 数学基础

- 概率统计
    - MLE：是用来做参数估计，估计模型的参数。先建立模型，再比如基于数据估计/推断模型的参数
        - 似然与概率
    - bayes theorem
- 矩阵分析
    - SVD：LoRA
    - 范数理论：谱范数
    - 求导：雅可比矩阵
- sampling-based methods
    - monte carlo：估计期望，估计积分（多维复杂难以得到直接解析解的多维积分），基于的是大数定理（LLN，Law of large numbers）；
        - importance sampling
        - mcmc, mh
        - mc in rl
- search-based methods
    - actor(policy) & critic(value)
        - AlphaGo
        - TongGeometry
- learning-based methods (data-driven)
    - machine learning
    - deep learning

## PyTorch

- 计算图（computational graph）与梯度流（Gradient flow）
    - 梯度可反向传播，才可学习，才是 learnable/trainable 的
- 梯度不可传播时 （出现了 sampling，梯度断流）
    - Policy Gradient
    - Reparameter Trick
- 优化视角（optimization perspective）
    - learning 即 optimization，对于 Deep Learning 而言；

## core concepts

- learning and optimization
    - reverse KL & forward KL
    - Q与P的讨论
- RL
    - onpolicy vs. offpolicy
    - mc vs. td
    - bias variance analysis

