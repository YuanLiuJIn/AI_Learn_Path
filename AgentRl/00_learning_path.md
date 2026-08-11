# 00. Agent RL 学习路线（论文驱动版）

> 目标：从"读得懂论文"到"训得动 Agent"。本路线强调：**先建立统一的框架概念，再读代表论文，最后动手**。

## 1. 推荐学习顺序

```text
阶段 0｜建立统一语言（最重要，别跳过）
  → 01_agent_rl_overview.md（MDP vs POMDP 形式化）
  → 01b_Landscape_Survey_详解.md（总纲综述逐章讲解）
  目的：搞懂"Agentic RL 到底在解决什么"，以及 Survey 的
        "能力 × 任务"双重分类法，后面所有论文都挂在这张地图上

阶段 1｜夯实 RL 算法
  → 02_rl_foundations.md
  要求：能手写出 PPO / DPO / GRPO 的目标函数区别
        知道 DAPO/GSPO/Dr.GRPO 各自改了什么

阶段 2｜深入多轮训练
  → 03_multi_turn_agent_rl.md
  要求：说清 AgentRL / RAGEN / AgentGym-RL 解决的核心痛点
        理解 Re-tokenize、变长 episode、轨迹过滤

阶段 2.5｜长程任务专题（本次新增，🔥重点）
  长程 = 一条轨迹几十~几百步，核心是「跨多步信用分配 + 奖励稀疏 + 非平稳」。
  本阶段把长程相关的论文/方法从 03、05 里抽出来单独成线，配 docs/ 里的 PDF。

  读这 3 篇导读（已在仓库内）：
    → 03_multi_turn_agent_rl.md  §1-§2（长程为何难、五篇代表框架）
    → 05_reward_design.md        §3、§6（过程奖励方法族 + 信用分配谱系）
    → 01b_Landscape_Survey_详解.md §3.7（Survey 的"长 horizon"专章）

  配套 PDF（docs/papers/，均已下载）：
    🔥 AgentRL.pdf        —— 全异步架构，长程才 scalable
    🔥 RAGEN_StarPO.pdf   —— 轨迹级表示 + 轨迹级优势
    🔥 AgentGym-RL.pdf    —— 长程跨环境决策
    🔥 AgentPRM.pdf       —— MC 反推每步价值（信用分配核心）
    🔥 DAPO.pdf / Dr_GRPO.pdf / GSPO.pdf —— 长序列训练稳定性三件套

  按"信号粒度"从粗到细掌握解法谱系：
    轨迹级  StarPO（轨迹级优势）
    turn 级 ASPO / GiGPO / SpaRL（turn-level 优势重分配）
    step 级 EPO / SDPO / Step-GRPO / Step-DPO（优势细化到单步）
    MC 估计 AgentPRM（从成功路径反推步价值）

  工程侧补充手段（长程必备）：
    课程学习（1轮→3轮→5轮→更长）
    中间奖励（工具成功+0.1、编译过+0.3、测试过+1.0、完成+2.0）
    轨迹过滤（太短/太长/无工具调用/奖励=0 → 丢弃）
    上下文压缩（滚动窗口+摘要，防爆炸）
    环境失败隔离（沙箱崩≠模型错）

  达标要求：能画出"长程信用分配"的解法谱系图，
            并说清 StarPO / AgentPRM / ASPO 各自在哪一层、解决什么问题。

阶段 3｜跑通框架
  → 04_rl_frameworks.md → 选一个跑 demo
  → projects/search_r1_verl/（实战：4×H200 复刻 Search-R1，veRL+Qwen2.5-14B+GRPO，
    把 02/03/04/05 全链路跑通，并练 GPU 分布式这一 JD 缺口）

阶段 4｜奖励与环境
  → 05_reward_design.md → 06_environment_and_benchmark.md
  要求：能为一个真实任务设计 outcome + process 奖励

阶段 5｜读论文、跟前沿
  → 07_papers_projects.md（按分类选读）→ references.md（追新）
```

## 2. 前置知识自查

```text
❑ 强化学习基础：MDP、Policy、Value、Reward、Credit Assignment
   推荐：Part5_reinforcement_learning/ 或 Sutton & Barto 前 3 章

❑ 大模型后训练：SFT、RLHF、DPO 的基本流程
   推荐：Part6_building_llm/ 或 InstructGPT 论文

❑ Agent 基础：ReAct、Tool Calling、Agent Loop、MCP
   推荐：Agent系统设计/ 或 ReAct (Yao et al. 2022) 论文

❑ 一点工程常识：Ray / vLLM / 分布式训练的基本概念（读 04 时补充即可）
```

## 3. 怎么"读论文"才学得到东西（本专题的方法论）

不要只读摘要。按这个模板拆解每篇论文：

```text
读一篇 Agent RL 论文的 6 问：
1. 它把 Agent 建模成什么？单步 MDP 还是多步 POMDP？
2. 它的 Action Space 是什么？纯文本 / 工具调用 / GUI 操作？
3. Reward 从哪来？可验证规则 / Reward Model / 过程奖励？
4. 它用哪个算法？PPO / GRPO / DPO / 自研？
5. 它解决了哪个具体痛点？（稳定性？信用分配？环境？）
6. 在 Survey 的哪一类下？（能力视角？任务视角？）
```

## 4. 学习原则

```text
1. 先建框架，再塞细节
   Survey 的双重分类法就是你的"文件夹结构"，
   每读一篇论文就归到某个能力/任务下，知识才不会散。

2. 带着"对比"读书
   PPO vs GRPO、Outcome vs Process、单步 vs 多步、
   OpenRLHF vs veRL vs Slime ——对比让概念更锋利。

3. 读原文，不只读二手
   本专题给的讲解是"导读"，真正吸收要靠你点开 arxiv 链接读 §Method。

4. 先跑通小 demo，再钻理论
   用 OpenRLHF + GRPO 跑一个数学题 Agent，
   看到 reward 曲线涨起来，理论才有锚点。
```
