# SkillForge

一个**自研的 Skill 自进化引擎**——整洁、集成度高、代码可维护。

融合前沿 skill 自进化研究的方法论（Voyager 的环境反馈、AutoSkill 的终身学习、
SkillRL 的经验蒸馏、ContDa 的持续适配等），从第一性原理独立实现。

> **一句话**：把 Skill 当成"可训练对象"——你备好数据(GT)、定好指标，剩下的交给
> 一个带门控、可回滚、有记忆的自我迭代闭环。

---

## 核心特性

| 特性 | 说明 |
|---|---|
| 端到端沙箱评测 | 不止静态"文档体检"，还能对 skill 的**执行产物**做能力验证 |
| Beam Search 搜索 | 并行多候选，避免单链贪心的局部最优 |
| 统计显著性门控 | 多维 AND + bootstrap 置信区间，缓解 LLM 评测噪声 |
| 三层结构化记忆 | trace → lesson → pattern，跨 skill 复用经验 |
| 强类型配置 | dataclass 配置（GateConfig/EvalConfig/...）+ 统一 `types.py` |
| 跨平台 UTF-8 | 所有文件 IO 显式声明 UTF-8，Windows/Linux/macOS 一致 |
| 职责分包 | evaluate / gate / memory / gitops 模块化组织，依赖单向 |

---

## 快速开始

### 安装（开发模式）

```bash
cd skill_project
pip install -e ".[dev]"     # 或直接:  pip install -e .
```

依赖：Python 3.10+，核心零第三方依赖（仅测试需要 pytest）。

### 1. 评测 baseline（无需 LLM）

```bash
skillforge eval --skill examples/hello-skill --gt examples/hello-skill/evals.json
# 或
python -c "from skillforge.cli import main; main(['eval','--skill','examples/hello-skill','--gt','examples/hello-skill/evals.json'])"
```

输出：
```
[dev] pass_rate=0.500 (2/4)
  - case_3: security 缺失
  - case_4: example 缺失
[holdout] pass_rate=1.000 (2/2)
[regression] pass_rate=1.000 (2/2)
```

### 2. 完整进化（需要 LLM 后端）

```bash
skillforge evolve --skill examples/hello-skill --gt examples/hello-skill/evals.json \
    --max-iterations 5 --beam-width 2 --git
```

`evolve` 的 Phase 2/3（诊断/修改）需要真实 LLM。接入方式：实现 `LLMBackend` 接口
（见 `src/skillforge/llm.py`），并在 `cli.py` 的 `_build_backend()` 里返回你的后端。

### 3. 跑测试

```bash
pytest tests/ -q
```

---

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│  cli.py            eval / evolve 命令入口                │
├─────────────────────────────────────────────────────────┤
│  loop.py           8 阶段循环驱动 + Beam 集成            │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ proposer │ evaluate │  gate    │ memory   │  gitops     │
│ (候选)   │ (评测)   │ (门控)   │ (记忆)   │ (git隔离)   │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│  target.py  优化目标抽象（Skill 目录/文件/section）       │
│  types.py   统一数据类型   config.py  强类型配置          │
│  gt.py      GT 加载校验   assertions.py  8 种断言         │
│  llm.py     LLM 后端 + 二元判定器                        │
└─────────────────────────────────────────────────────────┘
```

**8 阶段循环**：Setup → Review → Propose → Apply → Verify → Gate → Log → Loop-Control

**三层评测**：L1 结构/安全门卫 → L2 dev 全量 → L3 holdout+regression（条件触发）

**多维 AND 门控**：质量 / 触发 / 成本 / 延迟 / 回归，任一不达标即丢弃 + 回滚。

---

## 目录结构

```
skill_project/
├── src/skillforge/          # 核心包
│   ├── cli.py               # 命令行入口
│   ├── loop.py              # 8 阶段循环驱动
│   ├── proposer.py          # 候选生成（LLM + Beam）
│   ├── gate.py              # 门控 + 统计显著性
│   ├── memory.py            # 三层记忆
│   ├── gitops.py            # git 隔离
│   ├── evaluate/            # 评测层
│   │   ├── local.py         #   静态文档体检
│   │   └── sandbox.py       #   端到端沙箱能力验证
│   ├── target.py            # 优化目标抽象
│   ├── gt.py / assertions.py / types.py / config.py / llm.py
├── tests/                   # pytest 测试
├── examples/hello-skill/    # 最小示例（code-review-helper）
├── docs/ARCHITECTURE.md     # 架构设计文档
└── pyproject.toml
```

详见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。
