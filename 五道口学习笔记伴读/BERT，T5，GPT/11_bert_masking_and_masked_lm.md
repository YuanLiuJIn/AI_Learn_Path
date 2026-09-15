# 11 · masking 机制、BERT head 与 BertForMaskedLM

> **接 10**：10 讲清了 head 家族的"族谱"，其中 3.4 把 MLM 头（`transform` + `decoder`，且 decoder 与词嵌入 tied）先见了一次。
> 本篇把那条线**单独展开**：`[MASK]` 是怎么塞进去的、`labels` 与 `loss` 怎么对齐、"只算被 mask 的位置"到底是怎么实现的——也就是 BERT 预训练任务本身。
>
> **视频**：[动手写 BERT 系列] masking 机制、bert head 与 BertForMaskedLM `BV1Je4y1e7uF`（合集第 12 集，24:55，"动手写 bert"子系列收官篇）
> **配套 notebook**：`bilibili_vlogs/fine_tune/bert/tutorials/09_masked_lm.ipynb`（这次是**完整可跑的**，含 5 个 section：load / masking / forward & loss / from scratch / loss & translate）
>
> **一句话主旨**：MLM 预训练 = **把句子里的词挖掉几个，让模型根据上下文把它们填回来**；`BertForMaskedLM` 就是"把 30522 类的分类头接在每个词的最终向量上"，而 loss 只在**被挖空的位置**上算。

---

## 〇、30 秒直觉

一句话说清 MLM（Masked Language Modeling，掩码语言模型）：

```
输入：  The capital of France is [MASK] .
                          ↑
                    把"Paris"挖掉，换成一个占位符 [MASK]

模型：  只能看上下文（这里 [MASK] 左边、右边都能看，这是 BERT 的"双向"）
输出：  在 [MASK] 这个位置，从 30522 个词里挑一个 → 希望挑中 "paris"

loss：  只在这个 [MASK] 位置上算交叉熵；其它位置不算
```

**为什么这么设计？** 因为语言模型总得有个"监督信号"。GPT 用"预测下一个词"（只能看左边），BERT 想**同时看左右两边**——但"预测下一个词"这个任务天然不允许看右边。于是 BERT 换个玩法：**随机挖空，让模型填空**。要填对，它必须同时理解左边和右边，于是被迫学出双向的语义表示。

关键认知（也是本篇后面反复用到的）：

| | 说明 |
|---|---|
| **挖空的位置** | 叫 masked position，输入里是 `[MASK]` |
| **正确答案** | 来自**原始句子**（`labels` = 挖空前的 id） |
| **不算 loss 的位置** | 没被挖空的那些位置，用 `-100` 标记、被 `CrossEntropyLoss` 忽略 |
| **预测用哪个向量** | `[MASK]` 那个位置的**最终隐藏向量**（`last_hidden_state[mask_pos]`） |
| **分类头** | 一个 `Linear(768 → 30522)`，即 10 讲的 `cls.predictions.decoder` |

> 类比：把一句英文里的几个词涂黑，交给一个"看过海量文本"的人填。要是他填对了，说明他真懂这句话——而不是靠"上一个词的惯性"（那是 GPT 的玩法）。

---

## 一、先看 notebook 的 5 个 section

配套 notebook 结构清晰，本篇就**跟着它走**：

| section | 内容 | 本篇对应 |
|---|---|---|
| 1. model load and data preprocessing | 加载 `BertModel` / `BertForMaskedLM`，看那条加载警告 | §一 |
| 2. masking | **手写 masking**：造 mask、选位置、替换成 `[MASK]` | §二、§三 |
| 3. forward and calculate loss | `mlm(**inputs)` → `loss` / `logits` / `hidden_states` | §四、§五 |
| 4. from scratch | 手动走一遍 `mlm.cls(hidden_states[-1])`，和 `output.logits` 对齐 | §六 |
| 5. loss and translate | 手算 `CrossEntropyLoss`，argmax 解码看预测 | §六 6.1 / 6.2 |

**section 1 那条加载警告**（notebook 里真实输出）：

