# 07. 实战：从零搭建 Hermes 并培养你自己的助手

> 目标：跟随本章从零完成 Hermes 的部署、配置、接入企微，并像养宠物一样训练你自己的助手。
> 前置要求：有一个 AnyDev 容器或 Linux 环境。Python ≥3.11。

## 1. 环境搭建

### 1.1 拉取代码

```bash
# 拉取 AnyDev 容器（内网环境）
cd /data/workspace

# 源码安装（推荐，方便看代码）
git clone <hermes-agent仓库地址>
cd hermes-agent
./setup-hermes.sh

# 如果缺少依赖，直接把报错丢给 CodeBuddy
# （实测：自动检测到 Python 3.10 不够，用 uv 安装了 3.11）
```

### 1.2 配置模型

编辑 `~/.hermes/config.yaml`：

```yaml
model:
  default: "claude-sonnet-4-6"
  provider: "venus"

providers:
  venus:
    api: "http://v2.open.venus.oa.com/llmproxy"
    key_env: "VENUS_API_KEY"
    default_model: "claude-sonnet-4-6"
```

```bash
# 设置 API Key
export VENUS_API_KEY="your-key-here"
```

### 1.3 创建软链（可选）

```bash
mkdir -p ~/.local/bin
ln -sf /data/workspace/hermes-agent/venv/bin/hermes ~/.local/bin/hermes
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 2. 接入企微机器人

### 2.1 创建工作台机器人

1. 企业微信工作台 → 创建机器人
2. 选择 API 模式
3. 复制 BotID 和 Secret

### 2.2 配置连接

编辑 `~/.hermes/.env`：

```bash
# 企业微信智能机器人（WebSocket 长连接）
WECOM_BOT_ID=***
WECOM_SECRET=***

# Gateway 访问控制（先开放，调通后再限制）
GATEWAY_ALLOW_ALL_USERS=true

# 全信任模式 — 自动批准所有命令，不弹确认
# ⚠️ 仅调试用！生产必须关闭！
HERMES_YOLO=true
```

### 2.3 启动 Gateway

```bash
# 方式 1：后台启动
nohup hermes gateway run > /tmp/hermes_gateway.log 2>&1 &

# 方式 2：标准启动
hermes gateway start

# 查看状态
hermes gateway status

# 查看日志
tail -f ~/.hermes/logs/gateway.log
```

## 3. 验证和常用命令

```bash
# 启动 CLI 交互（测试是否通）
hermes

# 选择模型
hermes model

# 配置工具
hermes tools

# Gateway 管理
hermes gateway setup  # 交互式配置平台
hermes gateway status

# 定时任务
hermes cron list

# 诊断问题
hermes doctor

# 更新版本
hermes update
```

## 4. 从零培养一个排查助手

这是 Hermes 最具特色的实战场景。我们一步步来。

### Step 1：建立用户画像

用自然语言告诉 Hermes 你是谁、做什么、代码在哪：

```
我是一名程序员，负责广告投放后端开发，主要负责：

1. 一致性模块
   代码在 /data/workspace/consistency
   核心职责：保证广告投放数据在多个系统间的一致性

2. 消息中心
   代码在 /data/workspace/message-center
   核心职责：处理审核通知的推送和回调

排查技巧：
- 消息中心日志 index: newbiz_message_center
- API 消费日志 index: mkt_developer_log
- 日志查询 API 文档在: https://zhiyan.woa.com/docs/...
```

**发生了什么？**
- Hermes 把你说的内容记入 `~/.hermes/memories/USER.md`（用户画像）
- 下次对话时，这些信息会自动作为 System Prompt 的一部分
- 你不再需要重复自我介绍

### Step 2：第一次手把手带（教它排查流程）

发一个真实的排查请求：

```
京东反馈了一个商家 case：
创意通过但审核信息京东没收到

广告主ID：222
广告ID：123
DCID：44444

请按以下步骤排查：
1. 先查消息中心日志 (newbiz_message_center)，搜索 dcid=44444
   确认消息是否真的生产了
2. 查消费日志，确认消息是否自动消费成功、下发通知
3. 查 API 消费日志 (mkt_developer_log)，搜索 dcid=44444
   确认是否消费成功并向用户回调地址推送
4. 给出结论：能不能正常推送？要有充分证据，不能靠猜
```

**Agent 会做什么：**
- 调用 zhiyan 日志查询 API
- 可能需要你纠正几次（告诉它 API 参数怎么填）
- 最终给出四步排查结论

**此时你已经完成第一次"手把手教学"！**

### Step 3：等待后台自动沉淀

这次对话结束后，Hermes 的 Background Review 会在后台：

1. **更新用户画像**：记住你的排查偏好
2. **创建 Skill**：把"消息中心四步排查流程"自动沉淀为一个可复用 Skill

你完全不需要手动做任何事情。

### Step 4：新对话验证（它自己能做了）

```bash
hermes /new  # 开启全新对话
```

```
用户：dcid=55555，同样的问题，帮我排查
```

**Hermes 会自动**：
- 调出上次沉淀的排查 Skill
- 按"消息生产 → 消费 → 通知下发 → API 推送"四步执行
- 给出有数据支撑的结论

这就是"越用越懂你"的实际效果。

## 5. 安全收口清单（部署前必查）

### 5.1 关闭全用户访问

```bash
# ~/.hermes/.env
GATEWAY_ALLOW_ALL_USERS=false
GATEWAY_ALLOWED_USERS=你的企微ID
```

### 5.2 关闭 YOLO 模式

```bash
HERMES_YOLO=false  # 恢复正常审批流程
```

### 5.3 保护记忆文件

```bash
# ~/.hermes/memories/MEMORY.md 和 USER.md 是普通文本
# 注意文件权限
chmod 600 ~/.hermes/memories/MEMORY.md
chmod 600 ~/.hermes/memories/USER.md
```

## 6. Curator 的使用

```bash
# 预览模式：只生成报告，不做实际变更
hermes curator run --dry-run

# 查看预览报告
cat REPORT.md

# 确认无误后正式运行
hermes curator run
```

## 7. 进阶技巧

### 7.1 手动触发 Background Review

```bash
# 不等计数器自动触发，手动强制复查上一轮对话
hermes review --last-session
```

### 7.2 查看当前记忆

```bash
# 查看 Agent 记了关于你的什么
cat ~/.hermes/memories/USER.md

# 查看 Agent 自己的笔记
cat ~/.hermes/memories/MEMORY.md

# 查看已创建的技能
ls -la ~/.hermes/skills/
```

### 7.3 手动管理技能

```
# 在对话中直接让 Agent 帮你管理
"帮我把 server-debug 这个 Skill 里过时的那步删掉"
"我最近一个月没用过 db-backup 这个技能，帮我归档掉"
```

## 8. 常见问题排查

```bash
# Q: Gateway 启不来？
hermes doctor  # 诊断常见问题

# Q: Agent 回复很慢？
tail -f ~/.hermes/logs/gateway.log  # 看是否有超时

# Q: 企微收不到消息？
hermes gateway status  # 检查 Gateway 状态
# 确认 WECOM_BOT_ID 和 WECOM_SECRET 正确

# Q: 模型调用失败？
# 检查 ~/.hermes/config.yaml 的 provider 配置
# 检查 API Key 是否过期
```

## 9. 一句话总结

> Hermes 的实战上手分三步：**搭环境（10 分钟）→ 接入企微（10 分钟）→ 像带新人一样带 Agent 做一次任务（30 分钟）**。之后 Agent 会在后台自动学习，你只需要正常使用，它会越来越懂你。
