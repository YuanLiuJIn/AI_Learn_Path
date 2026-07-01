# Harness Engineering：AI Agent 时代的“外部控制系统”

## Executive Summary

Harness Engineering 是一个正在形成中的 AI 工程概念，最适合理解为“围绕模型或 Agent 构建外部运行、约束、评测、反馈和治理系统”的工程实践。它不是单纯写提示词，也不是只做 benchmark，而是把 `AGENTS.md`、工具接口、沙箱、测试、评测器、日志追踪、CI 回归和人工审批等组件组合成一个能让 Agent 可靠工作的“控制层”。结合论文和项目看，HELM、`lm-evaluation-harness`、OpenAI Evals、Inspect AI、SWE-bench、WebArena、AgentBench、ToolBench、AutoGen、OpenHands 等共同说明：模型能力只是 Agent 的一部分，真正决定生产可用性的，往往是模型外面的 Harness。

## Background / Context

这里默认讨论的是 AI/软件工程语境下的 Harness Engineering，而不是汽车或电子电气中的线束工程。传统软件工程里早就有 test harness：它把被测代码放入一个可控环境，提供输入、夹具、断言、日志和结果报告。大模型时代，这个概念被扩大了：评测模型需要 evaluation harness，评测 Agent 需要交互环境和任务 runner，生产使用 coding agent 需要工具、文档、权限、测试、反馈循环和可观测性。

Mitchell Hashimoto 在 2026 年 2 月的文章中把自己使用 AI 编程 Agent 的一个阶段称为 “Engineer the Harness”。他的定义很朴素：当 Agent 犯错时，不只是修正这次错误，而是花时间工程化一个解决方案，让 Agent 以后不要再犯同类错误。这类解决方案可能是 `AGENTS.md` 里的项目级隐式提示，也可能是截图脚本、筛选测试脚本、自动检查工具等可编程工具。Martin Fowler 网站上 Birgitta Böckeler 的文章进一步把 harness 定义为 “AI agent 中除模型以外的一切”，即 `Agent = Model + Harness`，并把 coding agent 的外部 harness 拆成 guide/sensor、feedforward/feedback、computational/inferential 控制等概念。

微信公众号检索也显示，中文技术社区在 2026 年 3 月后集中讨论 Harness Engineering，常见关键词包括“大模型”“AI Agent”“评测框架”“AI Coding”“模型不是关键，Harness 才是关键”。这些中文材料有助于理解社区共识，但核心事实仍应以论文、官方项目和原文为主。

## What is Harness Engineering?

一句话说，Harness Engineering 是把模型放进一套可控工程系统里，让它能在真实任务中更稳定、更可复现、更可审计地工作。

如果 Prompt Engineering 关注“这次怎么问”，Context Engineering 关注“模型这次看见什么信息”，Eval Engineering 关注“怎么衡量输出好坏”，那么 Harness Engineering 关注的是“怎样设计整个外部系统，让模型或 Agent 在行动前被正确引导，行动中被安全限制，行动后能被快速检查和修正”。它包含 prompt 和 context，但范围更大，因为它还包括工具调用、运行环境、沙箱隔离、权限控制、任务状态、评测器、日志、回归测试和人类审批。

更具体地说，一个 Harness 至少有几类组件。第一是 guides，也就是前馈控制，例如 `AGENTS.md`、项目架构说明、编码规范、任务模板、工具说明、示例轨迹。它们让 Agent 在行动前更可能走对方向。第二是 sensors，也就是反馈控制，例如单元测试、类型检查、lint、结构化架构测试、浏览器截图、运行日志、LLM-as-judge、人工 review。它们让 Agent 在行动后知道哪里错了，并尝试自我修复。第三是 execution environment，例如 Docker、Kubernetes、浏览器环境、repo checkout、git worktree、数据库快照、API mock。它们确保 Agent 的动作可执行、可隔离、可恢复。第四是 observability 与 governance，例如 trace、token/cost、工具调用记录、审批策略、权限边界、数据留痕。

