# Search-R1 复刻 · Agentic RL 实战脚手架

> 目标：在 **4×NVIDIA H200** 上，用 **veRL** 复刻 **Search-R1**（训练 LLM 学会"边推理边调搜索工具"的多轮 Agentic RL）。
> 模型：**Qwen2.5-14B**，算法：**GRPO（RLVR 奖励）**。
> 这是对你 `AgentRl/` 笔记的全链路实战：多轮轨迹(03) + RLVR 奖励(05) + GRPO(02) + veRL 框架(04)。
> 同时也是**补齐 JD 缺口**的练兵：GPU 分布式（NCCL/FSDP/vLLM），不是你升腾那套 HCCL。

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

用本仓库提供的 `scripts/run_grpo.sh`（已按 14B/4H200 调好），或见 `configs/grpo_qwen14b_4xh200.yaml`：

```bash
cd Search-R1
conda activate searchr1
export CUDA_VISIBLE_DEVICES=0,1,2,3
bash scripts/run_grpo.sh
```

关键参数（已在 `configs/` 给出，并在 `run_grpo.sh` 用命令行覆盖）：
```text
actor_rollout_ref.model.path          = Qwen/Qwen2.5-14B
actor_rollout_ref.rollout.name        = vllm
actor_rollout_ref.rollout.tensor_model_parallel_size = 2   # 14B → 14GB/卡
actor_rollout_ref.rollout.gpu_memory_utilization     = 0.5
actor_rollout_ref.rollout.n            = 5     # GRPO 组内样本数
algorithm.adv_estimator               = grpo   # 省 Critic，对应你 02
trainer.n_gpus_per_node               = 4
trainer.nnodes                        = 1
data.max_prompt_length                = 2048   # 搜索上下文较长
data.max_response_length              = 4096   # 多轮推理+检索
```

---

## 5. 你会亲手踩的坑（← 全是笔记里的考点）

| 现象 | 原因 | 对应笔记 / 处理 |
|---|---|---|
| loss 不降 / reward 恒为 0 | 答案解析正则不匹配 `<answer>` | `05` §4 Rule 奖励要和可验证格式对齐 |
| 训练 OOM | rollout 占满显存 | 降 `gpu_memory_utilization` 到 0.4，或 rollout TP=4 |
| 推理时搜索结果和训练对不上 | Re-tokenize（回填分词不一致） | `03` §4.1，确保 search 结果稳定分词 |
| 长尾样本拖慢 | 变长 episode | `03`：开启 `filter_overlong_prompts`，轨迹过滤 |
| 模型只输出不搜索 | 奖励没激励工具调用 | `05`：加"使用搜索"格式奖励 |
| 多卡通信慢 | NCCL 拓扑 | `04`：检查 `n_gpus_per_node` 与 NVLink |

---

## 6. 验收标准（跑通即达成）

```text
[ ] 环境点亮：4 卡 `nvidia-smi` 可见，vLLM 能加载 Qwen2.5-14B
[ ] 数据跑通：NQ 处理成 parquet，reward 函数能算分
[ ] 训练启动：GRPO 跑起来，wandb/console 看到 reward 曲线
[ ] 行为涌现：训练若干步后，模型学会插入 <search> 调用且答案准确率上升
[ ] 复盘：能对照 03/05 说出本项目的轨迹表示、奖励来源、信用分配点
```

---

## 7. 延伸（跑通后）

- 换 **在线搜索**（Google/Bing API）替代本地检索，见 Search-R1 "Use your own search engine"。
- 上 **Qwen2.5-32B**（TP=4 + ZeRO）验证分布式扩展。
- 接你 `升腾910b_infra/` 的并行概念，做"GPU vs NPU 分布式"对照笔记。
- 参考 `AgentRl/05_reward_design.md` 把 Rule 奖励升级为 AgentPRM 过程奖励。

## 参考

- Search-R1 仓库：https://github.com/PeterGriffinJin/Search-R1
- 论文：arXiv:2503.09516（Search-R1），arXiv:2505.15117（实证）
- veRL：https://github.com/volcengine/verl
- 你的笔记：`AgentRl/02`(GRPO) `03`(多轮) `04`(veRL) `05`(RLVR) `docs/`(已下 PDF)
