# 07 PyTorch 基础

PyTorch 是当前深度学习和大模型研究、训练、微调中最常用的框架之一。本章目标是掌握 PyTorch 的核心概念，而不是背 API。

## 1. PyTorch 的核心模块

| 模块 | 作用 |
|---|---|
| `torch.Tensor` | 张量计算 |
| `torch.autograd` | 自动求导 |
| `torch.nn` | 神经网络层和模型容器 |
| `torch.optim` | 优化器 |
| `torch.utils.data` | 数据集和 DataLoader |
| `torch.cuda` | GPU 支持 |

一个标准训练流程基本都会用到这些模块。

## 2. Tensor

Tensor 是 PyTorch 的基本数据结构，本质是一个“能放到 GPU 上、能自动求梯度的多维数组”。

### 2.1 按维度理解

“维度”就是这个数字容器嵌套了几层：

```text
0 维：标量    5              一个 loss 值
1 维：向量    [1, 2, 3]      一个样本的特征
2 维：矩阵    [[1,2],[3,4]]  一批样本
3 维及以上    图片、视频、文本批次
```

### 2.2 三个必看属性

```python
import torch

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(x.shape)   # torch.Size([2, 2])  形状：几行几列、几维
print(x.dtype)   # torch.float32       数据类型
print(x.device)  # cpu                 在 CPU 还是 GPU
```

很多 PyTorch 错误都来自这三者不匹配：

- `shape`：维度对不上，矩阵乘法报错。
- `dtype`：类型不对，例如分类标签要 `torch.long`。
- `device`：一个在 CPU 一个在 GPU 不能一起算。

### 2.3 和 list / NumPy 的区别

```text
Python list   -> 只能存数据，不能算梯度，不能上 GPU
NumPy array   -> 能高效计算，但不能算梯度，不能上 GPU
PyTorch Tensor-> 能计算、能自动求梯度、能上 GPU  ← 深度学习需要
```

神经网络里的数据和参数全都是 Tensor。

### 2.4 batch 维度

训练时通常一次喂一小批样本，这“一批”就是在 Tensor 最前面加一个维度：

```text
单条表格样本：[特征数]            例如 [10]
一批 32 条：  [32, 10]           ← 第一维 32 就是 batch_size

单张图片：    [通道, 高, 宽]      例如 [3, 224, 224]
一批 32 张：  [32, 3, 224, 224]  ← 第一维 32 是 batch
```

看任何 PyTorch 代码的习惯：先看 Tensor 的 `shape`，**第一维通常就是 batch_size**，后面才是数据本身的形状。

## 3. 自动求导 autograd

PyTorch 可以自动记录计算图并求梯度。

```python
import torch

x = torch.tensor([2.0], requires_grad=True)
y = x ** 2 + 3 * x + 1
y.backward()
print(x.grad)
```

这里：

```text
y = x^2 + 3x + 1
dy/dx = 2x + 3
x = 2 时，梯度 = 7
```

PyTorch 会自动算出这个梯度。

## 4. nn.Module

`nn.Module` 是 PyTorch 中所有神经网络模型的“父类/模板”。你写任何模型都继承它，它会帮你自动管理层、参数、设备、训练/评估模式等繁琐事务。你只需做两件事：在 `__init__` 里声明用到哪些层，在 `forward` 里定义数据怎么从输入流到输出。

```python
import torch
from torch import nn

class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()                     # 必须调用，初始化父类
        self.net = nn.Sequential(              # 第1步：声明有哪些层
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):                      # 第2步：定义前向传播
        return self.net(x)
```

使用：

```python
model = MLP(input_dim=10, hidden_dim=64, output_dim=2)

x = torch.randn(32, 10)   # 一批数据：32 个样本，每个 10 维
output = model(x)         # 用 model(x)，不要 model.forward(x)
print(output.shape)       # torch.Size([32, 2])
```

重要规则：

- 层在 `__init__` 中定义，前向计算在 `forward` 中写。
- 调用模型用 `model(x)`，不要手动调用 `model.forward(x)`（前者还会执行 PyTorch 的内部钩子）。

继承 `nn.Module` 后，它自动帮你做：

```python
model.parameters()   # 自动收集所有参数，交给优化器
model.to("cuda")     # 一行把整个模型搬到 GPU
model.train()        # 切训练模式（Dropout、BatchNorm 生效）
model.eval()         # 切评估模式
model.state_dict()   # 打包所有参数，方便保存
```

## 5. Dataset 与 DataLoader

`Dataset` 定义如何取单条数据，`DataLoader` 负责批量读取、打乱和并行加载。

