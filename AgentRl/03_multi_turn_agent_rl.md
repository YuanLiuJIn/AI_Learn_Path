# 03. 多轮 Agent RL：从"生成"到"交互"（框架与代表论文）

> 目标：把「单步 MDP」升级到「多步 POMDP」后，训练到底难在哪？
> 用 AgentRL / RAGEN+StarPO / AgentGym-RL / MUA-RL / Verlog 五篇代表论文，
> 讲清每个框架**解决了什么具体痛点、用了什么机制**。

## 1. 为什么"多轮"不是"多 token"

```text
单步 RL：生成一段文本 → 一个奖励（T=1）
多轮 Agent RL：思考→调工具→看结果→再思考→…（T>1, POMDP）

本质差异（回顾 01）：
  状态在变（s_{t+1} ~ P(·|s_t,a_t)）
  动作含工具调用（𝒜_text ∪ 𝒜_action）
  奖励分步骤（稀疏终奖 + 过程子奖）
  → 信用分配、部分可观测、环境非平稳三大难题全部被激活
```

---

## 2. 五篇代表论文逐篇拆解

### 2.1 AgentRL: Scaling Agentic RL with Multi-Turn (arXiv:2510.04206)

**解决什么痛点**：训练吞吐与稳定性——传统"同步等待整条轨迹"导致 GPU 大量空转。

```text
核心贡献：全异步（fully asynchronous）生成-训练架构
  推理池（Rollout Workers）：持续生成轨迹，不等训练
  训练池（Train Workers）：   持续消费轨迹，更新模型
  两者解耦，通过队列/缓冲区连接，互不阻塞

关键设计：
  - 推理和训练完全异步，GPU 利用率拉满
  - 支持多任务、多轮 RL 训练混合
  - 在开源模型上训练后，报告超越 GPT-5 / Claude-Sonnet-4 的结果

为什么重要：它证明"异步解耦"是 Agent RL 从玩具到工业的关键工程范式
            （和 Slime 的"Agent 与 RL 解耦"思想一致，见 04）。
```

### 2.2 RAGEN + StarPO (arXiv:2504.20073)

**解决什么痛点**：多轮轨迹如何统一表示、如何做"轨迹级"优化。

```text
StarPO（Star Policy Optimization）：轨迹级 Agent RL 框架
  把每一步统一为四元组：
    State  (s_t)：当前环境状态（部分观测）
    Thinking(τ_t)：模型推理（CoT / 内部思考）
    Action (a_t)：执行的动作（文本 or 工具调用）
    Reward (r_t)：环境返回的奖励

训练对象：整条轨迹 τ = {(s_t, τ_t, a_t, r_t)}，而非单 token
  → 优势在轨迹层面计算，天然适配多轮

为什么重要：给出了"多轮 Agent 轨迹"的标准数据结构和优化目标，
           后面很多框架（含 Slime）都受其轨迹级思想影响。
```

### 2.3 AgentGym-RL (arXiv:2509.08750)

**解决什么痛点**：长程决策（long-horizon）下，跨多种环境的统一训练。

```text
核心贡献：长程决策 Agent RL 框架
  - 轨迹级训练，支持 Web / OS / 数据库等多环境
  - 异步环境交互
  - 统一的轨迹格式（和 StarPO 类似，但更强调"跨环境"）

为什么重要：把"环境多样性"当成一等公民，
           对应 Survey §5.1 的环境分类（Web/GUI/Coding/...）。
```

### 2.4 MUA-RL (arXiv:2508.18669)

**解决什么痛点**：多轮**用户交互**场景（不是纯工具，而是和用户来回对话）。

```text
核心贡献：Multi-turn User-interaction Agent RL
  - 用户的反馈本身成为环境动态的一部分
  - 处理"对话轮次 + 用户意图漂移"带来的非平稳性

为什么重要：填补了"和用户协作"而非"操作环境"的 Agent RL 空白，
           对应 Survey §4.7 Multi-Agent / 用户协作方向。
```

### 2.5 Verlog (CMU blog)：变长 episode RL

**解决什么痛点**：不同任务 episode 长度差异巨大（有的 3 步，有的 300 步），
等长 batch 会造成短任务被长任务"淹没"或 GPU 浪费。

```text
核心贡献：专门处理变长 episode
  - 动态 batch：按 episode 长度分组
  - 避免短 episode 等长 episode 导致的效率/梯度问题

为什么重要：工程细节决定能不能 scale，对应 Survey §6.3 环境扩展挑战。
```

---

## 3. 跨论文的共同主题（对照 Survey 三大难题）

```text
难题               代表解法
─────────────────────────────────────────────
异步/吞吐          AgentRL（全异步）、AgentGym-RL（异步交互）
轨迹表示           RAGEN/StarPO（四元组轨迹级）、AgentGym（统一格式）
变长/非平稳        Verlog（动态 batch）、MUA-RL（用户漂移）
信用分配（§3.7）   见 05：EPO/ThinkRM/AgentPRM/GiGPO/SpaRL
```

---

## 4. 多轮训练的工程痛点（必须理解）

### 4.1 Re-tokenize 问题（最常被忽略的坑）

```text
训练时：一次性生成整条轨迹 → 统一 tokenize → 算 loss
推理时：一轮一轮生成，每轮独立前向

若两者 tokenization 不一致（比如工具返回被重新分词），
训练学到的策略在推理时不 work。
→ Slime 用 RadixTree 保证多轮 logits 准确（见 04）。
```

### 4.2 上下文爆炸

```text
多轮历史撑爆上下文窗口。
解法：滚动窗口、摘要压缩（连到 Survey §3.3 Memory）、关键步保留。
```

### 4.3 环境失败 ≠ 模型失败

```text
沙箱崩了、网页超时 ≠ Agent 做错。
必须隔离：环境错误重试不计分，模型错误才记失败轨迹（见 06）。
```

---

## 5. 多轮 RL 的训练技巧（可操作）

```text
技巧 1｜课程学习：1轮→3轮→5轮→更长，避免一上来过难
技巧 2｜中间奖励：工具成功 +0.1、编译过 +0.3、测试过 +1.0、完成 +2.0
         （需 Process Reward / 规则，见 05）
技巧 3｜轨迹过滤：太短(可能失败)/太长(可能循环)/无工具调用/奖励=0 → 丢弃
技巧 4｜优势塑形：ASPO 等把优势在 turn 级重分配，缓解长 horizon 信用分配
```

---

## 6. 和你项目的关联（UE5 测试 Agent）

```text
你的测试 Agent 天然多轮：
  读 JSON 用例 → 执行步骤 → 观察结果 → 判通过/失败 → 下一条

若引入 Agent RL：
  1. 奖励：通过 +1、性能不退化 +0.5、步骤少 +0.2、崩溃 -2
  2. 框架：用 Slime（Agent 解耦）或 veRL+uni-agent 跑多轮
  3. 算法：GRPO（组内相对，省 Critic）
  4. 痛点：Re-tokenize（步骤返回要稳定分词）、环境失败隔离（游戏崩了别算模型错）
```

---

## 7. 下一步

进入 `04_rl_frameworks.md`，看 OpenRLHF / veRL / Slime 怎么把上面
这些论文思想工程化；以及 Survey §5.2 的框架分类法。

## 8. 一句话总结

> 多轮 Agent RL 的难点是"生成变交互"激活的三大难题。AgentRL 用全异步解吞吐，
> StarPO 用四元组轨迹级统一表示，AgentGym-RL 攻跨环境长程，MUA-RL 攻用户交互，
> Verlog 攻变长 batch——它们共同把 Survey 的 POMDP 形式化落到了可训练系统。
