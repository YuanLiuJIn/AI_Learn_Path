# 03. 特定场景强化训练：从 SFT 到 GRPO

> 目标：掌握如何用强化学习（尤其是 GRPO）让 GUI Agent 适应你的特定业务场景。
> 核心：不想花大量人力标注数据？GRPO 用极少数据 + 规则奖励就能做到。
> 阅读时间：约 1.5 小时。

## 0. 为什么 GUI Agent 需要"训练"？

```
通用 GUI Agent（Zero-shot）：
  理解"点击提交按钮" ← 任何模型都能做
  但不知道"你公司的 OA 审批页面上，那个写着'流转'的小图标才是提交"
  → 这就是为什么需要针对特定场景训练

特定业务 GUI Agent（Trained）：
  知道 OA 里那个云朵图标是"附件上传"
  知道 CRM 里那个对勾不是"确认"而是"批量审批"
  知道异常弹窗出现时应该先关闭而不是硬点
```

## 1. SFT vs RL：两条路线的本质差异

### 1.1 SFT（监督微调）：老师手把手教

```
SFT 的过程：
  收集 1000 条标注数据：
    截图 → 正确操作序列
    截图 → 正确操作序列
    ...
  让模型背诵"看到这个截图 → 做这个操作"

问题：
  ❌ 需要大量标注（百万级样本才够）
  ❌ 过拟合训练的界面，界面一改就不认识
  ❌ 标注成本巨高
```

### 1.2 RL（强化学习）：在试错中学习

```
RL 的过程：
  给模型一个任务（如"帮我填写这张表单"）
  模型自己尝试 → 做对了给奖励 → 做错了给惩罚
  不断试错 → 策略越来越好

优势：
  ✅ 只需少量样本（几十到几千条）
  ✅ 能泛化到没见过的新界面
  ✅ 不需要人工逐条标注（奖励函数自动评分）
```

### 1.3 对比

| 维度 | SFT | RL（GRPO） |
|---|---|---|
| 数据需求 | 百万级 | **3K~24K**（省 50%+） |
| 泛化能力 | 差（过拟合） | **好**（跨平台跨场景） |
| 标注成本 | 高（人工逐条） | **低**（规则自动评分） |
| 训练成本 | GPU 时间长 | **省 30-50% 显存/时间** |
| 纠错能力 | 需重新标注 | **在线自纠错** |
| 适用场景 | 有大量标注数据 | 数据稀缺、追求泛化 |

> 一句话：**如果你有充足标注预算 → SFT。如果你想用小数据获得通用性 → GRPO。**

## 2. GRPO 算法：GUI Agent 的主流 RL 选择

### 2.1 为什么选 GRPO 而不是 PPO？

```
PPO 的问题：
  - 需要额外训练一个和策略模型一样大的 Critic（价值网络）
  - 显存翻倍
  - 实现复杂
  - GUI 任务里"每一步该给多少奖励"很难定义（信用分配问题）

GRPO 的解法：
  - 完全不要 Critic！用"组内比较"代替
  - 给一个任务生成多个候选方案 → 奖励高的优于平均 → 奖励低的弱于平均
  - 显存省 50%，速度提升 30%+
```

### 2.2 GRPO 核心公式

```
对每个任务，模型生成 N 个候选响应 o1, o2, ..., oN

每个候选的奖励：r1, r2, ..., rN（由奖励函数计算）

相对优势：
  Ai = (ri - mean(r)) / std(r)

含义：
  - 奖励高于平均 → Ai 为正 → 强化这个方案
  - 奖励低于平均 → Ai 为负 → 弱化这个方案
  - 用标准差归一化 → 避免尺度问题
```

### 2.3 GRPO 在 GUI Agent 中的完整流程

```python
def grpo_training_loop(gui_agent, tasks, reward_function, num_candidates=8):
    """GRPO 训练 GUI Agent 的完整流程"""
    
    for epoch in range(num_epochs):
        for task in tasks:
            # 1. 对每个任务，生成多个候选响应
            candidates = []
            for _ in range(num_candidates):
                screenshot = get_screenshot()
                response = gui_agent.generate(screenshot, task)
                candidates.append(response)
            # 每个 response 包含：思考过程 + 动作（类型、坐标、文本）
            
            # 2. 用奖励函数给每个候选打分
            rewards = [reward_function(task, c) for c in candidates]
            # 奖励函数检查：
            #   - 动作类型对不对（点击 vs 输入）
            #   - 坐标在不在目标区域内
            #   - 输入的文本对不对
            
            # 3. 计算相对优势
            mean_r = sum(rewards) / len(rewards)
            std_r = (sum((r - mean_r)**2 for r in rewards) / len(rewards)) ** 0.5
            advantages = [(r - mean_r) / max(std_r, 1e-8) for r in rewards]
            
            # 4. 更新策略（强化优势为正、弱化优势为负）
            for response, advantage in zip(candidates, advantages):
                loss = -advantage * log_prob(response | screenshot, task)
                # + KL 散度约束（防止策略突变）
                loss += beta * kl_divergence(current_policy, reference_policy)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
```

## 3. 三阶段训练法（企业级方案）

参考 Mobile-R1 的实践，把训练分成三个阶段：

