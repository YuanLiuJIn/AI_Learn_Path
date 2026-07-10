# CMA Data Agent：Playwright 实操项目

> 目标站点：`https://data.cma.cn`（中国气象数据网）
> 技术路线：**Playwright DOM 驱动为主，人工登录/验证码处理，网络请求捕获辅助转 API**。

这个项目不是用纯多模态截图点坐标，也不是依赖 Page-Agent bookmarklet。它更适合你的目标：

```text
进入数据服务 / 高级检索 → 填条件 → 查询 → 读取结果 → 下载或加入数据筐
```

## 目录结构

```text
cma_data_agent/
├── README.md
├── requirements.txt
├── setup_windows.cmd
├── config.example.json
├── login_save_session.py      # 人工登录一次，保存 cookies/session
├── explore_page.py            # 提取当前页 DOM、按钮、链接、输入框
├── search_dataset.py          # DOM-first 关键词检索
├── download_data.py           # 下载 / 加入数据筐（带确认）
├── capture_api.py             # 手动操作时捕获网络请求，寻找真实接口
├── cma_agent/
│   ├── __init__.py
│   └── common.py
├── storage/                   # 登录态保存位置（本地生成，不提交）
└── outputs/                   # 截图、DOM、网络日志、结果文本
```

## 0. 安全边界

- 不绕过验证码。
- 不保存明文账号密码。
- 第一次登录由你手动完成，然后保存浏览器登录态。
- 下载/加入数据筐前默认会暂停确认。
- 请遵守目标网站服务条款、下载权限和频率限制。

## 1. 安装环境（Windows）

在 PowerShell 或 CMD 中：

```powershell
cd d:\AI_Learn_Path\GUI_Agent\examples\cma_data_agent
.\setup_windows.cmd
```

它会自动：

```text
创建 .venv
安装 playwright
安装 Chromium 浏览器
```

后续每次使用前激活环境：

```powershell
cd d:\AI_Learn_Path\GUI_Agent\examples\cma_data_agent
.\.venv\Scripts\activate
```

如果 PowerShell 不允许执行激活脚本，也可以直接用：

```powershell
.\.venv\Scripts\python.exe explore_page.py
```

## 2. 第一次：保存登录态

如果下载数据需要登录，先运行：

```powershell
python login_save_session.py
```

浏览器会打开 `https://data.cma.cn`。
你手动完成登录、扫码或验证码，然后回到终端按 Enter。

脚本会保存：

```text
storage/cma_storage.json
```

后续脚本会自动复用。

## 3. 探索首页/检索页 DOM

```powershell
python explore_page.py
```

输出会保存在：

```text
outputs/*_interactive_elements.md
outputs/*_interactive_elements.json
outputs/*_screenshot.png
outputs/*_body_text.md
```

你可以用它确认页面上是否有：

```text
数据服务
高级检索
接口服务
下载
加入数据筐
关键词输入框
查询按钮
```

也可以指定 URL：

```powershell
python explore_page.py --url "https://data.cma.cn/某个页面"
```

## 4. 关键词检索

例如搜索“降水”：

```powershell
python search_dataset.py --keyword "降水"
```

如果你想手动调整筛选条件后再查询：

```powershell
python search_dataset.py --keyword "降水" --manual-before-query
```

脚本会尝试：

```text
打开网站
点击“高级检索/搜索”等入口
填写关键词
点击“查询/搜索/检索”
保存结果页面截图、DOM、文本、网络日志
```

如果自动找不到输入框或查询按钮，它会让你手动介入。

## 5. 捕获真实接口

很多数据站的前端查询背后都有接口。建议你运行：

```powershell
python capture_api.py
```

然后在浏览器里手动操作：

```text
进入高级检索
输入关键词
点击查询
点击详情或下载前一步
```

脚本会把疑似接口写入：

```text
outputs/*_network_responses.jsonl
```

如果发现稳定接口，后续可以不用 GUI，直接用 `requests` 批量下载。

## 6. 下载或加入数据筐

### 下载

先打开某个具体数据详情/结果页面：

```powershell
python download_data.py --url "目标详情页URL" --mode download
```

默认会暂停让你确认。确认后才会点“下载”。

如果你已经确认想直接执行：

```powershell
python download_data.py --url "目标详情页URL" --mode download --confirm
```

### 加入数据筐

```powershell
python download_data.py --url "目标详情页URL" --mode basket
```

如果按钮文字不是“下载”或“加入数据筐”，可以指定：

```powershell
python download_data.py --url "目标详情页URL" --mode download --click-text "立即下载"
```

## 7. 推荐工作流

```text
Step 1: python login_save_session.py
        手动登录一次，保存状态

Step 2: python explore_page.py
        看首页入口、按钮、链接

Step 3: python capture_api.py
        手动完成一次查询，捕获接口

Step 4: python search_dataset.py --keyword "降水" --manual-before-query
        自动化初步检索

Step 5: python download_data.py --url "详情页URL" --mode download
        测试单个下载

Step 6: 如果抓到接口，转 requests 批量下载
```

## 8. 为什么不用纯 Page-Agent？

Page-Agent bookmarklet 适合当前页面内探索，但你的任务涉及：

```text
跨页面
登录态
下载文件
加入数据筐
批量获取数据
```

这些更适合 Playwright。Page-Agent 可以辅助探索按钮名称和入口，但最终流程应固化为 Playwright 脚本。

## 9. 故障排查

### Playwright 浏览器未安装

```powershell
python -m playwright install chromium
```

### 登录态失效

重新运行：

```powershell
python login_save_session.py
```

### 自动点击不到按钮

先运行：

```powershell
python explore_page.py
```

查看 `outputs/*_interactive_elements.md` 里按钮真实文字，再调整脚本或使用 `--click-text`。

### 查询无结果

尝试：

```powershell
python search_dataset.py --keyword "降水" --manual-before-query
```

手动设置时间、站点、数据类型后再继续。
