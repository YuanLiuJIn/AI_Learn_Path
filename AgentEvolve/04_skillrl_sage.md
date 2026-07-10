# 04. 前沿突破：SkillRL + SAGE

> 2025-2026 年最前沿的 Agent 自进化方案：用 RL 自动发现技能并组合使用。

---

## 1. SkillRL：从经验中自动发现技能

### 基本信息

| 项目 | 详情 |
|---|---|
| 论文 | "SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning" |
| 年份 | 2026.2 |
| GitHub | github.com/aiming-lab/SkillRL |

### 核心问题

```text
传统 Agent 记忆的问题：
  记录了大量原始操作序列
  但这些都是"流水账"：
    "点击这里 → 输入那里 → 滚动 → 点击那里 → 等待 → 提交"
  
  问题：
    冗长、重复、噪音多
    下次遇到类似任务，还是要从头推理
    不能直接复用"段落"级别的操作经验
```

### SkillRL 的解法

```text
Action Level（单步操作） → Skill Level（技能段落） → Meta Skill Level（元技能）

类比：
  单步操作 = 单词
  技能 = 词组/短语
  元技能 = 句子模板
  
  "click search box"               ← 单词
  "search + analyze results"       ← 短语（技能）
  "data retrieval workflow"        ← 句子（元技能）
```

### 自动技能发现流程

```text
Step 1：收集经验
  Agent 完成大量任务，记录所有操作序列

Step 2：模式识别
  从操作序列中自动发现重复出现的子序列：
    "点击搜索框→输入关键词→点击查询→等待结果→分析总结"
    这个模式出现了几十次 → 提取为技能 "information_search"

Step 3：技能抽象
  把具体参数替换为占位符：
    skill_info_search(query, click_target) = {
      step1: click(search_box)
      step2: type(query)
      step3: click(search_button)
      step4: wait
      step5: analyze(results)
    }

Step 4：递归进化
  低级技能可以组合成高级技能：
    skill_competitor_analysis = 
      skill_info_search("competitor X") + 
      skill_info_search("competitor Y") + 
      skill_compare()
```

### 与 Voyager 技能库的区别

```text
Voyager：技能 = 手工存的代码片段
        需要 Agent 成功执行并自己保存

SkillRL：技能 = RL 自动发现的模式
        不需要 Agent 自己保存
        从大数据中统计出现的高频、有效模式
        自动发现 Agent 自己都没意识到的"习惯性操作模式"
```

---

## 2. SAGE：技能增强 GRPO

### 基本信息

| 项目 | 详情 |
|---|---|
| 论文 | "Skill Augmented GRPO for self-Evolution" |
| 年份 | 2025.12 |

### 核心创新

```text
传统 GRPO：
  对同一任务，生成 N 个"单步操作序列"
  比较：哪个序列更好？

SAGE：
  对同一任务，生成 N 个"技能组合方案"
  比较：哪个技能组合更好？

区别：
  传统 GRPO 的"动作" = 单击、输入、滚动  （微观）
  SAGE 的"动作"   = 搜索技能、分析技能、撰写技能（宏观）
```

### 效果

```text
传统 GRPO（单步动作）：
  Agent 学会了"点搜索框再输入关键字比乱点好"
  但不知道"什么时候该切换到分析阶段"

SAGE（技能组合）：
  Agent 学会了"遇到复杂查询，先用搜索技能，再用分析技能，最后用写报告技能"
  学会了高层次的策略规划
```

---

## 3. 一句话总结

```text
SkillRL = 从海量经验中自动发现"可复用的操作段落"（技能）
SAGE    = 用 GRPO 训练 Agent 学会"如何组合技能"（高级策略）
两者叠加 = Agent 从"背单词"升级为"学会写作"
```
