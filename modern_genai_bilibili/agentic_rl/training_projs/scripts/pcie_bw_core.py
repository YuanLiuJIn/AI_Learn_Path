"""Minimal PCIe H2D/D2H bandwidth demo.

Bind the process to CPUs local to the target GPU before pinned-memory allocation.
"""

import os

import torch


GPU = int(os.environ.get("GPU", "0"))
SIZE_MIB = 512
WARMUP = 5
ITERS = 50

num_bytes = SIZE_MIB * 1024**2
device = f"cuda:{GPU}"

torch.cuda.set_device(GPU)

# Pinned host memory allows the GPU copy engine to DMA over PCIe.
host_src = torch.empty(num_bytes, dtype=torch.uint8, pin_memory=True)
host_dst = torch.empty_like(host_src, pin_memory=True)
gpu_buffer = torch.empty(num_bytes, dtype=torch.uint8, device=device)

host_src.zero_()
gpu_buffer.zero_()


def measure_gbps(copy_operation):
    for _ in range(WARMUP):
        copy_operation()
    torch.cuda.synchronize()

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()
    for _ in range(ITERS):
        copy_operation()
    end.record()
    end.synchronize()

    seconds = start.elapsed_time(end) / 1000.0
    return num_bytes * ITERS / seconds / 1e9


# Host DRAM -> PCIe -> GPU HBM
h2d_gbps = measure_gbps(
    lambda: gpu_buffer.copy_(host_src, non_blocking=True)
)

# GPU HBM -> PCIe -> Host DRAM
d2h_gbps = measure_gbps(
    lambda: host_dst.copy_(gpu_buffer, non_blocking=True)
)

print(f"GPU{GPU}: {torch.cuda.get_device_name(GPU)}")
print(f"H2D payload: {h2d_gbps:.2f} GB/s")
print(f"D2H payload: {d2h_gbps:.2f} GB/s")