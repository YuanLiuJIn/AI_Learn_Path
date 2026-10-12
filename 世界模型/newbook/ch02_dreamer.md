# Chapter 02：经典世界模型——Dreamer 系列

## 2.1 一句话理解

Dreamer = **学一个隐空间世界模型，再在这个模型"想象"出来的轨迹上训练策略**。采数据之外，训练过程完全不碰真实环境——所以它是"在梦里学开车"的成熟版。

论文谱系：PlaNet（Hafner, 2019）→ Dreamer V1《Dream to Control》(2019) → V2《Mastering Atari with Discrete World Models》(2020) → V3 (2023，Nature 2025)。代码：`danijar/dreamerv3`。

## 2.2 核心组件：RSSM（循环状态空间模型）

RSSM（Recurrent State-Space Model）是 Dreamer 的心脏。它把隐状态拆成两部分：

$$
\underbrace{h_t}_{\text{确定性路径（RNN 记忆）}},\qquad \underbrace{z_t}_{\text{随机路径（从观测推断）}}
$$

- $h_t = f(h_{t-1},\,z_{t-1},\,a_{t-1})$：确定性循环，负责记忆与稳定。
- $z_t$：随机变量，负责表达不确定性与多模态未来。

围绕它定义**四个模型**：

| 模型 | 公式 | 作用 |
|---|---|---|
| 表示（编码） | $q(z_t\mid h_t,o_t)$ | 从观测推断隐状态（后验） |
| 过渡（先验） | $p(z_t\mid h_t)$ | 不靠观测预测隐状态 |
| 解码 | $p(o_t\mid h_t,z_t)$ | 重建观测 |
| 奖励 | $p(r_t\mid h_t,z_t)$ | 预测奖励 |

**为什么要有先验和后验两套？** 后验看得到观测，用于训练；先验看不到观测，用于"做梦"时往前滚。两者越接近，想象就越接近现实——这正是 KL 项要约束的。

## 2.3 训练目标：ELBO + 奖励

世界模型损失 = 重构 + 奖励 + KL（近似的 ELBO）：

$$
\mathcal{L}=\underbrace{-\log p(o_t\mid h_t,z_t)}_{\text{重构}}\;-\;\underbrace{\log p(r_t\mid h_t,z_t)}_{\text{奖励}}\;+\;\underbrace{\beta\,D_{\mathrm{KL}}\big[q(z_t\mid h_t,o_t)\,\|\,p(z_t\mid h_t)\big]}_{\text{保持先验≈后验}}
$$

关键技巧 **KL 平衡（KL balancing）**：不希望后验硬拉向先验（会学不到信息），也不希望先验硬追后验（会幻觉）。于是给两项不同的权重，让它们"各让一步"。这一条看不懂，就读不懂 Dreamer 为什么稳定。

## 2.4 想象训练：在隐空间里学策略

世界模型训好后，固定它，让 actor 与 critic 只在**想象轨迹**上学习：

```text
从真实数据里挑一个 (h_t, z_t) 作为起点
    │
    ▼  for k = 1..H:（H 通常 15 左右，短才稳）
actor 输出 a_k ──► 过渡模型给出 (h_{k+1}, z_{k+1})
              ──► 奖励模型给出 r_k
    │
    ▼
用这些想象出来的 (z, r) 计算 λ-return，更新 actor-critic
（策略梯度可穿过后验/先验采样——靠重参数化 + 直通估计）
```

**为什么是"求梯度"而不是"做规划"？** Dreamer 属于第③类用法：模型可微，梯度直接从回报回传到策略，比在线搜索快得多。

## 2.5 从 V1 到 V3 的演进

| 版本 | 关键创新 | 解决什么 |
|---|---|---|
| **V1** (2019) | RSSM + 想象训练，连续隐变量 | 首次把隐空间世界模型与 actor-critic 端到端打通 |
| **V2** (2020) | 隐变量**离散化**（分类分布）+ 直通估计；可选 model-free 混合 | Atari 上追平/超越 model-free，容量更强 |
| **V3** (2023) | symlog 预测、two-hot 编码、回报归一化、鲁棒超参、去掉 model-free 依赖 | **一套超参跨域通用**（Atari、DMC、Minecraft 通吃） |

V3 的哲学：与其精调，不如让**目标尺度自适应**（归一化 + symlog），从而对奖励尺度、任务类型都不敏感。

## 2.6 局限

- **压缩瓶颈**：像素压到几十维隐变量，细节大量丢失；背景等无关信息也会占用容量。
- **长期依赖衰减**：想象 horizon 短（约 15 步），长程信用分配仍难。
- **误差累积**：即便在隐空间，rollout 越长偏离真实动态越远（对照 Ch01 的陷阱）。

## 2.7 实践与资源

- **论文**：PlaNet arXiv:1906.11238；DreamerV1 arXiv:1912.01603；DreamerV2 arXiv:2010.02193；DreamerV3 arXiv:2301.04104。
- **代码**：`danijar/dreamerv3`（JAX）、`danijar/dreamer`（V1，TF）。
- **博客/视频**：Danijar Hafner 个人博客（danijar.com）逐篇讲动机；B 站搜"Dreamer 精读"。
- **阶梯实验**：① 先跑官方 repo 的 `dmc` 小环境；② 记录"想象回报 vs 真实回报"；③ 手改 horizon $H$，看多短才稳。

## 2.8 自检清单

- [ ] RSSM 里 $h_t$ 与 $z_t$ 各负责什么？为什么要两条路径？
- [ ] 先验与后验各在什么时候用？KL 平衡在防什么？
- [ ] Dreamer 属于四类用法中的哪一类？它做规划吗？
- [ ] V2 的离散隐变量、V3 的归一化分别解决什么问题？