```
┌──────────────────────────────────────────┐
│  阶段 1：感知预训练（SFT）               │
│  ─────────────────────                   │
│  目标：让模型"看懂"你的 APP 界面         │
│  方法：APP 截图 + 元素标注做微调          │
│  数据：几百张带标注的截图即可             │
│  时长：1-2 小时                          │
├──────────────────────────────────────────┤
│  阶段 2：单步 GRPO（Action-Level）       │
│  ─────────────────────────────           │
│  目标：每一步操作都精准（点对按钮）       │
│  方法：GRPO 优化单步动作                  │
│  奖励：坐标命中 + 动作类型正确             │
│  数据：数百个单步操作样本                 │
│  时长：数小时                            │
├──────────────────────────────────────────┤
│  阶段 3：任务级 GRPO（Task-Level）       │
│  ─────────────────────────────           │
│  目标：学会多步规划 + 自行纠错            │
│  方法：GRPO 优化完整任务轨迹               │
│  奖励：最终任务完成度 + 轨迹效率          │
│  数据：数十个完整任务样本                 │
│  时长：数小时                            │
└──────────────────────────────────────────┘
```

### 奖励函数设计（最关键的一步）

```python
class GUI_RewardFunction:
    """GUI Agent 的奖励函数设计"""
    
    @staticmethod
    def compute_reward(action, ground_truth, task_context):
        reward = 0
        
        # === 1. 动作类型奖励 ===
        # 点对了按钮类型？（点击 vs 输入 vs 滚动）
        if action.type == ground_truth.type:
            reward += 1.0
        else:
            reward += 0.0
        
        # === 2. 坐标命中奖励 ===
        # 点到了目标区域内？
        if action.type == "click":
            if is_inside_bbox(action.x, action.y, ground_truth.bbox):
                reward += 1.0
            elif is_near_bbox(action.x, action.y, ground_truth.bbox, tolerance=20):
                reward += 0.5  # 差一点，给一半奖励
            else:
                reward += 0.0
        
        # === 3. 文本匹配奖励 ===
        # 输入的内容对不对？
        if action.type == "type":
            f1 = compute_f1(action.text, ground_truth.text)
            if f1 > 0.8:
                reward += 1.0
            elif f1 > 0.5:
                reward += 0.5
        
        # === 4. 格式奖励 ===
        # 输出格式对不对？（需要包含 <think> 和 <action>）
        if is_valid_format(action.raw_output):
            reward += 0.2
        else:
            reward -= 0.5  # 格式错扣分
        
        # === 5. 安全奖励 ===
        # 危险操作扣重分
        if is_dangerous_action(action, task_context):
            reward -= 2.0
        
        return reward
```

## 4. 企业级落地四步走

### Step 1：梳理核心场景 + 数据准备

```python
# 优先收集"难样本"：基础模型原本做不对的操作
hard_samples = collect_hard_samples(app, base_model)
# 例如：
# - APP 专属图标的识别（不是通用按钮）
# - 复杂表单填写（字段多、依赖关系复杂）
# - 异常弹窗的处理（登录过期、网络错误）

# 数据量参考
DATA_BUDGET = {
    "sft_stage": 100-500,    # 感知预训练
    "action_grpo": 50-200,   # 单步 GRPO
    "task_grpo": 20-100,     # 任务级 GRPO
}
```

### Step 2：设计专属奖励函数

```python
# 奖励设计原则
DESIGN_PRINCIPLES = """
1. 准确性优先：点击位置/输入内容对了才给分
2. 效率加分：步骤越少越好
3. 安全兜底：危险操作重罚
4. 格式规范性：确保输出可解析
5. 场景定制：结合业务逻辑（如"审批流中不能跳过必填项"）
"""
```

### Step 3：分阶段训练

```python
# 参考 Mobile-R1 训练配置
TRAINING_CONFIG = {
    "stage1_sft": {
        "method": "Supervised Fine-Tuning",
        "data_size": "4635 轨迹, 24521 步骤",
        "epochs": 3,
    },
    "stage2_action_grpo": {
        "method": "Action-Level GRPO",
        "reward": "坐标命中 + 动作类型 + 文本匹配 + 格式",
        "candidates_per_task": 8,
    },
    "stage3_task_grpo": {
        "method": "Task-Level GRPO",
        "reward": "任务完成度 + 轨迹效率 + 格式",
        "candidates_per_task": 4,
    },
}
```

### Step 4：在线迭代与适配

```python
# 保持持续进化
class OnlineAdaptation:
    """APP 更新后快速适配"""
    
    def adapt_to_new_ui(self, old_ui_screenshots, new_ui_screenshots):
        """UI 改版后：只补充差异界面样本，GRPO 快速微调"""
        diff_samples = find_diff_samples(old_ui_screenshots, new_ui_screenshots)
        # 不需要全量重训！
        grpo_fine_tune(diff_samples, additional_steps=100)
    
    def continuous_improvement(self):
        """从线上错误日志中持续学习"""
        error_cases = load_error_logs()
        # 把线上出错的 case 加入训练集
        # 模型会越来越好
        grpo_fine_tune(error_cases)
```

## 5. 关键开源项目与论文

| 项目/论文 | 训练方案 | 数据量 | 效果 |
|---|---|---|---|
| **GUI-R1** | GRPO 统一动作空间 | 3K (原 1400 万的 0.02%) | 超越 SFT |
| **UI-R1** | GRPO 坐标优化 | 136 样本 | 超 SFT |
| **Mobile-R1** | 三阶段：SFT→单步GRPO→任务GRPO | 4635 轨迹 | 任务完成率大幅提升 |
| **MobileGUI-RL** | MobGRPO 在线学习 | 自主生成+筛选 | 自适应新环境 |
| **GUI-Critic-R1** | S-GRPO 术前批评 | 专用训练集 | 错误率显著降低 |

## 6. 一句话总结

> `SFT 靠标注数据喂 → 成本高、泛化差`。`GRPO 靠规则奖励 + 组内比较 → 极少数据、省钱、泛化好`。三阶段训练（感知预训练→单步精化→任务级规划）是企业落地的标准范式。
