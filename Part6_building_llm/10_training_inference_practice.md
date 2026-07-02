# 10. 结合 KM 实践补充：大模型训练稳定性与推理优化全栈

> 本章把 KM 中关于 CUDA Graph、FalconGEMM、Hy3 推理优化、AngelFT 训练稳定性、Token 工厂等内容整理为 Part6 的直接学习补充。

---

## 1. 大模型训练的真实难题：不是“会不会写训练代码”，而是“能不能稳定跑完”

当模型规模从单卡小模型变成千卡、万卡训练，问题会完全变样：

```text
单卡训练：代码错了就修代码
大规模训练：
  - 哪张卡慢了？
  - 哪个节点通信异常？
  - loss 为什么突然 NaN？
  - checkpoint 写坏了怎么办？
  - 训练中断后怎么无损续训？
```

因此 Part6 的重点不是只学模型结构，而是学习：

```text
训练系统 = 模型 + 并行策略 + 通信 + 存储 + 监控 + 自动恢复
推理系统 = 模型 + KV Cache + 调度 + 算子 + 量化 + 多级缓存
```

---

## 2. CUDA Graph：训练性能的“调度开销消除器”

KM 中 CUDA Graph 实践给了一个非常具体的优化案例：

```text
优化对象：ZeroOptimizer 的 _optimize_step
优化目标：把大量小 kernel 的 CPU launch 开销压缩掉
```

### 2.1 为什么选择 Optimizer Step？

```text
1. 小 kernel 多，launch-bound 明显
2. 边界清晰，梯度收集和裁剪已完成
3. 地址、形状、分支相对稳定
4. 风险比捕获整个 forward/backward 小
```

### 2.2 工程关键点

```text
Feature Flag + Fallback：捕获失败就回退 eager，保证训练稳定
动态标量 device tensor：学习率/step 等动态值不固化进 graph
地址/形状/分支检查：防止 replay 时使用错误 graph
Graph-safe kernel：kernel 从固定地址读取动态超参
```

### 2.3 收益

```text
21B 参数 CI 场景：
_optimize_step 区域 1.5s → 0.5s，局部约 3 倍加速
主计算流空闲间隙减少 53.2%
<50us 的 launch-addressable 间隙减少 83.9%
```

---

## 3. FalconGEMM：用算法换算力，把 H20 跑出 116% 等效峰值

H20 的特点：

```text
算力被限制
显存带宽相对充裕
```

传统 GEMM 无法充分利用“富余带宽”。FalconGEMM 的思想：

```text
用低复杂度矩阵乘法 LCMA，把部分乘法换成加法和访存。
```

### 3.1 Strassen 的直觉

普通矩阵乘法复杂度约：

```text
O(N^3)
```

Strassen 通过数学变换减少乘法次数：

```text
O(N^2.807)
```

理论上能省计算，但工程落地很难。

### 3.2 三座大山

```text
1. 冗余访存：中间矩阵重复读输入
2. 算子碎片化：大 GEMM 拆成多个小 GEMM，SM 利用率低
3. 写冲突：多个计算单元写同一输出区域
```

### 3.3 Group 并行融合

FalconGEMM 的核心创新：

```text
把同一相对坐标位置的所有中间矩阵元素打包为一个 Group
一个 CTA 负责这个 Group
```

优势：

```text
零冗余访存：输入只加载一次
无写冲突：每个 CTA 独立负责自己的输出
```

效果：

```text
H20 BF16：等效算力最大提升 28%，最高达硬件峰值 116%
H20 FP8：等效算力最大提升 86%
vLLM Prefill 替换后端到端加速 8%~14%
```

这个案例告诉我们：

> 大模型性能优化不只是调参数，底层数学算法和编译器也能改变硬件利用边界。

---

## 4. Hy3 preview 推理优化：五层全栈地图

Hy3 preview 是 GQA + MoE 混合架构，支持 256K 超长上下文。H20 上部署挑战巨大：

