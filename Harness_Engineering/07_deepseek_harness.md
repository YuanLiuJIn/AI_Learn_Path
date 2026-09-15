# 07 DeepSeek Harness 实战：生产级开源 Harness 源码解析

> 定位：前面 00~06 学的是 **Harness 工程方法论**（抽象层），本文看 **DeepSeek 官方开源实现**（具体层），
> 与 Hermes 专题互补：Hermes 看"产品如何打包记忆/自进化/安全"，本文看"生产级 Harness 的工程架构"。
> 配套源码：`/Users/aeiouliu/AI_Learn_Path/deepseek-harness`（本地已 clone + 构建 + 跑通）

## 1. 项目速览

| 项 | 内容 |
|---|---|
| 名称 | DeepSeek Harness（命令 `dsh`） |
| 定位 | DeepSeek 官方开源的 Agent Harness，连接"模型"与"外部世界" |
| 核心哲学 | **一切皆插件**（Everything is a plugin） |
| 底座 | [Cordis](https://github.com/cordiverse/cordis)（插件框架，基于"时空可组合性"编程范式） |
| 协议 | 支持 ACP（Agent Client Protocol）、JSON-RPC、Python SDK |
| 状态 | Developer preview（`0.1.0-rc`，接口会变） |
| 许可证 | MIT |
| 技术栈 | TypeScript monorepo（pnpm workspace），Node >= 22.19 |

**为什么它重要**：它把 `Agent = Model + Harness` 公式做成了可插拔的产品级实现——
模型路由、文件系统/进程沙箱、工具注册表、MCP 客户端、子代理委派、会话持久化、权限审批，全部是插件。
看懂它的分层方式，等于看懂现代生产 Harness 的标准答案之一。

## 2. 架构核心

### 2.1 Cordis：一切皆插件的底座

Cordis 提供**依赖注入 + 插件生命周期**：

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'my-plugin'
export const inject = ['tools']          // 声明依赖：tools 就绪后才加载本插件

export function apply(ctx: Context) {
  ctx.tools.register(/* ... */)          // 注册能力
  ctx.effect(() => () => console.log('unload'))  // 卸载时自动清理，无需手动 removeListener
}
```

- 三种插件形态：函数式（最常用）、对象式、类式（`extends Service`，给其他插件提供服务）
- **自动清理**：`ctx` 注册的一切（事件/工具/定时器）在插件卸载时自动回收
- **服务分层**：Service Definition / Service Provider / Consumer 三类包，可替换能力（如换一个沙箱实现）

### 2.2 Profile：插件束的堆叠（patch layer）

```
dsh --profile web   # 别名 = --profile web
```

一个 Profile = 一组**有序的插件束（bundle）补丁层**，从空根开始叠加：

```
空根
 └─ 每个 bundle 的 patch（dsh.profile.bundles 顺序）
     └─ profile 的 cordis.patch.yml（用户自己的覆盖层）
         └─ $DSH_HOME/cordis.patch.yml（全局层）
             └─ --patch 追加层
```

- 内置 Profile：`web`、`headless`（首次使用自动初始化）
- 查配置树：`dsh --profile web --dump-config`（不看效果、只看组合结果）
- 换层方式：`pnpm dsh web --patch ./my-patch.yml`

### 2.3 关键模块（packages/ 对应关系）

| 理论组件（00 笔记） | dsh 具体实现 |
|---|---|
| Model 路由 | `llm/*`：多提供方、OpenAI 兼容端点、可自定义 adapter |
| Sandbox（进程/文件隔离） | `sandbox/*` + `subprocess/*`：bash、fs、PTY、LSP 本地提供方；E2B 云沙箱 overlay |
| Tools | `tools/*`：`defineTool` DSL（参数 schema、输出渲染、后台任务、权限钩子） |
| 外部能力接入 | `mcp/*`：通用 MCP 客户端（如 mcp-memory 示例） |
| Subagent 委派 | `subagent/*`：子代理循环、独立会话 |
| 会话持久化 | `session/*`：JSONL 持久化、checkpoint/恢复 |
| 上下文管理 | agent 上下文窗口 + 计划维护 + 委派 |
| 权限审批 | 会话级权限策略，Web UI 交互审批 |
| UI | `client/*`（React Web 前端）+ `host/*`（服务端） |

## 3. 环境搭建（macOS 实测）

```sh
# 1. Node >= 22.19（实测用 24.14.0）+ pnpm 11.7
npm install -g pnpm@11.7.0

# 2. 源码 + 依赖 + 构建
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install      # 约 4 分钟（大 monorepo）
pnpm run build    # 构建产物（frontend + packages）

# 3. 启动 Web UI
pnpm dsh web                 # 默认 http://127.0.0.1:3080 并自动开浏览器
pnpm dsh web --no-open       # 不自动开浏览器（SSH 环境）
```

**坑**：
- `git clone` 在受限网络下易 SSL 超时 → 用 `curl -L codeload.github.com/.../zip/refs/heads/master` 下载 zip 解压
- 默认分支是 `master` 不是 `main`
- pnpm 11.7.0 要求 Node >= 22.13，Node 22.12 会拒绝安装
- engines 只警告不阻止，但低版本 Node 可能出奇怪问题，尽量满足

## 4. 上手路径（四种模式）

### 4.1 Web UI（推荐入门）

1. `pnpm dsh web` 启动后打开 `http://127.0.0.1:3080`
2. **设置 → 模型**：填 DeepSeek API Key（或自定义 OpenAI 兼容端点），立即生效无需重启
3. **选择工作区**：添加启动 dsh 所在目录并选中（未选工作区前输入框不可用）
4. 发送任务：`Summarize this repository and identify its main packages.`
5. Agent 可读写文件、跑命令、委派子代理、维护计划；权限策略触发审批时 UI 会询问

### 4.2 headless（无人值守编码 agent）

```sh
# 根目录 .env（gitignored）：
#   DEEPSEEK_API_KEY=sk-…
pnpm dsh --profile headless "fix the failing test in this workspace"
```

接受一个任务 → 创建并持久化全新会话 → 打印最终回复 → 退出。

### 4.3 Python SDK

`docs/user/guide/python-sdk.md`：通过 Python 驱动 dsh（JSON-RPC 通道），适合做评测/批量跑任务的自动化。

### 4.4 ACP（Agent Client Protocol）

`dsh acp-agent`：面向程序化客户端的自动化服务器，支持会话、权限、取消（Cline 等客户端可对接）。

## 5. 插件开发三步（动手验证）

```sh
mkdir -p scratch-plugin/src
```

**Step 1：第一个插件** `scratch-plugin/src/my-plugin.ts`

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello-plugin'
export function apply(ctx: Context) {
  console.log('[hello-plugin] plugin loaded!')
}
```

**Step 2：注册到覆盖层** `scratch-plugin/cordis.yml`

```yaml
- insert:
    - id: hello
      name: '/absolute/path/to/deepseek-harness/scratch-plugin/src/my-plugin.ts'
```

```sh
pnpm dsh web --patch ./scratch-plugin/cordis.yml   # 启动日志出现 plugin loaded!
```

**Step 3：注册一个工具**（替换 my-plugin.ts）

```ts
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'greet-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'greet',
    description: 'Greet someone by name.',
    parameters: { name: { type: 'string', required: true, description: 'The name to greet' } },
    output: { schema: { type: 'string' }, render: (_args, value) => [{ type: 'text', text: value }] },
    async execute(args) { return `Hello, ${args.name}!` },
  }))
}
```

在 Web UI 里输入 `Use the greet tool to greet Ada.`，模型即可调用 `greet` 并得到 `Hello, Ada!`。
`defineTool` 自动从 `parameters` 推导类型和校验；`execute` 返回规范值，`render` 转成面向模型的内容。

## 6. 示例地图（examples/）

| 示例 | 演示点 | 命令 |
|---|---|---|
| `headless-agent` | 非交互 agent：任务→结果，JSONL 持久化 | `pnpm dsh --profile headless "task"` |
| `jsonrpc-agent` | Python SDK / JSON-RPC 无人值守 agent | 见其 README |
| `acp-agent` | ACP 协议服务器（会话/权限/取消） | `dsh --profile acp-agent` |
| `mcp-memory` | MCP 客户端接第三方记忆服务器 | 见其 README |
| `web-cordis` | 自指 agent：检查并修改内存中插件树 | 见其 README |
| `web-schedule` | 会话内持久提醒（schedule_create/list/delete） | `dsh web --patch examples/web-schedule/cordis.yml` |

## 7. 命令速查

```sh
pnpm dsh --help                         # launcher 帮助
pnpm dsh web --help                     # web 应用自己的参数
pnpm dsh --profile headless "job"       # 单任务跑完即退出
pnpm dsh --profile web --dump-config    # 打印组合后的完整配置树
pnpm dsh web --patch ./x.yml            # 追加补丁层
pnpm dsh plugin --profile <name> <args> # 管理 profile 的插件（转发给 pnpm）
pnpm mock:llm                           # 启动 mock LLM 服务器（无 key 测试）
```

## 8. 与理论笔记的对照感悟

1. **00 笔记"四大组件"→ dsh**：Guides→Profile/patch 层；Sensors→工具/事件；Loop→agent 循环插件；Context→会话/记忆。全部可替换 = 插件化。
2. **Agent Loop 深挖（03）**：dsh 的 agent loop 不是一个写死的循环，而是可被插件替换/叠加的行为——改行为 = 换插件，而不是改代码。
3. **沙箱（05/06）**：dsh 默认本地 bash/fs/PTY/LSP 沙箱，E2B 示例演示了把沙箱整体换成云沙箱（Provider 替换），印证"decoupling brain from hands"。
4. **权限治理**：审批不是写死在循环里，而是**会话级权限策略**，UI 交互触发——Harness 的"引导/约束"落到了产品层。

## 9. 下一步学习建议

- 无 API Key 也能玩：`pnpm mock:llm` 起 mock 模型，配合 cordis-tutorial 在临时目录构建插件
- 深挖 Cordis：`docs/cordis-tutorial/`（从头搭插件框架）、`docs/cordis-primer.md`
- 插件进阶：`docs/user/develop/basic/{tool,config,publish}` → `docs/user/develop/framework/`（服务与依赖）
- 按需翻 cookbook：`docs/cookbook/adding-a-tool.md`、`adding-an-llm-adapter.md`、`adding-a-settings-card.md`
- 阅读顺序推荐：architecture → cordis-primer → user/guide → develop/basic → 选一个 example 跑起来 → 写自己的工具插件

> 一句话总结：**deepseek-harness 把 Harness 工程的每个子系统都做成了 Cordis 插件，profile 是插件的"装配单"，patch 层是用户的"改装件"，学会它 = 学会一套可复用的 Harness 产品化骨架。**
