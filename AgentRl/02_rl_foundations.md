# 02. RL 基础：算法全家桶（REINFORCE / PPO / DPO / GRPO + 变体族）

> 目标：把 Landscape Survey §2.7 提到的算法一个个拆开，配上**目标函数直觉 + 伪代码 + 代表变体**。
> 读完应能回答："为什么 DeepSeek-R1 用 GRPO 而不是 PPO？""DAPO 改了 GRPO 的哪几点？"

## 0. 先建立一个统一视角：它们都是"策略优化"

```text
所有下面算法都在解决同一件事：
  给定一个能打分的环境/奖励，更新策略 πθ 让它生成更高分的轨迹。

区别在于：
  (1) 奖励从哪来？  → Reward Model（RLHF） / 可验证规则（RLVR） / 偏好对（DPO）
  (2) 有没有 Critic？→ PPO 有，GRPO 没有
  (3) 优势怎么估？  → 单样本 / 组内相对 / 偏好对比
  (4) 是否在线？    → 在线探索（PPO/GRPO） vs 离线（DPO）
```

---

## 1. REINFORCE（策略梯度 baseline）

最朴素的策略梯度，是后面所有算法的祖宗。

```text
目标：最大化期望回报 J(θ) = E_{τ~πθ}[ R(τ) ]
梯度：∇J(θ) = E[ ∇log πθ(a|s) · R(τ) ]

问题：方差极大（一次采样就决定梯度方向）
补救：减掉 baseline b（通常用价值函数 V(s) 估计）
```

```python
# 伪代码（带 baseline）
for trajectory in sampled_trajectories:
    for (s, a, r) in trajectory:
        adv = r - V(s)                       # 减 baseline 降方差
        loss += -log_prob(pi_theta, a, s) * adv
theta = theta - lr * grad(loss)
```

> 直觉：REINFORCE 方差大、样本效率低，工业上几乎不用，但它是理解 PPO/GRPO 的钥匙。

---

## 2. PPO（Proximal Policy Optimization）

RLHF 时代的工业标准。Survey 归类为"需 Critic + 裁剪"的稳定算法。

### 目标函数

```text
L_PPO = E[ min( r_t(θ)·Â_t,  clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ] - c·V_loss + β·KL

其中：
  r_t(θ) = πθ(a_t|s_t) / π_old(a_t|s_t)    # 概率比
  Â_t     = 优势估计（由 Critic V 算：Q - V 或 GAE）
  clip    = 把概率比限制在 [1-ε, 1+ε]，防止更新过猛
```

### 关键组件

```text
Critic（价值网络）：估计 V(s)，用于算优势 Â。这是 PPO 区别于 GRPO 的核心成本。
GAE（广义优势估计）：λ 权衡偏差/方差，Â = Σ (γλ)^l δ_{t+l}
KL 惩罚：防止策略偏离参考模型太远（防止 Reward Hacking / 坍塌）
```

### PPO 家族（Survey Table 2 摘录）

```text
VAPO        —— 价值引导的 PPO（解决价值估计偏差）
LitePPO     —— 轻量化
PF-PPO      —— 过程反馈 PPO
VinePPO     —— 用精确 rollout 估计优势（减少方差）
PSGPO       —— 过程级优势 GPO（用于代码 Agent）
```

```python
# 伪代码
for each batch:
    rollout = old_policy.generate(env)          # 采样
    rewards = reward_model(rollout)
    advantages = GAE(rollout, critic)           # 需要 Critic
    for k in range(K):                          # K 次 epoch 复用同批数据
        ratio = pi_new.logp/pi_old.logp
        loss = -min(ratio*adv, clip(ratio,1-ε,1+ε)*adv) + β*KL
        update(pi_new, critic)
```

> 痛点：Critic 要占一份近似于 Actor 的显存/算力，且价值估计不准会传染到策略。

---

## 3. DPO（Direct Preference Optimization）

跳过 Reward Model，直接用偏好对优化。Survey 归类为"离线、免显式 RM"。

### 核心直觉

```text
DPO 证明：在 Bradley-Terry 模型下，最优策略与奖励满足
  r(x,y) = β·log[ π(y|x) / π_ref(y|x) ] + β·log Z(x)
代入偏好损失，Reward Model 被"消掉"，只剩策略对比。
```

### 目标函数

```text
L_DPO = -E[ log σ( β·log[πθ(y_w|x)/π_ref(y_w|x)]
                   - β·log[πθ(y_l|x)/π_ref(y_l|x)] ) ]

y_w = 偏好回答（win），y_l = 非偏好回答（lose）
β   = 偏离参考模型的强度
```

```python
# 伪代码（无需 RM，无需在线环境）
for (x, y_w, y_l) in preference_pairs:
    loss = -log_sigmoid( β*(logp_pi(y_w|x) - logp_ref(y_w|x))
                       - β*(logp_pi(y_l|x) - logp_ref(y_l|x)) )
    update(pi_theta)
```

