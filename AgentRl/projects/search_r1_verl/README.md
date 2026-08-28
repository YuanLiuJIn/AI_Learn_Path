# Search-R1 复刻与改进 · Agentic RL 实战项目

> 目标：在 **4×NVIDIA H200** 上，用 **veRL** 复刻 **Search-R1**，并完成「多目标 Reward 消融 + Agentic-Search 评测 + 训评闭环」。
> 模型：**Qwen2.5-14B**，算法：**GRPO（RLVR / 可插拔 PRM）**。
> 核心增量：对比 `outcome`、`outcome + 检索效率`、`outcome + 检索效率 + PRM` 三组训练，统一评估正确率、平均搜索轮次和工具调用合理率。
> 这是对 `AgentRl/` 笔记的全链路实战：多轮轨迹(03) + 多目标奖励(05) + GRPO(02) + veRL 框架(04) + 评测闭环。

---

## 0. 这个项目在练什么（对照你的笔记）

| 你笔记里的概念 | 在本项目里对应 | 出处 |
|---|---|---|
| 多轮 Agent / POMDP | LLM 反复 `思考→调搜索→看结果→再思考` | `03_multi_turn_agent_rl.md` §1 |
| 工具调用 Action Space | `<search>query</search>` 特殊 token | `03` §2 |
| RLVR / Rule / Outcome 奖励 | 答案精确匹配 + 格式奖励，零 RM | `05_reward_design.md` §2/§4 |
| GRPO（组内相对，省 Critic） | `algorithm.adv_estimator=grpo` | `02_rl_foundations.md` |
| 轨迹级 / 变长 episode | 每题多轮、长度不一，需过滤 | `03` §2.2 / `05` §6 |
| Re-tokenize 坑 | 搜索结果回填后需稳定分词 | `03` §4.1 |
| veRL 框架 | 训练主入口 `verl.trainer.main_ppo` | `04_rl_frameworks.md` |
| **GPU 分布式（JD 缺口）** | FSDP + vLLM TP + NCCL | 见本 README §3 |

---

## 1. 硬件落地映射（4×H200）

```text
单卡：H200 = 141GB HBM3e，~990 TFLOPS BF16，NVLink 4th-gen
4 卡合计：564GB HBM，卡间 NVLink 900GB/s

Qwen2.5-14B：权重 ~28GB(BF16)
  → 推理(rollout)：vLLM tensor_model_parallel_size=2  → 14GB/卡，富余
  → 训练(actor)：FSDP 跨 4 卡，优化器态(~0.5GB→14B×12B≈168GB) 4 卡分摊轻松
  → 全 4 卡 colocated（rollout 与 train 复用同批卡）即可

显存策略：rollout.gpu_memory_utilization=0.5，给训练留余量，避免 OOM
```

> 对比你 `升腾910b_infra/`：那儿是 Da Vinci + HCCL + torch_npu；这里是 Hopper + NCCL + torch(cu124)。
> **概念互通（并行/通信/吞吐），但栈不同**——这次正好练 GPU 主流分布式。

---

## 2. 环境与安装（Linux, CUDA 12.4）

```bash
# 2.1 克隆仓库（含其 veRL 依赖）
git clone https://github.com/PeterGriffinJin/Search-R1.git
cd Search-R1

# 2.2 建环境（H200 用 Python 3.11 + CUDA 12.4 轮子）
conda create -n searchr1 python=3.11 -y && conda activate searchr1
pip install torch==2.4.0 --index-url https://download.pytorch.org/whl/cu124
pip install vllm==0.6.3
pip install flash-attn --no-build-isolation
pip install -e .                       # 安装 Search-R1（含其 veRL fork）
pip install wandb datasets transformers accelerate pyserini

# 2.3 （可选）本地检索服务环境，另开一个 env
conda create -n retriever python=3.10 -y && conda activate retriever
conda install pytorch==2.4.0 pytorch-cuda=12.1 -c pytorch -c nvidia
pip install transformers datasets pyserini faiss-gpu uvicorn fastapi
```

