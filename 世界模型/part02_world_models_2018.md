# Part02：World Models 论文精读与复现（第 3–4 周）

> 本部分只做一件事：把 **Ha & Schmidhuber (2018), _World Models_** 彻底读懂，并跑通 `worldmodels.github.io` 的交互实验。
> 这篇论文的价值不在于效果多强，而在于它第一次把"在梦里训练智能体"这条流水线完整跑通，并且每个模块都简单到可以手写。

前置：完成 `part01_rl_basics_and_mbrl_survey.md`（MDP、四类模型用法、Dyna-Q、compounding error）。

> 路线微调说明：Part01 中把 PlaNet/RSSM 也列在第 3–4 周，实际执行时建议**顺延到 Part03**。
> 原因：World Models 与 RSSM 虽然思想相关，但前者的训练管线（VAE → MDN-RNN → CMA-ES）本身就足够占满两周，混着学容易两头都不透。

```text
两周目标
  Week 3：读懂三组件 + 数学目标 + 设计动机，跑通网页交互实验
  Week 4：跑通官方代码 / 自写 VAE+RNN，尝试"在梦中训练控制器"
```

---

## 1. 论文速览

| 项 | 内容 |
|---|---|
| 论文 | *World Models*, David Ha, Jürgen Schmidhuber, 2018, arXiv:1803.10122 |
| 会议版 | *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1809.01999 |
| 官网/交互版 | worldmodels.github.io（可交互文章 + 在线 demo + Colab 训练入口） |
| 代码 | `hardmaru/WorldModelsExperiments`（官方，TensorFlow）、`hardmaru/estool`（CMA-ES/ES 工具） |
| 一句话贡献 | 用 VAE + MDN-RNN 学一个**隐空间世界模型**，让一个极小的控制器完全在这个模型内部"做梦"训练 |
| 影响 | Dreamer 系列、Genie、视频世界模型的思想源头之一；"世界模型"进入大众视野的起点 |

论文的两条主线：

```text
主线一：结构 —— 视觉压缩(V) + 时序记忆(M) + 决策(C) 分工
主线二：范式 —— 控制器可以不在真实环境中训练，而在模型生成的"梦"里训练
```

这两条线分别对应 Part01 里 MBRL 综述的"问题一（模型怎么学）"和"问题二（模型怎么用）"。

### 1.1 实验环境

| 环境 | 任务 | 说明 |
|---|---|---|
| **CarRacing-v0** | 俯视视角赛车，连续转向/油门/刹车 | OpenAI Gym，需要像素输入，逼真到"看画面开车" |
| **VizDoom** | 3D 第一人称射击，只有"移动+射击" | 训练智能体在虚拟场景中生存/击杀 |

两个环境的共同点：**观测是高维像素（64×64×3），状态不可直接获得**。这正是世界模型的用武之地。

---

## 2. 三大组件详解

论文把智能体拆成三块，符号沿用原文：

```text
         ┌─────────────────────────────────────────┐
         │  V：Vision (VAE)  观测 → 隐状态 z        │
         │  M：Memory (MDN-RNN)  预测下一个 z       │
         │  C：Controller  在 z（和 h）上决定动作 a │
         └─────────────────────────────────────────┘

真实环境 rollout：  o_t ──V──► z_t ──C──► a_t ──► 环境 ──► o_{t+1}
模型（梦境）rollout：z_t ──M──► ẑ_{t+1} ──C──► a_t ──► M ──► ...
```

### 2.1 V：Vision，把画面压成向量

- 结构：标准 VAE（卷积编码器 → 32 维隐向量 $z$ → 卷积解码器）
- 输入：单帧图像 $o_t$（64×64×3）
- 损失：重建误差 + KL 正则

$$
\mathcal{L}_{V}=\underbrace{\mathbb{E}\big[-\log p(o_t\mid z_t)\big]}_{\text{重建}}\;+\;\underbrace{D_{\mathrm{KL}}\big(q(z_t\mid o_t)\,\|\,\mathcal{N}(0,I)\big)}_{\text{让隐空间规整}}
$$

