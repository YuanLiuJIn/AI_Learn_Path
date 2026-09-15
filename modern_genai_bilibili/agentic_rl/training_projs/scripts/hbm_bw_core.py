"""Minimal single-GPU HBM copy and stream-add bandwidth demo."""

import os

import torch


GPU = int(os.environ.get("GPU", "0"))
NUM_ELEMENTS = 256 * 1024 * 1024
WARMUP = 5
ITERS = 30

device = f"cuda:{GPU}"
torch.cuda.set_device(GPU)

x = torch.empty(NUM_ELEMENTS, dtype=torch.float32, device=device)
y = torch.empty_like(x)
z = torch.empty_like(x)

x.fill_(1.0)
y.fill_(2.0)
z.zero_()

tensor_bytes = x.numel() * x.element_size()


def measure_seconds(operation):
    for _ in range(WARMUP):
        operation()
    torch.cuda.synchronize()

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)

    start.record()
    for _ in range(ITERS):
        operation()
    end.record()
    end.synchronize()

    return start.elapsed_time(end) / 1000.0


# z = x: read x once and write z once -> 2 * tensor_bytes of HBM traffic.
copy_seconds = measure_seconds(lambda: z.copy_(x))
copy_payload_gbps = tensor_bytes * ITERS / copy_seconds / 1e9
copy_hbm_gbps = 2 * copy_payload_gbps

# z = x + y: read x and y, then write z -> 3 * tensor_bytes of HBM traffic.
add_seconds = measure_seconds(lambda: torch.add(x, y, out=z))
add_hbm_gbps = 3 * tensor_bytes * ITERS / add_seconds / 1e9

print(f"GPU{GPU}: {torch.cuda.get_device_name(GPU)}")
print(f"Local-copy payload: {copy_payload_gbps:.2f} GB/s")
print(f"Local-copy HBM read+write: {copy_hbm_gbps:.2f} GB/s")
print(f"Stream-add HBM 2-read+1-write: {add_hbm_gbps:.2f} GB/s")