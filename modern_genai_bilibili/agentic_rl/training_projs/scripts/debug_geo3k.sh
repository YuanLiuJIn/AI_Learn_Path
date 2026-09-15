#!/usr/bin/env bash
# =============================================================================
# geo3k GRPO 单卡断点调试 (self-contained) —— Qwen3.5-2B。
# 不依赖任何其他脚本 / 补丁;完整 main_ppo 调用就在下面。
#
#   ① Driver 断点(主流程 / 数据 / reward / advantage,最常用):
#        DEBUGPY=1 bash scripts/debug_geo3k.sh
#      → 卡在 0.0.0.0:5678 等 IDE。Cursor 里 Run&Debug 选
#        "verl driver — attach (in-container, 5678)" → F5,再在行号打红点。
#
#   ② Worker 断点(actor 前/反向、rollout、模型 forward):
#        先在 worker 代码插一行 breakpoint()(例:
#        verl/verl/workers/actor/dp_actor.py 的 update_policy),然后
#        bash scripts/debug_geo3k.sh
#      → 用 "Ray Distributed Debugger" 扩展 attach 到暂停的 task。
#
# 只跑 1 步、关验证、不存 ckpt、只打 console。GPU=N 选卡,变量按需覆盖。
# =============================================================================
set -Eeuo pipefail
cd /workspace/verl-train

# ---- 可调的就这几个 ----
MODEL_PATH=${MODEL_PATH:-/workspace/models/Qwen3.5-2B}
GPU=${GPU:-0}                 # 用哪张卡(nvidia-smi 看空闲)
DEBUGPY=${DEBUGPY:-0}         # 1 = driver 断点(debugpy 等 IDE)
PORT=${PORT:-5678}

export CUDA_VISIBLE_DEVICES=$GPU
export RAY_DEBUG=1                                   # worker 断点(Ray 分布式调试器)
export HYDRA_FULL_ERROR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
pip show debugpy >/dev/null 2>&1 || pip install -q debugpy

LAUNCH=(python3 -m verl.trainer.main_ppo)
if [ "$DEBUGPY" = 1 ]; then
  echo "[debug] debugpy 等 IDE attach → 0.0.0.0:$PORT  (Cursor: Run&Debug → attach 5678)"
  LAUNCH=(python3 -m debugpy --listen 0.0.0.0:"$PORT" --wait-for-client -m verl.trainer.main_ppo)
fi

# —— 2B 单卡:不 offload(全程 GPU 常驻,断点看到的就是 cuda 张量);小 token 预算省显存 ——
"${LAUNCH[@]}" \
  algorithm.adv_estimator=grpo algorithm.use_kl_in_reward=False \
  data.train_files=/workspace/verl-train/data/geo3k/train.parquet \
  data.val_files=/workspace/verl-train/data/geo3k/test.parquet \
  data.image_key=images data.train_batch_size=8 data.shuffle=False \
  data.max_prompt_length=1024 data.max_response_length=1024 \
  data.filter_overlong_prompts=True data.truncation=error data.return_raw_chat=True \
  reward.custom_reward_function.path=/workspace/verl-train/rewards/geo3k_think_reward.py \
  reward.custom_reward_function.name=compute_score \
  actor_rollout_ref.model.path="$MODEL_PATH" \
  actor_rollout_ref.model.use_remove_padding=True \
  actor_rollout_ref.model.use_fused_kernels=True \
  actor_rollout_ref.model.enable_gradient_checkpointing=True \
  +actor_rollout_ref.model.override_config.attn_implementation=flash_attention_2 \
  actor_rollout_ref.actor.strategy=fsdp2 actor_rollout_ref.actor.optim.lr=1e-6 \
  actor_rollout_ref.actor.ppo_mini_batch_size=4 \
  actor_rollout_ref.actor.use_dynamic_bsz=True \
  actor_rollout_ref.actor.ppo_max_token_len_per_gpu=4096 \
  actor_rollout_ref.actor.use_kl_loss=True actor_rollout_ref.actor.kl_loss_coef=0.01 \
  actor_rollout_ref.actor.kl_loss_type=low_var_kl actor_rollout_ref.actor.entropy_coeff=0 \
  actor_rollout_ref.actor.use_torch_compile=False \
  actor_rollout_ref.actor.fsdp_config.use_torch_compile=False \
  actor_rollout_ref.actor.fsdp_config.param_offload=False \
  actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
  actor_rollout_ref.actor.fsdp_config.fsdp_size=1 \
  actor_rollout_ref.actor.fsdp_config.ulysses_sequence_parallel_size=1 \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.3 \
  actor_rollout_ref.rollout.prompt_length=1024 actor_rollout_ref.rollout.response_length=1024 \
  actor_rollout_ref.rollout.max_model_len=2048 \
  actor_rollout_ref.rollout.max_num_batched_tokens=8192 \
  actor_rollout_ref.rollout.max_num_seqs=32 \
  actor_rollout_ref.rollout.enable_chunked_prefill=True \
  actor_rollout_ref.rollout.enable_prefix_caching=False \
  actor_rollout_ref.rollout.free_cache_engine=True \
  actor_rollout_ref.rollout.n=2 \
  actor_rollout_ref.rollout.log_prob_use_dynamic_bsz=True \
  actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=4096 \
  actor_rollout_ref.ref.strategy=fsdp2 \
  actor_rollout_ref.ref.log_prob_use_dynamic_bsz=True \
  actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=4096 \
  actor_rollout_ref.ref.fsdp_config.param_offload=False \
  actor_rollout_ref.ref.fsdp_config.use_torch_compile=False \
  actor_rollout_ref.ref.fsdp_config.ulysses_sequence_parallel_size=1 \
  trainer.logger='["console"]' \
  trainer.project_name=geo3k_debug trainer.experiment_name=debug_2b_1gpu \
  trainer.n_gpus_per_node=1 trainer.nnodes=1 \
  trainer.val_before_train=False trainer.save_freq=-1 trainer.test_freq=999 \
  trainer.total_epochs=1 trainer.total_training_steps=1 \
  trainer.resume_mode=disable trainer.use_v1=True trainer.device=cuda "$@"
