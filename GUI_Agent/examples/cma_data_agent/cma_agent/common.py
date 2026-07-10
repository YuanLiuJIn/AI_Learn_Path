from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, TimeoutError, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "config.example.json"
STORAGE_DIR = ROOT / "storage"
OUTPUT_DIR = ROOT / "outputs"
STORAGE_FILE = STORAGE_DIR / "cma_storage.json"
BASE_URL = "https://data.cma.cn"


def ensure_dirs() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def output_path(name: str) -> Path:
    ensure_dirs()
    return OUTPUT_DIR / f"{timestamp()}_{name}"


@contextmanager
def browser_context(
    *,
    headless: bool = False,
    use_storage: bool = True,
    accept_downloads: bool = True,
) -> Iterable[tuple[Playwright, Browser, BrowserContext, Page]]:
    """Create a Chromium context with optional saved login state."""
    ensure_dirs()
    config = load_config()
    viewport = config.get("viewport", {"width": 1365, "height": 900})
    slow_mo = int(config.get("slow_mo_ms", 150))
    nav_timeout = int(config.get("navigation_timeout_ms", 30000))
    action_timeout = int(config.get("action_timeout_ms", 8000))

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless, slow_mo=slow_mo)

    storage_state = str(STORAGE_FILE) if use_storage and STORAGE_FILE.exists() else None
    context = browser.new_context(
        storage_state=storage_state,
        accept_downloads=accept_downloads,
        viewport=viewport,
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    context.set_default_navigation_timeout(nav_timeout)
    context.set_default_timeout(action_timeout)
    page = context.new_page()

    try:
        yield pw, browser, context, page
    finally:
        context.close()
        browser.close()
        pw.stop()


def goto(page: Page, url: str | None = None) -> None:
    target = url or load_config().get("base_url", BASE_URL)
    page.goto(target, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except TimeoutError:
        pass


def safe_filename(value: str, default: str = "file") -> str:
    value = re.sub(r"[\\/:*?\"<>|\s]+", "_", value).strip("_")
    return value[:80] or default


def dump_json(data: Any, name: str) -> Path:
    path = output_path(name)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def dump_text(data: str, name: str) -> Path:
    path = output_path(name)
    path.write_text(data, encoding="utf-8")
    return path


def extract_interactive_elements(page: Page) -> list[dict[str, Any]]:
    """Extract visible interactive DOM elements.

    This is intentionally similar to Page-Agent's DOM-first idea: read DOM, not screenshots.
    """
    return page.evaluate(
        """
() => {
  const selectors = [
    'a', 'button', 'input', 'select', 'textarea',
    '[role="button"]', '[role="link"]', '[role="tab"]',
    '[onclick]', '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  const visible = (el) => {
    const style = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return style.display !== 'none' &&
      style.visibility !== 'hidden' &&
      Number(style.opacity || '1') > 0 &&
      rect.width > 0 && rect.height > 0;
  };

  const textOf = (el) => {
    const parts = [
      el.innerText,
      el.getAttribute('aria-label'),
      el.getAttribute('title'),
      el.getAttribute('placeholder'),
      el.getAttribute('value'),
      el.getAttribute('name'),
      el.id,
    ].filter(Boolean).map(x => String(x).trim()).filter(Boolean);
    return Array.from(new Set(parts)).join(' | ').slice(0, 200);
  };

  return Array.from(document.querySelectorAll(selectors))
    .filter(visible)
    .slice(0, 500)
    .map((el, index) => {
      const rect = el.getBoundingClientRect();
      return {
        index: index + 1,
        tag: el.tagName.toLowerCase(),
        type: el.getAttribute('type') || '',
        text: textOf(el),
        href: el.href || el.getAttribute('href') || '',
        id: el.id || '',
        name: el.getAttribute('name') || '',
        role: el.getAttribute('role') || '',
        placeholder: el.getAttribute('placeholder') || '',
        value: el.getAttribute('value') || '',
        disabled: !!el.disabled,
        rect: {
          x: Math.round(rect.x), y: Math.round(rect.y),
          width: Math.round(rect.width), height: Math.round(rect.height)
        }
      };
    });
}
"""
    )


def elements_to_markdown(elements: list[dict[str, Any]]) -> str:
    rows = ["| # | tag | text | href |", "|---:|---|---|---|"]
    for el in elements:
        text = str(el.get("text", "")).replace("|", "\\|").replace("\n", " ")
        href = str(el.get("href", "")).replace("|", "\\|")
        rows.append(f"| {el.get('index')} | `{el.get('tag')}` | {text} | {href} |")
    return "\n".join(rows) + "\n"


def click_by_text(page: Page, texts: list[str], *, exact: bool = False) -> str | None:
    """Try to click the first visible element containing one of the candidate texts."""
    for text in texts:
        candidates = [
            page.get_by_role("link", name=re.compile(re.escape(text), re.I)),
            page.get_by_role("button", name=re.compile(re.escape(text), re.I)),
            page.get_by_text(text, exact=exact),
        ]
        for locator in candidates:
            try:
                first = locator.first
                if first.count() > 0:
                    first.click()
                    return text
            except Exception:
                continue
    return None


def fill_keyword_input(page: Page, keyword: str) -> str | None:
    """Fill the most likely keyword/search input."""
    locators = [
        page.get_by_placeholder(re.compile("关键词|搜索|请输入|查询", re.I)),
        page.locator("input[type='search']"),
        page.locator("input[type='text']"),
        page.locator("input:not([type])"),
    ]
    for locator in locators:
        try:
            first = locator.first
            if first.count() > 0 and first.is_visible():
                first.fill(keyword)
                return "filled"
        except Exception:
            continue
    return None


def extract_table_text(page: Page) -> str:
    """Extract visible table/list-like text for quick inspection."""
    chunks: list[str] = []
    for selector in ["table", ".table", ".list", ".result", ".data", "body"]:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                text = locator.inner_text(timeout=3000)
                if text.strip():
                    chunks.append(f"## selector: {selector}\n{text.strip()}")
                    if selector != "body":
                        break
        except Exception:
            continue
    return "\n\n".join(chunks)


def pause_for_user(message: str = "操作完成后按 Enter 继续...") -> None:
    input(f"\n{message}\n")


def record_basic_artifacts(page: Page, prefix: str) -> dict[str, str]:
    """Save screenshot, DOM elements JSON/MD and body text."""
    ensure_dirs()
    shot = output_path(f"{prefix}_screenshot.png")
    page.screenshot(path=str(shot), full_page=True)

    elements = extract_interactive_elements(page)
    elements_json = dump_json(elements, f"{prefix}_interactive_elements.json")
    elements_md = dump_text(elements_to_markdown(elements), f"{prefix}_interactive_elements.md")
    text = dump_text(page.locator("body").inner_text(timeout=5000), f"{prefix}_body_text.md")

    return {
        "screenshot": str(shot),
        "interactive_elements_json": str(elements_json),
        "interactive_elements_md": str(elements_md),
        "body_text": str(text),
    }


def attach_network_logger(page: Page, output_name: str = "network_responses.jsonl") -> Path:
    """Attach a lightweight response logger and return the output path."""
    ensure_dirs()
    config = load_config()
    keywords = [k.lower() for k in config.get("network_capture_keywords", [])]
    path = output_path(output_name)

    def on_response(response) -> None:
        url = response.url
        lower = url.lower()
        if keywords and not any(k in lower for k in keywords):
            return
        item = {
            "ts": time.time(),
            "status": response.status,
            "url": url,
            "method": response.request.method,
            "resource_type": response.request.resource_type,
            "content_type": response.headers.get("content-type", ""),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    page.on("response", on_response)
    return path