> 版本敏感提示：vllm/veRL/Search-R1 三者版本耦合较紧。`vllm==0.6.3` + `torch==2.4.0` 是 Search-R1 官方验证组合；
> 若用更新版 veRL，请以其 `train_grpo.sh` 的字段为准，本脚手架 config 仅作模板。

---

## 3. 数据准备（RLVR 需要"可验证答案"的 QA）

Search-R1 官方用 **NQ / HotpotQA + Wikipedia 语料 + e5 检索器**。你也可换自己的 QA 数据集。

```bash
# 3.1 下载检索索引与语料（NQ 示例）
save_path=/data/searchr1
python scripts/download.py --save_path $save_path
cat $save_path/part_* > $save_path/e5_Flat.index
gzip -d $save_path/wiki-18.jsonl.gz

# 3.2 处理 NQ 为 RL 训练格式
python scripts/data_process/nq_search.py

# 3.3 启动本地检索服务（另开 retriever 环境）
conda activate retriever && bash retrieval_launch.sh
# 默认监听 http://127.0.0.1:8000/retrieve
```

数据格式（每条样本，对应你 `05` 的 Rule/Outcome）：
```python
{
  "data_source": "nq",
  "prompt": [{"role": "user", "content": "<question>"}],
  "ability": "fact-reasoning",
  "reward_model": {"style": "rule", "ground_truth": <answer>},
  "extra_info": {"split": "train", "index": 0}
}
```
详见 `data/README.md`。

---

## 4. 启动训练（4×H200, Qwen2.5-14B, GRPO）

`scripts/run_grpo.sh` 已通过 veRL 的 `custom_reward_function.path/name` 接入本项目奖励函数。先设置外部 Search-R1/veRL 环境和检索服务，再选择消融组：

```bash
cd /path/to/search_r1_verl
conda activate searchr1

# A：仅最终答案奖励
REWARD_VARIANT=outcome bash scripts/run_grpo.sh

# B：最终答案 + 检索效率惩罚
REWARD_VARIANT=outcome_efficiency bash scripts/run_grpo.sh

# C：最终答案 + 检索效率惩罚 + 真实 PRM
PRM_ENDPOINT=http://127.0.0.1:9000/score \
REWARD_VARIANT=outcome_efficiency_prm bash scripts/run_grpo.sh
```

模型、数据和输出目录可分别通过 `MODEL_PATH`、`TRAIN_FILE`、`VAL_FILE`、`CHECKPOINT_DIR` 覆盖。`scripts/run_reward_ablation.sh` 可顺序启动三组实验；未设置 `PRM_ENDPOINT` 时会跳过 C 组，防止把启发式分数冒充 PRM。

关键参数：

```text
actor_rollout_ref.model.path          = Qwen/Qwen2.5-14B
actor_rollout_ref.rollout.name        = vllm
actor_rollout_ref.rollout.tensor_model_parallel_size = 2
actor_rollout_ref.rollout.gpu_memory_utilization     = 0.5
actor_rollout_ref.rollout.n           = 5
algorithm.adv_estimator               = grpo
custom_reward_function.path           = src/reward.py
custom_reward_function.name           = reward_<消融组>
```

### Reward 定义

\[
R = w_oR_{outcome} - c_sN_{excess} - c_iN_{invalid} - c_dN_{duplicate} - c_bN_{overbudget} + w_pR_{PRM}
\]

- `outcome`：最终 `<answer>` 与一个可接受答案归一化精确匹配。
- `efficiency`：只惩罚超过免费额度的搜索、空/未闭合调用、重复查询和超预算调用，不无条件奖励“用了工具”。
- `PRM`：读取当前轨迹的真实过程分数。在线训练走 `PRM_ENDPOINT`；离线评测也可用 `process_scores`。
- 所有权重集中在 `configs/reward_ablation.json`，三组实验除了 Reward 之外应保持数据、模型、seed 和训练预算一致。

PRM 服务接收：

```json
{"data_source":"nq","trajectory":"...","steps":["..."],"ground_truth":{"target":"..."},"extra_info":{}}
```

