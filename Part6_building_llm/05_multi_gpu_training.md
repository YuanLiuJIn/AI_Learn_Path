# 05 如何使用多 GPU 训练？DP、TP、PP 和 ZeRO

## 1. 它解决什么问题

大模型大到**单张 GPU 既装不下、也算不快**。必须用多张 GPU（甚至多台机器）协同训练。本章讲清四种并行：DP、TP、PP、ZeRO，以及何时用哪种。

回顾 Part1：显存被模型参数、梯度、优化器状态、激活值占用。多卡并行就是把“计算”或“存储”分摊到多张卡上。

## 2. 四种并行一句话概览

```text
DP（数据并行）：  每卡放完整模型，各算不同数据，再同步梯度
TP（张量并行）：  把单层(如大矩阵)横切到多卡，一层的计算多卡合作
PP（流水线并行）：把不同层放到不同卡，像流水线接力
ZeRO：           数据并行的升级，把参数/梯度/优化器状态切分到多卡，消除冗余
```

## 3. 数据并行（Data Parallel, DP）

### 一句话直觉

> 每张卡都放一份完整模型，把一个大 batch 拆成几份分给各卡，各自前向反向算梯度，然后把梯度平均同步，一起更新。

```text
卡0: 模型副本 + 数据块A -> 梯度A ┐
卡1: 模型副本 + 数据块B -> 梯度B ├─ 平均梯度 -> 各卡同步更新
卡2: 模型副本 + 数据块C -> 梯度C ┘
```

```text
优点：简单、最常用，适合模型能放进单卡的情况
缺点：每卡都存完整模型+梯度+优化器状态 -> 冗余巨大；模型放不下就没用
实现：PyTorch DDP(DistributedDataParallel)
```

## 4. 张量并行（Tensor Parallel, TP）

### 一句话直觉

> 一层里的大矩阵乘法太大，单卡装不下/算不快？把这个矩阵**横向切开**，每张卡算一部分，再把结果拼起来。一层的计算由多卡合作完成。

```text
一个大矩阵乘法 Y = X·W
把 W 按列切成 [W1 | W2]，分到两卡：
  卡0 算 X·W1，卡1 算 X·W2 -> 拼接得到 Y
```

```text
优点：能放下单层都装不下的超大模型；层内并行
缺点：卡间通信频繁(每层都要通信) -> 需要高速互联(NVLink)
适用：单机多卡(通信快)，常用于 Transformer 的注意力和 FFN 层
代表：Megatron-LM
```

## 5. 流水线并行（Pipeline Parallel, PP）

### 一句话直觉

> 模型有很多层，把不同层段放到不同卡上，数据像流水线一样依次流过：卡0 算完第 1-10 层，把结果传给卡1 算第 11-20 层……

```text
卡0: 层 1-10  ┐
卡1: 层 11-20 ├─ 数据依次流过，像工厂流水线
卡2: 层 21-30 ┘
```

问题与解决：

```text
问题：朴素流水线有"气泡"(bubble)——卡1 等卡0 时在空转
解决：把 batch 切成多个 micro-batch，让各卡尽量同时有活干(GPipe/1F1B)
```

```text
优点：能放下层数极多的大模型；卡间通信少(只在层段边界)
缺点：有流水线气泡，调度复杂
代表：GPipe、PipeDream
```

## 6. ZeRO：消除数据并行的冗余

### 问题

数据并行里，每张卡都存了**完整的**参数、梯度、优化器状态。用 Adam 时优化器状态是参数的 2 倍，冗余极大。

### 一句话直觉

> 既然每张卡都存一份太浪费，那就把这些东西**切片分给各卡**，谁需要完整的，临时从别的卡同步过来。（呼应 Part1 第 6 章。）

```text
ZeRO-1：切分 优化器状态（Adam 的动量/方差）
ZeRO-2：再切分 梯度
ZeRO-3：再切分 模型参数本身
        每张卡只存 1/N，需要完整参数时临时聚合
```

```text
优点：大幅降低每卡显存，让数据并行能训超大模型；用法接近 DP，较易上手
缺点：通信量增加(尤其 ZeRO-3)，需要权衡
代表：微软 DeepSpeed ZeRO；PyTorch FSDP(思想类似 ZeRO-3)
```

## 7. 怎么选？组合使用（3D 并行）

```text
模型能放进单卡         -> DP（或 ZeRO 省显存）
单层太大放不下          -> TP（单机多卡，靠 NVLink）
层数太多、模型很深       -> PP（跨多机）
超大模型(百亿~万亿)      -> TP + PP + DP/ZeRO 组合（"3D 并行"）
```

```text
典型大模型训练：
  机器内部：TP（高速 NVLink）
  机器之间：PP + DP/ZeRO（InfiniBand）
```

## 8. 配合的省显存技术（来自 Part1）

```text
混合精度(bf16)：参数/激活减半
梯度检查点(checkpointing)：用重算换显存
梯度累积：模拟更大 batch
=> 这些和并行策略叠加使用
```

## 9. 代码直觉（PyTorch DDP 最常用）

```python
import torch, torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group("nccl")               # 初始化多卡通信
model = DDP(model.to(local_rank), device_ids=[local_rank])
# 之后训练循环和单卡几乎一样，DDP 自动同步梯度
```

更大规模用 DeepSpeed / FSDP（配置文件里开 ZeRO stage）。

## 经典论文与开源项目

- Shoeybi et al., "Megatron-LM (张量并行)", 2019。
- Huang et al., "GPipe (流水线并行)", 2019。
- Rajbhandari et al., "ZeRO", 2020；Rasley et al., "DeepSpeed", 2020。
- GitHub: `microsoft/DeepSpeed`、`NVIDIA/Megatron-LM`、PyTorch FSDP、`huggingface/accelerate`。

## 本章小结

多 GPU 训练四件套：DP（复制模型分数据，简单但冗余）、TP（切单层，层内合作，需高速互联）、PP（切层段，流水线接力）、ZeRO（切分参数/梯度/优化器状态，消除 DP 冗余）。超大模型用 TP+PP+DP/ZeRO 的 3D 并行，并叠加混合精度、梯度检查点等省显存技术。选择取决于“模型放不放得下、瓶颈在显存还是通信”。
