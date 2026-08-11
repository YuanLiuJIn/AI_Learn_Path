# AgentRl/docs — 论文库（PDF 索引）

> 本文件夹存放本专题的**核心论文 PDF 原件**，与 `../references.md`（在线链接版）互为补充。
> 全部 PDF 已下载至 `docs/papers/`，离线可读。
> 标注 🔥 的为该论文**直接面向"长程 / 多轮 / 信用分配"问题**，是这次专题重点。

---

## 一、总纲综述（起点必读）

| 文件名 | 论文 | 主题 |
|---|---|---|
| `Landscape_Survey_AgenticRL.pdf` | The Landscape of Agentic RL for LLMs: A Survey (arXiv:2509.02547) | 500+ 篇工作总览，MDP/POMDP 形式化 + "能力×任务"双重分类法。§3.7 即"长 horizon 信用分配"专章 |

## 二、基础 RL 算法（阶段 1 配套）

| 文件名 | 论文 | 关键改动 |
|---|---|---|
| `PPO.pdf` | Proximal Policy Optimization (arXiv:1707.06347) | clip 约束，稳定策略梯度 |
| `DPO.pdf` | Direct Preference Optimization (arXiv:2305.18290) | 消掉显式 reward model |
| `GRPO_DeepSeekMath.pdf` | DeepSeekMath / GRPO (arXiv:2402.03300) | 组内相对优势，省 Critic |
| `DAPO.pdf` 🔥 | Dynamic Sampling + Clip-Higher (arXiv:2503.14476) | 解耦 clip / token-level 损失 / 动态采样，专治长序列训练不稳 |
| `Dr_GRPO.pdf` 🔥 | Dr.GRPO (arXiv:2503.20783) | 去掉 GRPO std 归一化偏置，长轨迹更稳 |
| `GSPO.pdf` 🔥 | Group Sequence Policy Optimization (arXiv:2507.18071) | 策略比从 token 级改 sequence 级，长程训推更一致 |
| `DeepSeek-R1.pdf` | DeepSeek-R1 (arXiv:2501.12948) | RLVR + GRPO 推理范式 |

## 三、多轮 / 长程 Agent RL 框架（阶段 2 配套，🔥重点）

| 文件名 | 论文 | 解决的长程痛点 |
|---|---|---|
| `AgentRL.pdf` 🔥 | AgentRL: Scaling Agentic RL with Multi-Turn (arXiv:2510.04206) | 全异步生成-训练架构，长程才 scalable（GPU 不空转） |
| `RAGEN_StarPO.pdf` 🔥 | RAGEN + StarPO (arXiv:2504.20073) | 四元组轨迹级表示 + 轨迹级优势，天然适配多轮 |
| `AgentGym-RL.pdf` 🔥 | AgentGym-RL (arXiv:2509.08750) | 长程决策 + 跨多环境统一轨迹格式 |
| `MUA-RL.pdf` 🔥 | MUA-RL (arXiv:2508.18669) | 多轮用户交互 + 用户意图漂移的非平稳性 |
| `AgentPRM.pdf` 🔥 | AgentPRM (arXiv:2502.10325) | MC 采样从成功路径反推每步价值 → 信用分配核心武器 |

> 注：`Verlog`（变长 episode 动态 batch，CMU blog）为博客非 arXiv，未存 PDF，见 `../references.md` 链接。
> `ASPO / GiGPO / SpaRL / EPO / SDPO / Step-GRPO` 等长 horizon 优势方法，目前多散见于 Survey §3.2/§3.7 与各框架论文，暂无统一独立 PDF，以 `../03_multi_turn_agent_rl.md` 与 `../05_reward_design.md` 的导读为准。

## 四、怎么用这套 PDF

```text
1. 读顺序：先看 Landscape_Survey（建立地图）→ 按需翻开对应算法/框架 PDF 的 §Method
2. 长程专题：重点读 🔥 标记 7 篇，配合 ../03、../05 的导读
3. 对照表：每篇 PDF 在 ../references.md 都有在线链接 + 中文解读，可比对
4. 笔记法：用 ../00_learning_path.md §3 的"6 问模板"拆解每篇
```

## 五、文件清单（校验用）

```text
docs/papers/
├── Landscape_Survey_AgenticRL.pdf   ~9.4 MB
├── PPO.pdf                          ~2.9 MB
├── DPO.pdf                          ~1.3 MB
├── GRPO_DeepSeekMath.pdf            ~1.8 MB
├── DAPO.pdf                         ~0.8 MB
├── Dr_GRPO.pdf                      ~1.6 MB
├── GSPO.pdf                         ~0.4 MB
├── DeepSeek-R1.pdf                  ~4.9 MB
├── AgentRL.pdf                      ~1.5 MB
├── RAGEN_StarPO.pdf                 ~1.8 MB
├── AgentGym-RL.pdf                  ~0.7 MB
├── MUA-RL.pdf                       ~4.5 MB
└── AgentPRM.pdf                     ~4.5 MB
```
