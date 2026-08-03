# 02 · CANN 软件栈与算子开发

> infra 核心章节。理解"PyTorch 模型 → NPU 上真正跑起来"中间发生了什么。
> 对标：CUDA 的 Driver + cuDNN/cuBLAS + TensorRT 编译链。

## 1. CANN 是什么

**CANN（Compute Architecture for Neural Networks）** 是升腾的异构计算架构，是连接"上层框架"和"底层 Da Vinci 硬件"的中间层。

```
┌─────────────────────────────────────────────┐
│  PyTorch / MindSpore  (框架层)                │
│        │  torch_npu / 框架插件                 │
├─────────────────────────────────────────────┤
│  CANN                                        │
│   ├─ GE (Graph Engine)   图编译/融合/切分      │
│   ├─ 算子库 (OPs)        Cube/Vector 算子实现  │
│   ├─ AscendCL            C/Python 调用接口    │
│   ├─ Runtime             设备管理/ stream/队列 │
│   └─ ATC                 模型转换 (→ OM)       │
├─────────────────────────────────────────────┤
│  驱动 + 固件  →  Da Vinci 910B 硬件           │
└─────────────────────────────────────────────┘
```

对标理解：
- GE ≈ TensorFlow 的 XLA / PyTorch 的 inductor（但更偏 NPU 专用）
- 算子库 ≈ cuDNN + cuBLAS
- AscendCL ≈ CUDA Runtime API
- ATC ≈ ONNX→TensorRT 的转换工具

## 2. 一条训练/推理请求的执行链路

以 PyTorch + torch_npu 为例：

```
1. Python 定义模型 → torch 计算图
2. torch_npu 把算子映射为 NPU 算子（op adapter）
3. GE 接收图：做构图、算子融合、分块(tiling)、调度规划
4. Runtime 把算子下发到 AI Core，管理 stream/event
5. Da Vinci 的 Cube/Vector 执行，结果写回 Global Memory
6. 反向时同样走 GE + 算子库（含梯度算子）
```

**infra 要点**：你写的 `x @ w` 不会直接变成一次 Cube 调用——GE 会把它和前后算子融合（fusion），以减少 Global Memory 往返。融合做得多不多，直接决定性能（这正是 msprof 要看的东西，见 [05](05_profiling_troubleshooting.md)）。

## 3. AscendCL：最小调用流程（对标 CUDA Runtime）

C/C++ 或 Python 都能调。一个最小推理流程骨架：

```c
// 伪代码：AscendCL 推理骨架
aclInit(NULL);                       // 初始化
aclrtSetDevice(deviceId);            // 选设备（对标 cudaSetDevice）
aclrtCreateContext(&ctx, deviceId);
aclrtCreateStream(&stream);

// 加载 OM 模型（ATC 离线转换好的）
aclmdlLoadFromFile("model.om", &modelId);
aclmdlDataset *input  = ...;         // 构造输入（对标 cudaMalloc + memcpy H2D）
aclmdlDataset *output = ...;

aclmdlExecute(modelId, input, output);  // 执行（对标 kernel launch）
// 拷回结果 D2H，后处理

aclmdlDestroyDataset(input);
aclrtDestroyStream(stream);
aclrtResetDevice(deviceId);
aclFinalize();
```

要点对照：
- `aclrtSetDevice` ↔ `cudaSetDevice`
- `aclrtMalloc` / `aclrtMemcpy` ↔ `cudaMalloc` / `cudaMemcpy`
- `aclrtStream` ↔ `cudaStream`
- `aclmdlExecute` ↔ kernel launch / `cudaGraph` 执行

> 日常用 PyTorch 时你不用手写 AscendCL（torch_npu 封装好了），但**理解它能帮你排错**：比如某算子 hang 住，本质是 AscendCL 的 stream 没调度起来。

## 4. 算子库与"算子缺失"问题

PyTorch 算子丰富，但 NPU 算子库是子集。常见情况：

| 情况 | 现象 | 解法 |
|---|---|---|
| 算子已支持 | 直接跑 | 无需处理 |
| 算子未支持 | 报错 `算子 xxx not implemented` | 用组合算子替代 / 自定义算子 |
| 精度差异 | 结果数值偏离 GPU | 检查精度（FP16/BF16）、开 `npu.allow_ops_fallback` 看是否走了 CPU 兜底（慢！） |

```python
import torch_npu
# 查看某算子是否落到 NPU，还是 fallback 到 CPU
torch.npu.allow_ops_fallback(True)   # 开启后，fallback 会告警
```

**infra 要点**：`fallback to CPU` 是性能黑洞——一个没映射到 NPU 的算子会让整条 stream 在 CPU 上串行执行。生产上要**零 fallback**。

## 5. 自定义算子（对标 Triton / CUDA C++）

当算子库没有你要的算子，用 **TBE（Tensor Boost Engine）** 开发：

- 方式一：**TBE DSL**（基于 TVM 的调度原语，写调度而非写指令，门槛较低）
- 方式二：**TIK**（类 C++ 的底层指令编程，直接操控 Cube/Vector/UB，性能好但难）

最小 TBE 算子骨架（DSL 风格）：

```python
from tbe import tvm
from tbe.dsl import auto_schedule, build
from tbe.common.utils import shape_util

# 1. 定义计算（compute）
def compute(data):
    return tvm.compute(data.shape, lambda *i: data(*i) + 1, name="add_one")

# 2. 调度（schedule）：决定如何切分到 Cube/Vector/UB
s = tvm.create_schedule([out.op])
# ... tiling、bind 到 UB/L1 ...

# 3. 编译生成 NPU 二进制
with tvm.target.cce():
    build(s, [data, out], "add_one.o", "add_one.json")
```

**infra 要点**：算子开发最关键的不是"算对"，是**调度（schedule）**——把数据块大小对齐 UB、让 Cube 和 Vector 流水重叠。这和 GPU 上 Triton 的 tiling 思路一致。

## 6. ATC：模型转换（训练→部署的桥梁）

ATC（Ascend Tensor Compiler）把训练框架的模型转成 **OM（Offline Model）** 格式，供推理引擎加载。

```bash
# 基本转换（PyTorch → OM）
atc --model=model.onnx \
    --framework=5 \
    --output=model \
    --input_shape="input:1,3,224,224" \
    --soc_version=Ascend910B \
    --precision_mode=force_fp16
```

参数要点：
- `--soc_version`：必须匹配硬件（如 `Ascend910B`），否则装不对算子
- `--precision_mode`：fp16/bf16/fp32 选择
- `--framework`：5=ONNX，3=MindSpore，等

> ATC 在**推理部署**章节会深入（[04](04_inference_deployment.md)）。这里先知道它的位置：CANN 链路的"离线编译"出口。

## 7. 本章验收

- [ ] 能画 CANN 分层图，并说清 GE / 算子库 / AscendCL / ATC 各干什么
- [ ] 解释"一个 PyTorch 算子 → NPU 执行"中间的图编译与融合
- [ ] 写得出 AscendCL 最小推理骨架，并与 CUDA Runtime 对照
- [ ] 知道算子缺失时的三类解法，明白 "fallback to CPU" 为何是性能黑洞
- [ ] 跑过一次 ATC 转换（哪怕最小的 ONNX）

## 参考

- 官方：CANN 学习中心（cann-learning-hub）、AscendCL 开发指南、TBE 算子开发指南（见 [references.md](references.md)）
- 搜索结果：《CANN 学习路线》（1-2 周入门 API，2-4 周算子与优化）可作为节奏参考
