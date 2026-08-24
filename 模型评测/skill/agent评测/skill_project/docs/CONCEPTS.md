# SkillForge 概念详解

本文详细解释 SkillForge 的核心概念：Ground Truth、7 个核心特性、以及四大核心机制的
实现与意义。每个概念都对应 `src/skillforge/` 里的真实代码。

---

## 一、Ground Truth（GT）是什么

GT 是进化的"燃料"：它定义"一个好的 skill 面对这些输入时，应该满足什么"。
没有 GT 就没有优化目标。GT 由两层组成（`types.py` 里的
`GroundTruth` → `TestCase` → `Assertion`）。

### 1. 测试用例（TestCase）

**一个完整的评测场景**。字段：`id`、`prompt`、`assertions`、`split`、`metadata`。

```python
@dataclass(frozen=True)
class TestCase:
    id: str                    # 唯一标识
    prompt: str                # 用户会怎么触发这个 skill
    assertions: tuple[Assertion, ...]  # 期望它满足什么
    split: Split               # dev / holdout / regression
    metadata: Mapping[str, Any] = ...
```

以示例里的 `case_3` 为例：

```json
{
  "id": "case_3",
  "prompt": "review this code for security issues",
  "split": "dev",
  "assertions": [
    {"type": "contains", "value": "security"},
    {"type": "not_contains", "value": "always find issues"}
  ]
}
```

含义：**当用户问"审查安全问题"时，这个 skill 应该覆盖"security"维度，且不能强迫
"必须找出问题"**。

### 2. 断言（Assertion）

**最小可判定的检查单元**，一条断言只回答一个"是/否"。字段：`type`、`value`、
`description`、`params`。共 8 种类型（`AssertionType`），分两类：

| 类型 | 谁判定 | 检查什么 |
|---|---|---|
| `contains` | 程序 | 文本/产物包含某子串（大小写不敏感） |
| `not_contains` | 程序 | 不包含某子串 |
| `regex` | 程序 | 匹配正则 |
| `file_exists` | 程序 | 产物文件存在 |
| `json_schema` | 程序 | 产物 JSON 满足 schema |
| `script_check` | 程序 | 自定义脚本 exit code 为 0 |
| `path_hit` | LLM | 命中了正确的知识/工具路径 |
| `fact_coverage` | LLM | 覆盖了关键事实 |

**关键区别**：测试用例 = "一个场景 + 一堆期望"；断言 = "一条可机器判定的最小检查"。
GT 就是这些用例的集合，再按 `split` 切成三份（见"三层评测"）。

---

## 二、7 个核心特性的实现与意义

### 1. 端到端沙箱评测

**实现**：`evaluate/sandbox.py` 的 `SandboxEvaluator` + `SkillRunner`。

关键点：断言的对象变了。静态评测对 **skill 文本**做断言（"SKILL.md 里有没有写
security 这个词"）；沙箱评测对 **skill 的执行产物**做断言。

```python
class SandboxEvaluator(Evaluator):
    def evaluate(self, target, gt, split):
        corpus = target.snapshot().corpus
        with tempfile.TemporaryDirectory() as td:
            for case in gt.by_split(split):
                outcome = self._runner.run(corpus, case.prompt, workdir)  # 真正执行
                # 对 outcome.output 做 contains/regex
                # 对 outcome.artifacts_dir 做 file_exists/schema/script
```

`SkillRunner` 是可插拔接口，`LLMSkillRunner` 是简化版（把 skill + 问题喂给 LLM 生成
响应）。

**意义**：解决"文档体检 vs 能力验证"的根本鸿沟。一个 skill 文档里写了"我会审查安全
问题"，不代表它真的会。沙箱评测就是要看它"干不干得了活"。

### 2. Beam Search 搜索

**实现**：`proposer.py` 的 `propose(n=beam_width)` + `loop.py` 里的循环。

朴素做法是单链贪心：每轮只试一个改动，容易卡在局部最优。Beam 是每轮**并行生成 K 个
候选**，各自评测 + 门控，保留质量最优的作为下一轮起点。

```python
candidates = self._proposer.propose(ctx, n=self._cfg.search.beam_width)
for cand in candidates:          # K 个候选并行试
    self._target.write_skill_md(cand.content)
    results = self._evaluator.run_all(...)
    decision = self._gate.decide(...)
    if decision.passed and rate > round_best_rate:
        round_best_rate = rate      # 保留最优
```

**意义**：搜索空间从"一条线"变成"一束光"。代价是每轮多花 K 倍评测成本，所以
`beam_width` 默认 1（退回贪心），需要时再调大。

### 3. 统计显著性门控

**实现**：`gate.py` 的 `bootstrap_mean_diff_significant()`。

问题根源：**LLM 评测有噪声**——同一个 skill 同一个 GT，多次评测 pass_rate 会漂移
（`path_hit`/`fact_coverage` 靠 LLM 判断，有随机性）。硬阈值 `min_delta=0.02` 会把
"运气好的一次"误判成"真改进"。

解法：对 dev pass_rate **多次采样**，用 bootstrap 重采样构造"均值差"的置信区间，
只有置信区间下界 > 0（显著提升）才认：

```python
def bootstrap_mean_diff_significant(a, b, confidence=0.95, n_boot=2000):
    lower = diffs[int(alpha * n_boot)]
    return lower > 0.0, lower
```

**意义**：把"运气"和"真改进"分开。成本是每轮多跑几次评测（`significance_samples=3`
即 3 倍），换来门控的可信度。