```text
Some weights of the model checkpoint at bert-base-uncased were not used
when initializing BertModel: ['cls.seq_relationship.bias', 'cls.predictions.bias',
'cls.predictions.transform.LayerNorm.bias', 'cls.seq_relationship.weight', ...]
Some weights of the model checkpoint at bert-base-uncased were not used
when initializing BertForMaskedLM: ['cls.seq_relationship.weight', 'cls.seq_relationship.bias']
```

**这正是 10 第四节讲的"族谱体检验报告"，这里给出了最干净的两个对照**：

- 装 `BertModel`：忽略**全部** `cls.predictions.*` + `cls.seq_relationship.*`——因为它连 MLM 头、NSP 头都没有；
- 装 `BertForMaskedLM`：**只忽略** `cls.seq_relationship.*`——因为它有 MLM 头（`cls.predictions.*` 接住了），但**没有 NSP 头**。

> 一句话：`BertForMaskedLM` = `BertModel` + MLM 头；它不需要 NSP 头，所以 NSP 的权重无处安放，被忽略。**忽略清单 = 这个类缺哪些模块的清单。**

---

## 二、手写 masking：逐行拆解

notebook 的 masking 一共 4 行，是本篇的心脏：

```python
inputs = tokenizer(text, return_tensors='pt')            # ① 分词
inputs['labels'] = inputs['input_ids'].detach().clone()  # ② 抄一份原始 id 当"标准答案"

mask_arr = (torch.rand(inputs['input_ids'].shape) < 0.15) \
        * (inputs['input_ids'] != 101) \                 # ③ 排除 [CLS]
        * (inputs['input_ids'] != 102)                   #    排除 [SEP]

selection = torch.flatten(mask_arr[0].nonzero()).tolist()  # ④ 取出被选中位置的"下标"
inputs['input_ids'][0, selection] = 103                    # ⑤ 把这些位置换成 [MASK]
```

### 3.1 第 ② 行：为什么要先 `labels = input_ids.clone()`

因为第 ⑤ 行会**原地改掉** `input_ids`（把词换成 103）。如果 `labels` 不先抄一份，等 `input_ids` 被改完，"正确答案"就没了。

```python
inputs['labels']    # 改之前抄的 → 还是 "1860"、"out"、"in"、"April" ...（原始词）
inputs['input_ids'] # 被改成  → "[MASK]"、" [MASK]" ...（挖空后）
```

> `.detach().clone()`：`clone` 是深拷贝（断开与原张量的共享），`detach` 是把它从计算图里摘出来（当"答案"不该有梯度）。两个一起写是标准姿势。

对照 notebook 的两行输出，能直接看到"答案 vs 输入"的差别：

```text
labels      : [CLS] after abraham lincoln won the november 1860 presidential election on an
              anti - slavery platform , an initial seven slave states declared their ... [SEP]
input_ids   : [CLS] after abraham lincoln won the november [MASK] presidential election on an
              anti - slavery platform , an initial seven slave states declared their ... [SEP]
```

### 3.2 第 ③ 行：那个"三连乘"在干嘛

`torch.rand(shape) < 0.15` 生成一个**和输入同形状**的布尔张量：每个位置有 15% 概率是 `True`（被抽中挖空）。后面两个乘法是**把不该挖的位置强制排除**：

```python
(rand < 0.15)          # True/False → 15% 的随机抽签
* (ids != 101)         # [CLS] 位置强制 False（101 = [CLS]，不能挖）
* (ids != 102)         # [SEP] 位置强制 False（102 = [SEP]，不能挖）
```

**注意这里的乘法是"逻辑与"**：Python/Torch 里 `True * True = True`、`True * False = False`。所以三行乘完，等价于"随机抽中 **且** 不是 `[CLS]` **且** 不是 `[SEP]`"。

notebook 实测：62 个 token 里抽中 **11** 个，`11 / 62 ≈ 0.177`（比 0.15 略高，因为是随机抽样，本来就允许浮动）。

### 3.3 第 ④ 行：`nonzero()` 把布尔表变成下标

