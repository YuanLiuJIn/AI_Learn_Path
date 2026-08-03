# 扩散模型 / 视觉生成评测：标准、评测集、方法与论文项目

> 整理时间：2026-07。覆盖文生图（T2I）、文生视频（T2V）、图像编辑、个性化生成。

---

## 一、评测标准（维度）

| 维度 | 说明 | 代表指标/评测集 |
|---|---|---|
| 保真度 / 图像质量 | 清晰度、真实感、无伪影 | FID、KID、IS、人评 |
| 图文一致性（Alignment） | 是否画出了 prompt 说的内容 | CLIPScore、GenEval、DPG-Bench、TIFA、VQAScore |
| 组合性（Compositionality） | 属性绑定、空间关系、计数 | T2I-CompBench、GenEval |
| 人类偏好（Aesthetics） | 好不好看、符不符合喜好 | HPSv2、PickScore、ImageReward、Aesthetic Predictor |
| 多样性 | 同 prompt 多样输出、模式坍塌 | Recall/Coverage、LPIPS diversity |
| 安全 / 版权 | NSFW、记忆化复制训练数据 | 记忆化检测、NSFW 分类器 |
| 效率 | 采样步数、延迟、显存 | steps / latency / FLOPs |
| **视频专属** | 时序一致性、运动质量、主体一致性 | VBench、FVD、EvalCrafter |
| **编辑专属** | 编辑成功率 + 非编辑区保持 | ImagenHub、编辑 CLIP 方向相似度 |

---

## 二、核心指标与原始论文

### 2.1 分布级指标
- **IS（Inception Score）** — arXiv:1606.03498（Improved Techniques for Training GANs）
- **FID（Fréchet Inception Distance）** — arXiv:1706.08500（TTUR 论文）。**必须理解其缺陷**：依赖 Inception 特征、对样本量敏感（常需 50k）、与人类判断相关性弱、对图文一致性完全不敏感
- **KID** — 无偏、小样本更稳
- **FVD（Fréchet Video Distance）** — arXiv:1812.01717，视频版 FID，基于 I3D 特征
- **Precision / Recall / Density / Coverage** — 拆分保真度与多样性

### 2.2 图文一致性指标
- **CLIPScore** — arXiv:2104.08718。无参考的图文相似度，最常用但对组合关系不敏感
- **TIFA** — arXiv:2303.11897。用 LLM 生成问题 + VQA 模型作答来验证 prompt 内容是否被画出
- **VQAScore** — arXiv:2404.01291。用 VQA 模型输出 "Yes" 的概率作为一致性分数，对复杂 prompt 显著优于 CLIPScore
- **DPG-Bench** — 密集长 prompt 的一致性评测（ELLA 论文 arXiv:2403.05135 提出）

### 2.3 人类偏好模型（Reward Model）
| 指标 | 论文 | 说明 |
|---|---|---|
| **ImageReward** | arXiv:2304.05977 | 137k 专家对比数据训练的偏好模型，可直接做 RLHF 奖励 |
| **HPS v2** | arXiv:2306.09341 | HPD v2 数据集（798k 对比），跨模型可比性好 |
| **PickScore / Pick-a-Pic** | arXiv:2305.01569 | 真实用户 500k+ 偏好数据，CLIP-H 微调 |
| **Aesthetic Predictor** | LAION | 纯美学打分，无关文本 |

### 2.4 结构化评测集
- **GenEval** — arXiv:2310.11513。用**目标检测器**客观验证：单/双物体、计数、颜色、位置、属性绑定。对象化验证范式的代表作
- **T2I-CompBench (++)** — arXiv:2307.06350。属性绑定 / 空间关系 / 非空间关系 / 复杂组合四大类
- **DrawBench / PartiPrompts** — Imagen、Parti 论文附带的经典 prompt 集，人评为主
- **HEIM（Holistic Evaluation of Text-to-Image Models）** — arXiv:2311.04287，斯坦福，12 个维度整体评估
- **ImagenHub** — arXiv:2310.01596（ICLR'24）。**统一 7 类条件图像生成任务**（T2I、编辑、控制、主体驱动等）的标准化人评框架，含标注规范与一致性分析
- **GenAI-Arena / GenAI-Bench** — arXiv:2406.04485。视觉生成的 Arena 式人类投票平台 + Elo 榜
- **DreamBench++** — arXiv:2406.16855。个性化/主体驱动生成的自动化人类对齐评测

