# 科研 Skill 使用指南（论文阅读 / 文献综述 / 学术翻译 / 科研选题）

> 记录日期：2026-09-11
> 适用场景：地质 + AI（AI4S）方向的论文阅读、文献检索、学术翻译与科研选题
> 安装位置：`C:\Users\Administrator\.codebuddy\skills\`

---

## 一、总览

| # | Skill（文件夹名） | 内部 name | 一句话定位 | 主要产物 |
|---|---|---|---|---|
| 0 | （内置 `pdf`） | pdf | PDF 全文/表格提取、扫描件 OCR | 纯文本内容，供其他 skill 使用 |
| 1 | `literature-review-cn` | literature-review | 多源学术检索 + 带引用综述 | 论文列表（题名/DOI/摘要/被引）、综述段落 |
| 2 | `mli-paper-reading` | mli-paper-reading | 李沐三遍法精读 | Paper Card + 图文并茂的 HTML 阅读笔记 |
| 3 | `nature-reader` | nature-reader | 全文中英对照精读 | 结构化双语 Markdown（原文+译文+图注） |
| 4 | `zcx-translation-assistant` | translation-assistant | 专业翻译（保格式/术语一致） | 直译 / 双语并排 / 保格式译文 |
| 5 | `paper-reading-socratic-coach` | paper-reading-socratic-coach | 苏格拉底式提问训练独立阅读 | 精度报告 + 逐题反馈 + 学习状态档案 |
| 6 | `researchideation` | research-ideation | 科研想法生成/评估/管理 | IDEA 工作区 + 评估白皮书 + 30 分评分 |

**一句话分工**：检索用 1 → 精读用 2/3 → 翻译用 4 → 训练用 5 → 找创新点用 6。

---

## 二、逐个详解

### 0. `pdf`（内置，无需安装）

- **描述**：读取 PDF 文件，提取文本、表格；对扫描版 PDF 可做 OCR；也能处理图片型内容。
- **推荐用法**：
  - 直接说"读一下这个 PDF：<路径>"，即可让模型基于全文作答。
  - 与其它 skill 搭配时作为**底层读取能力**（例如先把 PDF 转文本，再交给翻译或精读 skill）。
- **本项目场景**：`docs/综述/`、`docs/近期研究/` 下的 16 篇 PDF 可直接读取。

---

### 1. `literature-review-cn` —— 文献检索 + 综述写作

**描述**：通过 **Semantic Scholar（s2）/ OpenAlex（oa）/ Crossref（cr）/ PubMed（pm）** 四个学术 API 检索文献，自动按 DOI 去重，支持取详情并撰写带引用的综述章节。

**核心能力**
- 多源检索、全摘要返回、DOI 提取、多源自动去重
- 支持 "Polite Pool" 礼貌访问（通过 `USER_EMAIL`）
- 提供 `scripts/lit_search.py` 脚本

**可用参数**
| 参数 | 值 | 说明 |
|---|---|---|
| `--limit` | 数量 | 返回条数 |
| `--source` | `all` / `both` / `s2` / `oa` / `cr` / `pm` | `all`=四库合并去重；`both`=S2+OA |
| 详情 | `details "DOI:xxx"` | 取元数据 + TL;DR |

**推荐使用方法**
```bash
# 1) 宽泛检索（四库合并、自动去重）
python3 scripts/lit_search.py search "deep learning mineral prospectivity mapping" --limit 10 --source all

# 2) 定向检索
python3 scripts/lit_search.py search "earthquake prediction machine learning" --source s2

# 3) 按 DOI 取详情
python3 scripts/lit_search.py details "DOI:10.3390/min14101021"
```
> 地质/地球科学优先用 `--source all` 或 `--source both`；PubMed 主要面向生物医学，地学用得少。

**写综述流程**：提取要点 → 按主题/时间组织 → 分步起草（Think step-by-step）。

**环境变量（可选，建议配置）**
| 变量 | 用途 | 默认 |
|---|---|---|
| `USER_EMAIL` | 礼貌池邮箱（提高速率与稳定性） | anonymous@example.org |
| `SEMANTIC_SCHOLAR_API_KEY` | 提高 S2 速率限制 | — |
| `OPENALEX_API_KEY` | OpenAlex API Key | — |

**注意**：依赖 Python；建议先设 `USER_EMAIL`，否则高频检索可能被限流。

---

### 2. `mli-paper-reading` —— 李沐式论文精读

**描述**：基于李沐论文精读系列（快速筛选 + 三遍阅读 + 逐段精读）。支持 **arXiv 链接 / PDF 链接 / 本地 PDF / DOI / 论文标题**，自动从 PDF 提取插图，生成含 **MathJax 公式**与 **Mermaid 图**的**自包含 HTML 阅读笔记**并在浏览器展示。

**三遍读法**
| 阶段 | 目标 |
|---|---|
| Pass 1 | 建立整体图像，决定"精读 / 略读 / 跳过" |
| Pass 2 | 梳理内容、图表、方法、实验与核心证据（不陷入证明细节） |
| Pass 3 | 虚拟复现：重建假设、步骤、公式/伪代码、实验设计、局限、缺失细节 |

**推荐使用方法**
```
# 精读单篇（arXiv / PDF / DOI / 标题均可）
/mli-paper-reading 帮我精读这篇论文: https://arxiv.org/abs/1706.03762
/mli-paper-reading 精读这篇论文: d:\...\docs\近期研究\2025_NatComms_机器学习预测米尺度实验室地震.pdf

