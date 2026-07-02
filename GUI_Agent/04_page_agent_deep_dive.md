# 04. Page-Agent 详解：阿里纯前端 GUI Agent 方案

> 目标：深入理解阿里巴巴开源的 Page-Agent 项目（14K+ Stars）——DOM 文本化路线的最佳实践。
> 为什么重要：它提出了一种和 Claude Computer Use 完全不同的技术路线。
> 阅读时间：约 1.5 小时。

## 0. 一句话描述

> Page-Agent = 一个运行在网页内部的 JavaScript GUI Agent，通过 **DOM 文本化**（而非截图识别）来完成网页操作。不需要浏览器扩展、不需要 Python、不需要无头浏览器。

## 1. 核心理念：DOM 文本化 vs 截图识别

### 1.1 为什么选 DOM 文本化？

```
截图识别方案（Claude Computer Use）：
  截屏 → 传图片给多模态模型 → 模型识别按钮位置 → 输出坐标 → 点击

  问题：
  ❌ 每步都要截图 + 图片推理 → 慢（1-3秒/步）
  ❌ 多模态模型比文本模型贵得多
  ❌ 坐标可能不准（不同分辨率）
  ❌ 遇到动态页面、动画、加载态容易出错

DOM 文本化方案（Page-Agent）：
  提取 DOM 结构 → 转为带编号的文本 → 传给纯文本模型 → 输出编号 → 操作

  优势：
  ✅ 快（~0.5秒/步，不需要图片推理）
  ✅ 便宜（用文本模型，比多模态模型便宜 10-100 倍）
  ✅ 精确（编号直接对应 DOM 元素，不存在"猜坐标"问题）
  ✅ 不需要无头浏览器/截图
```

### 1.2 DOM 文本化的核心过程

```
原始 HTML DOM：
<div id="app">
  <button class="btn-primary">提交订单</button>
  <input type="text" placeholder="请输入姓名" />
  <a href="/help">帮助中心</a>
  <div class="modal">
    <button>取消</button>
    <button>确认支付</button>
  </div>
</div>

↓ Page-Agent 文本化 ↓

[1] <button> 提交订单 </button>
[2] <input> 输入框 placeholder="请输入姓名" </input>
[3] <a> 帮助中心 </a>
[4] <button> 取消 </button>
[5] <button> 确认支付 </button>

模型只需要输出：
  点击 [1]     → Page-Agent 自动定位到该 DOM 元素
  在 [2] 中输入 "张三"
  点击 [5]
```

## 2. 项目架构

```
┌──────────────────────────────────────────────┐
│              Page-Agent 架构                  │
│                                              │
│  ┌──────────────┐   ┌──────────────────────┐ │
│  │ page-agent   │   │  page-controller     │ │
│  │ (AI 决策层)  │◄──┤  (DOM 操作层)        │ │
│  │              │   │                      │ │
│  │ - 接收指令   │   │ - DOM 提取并编号      │ │
│  │ - 调用 LLM   │   │ - 高亮目标元素        │ │
│  │ - 决策下一步 │   │ - 执行点击/输入/滚动  │ │
│  │ - 多页协作   │   │ - 等待页面变化         │ │
│  └──────────────┘   └──────────────────────┘ │
│         │                    │               │
│         ▼                    ▼               │
│  ┌──────────────────────────────────────┐    │
│  │           LLM API                     │    │
│  │   OpenAI / Claude / DeepSeek / ...    │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 分层设计的精妙之处

- **page-agent**：AI 决策层，与具体 DOM 操作解耦。可以替换不同的 LLM
- **page-controller**：DOM 操作层，可独立复用于其他场景。处理所有浏览器 API 交互

> 这种分离意味着：换模型只需改 agent 层，换前端框架只需改 controller 层。

## 3. 关键代码解析

### 3.1 核心集成方式

```javascript
// 最简使用：一行 script 标签
<script type="module">
  import { PageAgent } from 'https://esm.sh/page-agent';
  
  const agent = new PageAgent({
    model: 'openai/gpt-4o-mini',  // 支持任意兼容 OpenAI API 的模型
    apiKey: 'sk-xxx',
    instruction: '帮我填写这个表单并提交',
  });
  
  await agent.run();
</script>
```

### 3.2 DOM 提取与编号（page-controller 核心）

```javascript
class PageController {
  // 提取页面上所有可交互元素，给每个元素编号
  extractInteractiveElements() {
    const elements = [];
    const selectors = 'button, a, input, select, textarea, [onclick], [role="button"]';
    
    document.querySelectorAll(selectors).forEach((el, index) => {
      // 跳过不可见元素
      if (!this.isVisible(el)) return;
      
      // 添加可视化标记（用 data-page-agent-id 属性）
      el.setAttribute('data-page-agent-id', index + 1);
      
      elements.push({
        id: index + 1,
        tag: el.tagName.toLowerCase(),
        type: el.type || '',
        text: this.getVisibleText(el),
        placeholder: el.placeholder || '',
        aria_label: el.getAttribute('aria-label') || '',
        rect: el.getBoundingClientRect(),
      });
    });
    
    return elements;
  }
  
  // 判断元素是否可见
  isVisible(el) {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return (
      style.display !== 'none' &&
      style.visibility !== 'hidden' &&
      style.opacity !== '0' &&
      rect.width > 0 &&
      rect.height > 0
    );
  }
  
