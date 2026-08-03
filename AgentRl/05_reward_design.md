# 05. 奖励设计：Agent RL 的指挥棒（含过程奖励方法族）

> 目标：理解奖励信号**从哪来、怎么分密度、怎么防黑客**，并掌握
> RLVR / Outcome / Process / EPO / ThinkRM / AgentPRM / ASPO 等方法族。
> 对应 Landscape Survey §2.5、§3.7 与能力视角下的奖励相关方法。

## 1. 奖励 = 训练方向的唯一指挥棒

```text
奖励错了   → 模型学错行为（Reward Hacking）
奖励太稀疏 → 模型不知哪步对（信用分配崩溃）
奖励太好骗 → 模型钻空子（重复输出正确词刷分）
```

---

## 2. 奖励来源的三条主线

### 2.1 RLVR（可验证奖励，Verifiable Rewards）

```text
来源：任务本身有客观判定
  数学题 → 答案对不对
  代码   → 测试过没过
  游戏   → 通没通关

特点：零标注、无 Reward Model、无法被欺骗
局限：只覆盖"有确定答案"的任务（Survey §3.2/§3.3 大量 TIR/Code 工作依赖它）
代表：DeepSeek-R1（GRPO + RLVR）
```

### 2.2 Outcome Reward（结果奖励）

```text
只看最终结果：任务完成?/测试通过?/答案正确?
优点：简单、客观、不易黑客
缺点：稀疏，中间步骤无信号 → 长 horizon 训练困难
```

### 2.3 Process Reward（过程奖励）

```text
每一步给奖励，引导走正确过程：
  工具调用成功 +0.1、编译过 +0.3、测试过 +0.5、完成 +1.0
优点：密集信号，训练更易
缺点：需设计规则或训练 PRM（引入新模型、新偏差）
```

---

## 3. Process Reward Model（PRM）方法族

这部分是 Survey §3.7「长 horizon 时序信用分配」的核心武器。

### 3.1 AgentPRM (arXiv:2502.10325)

```text
思想：用 Monte Carlo 采样评估每个 step 价值
  1. 从某 step 起随机采样多条后续路径
  2. 统计最终成功概率 → 成功率高说明这步好
  3. 训练 PRM 预测每步价值，给每步提供信号
```

### 3.2 InversePRM

```text
思想：直接从成功轨迹学 PRM，免 MC 采样
假设：成功轨迹每步都"好"，失败轨迹某些步"坏"
训练：成功轨迹每步高分，失败轨迹每步低分
```

### 3.3 EPO / ThinkRM / SPO / RLVMR（Survey §3.7）

```text
EPO        —— 过程监督 + 结果奖励混合
ThinkRM    —— 对"思考/推理"步骤单独建模奖励
SPO        —— 步级策略优化（把优势细化到单步）
RLVMR      —— 强化学习的 verifiable multi-step reward
SDPO       —— 段级 DPO，把偏好优化扩展到多步（连 02 的 Step-DPO）
```

### 3.4 ASPO（优势塑形策略优化，Survey §3.2）

```text
思想：在工具集成 RL（TIR）长 horizon 下，理论证明如何做 turn-level 优势塑形
意义：直接针对"哪个工具调用对最终成功贡献多大"的信用分配问题
```

### 3.5 GiGPO / SpaRL（Survey §3.2 长 horizon TIR）

```text
初步尝试 turn-level 优势，缓解长轨迹的信用分配。
（这是当前最热、最未解决的开放方向之一）
```

---

## 4. Rule-based Reward（规则奖励）

```text
用规则自动判定，无需 RM：
  格式正确（JSON/代码规范）、长度合理、用了正确工具
优点：零成本、可大规模
缺点：只覆盖有明确定则的任务
典型：GRPO 的"答案匹配规则"、ReTool 的"工具调用格式规则"
```

---

## 5. 奖励设计四原则（可操作清单）

```text
原则 1｜可验证：用客观事实（测试过/答案对），避免主观（"看起来好"）
原则 2｜密度合适：终奖(高权) + 过程奖(低权)，太密模型会钻小奖
原则 3｜防黑客：多维奖励 + KL 惩罚 + 人类抽检 + 规则约束
原则 4｜可扩展：能自动产生海量数据（数学自动判、代码自动测）
```

---

## 6. 长 horizon 信用分配（本文件的"皇冠难题"）

```text
问题：最终奖只有终点一个，但成功依赖第 3、7、12 步的正确动作
      → 怎么把终奖"分配"回这些步骤？

解法谱系（由粗到细）：
  整轨迹级：StarPO（轨迹级优势，见 03）
  turn 级：  GiGPO / SpaRL / ASPO
  step 级：  EPO / SDPO / Step-GRPO / Step-DPO
  MC 估计：  AgentPRM（从成功路径反推步价值）
```

---

## 7. 和你项目关联（UE5 测试 Agent）

```text
Outcome：全过 +10、部分 +3、全失败 -5、崩溃 -10
Process：每步成功 +0.1、性能正常 +0.2、断言过 +0.3、发现 Bug +2
Rule：   步骤数合理 +0.5、用对 Action +0.2、JSON 对 +0.1

建议：先用 Rule + Outcome 跑通（零 RM 成本），
      再上 AgentPRM 类过程奖励提升长轨迹表现。
```

---

## 8. 下一步

进入 `06_environment_and_benchmark.md`，看奖励从**哪些环境**来、
以及 Survey §5.1 的环境分类法。

## 9. 一句话总结

> 奖励设计决定 Agent 能学到什么。RLVR 是当前最可靠燃料；Outcome 简单但稀疏；
> Process（EPO/ThinkRM/AgentPRM）解决稀疏但需 RM；ASPO/GiGPO 攻长 horizon 信用分配。
> 这整条谱系，正是 Survey §3.7 标为"长交互中心挑战"的内容。
