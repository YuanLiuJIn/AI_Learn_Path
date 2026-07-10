# 03. GUI Agent 采集引擎设计

---

## 1. 引擎架构

```text
采集入口 → 数据源路由器
              ↓
         ┌────┴────┐
         ↓         ↓
    DOM文本化    截屏识别
    (标准网页)   (地图/Canvas)
         ↓         ↓
     表单填写    坐标操作
         ↓         ↓
     结果提取    网络拦截
         ↓         ↓
         └────┬────┘
              ↓
         数据标准化
```

---

## 2. 混合感知方案

```python
class HybridPerception:
    """DOM文本化 + 截屏识别混合感知"""
    
    def __init__(self):
        self.dom_agent = DOMAgent()      # Playwright + 元素提取
        self.vision_agent = VisionAgent()  # OmniParser + Gemini Flash
    
    def perceive(self, page, data_source_type):
        if data_source_type == "form_based":
            # 标准 HTML 表单 → DOM 文本化
            elements = self.dom_agent.extract_interactive_elements(page)
            return self.dom_agent.textify(elements)
        
        elif data_source_type == "map_based":
            # 地图/卫星图/Canvas → 截图识别
            screenshot = self.vision_agent.capture(page)
            parsed = OmniParser.parse(screenshot)
            return parsed  # [{id, type, text, bbox}, ...]
        
        elif data_source_type == "hybrid":
            # 先 DOM，DOM 解决不了再截图
            dom_result = self.dom_agent.extract(page)
            if dom_result.confidence < 0.7:
                return self.vision_agent.fallback(page, dom_result)
            return dom_result
```

---

## 3. 操作指令解析器

```python
class ActionParser:
    """支持 9 种操作的统一解析器"""
    
    ACTIONS = {
        "click":        lambda args: pyautogui.click(args["x"], args["y"]),
        "type":         lambda args: paste_text(args["text"]),
        "hotkey":       lambda args: pyautogui.hotkey(*args["keys"]),
        "scroll":       lambda args: pyautogui.scroll(args["amount"]),
        "drag":         lambda args: pyautogui.drag(args["x2"]-args["x1"], args["y2"]-args["y1"]),
        "wait":         lambda args: time.sleep(args["seconds"]),
        "screenshot":   lambda args: pyautogui.screenshot(),
        "right_click":  lambda args: pyautogui.rightClick(args["x"], args["y"]),
        "double_click": lambda args: pyautogui.doubleClick(args["x"], args["y"]),
    }
    
    def parse_and_execute(self, action_json):
        action_type = action_json["action"]
        params = self.normalize_coordinates(action_json["params"])
        return self.ACTIONS[action_type](params)
    
    def normalize_coordinates(self, params):
        """0-1000 相对坐标 → 实际像素"""
        if "x" in params:
            params["x"] = int(params["x"] / 1000 * self.screen_width)
        if "y" in params:
            params["y"] = int(params["y"] / 1000 * self.screen_height)
        return params
```

---

## 4. 记忆增强防死循环

```python
class LoopDetector:
    """检测并防止操作死循环"""
    
    def __init__(self):
        self.action_history = []
        self.MAX_REPEAT = 3  # 连续3次同屏同操作 → 死循环
    
    def is_loop(self, action, current_screenshot_hash):
        recent = self.action_history[-5:]
        same = [a for a in recent 
                if a["action"] == action["type"] 
                and a["screenshot_hash"] == current_screenshot_hash]
        
        if len(same) >= self.MAX_REPEAT:
            return True, "检测到死循环，切换策略或请求人工介入"
        
        self.action_history.append({
            "action": action["type"],
            "screenshot_hash": current_screenshot_hash,
        })
        return False, None
```

---

## 5. 网络请求捕获（GUI→API 升级路径）

```python
class APISniffer:
    """捕获 GUI 操作背后的真实 API，为后续批量请求做准备"""
    
    def __init__(self, page):
        self.captured_apis = []
        page.on("response", self._on_response)
    
    def _on_response(self, response):
        url = response.url
        if any(kw in url.lower() for kw in ["api", "data", "download", "search"]):
            self.captured_apis.append({
                "url": url,
                "method": response.request.method,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
                "body": response.request.post_data if response.request.method == "POST" else None,
            })
    
    def suggest_api_upgrade(self):
        """分析捕获到的 API，建议是否可以从 GUI 升级到 API"""
        stable_apis = [api for api in self.captured_apis if api["status"] == 200]
        if len(stable_apis) >= 2:
            return {
                "upgrade_possible": True,
                "recommended_apis": stable_apis,
                "speedup_estimate": f"{len(stable_apis)}x faster than GUI",
            }
        return {"upgrade_possible": False}
```

---

## 6. LangGraph 工作流

```python
from langgraph.graph import StateGraph, END

class GUIWorkflowState(TypedDict):
    task: dict           # {location, metric, timerange, source}
    screenshot_path: str
    current_step: int
    max_steps: int
    action_history: list
    result: dict
    status: str

def build_gui_workflow():
    """截图→模型决策→执行→检查→循环"""
    workflow = StateGraph(GUIWorkflowState)
    
    workflow.add_node("capture",   capture_screenshot)    # 截图
    workflow.add_node("decide",    model_decide_action)   # 模型决策
    workflow.add_node("execute",   execute_action)        # 执行操作
    workflow.add_node("check",     check_completion)      # 检查完成
    
    workflow.set_entry_point("capture")
    workflow.add_edge("capture", "decide")
    workflow.add_edge("decide", "execute")
    workflow.add_edge("execute", "check")
    
    workflow.add_conditional_edges(
        "check",
        lambda s: "capture" if s["status"] == "continue" else END,
        {"capture": "capture", END: END}
    )
    
    return workflow.compile()
```