# 多篇对比
/mli-paper-reading 比较这两篇的地震预测方法差异: <论文A> <论文B>

# 为复现做准备
/mli-paper-reading 我要复现这篇，帮我整理复现清单和风险点

# 文献地图（找前驱/后续工作）
/mli-paper-reading 帮我梳理"矿产远景预测 + 深度学习"的研究谱系
```

**产出结构**（HTML 笔记）：粘性导航 → Paper Card → 整体认知 → 方法（内嵌原图）→ **证据账本表**（主张/证据/强度/注意事项）→ 批判评价 → 研究用途 → 附录图。

**依赖**：Python 3.7+、**pymupdf（唯一需手动安装）**、`http.server`、`lsof`、`curl`、浏览器打开命令。

**⚠️ Windows 注意事项（重要）**
- 该 skill 的脚本命令是 **macOS/Linux 版**（`lsof` / `open` / `xdg-open` / `bash` 语法），在 Windows 上需替换为：
  - 找空闲端口 → PowerShell `Test-NetConnection`
  - 起服务 → `python -m http.server 7410 --directory "$env:USERPROFILE\paper-notes"`
  - 打开浏览器 → `Start-Process "http://localhost:7410/xxx.html"`
- 笔记默认输出到 `~/paper-notes/`（Windows 即 `C:\Users\<用户>\paper-notes\`）。
- 首次使用前建议执行：`python -m pip install pymupdf --user`。
- 若公式/图离线不渲染：MathJax、Mermaid 走 `cdn.jsdelivr.net`，需联网。

**会话结束后的追问菜单**（可直接回复数字）：方法深挖 / 实验审查 / 复现清单 / 对比分析 / 文献地图 / 研究方向 / 自由提问。

---

### 3. `nature-reader` —— 全文中英对照精读

**描述**：把一篇论文（**PDF 路径 / DOI / arXiv ID / URL**）转换成**带注释的双语 Markdown**：英文原文 + 行内中文翻译 + 图表与正文对应（figure grounding）+ 逐节小结。虽名为 Nature 系优化，实际可用于各类期刊论文。

**推荐使用方法**
```
用 nature-reader 读这篇：d:\...\2025_CommsEarthEnv_可泛化深度学习预测实验室地震.pdf
把这篇论文转成中英对照 Markdown：10.1038/s41467-025-64542-4
```

**输出结构**
| 区块 | 内容 |
|---|---|
| 速览表 | 核心问题 / 核心方法 / 关键结果 / 意义 / 适合引用于 |
| 摘要 | 英文原文 + 中文翻译 |
| 引言 / 结果 / 讨论 | 逐段：原文 + 中文 + 💡要点 + 📚关键引用 |
| 方法 | 中文为主，保留关键参数/仪器/条件 |
| 图表解读 | 原图注 + 中文说明 + "这张图证明了什么、哪一栏最重要" |
| 参考文献 | 关键文献 + 简要说明 |
| 🎯 如何使用这篇论文 | 可在哪写/引用、需要注意的局限 |

**输出选项（可直接指定）**
1. **全文双语**（默认，每段都翻译）
2. **仅速览**（速览 + 摘要 + 图表解读）
3. **方法重点**（重点翻译 Methods）
4. **导出**为 `[论文名]-reader.md`

**翻译规范**：忠实而非逐字；**数字、化学式、基因名、专有名词保留原文**；术语用"中文（English）"双写，如"析氧反应（oxygen evolution reaction）"；保留 hedging 语气（suggest→表明、demonstrate→证明）。

**获取全文的合法途径（付费墙时）**
- **Unpaywall**：`https://unpaywall.org/api/v2/<DOI>?email=<你的邮箱>` → 取 `best_oa_location.url_for_pdf`
- **arXiv 预印本**：用 `arxiv "<标题>" "<第一作者>"` 检索
- **机构订阅 / 图书馆**（校园网）或作者主页/机构仓库版本

---

### 4. `zcx-translation-assistant` —— 专业翻译（保格式 / 术语一致）

