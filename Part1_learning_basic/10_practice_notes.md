# 10. 结合 KM 实践补充：从基础概念到真实训练工程

> 本章不是文章索引，而是把 KM 上几类一线实践内容，消化成 Part1 可直接学习的补充章节。
> 重点回答：基础机器学习、深度学习、GPU/CUDA、PyTorch 训练框架学完后，在真实业务里会遇到什么工程问题？

---

## 1. 从“机器怎么学”到“系统怎么跑”

Part1 里你已经学了监督学习、损失函数、梯度下降、深度学习、PyTorch 和 CUDA。真实业务里的 AI 系统并不是只写一句：

```python
loss.backward()
optimizer.step()
```

就结束了。真实训练链路更像下面这样：

```text
数据准备 → 模型定义 → 训练循环 → GPU 资源申请 → 容器环境 → 分布式调度
        → 性能分析 → 训练监控 → 异常诊断 → 断点续训 → 部署推理
```

所以 Part1 的核心目标不只是“知道算法名字”，而是建立四层直觉：

```text
第1层：模型怎么学？        监督学习 / 损失函数 / 梯度下降
第2层：网络怎么训练？      前向传播 / 反向传播 / 优化器 / 正则化
第3层：计算怎么跑快？      GPU / CUDA / 混合精度 / CUDA Graph
第4层：训练怎么稳定运行？  容器 / 调度 / 监控 / 异常恢复
```

---

## 2. GPU/CUDA 的真实痛点：不是“有没有 GPU”，而是“GPU 有没有空转”

初学 CUDA 时，我们容易以为：

> 只要把张量放到 `cuda` 上，训练就会变快。

真实情况更复杂。KM 中关于 CUDA Graph 的训练实践文章给了一个非常重要的视角：**GPU 很多时候不是算不动，而是在等 CPU 发指令。**

### 2.1 GPU 时间线里的“微空洞”

训练时 CPU 会不断向 GPU 发射 kernel：

```text
CPU: launch kernel A → launch kernel B → launch kernel C → ...
GPU:      run A      gap     run B      gap     run C
```

这些 `gap` 可能只有几十微秒，但大模型训练里 kernel 数量极多，累积起来就是显著损耗。

这类问题叫 **launch-bound**：

```text
计算本身不慢，慢在“发射太多小任务”的调度开销。
```

### 2.2 为什么 Optimizer Step 很适合 CUDA Graph？

在大模型训练中，Optimizer Step 往往包含大量小 kernel：

```text
for each parameter:
    更新一阶矩 m
    更新二阶矩 v
    做 weight decay
    更新参数 w
```

如果每个参数、每个小操作都单独发 kernel，CPU 调度开销会非常高。

CUDA Graph 的思路是：

```text
第一次：把一串 kernel 发射过程“录下来”
之后：直接 replay 这张图，不再逐个发射 kernel
```

伪代码直觉：

```python
# eager 模式：每步都由 CPU 一次次发射 kernel
for step in range(num_steps):
    optimizer.step()

# CUDA Graph 思路：先捕获，再 replay
graph = capture(lambda: optimizer.step())
for step in range(num_steps):
    update_dynamic_scalars(lr, step)  # 学习率等动态值通过固定地址 tensor 更新
    graph.replay()
```

### 2.3 动态标量为什么麻烦？

CUDA Graph 要求地址、形状、分支尽量稳定。但训练中有些东西每步都变，例如：

```text
learning_rate
step_count
loss_scale
```

如果把这些值直接固化到 graph 里，replay 时就会用旧值，产生静默错误。

工程解法是：

```text
把动态标量放进固定地址的 device tensor。
每次 replay 前只更新这个 tensor 的内容，不改变地址。
Graph 内 kernel 从固定地址读最新值。
```

这体现了一个重要工程原则：

> 高性能训练不是“把所有代码都 graph 化”，而是选择边界清晰、动态性较低、收益明确的部分先优化。

---

## 3. GPU 容器：环境一致性比你想象得更重要