`mask_arr` 是一张 `True/False` 的"哪些位置要挖"的表格；模型真正需要的是**位置编号**：

```python
torch.flatten(mask_arr[0].nonzero()).tolist()
# → [7, 18, 20, 24, 33, 39, 40, 47, 50, 52, 56]
```

- `mask_arr[0]`：取第 1 句话（batch 里那句）；
- `.nonzero()`：返回所有为 `True` 的位置的下标，形状 `[11, 1]`；
- `torch.flatten(...)`：拍平成 `[11]`；
- `.tolist()`：变成普通 Python 列表。

### 3.4 第 ⑤ 行：`[MASK]` 的 id 是 103

`[MASK]` 不是一个"特殊的模型行为"，它就是**词表里的一个普通 id**：

```python
tokenizer.vocab['[MASK]']        # → 103
tokenizer.special_tokens_map     # → {'unk': '[UNK]', 'sep': '[SEP]', 'pad': '[PAD]',
                                 #    'cls': '[CLS]', 'mask': '[MASK]'}
```

BERT-base-uncased 的五个特殊 token（记牢）：`[PAD]=0`、`[UNK]=100`、`[CLS]=101`、`[SEP]=102`、`[MASK]=103`。

于是最后一行就是**高级索引赋值**：

```python
inputs['input_ids'][0, selection] = 103
#                     ↑  ↑
#                  第1句  下标列表 [7,18,20,...] → 一次性把这 11 个位置全写成 103
```

改完的效果（notebook 真实输出）：

```text
[CLS] after abraham lincoln won the november [MASK] presidential election on an anti - slavery
platform , an initial seven slave states declared their secession from the country to form the
confederacy . war broke [MASK] in [MASK] 1861 when secession ##ist forces attacked fort sum
##ter in south carolina , [MASK] over a month after lincoln [MASK] s inauguration . [SEP]
```

> **这就是"手写 masking"的全貌**：随机选位置 → 用 `[MASK]` 覆盖 → 原词留在 `labels` 里当答案。真实 BERT 预训练在此基础上多了一层"80/10/10"规则，见 §三。

---

## 三、80/10/10：真实 BERT 的 masking 规则

notebook 里的 masking 是**教学简化版**：它把所有抽中的位置**都**换成 `[MASK]`。但原论文《BERT: Pre-training of Deep Bidirectional Transformers》用的是更讲究的 **80/10/10**：

| 比例 | 处理方式 | 目的 |
|---|---|---|
| **80%** | 换成 `[MASK]` | 正常的"填空"训练 |
| **10%** | 换成**一个随机词** | 逼模型别迷信"看到 [MASK] 才动脑" |
| **10%** | **保持不变**（还是原词） | 逼模型对**每个**位置都保持"我可能要预测我自己"的警觉 |

### 为什么必须搞 80/10/10？

核心矛盾是**预训练和微调的不一致（mismatch）**：

- **预训练时**：输入里有 `[MASK]`，模型学会了"看到 `[MASK]` 就集中火力预测它"。
- **微调 / 推理时**：真实下游任务（分类、NER、问答）的输入里**根本不会出现 `[MASK]`**。

如果只做 100% `[MASK]` 训练，模型就形成一种依赖：**"只有当那个位置是 [MASK] 时，它的表示才需要被认真编码"**。而微调时没有任何 `[MASK]`，模型不知道该对哪个位置"认真"，表示质量就掉了。

80/10/10 的解法很巧妙：

- 那 **10% 随机词**：模型看到的是个"错词"，位置不是 `[MASK]`，但答案仍是原词 → 逼它**不靠 `[MASK]` 这个标记，而是靠上下文**发现问题；
- 那 **10% 保持原词**：这个位置输入 == 答案，模型被逼着"对每个位置都准备好预测自己"——即使它是正常词。

两者合起来，等于告诉模型：**"别盯着 [MASK] 看，你要在任意位置都能根据双向上下文重建语义。"** 这样微调时即便没有 `[MASK]`，模型也表示得很好。

