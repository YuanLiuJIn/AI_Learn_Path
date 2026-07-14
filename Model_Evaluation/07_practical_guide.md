# 07. 动手实践：跑评测 + 设计自定义评测

> 目标：学会用 lm-eval-harness 跑标准评测，以及设计自己的评测任务。

---

## 1. 环境搭建

```bash
pip install lm-eval
pip install transformers torch  # 如果需要本地模型推理
```

---

## 2. 跑第一个标准评测

```python
# 评测本地 HuggingFace 模型在 MMLU 上的表现
import lm_eval
from lm_eval.models.huggingface import HFLM

model = HFLM(pretrained="Qwen/Qwen2.5-7B-Instruct")

results = lm_eval.simple_evaluate(
    model=model,
    tasks=["mmlu"],                  # 评测任务
    num_fewshot=5,                    # few-shot 示例数
    batch_size="auto",
)
print(results["results"]["mmlu"]["acc,none"])
```

```bash
# 或者用命令行
lm_eval --model hf \
    --model_args pretrained=Qwen/Qwen2.5-7B-Instruct,dtype=bfloat16 \
    --tasks mmlu,gsm8k,hellaswag \
    --num_fewshot 5 \
    --batch_size auto \
    --output_path ./eval_results/
```

---

## 3. 跑多个评测生成能力剖面

```python
TASKS = [
    "mmlu",           # 知识理解
    "gsm8k",          # 数学推理
    "hellaswag",      # 常识推理
    "truthfulqa_mc2", # 真实性
    "winogrande",     # 常识 + 歧义消解
]

results = lm_eval.simple_evaluate(
    model=model,
    tasks=TASKS,
    num_fewshot=5,
    batch_size="auto",
)

# 生成能力剖面
for task in TASKS:
    acc = results["results"][task].get("acc,none", "N/A")
    print(f"{task}: {acc}")
```

---

## 4. 设计自己的评测任务

### 场景：评测模型的地理知识水平

```json
// geo_eval.json
[
  {
    "question": "世界上最长的河流是哪一条？",
    "A": "亚马孙河",
    "B": "尼罗河",
    "C": "长江",
    "D": "密西西比河",
    "answer": "B"
  },
  {
    "question": "珠穆朗玛峰位于哪个国家边境？",
    "A": "中国和印度",
    "B": "中国和尼泊尔",
    "C": "印度和尼泊尔",
    "D": "中国和巴基斯坦",
    "answer": "B"
  }
]
```

```yaml
# geo_eval.yaml
task: geo_eval
dataset_path: json
dataset_kwargs:
  data_files: ./geo_eval.json
output_type: multiple_choice
doc_to_text: "{{question}}\nA. {{A}}\nB. {{B}}\nC. {{C}}\nD. {{D}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
doc_to_target: "{{answer}}"
metric_list:
  - metric: acc
```

```bash
lm_eval --model hf \
    --model_args pretrained=Qwen/Qwen2.5-7B-Instruct \
    --tasks geo_eval.yaml \
    --batch_size auto
```

---

## 5. 评测你的 GeoInfoAgent

```python
class GeoInfoAgentEval:
    """评测 GeoInfoAgent 的数据采集准确率"""
    
    def __init__(self, agent):
        self.agent = agent
        self.test_cases = self.load_test_cases()
    
    def evaluate(self):
        results = {"passed": 0, "failed": 0, "partial": 0}
        
        for case in self.test_cases:
            result = self.agent.execute(case["query"])
            
            # 评测：回答中的数据和预期是否一致
            score = self.score_result(result, case["expected"])
            
            if score >= 1.0:
                results["passed"] += 1
            elif score >= 0.5:
                results["partial"] += 1
            else:
                results["failed"] += 1
        
        accuracy = results["passed"] / len(self.test_cases)
        print(f"Accuracy: {accuracy:.1%}")
        return accuracy
    
    def load_test_cases(self):
        return [
            {
                "query": "北京 2026-07-01 降水",
                "expected": {"city": "北京", "date": "2026-07-01", "metric": "降水"}
            },
        ]
```

---

## 6. 一句话总结

> 用 lm-eval-harness 跑标准评测，用 YAML 配置自定义评测，用结构化测试用例评测你的 Agent。关键是：统一框架 + 统一配置 → 分数可比。
