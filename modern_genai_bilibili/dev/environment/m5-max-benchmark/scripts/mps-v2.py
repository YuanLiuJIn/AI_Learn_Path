import time
import torch


def gib(byte_count: int) -> float:
    return byte_count / (1024 ** 3)


if not torch.backends.mps.is_available():
    raise SystemExit("MPS is not available on this machine.")


device = torch.device("mps")
dtype = torch.float32
bytes_per_element = torch.tensor([], dtype=dtype).element_size()

# Use multiple large buffer triplets to reduce temporal locality between iterations.
chunk_elements = 64_000_000
bytes_per_triplet = chunk_elements * bytes_per_element * 3
min_buffer_triplets = 4
max_working_set_bytes = 12 * 1024 ** 3
recommended_max_memory = torch.mps.recommended_max_memory()
target_working_set_bytes = min(int(recommended_max_memory * 0.25), max_working_set_bytes)
buffer_triplets = max(min_buffer_triplets, target_working_set_bytes // bytes_per_triplet)
working_set_bytes = buffer_triplets * bytes_per_triplet

print("开始更接近真实外部内存带宽的流式压测...")
print(f"recommended_max_memory: {gib(recommended_max_memory):.2f} GiB")
print(f"working_set_size: {gib(working_set_bytes):.2f} GiB")
print(f"buffer_triplets: {buffer_triplets}")

inputs_a = [torch.randn(chunk_elements, dtype=dtype, device=device) for _ in range(buffer_triplets)]
inputs_b = [torch.randn(chunk_elements, dtype=dtype, device=device) for _ in range(buffer_triplets)]
outputs = [torch.empty(chunk_elements, dtype=dtype, device=device) for _ in range(buffer_triplets)]

# Warm up kernels and force initial page population before timing.
for index in range(buffer_triplets):
    torch.add(inputs_a[index], inputs_b[index], out=outputs[index])
torch.mps.synchronize()

iterations = buffer_triplets * 8
start_time = time.perf_counter()

for index in range(iterations):
    slot = index % buffer_triplets
    torch.add(inputs_a[slot], inputs_b[slot], out=outputs[slot])

torch.mps.synchronize()
end_time = time.perf_counter()

duration = end_time - start_time
total_bytes = bytes_per_triplet * iterations
bandwidth_gbs = (total_bytes / duration) / 1e9
avg_ms_per_iteration = duration * 1000 / iterations

print(f"iterations: {iterations}")
print(f"total_streamed_bytes: {gib(total_bytes):.2f} GiB")
print(f"总耗时: {duration:.3f} 秒")
print(f"平均每轮: {avg_ms_per_iteration:.3f} ms")
print(f"更接近外部内存的有效带宽: {bandwidth_gbs:.2f} GB/s")