> 一句话：80/10/10 是**为了消除"[MASK] 依赖"**，让预训练学到的表示能平滑地迁移到没有 `[MASK]` 的下游任务。
>
> 补充：那 10% 随机词理论上都替换了还对不上，但**答案仍是原词**——所以模型会偶尔被"喂错"、loss 偏高，这是可接受的代价（论文实测比 100% [MASK] 更好）。

---

## 四、`labels` 与 `loss`：`-100` 与 `ignore_index`

### 4.1 前向输出长什么样

跑 `mlm(**inputs)`，notebook 拿到的 keys 是：

```text
odict_keys(['loss', 'logits', 'hidden_states'])
```

| 输出 | shape | 含义 |
|---|---|---|
| `loss` | 标量 | 交叉熵损失（**是不是只算 mask 位置，取决于 `labels`**，见 4.3） |
| `logits` | `[1, 62, 30522]` | **每个位置**都给出"30522 个词的分数"，不止 mask 位置 |
| `hidden_states` | 13 帧 | 和 07 一样，embedding + 12 层 |

> 注意 `logits` 是 `[B, N, vocab]`——**每个位置都有一份 30522 维的分数**。这是 MLM 头的本质：它就是把 `Linear(768→30522)` 接在**每个位置**上（10 讲 3.4）。

### 4.2 HF 源码：loss 是怎么算的

```python
# BertForMaskedLM.forward（简化）
prediction_scores = self.cls(hidden_states)      # hidden_states = last_hidden_state
masked_lm_loss = None
if labels is not None:
    loss_fct = CrossEntropyLoss()                # 注意：默认 ignore_index = -100
    masked_lm_loss = loss_fct(
        prediction_scores.view(-1, self.config.vocab_size),   # [B*N, 30522]
        labels.view(-1)                                       # [B*N]
    )
```

两件事要看清：

1. **预测和答案在同一位置对齐**（`[B*N]` 对 `[B*N]`）。BERT **不做 shift**——第 i 个位置的 logits 就是用来预测第 i 个位置的答案。
   > 对比 GPT：GPT 预测"下一个词"，所以要 `logits[..., :-1, :]` 对 `labels[..., 1:]` **错开一格**（那就是番外第 29 集讲的 `ignore_index` 与 shift）。BERT 是"填空"，不 shift。
2. **`CrossEntropyLoss` 默认 `ignore_index=-100`**：凡是 `labels == -100` 的位置，**不贡献 loss、也不进分母**。这就是"只算被 mask 的位置"的实现手段。

### 4.3 notebook 的一个"隐藏细节"（很重要）

看 notebook 的 ② 行：`inputs['labels'] = inputs['input_ids'].clone()`——它抄的是**完整序列**，**没有把非 mask 位置设成 `-100`**。

那么按 HF 的算法，这个 `loss` 是在**全部 62 个位置**上算的平均交叉熵，而不是只算 11 个 mask 位置。这也正是为什么 notebook 能这样手算并**完全对上**：

```python
ce = nn.CrossEntropyLoss()
ce(output.logits[0], inputs['labels'][0].view(-1))   # → 0.5636
output.loss                                          # → 0.5636   （一模一样）
```

因为两边都没有 `-100`，都在全 62 个位置上算。

> **这就是本篇最值得记住的一处"陷阱"**：
> - **教学 notebook**：`labels` = 完整原句 → loss 覆盖**所有位置**（每个词都要预测自己，是个更难的任务）；
> - **真实 BERT 预训练**：非 mask 位置的 `labels` 设成 `-100` → loss **只覆盖被挖空的位置**。

### 4.4 改造成"标准 MLM loss"

想把 notebook 改成真实规则，只需在挖空后，把**没被挖空的位置**的 `labels` 抹成 `-100`：

```python
labels = inputs['input_ids'].clone()          # 先把原句抄下来（挖空前！）
# ... 执行 §二 的 mask_arr / selection / input_ids[0, selection] = 103 ...

# 只保留 selection（被挖空）位置的答案，其余位置置 -100
keep = torch.zeros_like(labels, dtype=torch.bool)
keep[0, selection] = True
labels = labels.masked_fill(~keep, -100)

inputs['labels'] = labels
# 现在再跑 mlm(**inputs)，loss 就只在 11 个位置上了 —— 数值会与全位置版本不同
```