### DPO 家族

```text
β-DPO / SimPO / IPO / KTO / ORPO   —— 改权重/损失形式
Step-DPO / LCPO                    —— 步级/长度控制偏好
Step-DPO                           —— 把偏好细化到单个推理步骤（连到 §3.7 信用分配）
```

> 优点：稳定、便宜、不需 Critic；缺点：离线、受限于已有偏好数据、无在线探索。

---

## 4. GRPO（Group Relative Policy Optimization）

DeepSeek-R1 引爆的算法，Agent RL 当前主流。Survey 归类为"免 Critic、组内相对优势"。

### 核心思想

```text
对同一 prompt 采样一组 G 个回答 {o_1..o_G}
用组内相对分数（去掉均值、除标准差）当优势 —— 省掉整个 Critic！
```

### 优势估计

```text
Â_i = (r_i - mean(r_1..r_G)) / std(r_1..r_G)
# 不需要价值网络 V，组内归一化自动处理了奖励尺度问题
```

### 目标函数

```text
L_GRPO = -E[ (1/G)·Σ_j min( r_j·Â_j, clip(r_j,1-ε,1+ε)·Â_j ) ] + β·KL[πθ ‖ π_ref]
```

### 为什么比 PPO 适合 Agent RL？

```text
1. 不要 Critic → 省一半显存，训练更简单
2. 组内归一化 → 不受奖励绝对值尺度影响（不同任务奖励量级不同）
3. 稳定 → 比 PPO 更不容易崩
```

### GRPO 家族（Survey Table 2 重点，爆发于 2025）

```text
DAPO      —— Dynamic Sampling + Clip-Higher + Token-level Loss + Overlong Reward
            （解决"组内全对/全错导致梯度为 0"和长文本惩罚问题）
Dr.GRPO   —— 去掉 GRPO 里的 bias（如长度归一化陷阱），更 pure
GSPO      —— Group Sequence Policy Optimization（按序列而非 token 归一化，更稳）
DARS      —— 动态优势重缩放
SRPO / GRESO / GHPO / ASPO / TreePo / EDGE-GRPO / CHORD / PAPO / Pass@k Training
StarPO    —— 轨迹级（Star Personality？其实是轨迹级 GRPO，连到 RAGEN，见 03）
Step-GRPO —— 步级 GRPO（过程信号）
```

> 关键认知：**GRPO 不是"一个算法"，而是一个家族**。DAPO/Dr.GRPO/GSPO 都是
> 针对不同痛点（方差、偏差、稳定性）的改进。读论文时别只说"用了 GRPO"，
> 要问"用的哪个变体、改了哪点"。

---

## 5. 四家族对比表（精要）

| | REINFORCE | PPO | DPO | GRPO |
|---|---|---|---|---|
| 需 Critic | ❌(但需 baseline) | ✅ | ❌ | ❌ |
| 需 Reward Model | 视奖励来源 | ✅ | ❌(偏好替代) | 可选 |
| 在线探索 | ✅ | ✅ | ❌ | ✅ |
| 优势来源 | 整轨迹回报 | GAE(Critic) | 偏好对比 | 组内相对 |
| 训练稳定性 | 低 | 中 | 高 | 较高 |
| 代表 | — | InstructGPT | Zephyr | DeepSeek-R1 |
| 适用 | 教学 | RLHF | 离线偏好 | Agent RL/RLVR |

---

## 6. 和 Landscape Survey 的衔接

```text
Survey §2.7 把算法划为两大类：
  PBRFT（偏好型强化微调）← 单步 MDP，对应 PPO/DPO 做对齐
  Agentic RL（环境交互）  ← POMDP，对应 GRPO 家族 + 策略梯度做 Agent 训练

你会在 §3 看到：
  规划里用 DPO（ETO）→ 把成败轨迹当偏好
  工具里用 GRPO（ToolRL/ReTool）→ 环境可验证奖励
  自我改进里用 Reflection-DPO → 把"反思后"当 win
同一个算法，因"奖励从哪来"不同而落到不同分类。
```

## 7. 下一步

进入 `03_multi_turn_agent_rl.md`，看这些算法在**多步 POMDP** 里怎么落地，
以及 AgentRL / RAGEN / AgentGym-RL 各自怎么解决多轮训练的痛点。

## 8. 一句话总结

> REINFORCE 是祖宗，PPO 靠 Critic 稳但贵，DPO 离线免 RM 但无探索，GRPO 用
> 组内相对优势去掉 Critic 成为 Agent RL 主流。但 GRPO 已是家族（DAPO/Dr.GRPO/GSPO…），
> 读论文务必分清"用哪个变体、改了哪点"——这正是 Survey Table 2 的价值。
