# 03 · Agentic RL 后训练主线（伴读）

> 对应原始库：`agentic_rl/`（全库最深，201 文件）。
> 这条主线让你从"会用 LLM"走到"能让 LLM 通过 RL 变强"。和你的 `AgentRl/` 文件夹是同一主题，本伴读负责把 `modern_genai_bilibili` 的笔记串成动线。

## 0. 这条主线在干什么

**Agentic RL = 用强化学习做 LLM 的后训练（post-training）**，让模型在"多步、有环境反馈、可调用工具"的 agent 场景里变强。区别于传统 RLHF（单轮偏好），它强调**多轮、长时间 horizon、环境交互**。

```
SFT（模仿） → RLHF（偏好对齐） → RLAIF/Constitutional → RLVR/RFT（推理增强） → Agentic RL（多步 agent）
```

## 1. 学习动线（务必按顺序）

### 1.1 RL 地基 → `deep_RL/`
顺序严格如下（每个都是下一个的前提）：
```
rl_mdp_bandit_basics      MDP / bandit / 基础定义
  → bellman_equation_最优控制   贝尔曼方程（值函数的递归本质）
  → from_dp_to_rl          动态规划 → 强化学习（采样替代全枚举）
  → mc_td                  MC vs TD（见 02 章）
  → onpolicy_offpolicy     同 02
  → online_offline        online/offline 学习范式
  → pg/                   策略梯度（你之前学过的 ∇logπ·A）
  → actor-critic/          Actor-Critic（策略+值函数）
  → ppo/                  PPO（clip 的重要性采样策略梯度）
  → q-learning/           Q-learning / DQN（值函数方法）
  → group_policy_optimization/   GRPO 家族（组内相对，去掉 critic）
  → align/                对齐方法汇总
  → 稀疏奖励与奖励分配        credit assignment 难题
```

### 1.2 顶层原理笔记（在 `agentic_rl/` 根目录）
- `rft.ipynb`：RFT（Reinforced Fine-Tuning）。拒绝采样微调，**数据来自 base model 自己 rollout**（类 on-policy）。对比 RLHF（主观偏好）vs RFT/RLVR（客观推理）。
- `sft_rl_fkl_rkl.ipynb`：SFT/RL 与 forward/reverse KL 的对照（连回 `02`）。
- `RL-SFT-等价性.ipynb`：在特定设定下 RL 与 SFT 等价——理解"RL 不是魔法"。
- `rlaif_Constitutional_AI.ipynb`：RLAIF，用 AI 反馈替代人类反馈（省标注）。
- `token-seq.ipynb`：token / sequence 层面的 RL 目标差异。

### 1.3 调参实战 → `training_practices/`（极实用，必读）
- `kl_数值内涵.ipynb` / `review_kl.ipynb`：KL 怎么算、forward/reverse 差异（连回 `02`）。
- `entropy.ipynb`：策略熵管理——熵塌方是 RL 训练崩的前兆。
- `训推mismatch.ipynb`：训练（带温度/sampler）与推理（greedy）分布不一致 → 部署掉点。

### 1.4 奖励与推理 → `reward_model/`、`reasoning/`
- `reward_model/`：奖励模型怎么训、奖励黑客（reward hacking）怎么防。
- `reasoning/`：推理模型的 RL（如 o1 类思维链训练思路）。

### 1.5 框架与基础设施（落地关键）
- `verl/`（62 文件）：**最成体系的 RL 训练框架**（HybridFlow 思路，你 `AgentRl/04` 讲过）。这里是从 0 到 1 跑通 PPO/GRPO 的实操。
- `infra/`（27 文件）：训练基础设施——多卡调度、通信、显存、profiling。和你 `升腾910b_infra/` 的 HCCL/msprof 主题可互证。

### 1.6 项目与扩展
- `training_projs/`：端到端训练项目。
- `distillation/`（蒸馏）、`Robotics/`（机器人）、`3D/`、`data-curation/`、`sandbox-env/`、`tasks/`、`cleanrl/`、`trl/`。

## 2. 核心算法族速记（连回你的 AgentRl）

| 算法 | 关键思想 | 去掉了什么 | 库内位置 |
|---|---|---|---|
| PG / REINFORCE | ∇logπ·G | — | `deep_RL/pg` |
| Actor-Critic | PG + 值函数 baseline | 高方差 | `actor-critic` |
| PPO | PG + IS + **clip** | 训练不稳 | `ppo` |
| GRPO | 组内相对优势，**去掉 critic** | critic + 值网络 | `group_policy_optimization` |
| DAPO / Dr.GRPO | GRPO 的工程改进 | 各改一处 | （见 `AgentRl/02`） |

**GRPO 为什么省事**：用"同一 prompt 采样一组回答、组内相对排名"当优势，**不需要单独训一个价值网络（critic）**，显存和稳定性都更好 —— 这也是 DeepSeek 系列用 GRPO 的原因。

## 3. 和你的 `AgentRl/` 文件夹如何配合

- `AgentRl/02_算法`：算法家族 + 伪代码（原理）
- `AgentRl/03_多轮`：AgentRL / RAGEN / StarPO 等具体框架论文
- 本伴读 + `modern_genai_bilibili/agentic_rl/`：同一主题的**动手笔记 + 代码实验**

读的顺序：先本伴读建立动线 → 去 `agentic_rl/deep_RL/` 跑 notebook → 卡住回 `AgentRl/` 看论文级讲解。

## 4. 在原始库里的阅读落点（精确路径）

- `agentic_rl/deep_RL/` 全部（按 1.1 顺序）
- `agentic_rl/rft.ipynb`、`sft_rl_fkl_rkl.ipynb`、`RL-SFT-等价性.ipynb`、`rlaif_Constitutional_AI.ipynb`
- `agentic_rl/training_practices/` 四个笔记
- `agentic_rl/reward_model/`、`reasoning/`、`verl/`、`infra/`

## 验收

- [ ] 能画出"RL 基础 → PPO → GRPO → verl → 落地"的动线
- [ ] 说清 PPO 的 clip 与 IS 作用（连回你之前问的）
- [ ] 说清 GRPO 为什么不需要 critic
- [ ] 能解释 align tax、entropy 塌方、训推 mismatch 三个 RL 后训练坑
- [ ] 能跑通 `verl/` 里至少一个最小 PPO/GRPO 例子