  // 获取元素的可见文本（处理复杂嵌套）
  getVisibleText(el) {
    // 优先 aria-label
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label');
    // 再取 innerText（只包含可见文本）
    return el.innerText?.trim().substring(0, 100) || '';
  }
  
  // 高亮目标元素（给用户视觉反馈）
  highlightElement(elementId) {
    const el = document.querySelector(`[data-page-agent-id="${elementId}"]`);
    if (!el) return;
    
    // 红色闪烁边框
    el.style.outline = '3px solid red';
    el.style.outlineOffset = '2px';
    el.style.transition = 'outline 0.3s';
    
    setTimeout(() => {
      el.style.outline = '';
    }, 2000);
  }
}
```

### 3.3 多页协作（跨页面操作）

```javascript
class MultiPageAgent {
  // 支持跨页面/跨标签页的操作
  // 通过 Chrome Extension 实现标签页间通信
  
  async navigateToNewPage(url) {
    // 1. 在新标签页打开
    const newTab = await chrome.tabs.create({ url });
    
    // 2. 等待页面加载
    await this.waitForPageLoad(newTab.id);
    
    // 3. 在新标签页注入 Page-Agent
    await chrome.scripting.executeScript({
      target: { tabId: newTab.id },
      files: ['page-agent.js'],
    });
    
    return newTab;
  }
  
  // 标签页间通信
  async sendToTab(tabId, action) {
    return chrome.tabs.sendMessage(tabId, action);
  }
}
```

### 3.4 MCP 集成

```javascript
// Page-Agent 支持 MCP 协议
// 可以让其他 Agent 框架通过 MCP 控制浏览器

// MCP Server 暴露的工具
const MCP_TOOLS = {
  "page_agent_navigate": {
    description: "导航到指定 URL",
    parameters: { url: "string" },
  },
  "page_agent_click": {
    description: "点击指定编号的元素",
    parameters: { element_id: "number" },
  },
  "page_agent_type": {
    description: "在指定编号的输入框中输入文字",
    parameters: { element_id: "number", text: "string" },
  },
  "page_agent_get_dom": {
    description: "获取当前页面的可交互元素列表（带编号）",
    parameters: {},
  },
  "page_agent_screenshot": {
    description: "截取当前页面（可选，用于视觉验证）",
    parameters: {},
  },
};
```

## 4. 模型兼容性

Page-Agent 的设计哲学是"文本化 DOM → 文本模型"：

| 模型类型 | 兼容性 | 说明 |
|---|---|---|
| **GPT-4o / GPT-4o-mini** | ✅ 完美 | 推荐，性价比高 |
| **Claude 3.5 Sonnet / Haiku** | ✅ 完美 | 推荐，指令遵循好 |
| **DeepSeek-V3** | ✅ 良好 | 成本优势 |
| **Qwen 系列** | ✅ 良好 | 中文场景优秀 |
| **本地 Ollama 模型** | ⚠️ 需测试 | 取决于模型大小和指令遵循能力 |
| **多模态模型** | ✅ 可用 | 但浪费（不需要图片能力） |

## 5. 适用场景与局限

### ✅ 最适合的场景

```
1. 内部管理系统自动化
   - OA、ERP、CRM 等内部系统的自动化操作
   - 不需要 API，直接在页面上做事

2. 数据采集与表单填写
   - 跨系统数据同步
   - 批量信息录入

3. 工作流自动化
   - 审批流转
   - 多步骤操作自动化

4. 聊天/客服辅助
   - 自动填充工单信息
   - 知识库快速检索
```

### ❌ 不适用的场景

```
1. 桌面应用
   - Page-Agent 是纯 Web 方案，不能操作桌面软件
   - 需要 Claude Computer Use 或 UI-TARS

2. 非标准 Web（Canvas/WebGL 绘制）
   - DOM 文本化拿不到这些元素
   - 需要截图识别方案

3. DOM 极深的巨型页面
   - 可交互元素太多 → 模型上下文爆炸
   - 需要元素筛选策略

4. 高度动态的单页应用
   - DOM 频繁变化 → 编号可能失效
   - 需要实时刷新元素列表
```

## 6. 两路线对比总结

| | Page-Agent（DOM 文本化） | Claude Computer Use（截图识别） |
|---|---|---|
| **平台** | 仅 Web | 任意（Web/桌面/手机） |
| **速度** | ⚡ 快（~0.5s/步） | 🐢 慢（~1-3s/步） |
| **成本** | 💰 低（文本模型） | 💰💰💰 高（多模态模型） |
| **精度** | 🎯 高（元素编号直连 DOM） | 🎯 中（坐标推理） |
| **部署** | 📦 一行 script 标签 | 🖥️ 需要安装软件 |
| **隐私** | 🔒 数据可本地（自部署模型） | ☁️ 数据上传云端 |
| **适用** | Web 专用 | 全平台通用 |

## 7. 一句话总结

> Page-Agent 的核心创新是 **"DOM 文本化"**——把浏览器页面变成编号列表，让纯文本模型就能精准操作。这条路线的优势是**快、准、便宜**，代价是**只适用于 Web**。选择哪条路取决于你的场景是全平台通用还是 Web 专用。
