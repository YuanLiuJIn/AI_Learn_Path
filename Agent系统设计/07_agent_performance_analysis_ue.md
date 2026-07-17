# 07. Agent 赋能 UE 引擎性能分析

> 本文提炼 Agent 如何通过 MCP 协议把 UE 性能分析工具 API 化，覆盖 GPU、CPU、内存三个维度。

## 1. 核心设计哲学

> 不是把数据喂给 AI，而是给 AI 一套查数据的工具。

传统做法：把几十 MB 的 Profiling 数据塞进 Prompt → Context 撑爆 → 分析不完整。

MCP 做法：把工具能力暴露给 LLM，让 Agent 按需查询，像工程师一样"拿起工具查数据"。

```text
传统模式：
  数据 → 全量塞进 Prompt → LLM 分析 → 结论（受 Context 限制）

Agent 模式：
  数据 → MCP 工具暴露 → Agent 按需调用工具 → 逐步分析 → 结论
  （不受 Context 大小限制）
```

## 2. GPU 维度：RenderDoc CLI

### 核心思路

把 RenderDoc 的分析能力拆成可组合的 MCP 工具，让 Agent 像"读源代码"一样读一帧抓帧。

```text
传统方式：
  工程师打开 RenderDoc GUI → 一帧帧翻 → 逐个看 DrawCall → 逐个看 Shader

Agent 方式：
  get_action_tree → 定位可疑 Pass
  analyze_shader_performance → 调 Mali Offline Compiler 算 Cycle
  get_frame_screenshot → 截图验证渲染状态
```

### 两种分析模式

| | Static Mode | Dynamic Mode |
|---|---|---|
| 实现 | renderdoccmd → XML → Python 解析 | renderdoc.pyd → 无头 GPU Replay |
| GLSL 源码 | ✅ | ❌ |
| Mali 性能分析 | ✅ | ❌ |
| 任意 EID 截图 | ❌ | ✅ |
| 任意 EID 导出 Texture | ❌ | ✅ |

### 核心 MCP 工具

```text
load_capture        → 加载 .rdc 抓帧文件
get_action_tree     → 层级化 GPU 命令树
get_frame_overview  → 按 RenderPass 聚合的帧概览
list_draw_calls     → 分页列出所有 DrawCall
get_draw_call_detail → 单个 DrawCall 完整信息
get_shader_source   → 提取 GLSL 源码
analyze_shader_performance → Mali cycle 分析（识别 ALU/LS/Tex 瓶颈）
get_frame_screenshot → 任意 EID 的渲染输出截图
save_texture        → 导出纹理文件
```

### 使用实例：定位最重的 DrawCall

```text
1. load_capture("game.rdc", mode="dynamic")
   → 帧统计：120 个 DrawCall

2. get_action_tree(max_depth=2)
   → MobileBasePass 下 WP_Weapon_HK416 占用 23,997 verts

3. get_draw_call_detail(event_id=951)
   → 绑定 10 个 texture，shader: M_TK_Weapon_Scope

4. analyze_shader_performance(program_id="16150")
   → fragment LS-bound, Total cycles: 16.1
   → 优化建议：减少 texture fetch 次数
```

---

## 3. CPU 维度：UTrace MCP

### 核心思路

把 .utrace 上亿条 event 数据 SQL 化后暴露给 LLM，让 Agent 像查数据库一样查函数耗时。

### prefilter_jank：从帧到 Cluster

```text
传统方式：
  打开 Unreal Insights GUI → 逐帧翻找 Jank → 逐个分析调用链

Agent 方式：
  prefilter_jank → 批量检测所有 Jank 帧 → 提取热路径签名 → 聚类
  → 100 帧 Jank 变成 33 个 Cluster → 逐类分析
```

### Idle-aware 线程归因

关键设计：GameThread 卡顿经常是因为在"等待" RHIThread 或 RenderThread。

```text
如果直接拿 GameThread 签名聚类：
  → 结论是"等待太多"，没有意义

内置约 25 种 idle timer 检测：
  → CPU Stall - Wait For Event
  → Wait For RHIThread
  → ...
  → 跳过 idle 帧，找到真正原因
```

### 跨会话断点续传

```text
对话 1：prefilter_jank() → 80 个 cluster
       → 分析了 15 个 → Context 快满

对话 2：start_jank_report() → 自动检测 15/80 已完成
       → 继续分析 16~30

对话 N：generate_jank_report() → 完整 HTML 报告
```

所有中间结果持久化到 SQLite，对话重启不丢失。

### 核心 MCP 工具

