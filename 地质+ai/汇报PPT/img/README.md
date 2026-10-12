# AI 配图素材（可引用学术来源版）

本目录收集 **PPT 中 AI 相关「〔配图占位〕」** 可直接使用的、来自**原始论文或权威技术博客**的示意图。
文件名规则：`C{章}_P{幻灯片号}_{内容}_{来源}.png`，便于直接对应回 deck 的页码。

> 版权说明：均为各论文/项目的原始插图或官方文档图，用于内部教学汇报请**在图下标注出处**（下表「建议标注」列已给出可直接复制的一行）。对外正式发布前请再确认各来源的许可（多数为 arXiv 非独占许可 / CC-BY-NC-SA / 官方文档）。

---

## 一、清单与对应页码

| # | 文件名 | 对应幻灯片 | 图的内容 | 来源（可引用） | 建议标注 |
|---|--------|-----------|---------|---------------|---------|
| 1 | `C1_P21_underfit-overfit_sklearn.png` | P21 过拟合 vs 泛化 | 左欠拟合 / 中合适 / 右过拟合 三连曲线 | scikit-learn 官方示例图 `plot_underfitting_overfitting` | 图源：scikit-learn 官方文档 |
| 2 | `C1_P22_scaling-law_kaplan2020.png` | P22 大模型「规模越大能力越强」 | 固定算力/步数下，损失随参数量下降 | Kaplan et al., *Scaling Laws for Neural Language Models*, 2020, Fig.11（arXiv:2001.08361） | 图源：Kaplan et al. 2020, arXiv:2001.08361 |
| 3 | `C1_P23_transformer-architecture_vaswani2017.png` | P23 Transformer 架构革命 | Transformer 整体架构图 | Vaswani et al., *Attention Is All You Need*, 2017, Fig.1（arXiv:1706.03762） | 图源：Vaswani et al. 2017, arXiv:1706.03762 |
| 4 | `C1_P23_attention-module_vaswani2017.png` | P23 / P24 注意力机制 | 左：Scaled Dot-Product Attention；右：Multi-Head Attention | 同上，Fig.2 | 图源：Vaswani et al. 2017, arXiv:1706.03762 |
| 5 | `C1_P24_selfattention-viz_jalammar.png` | P24 注意力热力图 | 自注意力权重可视化（热力图） | Jay Alammar, *The Illustrated Transformer* | 图源：J. Alammar, The Illustrated Transformer |
| 6 | `C2_P37_world-model-overview_ha2018.png` | P37 什么是世界模型 | 智能体三件套 V（视觉）/ M（记忆）/ C（控制器） | Ha & Schmidhuber, *World Models*, 2018, Fig.4（arXiv:1803.10122） | 图源：Ha & Schmidhuber 2018, arXiv:1803.10122 |
| 7 | `C2_P37_world-model-schematic_ha2018.png` | P37 什么是世界模型 | 世界模型内部数据流示意 | 同上，Fig.8 | 图源：同上 |
| 8 | `C2_P40_genie_bruce2024.png` | P40 通用世界模型「以生成为主」 | 视频帧 → 离散 token → 生成可交互世界 | Bruce et al., *Genie: Generative Interactive Environments*, 2024, Fig.2（arXiv:2402.15391） | 图源：Bruce et al. 2024, arXiv:2402.15391 |
| 9 | `C2_P51_vit-patch-tokens_dosovitskiy2020.png` | P51 / P52 空间 token 化 | 图像被切成 patch → 每个 patch 变成 token | Dosovitskiy et al., *An Image is Worth 16x16 Words* (ViT), 2020, Fig.1（arXiv:2010.11929） | 图源：Dosovitskiy et al. 2020, arXiv:2010.11929 |
| 10 | `C3_P89_agent-overview_weng2023.png` | P89 智能体的构成（大脑+工具+记忆） | Agent = Planning + Memory + Tools 总览 | Lilian Weng, *LLM Powered Autonomous Agents*, 2023 | 图源：L. Weng, LLM Powered Autonomous Agents (2023) |
| 11 | `C3_P98_rag-pipeline_gao2023.png` | P98 RAG 原理（问题→检索→生成） | RAG 应用于问答的三步流程实例 | Gao et al., *Retrieval-Augmented Generation for LLMs: A Survey*, 2023, Fig.2（arXiv:2312.10997） | 图源：Gao et al. 2023, arXiv:2312.10997 |
| 12 | `C3_P98_rag-three-paradigms_gao2023.png` | P98 / P99 RAG 检索与生成 | Naive / Advanced / Modular 三种 RAG 范式对比 | 同上，Fig.3 | 图源：同上 |
| 13 | `C3_P99_vector-retrieval_weng2023.png` | P99 从问题到资料（语义检索） | 向量最大内积检索（MIPS）示意 | Lilian Weng, *LLM Powered Autonomous Agents*, 2023 | 图源：L. Weng (2023) |
| 14 | `C3_P101_raptor-tree_sarthi2024.png` | P101 语义聚类树 | 按向量嵌入递归聚类、自底向上建树 | Sarthi et al., *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*, 2024, Fig.1（arXiv:2401.18059） | 图源：Sarthi et al. 2024, arXiv:2401.18059 |

**特别说明**：`C3_P101_raptor-tree` 与 deck 里自研的「语义聚类树」思路几乎完全一致，用来解释 P101 非常贴切。
`C2_P51_vit-patch-tokens` 正好可用于澄清 P49/P51 的「空间 token 化」——图像 patch 本身就是空间 token 化的既有做法。