理解要点：

1. VAE 的作用**不是让人看懂重建图，而是给 M 和 C 一个低维、平滑、可控的输入**。
2. 重建质量对控制的影响有上限：论文的 VAE 重建出的画面相当模糊，控制器依然能开车。所以**别把时间全花在调 VAE 画质上**。
3. KL 项是隐空间"规整"的来源：没有它，$z$ 的分布会碎成记忆点，M 无法学到连续的动力学。

### 2.2 M：Memory，预测"下一个隐状态"

这是全篇最重要的部分，也是最多人读不懂的部分。

- 结构：RNN（LSTM），输出**混合密度网络（MDN）**参数
- 输入：$z_t$ 与上一时刻动作 $a_t$、隐状态 $h_t$
- 输出：$z_{t+1}$ 的**概率分布**，而不是一个确定值

$$
p(z_{t+1}\mid a_t,\;z_t,\;h_t)=\sum_{i=1}^{K}\pi_i\,\mathcal{N}\!\big(z_{t+1};\mu_i,\sigma_i^2\big),\qquad K\approx 5
$$

训练目标是最小化负对数似然（NLL）：

$$
\mathcal{L}_{M}=-\sum_{t}\log p(z_{t+1}\mid a_t,z_t,h_t)
$$

**为什么必须是混合分布，而不是单高斯？**

```text
场景：CarRacing 前方有障碍，可以左转也可以右转。
单高斯模型会把两条可能的未来平均成"直着撞上去"——
一个现实中不存在、却"概率最大"的预测。
混合分布能同时保留多个模式（多峰），因此预测更可信。
```

**温度参数 τ**：采样时把方差乘以 τ：

```text
z_{t+1} ~ Σ_i π_i · N(μ_i, σ_i² · τ)

τ = 0     → 确定性预测（模型最"自信"，也最容易骗过控制器）
τ = 1     → 原始分布
τ > 1     → 更随机，注入噪声（论文训练 CarRacing 控制器时用 τ ≈ 1.15）
```

这条设计是"防模型被滥用"的最原始版本，回头对照 Part01 的陷阱 2。

### 2.3 C：Controller，极小、极简、用进化策略优化

- 结构：**单层线性模型**，输入 $[z_t; h_t]$，输出动作
- 优化：**CMA-ES**（协方差矩阵自适应进化策略），不是梯度下降

$$
\theta \leftarrow \theta+\eta\,\mathbb{E}_{\epsilon}\big[\epsilon\,\mathcal{R}(\theta+\sigma\epsilon)\big]
$$

理解要点：

1. 控制器参数量极小（几百个），所以可以在**噪声很大**的梦境里靠进化策略搜出来，不需要可微路径。
2. 用 ES 而不是梯度，绕开了"如何通过采样出的随机 $z_{t+1}$ 反传梯度"这个难题（这个难题后来由 Dreamer 用重参数化 + 解析梯度解决，见 Part03）。
3. **不把 $h_t$ 输入给 C 的实验**（只用 $z_t$）会显著变差——这是"记忆"对策略必要性的直接证据，也是 NeurIPS 版论文的重点之一。

### 2.4 三组件对照表

| 组件 | 角色 | 结构 | 目标函数 | 训练方式 | 对应 Part01 概念 |
|---|---|---|---|---|---|
| V (VAE) | 压缩观测 | 卷积 VAE，$z$ 约 32 维 | 重建 + KL | 反向传播 | 表征学习 |
| M (MDN-RNN) | 学动力学 | LSTM + 5 个高斯混合 | NLL（等价 KL） | 反向传播（BPTT） | $p(z_{t+1}\mid z_t,a_t)$ |
| C (Controller) | 做决策 | 单层线性 | 最大化累计回报 | CMA-ES | 策略 $\pi(a\mid z,h)$ |

> 超参（$z$ 维度、$h$ 维度、混合数、τ 取值）各环境不同，**以论文附录与官方代码为准**，不要背数字。