因此，Harness Engineering 的核心不是“把模型调得更聪明”，而是“把模型周围的世界设计得更适合它可靠地做事”。这也是为什么它特别适合 coding agent、browser agent、tool-use agent、企业内部自动化和大模型评测平台。

## 论文脉络：从评测 Harness 到 Agent Harness

下表列出最能支撑这个概念的论文和技术工作。严格说，并非所有论文都使用 “Harness Engineering” 这个新词，但它们共同构成了这个领域的技术基础。

| 论文/工作 | 年份 | 与 Harness Engineering 的关系 |
|---|---:|---|
| ReAct: Synergizing Reasoning and Acting in Language Models | 2022/2023 | 把 reasoning 与 action 交替组织成 Reason-Act-Observe 循环，是 Agent harness 的基本交互范式之一。 |
| Toolformer: Language Models Can Teach Themselves to Use Tools | 2023 | 说明模型可以学习何时调用工具、调用哪个工具、如何吸收工具结果，为 tool harness 提供学习范式。 |
| Holistic Evaluation of Language Models (HELM) | 2022/2023 | 提出多场景、多指标、标准化、透明的语言模型整体评测，是 evaluation harness 的代表。 |
| Language Model Evaluation Harness | 2024 Zenodo 版本 | EleutherAI 的统一评测框架，把任务、prompt、模型适配、指标和结果管理工程化。 |
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | 2023/2024 | 将真实 GitHub issue 转成可评测的软件工程任务，要求 Agent 修改代码并用测试判定是否解决。 |
| WebArena: A Realistic Web Environment for Building Autonomous Agents | 2023 | 提供自托管真实 Web 环境和 812 个任务，展示了 browser agent 所需的环境 harness。 |
| AgentBench: Evaluating LLMs as Agents | 2023/ICLR 2024 | 用 8 类交互环境评测 LLM-as-Agent，把 OS、DB、KG、网页等环境统一纳入 agent benchmark。 |
| ToolLLM / ToolBench | 2023/ICLR 2024 | 构建 3,451 个工具、16,464 个 API、126,486 条实例的工具学习与评测平台，体现 tool-use harness 的复杂性。 |
| AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation | 2023 | 把多 Agent 对话、工具、人类输入和外部执行组织为应用框架，属于 multi-agent harness。 |

这些工作可以按层次理解。最底层是模型评测 harness，例如 HELM、`lm-evaluation-harness` 和 OpenAI Evals，它们解决“怎么在统一任务上比较模型”。中间层是交互环境 harness，例如 WebArena、AgentBench、ToolBench，它们解决“Agent 如何在环境里行动、观察、调用工具并被评分”。更靠近生产的一层是软件工程和 coding agent harness，例如 SWE-bench、SWE-agent/OpenHands、Inspect AI、AutoGen、LangGraph/LangSmith，它们解决“Agent 如何进入真实工作流，如何修改代码、运行测试、留下轨迹、接受审批并持续改进”。

## 代表性项目与工程启示