返回 `{"scores":[0.7, 0.9]}` 或 `{"score":0.8}`。默认 fail-closed：服务不可用即终止 C 组，避免实验口径失真。

---

## 5. Agentic-Search 离线评测

输出文件格式见 `data/README.md`，可先用样例验证：

```bash
python scripts/evaluate.py \
  --input examples/eval_sample.jsonl \
  --variant outcome_efficiency \
  --reward-config configs/reward_ablation.json \
  --output-dir outputs/example
```

输出：

- `summary.json`：正确率、平均搜索轮次、工具调用合理率、指标覆盖率、格式通过率、重复/非法/超预算比例及各奖励分量。
- `details.csv`：逐样本明细，支持 bad case 归因。

工具调用合理率是以下**可审计分量的均值**：格式有效性、查询去重、预算遵循、搜索必要性对齐，以及可选的查询相关性。若样本没有搜索且缺少 `requires_search` 标签，该指标记为缺失而非满分，并由 `rationality_coverage` 披露覆盖率。

三组训练完成并分别导出轨迹后，生成消融表：

```bash
python scripts/compare_ablations.py \
  --run outcome=outputs/outcome.jsonl \
  --run outcome_efficiency=outputs/outcome_efficiency.jsonl \
  --run outcome_efficiency_prm=outputs/outcome_efficiency_prm.jsonl \
  --output-dir outputs/ablation
```

重点比较：**正确率是否保持或提升、平均搜索轮次是否下降、工具调用合理率是否提升**，而不是只比较训练 reward。

---

## 6. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| loss 不降 / reward 恒为 0 | 答案解析格式与 `<answer>` 不一致 | 先运行单元测试，再抽样检查 rollout 原文和 ground truth |
| 搜索次数下降但正确率也下降 | 检索成本过高 | 下调 `search_cost` 或提高 `free_search_calls`，看 Pareto 而非单指标 |
| 模型重复改写同一查询 | 没有重复惩罚或归一化不足 | 调整 `duplicate_search_penalty`，检查逐样本 `details.csv` |
| PRM 组启动即失败 | 未提供当前轨迹的过程分数 | 配置真实 `PRM_ENDPOINT`；不要用固定启发式分数代替 |
| 推理时搜索结果和训练对不上 | 回填后 Re-tokenize 不一致 | 固定检索结果模板与 tokenizer，检查状态掩码 |
| 训练 OOM | rollout 占满显存 | 降 `gpu_memory_utilization`，或调整 rollout TP/micro batch |
| 长尾样本拖慢 | 变长 episode | 开启过长轨迹过滤，并报告被过滤比例 |

---

## 7. 验收标准

```text
[ ] python -m unittest discover -s tests -v 全部通过
[ ] 三组 Reward 在同一批固定轨迹上的分量符合预期
[ ] A/B/C 三组保持模型、数据、seed、训练步数和采样参数一致
[ ] 每组导出独立测试轨迹，并生成 summary.json + details.csv
[ ] 消融表至少报告：accuracy / avg_search_turns / tool_call_rationality
[ ] 对重复搜索、错误搜索、无需搜索和答案正确但低效四类 bad case 完成归因
[ ] 只有接入真实 PRM 模型或真实逐步分数后，才对外声称完成 PRM 实验
```

---

## 8. 下一步

- 接入语义相关性评审器，替代人工填写 `search_relevance`。
- 对搜索成本系数做网格实验，绘制正确率—搜索成本 Pareto 曲线。
- 对 PRM 的 `mean/min/last` 聚合方式做消融，分析长轨迹信用分配。
- 换在线搜索或不同检索器，控制检索质量变量做交叉实验。

## 参考

- Search-R1 仓库：https://github.com/PeterGriffinJin/Search-R1
- 论文：arXiv:2503.09516（Search-R1），arXiv:2505.15117（实证）
- veRL：https://github.com/volcengine/verl
- 你的笔记：`AgentRl/02`(GRPO) `03`(多轮) `04`(veRL) `05`(RLVR) `docs/`(已下 PDF)
