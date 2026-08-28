#!/usr/bin/env bash
# 顺序启动 outcome / outcome+efficiency / outcome+efficiency+PRM 三组实验。
# 每组训练耗时较长；PRM 组要求 PRM_ENDPOINT 已配置。

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_SCRIPT="$PROJECT_ROOT/scripts/run_grpo.sh"

for variant in outcome outcome_efficiency outcome_efficiency_prm; do
  if [[ "$variant" == "outcome_efficiency_prm" && -z "${PRM_ENDPOINT:-}" ]]; then
    echo "Skip $variant: set PRM_ENDPOINT to a process reward service first." >&2
    continue
  fi
  REWARD_VARIANT="$variant" bash "$RUN_SCRIPT"
done