> 一行记忆：**`-100` = "这个位置不考试"**。`CrossEntropyLoss` 会跳过所有 `-100` 的位置，连分母都不算它。

---

## 五、`BertForMaskedLM` 源码级解剖

### 5.1 模块族谱

```python
mlm = BertForMaskedLM(config)
print(mlm)
```

```text
BertForMaskedLM(
  (bert): BertModel(                 ← 和 10 讲一模一样：embeddings + encoder + pooler
    (embeddings): BertEmbeddings(...)
    (encoder): BertEncoder(...)      ← 08 / 08B / 09 讲的全部
    (pooler): BertPooler(...)        ← ⚠️ MLM 用不到它（pooler 是给句子级任务用的）
  )
  (cls): BertOnlyMLMHead(
    (predictions): BertLMPredictionHead(
      (transform): BertPredictionHeadTransform(   ← dense(768→768) + GELU + LayerNorm
        (dense): Linear(768, 768)
        (LayerNorm): LayerNorm(768)
      )
      (decoder): Linear(768, 30522)               ← 输出层，权重与 word_embeddings 共享
    )
  )
)
```

对照 10 讲的族谱，几个点现在能串起来了：

| 观察 | 解释 |
|---|---|
| `mlm.bert` 就是完整的 `BertModel` | MLM = backbone + 头，backbone 分毫不差（10 讲 6.1） |
| `mlm.bert.pooler` 存在但**从不被调用** | pooler 服务于句子级任务；MLM 是 token 级，只用 `last_hidden_state` |
| MLM 头是**两段式**：`transform` + `decoder` | 先"深加工"（768→768 + 非线性 + 归一化），再"映射到词表"（768→30522） |
| `decoder` 的权重 `w` == `word_embeddings.weight` | **权重共享（weight tying）**，不是两份参数，是同一块显存（`data_ptr()` 相等，见 10 讲 6.4） |
| `cls.predictions.bias` 形状 `[30522]` | 输出偏置**不共享**，是独立参数 |

### 5.2 为什么 decoder 要和词嵌入 tie 起来

- **语义上**：词嵌入是"**词 → 向量**"（编码），decoder 是"**向量 → 词**"（解码）。它们是同一个映射的正反两面，权重共享等于强制这两套表示"对齐、成为互逆的表"。
- **参数上**：`30522 × 768 ≈ 23.4M`——这是全模型最大的一块参数之一（backbone 才 109M）。共享一次能**省掉 23.4M 参数**，也让稀有词的输入/输出表示互相受益。
- **历史**：这个技巧来自《Using the Output Embedding to Improve Language Models》（Press & Wolf, 2017），BERT / GPT / T5 全都在用。GPT 番外（合集第 25 集 `wte / lm_head`）讲的是同一件事。

### 5.3 前向数据流（一条线走完）

```
input_ids [1, 62]
   │
   ├─ BertModel ──► last_hidden_state [1, 62, 768]   ← 每个词一个 768 维向量
   │                        │
   │         （取 [MASK] 位置的那些向量做预测，但实际是"整句都算"）
   │                        ▼
   └─ BertOnlyMLMHead
        ├─ transform:  dense(768→768) → GELU → LayerNorm   → [1, 62, 768]
        └─ decoder:    Linear(768→30522)                    → [1, 62, 30522]
                                                                    │
        loss: CrossEntropyLoss(logits.view(-1,30522), labels.view(-1), ignore_index=-100)
```

> **一个常见误解**："MLM 头只对 `[MASK]` 位置计算。"其实**前向是对整句都算**（`logits` 是 `[1,62,30522]`），只是 **loss 只在 mask 位置算**（用 `-100` 屏蔽）。区分"前向算全句"和"loss 只算 mask"这两件事，是理解 MLM 的关键。

---

