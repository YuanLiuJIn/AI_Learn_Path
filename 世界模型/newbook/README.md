# 世界模型学习教程（分章版）

> 本系列把"800 字总览"展开为 5 个章节，每章约 1500–2000 字，聚焦一个主题，兼顾深度与可读性。
> 目标：把读者从**零基础**带到能读懂 Dreamer、JEPA、扩散世界模型论文，并动手做小实验。

**一句话定义**：世界模型是智能体对环境动态的**内部可预测模型**，回答"如果这样做，接下来会发生什么"（$p(s_{t+1}\mid s_t,a_t)$），而非"该做什么"。它是环境的廉价替身——在它里面练习，再回到真实世界决策。

## 目录

| 章节 | 主题 | 关键词 |
|---|---|---|
| [Chapter 01](ch01_overview.md) | 总览与核心思想 | 定义、三大流派、阅读地图 |
| [Chapter 02](ch02_dreamer.md) | 经典世界模型：Dreamer 系列 | RSSM、想象训练、V1→V3 |
| [Chapter 03](ch03_ebm_diffusion.md) | 基于能量的世界模型：EBM 与扩散 | 能量函数、Diffusion Forcing、DIAMOND |
| [Chapter 04](ch04_jepa.md) | 联合嵌入预测架构：JEPA / I-JEPA | 表征预测、防坍塌、V-JEPA 2 |
| [Chapter 05](ch05_comparison_future.md) | 对比与融合：未来方向 | 评估、混合架构、开放问题 |

## 三大流派一眼看懂

| 流派 | 预测目标 | 代表 | 一句话 |
|---|---|---|---|
| MBRL（潜在动力学） | 隐状态 | Dreamer、PlaNet、MuZero | 压缩世界，为了决策 |
| EBM / 扩散 | 能量 / 像素分布 | LeCun 2022、Diffusion Forcing、DIAMOND | 建模不确定性与多模态未来 |
| JEPA | 抽象表征 | I-JEPA、V-JEPA 2 | 只预测"含义"，不重建像素 |

## 阅读路径（按需选择）

- **只想快速了解**：Ch01 → Ch05
- **做 RL / 机器人决策**：Ch01 → Ch02 →（Ch04 的 V-JEPA 2）
- **做视频生成 / 仿真**：Ch01 → Ch03 →（Ch05）
- **做自监督表征**：Ch01 → Ch04
- **完整打底**：Ch01 → Ch02 → Ch03 → Ch04 → Ch05

> 每章末尾都有"自检清单 / 资源"小节，读完一章做一次自检即可。
> 与本仓库 `../part01_rl_basics_and_mbrl_survey.md`、`../part02_world_models_2018.md` 互为补充：那两篇是单篇论文精读，本系列是**脉络与对比**。
