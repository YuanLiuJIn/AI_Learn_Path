# 06. 环境与评测（对照 Survey §5.1 分类）

> 目标：理解 Agent RL 的"环境"为何比单步 RL 复杂，并用 Landscape Survey §5.1 的
> **环境分类法**（Web / GUI / Coding / Domain-specific / Simulated-Game / General-Purpose）
> 组织主流基准。读完应能为自己的任务挑/建环境。

## 0. 为什么环境是 Agent RL 的第一性

```text
Agentic RL = 策略 × 环境反馈（POMDP 里的 P(s_{t+1}|s_t,a_t) 和 R）
没有环境，就没有奖励，就没有学习。
环境决定了：模型能学到什么、奖励从哪来、训练成本、评测真实性。
```

---

## 1. Survey §5.1 的六大环境分类

### 1.1 Web Environments

```text
代表：WebArena（Amazon/Wiki/GitLab/Reddit 等真实网站交互）
任务：搜索、填表、购物、信息综合
挑战：网站会变、网络延迟、反爬
对应能力：Survey §4.1 Search & Research、§4.4 GUI/Web
```

### 1.2 GUI Environments

```text
代表：OSWorld、AndroidEnv、WebVoyager
任务：操作系统点击/输入、移动端操作
挑战：动作空间大、状态难观测、动作粒度选择
对应：Survey §4.4 GUI Agent
```

### 1.3 Coding & SWE Environments

```text
代表：SWE-bench（给 GitHub Issue 修 Bug）
子分类（Survey）：交互式 SWE、基准数据集、程序化世界模型
奖励：测试通过率（天然 RLVR 可验证）
对应：Survey §4.2 Code Agent —— 当前 Agent RL 最热、最易出成果的方向
```

### 1.4 Domain-specific Environments

```text
Science / MLE / Biomedical / Cybersecurity
特点：专业工具链、领域验证器（如形式证明、蛋白质折叠评分）
对应：Survey §4.3 Math（形式证明）、§4.5 Vision、其它垂直任务
```

### 1.5 Simulated & Game Environments

```text
代表：TextGame、Minecraft（VOYAGER 的试验场）、棋盘/策略游戏
特点：可控、可重置、奖励清晰
价值：作为算法验证的"沙盒苗圃"，先在这里调通再上真实环境
```

### 1.6 General-Purpose Environments

```text
代表：AgentBench（8 种环境多维评测）、AgentGym
特点：统一接口、多环境混合训练
价值：对应 03 里 AgentGym-RL 的"跨环境长程"训练需求
```

---

## 2. 环境的核心工程需求

```text
1. 高并发：一次训练同时跑数百环境实例，互不影响
2. 高可靠：环境不能频繁崩；崩了不影响训练
3. 可重置：episode 结束快速重置，保证初始条件一致
4. 沙箱隔离：代码执行/文件操作隔离，不碰真实系统
```

---

## 3. 主流评测基准（带数据）

| 基准 | 环境分类 | 任务 | 指标 | 现状 |
|---|---|---|---|---|
| SWE-bench | Coding | 修 GitHub Issue | Resolved Rate | SOTA ~50%+ |
| WebArena | Web | 真实网站交互 | 任务成功率 | 多站点 |
| AgentBench | General | 8 环境多维 | 分环境评测 | 综合榜 |
| GAIA | General | 多步推理+工具 | 准确率 | 人易 AI 难 |
| OSWorld | GUI/OS | 操作系统任务 | 成功率 | GUI 主流 |
| Spider/BIRD | Domain(DB) | NL→SQL | 查询正确 | 数据库 Agent |

---

## 4. 环境失败 ≠ 模型失败（工程铁律）

```text
必须区分：
  环境崩溃（沙箱挂了）→ 重试，不计入模型表现
  模型错误（调错工具）→ 模型责任，记失败轨迹
  超时 → 判断是模型慢还是环境慢

否则：训练信号被污染，模型学到"环境噪声"而非"任务逻辑"。
（对应 Survey §6.5 真实部署架构、03 的 Re-tokenize/隔离讨论）
```

---

## 5. 沙箱管理常用方案

```text
Docker 容器 / Kubernetes 编排 / 自定义沙箱服务
关键参数：并发数、独立文件系统、命令隔离、超时控制、资源限额
```

---

## 6. 给你的实操建议（自建环境）

```text
Step 1：选最接近你任务的 Survey 环境类（如你的 UE5 测试 ≈ Simulated + Coding 混合）
Step 2：定义 Action Space（哪些操作可调用：点击/截图/读 JSON/断言）
Step 3：定义 Reward（见 05：Outcome + Process + Rule）
Step 4：用 Docker 起高并发沙箱，分离"环境失败"与"模型失败"
Step 5：先在小 simulated 环境调通算法，再上真实环境
```

---

## 7. 一句话总结

> 环境是 Agent RL 的"世界"。Survey §5.1 把环境分为 Web/GUI/Coding/Domain/Simulated/General
> 六类，每一类有独特奖励与挑战。SWE-bench 因"测试可验证"成为最热试验场；而能否
> 高并发、可重置、隔离失败，决定了训练能不能 scale——这正是 Survey §6.3「环境扩展」挑战。
