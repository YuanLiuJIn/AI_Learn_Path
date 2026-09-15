import torch
import time

# 指定 Apple Silicon GPU
device = torch.device("mps")

# 创建极大的张量 (例如: 1.5 GB 的 float32 张量)，以彻底击穿 SLC 缓存
# 400,000,000 * 4 bytes ≈ 1.6 GB
size = 400_000_000 
a = torch.randn(size, dtype=torch.float32, device=device)
b = torch.randn(size, dtype=torch.float32, device=device)

# 预热 GPU (消除上下文初始化的开销)
for _ in range(5):
    c = a + b
torch.mps.synchronize()

print("开始内存带宽极限压测...")
iterations = 50
start_time = time.time()

# 执行高频的 Element-wise 操作
for _ in range(iterations):
    c = a + b
    # 强制 MPS 队列立即执行并等待完成
    torch.mps.synchronize() 

end_time = time.time()

# 数学推导与统计
# 每次循环：读取 a (1.6GB), 读取 b (1.6GB), 写入 c (1.6GB)，共计 4.8 GB 物理 I/O
bytes_per_iteration = size * 4 * 3 
total_bytes = bytes_per_iteration * iterations
duration = end_time - start_time

# 带宽公式：总字节数 / 时间 / 10^9 (转换为 GB/s)
bandwidth_gbs = (total_bytes / duration) / 1e9

print(f"张量操作耗时: {duration:.3f} 秒")
print(f"应用层测算有效带宽: {bandwidth_gbs:.2f} GB/s")