**描述**：专业多语言翻译，重点处理**领域术语**并**保持格式**，支持双语并排输出。默认语对 **中文（简体）↔ 英文**。

**支持语对**：zh-CN↔en（母语级）、zh-TW↔en、zh-CN↔ja/ko、en↔fr/de/es。

**内置领域术语表**：金融、法律、科技、医药（含常见误译对照，如"爆仓 → forced liquidation / margin call"，而非 "explode warehouse"）。

**四种输出格式**
| 格式 | 适用 |
|---|---|
| 直译 | 只要目标语言、追求可读性 |
| 双语并排 | 原文/译文段落对齐，准确敏感内容推荐 |
| 双语逐句 | 句级对照，适合精读 |
| **保格式** | 保留 Markdown/表格/代码块/列表/标题，只替换文本 |

**格式保持规则（要点）**
| 元素 | 处理 |
|---|---|
| 标题 | 译文本，保留层级 |
| 粗体/斜体 | 保留标记，译内容 |
| 链接/图片 | 译文案/alt，**URL 不变** |
| 代码块 | **只译注释与字符串，代码本体不动** |
| 表格 | 译单元格，保持行列与对齐 |
| 列表/引用/分隔线 | 保留结构 |

**推荐使用方法**
```
把这篇论文摘要翻成中文，保留 Markdown 格式：
<粘贴内容>

把下面这段做中英双语并排对照翻译（科技领域，保留专业术语）：
<粘贴内容>

翻译这个 PR 描述，只译注释，代码别动：
<粘贴代码>

把这个 md 文件译成英文，输出到 xxx_translated.md
```

**质量自检**（要求时执行）：可读性 / 术语一致性 / 数字准确 / 无漏译 / 无编造。

**注意**：源码/API 名/文件路径/变量名一律不译；法律合同类建议强制"双语并排"。

---

### 5. `paper-reading-socratic-coach` —— 苏格拉底式阅读训练

**描述**：**诊断优先**的论文阅读教练。目标不是替你读，而是训练你**不依赖 AI 也能读好论文**。训练三种长期能力：**阅读精度**、**科学思维**、**研究方法论**。

**核心流程**
| 阶段 | 内容 |
|---|---|
| Stage 0 | 教师侧参考理解（静默建立，不直接倾倒给用户） |
| Stage 1 | **先出精度报告**（Precision Report，含预测基线诊断假设） |
| Stage 2 | **自适应提问**：单选 / 多选 / 简答 / 证据检索 / 推理重建 / 方法批判 / 前沿生成 |
| Stage 3 | **每题反馈**：判定 + 讲清为什么 + 引用论文证据 + 归类弱点类型 + 更新状态 |
| Stage 4 | **会话末更新学习状态** |

**评分体系**：10 个维度各 0–5 分（问题理解、题文对应、相关工作映射、方法重建、公式/定理理解、实验解读、主张-证据一致性、局限识别、方向生成、方法论意识）；另有 3 个宏观分：**Reading / Thinking / Methodology**。

**进度设置**：默认**一次一题**、每场 **6–10 题**；由易到难，先"提取→重建"，再"批判→延伸"。

**状态持久化**：`.paper-reading-coach/learning_state_latest.md` 与 `session_log.md`（无写入权限时会打印完整状态块供手动保存）。

**推荐开场话术**
```
用这篇论文训练我：先给精度报告，再出题考我
继续上次的阅读训练（读取我的学习状态），接着练
诊断我在这篇论文上"阅读/思维/方法论"的薄弱点
这轮只出简答题和多选题
这轮重点考公式和实验解读
```

**⚠️ 注意**：不要把它当"一次性总结"用；它在核心理解未验证前**不会**问前沿/选题类问题——这是有意设计。

---

### 6. `researchideation` —— 科研选题与创新点评估

**描述**：领域无关的系统化**科研想法生成 → 评估 → 管理**框架。核心观点：想法可以**被系统地生成、严格评估、客观比较**；而且**先有文献基线，才知道什么才是真新**。

**工作区结构**
```
IDEA/
├── 01-灵感收集/   # 索引.md（新颖性地图+想法登记）｜想点子指南.md（6 法）｜待评估点子.md
├── 02-评估中/     # 每个想法一个文件夹 + 评估白皮书
├── 03-进行中/
├── 04-已归档/
├── 05-文献库/     # 每篇论文一个 .md（题名/作者/方向/核心思想）
└── README.md
```

**工作流（Phase 0–6）**
| 阶段 | 动作 |
|---|---|
| 0 | 初始化 + **建文献基线**（扫描 `05-文献库/`，分类，写索引，找空白） |
| 1 | 生成想法（应用 6 种方法 + 网络新颖性核验 + 登记为"待评估"） |
| 2 | 评估想法（调研竞品/邻近工作 → 写评估白皮书 → 状态改"评估中"） |
| 3 | 新颖性核验（文献库 + **≥3–5 组中英文关键词**网络检索 + 综述 + 外部知识库） |
| 4 | 文献 → 索引同步 |
| 5 | 状态流转（待评估 → 评估中 → 进行中 → 已归档） |
| 6 | 修正与更新评估（补检索、改白皮书、升版本号） |