### 2.5 视频生成
- **VBench** — arXiv:2311.17982（CVPR'24 Highlight）。**事实标准**。16 个细粒度维度（主体一致性、背景一致性、时序闪烁、运动平滑度、动态程度、美学质量、成像质量、物体类别、多物体、人物动作、颜色、空间关系、场景、外观风格、时序风格、整体一致性），每个维度都有专门 prompt 套件与人评校准。后续有 **VBench++**、**VBench-2.0**（强调"内在真实性"：物理规律、常识）
- **EvalCrafter** — arXiv:2310.11440（CVPR'24）。17+ 客观指标 + 与人类意见的回归对齐
- **VideoScore** — arXiv:2406.15252（EMNLP'24）。用 VideoFeedback 数据训练的自动评分模型，5 维度模拟人评
- **T2V-CompBench** — 视频组合性评测

### 2.6 图像编辑
- **ImagenHub** 编辑子集、**EditVal**、**Emu Edit Benchmark**
- 常用双指标：编辑区 CLIP 方向一致性（CLIP directional similarity）+ 非编辑区 L1/LPIPS 保持度

---

## 三、评测方法要点（面试重点）

1. **FID 不能单独用**：必须搭配一致性指标 + 偏好指标，形成三角（质量 / 对齐 / 偏好）
2. **自动指标 vs 人评相关性**：EvalCrafter、VBench、HEIM 的核心贡献都在于「用人评校准自动指标」。评测岗要能设计这类相关性验证实验（Spearman / Kendall τ）
3. **人评设计**：双盲 side-by-side、多标注员、Krippendorff's α 计算一致性、防止美学压倒一致性（分开问两个问题）
4. **VQA-based 评测范式**：TIFA / VQAScore / GenEval 代表趋势——**把生成评测转化为可判定的判别问题**
5. **采样设置公平性**：steps、CFG scale、seed、分辨率、negative prompt 必须统一
6. **Reward Hacking**：用 HPSv2/ImageReward 做 RLHF 会导致过饱和油画风，评测时需交叉验证

---

## 四、开源框架与项目

| 项目 | 说明 |
|---|---|
| **VBench**（Vchitect/VBench）| 视频生成评测首选，含 leaderboard |
| **EvalCrafter** | 视频多指标评测工具箱 |
| **ImagenHub**（TIGER-AI-Lab）| 条件图像生成统一评测库 |
| **GenAI-Arena**（TIGER-AI-Lab）| 生成模型 Arena 实现 |
| **T2I-CompBench** / **GenEval** 官方 repo | 组合性评测脚本 |
| **HPSv2** / **ImageReward** / **PickScore** | 偏好模型权重与推理代码 |
| **clean-fid** | 修正 FID 实现不一致问题的库，**强烈推荐**（不同 resize 实现会导致 FID 差异） |
| **HEIM (crfm-helm)** | 整体评估框架的 T2I 版 |
| **t2v-turbo / VideoScore** | 视频自动评分模型 |

---

## 五、精读论文清单

1. **VBench**（2311.17982）— 维度拆解 + 人评校准，方法论范本
2. **GenEval**（2310.11513）— 判别式客观评测
3. **VQAScore**（2404.01291）与 **TIFA**（2303.11897）
4. **HPS v2**（2306.09341）/ **ImageReward**（2304.05977）/ **PickScore**（2305.01569）
5. **ImagenHub**（2310.01596）— 人评标准化流程（评测岗直接可复用的 SOP）
6. **T2I-CompBench**（2307.06350）
7. **HEIM**（2311.04287）
8. **FID 原始论文**（1706.08500）+ 关于 FID 缺陷的批评性工作
9. **EvalCrafter**（2310.11440）、**VideoScore**（2406.15252）

---

## 六、动手任务建议

1. 用 clean-fid 在同一数据集上比较不同实现的 FID 差异，理解指标复现坑；
2. 跑 GenEval + T2I-CompBench 评测 SDXL / FLUX，分析组合性失败模式；
3. 用 VQAScore 与 CLIPScore 对同一批图打分，与自己的人工标注算 Spearman，验证哪个更贴近人类；
4. 用 VBench 评测一个开源视频生成模型，写一份 16 维度的分析报告。