很多新手训练失败，不是模型错，而是环境错：

```text
CUDA 版本不匹配
Driver 和 Runtime 不兼容
PyTorch 编译版本不对
容器里看不到 GPU
多机机器环境不一致
```

因此真实团队通常会把训练环境做成 CUDA 容器：

```text
镜像 = 操作系统 + CUDA Runtime + cuDNN/cuBLAS + PyTorch + 业务代码依赖
```

好处：

1. **可复现**：别人拉同一个镜像，就能跑同样环境
2. **可迁移**：从一台 GPU 机器迁移到另一台，依赖不乱
3. **可调度**：平台可以统一分配 GPU 容器
4. **可回滚**：环境出问题换回旧镜像即可

学习 Part1 时建议建立这个意识：

```text
模型代码只是训练系统的一部分。
环境、驱动、容器、监控、数据路径同样会决定训练成败。
```

---

## 4. 训练稳定性：大模型训练不是“跑起来”就够了

真实训练经常遇到：

```text
某张卡变慢，但任务没挂
某个节点精度异常，但 loss 还在下降
网络抖动导致 checkpoint 写失败
训练跑了三天后突然 NaN
人工发现问题太晚，浪费大量 GPU 时间
```

KM 中 AngelFT 的实践把训练稳定性拆成三步：

```text
感知 → 诊断 → 恢复
```

### 4.1 感知：先知道哪里不对

需要采集：

```text
GPU 利用率 / 显存 / 温度
step time
loss 曲线
梯度范数
通信耗时
checkpoint 状态
```

### 4.2 诊断：定位慢卡、坏卡、精度异常

训练慢不一定是模型慢，可能是：

```text
某张卡通信慢
某个 DataLoader 卡住
某个节点文件系统抖动
某个 kernel 退化
```

因此诊断系统要能把“整体变慢”拆成具体原因。

### 4.3 恢复：自动续训，而不是人工救火

生产级训练必须有：

```text
定期 checkpoint
故障节点剔除
自动重启
从最近 checkpoint 续训
失败原因记录
```

这和你在 Part1 学的 `state_dict` 是同一件事的工程放大版：

```python
checkpoint = {
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "scheduler": scheduler.state_dict(),
    "step": global_step,
    "rng_state": torch.get_rng_state(),
}
```

只是到了万卡训练，checkpoint 不再只是一个 `.pt` 文件，而是训练平台的核心可靠性机制。

---

## 5. Part1 学完后应该形成的工程直觉

```text
1. 机器学习不是“背算法”，而是用数据定义目标、用损失函数表达目标、用优化器逼近目标。
2. 深度学习不是“层数越多越好”，而是用表示学习把人工特征工程转移给模型。
3. PyTorch 的 Tensor/Module/Autograd 是最小训练闭环。
4. GPU 加速不只是“放到 cuda 上”，还涉及 kernel launch、显存、混合精度、通信、调度。
5. 真正的训练工程需要容器、监控、checkpoint、异常恢复。
```

---

## 6. 推荐练习

### 练习 1：观察 GPU 微空洞

用 PyTorch Profiler 跑一个小模型，观察 CPU 和 GPU 时间线：

```python
with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA],
    record_shapes=True,
) as prof:
    for step, batch in enumerate(loader):
        if step > 10:
            break
        loss = train_step(batch)
        prof.step()

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

观察：

```text
哪些算子耗时最高？
CPU self time 是否很大？
有没有大量小 kernel？
```

### 练习 2：保存完整 checkpoint

不要只保存模型参数，尝试保存：

```python
{
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "scheduler": scheduler.state_dict(),
    "epoch": epoch,
    "step": step,
}
```

然后模拟训练中断，从 checkpoint 恢复。

---

## 参考来源

本文综合整理自 KM 中关于 AI 通识、CUDA Graph、GPU 容器、训练稳定性与 GPU 调度的多篇实践文章，尤其参考了 CUDA Graph Optimizer Step 捕获、AngelFT 训练稳定性平台、GPU 容器部署等内部实践经验。
