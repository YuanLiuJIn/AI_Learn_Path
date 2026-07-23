# 多模态 / VLM 训练框架

> VLM（视觉语言模型）= 冻结的视觉编码器（ViT/CLIP）+ 投影层 Projector + LLM。
> 训练时通常：**Stage 1 只训 Projector 对齐视觉到词空间；Stage 2 解冻 LLM 联合训**。
> 这层和你 `多模态检索/` 专题直接打通：让模型"看懂"图片/截图再生成内容。

---

## 1. LLaVA（学术范式开创者）

### 特点

```text
- 2023 提出"视觉指令微调"范式，是所有 VLM 的祖师爷
- LLaVA-1.5 / NeXT / OneVision 演进，两阶段训练标准
- 代码必读：想真正理解 VLM 怎么训，从这里开始
- 适合：学术研究、想从源码理解 VLM
```

### 安装

```bash
git clone https://github.com/haotian-liu/LLaVA
cd LLaVA
pip install -e .
# 额外：需要 flash-attn、clip 等
```

### 最小可运行示例（两阶段训练）

```bash
# Stage 1：只训 Projector（冻结 ViT + LLM）
python llava/train.py \
    --model_name_or_path meta-llama/Llama-2-7b-hf \
    --vision_tower openai/clip-vit-large-patch14-336 \
    --tune_mm_mlp_adapter True \
    --mm_projector_type mlp2x_gelu \
    --data_path liuhaotian/LLaVA-Instruct-80K \
    --output_dir ./checkpoints/llava-stage1

# Stage 2：解冻 LLM 联合训
python llava/train.py \
    --model_name_or_path meta-llama/Llama-2-7b-hf \
    --vision_tower openai/clip-vit-large-patch14-336 \
    --tune_mm_mlp_adapter False \
    --trainable_flags "mm_mlp_adapter,llm" \
    --data_path liuhaotian/LLaVA-Instruct-80K \
    --output_dir ./checkpoints/llava-stage2
```

---

## 2. Qwen-VL / Qwen2.5-VL（官方强多模态）

### 特点

```text
- 阿里官方，原生多模态（图文/视频）
- 训练脚本开源，和你已有的 Qwen SFT 经验无缝衔接
- 适合：想基于 Qwen 做"看图生成测试判断"的最顺路线
```

### 安装

```bash
pip install qwen-vl-utils transformers
# 训练用 LLaMA-Factory / ms-swift 更省事（见下）
```

### 最小可运行示例（用 ms-swift 训 VLM）

```bash
# 直接复用 ms-swift，一行把 Qwen-VL 接成可训练
swift sft \
    --model Qwen/Qwen2.5-VL-7B-Instruct \
    --dataset AI-ModelScope/LaTeX_OCR \
    --train_type lora \
    --lora_rank 16
```

Python 推理（验证训出来的模型）：

```python
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

model = Qwen2_5_VLForConditionalGeneration.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")

messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": "ue_screenshot.png"},
        {"type": "text", "text": "这个按钮为什么点不了？"},
    ],
}]
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
images, videos = process_vision_info(messages)
inputs = processor(text=text, images=images, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=256)
print(processor.decode(out[0], skip_special_tokens=True))
```

---

## 3. InternVL（强视觉编码器）

### 特点

```text
- 上海 AI Lab，视觉编码器 ViT 很强，支持超大分辨率
- 训练代码完整，适合对视觉感知要求高的任务
- 适合：多模态研究、精细视觉理解
```

### 安装与示例

```bash
git clone https://github.com/OpenGVLab/InternVL
cd InternVL
pip install -e .
# 训练参考 internvl_chat/ 下的 shell 脚本
```

---

## 4. 用通用框架训 VLM（最省事）

其实多数时候不用直接用 LLaVA/Qwen 源码，而是用通用框架：

```bash
# LLaMA-Factory 训 VLM
llamafactory-cli train qwen2vl_lora_sft.yaml

# ms-swift 训 VLM（最推荐，一条命令）
swift sft --model Qwen/Qwen2.5-VL-7B-Instruct --dataset <多模态数据集>
```

---

## 5. 怎么选

| 维度 | LLaVA | Qwen-VL | InternVL | 通用框架 |
|---|---|---|---|---|
| 定位 | 学术范式 | 官方模型 | 强视觉 | 训 VLM 的便捷入口 |
| 上手 | 中 | 易（接 Qwen） | 中 | 最易 |
| 你用得到 | 学原理 | 主力模型 | 研究 | 实际训练 |

---

## 一句话总结

> VLM 训练 = 冻结 ViT + 训 Projector + 再联合训 LLM 的两阶段范式。
> 想懂原理读 **LLaVA** 源码，想快速出模型用 **ms-swift / LLaMA-Factory** 训 Qwen2.5-VL——
> 这正好把你"多模态检索"专题和 UE5 测试 Agent（看截图+日志生成判断）串起来。