---

## 3. 三个关键设计问答

### 3.1 为什么三个模块分开训练，不做端到端？

```text
若端到端联合训练：
  - 需要可微地把"采样"打通（当时缺成熟的重参数化 + 稳定的训练配方）
  - 梯度要从策略回传到动力学，再从动力学回传到像素，
    噪声大、易崩，且无法解释"到底哪部分坏了"

分开训练的好处：
  - 每个模块可以单独评估（重建图、预测误差、控制回报各看各的）
  - 可以用不同优化器（V/M 用梯度，C 用进化策略）
代价：
  - 表征只为重建优化，不为控制优化 → 这正是 Dreamer 后来把
    "表征 + 奖励 + 价值 + 策略"放进同一目标去优化（Part03）的动机
```

### 3.2 为什么叫"在梦里训练"（training inside the dream）？

```text
控制器 C 的训练数据全部来自 M 的虚拟 rollout：
  真实环境只用来训练 V 和 M（学世界），之后 C 完全不接触真实环境。

优点：样本效率极高（真实交互只用于建模型）
风险：C 会利用 M 的预测误差（model exploitation）
      ——模型说"往这儿冲得分最高"，现实里就撞墙了

论文的缓解手段：提高 τ（注入随机性），让 C 无法过度依赖模型的
              精确预测，从而学到更鲁棒的策略。
```

### 3.3 这篇论文在 Part01 的四类用法里属于哪一类？

| 问题 | 答案 |
|---|---|
| 它学什么模型？ | 隐空间动力学 $p(z_{t+1}\mid z_t,a_t)$ + 观测编码器（V 即推理模型 $q(z\mid o)$） |
| 它怎么用模型？ | **① 当模拟器产数据**（Dyna-style），把假 rollout 交给进化策略训练 C |
| 有规划吗？ | 没有（不像 PlaNet/MuZero 那样在线搜索） |
| 有复用真实数据做额外更新吗？ | 有，Dyna-Q 的精神在 V/M 与 C 的分工里被放大 |

**一句话定位**：World Models = Dyna 的深度版，把"模型"从表格换成 VAE + RNN，把"更新 Q"换成"用 ES 训一个线性控制器"。

---

## 4. 完整训练管线

```text
阶段 0  采集数据
   随机策略（或简单策略）在环境中跑若干回合，存下 (o_t, a_t, r_t) 序列
        │
        ▼
阶段 1  训练 V：VAE
   输入单帧 o_t → 重建 o_t；得到编码器 q(z|o)
        │
        ▼
阶段 2  用 V 把整条轨迹编码成 z 序列，训练 M：MDN-RNN
   输入 (z_t, a_t, h_t) → 预测 z_{t+1} 的混合高斯分布（NLL 损失）
        │
        ▼
阶段 3  固定 V 与 M，训练 C：线性控制器 + CMA-ES
   在 M 生成的"梦境"里 rollout，最大化累计回报（可加 τ 增大随机性）
```

各阶段的可观测信号（用来判断"到底哪一步坏了"）：

| 阶段 | 观察指标 | 健康标准 |
|---|---|---|
| 1 VAE | 重建图、隐空间 KL | 画面轮廓大致还原（模糊正常）；KL 不塌缩到 0 |
| 2 RNN | 单步预测的 NLL、预测帧可视化 | NLL 稳定下降；τ=0 的预测能大致"续上"画面 |
| 3 Controller | 梦境回报 vs 真实环境回报 | 两者接近说明模型可信；梦境高而现实低 = 模型被滥用 |

> **最关键的一组对比**：同一个控制器，在**梦境**中的平均回报与在**真实环境**中的平均回报。
> 二者差距就是"世界模型误差"的直接度量，也是这篇论文最值得自己动手验证的地方。

---

## 5. worldmodels.github.io 实验

这是论文的**交互式版本**（可理解为"论文 + 演示 + 代码入口"三合一），是把抽象概念变直觉的最快方式。

### 5.1 建议的浏览顺序（约 1.5 小时）

