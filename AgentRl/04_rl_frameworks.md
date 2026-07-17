# 04. Agent RL 开源框架

> 目标：理解三大主流开源 RL 框架的架构设计、核心特点和适用场景。

## 1. RL Infra 的标准范式

由 OpenRLHF 确立的行业标准架构：

```text
┌─────────────────────────────────────────┐
│              Ray（调度层）               │
├─────────────────────────────────────────┤
│                                          │
│  推理引擎               训练引擎          │
│  ├─ vLLM                ├─ DeepSpeed     │
│  └─ SGLang              ├─ FSDP          │
│                          └─ Megatron      │
│                                          │
│  Actor 模型 ←→ Critic 模型 ←→ Reward 模型 │
│                                          │
└─────────────────────────────────────────┘

核心设计：
  推理引擎负责生成（Rollout）
  训练引擎负责更新参数
  Ray 负责分布式调度
```

## 2. OpenRLHF

### 定位

首个基于 Ray + vLLM 的高性能 RLHF 框架，工业级生产可用。

### 核心特点

```text
1. Ray 分布式调度
   自动将 Actor、Critic、Reward 模型分布到不同 GPU

2. vLLM 推理加速
   利用 PagedAttention 提升推理吞吐

3. 支持多种算法
   PPO、DPO、Rejection Sampling、GRPO

4. 支持多种模型
   LLaMA、Qwen、DeepSeek、Mixtral 等

5. 统一 Agent 设计范式
   最新版将 RLHF 组件统一为 Agent 架构
```

### 适用场景

```text
中小规模 RL 训练（7B-70B）
快速实验和原型验证
学术研究和教学
```

### 学习建议

```text
入门首选：文档完善，社区活跃
先跑通 PPO 训练 → 理解 RLHF 流程
再尝试 GRPO → 理解最新算法
```

## 3. veRL（Volcano Engine RL）

### 定位

由字节跳动开源的灵活、高效的大规模 RL 训练框架。

### 核心特点

```text
1. HybridFlow 混合控制器
   推理和训练可以独立扩缩容
   推理用 vLLM/SGLang，训练用 Megatron/FSDP

2. 大规模验证
   已验证 70B+ 模型训练
   支持千卡级别分布式

3. uni-agent 集成
   最新版内置统一 Agent 框架
   支持构建、运行、训练 LLM Agent

4. 多模态支持（VeRL-Omni）
   扩展到 Diffusion 和多模态模型
```

### 适用场景

```text
大规模 RL 训练（70B+）
需要推理和训练独立扩缩容
多模态 RL 探索
```

## 4. Slime

### 定位

专为 Agent 时代设计的 RL 训练框架，GLM 全系列背后的 RL 引擎。

### 核心特点

```text
1. 解耦 Agent 与 RL 框架
   Agent 框架负责环境交互和轨迹生成
   RL 框架负责策略优化
   两者通过标准化接口通信

2. RadixTree 技术
   确保多轮对话中 logits 的准确性
   解决 Re-tokenize 导致的不一致

3. Megatron 原生集成
   直接透传 Megatron 参数
   不做中间转换，保证训练效率

4. 大规模验证
   训练了 GLM-4.5 到 GLM-5.2 全系列
   百亿参数级别的 Scaling 验证

5. 开源共建
   社区驱动的开发模式
   在特性上保持领先
```

### 核心创新

```text
为什么 Slime 要解耦 Agent 和 RL 框架？

传统 RL 框架（如 veRL、OpenRLHF）：
  将 Agent 逻辑和 RL 逻辑耦合在一起
  优点是简单，缺点是灵活性差

Slime 的设计：
  Agent 框架独立负责：
    环境交互（调用工具、读取文件）
    轨迹生成（记录每一步的状态、动作、奖励）
    Rollout 管理（批量生成、异步执行）

  RL 框架独立负责：
    策略优化（PPO、GRPO 等）
    参数更新（Megatron 分布式训练）
    模型管理（checkpoint、rollback）

好处：
  可以独立升级 Agent 或 RL 模块
  支持更复杂的环境（代码、浏览器、操作系统）
  训练和推理可以独立优化
```

### 适用场景

```text
多轮 Agent RL 训练（修 Bug、浏览网页、操作软件）
需要解耦 Agent 和 RL 框架
使用 Megatron 做分布式训练
```

## 5. 框架对比

| | OpenRLHF | veRL | Slime |
|---|---|---|---|
| 定位 | 通用 RLHF | 大规模 RL | Agent RL |
| 调度 | Ray | HybridFlow | Ray + 自研 |
| 推理引擎 | vLLM | vLLM/SGLang | vLLM/SGLang |
| 训练引擎 | DeepSpeed/FSDP | Megatron/FSDP | Megatron |
| 多轮支持 | 基础 | 较好 | 专门优化 |
| Agent 解耦 | ❌ | 部分 | ✅ |
| 验证规模 | 中小 | 大 | 百亿级 |
| 社区活跃度 | 高 | 高 | 中 |
| 学习难度 | 低 | 中 | 高 |

## 6. 选型建议

```text
入门学习 → OpenRLHF
  文档完善，社区活跃，快速上手

大规模训练（70B+） → veRL
  推理训练独立扩缩容，工业验证

多轮 Agent RL → Slime
  专门为 Agent 设计，GLM 系列验证

快速实验 → OpenRLHF + GRPO
  不需要 Reward Model，最简单
```

## 7. 实践路线

```text
1. 用 OpenRLHF 跑通一个 PPO 训练
   理解 RLHF 的完整流程
   观察 loss 曲线、reward 变化

2. 切换到 GRPO
   理解去掉 Critic 的好处
   对比训练稳定性

3. 尝试多轮任务
   用 veRL 或 Slime
   理解多轮 RL 的特殊挑战

4. 自定义环境
   设计自己的 Agent 任务
   定义奖励函数
   跑通训练
```

## 8. 一句话总结

> OpenRLHF 适合入门，veRL 适合大规模，Slime 适合 Agent RL。选择框架的关键不是"哪个最强"，而是"你的任务需要什么"——单轮还是多轮、规模多大、是否需要 Agent 环境解耦。
