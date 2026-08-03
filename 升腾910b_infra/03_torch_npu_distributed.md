# 03 · torch_npu 迁移与分布式训练

> 最实用的一章。把你在 GPU 上写的 PyTorch 训练脚本，迁到 910B 上跑通，并扩展到多卡/多机。
> 对标：PyTorch + CUDA + NCCL + DDP/FSDP。

## 1. 安装与验证

```bash
# 安装顺序：驱动/固件 → CANN → torch → torch_npu（版本严格配套！）
pip install torch torch_npu -f https://download.pytorch.org/whl/npu  # 示意，以官方源为准

python -c "import torch, torch_npu; print(torch.npu.is_available())"  # True
x = torch.randn(3,3).npu(); print(x.device)  # npu:0
```

**infra 要点**：版本配套是升腾最大的坑。驱动、CANN、torch_npu 三者的版本矩阵必须匹配，否则各种诡异报错。装之前先查官方配套表。

## 2. 单卡迁移：GPU 代码改什么

绝大多数情况，把 `cuda` 换成 `npu` 即可：

```python
# GPU 版
device = 'cuda'
x = x.cuda()
with torch.cuda.amp.autocast():
    y = model(x)
torch.cuda.synchronize()

# NPU 版（几乎一一对应）
import torch_npu
device = 'npu'
x = x.npu()
with torch.npu.amp.autocast():        # 对标 cuda.amp
    y = model(x)
torch.npu.synchronize()               # 对标 cuda.synchronize()
```

常见差异清单：

| 话题 | GPU | NPU | 注意 |
|---|---|---|---|
| 设备名 | `cuda` / `cuda:0` | `npu` / `npu:0` | 字符串替换 |
| 混合精度 | `torch.cuda.amp` | `torch.npu.amp` | API 一致 |
| 随机种子 | `torch.cuda.manual_seed` | `torch.npu.manual_seed` | — |
| 某些算子 | 全支持 | 部分需 fallback | 查 [02](02_CANN_operators.md) |
| 通信 | NCCL | **HCCL** | 见下文 |

## 3. 混合精度与 loss scale

大模型训练常需 FP16/BF16 + loss scale（防梯度下溢）：

```python
scaler = torch.npu.amp.GradScaler()      # 对标 cuda 版
with torch.npu.amp.autocast(dtype=torch.bfloat16):
    loss = model(x)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

**infra 要点**：910B 上 **BF16 是首选**（动态范围大，几乎不用 loss scale 也很稳）；FP16 则需要 GradScaler。这和 A100 上的经验一致。

## 4. 分布式：HCCL 对标 NCCL

### 4.1 集合通信库对照

| 通信原语 | NCCL | HCCL | 用途 |
|---|---|---|---|
| AllReduce | ✅ | ✅ | DDP 梯度同步 |
| Broadcast | ✅ | ✅ | 初始化广播 |
| ReduceScatter | ✅ | ✅ | FSDP / ZeRO |
| AllGather | ✅ | ✅ | FSDP 参数聚合 |
| AllToAll | ✅ | ✅ | MoE / 张量并行 |

HCCL 是华为集合通信库，接口与 NCCL 高度相似（PyTorch 分布式后端选 `hccl` 即可）。

### 4.2 DDP 多卡（最常用）

```python
import torch
import torch.distributed as dist
import torch_npu

# 启动：用 torchrun，后端选 hccl
# torchrun --nproc_per_node=8 train.py
dist.init_process_group(backend='hccl')      # 对标 backend='nccl'
local_rank = int(os.environ['LOCAL_RANK'])
torch.npu.set_device(local_rank)
model = model.npu(local_rank)
model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])

# 训练循环和 GPU 版几乎一样
for x, y in loader:
    x, y = x.npu(), y.npu()
    loss = model(x, y)
    loss.backward(); optimizer.step()
```

启动命令：

```bash
# 单机 8 卡
torchrun --nproc_per_node=8 --nnodes=1 train.py

# 多机（HCCL 需要 MASTER_ADDR/MASTER_PORT，和 NCCL 同套环境变量）
torchrun --nproc_per_node=8 --nnodes=2 \
         --node_rank=$RANK --master_addr=$MASTER \
         --master_port=29500 train.py
```

### 4.3 拓扑与并行策略（连回 [01](01_hardware_architecture.md)）

```
单机 8 卡（HCCS 域内）：
  - 张量并行(TP) / 流水线并行(PP)：放同一机内，吃 HCCS 带宽
  - 数据并行(DP)：机内+机间都行，跨机走 RoCE

多机：
  - 跨机尽量只放 DP / PP，避免 TP 跨机（HCCS→RoCE 带宽塌方）
  - HCCL 会自动做拓扑感知，但人工规划并行策略能显著提效
```

**infra 要点**：和 GPU 集群同理——**把通信最密的并行维度留在最快的互联域内**。910B 单机 HCCS 带宽远高于跨机 RoCE，所以 TP 必须单机内。

### 4.4 FSDP / ZeRO（显存优化）

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
model = FSDP(model.npu())     # 用 hccl 后端，自动走 ReduceScatter/AllGather
```

torch_npu 对 FSDP 的支持已较成熟，背后用 HCCL 的 ReduceScatter + AllGather。

## 5. MindSpore 的分布式（补充视角）

MindSpore 是华为原生框架，分布式能力开箱即用，文档最全：

```python
# MindSpore 分布式（对标 PyTorch DDP）
import mindspore as ms
from mindspore.communication import init, get_rank
ms.set_context(device_target="Ascend")
init()                                  # 封装了 HCCL 初始化
# 并行策略通过 shard/auto_parallel 声明，框架自动切图
```

MindSpore 的「分布式并行训练(Ascend)」官方教程对理解**图级并行切分**很有帮助（见 [references.md](references.md)）。如果你只做 PyTorch 生态，可跳过；若做华为全家桶，建议读。

## 6. 常见坑

| 现象 | 可能原因 | 排查 |
|---|---|---|
| 多卡启动卡住 | HCCL 初始化失败 / 网卡未通 | 查 `MASTER_ADDR`、RoCE 连通性、`npu-smi` 看卡在位 |
| 速度远慢于预期 | 算子 fallback CPU | 开 `allow_ops_fallback` 看告警 |
| OOM | 分块/并行策略不当 | 降 batch、开 FSDP、调 `max_split_size` 类参数 |
| 数值对不齐 GPU | 精度差异 | 用 BF16、检查 loss scale、对比单步 |

## 7. 本章验收

- [ ] 把一份 GPU 训练脚本改到 NPU 单卡跑通
- [ ] 用 `torchrun` + `hccl` 在 2~8 卡跑通 DDP
- [ ] 说清 HCCL 与 NCCL 的对照，以及为什么 TP 要单机内
- [ ] 能配置 FSDP 并解释其 HCCL 通信原语
- [ ] 遇到 fallback/OOM 能初步定位

## 参考

- 官方：torch_npu GitHub、MindSpore「分布式并行训练(Ascend)」教程（见 [references.md](references.md)）
- 搜索结果：百度云《910B 多机部署 DeepSeek-V3/R1 实战》含分布式配置实操
