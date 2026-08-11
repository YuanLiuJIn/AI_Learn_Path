#!/bin/bash
# Search-R1 复刻 · GRPO 启动脚本（Qwen2.5-14B / 4×H200）
# 用法：在 Search-R1 仓库根目录，conda activate searchr1 后执行
#   export CUDA_VISIBLE_DEVICES=0,1,2,3
#   bash scripts/run_grpo.sh
# 说明：本脚本的字段以 Search-R1 仓库 train_grpo.sh 为权威；
#       下面给出"标准 veRL 入口 + 本脚手架配置覆盖"的写法，按需对齐你实际版本。

set -x
export CUDA_VISIBLE_DEVICES=0,1,2,3
export PYTHONUNBUFFERED=1

# 若用 veRL 集成版（推荐）：把 Search-R1 作为 plugin 加载
# 若用 Search-R1 自带 veRL fork：直接 python3 -m verl.trainer.main_ppo ...
python3 -m verl.trainer.main_ppo \
    data.train_files=/data/searchr1/nq_train.parquet \
    data.val_files=/data/searchr1/nq_test.parquet \
    data.train_batch_size=128 \
    data.max_prompt_length=2048 \
    data.max_response_length=4096 \
    data.filter_overlong_prompts=True \
    actor_rollout_ref.model.path=Qwen/Qwen2.5-14B \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=64 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.n=5 \
    actor_rollout_ref.rollout.enable_search=True \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=2 \
    algorithm.adv_estimator=grpo \
    algorithm.kl_ctrl.kl_coef=0.001 \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.total_epochs=3 \
    trainer.save_freq=50 \
    trainer.test_freq=20 \
    trainer.save_checkpoint_path=/data/ckpt/search_r1_14b \
    trainer.logger=console \
    trainer.project_name=search_r1_14b \
    trainer.experiment_name=qwen25-14b-grpo-4xh200 \
    2>&1 | tee search_r1_grpo.log
