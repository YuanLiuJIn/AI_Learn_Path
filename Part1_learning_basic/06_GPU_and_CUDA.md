# 06 GPU 与 CUDA

深度学习能快速发展，除了算法和数据，也离不开 GPU。大模型训练尤其依赖 GPU、显存、通信和并行计算。

## 1. CPU 与 GPU 的区别

### CPU

CPU 像少数几个很强的专家，擅长复杂逻辑、分支判断和通用任务。

特点：

- 核心数量较少。
- 单核能力强。
- 擅长复杂控制流。
- 适合操作系统、业务逻辑、串行任务。

### GPU

GPU 像一大群执行简单任务的工人，擅长同时做大量相似计算。

特点：

- 核心数量多。
- 单个核心较简单。
- 擅长并行计算。
- 适合矩阵乘法、卷积、向量运算。

深度学习中大量计算可以写成矩阵乘法，因此非常适合 GPU。

## 2. 为什么神经网络适合 GPU

神经网络中最常见的计算是：

```text
Y = XW + b
```

这本质上是矩阵乘法。

矩阵乘法可以把很多元素计算拆开并行执行。例如计算输出矩阵中的每个元素，都可以由不同线程完成。

## 3. CUDA 是什么

CUDA 是 NVIDIA 提供的并行计算平台和编程模型。

它让开发者可以使用 NVIDIA GPU 进行通用计算，而不只是图形渲染。

简单理解：

```text
GPU 是硬件
CUDA 是让程序使用 GPU 的软件体系
cuDNN/cuBLAS 是深度学习常用高性能库
PyTorch 是上层深度学习框架
```

PyTorch 调用 GPU 时，底层很多操作会走 CUDA、cuDNN、cuBLAS 等库。

## 4. CUDA 编程模型的基本概念

CUDA 中常见层级：

```text
Grid -> Block -> Thread
```

- Thread：最小执行单元。
- Block：一组线程。
- Grid：一组 Block。

你可以把一个大任务拆成很多小任务，让成千上万个线程一起执行。

## 5. SIMT 思想

GPU 使用 SIMT：Single Instruction, Multiple Threads。

直觉：很多线程执行同一条指令，但处理不同数据。

这适合矩阵乘法这种规则计算，不适合大量复杂分支。

如果同一组线程走不同分支，会出现 warp divergence，降低效率。

## 6. 显存与内存带宽

GPU 有自己的显存。训练模型时，显存主要用于存放：

- 模型参数
- 梯度
- 优化器状态
- 中间激活值
- 输入 batch

显存不够时会出现 out of memory。

常见解决方法：

- 减小 batch size。
- 使用 mixed precision。
- 梯度累积。
- gradient checkpointing。
- 模型并行或 ZeRO 优化。

## 7. 计算瓶颈与内存瓶颈

有些任务主要受计算速度限制，有些任务主要受内存读写限制。

深度学习性能通常看：

- FLOPS：每秒浮点运算次数。
- Memory bandwidth：显存带宽。
- Utilization：GPU 利用率。
- Batch size：批大小。

不是所有代码放到 GPU 上都会变快。如果数据频繁在 CPU 和 GPU 之间搬运，反而会变慢。

## 8. PyTorch 中使用 GPU

常见模式：

```python
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

x = torch.randn(32, 128).to(DEVICE)
model = model.to(DEVICE)
output = model(x)
```

注意：模型和输入必须在同一个 device 上。

常见错误：

```text
Expected all tensors to be on the same device
```

意思是有的张量在 CPU，有的在 GPU。

## 9. dtype 与混合精度

常见 dtype：

| dtype | 特点 |
|---|---|
| float32 | 默认训练精度，稳定 |
| float16 | 更省显存，更快，但可能不稳定 |
| bfloat16 | 动态范围更大，大模型常用 |
| int8/int4 | 常用于推理量化 |

混合精度训练会在性能和数值稳定之间做平衡。

PyTorch 中常见工具：

```python
with torch.autocast(device_type="cuda", dtype=torch.float16):
    output = model(x)
    loss = loss_fn(output, y)
```

## 10. CUDA、驱动、PyTorch 版本关系

GPU 训练经常遇到版本匹配问题：

- NVIDIA Driver
- CUDA Toolkit
- cuDNN
- PyTorch CUDA build

一般建议：

- 优先按 PyTorch 官网安装命令安装。
- 不要随意混装多个 CUDA 版本。
- 遇到 GPU 不可用，先检查 `torch.cuda.is_available()`。

## 11. 常用检查命令

```bash
nvidia-smi
```

可查看 GPU、显存、驱动版本、当前进程。

在 Python 中：

```python
import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.version.cuda)
```

## 12. 与大模型的关系

大模型训练远远不只是“把模型放到 GPU”。还涉及：

- 数据并行
- 张量并行
- 流水线并行
- ZeRO 优化
- 显存优化
- 高速互联
- checkpoint
- 推理加速
- KV cache

这些属于后续大模型工程部分。本章只要求你理解 GPU 为什么快、CUDA 是什么、PyTorch 如何调用 GPU。

## 本章小结

GPU 擅长大规模并行矩阵计算，CUDA 是 NVIDIA GPU 的通用计算平台。深度学习框架隐藏了大部分 CUDA 细节，但理解线程、显存、数据搬运和 dtype，有助于排查训练和推理中的性能问题。

## 推荐阅读

- NVIDIA CUDA C Programming Guide。
- NVIDIA CUDA Best Practices Guide。
- PyTorch CUDA semantics documentation。
- Mark Harris, NVIDIA developer blog articles on CUDA optimization。
