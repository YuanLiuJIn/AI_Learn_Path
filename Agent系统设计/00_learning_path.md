# 00. Agent 系统设计学习路线

> 目标：系统理解生产级 AI Agent 的设计方法论。

## 1. 推荐阅读顺序

```text
1. 先理解核心公式
   → 01_agent_core_formula.md
   搞清楚 Agent 为什么不是"模型 + 工具"，而是"上下文 × 工具 × 循环"

2. 深入每个要素
   → 02_context_engineering.md
     五层分区、压缩、Memory、稳定前缀

   → 03_tools_design.md
     渐进式发现、增强描述、智能反馈、结果裁剪

   → 04_loop_control.md
     步进执行、三层防护、状态追踪、智能终止

3. 理解系统级权衡
   → 05_system_tradeoffs.md
     不可能三角、场景配置、指标体系

4. 实战落地
   → 06_apply_to_ue5_test_agent.md
     把设计模式应用到 UE5 测试 Agent
```

## 2. 前置知识

建议先掌握：

```text
什么是 AI Agent（思考 → 行动 → 观察 循环）
Agent 和 ChatBot 的区别
工具调用（Function Calling）的基本概念
System Prompt / 上下文窗口的基本概念
```

如果还没学过，建议先看 `AI_Learn_Path/Agent/` 中的基础内容。

## 3. 学习原则

```text
1. 先理解"为什么这样设计"，再学"具体怎么做"
   每个设计决策背后都有取舍

2. 带着自己的项目去读
   每学一个设计模式，想一下"我的 UE5 测试 Agent 能用上吗？"

3. 先学原理，再写代码
   不是"API 怎么调用"，而是"系统怎么组织"

4. 关注"权衡"而非"最优"
   Agent 设计没有银弹，只有场景化取舍
```