## 六、从零复现：`hidden_states[-1] → cls → logits`

notebook 的 section 4 做了一件事：**不调 `mlm(...)`，自己手动走一遍 head**，看能不能对上。

```python
output = mlm(**inputs)                                # ① 完整前向

# ② 手动：拿最后一帧隐藏状态，喂给 MLM 头
last = output['hidden_states'][-1]                    # [1, 62, 768]
manual = mlm.cls(last)                                # [1, 62, 30522]

print(torch.allclose(manual, output.logits, atol=1e-5))   # → True
```

**结论**：`BertForMaskedLM` 的前向，本质就是

```python
logits = clf_head(backbone(input_ids).last_hidden_state)
```

再把 `mlm.cls` 拆到最细，验证 5.1 的两段式：

```python
hidden = mlm.cls.predictions.transform(last)          # dense+GELU+LN → [1, 62, 768]
logits2 = mlm.cls.predictions.decoder(hidden)         # Linear(768→30522) → [1, 62, 30522]
print(torch.allclose(logits2, output.logits, atol=1e-5))   # → True
```

### 6.1 手算 loss（接 §四）

```python
ce = nn.CrossEntropyLoss()
loss_manual = ce(output.logits[0], inputs['labels'][0].view(-1))   # → 0.5636
print(loss_manual.item(), output.loss.item())                      # 0.5636  0.5636
```

两者相等，说明 `output.loss` 与"手算全位置 CE"完全一致（因为 `labels` 没设 `-100`）。

### 6.2 argmax 解码：看模型"填"了什么

```python
pred = torch.argmax(output.logits[0], dim=1)      # [62]，每个位置的最高分词的 id
tokenizer.decode(pred)
```

notebook 真实输出（节选）：

```text
. after abraham lincoln won the november 1860 presidential election on an anti - slavery
platform , an initial seven slave states declared their secession from the country to form the
confederacy . war broke out in december 1861 when secession ##ist forces attacked fort sum
##ter in south carolina , just over a month after lincoln ' s inauguration . [SEP]
```

逐点解读（这是本篇最生动的"看得见"的证据）：

| 位置 | 原句 | 模型预测 | 说明 |
|---|---|---|---|
| 0（`[CLS]`） | `.`（或首 token） | `.` | `[CLS]` 也可被 argmax，模型给个标点类的结果 |
| 未挖空处 | `after`、`lincoln`、`war`、`out` … | **几乎全对** | 前向覆盖全句，未挖空位置也大多能"回填"自己 |
| 挖空的 `[MASK]`(33) | `april` | **`december`** | 错了，但**是合理的月份**——它学到了"这里该是个月份" |
| 挖空的 `[MASK]`(24) 等 | `1860` | ✓ | 有时能填对 |

**为什么没挖空的位置也"预测得对"？** 因为 0.5636 这个 loss 是**全位置**的——模型被训练（这里是预训练好的权重）在**每个位置**都预测自己。而真正挖空的位置（如 `april`）模型并不能每次猜中——这正是 mask 位置 loss 的主要来源。

> **一句话**：argmax 解码让你"看见"MLM：没挖的地方基本能复原，挖掉的地方它会造一个"语境上合理"的词——这就是"理解上下文"的水平。

---

## 七、常见误区（10 个）

1. **误区：`[MASK]` 是一种"模型行为"。**
   不是。它就是词表里的**普通 id（103）**，和 `[CLS]=101` 一样。模型对它的处理，只是"它出现在输入序列里"而已。
2. **误区：masking 只把 15% 换成一个词。**
   notebook 的简化版是"全部换成 `[MASK]`"；真实 BERT 是 **80% `[MASK]` / 10% 随机词 / 10% 保持原词**（§三）。
3. **误区：`labels` 是模型输出的。**
   不是。`labels` 是**你喂进去的"标准答案"**，来自挖空前的原始 id（所以必须 `clone` 保底）。模型输出的是 `logits`。
4. **误区：`logits` 只有 `[MASK]` 位置是有效的。**
   不是。`logits` 是 `[B, N, 30522]`，**每个位置都有**；只是 loss 上屏蔽了非 mask 位置而已。