```python
from torch.utils.data import Dataset, DataLoader

class SimpleDataset(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

loader = DataLoader(SimpleDataset(x, y), batch_size=32, shuffle=True)
```

### epoch、batch、step 的关系

这三个概念会在下面的训练循环里反复出现：

- batch：一次喂给模型的一小批样本（如 32 条），对应 Tensor 的第一维。
- step：处理完一个 batch、更新一次参数，叫一个 step。
- epoch：模型完整看完一遍训练集，叫一个 epoch。

它们的换算：

```text
假设训练样本 = 1000，batch_size = 100

steps_per_epoch = 1000 / 100 = 10   （1 个 epoch 包含 10 个 step）
训练 5 个 epoch  = 5 × 10 = 50 个 step
```

为什么要多个 epoch：模型看一遍数据通常学不充分，多看几遍才能把损失降下来。但 epoch 太少会欠拟合，太多会过拟合（训练 loss 继续降，验证 loss 反而上升），这时用 early stopping、正则化等手段控制。

## 6. 标准训练循环

```python
import torch
from torch import nn

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = MLP(input_dim=10, hidden_dim=64, output_dim=2).to(DEVICE)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

for epoch in range(10):
    model.train()
    total_loss = 0.0

    for batch_x, batch_y in train_loader:
        batch_x = batch_x.to(DEVICE)
        batch_y = batch_y.to(DEVICE)

        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"epoch={epoch}, loss={total_loss / len(train_loader):.4f}")
```

训练循环必须理解，不要只复制。

关键顺序：

```text
前向传播 -> 计算损失 -> 清空旧梯度 -> 反向传播 -> 更新参数
```

## 7. 为什么要 `optimizer.zero_grad()`

PyTorch 默认会累积梯度。

如果不清空，上一个 batch 的梯度会叠加到当前 batch，导致更新错误。

常见写法：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

## 8. 训练模式与评估模式

```python
model.train()
model.eval()
```

它们会影响 Dropout、BatchNorm 等层的行为。

评估时通常需要：

```python
model.eval()
with torch.no_grad():
    logits = model(x)
```

`torch.no_grad()` 可以减少显存占用，因为不需要记录计算图。

## 9. 保存与加载模型

保存参数：

```python
torch.save(model.state_dict(), "model.pt")
```

加载参数：

```python
model = MLP(input_dim=10, hidden_dim=64, output_dim=2)
model.load_state_dict(torch.load("model.pt", map_location="cpu"))
model.eval()
```

推荐保存 `state_dict`，而不是直接保存整个模型对象。

## 10. GPU 训练

```python
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(DEVICE)
batch_x = batch_x.to(DEVICE)
batch_y = batch_y.to(DEVICE)
```

模型、输入和标签要在同一个 device。

## 11. 常见错误

### 11.1 shape 不匹配

错误示例：

```text
mat1 and mat2 shapes cannot be multiplied
```

通常是 `nn.Linear` 的输入维度写错。

### 11.2 dtype 不匹配

分类标签用于 `CrossEntropyLoss` 时通常应为 `torch.long`。

### 11.3 device 不匹配

```text
Expected all tensors to be on the same device
```

说明有的张量在 CPU，有的在 GPU。

### 11.4 忘记 `model.eval()`

评估时 Dropout 还在随机丢弃，结果不稳定。

## 12. 一个最小 PyTorch 学习模板

```python
for epoch in range(num_epochs):
    model.train()
    for x, y in train_loader:
        x = x.to(DEVICE)
        y = y.to(DEVICE)

        pred = model(x)
        loss = loss_fn(pred, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        for x, y in valid_loader:
            x = x.to(DEVICE)
            y = y.to(DEVICE)
            pred = model(x)
```

这个模板后面会反复出现，包括图像分类、文本分类、语言模型微调。

## 13. 后续需要继续学习的 PyTorch 能力

Part1 只要求基础。后续建议继续学习：

- 自定义训练器
- 学习率调度器
- mixed precision
- distributed training
- profiling
- TorchScript / torch.compile
- Hugging Face Transformers
- PyTorch Lightning 或 Accelerate

## 本章小结

PyTorch 的核心是 Tensor、autograd、nn.Module、Dataset/DataLoader 和训练循环。真正掌握 PyTorch，标志不是会查 API，而是能独立写出训练、验证、保存、加载和 GPU 迁移流程。

## 推荐阅读

- PyTorch Official Tutorials。
- PyTorch Documentation: Autograd, CUDA semantics, torch.nn。
- *Dive into Deep Learning* PyTorch version。
- fast.ai Practical Deep Learning course。
