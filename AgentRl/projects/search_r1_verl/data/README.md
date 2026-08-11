# 数据准备 · Search-R1 复刻

> 目标：得到"可验证答案"的 QA 数据，供 RLVR 奖励（对应 `05_reward_design.md` 的 Rule/Outcome）。

## 1. 官方路径（NQ + Wikipedia + e5 检索器）

```bash
cd Search-R1
save_path=/data/searchr1
python scripts/download.py --save_path $save_path     # 下载 e5 索引 + wiki 语料
cat $save_path/part_* > $save_path/e5_Flat.index
gzip -d $save_path/wiki-18.jsonl.gz

python scripts/data_process/nq_search.py               # 处理成训练 parquet

# 另开 retriever 环境启动检索服务
conda activate retriever && bash retrieval_launch.sh    # http://127.0.0.1:8000/retrieve
```

## 2. 每条样本格式（必须这样，奖励函数才能算分）

```python
{
  "data_source": "nq",
  "prompt": [{"role": "user", "content": "<你的问题>"}],
  "ability": "fact-reasoning",
  "reward_model": {"style": "rule", "ground_truth": "<标准答案>"},
  "extra_info": {"split": "train", "index": 0}
}
```

- `reward_model.style="rule"` → 走 RLVR 规则奖励（零 RM，最稳）。
- `ground_truth` 用于精确匹配（见 `src/reward.py`）。

## 3. 用自己的 QA 数据集

只要满足上述字段即可。处理脚本参考 `Search-R1/scripts/data_process/nq_search.py`。
常见来源：HotpotQA（多跳）、TriviaQA、2WikiMultihopQA。语料换成你自己的 jsonl：

```json
{"id": "0", "contents": "\"Evan Morris\"\nEvan L. Morris (...) was a lobbyist for Genentech..."}
```

## 4. 检索服务替代方案

| 搜索引擎 | 配置 | 说明 |
|---|---|---|
| 本地稀疏 BM25 | `search_r1/search/build_index.sh` | 无需联网，最快 |
| 本地稠密 e5 + ANN | 官方默认 | 需下载索引 |
| 在线 API（Google/Bing/Brave） | 见 Search-R1 "Use your own search engine" | 真实联网搜索 |

## 5. 数据量建议（4×H200, 14B）

- 起步：NQ train ~79k 题，先抽样 5k~10k 跑通流程，再全量。
- `train_batch_size=128`、`rollout.n=5` → 每步约 640 条轨迹，4 卡可接受。