5. **误区：`-100` 是个"特殊词的 id"。**
   不是。它是 `CrossEntropyLoss(ignore_index=-100)` 的**默认忽略值**，一个"不考试"的占位标记，和词表无关。
6. **误区：BERT 也要像 GPT 那样 shift（错开一格）。**
   不要。GPT 预测"下一个词"才 shift；BERT 是"填空"，**同位置对同位置**，不 shift。
7. **误区：`BertForMaskedLM` 会用到 `pooler`。**
   不用。pooler 服务句子级任务；MLM 是 token 级，只吃 `last_hidden_state`。`mlm.bert.pooler` 在 MLM 里是"挂在那儿不干活"的。
8. **误区：MLM 头就是一层 `Linear(768→30522)`。**
   不是两层中的**两段**：`dense(768→768)+GELU+LayerNorm` → `decoder(768→30522)`；而且只有 `decoder.weight` 与词嵌入共享，bias 和 `transform.*` 都是独立的。
9. **误区：tied weights 是"两份参数同步更新"。**
   不是。是**同一块显存/同一个对象**（`data_ptr()` 相等），更新一次两边都变，不是两份参数互相同步。
10. **误区：masking 的 15% 是"整句 15% 的词"。**
    教学版按 token 随机抽；真实预训练还有 **whole word masking**（整个词一起挖，而不是把 wordpiece 的某一截挖掉），以及**不挖 `[CLS]/[SEP]/[PAD]`**。notebook 只排除了 `[CLS]/[SEP]`（§二 3.2）。

---

## 八、记忆卡

- **MLM = 挖空填空**：随机挖 15% 的词，让模型根据**双向**上下文填回来
- **`[MASK]` 是普通 id 103**；特殊 token：`[PAD]=0 [UNK]=100 [CLS]=101 [SEP]=102 [MASK]=103`
- **`labels` = 挖空前的原句**（先 `clone` 保底），是"答案"不是"输出"
- **`-100` = 不考试**：`CrossEntropyLoss` 默认忽略 `-100` 的位置，这是"只算 mask 位置"的实现
- **前向算全句、loss 只算 mask 位置**——这两件事必须分开记
- **BERT 不 shift**（同位置对同位置）；GPT 才 shift（预测下一个词）
- **MLM 头两段式**：`transform(dense+GELU+LN)` + `decoder(768→30522, tied with word_embeddings)`
- **80/10/10**：消除 "[MASK] 依赖"，让预训练表示能迁移到没有 `[MASK]` 的下游任务
- **`BertForMaskedLM` 加载时只忽略 NSP 头**（`cls.seq_relationship.*`）——这是它"族谱"的指纹

---

## 九、自测（先答再看）

1. 教材里挖空用的是"每个位置 15% 概率"，为什么还要特意排除 `[CLS]` 和 `[SEP]`？
2. `output.logits` 是 `[1, 62, 30522]`。如果我要看第 33 个位置（原词是 `april`）的预测，代码怎么写？`logits[0, 33]` 的 argmax 是什么含义？
3. notebook 里 `inputs['labels']` 是完整原句、没有 `-100`，所以 `loss` 覆盖 62 个位置。要让它只覆盖被挖空的 11 个位置，改哪一行？
4. 为什么 `mlm.cls(last_hidden_state)` 能和 `output.logits` 严格相等，但 `mlm.bert.pooler` 在这条路径里一次都没出现？
5. 用一句话解释：为什么 80/10/10 里那"10% 保持原词"反而**有助于**模型学习？

<details>
<summary>参考答案</summary>

