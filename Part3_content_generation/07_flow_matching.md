# 07 大一统的生成模型 Flow Matching（含训练 Coding）

## 1. 它解决什么问题

扩散模型很强，但采样要很多步、训练目标绕（依赖噪声调度、SDE）。Flow Matching（Lipman et al., 2022）提供一个**更简单、更统一**的视角：

> 与其“加噪再去噪”，不如直接学一个**向量场**，把噪声分布“平滑地运输”到数据分布。训练目标极其简单，采样可以更直接、更快。

它在数学上统一了扩散、连续归一化流（CNF）等，被称为“大一统”框架，也是近年文生图/视频模型（如部分 SD3、Flux 路线）的核心。

## 2. 一句话直觉

> 想象噪声分布是 A 城，数据分布是 B 城。Flow Matching 学的是一张“流场地图”：在任意位置、任意时刻，箭头告诉你“往哪个方向走、走多快”，沿着箭头从 A 城匀速开到 B 城，就完成了“噪声 → 图像”。

生活类比：河流的水流场。每个点都有一个流速向量，一片落叶（噪声点）顺流而下，最终漂到出海口（数据点）。Flow Matching 就是学这个“流速场”。

## 3. 核心概念：概率路径与向量场

```text
定义一条从噪声到数据的"路径" p_t（t 从 0 到 1）：
  t=0：纯噪声分布 N(0,1)
  t=1：真实数据分布

学一个向量场 v_θ(x, t)：在位置 x、时刻 t，该往哪个方向移动。
生成 = 从噪声 x_0 出发，沿 v_θ 解一个常微分方程(ODE)积分到 t=1。
```

注意是 **ODE（确定性）** 而非扩散的 SDE（带随机），所以采样更直接。

## 4. 最优传输路径：直线最简单

Flow Matching 最优雅的一种是用**直线路径**（条件 OT 路径）：噪声点 `x_0` 和数据点 `x_1` 之间走直线。

```text
中间点：  x_t = (1 - t) · x_0 + t · x_1     （线性插值）
目标速度：v* = x_1 - x_0                     （指向终点的恒定方向）
```

也就是说，理想的“流速”就是**从起点直指终点的那个向量**，恒定不变。训练就是让网络预测这个速度。

## 5. 训练目标：简单到一行

```text
Flow Matching Loss = E[ || v_θ(x_t, t) - (x_1 - x_0) ||² ]

随机取：数据点 x_1、噪声 x_0 ~ N(0,1)、时刻 t ~ U(0,1)
构造：  x_t = (1-t)·x_0 + t·x_1
让网络预测的速度 v_θ(x_t, t) 对齐真实速度 (x_1 - x_0)，用 MSE。
```

对比扩散“预测噪声”，这里“预测速度”，同样是个 MSE 回归，但路径更直、概念更干净。

## 6. 采样：解 ODE

```text
从 x_0 ~ N(0,1) 起步
for t in 0 -> 1（分成若干步）:
    x ← x + v_θ(x, t) · Δt        # 沿预测的速度前进（欧拉法解 ODE）
得到 x_1，一张新图
```

因为路径接近直线，往往**很少的步数**就能生成高质量样本——这是 Flow Matching 相比扩散的速度优势。

## 7. Coding：Flow Matching 训练完整示例

下面是一个最小但完整、可运行的 Flow Matching（在 2D 玩具数据上，便于看清机制；换成图像数据 + U-Net 即为真实用法）。

```python
import torch
from torch import nn

# 向量场网络：输入 (x, t) -> 输出速度
class VectorField(nn.Module):
    def __init__(self, dim=2, h=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim + 1, h), nn.SiLU(),
            nn.Linear(h, h), nn.SiLU(),
            nn.Linear(h, dim),
        )
    def forward(self, x, t):
        t = t.view(-1, 1)
        return self.net(torch.cat([x, t], dim=1))

def sample_data(n):
    # 玩具目标分布：两个簇（换成你的真实数据即可）
    c = torch.randint(0, 2, (n, 1))
    return torch.randn(n, 2) * 0.3 + torch.where(c == 0, 2.0, -2.0)

model = VectorField()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)

# ---- 训练：让 v_θ 预测 (x1 - x0) ----
for step in range(5000):
    x1 = sample_data(256)                  # 真实数据
    x0 = torch.randn_like(x1)              # 噪声
    t = torch.rand(x1.size(0), 1)          # 随机时刻
    x_t = (1 - t) * x0 + t * x1            # 直线路径上的点
    target = x1 - x0                       # 真实速度（恒定方向）
    pred = model(x_t, t)
    loss = ((pred - target) ** 2).mean()   # Flow Matching 损失
    opt.zero_grad(); loss.backward(); opt.step()

# ---- 采样：从噪声解 ODE 到数据 ----
@torch.no_grad()
def generate(model, n=1000, steps=50):
    x = torch.randn(n, 2)                  # 从噪声起步
    dt = 1.0 / steps
    for i in range(steps):
        t = torch.full((n, 1), i * dt)
        x = x + model(x, t) * dt           # 欧拉法沿速度前进
    return x                               # 生成的样本
```

把 `VectorField` 换成注入时间步的 U-Net、数据换成图像，就是图像 Flow Matching；加上文本条件即可做文生图。

## 8. 与扩散、CNF 的关系

```text
扩散(SDE/score)：加噪去噪，随机过程，统一在 SDE
Flow Matching：  学向量场，确定性 ODE，路径可设计为直线 -> 更快
CNF(连续归一化流)：也学 ODE，但旧方法训练贵；Flow Matching 让它免去昂贵积分

它们都在做同一件事：把简单分布运输到数据分布，只是路径与训练方式不同。
```

## 经典论文与开源项目

- Lipman et al., "Flow Matching for Generative Modeling", 2022（奠基）。
- Liu et al., "Rectified Flow", 2022（直线路径、少步采样）。
- Esser et al., "Scaling Rectified Flow Transformers" (SD3), 2024（工业级应用）。
- GitHub: `facebookresearch/flow_matching`；`gnobitab/RectifiedFlow`。

## 本章小结

Flow Matching 学一个把噪声“运输”到数据的向量场，训练目标是预测“指向终点的速度”（MSE），采样是沿向量场解 ODE。用直线路径时步数少、速度快，并在数学上统一了扩散与连续流。它是新一代文生图/视频模型的重要内核。