```text
显存紧
算力弱
上下文长
请求长短混合
SLO 严格
```

KM 中 Hy3 推理优化文章把优化拆成五层。

### 4.1 算子优化与融合

```text
Attention 动态调度：解决长短请求混合负载不均，最高 2.95x
Router GEMM 双 BF16：FP32 权重拆成两个 BF16，2.86x~3.22x
FusedMoE：路由、门控、矩阵乘全链路融合，1.2x~1.6x
小算子融合：Rope/Norm/Quant 融合，约 5x
```

### 4.2 并行策略

```text
Prefill：TPSP（Tensor Parallel + Sequence Parallel）压缩 TTFT
Decode：DP + EP（数据并行 + 专家并行）提升吞吐
```

### 4.3 多级缓存

```text
GPU KV Cache
CPU KV Cache
远端 KVStore
```

目标：减少重复计算，把 KV Cache 从单一显存扩展到分层存储。

### 4.4 MTP 和异步调度

MTP（Multi-Token Prediction）可以一次预测多个 token。

异步调度的关键：

```text
不要让 CPU 每轮都等真实接收长度。
用乐观更新提前准备下一轮输入，消除 CPU 气泡。
```

收益：端到端性能提升 10%~20%。

### 4.5 量化与稀疏

```text
W4A8：权重 4bit，激活 8bit
结合 GPTQ 权重重建 + 激活平滑 + QAT 微调
端到端吞吐提升 28%+

Stem 稀疏注意力：
仅用 25% 计算预算，128K Prefill 延迟降低 3.6 倍
```

---

## 5. PD 分离：为什么 Prefill 和 Decode 要分开优化？

大模型推理分两段：

```text
Prefill：处理用户输入，一次性计算整段 prompt 的 KV Cache
Decode：逐 token 生成输出
```

二者计算特征不同：

| 阶段 | 特征 | 瓶颈 |
|---|---|---|
| Prefill | 大矩阵、并行度高 | 算力/带宽 |
| Decode | 小步循环、batch 动态 | KV Cache/调度/延迟 |

所以推理系统常做 PD 分离：

```text
Prefill 节点专门处理长输入
Decode 节点专门处理生成
二者独立扩缩容和调度
```

这比“一套机器干所有事”更容易提高吞吐和降低延迟。

---

## 6. 训练稳定性：AngelFT 的启发

AngelFT 把大模型训练稳定性拆成：

```text
感知 → 诊断 → 恢复
```

这在万卡训练里非常关键。

```text
感知：分钟级发现异常
诊断：定位慢卡、精度异常卡、通信异常
恢复：自动续训，降低人工救火
```

对学习者的启发：

```text
1. 训练系统一定要记录 step time、loss、梯度范数、GPU 利用率
2. checkpoint 不是“可选项”，而是大训练的生命线
3. 诊断系统比单次训练脚本更重要
```

---

## 7. Part6 学完后的工程地图

```text
训练侧：
  数据 → Tokenization → 并行训练 → CUDA Graph → 训练监控 → 自动恢复

推理侧：
  请求 → Prefill → KV Cache → Decode → 调度 → 量化 → 缓存 → 返回

算子侧：
  GEMM / Attention / MoE / Norm / Rope / Sampling

平台侧：
  GPU 调度 / 容器 / 多级缓存 / 弹性伸缩 / 观测系统
```

---

## 8. 一句话总结

> 打造 LLM 不只是“搭一个 Transformer”。训练要解决稳定性和并行效率，推理要解决吞吐、延迟、KV Cache、量化和调度。KM 中的 Hy3、FalconGEMM、CUDA Graph、AngelFT 都在说明：**真正的 LLM 能力，是模型算法 + 系统工程 + 硬件优化的合体。**

---

## 参考来源

本文综合整理自 KM 中 CUDA Graph Optimizer Step 实践、FalconGEMM、Hy3 preview 推理优化、AngelFT 训练稳定性、Token 工厂推理优化系列、训练监控系统等文章。
