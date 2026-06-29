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

Tensor 是 PyTorch 的基本数据结构。

```python
import torch

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(x.shape)
print(x.dtype)
print(x.device)
```

需要重点关注三个属性：

- `shape`：形状是否正确。
- `dtype`：数据类型是否正确。
- `device`：在 CPU 还是 GPU。

很多 PyTorch 错误都来自这三者不匹配。

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

所有复杂模型通常继承 `nn.Module`。

```python
import torch
from torch import nn

class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x):
        return self.net(x)
```

重要规则：

- 在 `__init__` 中定义层。
- 在 `forward` 中定义前向计算。
- 不要手动调用 `forward`，而是调用 `model(x)`。

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