1. 因为 `[CLS]`/`[SEP]` 不是"内容词"，把它们挖掉既没有语义答案、也没有预测价值；而且它们的表示被下游任务（句子级）大量使用，挖掉会破坏。真实做法还会排除 `[PAD]`。
2. `logits[0, 33]` 是一个长度 30522 的向量，代表"第 33 个位置最可能是哪个词"的分数；`logits[0, 33].argmax()` 就是模型给这个位置的**最佳猜测**的词 id，再用 `tokenizer.decode` 还原成词。notebook 里它就是 `december`（错，但合理）。
3. 在挖空之后，把非 `selection` 位置的 `labels` 置为 `-100`：`labels.masked_fill(~keep, -100)`（§四 4.4）。这样 `CrossEntropyLoss` 会跳过所有非 mask 位置，只算 11 个。
4. 因为 MLM 头只消费 `last_hidden_state`（`BertModel` 的**第一个**输出），而 pooler 是对 `[CLS]` 做 `Linear+Tanh` 得到的**另一个**输出，二者是同一趟前向的两个不同出口。`mlm.cls` 的输入是 `hidden_states[-1]`，与 pooler 无关，所以严格相等。
5. 因为"输入 == 答案"的位置逼迫模型**对每个位置都保持预测能力**，而不是形成"只有看到 `[MASK]` 才思考"的依赖。这样微调时（没有 `[MASK]`）表示依然可用，等价于一种"抗标记依赖"的正则。
</details>

---

## 十、费曼三连问

1. **一句话**：MLM 预训练就是"把句子挖几个空，让模型看着左右两边把词填回来"；`BertForMaskedLM` 把一个大词表分类头接在每个词的隐藏向量上，loss 只在被挖空的位置算。
2. **说形状**：给定 `B=1, N=62, vocab=30522`，写出 `mlm(**inputs)` 的 `loss` / `logits` / `hidden_states` 的形状，并说明 `hidden_states[-1]` 到 `logits` 中间经过了哪几层、每层的形状。
3. **讲出去**：向只会"下一词预测"（GPT 式自回归）的人解释——为什么 BERT 要"挖空"而不是"预测下一个词"，以及"挖空"为什么能带来**双向**理解、代价是什么（预训练/微调不一致 → 80/10/10）。

---

## 十一、与前面笔记的连接

- **接 10**：10 给了 head 家族的"族谱"与 MLM 头的模块结构；本篇把它展开成**训练任务**——`[MASK]` 怎么造、`labels` 怎么给、loss 怎么只算 mask 位置。
- **接 07**：07 讲过 MLM 也在输出里（`hidden_states` 13 帧）；本篇说明 `BertForMaskedLM` 用的正是 `hidden_states[-1]`（= `last_hidden_state`），而**不是** `pooler_output`。
- **接 04**：本篇用的 `torch.no_grad()` / `.detach()` 正是 04 讲过的——`labels` 是"目标"，必须 detach 出计算图。
- **接 06**：masking 挖掉的是 token；token 怎么来的是 06 的 subword/wordpiece——所以才会出现"整词 vs 子词"的 whole word masking 问题（§七 误区 10）。
- **接 02**：`tokenizer(text, return_tensors='pt')` 就是 02 的 `encode_plus` 管线；`token_type_ids`（segment embedding）也在其中。
- **→ 12**：合集第 13 集 **fine tune——文本分类/情感分析**，见 [12_fine_tune_transformers_classification.md](./12_fine_tune_transformers_classification.md)——`动手写 bert` 子系列到此**收官**（合集第 12 集），本篇起进入「BERT、T5、GPT」正片，第一次把 backbone + head **真正拿去训练**：`Trainer` + `TrainingArguments` + 两层 padding + 混淆矩阵 + 逐样本 loss。再后面的第 14~17 集是**从零手写 Transformer**（scaled dot-product attention、MultiHeadAttention、Encoder/Decoder Layer）。
- **番外呼应**：tied weights 的通用讲法见 GPT 番外（合集第 25 集 `wte / lm_head`）；`ignore_index` 与 PPL 见番外第 28、29 集——本篇的 `-100` 是它们的共同基础。

---

*11 完。跟着跑一遍 notebook：**重点盯 §二那 4 行 masking、§六的 `torch.allclose(mlm.cls(last), output.logits)`，以及 §四 4.4 把 `-100` 加上去前后 loss 的变化**——这三处跑通，MLM 就落地了。*

