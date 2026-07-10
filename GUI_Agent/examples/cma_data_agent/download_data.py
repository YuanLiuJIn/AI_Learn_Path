from __future__ import annotations

import argparse
from pathlib import Path

from cma_agent.common import browser_context, click_by_text, goto, pause_for_user, safe_filename, timestamp

DOWNLOAD_TEXTS = ["下载", "数据下载", "立即下载", "极速下载"]
BASKET_TEXTS = ["加入数据筐", "数据筐", "加入购物车", "加入订单"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download or add datasets to basket on data.cma.cn.")
    parser.add_argument("--url", default=None, help="Result/detail page URL. Defaults to config base_url.")
    parser.add_argument("--mode", choices=["download", "basket"], default="download")
    parser.add_argument("--click-text", default=None, help="Override button text to click.")
    parser.add_argument("--confirm", action="store_true", help="Actually click. Without this, script pauses for confirmation.")
    parser.add_argument("--no-storage", action="store_true", help="Do not load saved login state.")
    args = parser.parse_args()

    with browser_context(headless=False, use_storage=not args.no_storage) as (_, _, _, page):
        goto(page, args.url)
        print("\n页面已打开。")
        print("如果需要登录/验证码/扫码，请手动处理；脚本不会绕过。")

        if not args.confirm:
            pause_for_user("确认当前页面和按钮无误后按 Enter 继续；如不想执行请 Ctrl+C 退出...")

        texts = [args.click_text] if args.click_text else (DOWNLOAD_TEXTS if args.mode == "download" else BASKET_TEXTS)

        if args.mode == "download":
            download_dir = Path("downloads")
            download_dir.mkdir(exist_ok=True)
            try:
                with page.expect_download(timeout=15000) as download_info:
                    clicked = click_by_text(page, texts)
                    if not clicked:
                        raise RuntimeError(f"未找到下载按钮：{texts}")
                download = download_info.value
                suggested = safe_filename(download.suggested_filename, "cma_download")
                target = download_dir / f"{timestamp()}_{suggested}"
                download.save_as(str(target))
                print(f"\n下载完成：{target.resolve()}")
            except Exception as exc:
                print(f"\n未捕获到浏览器下载事件：{exc}")
                print("可能原因：按钮不是直接下载、需要登录/下单、或触发异步生成订单。")
                print("建议先运行 capture_api.py 捕获网络请求。")
        else:
            clicked = click_by_text(page, texts)
            if clicked:
                print(f"已点击：{clicked}")
                print("请在页面上确认是否已加入数据筐/订单。")
            else:
                print(f"未找到可点击按钮：{texts}")


if __name__ == "__main__":
    main()