| 项目 | 维护方 | 关键能力 | Harness 启示 |
|---|---|---|---|
| `lm-evaluation-harness` | EleutherAI | 支持 60+ 标准 LLM benchmarks、数百个子任务/变体、多模型后端、YAML 任务、缓存与结果记录 | 标准化任务定义、模型适配器和指标接口，是评测 harness 的基础模板。 |
| HELM | Stanford CRFM | living benchmark，多场景、多指标，强调覆盖、标准化和承认不完备性 | 好的 harness 不只给一个分数，还应暴露能力、风险、效率、公平性等多维指标。 |
| OpenAI Evals | OpenAI | LLM/LLM system 评测框架，支持私有 eval、model-graded eval、Completion Function Protocol | 业务场景需要自己的 eval registry，把真实工作流转成可重复回归的评测。 |
| Inspect AI | UK AI Security Institute | Dataset/Solver/Scorer/Task 组合，200+ 预构建评测，Docker/Kubernetes/Modal/Proxmox 沙箱，工具与 Agent 评测 | 生产级评测 harness 需要沙箱、工具审批、可视化 transcript 和可组合评分器。 |
| SWE-bench | SWE-bench Team | 2,294 个真实 GitHub issue；Verified 500、Lite 300、Multilingual 300、Multimodal 517 | 软件工程 Agent 必须用真实 repo、真实 issue、测试结果和 resolved rate 来验证。 |
| WebArena | WebArena Team | 自托管 Web 环境，购物、后台、Reddit、GitLab、地图、Wikipedia 等站点，812 个任务 | Browser agent 的 harness 必须包含可复现网页环境、登录状态、轨迹和自动评分。 |
| AgentBench | THUDM | 8 个交互环境：OS、DB、KG、数字卡牌、横向思维、家务、WebShop、Web browsing | Agent 能力不等于单轮问答能力，必须在多环境、多轮交互中评测。 |
| ToolBench / ToolLLM | OpenBMB | 3,451 工具、16,464 API、126,486 实例、ToolEval Pass Rate/Win Rate | 工具调用不是简单 function call，需要工具检索、参数规划、执行反馈和稳定评估。 |
| AutoGen | Microsoft | AgentChat、Core、Extensions、事件驱动、多 Agent、Docker 代码执行、MCP 扩展 | 多 Agent 应用需要消息协议、运行时、工具扩展和人类介入机制。 |
| OpenHands | OpenHands | 自托管 coding agent 控制中心，Agent Canvas、Agent Server、Automation Server，支持 Claude Code/Codex/Gemini/ACP Agent | Coding agent 的生产使用正在走向“常驻工程团队”式控制台，需要统一编排和自动化。 |

从这些项目可以抽象出一个通用 Harness 架构。任务层定义输入、目标、约束和评分标准；适配层把不同模型、Agent、工具、浏览器或代码仓库接到统一接口；执行层提供沙箱、依赖、数据库、浏览器、repo checkout 和资源限制；观察层记录每一步 prompt、response、tool call、stdout/stderr、截图、网络请求和成本；评分层运行 deterministic tests、规则匹配、LLM-as-judge 或人工审核；治理层处理权限、审批、数据隔离、审计、回滚和 CI/CD。

## 如何落地一个 Harness

如果你要在一个真实项目中做 Harness Engineering，可以从小到大分三步。

第一步是把隐性经验外显化。为项目写清楚 `AGENTS.md` 或类似文件，包括如何安装依赖、如何运行最小测试、哪些目录不能动、常见错误、API 使用方式、代码风格和 PR 标准。这个阶段的重点不是写长文档，而是把 Agent 反复犯错的地方变成短、准、可执行的项目规则。

第二步是建立快速反馈。把最常用的验证动作做成 Agent 能调用的脚本，例如 `check`、`test:changed`、`lint:fix`、`typecheck`、`screenshot`、`run-e2e-one`。反馈要快、局部、结构化，错误信息最好能直接告诉 Agent 下一步怎么改。Birgitta Böckeler 把这类东西称为 sensors，并区分 computational sensors 和 inferential sensors。前者包括测试、lint、类型检查、静态分析，便宜且确定；后者包括语义代码审查、LLM-as-judge、架构评审，昂贵且不完全确定，适合放在更靠后的流程。

第三步是把 Agent 放入可控执行环境。对 coding agent，常见做法包括每个任务独立 git worktree、容器化依赖、最小权限文件系统、只读/可写目录分离、自动回滚、CI 门禁、审计日志。对 browser agent，常见做法包括自托管网站副本、固定初始状态、自动登录 cookies、网络 HAR 记录、截图轨迹和任务完成断言。对 tool-use agent，常见做法包括工具 schema、参数校验、速率限制、API mock、敏感操作审批和工具返回结构化。

