# 09. GUI Agent 如何赋能 Agentic RAG

> 本文探讨如何将 GUI Agent 能力嵌入 Agentic RAG 体系，解决"数据源没有 API、无法被传统检索覆盖"的根本问题。

---

## 1. 问题：很多高价值数据源无法被传统 RAG 访问

```text
传统 Agentic RAG 的数据源：
  ✅ 向量数据库（文档、知识库）
  ✅ Web 搜索 API（Google、Bing）
  ✅ SQL 数据库
  ✅ 结构化 API（天气 API、金融 API）

无法覆盖的数据源：
  ❌ 气象数据平台（需要登录、填表单、点击查询）
  ❌ 卫星数据下载站（需要地图选区、图层操作）
  ❌ 政府公开数据门户（流程复杂、页面跳转多）
  ❌ 企业内部旧系统（无 API、DOM 复杂）

这些恰好是 GUI Agent 能解决的问题！
```

---

## 2. GUI Agent 在 Agentic RAG 管道中的位置

```text
┌─────────────────────────────────────────────────┐
│              Agentic RAG 管道                    │
│                                                 │
│  User Query                                     │
│      ↓                                          │
│  Router（判断复杂度）                              │
│      ↓                                          │
│  Planner（决定数据源）                             │
│      ↓                                          │
│  ┌─────────────┬──────────────┬───────────────┐ │
│  │ Vector DB   │   Web API    │  GUI Agent    │ │
│  │ 已有知识库  │   公开接口    │ ★ 无API站点   │ │
│  └─────────────┴──────────────┴───────────────┘ │
│      ↓              ↓              ↓            │
│  ┌──────────────────────────────────────────┐   │
│  │        数据融合 + 交叉验证                 │   │
│  │        Search-P1 风格质量评分              │   │
│  └──────────────────────────────────────────┘   │
│      ↓                                          │
│  Generator（生成答案）                             │
└─────────────────────────────────────────────────┘
```

---

## 3. 两种接入方式

### 方式 A：GUI Agent 作为"特殊检索工具"

```python
class GUIAgentTool:
    """将 GUI Agent 封装为标准 Agentic RAG 工具"""
    
    def __init__(self, site_config):
        self.site_url = site_config["url"]
        self.login_required = site_config.get("login")
        self.form_fields = site_config.get("form_fields", {})
    
    def execute(self, query_params):
        """执行一次 GUI 采集，返回结构化数据"""
        # 1. 打开站点（复用登录态）
        page = browser.new_page(storage_state="session.json")
        page.goto(self.site_url)
        
        # 2. 填写搜索表单
        for field, value in query_params.items():
            self.fill_form_field(page, field, value)
        
        # 3. 提交查询
        page.click("查询按钮")
        page.wait_for_load_state("networkidle")
        
        # 4. 提取结果
        results = self.extract_results(page)
        
        # 5. 同时捕获后台 API（为后续优化准备）
        api_calls = self.sniff_api_calls(page)
        
        return {"results": results, "source": self.site_url}
```

### 方式 B：GUI Agent 作为独立的 Worker Agent

```text
Planner Agent（调度中心）
     ↓ 分配子任务
Worker Agent 1: GUI Web Agent（气象数据平台）
Worker Agent 2: GUI Map Agent（卫星数据选取）
Worker Agent 3: RAG Agent（本地知识库）
Worker Agent 4: API Agent（公开天气 API）
     ↓ 结果汇总
Reviewer Agent（交叉验证）
     ↓
Writer Agent（生成报告）
```

---

## 4. 关键设计决策

### 4.1 何时用 GUI Agent vs API？

```text
决策逻辑：

有官方 API 吗？
  ├─ 有 → API Agent（更快、更稳、更便宜）
  └─ 没有 → 继续判断

页面是标准 HTML 表单 + 表格吗？
  ├─ 是 → DOM 文本化方案（Playwright + 元素提取）
  │       每步 0.5s，文本模型，低成本
  └─ 否 → 继续判断

页面有地图/卫星图/Canvas 吗？
  ├─ 是 → 截图识别方案（OmniParser + 多模态模型）
  │       每步 1-3s，多模态模型，较高成本
  └─ 否 → 人工介入或放弃
```

### 4.2 首次探索 vs 后续固化

```text
首次探索：
  GUI Agent 完全自主探索：
    识别按钮 → 填写表单 → 查看结果 → 捕获API
  产出：页面结构文档 + 采集流程描述 + 候选API

后续固化：
  基于首次探索的发现，生成 Playwright 固化脚本
  或直接调用捕获到的 API
  大幅提升稳定性和速度
```

### 4.3 记忆增强：不同数据站之间的经验复用

```text
多个数据站虽然是不同平台，但操作模式相似：
  - 都需要"搜索→筛选→查询→下载"
  - 都有按钮、输入框、下拉框、表格

Agent 可以复用模式经验：
  "这个站和 CMA 平台类似，搜索框也在顶部导航右侧"
  "上次另一个平台的时间选择器是 datepicker，这里应该也是"
```

---

## 5. 两篇内部文章的技术启发

### GUI Agent 搭建实践（文章1）

```text
核心技术点：
  1. 四大模块：设备环境、感知系统、决策系统、交互系统
  2. 感知→决策→执行循环（配合记忆增强防死循环）
  3. LangGraph 状态机工作流（优于硬编码）
  4. 坐标归一化：模型输出 0-1000 坐标系 → 按分辨率换算
  5. 中文输入方案：剪贴板粘贴规避 pyautogui 支持问题
  6. 操作指令解析器：9 种操作统一接口
```

### 多模态 UI 自动化综述（文章2）

```text
两大技术路线：

UI 大模型路线（Ferret-UI方向）：
  - 高分辨率视觉编码器
  - 大规模标注数据集（77,637个界面）
  - Any-Resolution 技术适配不同屏幕
  - 端到端方案，无额外模块依赖

MLLM-Agent 路线（Mobile-Agent方向）：
  - 视觉感知模块：OCR + 图标检测双引擎
  - 多 Agent 架构：规划→决策→反思三阶段
  - 高分辨率分析聚焦 UI 细节
  - 内存单元实现跨界面焦点追踪

对 GeoInfoAgent 的启发：
  1. 数据平台用 DOM 文本化方案（更快更准）
  2. 地图/卫星图用 OmniParser + 多模态感知
  3. 多 Agent 协作架构（规划、采集、验证分离）
  4. 合成数据 + 自我反思提升准确率
```

---

## 6. 一句话总结

> GUI Agent 是 Agentic RAG 的"最后一公里"：它把无法被 API 覆盖的高价值数据源也纳入了智能检索体系。DOM 文本化应对标准网页，截屏识别应对复杂界面，网络请求捕获实现从 GUI 到 API 的渐进式升级。
