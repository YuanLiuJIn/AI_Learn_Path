# 05. 工业化评测框架

> 目标：掌握三大主流评测框架的使用，能自己跑评测和设计自定义评测。

---

## 1. lm-evaluation-harness（最常用）

### 简介

```text
维护方：EleutherAI
定位：标准化、可复现的 LLM 评测框架
支持：60+ benchmarks、多模型后端、本地/云端

核心价值：
  同一个框架、同一个评测 → 分数完全可比
  不再各家自己实现，导致"同样 MMLU 分不可比"
```

### 安装与基础使用

```bash
pip install lm-eval
```

```python
# 跑一次 MMLU 评测
lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-3-8b \
    --tasks mmlu \
    --batch_size auto
```

```text
支持的模型后端：
  - HuggingFace (本地模型)
  - OpenAI API (GPT 系列)
  - vLLM (高性能推理)
  - Anthropic API (Claude 系列)

支持的任务：
  mmlu, gsm8k, hellaswag, truthfulqa, human_eval...
  共 60+ 个标准评测任务
```

### 自定义评测任务

```yaml
# my_eval.yaml
task: my_custom_eval
dataset_path: json
dataset_kwargs:
  data_files: ./my_questions.json
output_type: multiple_choice
doc_to_text: "{{question}}\nA. {{A}}\nB. {{B}}\nC. {{C}}\nD. {{D}}\nAnswer:"
doc_to_choice: ["A", "B", "C", "D"]
doc_to_target: "{{answer}}"
metric_list:
  - metric: acc
```

```bash
lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-3-8b \
    --tasks my_eval.yaml \
    --batch_size auto
```

---

## 2. HELM（Stanford 全景评测）

### 简介

```text
维护方：Stanford CRFM
定位：全景式评测，不只"一个分数"

核心理念：
  不只给你一个总分
  给你一张"能力雷达图"：
    知识、推理、安全、公平、效率、毒害性...
  多个维度、多个场景、多个指标

  承认不完备性：不可能测完所有维度
  追求透明度：清晰说明"什么是没测的"
```

### 设计哲学

```text
HELM 的七大评测维度：

1. 准确性：知识问答正确率
2. 鲁棒性：对轻微输入变化是否稳定
3. 公平性：对不同群体表现是否一致
4. 效率：推理速度、资源消耗
5. 偏见：是否有种族/性别等偏见
6. 毒害性：是否生成有害内容
7. 校准度：置信度是否匹配实际准确率
```

---

## 3. OpenCompass（中文评测首选）

```text
维护方：上海AI实验室
定位：中文 LLM 评测最完整的框架

特点：
  支持 100+ 中文/英文评测集
  支持国产模型（Qwen、ChatGLM、DeepSeek 等）
  支持多模态评测
  有可视化排行榜
```

---

## 4. 三大框架对比

| | lm-eval-harness | HELM | OpenCompass |
|---|---|---|---|
| **定位** | 快速标准化 | 全景深度 | 中文全覆盖 |
| **Benchmark数** | 60+ | 50+ | 100+ |
| **多维度** | 否（主要是准确率） | 是（7维度） | 部分 |
| **自定义难度** | 低（YAML配置） | 中 | 低 |
| **中文支持** | 中 | 弱 | 强 |
| **最适合** | 日常模型对比 | 深度能力分析 | 中文模型评测 |

---

## 5. 评测结果的可比性

```text
关键原则：同框架、同配置、同版本

错误做法：
  "模型 A 在 MMLU 上 85%"
  "模型 B 在 MMLU 上 82%"
  → 但它们用的不同框架、不同 prompt → 不可比！

正确做法：
  所有模型用同一个 lm-eval-harness 版本
  同一套 prompt 模板
  同一套 few-shot 示例
  → 分数才有可比性
```

---

## 6. 一句话总结

> lm-eval-harness 用于日常快速评测（60+ benchmarks），HELM 用于深度全景分析（7 维度），OpenCompass 用于中文模型评测（100+ 评测集）。评测可比性的前提是同框架、同配置、同版本。