| 顺序 | 做什么 | 目的 |
|---|---|---|
| 1 | 读架构总览图与三组件说明 | 建立"V/M/C 各管一段"的心智图 |
| 2 | 玩 CarRacing / VizDoom 在线 demo | 直观看到"模糊重建 + 简单控制器"也能开车 |
| 3 | 看 VAE 重建与 RNN 预测帧的可视化 | 亲眼看到预测帧在几帧后开始"糊"——compounding error 的具象化 |
| 4 | 打开页面提供的 Colab 训练入口 | 确认三段训练各占多少算力、分别需要多久 |
| 5 | 回到论文原文对照读 | 网页给你直觉，论文给你公式与超参 |

### 5.2 Colab 实验的最小路径

```text
目标：不做完整复现，只验证"梦境可训练"这件事

Step 1  用预训练/短训的 VAE 把 CarRacing 帧编码成 z
Step 2  训练 MDN-RNN（缩短序列长度与轮数即可）
Step 3  用 CMA-ES 在 M 上训练线性控制器（可只用几百代）
Step 4  把同一控制器放回真实环境评估，记录"梦境回报 vs 真实回报"
```

注意：官方实验代码基于 **TensorFlow 1.x**（`tf.placeholder` 风格），在当今 Colab 默认环境里需要 `tf.compat.v1` 或手动装 TF1，否则会直接报错。若不想折腾，两条替代路径：

1. 只跑网页/Colab 上已经准备好的 notebook（最省事）；
2. 自己用 PyTorch 重写三个模块（推荐，代码量不大，理解最深）。

### 5.3 环境安装的坑（本地复现才会遇到）

| 问题 | 说明 |
|---|---|
| `CarRacing-v0` 已从新版 Gym 移除 | 需要旧版 `gym==0.21.0` + `box2d-py`，或改用 Gymnasium 的 `CarRacing-v3` 并适配 `render_mode="rgb_array"` |
| 观测尺寸 | 需要把 96×96 的画面缩放/裁剪到 64×64×3，否则 VAE 与论文不一致 |
| VizDoom | 需单独 `pip install vizdoom` 并下载 `.wad` 场景文件，配置成本高于 CarRacing |
| 渲染依赖 | Linux 下需 `xvfb` 做无头渲染，Mac 上 `render_mode` 行为不同 |

**建议**：本地只用 CarRacing，VizDoom 交给 Colab 或直接跳过（它对理解论文结构没有额外贡献）。

---

## 6. 代码骨架（PyTorch，可直接照写）

### 6.1 V：VAE

```python
class VAE(nn.Module):
    def __init__(self, z_dim=32):
        super().__init__()
        self.enc = nn.Sequential(          # 64x64x3 -> 特征
            nn.Conv2d(3, 32, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(32, 64, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(128, 256, 4, 2, 1), nn.ReLU(), nn.Flatten(),
        )
        self.mu, self.logvar = nn.Linear(256 * 4 * 4, z_dim), nn.Linear(256 * 4 * 4, z_dim)
        self.dec = nn.Sequential(
            nn.Linear(z_dim, 256 * 4 * 4), nn.ReLU(), nn.Unflatten(1, (256, 4, 4)),
            nn.ConvTranspose2d(256, 128, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, 2, 1), nn.Sigmoid(),
        )

    def encode(self, x):
        f = self.enc(x)
        return self.mu(f), self.logvar(f)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)   # 重参数化
        return self.dec(z), mu, logvar
```

```python
# 损失：重建 + KL
recon_loss = F.mse_loss(recon, x, reduction="none").sum(dim=(1, 2, 3)).mean()
kl_loss = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1).mean()
loss = recon_loss + kl_loss          # 实践中常对 kl_loss 加权重（如 1.0 起步，看 KL 是否塌缩）
```

### 6.2 M：MDN-RNN

