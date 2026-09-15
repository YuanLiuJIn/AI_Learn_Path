import argparse
import gc
import os
import subprocess
import time

import torch
import torch.distributed as dist
from torch.distributed.fsdp import CPUOffload
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy
from transformers import GPT2Config, GPT2LMHeadModel

# Keep the original large config so memory contrast is obvious.
LARGE_CONFIG = GPT2Config(n_layer=12, n_embd=2048, n_head=16, vocab_size=50257)


def _str_to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def get_mem(device: torch.device) -> float:
    return torch.cuda.memory_allocated(device) / 1024**2


def get_peak(device: torch.device) -> float:
    return torch.cuda.max_memory_allocated(device) / 1024**2


def build_fsdp_kwargs(use_cpu_offload: bool, device: torch.device) -> dict:
    kwargs = {
        "cpu_offload": CPUOffload(offload_params=use_cpu_offload),
        "sharding_strategy": ShardingStrategy.FULL_SHARD,
    }
    # Passing device_id forces GPU-side init; that hides offload effect in this demo.
    if not use_cpu_offload:
        kwargs["device_id"] = device
    return kwargs


def is_torchrun_worker() -> bool:
    return all(k in os.environ for k in ("RANK", "WORLD_SIZE", "LOCAL_RANK"))


def run_distributed_scenario(use_cpu_offload: bool, warmup: int, iters: int) -> None:
    rank = int(os.environ["RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    local_rank = int(os.environ["LOCAL_RANK"])

    torch.cuda.set_device(local_rank)
    device = torch.device(f"cuda:{local_rank}")
    dist.init_process_group(backend="nccl", device_id=device)

    model = None
    fsdp_model = None
    output = None

    try:
        if world_size < 2:
            raise RuntimeError(
                "WORLD_SIZE 必须 >= 2。单卡会退化到 NO_SHARD，CPU offload 对比会失真。"
            )

        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
        dist.barrier()

        if rank == 0:
            print(f"\n{'=' * 20} 测试场景: CPU Offload = {use_cpu_offload} {'=' * 20}")
            print(
                f"[-] World Size: {world_size}; 可见设备映射: {os.environ.get('CUDA_VISIBLE_DEVICES', '(all)')}"
            )

        baseline = get_mem(device)
        if rank == 0:
            print(f"[-] 初始底噪显存 (rank0): {baseline:.2f} MB")
            print("[-] 创建模型 (默认在 CPU)...")

        model = GPT2LMHeadModel(LARGE_CONFIG)

        if not use_cpu_offload:
            model = model.to(device)
            if rank == 0:
                print("[-] (常规模式) 手动将模型移动到 GPU")

        before_wrap = get_mem(device)
        if rank == 0:
            print(f"[-] FSDP 包装前显存 (rank0): {before_wrap:.2f} MB")

        fsdp_model = FSDP(model, **build_fsdp_kwargs(use_cpu_offload, device))
        dist.barrier()

        after_wrap = get_mem(device)
        param_device = str(next(fsdp_model.parameters()).device)

        # Collect max value across ranks to represent worst-case memory footprint.
        wrap_stats = torch.tensor([after_wrap], device=device)
        dist.reduce(wrap_stats, dst=0, op=dist.ReduceOp.MAX)

        if rank == 0:
            print(f"[-] FSDP 包装后静态显存 (跨 rank 最大值): {wrap_stats.item():.2f} MB")
            print(f"[-] rank0 参数设备: {param_device}")

        fsdp_model.eval()
        input_ids = torch.randint(0, LARGE_CONFIG.vocab_size, (1, 10), device=device)

        # Warmup to avoid measuring startup artifacts.
        with torch.no_grad():
            for _ in range(max(0, warmup)):
                output = fsdp_model(input_ids)

        dist.barrier()
        torch.cuda.synchronize(device)
        torch.cuda.reset_peak_memory_stats(device)

        start = time.perf_counter()
        with torch.no_grad():
            for _ in range(max(1, iters)):
                output = fsdp_model(input_ids)
        torch.cuda.synchronize(device)
        elapsed_ms = (time.perf_counter() - start) * 1000 / max(1, iters)

        peak = get_peak(device)
        end_mem = get_mem(device)
        step_stats = torch.tensor([peak, end_mem, elapsed_ms], device=device)
        dist.reduce(step_stats, dst=0, op=dist.ReduceOp.MAX)

        if rank == 0:
            print(f"[-] Forward 峰值显存 (跨 rank 最大值): {step_stats[0].item():.2f} MB")
            print(f"[-] Forward 结束显存 (跨 rank 最大值): {step_stats[1].item():.2f} MB")
            print(f"[-] 平均单步时延 (跨 rank 最大值): {step_stats[2].item():.2f} ms")
            if use_cpu_offload:
                print("   (CPU offload 预期: 静态显存更低，但时延通常更高)")

    finally:
        del output, fsdp_model, model
        gc.collect()
        torch.cuda.empty_cache()
        if dist.is_initialized():
            dist.destroy_process_group()


def launch_with_torchrun(use_cpu_offload: bool, gpus: str, warmup: int, iters: int) -> None:
    gpu_list = [x.strip() for x in gpus.split(",") if x.strip()]
    if len(gpu_list) < 2:
        raise ValueError("至少需要 2 张 GPU 才能做 FULL_SHARD + CPU offload 对比")

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = ",".join(gpu_list)

    cmd = [
        "torchrun",
        "--standalone",
        "--nproc_per_node",
        str(len(gpu_list)),
        __file__,
        "--cpu-offload",
        str(use_cpu_offload).lower(),
        "--warmup",
        str(warmup),
        "--iters",
        str(iters),
    ]

    print(f"\n[launcher] CUDA_VISIBLE_DEVICES={env['CUDA_VISIBLE_DEVICES']} {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-offload", choices=["true", "false"], default=None)
    parser.add_argument("--gpus", default="1,2", help="仅在 launcher 模式有效，如: 1,2")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--iters", type=int, default=5)
    args = parser.parse_args()

    if is_torchrun_worker():
        if args.cpu_offload is None:
            raise ValueError("torchrun worker 模式必须显式传 --cpu-offload true/false")
        run_distributed_scenario(_str_to_bool(args.cpu_offload), args.warmup, args.iters)
        return

    # Launcher mode: run each scenario in a fresh process for clean memory comparison.
    launch_with_torchrun(use_cpu_offload=True, gpus=args.gpus, warmup=args.warmup, iters=args.iters)
    launch_with_torchrun(use_cpu_offload=False, gpus=args.gpus, warmup=args.warmup, iters=args.iters)


if __name__ == "__main__":
    main()