## 为什么这比“换更强模型”重要

强模型当然重要，但很多失败并不是模型智商不够，而是环境不可读、工具不可用、反馈太慢、权限过大、任务不可验证。SWE-bench 初始论文中，最强模型 Claude 2 只解决了 1.96% 的真实 GitHub issue，这说明真实软件工程任务远超传统代码补全。后来 SWE-bench 生态中 resolved rate 快速提升，除了模型进步，也离不开 Agent 工作流、repo 环境、patch 生成、测试执行和错误恢复的改进。ToolBench 也显示，工具调用性能不仅取决于模型，还取决于工具检索、调用轨迹、评测器和 API 环境稳定性。HELM 和 `lm-evaluation-harness` 则说明，即使只是评测基础模型，也需要统一 prompt、模型适配、指标、缓存和结果记录，否则分数不可比。

因此可以把 Harness Engineering 理解为 AI 时代的软件工程杠杆：当模型越来越强，差异会越来越多地体现在谁能把模型放进更好的工作系统里。

## 局限与风险

首先，Harness Engineering 不是一个完全定型的学术学科，很多材料是 2026 年工程社区快速形成的术语和实践总结。它与 context engineering、eval engineering、agent engineering、MLOps/LLMOps 有重叠，边界仍在变化。

其次，Harness 也会制造虚假的安全感。测试通过不等于行为正确，LLM-as-judge 不等于客观真值，自生成测试可能只验证了模型自己的假设，benchmark 高分也不一定迁移到真实生产环境。WebArena、AgentBench、SWE-bench 这类 benchmark 很有价值，但仍存在环境分布、数据污染、任务代表性和评分覆盖的问题。

最后，Harness 本身会变复杂。规则、工具、prompt、脚本、CI、审批、评测数据和 Agent 轨迹如果缺少版本管理，会变成新的技术债。一个好的 Harness 应该可测试、可维护、可观测、可迭代，而不是堆满互相矛盾的提示词和脚本。

## Conclusion

Harness Engineering 可以概括为：为 AI Agent 设计外部控制系统。它把模型的能力接入任务环境，通过前馈指导、受控工具、沙箱执行、快速反馈、可观测轨迹和回归评测，把“模型可能会做事”转化为“系统可以可靠地交付”。相关论文和项目已经给出了不同层面的实证基础：HELM 与 `lm-evaluation-harness` 证明评测需要标准化框架，SWE-bench、WebArena、AgentBench、ToolBench 证明 Agent 需要真实环境和自动评分，Inspect AI、OpenAI Evals、AutoGen、OpenHands 等项目则展示了生产化工具链的方向。对工程团队来说，最实用的起点不是追新名词，而是把 Agent 反复犯错的地方沉淀成文档、脚本、测试、沙箱和 CI 反馈，让每次错误都改进下一次执行环境。

## References

1. [Mitchell Hashimoto - My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey)
2. [Birgitta Böckeler - Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)
3. [Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110)
4. [Stanford CRFM - HELM](https://crfm.stanford.edu/helm/)
5. [EleutherAI - lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
6. [OpenAI - Evals](https://github.com/openai/evals)
7. [UK AI Security Institute - Inspect AI](https://inspect.aisi.org.uk/)
8. [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)
9. [SWE-bench Leaderboards](https://www.swebench.com/)
10. [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854)
11. [WebArena GitHub](https://github.com/web-arena-x/webarena)
12. [AgentBench GitHub](https://github.com/THUDM/AgentBench)
13. [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)
14. [ToolBench GitHub](https://github.com/OpenBMB/ToolBench)
15. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
16. [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155)
17. [Microsoft AutoGen Documentation](https://microsoft.github.io/autogen/stable/index.html)
18. [OpenHands GitHub](https://github.com/OpenHands/OpenHands)