```python
class MDNRNN(nn.Module):
    def __init__(self, z_dim=32, a_dim=3, h_dim=256, n_mix=5):
        super().__init__()
        self.n_mix, self.z_dim, self.h_dim = n_mix, z_dim, h_dim
        self.rnn = nn.LSTM(z_dim + a_dim, h_dim, batch_first=True)
        self.pi   = nn.Linear(h_dim, n_mix)
        self.mu   = nn.Linear(h_dim, n_mix * z_dim)
        self.sig  = nn.Linear(h_dim, n_mix * z_dim)     # 输出 log σ²，保证为正

    def forward(self, z, a, h=None):
        out, h = self.rnn(torch.cat([z, a], dim=-1), h)
        return self.pi(out), self.mu(out), self.sig(out), h
```

```python
# NLL 损失（log-sum-exp 保证数值稳定）
def mdn_loss(pi, mu, log_sig, target, n_mix, z_dim):
    B, T, _ = mu.shape
    mu = mu.view(B, T, n_mix, z_dim)
    log_sig = log_sig.view(B, T, n_mix, z_dim)
    tgt = target.unsqueeze(2)                                   # B,T,1,z
    log_gauss = -0.5 * (((tgt - mu) ** 2) / log_sig.exp()
                        + log_sig + math.log(2 * math.pi)).sum(-1)   # B,T,n_mix
    log_pi = F.log_softmax(pi, dim=-1)                          # B,T,n_mix
    return -torch.logsumexp(log_pi + log_gauss, dim=-1).mean()
```

### 6.3 梦境 rollout + CMA-ES 训练控制器

```python
def dream_rollout(M, C, z0, h0, horizon=500, tau=1.15):
    """在 MDN-RNN 内部 rollout，只返回累计回报（CMA-ES 只需要一个标量）"""
    z, h, total = z0, h0, 0.0
    for _ in range(horizon):
        a = C(torch.cat([z, h.squeeze(0)], dim=-1))
        pi, mu, log_sig, h = M(z.unsqueeze(0), a.unsqueeze(0), h)
        # 按混合权重采样，方差乘上温度 tau
        k = torch.multinomial(F.softmax(pi[0, 0], dim=-1), 1)
        m = mu[0, 0].view(M.n_mix, M.z_dim)[k]
        s = log_sig[0, 0].view(M.n_mix, M.z_dim)[k].exp()
        z = m + s * tau ** 0.5 * torch.randn_like(m)
        total += 0.0        # 真实实现里用 M 输出的 reward 头（或环境奖励的预测）打分
    return total
```

```python
import cma          # pip install cma
es = cma.CMAEvolutionStrategy(theta0, sigma0=0.1)
while not es.stop():
    solutions = es.ask()
    es.tell(solutions, [-dream_rollout(M, set_params(C, s), z0, h0) for s in solutions])
```

三个必须自己动手验证的小结论：

1. **τ 的影响**：τ=0 时梦境回报涨得最快但真实回报差；τ≈1.1–1.2 更平衡（复现论文结论）。
2. **$h$ 的必要性**：把 $h$ 从控制器输入里去掉，CarRacing 表现会明显退化。
3. **梦境 vs 现实**：把同一个控制器的两组回报画成曲线，差值就是模型误差的代价。

---

## 7. 六个常见误解

| 误解 | 事实 |
|---|---|
| 三个模块是端到端联合训练的 | 分开训练：V 与 M 用梯度，C 用 CMA-ES，互不回传 |
| 控制器是个大网络 | 论文里是**单层线性**模型，参数量极小 |
| 世界模型就是视频生成 | 这里学的是**隐空间动力学**，重建只是副产品 |
| 重建越清晰控制越好 | 论文的 VAE 重建很模糊，照样能开车；重建不是目标 |
| "在梦里训练"总能提升表现 | 模型误差会被控制器利用，必须靠 τ、短视野等手段约束 |
| CarRacing 上跑通就等于复现了论文 | 论文另有 VizDoom 与多组消融；至少要复现 τ 与 $h$ 两个对比 |

---

## 8. 两周日程表

