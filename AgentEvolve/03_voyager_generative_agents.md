# 03. 经典项目：Voyager + Generative Agents

> 这两个项目是 Agent 自进化的奠基之作，分别展示了"技能驱动自进化"和"记忆驱动自进化"。

---

## 1. Voyager：Minecraft 里的终身学习 Agent

### 基本信息

| 项目 | 详情 |
|---|---|
| 论文 | "Voyager: An Open-Ended Embodied Agent with Large Language Models" |
| 年份 | 2023 |
| 机构 | NVIDIA |
| GitHub | github.com/MineDojo/Voyager |
| Stars | ~10K |

### 做什么？

```text
Agent 在 Minecraft 里自主探索，不需要人教：
  1. 自己写 JavaScript 代码控制角色
  2. 执行成功 → 代码存入技能库
  3. 执行失败 → 反思错误 → 改进代码
  4. 自动生成更难的目标 → 持续进阶
```

### 三大核心组件

```text
① 自动课程（Automatic Curriculum）
   根据当前能力，自动生成下一个学习目标
   
   例：
   "你已经会砍树了 → 试试做木镐"
   "你已经会做木镐了 → 试试采集石头"
   "你已经会采集石头了 → 试试做石镐"
   
   难度呈阶梯式递增，确保 Agent 始终在"最近发展区"

② 技能库（Skill Library）
   每个成功的代码片段都存入技能库
   技能 = {描述, 代码, 使用条件}
   
   例：
   skill_cut_tree = {
     "description": "砍下一棵树",
     "code": "async function cutTree(bot) { ... }",
     "precondition": "附近有树 + 手上有斧头"
   }
   
   遇到同类任务 → 直接查技能库调用 → 不需要从头写代码

③ 迭代提示（Iterative Prompting）
   代码执行失败时，不是放弃，而是反思改进：
   
   第 1 次尝试：代码报错 "block not found"
    → Agent 反思："可能是坐标没对准，调整 Y 轴"
    → 生成改进版代码
   第 2 次尝试：执行成功！
    → 代码 + 改进经验 存入技能库
```

### 自进化的体现

```text
传统 Agent：
  在 Minecraft 里 = 每次重开游戏都从头学
  "我不知道怎么砍树" → 每次都一样

Voyager：
  第一次：尝试砍树，经过 3 次失败才成功
         记录下"砍树技能"
  第二次：遇到树，直接调用已学技能
  第三次：把"砍树+做木板+做工作台"组成更高级技能
  ...
  第 N 次：已掌握数百个技能，可以独立建造复杂建筑
  
  真正做到了在开放世界里终身学习、持续进化
```

---

## 2. Generative Agents：AI 小镇的"居民"

### 基本信息

| 项目 | 详情 |
|---|---|
| 论文 | "Generative Agents: Interactive Simulacra of Human Behavior" |
| 年份 | 2023 |
| 机构 | Stanford |
| 通俗理解 | 25 个 AI Agent 生活在一个虚拟小镇，有记忆、会反思、自发社交 |

### 三层记忆架构

```text
① 记忆流（Memory Stream）
   记录 Agent 经历的一切：
   "早上 8 点，我吃了早餐"
   "早上 9 点，我和 A 聊了 B 话题"
   "中午 12 点，我在公园散步时发现..."

② 反思（Reflection）
   定期从记忆流中提取高层次洞察：
   记忆流中有多条"和 A 聊 B 话题"
   → 反思："我对 B 话题很感兴趣，A 是讨论这个的好伙伴"
   → 这个反思也被存入记忆流

③ 规划（Planning）
   基于反思生成每日计划：
   "我今天想去公园、想和 A 聊 B 话题、想完成手头的工作"
```

### 自进化的体现

```text
传统记忆：
  只是存储原始对话记录
  "上次和 A 说了什么" → 知道事实，但不理解含义

Generative Agents 的自进化记忆：
  记忆流 → 定期反思 → 提炼洞察 → 反思也存入记忆 → 影响后续行为
  "通过和 A 的多次对话，我理解了 B 话题，知道了 A 的偏好"
  → 这就是从"记忆"到"理解"的进化
```

---

## 3. Voyager vs Generative Agents：两种进化路线

| | Voyager | Generative Agents |
|---|---|---|
| **进化什么** | 技能（可复用代码） | 记忆（高层次理解） |
| **怎么进化** | 试错 → 改进代码 → 存入技能库 | 记忆流 → 反思 → 提炼洞察 |
| **使用场景** | 动手操作、工具调用 | 社交、长期理解 |
| **核心价值** | 做事的经验积累 | 理解的经验积累 |
| **给现代 Agent 的启发** | SkillRL 的技能自动发现 | AgentEvolver 的经验复用 |

---

## 4. 一句话总结

```text
Voyager = Agent 学会"怎么做"（技能驱动进化）
Generative Agents = Agent 学会"怎么理解"（记忆驱动进化）

两者共同奠定了自进化 Agent 的两条核心技术路线。
```