```text
load_db             → 加载 .insights.db
get_trace_summary   → 会话元数据 + 线程列表 + 帧统计
query_frames        → 按耗时筛帧
get_frame_events    → 展开事件树
get_hotpath         → 贪心最重子链游走
prefilter_jank      → 批量检测 + 签名聚类（写入 DB）
get_jank_summary    → 查看聚类结果
start_jank_report   → 创建 & 恢复分析计划
save_cluster_analysis → 持久化 LLM 分析结果
generate_jank_report  → 生成 Markdown + HTML 报告
execute_sql         → 只读 SQL，支持复杂聚合 JOIN
```

### execute_sql 的设计初衷

```text
很多情况下，Agent 直接写 SQL 查询效率更高、更易理解。

显式提供一个只读 SQL 接口，告诉 Agent：
  "你可以直接写 SQL，不需要逐个 API 调用"
```

---

## 4. 内存维度：Heap2Report

### 核心思路

把 UE 堆内存分析的全链路自动化，从平台差异化符号化到 AI 交互式堆探索。

```text
传统方式：
  拿真机数据 → 手动符号化 → 可视化 → 分析 → 写报告
  手工做要 1-2 小时

Agent 方式：
  一条命令符号化 + 几分钟 AI 分析
```

### 符号化流程

```text
iOS：支持 .dSYM.zip / .dSYM bundle / DWARF 目录
Android：自动去除 .so 版本后缀，创建 symlink

翻译完成后生成 .loli 格式文件
```

### AI 堆分析

核心设计：不把大文件塞进 Prompt。

```text
原始文件：几十 MB 的调用树
Context 消耗：只 10-20KB（因为 Agent 按需查询，不一次性加载）

两种模式：
  Snapshot（单帧快照）：分析内存分布，找各模块最大占用
  Diff（两帧对比）：分析内存增长点，定位泄漏或回归

自动联动源码：
  Agent 在分析节点时会 Grep/Read 游戏仓库源文件
  给出带代码上下文的根因和优化建议
```

### 核心 MCP 工具

```text
load_file           → 加载数据文件，自动判断 Diff/Snapshot
get_summary         → 总体统计 + Top 5 根节点
get_top_allocations → 全树最大的 N 个节点
get_children        → 某节点的直接子节点
get_call_path       → 从根到该节点的完整调用链
search_function     → 正则全树搜索函数名
get_subtree         → 该节点以下的缩进树
```

### 使用实例

```text
1. load_file("output/ios_heap.txt")
   → Loaded 588,473 nodes [mode: snapshot]

2. get_summary()
   → Total: 634.21 MB, 2,655,709 allocations

3. get_top_allocations(20, 2.0)
   → CacheMeshDrawCommands: 12.72 MB

4. get_call_path(31162)
   → 完整 12 层调用链

5. Grep 源码 "CacheMeshDrawCommands"
   → 找到 PrimitiveSceneInfo.cpp:1234，读取实现

6. 输出结论："CacheMeshDrawCommands 在场景初始化时分配了
   12.72 MB，建议检查静态网格体数量或开启异步缓存"
```

---

## 5. 两套工作模式

### 交互模式

```text
像和一个熟悉代码库的同事对话一样提问：
  "这帧 GPU 耗时为什么高？"
  "新版本比旧版本多了哪些内存？"
  "这个 Cluster 的 Jank 是 GameThread 还是 RenderThread 的问题？"

Agent 实时调用 MCP 工具查数据、翻源码、给结论。
人掌握分析方向，Agent 负责数据搬运和模式识别。
```

### 全自动模式

```text
Agent 借助跨对话状态持久化和多轮会话机制：
  数据加载 → Jank 聚类 → 逐 Cluster 深度分析 → 生成 HTML 报告

无需人工干预，无需担心 Context 被大文件撑爆。
几十分钟的 Trace、上百帧的 Jank 可以后台自主跑完。
```

### 大模型"偷懒"问题的解决

```text
问题：大模型在一个 Context 下分析大量数据时，
      倾向于深度分析头几个问题，后面敷衍

解决：写 TODO 表
  让大模型通过多次（或并行）运行，
  每次只处理合适量级的数据，
  最终输出完整且深入的分析报告
```

---

## 6. 三个工具背后的统一设计哲学

```text
1. 不是把数据喂给 AI，而是给 AI 一套查数据的工具
   → 按需查询，不受 Context 大小限制

2. 把工具能力拆成可组合的 MCP 接口
   → 每个工具职责单一，Agent 自主组合

3. 持久化中间结果
   → SQLite 存储分析进度，支持跨会话续传

4. 自动联动源码
   → Agent 分析时 Grep/Read 游戏源码，给出带上下文的根因

5. 支持交互 + 全自动双模式
   → 日常排查用交互，批量回归用全自动
```

## 7. 一句话总结

> Agent 赋能 UE 性能分析的核心不是"用 LLM 替代 Profiler"，而是通过 MCP 把 GPU/CPU/内存分析工具 API 化，让 Agent 能够按需查询、逐步推理、跨会话续传、自动联动源码。最终目标是让性能工程师把注意力放在决策上，而不是数据搬运上。