| 天 | 任务 |
|---|---|
| D1 | 论文第 1–2 章 + 网页架构图；写"三组件各干什么"一页笔记 |
| D2 | VAE 部分精读（含附录），手推重建 + KL 损失 |
| D3 | 网页 demo + 预测帧可视化，记录"第几帧开始糊" |
| D4 | 自写 VAE 并在 CarRacing 帧上训练，检查重建与 KL |
| D5 | MDN-RNN 部分精读，手写混合高斯 NLL |
| D6 | 训练 MDN-RNN（τ=0 与 τ=1.15 各一版），对比预测帧 |
| D7 | 复盘 + 用 7.1 模板（Part01）填两篇笔记 |
| D8 | 网页 Colab 入口跑通，或搭好本地环境（CarRacing-v3 + 缩放） |
| D9 | 实现梦境 rollout，先用手工权重验证流程能跑 |
| D10 | 接 CMA-ES，训练一个能过弯的简易控制器 |
| D11 | 做 τ 对比实验 + $h$ 消融实验 |
| D12 | 画"梦境回报 vs 真实回报"曲线，写分析 |
| D13 | 读 NeurIPS 版（1809.01999）差异部分 + estool 代码结构 |
| D14 | 写本 Part 小结：一句话说清"为什么这样分工" + 更新术语表 |

---

## 9. 自检清单

- [ ] 能用一句话说清 V、M、C 各自的输入、输出、损失函数。
- [ ] 为什么 M 输出混合高斯而不是单高斯？τ 在采样时起什么作用？
- [ ] 为什么控制器用 CMA-ES 而不是梯度下降？这个选择在 Dreamer 里被怎样改掉？
- [ ] "在梦里训练"的好处和代价分别是什么？论文如何缓解代价？
- [ ] 为什么 $h$ 输入给控制器很重要？去掉会怎样？
- [ ] 为什么说 VAE 的重建质量对控制不是首要目标？
- [ ] 这篇论文属于 Part01 四类用法中的哪一类？它缺了哪一类的能力（规划）？
- [ ] 我自己复现的"梦境回报 vs 真实回报"差距有多大？差距来自哪里？

## 10. 衔接 Part03（Dreamer）

World Models 留下的三个"待解决"问题，正是 PlaNet → Dreamer 的演进主线：

```text
问题 1  三个模块分开训练，表征不为控制服务
        → Dreamer：把世界模型与 actor-critic 放到同一目标里优化

问题 2  用 ES 训练控制器，样本效率和可扩展性有限；且无法穿越随机采样反传
        → Dreamer：重参数化 + 解析梯度，直接在想象中反传

问题 3  VAE 重建像素，容量浪费在背景上；无法处理部分可观测
        → PlaNet/Dreamer：RSSM（确定性路径 + 随机路径）显式建模 POMDP

另外：学完本篇后，MuZero 在 Part04 会作为"不做重建"的对照再次出现。
```

---

## 11. 本部分参考资源

| 类型 | 资源 |
|---|---|
| 论文 | Ha & Schmidhuber, *World Models*, 2018, arXiv:1803.10122 |
| 论文 | *Recurrent World Models Facilitate Policy Evolution*, NeurIPS 2018, arXiv:1809.01999 |
| 交互版 | worldmodels.github.io（架构图、在线 demo、Colab 入口） |
| 代码 | `hardmaru/WorldModelsExperiments`（官方，TF1）、`hardmaru/estool`（CMA-ES/ES） |
| 博客 | David Ha 的 otoro.net 系列（含 ES 与 CarRacing 的实践文章） |
| 博客 | Danijar Hafner 的 danijar.com（后续 Dreamer 系列的动机，读 Part03 前先看） |
| 课程 | CS285 的 Latent Variable Models / Model-Based RL 讲次（ELBO 与隐模型推导） |
| 综述 | Moerland et al., *Model-based RL: A Survey*, 2020（把本篇放回四类用法） |
| 对照 | 本仓库 `../Part5_reinforcement_learning/09_modelbased_alphazero.md`（另一条"学模型/用模型"的路线） |
