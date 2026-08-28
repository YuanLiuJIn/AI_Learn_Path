#!/usr/bin/env bash
# Search-R1 · GRPO 启动脚本（Qwen2.5-14B / 4×H200）
# REWARD_VARIANT 可选：outcome / outcome_efficiency / outcome_efficiency_prm

set -euo pipefail
set -x

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SEARCH_R1_PROJECT_ROOT="$PROJECT_ROOT"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
export PYTHONUNBUFFERED=1
export REWARD_VARIANT="${REWARD_VARIANT:-outcome}"
export REWARD_CONFIG_PATH="${REWARD_CONFIG_PATH:-$PROJECT_ROOT/configs/reward_ablation.json}"

case "$REWARD_VARIANT" in
  outcome) REWARD_FUNCTION=reward_outcome ;;
  outcome_efficiency) REWARD_FUNCTION=reward_outcome_efficiency ;;
  outcome_efficiency_prm) REWARD_FUNCTION=reward_outcome_efficiency_prm ;;
  *) echo "Unsupported REWARD_VARIANT: $REWARD_VARIANT" >&2; exit 2 ;;
esac

if [[ "$REWARD_VARIANT" == "outcome_efficiency_prm" && -z "${PRM_ENDPOINT:-}" ]]; then
  echo "PRM_ENDPOINT is required for the PRM ablation." >&2
  exit 2
fi

MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-14B}"
TRAIN_FILE="${TRAIN_FILE:-/data/searchr1/nq_train.parquet}"
VAL_FILE="${VAL_FILE:-/data/searchr1/nq_test.parquet}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-/data/ckpt/search_r1_14b/$REWARD_VARIANT}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/logs}"
mkdir -p "$LOG_DIR" "$CHECKPOINT_DIR"

# 使用支持 custom_reward_function 的 veRL；多轮检索插件需按实际 Search-R1 版本加载。
python3 -m verl.trainer.main_ppo \
    data.train_files="$TRAIN_FILE" \
    data.val_files="$VAL_FILE" \
    data.train_batch_size=128 \
    data.max_prompt_length=2048 \
    data.max_response_length=4096 \
    data.filter_overlong_prompts=True \
    actor_rollout_ref.model.path="$MODEL_PATH" \
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
    custom_reward_function.path="$PROJECT_ROOT/src/reward.py" \
    custom_reward_function.name="$REWARD_FUNCTION" \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.total_epochs=3 \
    trainer.save_freq=50 \
    trainer.test_freq=20 \
    trainer.save_checkpoint_path="$CHECKPOINT_DIR" \
    trainer.logger=console \
    trainer.project_name=search_r1_14b \
    trainer.experiment_name="qwen25-14b-grpo-$REWARD_VARIANT" \
    2>&1 | tee "$LOG_DIR/$REWARD_VARIANT.log"
