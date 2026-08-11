# Agent RL 参考资料索引

> 按「总纲综述 → 算法 → 多轮框架 → 奖励 → 环境 → 专题博客」组织，便于追踪最新工作。

## 一、核心总纲（必读）

- **The Landscape of Agentic Reinforcement Learning for LLMs: A Survey**
  Zhang, Geng, et al. (25 位作者, 牛津/上海AI实验室/NUS 等). arXiv:2509.02547 (v5, 2026-04), 已发表于 TMLR.
  综合 500+ 篇近期工作，提出 MDP/POMDP 形式化 + "能力×任务"双重分类法。
  - 论文：https://arxiv.org/abs/2509.02547
  - PDF：https://arxiv.org/pdf/2509.02547
  - 解读（中文）：https://zhuanlan.zhihu.com/p/1949946009036756270
  - 概览：https://www.alphaxiv.org/overview/2509.02547

## 二、强化学习算法

- PPO (Schulman et al., 2017): https://arxiv.org/abs/1707.06347
- DPO (Rafailov et al., 2023): https://arxiv.org/abs/2305.18290
- GRPO / DeepSeekMath (Shao et al., 2024): https://arxiv.org/abs/2402.03300
- DAPO (Dynamic Sampling + Clip-Higher): https://arxiv.org/abs/2503.14476
- Dr.GRPO: https://arxiv.org/abs/2503.20783
- GSPO (Group Sequence Policy Optimization): https://arxiv.org/abs/2507.18071
- R1 类推理模型: DeepSeek-R1 https://arxiv.org/abs/2501.12948

## 三、多轮 Agent RL 框架论文

- AgentRL (全异步多轮 RL): https://arxiv.org/abs/2510.04206
- RAGEN + StarPO (轨迹级 Agent RL): https://arxiv.org/abs/2504.20073
- AgentGym-RL (长程跨环境): https://arxiv.org/abs/2509.08750
- MUA-RL (多轮用户交互): https://arxiv.org/abs/2508.18669
- Verlog (变长 episode RL, CMU blog): https://blog.castellanjiang.com/posts/2025-09-25-verlog

## 四、奖励设计 / 过程奖励

- AgentPRM (MC 采样估步价值): https://arxiv.org/abs/2502.10325
- InversePRM: https://arxiv.org/abs/2504.15864 (示例)
- RLVR 相关: DeepSeek-R1 等
- ASPO / GiGPO / SpaRL (长 horizon TIR 优势): 见 Survey §3.2, §3.7

## 五、环境与基准

- SWE-bench (修 Bug): https://www.swebench.com
- WebArena: https://webarena.dev
- AgentBench: https://arxiv.org/abs/2308.03688
- GAIA: https://arxiv.org/abs/2311.12983
- OSWorld: https://os-world.github.io
- AgentGym: https://arxiv.org/abs/2406.04151

## 六、开源训练框架

- OpenRLHF: https://github.com/OpenRLHF/OpenRLHF
- veRL (HybridFlow): https://github.com/volcengine/verl
- Slime (GLM 系列 Agent RL 引擎): https://github.com/THUDM/slime
- TRL (HuggingFace): https://github.com/huggingface/trl

## 七、延伸阅读（站内）

- 训练框架/ → 看 RL 工程细节
- Agent系统设计/ → ReAct / Tool Calling 基础
- Part5_reinforcement_learning/ → MDP/PPO 理论
- Part6_building_llm/ → RLHF/DPO 后训练

## 八、跟进前沿的建议

```text
1. 定期刷 arxiv 最新: https://arxiv.org/list/cs.AI/recent
2. 关注 Survey §6 的 6 大开放挑战对应的新工作
3. 用 Survey "能力×任务"分类法给新论文贴标签，扩充 07 清单
```