### 4. 三层结构化记忆

**实现**：`memory.py` 的 `MemoryStore` + `MemoryLevel` 枚举。

三层递进：
- **TRACE**（原始）：执行轨迹，诊断现场。
- **LESSON**（失败教训）：结构化"什么改动 → 什么后果 → 为什么"。
- **PATTERN**（可复用模式）：通过门控的成功改法，可跨 skill 迁移。

```python
class MemoryLevel(str, Enum):
    TRACE = "trace"     # 原始
    LESSON = "lesson"   # 教训
    PATTERN = "pattern" # 可复用
```

写入时机：门控 keep → `add_pattern`；门控 discard → `add_lesson`。检索时
`format_for_prompt()` 把历史 pattern 注入 proposer（含 token 预算），实现**新 skill
冷启动**。

**意义**：把"扁平日志"变成"可增殖的经验资产"，越用越聪明。

### 5. 强类型配置

**实现**：`config.py` 的 dataclass 全家桶 + `types.py` 的统一类型。

```python
@dataclass
class GateConfig:
    min_delta: float = 0.02
    significance_samples: int = 3
    ...
```

**意义**：杜绝"字段漂移"。用 dict 传数据时，写错键名、类型不符运行时才炸；用
dataclass + 类型注解，IDE 能提示、拼错直接报错、默认值集中管理。

### 6. 跨平台 UTF-8

**实现**：所有文件 IO 显式写 `encoding="utf-8"`。

```python
self.skill_md_path.read_text(encoding="utf-8")                # 读
self.skill_md_path.write_text(new_content, encoding="utf-8")  # 写
```

**意义**：Windows 上 Python 默认用 GBK 读文件，遇到 SKILL.md 里的 em dash "—"
（UTF-8 字节 `E2 80 94`）直接崩。显式声明编码，三平台行为一致。

### 7. 职责分包

**实现**：`evaluate/`、`gate.py`、`memory.py`、`gitops.py` 各自独立，依赖单向。

**意义**：可导航、可替换。评测器换成沙箱版只需换一个类；门控逻辑独立测试；记忆层
独立演进。

---

## 三、核心机制的意义与功能

### 1. 8 阶段循环

`loop.py` 的 `EvolutionLoop.run()`，每轮走一遍：

| 阶段 | 功能 | 意义 |
|---|---|---|
| **Setup** | 初始化工作区、跑 baseline | 建立**参照系** |
| **Review** | 读三层记忆 + 上一轮失败 case | 给 proposer 提供**诊断依据** |
| **Propose** | LLM 诊断失败 + 生成原子修改 | 搜索的"提出"半边 |
| **Apply** | 把候选写回 SKILL.md | 显式化副作用，可 diff、可回滚 |
| **Verify** | 三层评测 | 验证"到底有没有变好" |
| **Gate** | 多维 AND 门控 | keep / discard 的硬决策 |
| **Log** | 写记忆（lesson/pattern） | 沉淀经验 |
| **Loop-Control** | 继续 / 升层 / 停止 | 收敛判断与策略切换 |

一句话：这是一个**受控的试错循环**——每一步都可审计、可回滚、可复现。

### 2. 三层评测

核心思想：**成本递增 + fail-fast**。

| 层 | 速度 | 测什么 | 意义 |
|---|---|---|---|
| **L1** | 秒级 | 结构/安全门卫 | 挂了直接丢弃，**不跑后面** |
| **L2** | 分钟级 | dev 全量 | 主信号，驱动门控决策 |
| **L3** | ~10 分钟 | holdout + regression | 条件触发，防过拟合 + 防退化 |

关键设计：`holdout`（盲测集）**绝不喂给 proposer**，否则 LLM 会"背答案"式过拟合；
`regression`（回归集）确保"改好了 A 没弄坏 B"。

### 3. 多维 AND 门控

5 个维度，每个回答一个独立的问题：

| 维度 | 问题 | 阈值 |
|---|---|---|
| **quality** | dev 通过率真的提升了吗 | `min_delta=0.02` |
| **trigger** | 触发准确率没降吧 | 容忍 5% |
| **cost** | token 没爆炸吧 | 增幅 ≤ 20% |
| **latency** | 延迟没爆炸吧 | 增幅 ≤ 20% |
| **regression** | 没破坏已有能力吧 | 下降 ≤ 5% |

**为什么用 AND 而非加权求和**：加权和允许"质量 +10% 但 token 翻倍"靠一个高分拉平
低分蒙混过关；AND 是"全过才留，任一不过就回滚"，逻辑上杜绝了这种作弊。

### 4. 分层突变

`MutationLayer` 三层，从便宜到贵：

| 层 | 改什么 | 成本 | 类比 |
|---|---|---|---|
| **TRIGGER** | 触发词/描述 | 低 | 学习率小步 |
| **BODY** | 正文指令 | 中 | 中等步长 |
| **SCRIPT** | 辅助脚本/references | 高 | 大步长 |

两条规则：
1. **一次只动一层**——保证改动可归因。
2. **卡住才升层**——先在便宜的层上榨干收益，连续 plateau 才升到更贵的层。

---

## 四、一句话串起来

**GT 定义"什么叫好"，8 阶段循环去"找更好的"，Beam Search 决定"往哪找"，
三层评测"测好不好"，AND 门控"留不留"，三层记忆"记住经验"，分层突变"控制改动粒度"，
强类型 + UTF-8 + 分包保证"工程上靠得住"。**
