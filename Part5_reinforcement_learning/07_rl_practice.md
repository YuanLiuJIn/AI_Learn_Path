# 07 RL 实战：月球车降落 & Atari 游戏

## 1. 本章目标

把前面的算法落到能跑的环境里。RL 是“纸上学不会”的学科，必须动手。本章用两个经典环境：LunarLander（月球车降落）和 Atari（雅达利游戏）。

## 2. 标准工具栈

```text
环境：Gymnasium（原 OpenAI Gym 的维护版）
算法库：Stable-Baselines3（开箱即用的 PPO/DQN 等）
       或 CleanRL（单文件实现，适合读懂细节）
可视化：TensorBoard 看奖励曲线
```

安装（可选）：`pip install gymnasium[box2d,atari] stable-baselines3`。

## 3. 实战一：LunarLander（月球车降落）

### 任务

```text
控制一个着陆器，靠点燃引擎平稳降落到两面旗之间的平台。
状态：8 维（位置、速度、角度、是否触地等）—— 连续状态
动作：4 个（什么都不做、点左/主/右引擎）—— 离散动作
奖励：平稳着陆 +100~+200；坠毁 -100；省燃料有加分
判定"解决"：连续 100 回合平均奖励 ≥ 200
```

### 用 PPO 训练（Stable-Baselines3）

```python
import gymnasium as gym
from stable_baselines3 import PPO

env = gym.make("LunarLander-v2")
model = PPO("MlpPolicy", env, verbose=1)     # MLP 策略（状态是低维向量）
model.learn(total_timesteps=500_000)         # 训练

# 评估
obs, _ = env.reset()
for _ in range(1000):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, term, trunc, _ = env.step(action)
    if term or trunc:
        obs, _ = env.reset()
```

观察奖励曲线：从一开始乱坠毁（负奖励），到逐渐学会悬停、对准、轻轻降落（奖励升到 200+）。

### 适合的算法

```text
LunarLander-v2（离散动作）：PPO、DQN、A2C 都可以
LunarLanderContinuous（连续动作）：PPO、SAC、TD3
```

## 4. 实战二：Atari 游戏

### 任务

```text
输入：游戏画面像素（210×160×3）—— 高维图像状态
动作：手柄按键（离散）
目标：最大化游戏得分（Breakout 打砖块、Pong 乒乓等）
这是 DQN 一战成名的舞台（DeepMind 2013/2015 超越人类玩家）。
```

### 关键工程处理（Atari 特有）

直接喂原始像素学不动，需要预处理（已封装在标准 wrapper 里）：

```text
1. 灰度化 + 缩放到 84×84：降维
2. 帧堆叠（Frame Stacking）：把连续 4 帧叠一起
   -> 让模型感知"运动"（单帧看不出球往哪飞）
3. 跳帧（Frame Skip）：每隔几帧才决策一次，加速
4. 奖励裁剪：把奖励限制到 [-1,1]，稳定训练
```

帧堆叠是重点直觉：

```text
单帧：只看到球在某个位置，不知道方向和速度
4 帧叠加：能看出球的运动轨迹 -> 才能决定挡板往哪移
```

### 用 DQN 训练

```python
from stable_baselines3 import DQN

# Atari 用 CnnPolicy（状态是图像，需要卷积网络，呼应 Part2 CNN）
model = DQN("CnnPolicy", "BreakoutNoFrameskip-v4",
            buffer_size=100_000,      # 经验回放池
            learning_starts=50_000,
            verbose=1)
model.learn(total_timesteps=1_000_000)
```

注意 Atari 用 `CnnPolicy`（卷积处理图像），而 LunarLander 用 `MlpPolicy`（全连接处理向量）——状态形态决定网络结构。

## 5. 调试 RL 的常见坑

RL 比监督学习难调，常见问题：

```text
1. 不收敛 / 奖励上不去：
   - 学习率、网络规模、训练步数不够
   - 奖励设计不合理（reward shaping 很关键）
2. 训练不稳定 / 突然崩盘：
   - PPO 的 clip 范围、batch 大小
   - 随机种子影响大（RL 方差高，多跑几个种子）
3. 学到"投机取巧"（reward hacking）：
   - 智能体钻奖励函数的空子（比如原地刷分而不完成任务）
4. 样本效率低：
   - RL 往往需要百万级交互，耐心 + 用 off-policy 算法复用数据
```

实用建议：

```text
- 先用 Stable-Baselines3 跑通，确认环境/流程没问题
- 再用 CleanRL 读单文件实现，理解每一行
- 一定要画奖励曲线（TensorBoard），靠数字而非感觉判断
- RL 方差大，同一配置多跑几个随机种子看平均
```

## 6. 从实战到前沿

```text
LunarLander/Atari -> 连续控制(MuJoCo 机器人) -> 复杂游戏(星际/Dota)
                  -> 真实机器人 -> RLHF(用 PPO 对齐大模型)
下一章进入另一条线：棋类 AI（搜索 + RL）。
```

## 经典论文与开源项目

- Mnih et al., "Human-level control through deep RL" (DQN/Atari), 2015。
- Schulman et al., "PPO", 2017。
- GitHub: `DLR-RM/stable-baselines3`（开箱即用）、`vwxyzjn/cleanrl`（单文件精读）、`Farama-Foundation/Gymnasium`。

## 本章小结

RL 必须动手。用 Gymnasium + Stable-Baselines3，PPO 可以解决 LunarLander（低维向量状态，用 MLP），DQN 可以玩 Atari（图像状态，用 CNN，需帧堆叠等预处理）。调 RL 要重视奖励设计、随机种子和奖励曲线，警惕 reward hacking。跑通这两个环境，你就真正“做过” RL 了。