**30 分评分体系**（6 维 × 1–5 分，0.5 递增）
| 维度 | 含义 |
|---|---|
| 新颖性 Novelty | 是否已有人做过 |
| 技术可行性 | 能否实现 |
| 实验可验证性 | 能否被证实 |
| 发表可行性 | 审稿人是否买账 |
| 契合度 | 与现有工作是否一致 |
| 紧迫性 | 竞争压力 |

> 评分为 3.0 只代表"合格"，不代表"好"，切勿虚高。

**推荐使用方法**
```
初始化 IDEA 系统，并把 docs/近期研究 的论文录入 05-文献库
围绕"地质+AI 的矿产远景预测"帮我想 5 个研究方向，并做新颖性核验
评估这个想法：<你的想法>，输出评估白皮书和评分
把这批新读的论文同步到文献库并更新索引
把这个想法移到"进行中"
```

**铁律**：文献先行；一说"新"必须先检索 ≥3 组关键词；`索引.md` 是唯一事实源。

---

## 三、推荐组合工作流

### 工作流 A：做一个新方向的调研（最常用）
```
① researchideation      初始化 IDEA + 建文献基线，定位研究空白
② literature-review-cn  按主题多源检索，拿题名/DOI/摘要/被引
③ mli-paper-reading     对核心 3–5 篇做三遍精读，产出 HTML 笔记 + 证据账本
④ nature-reader         对最关键的 1–2 篇做中英对照，逐段吃透
⑤ zcx-translation-assistant  需要把关键段落译成中文/英文并保格式时使用
⑥ researchideation      基于空白提出想法 → 新颖性核验 → 30 分评分
```

### 工作流 B：把一篇论文吃透
```
pdf（读全文）→ mli-paper-reading（三遍精读+证据账本）
→ nature-reader（逐段中英对照）→ zcx-translation-assistant（关键段落精译）
```

### 工作流 C：训练自己的阅读能力
```
paper-reading-socratic-coach（精度报告→逐题训练→学习状态档案）
配合 mli-paper-reading 的笔记做复盘
```

### 工作流 D：写给导师/组的汇报
```
literature-review-cn（检索）→ mli-paper-reading（精读笔记）
→ nature-reader（双语材料）→ zcx-translation-assistant（图表/摘要精译）
```

---

## 四、安装、调用与注意事项

**调用方式**
- 显式（最可靠）：`/skill名 <任务>`，如 `/mli-paper-reading 精读这篇 ...`
- 自然语言：命中描述里的关键词即可自动触发（如"精读""文献综述""翻译""中英对照""想研究方向"）

**安装/生效**
- 已安装到：`C:\Users\Administrator\.codebuddy\skills\<skill文件夹>\`
- 新装 skill 若未被识别，**重启/重载 IDE** 后再试。

**命名提示**
- 文件夹名与内部 `name` 不完全一致（`literature-review-cn`→`literature-review`；`zcx-translation-assistant`→`translation-assistant`）；按**文件夹名**调用即可，但后续若再装同名 skill 会冲突。

**依赖清单**
| Skill | 依赖 |
|---|---|
| literature-review-cn | Python 3（+ `requests` 类库）；建议设 `USER_EMAIL` |
| mli-paper-reading | Python 3.7+、**pymupdf**、本地 HTTP 服务、浏览器；脚本为 macOS/Linux 写法，**Windows 需替换命令** |
| nature-reader | 无特殊依赖（靠 read/web_fetch）；需联网取开放版本 |
| zcx-translation-assistant | 无特殊依赖 |
| paper-reading-socratic-coach | 建议可写文件（保存学习状态） |
| researchideation | 无特殊依赖；建议可写文件（IDEA 工作区） |

**合规提示**
- 论文全文请通过**开放获取（Unpaywall / 出版商 OA / 机构订阅 / 作者主页 / 预印本）**获取；请勿使用盗版镜像站点。

---

## 五、本目录（`docs/reading_skill/`）建议用法

- 本文件即"说明书"，新开对话时可直接让模型读取它来按规范执行。
- 建议在本目录下逐步积累：
  - `笔记/`：`mli-paper-reading` 产出的精读笔记（可复制 HTML）
  - `双语/`：`nature-reader` 产出的中英对照 Markdown
  - `训练日志/`：`paper-reading-socratic-coach` 的学习状态与错题记录
  - `IDEA/`：`researchideation` 的选题工作区
