from __future__ import annotations

import argparse

from cma_agent.common import attach_network_logger, browser_context, goto, pause_for_user, record_basic_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture network responses while manually operating data.cma.cn.")
    parser.add_argument("--url", default=None, help="Page URL. Defaults to config base_url.")
    parser.add_argument("--no-storage", action="store_true", help="Do not load saved login state.")
    args = parser.parse_args()

    with browser_context(headless=False, use_storage=not args.no_storage) as (_, _, _, page):
        log_path = attach_network_logger(page)
        goto(page, args.url)
        print(f"\n网络响应日志将写入：{log_path}")
        print("请在浏览器中手动执行一次查询/下载前的流程。")
        print("脚本会记录 URL 中包含 api/data/download/search/query 等关键词的响应。")
        pause_for_user("完成手动操作后，回到这里按 Enter 保存页面状态并退出...")
        artifacts = record_basic_artifacts(page, "capture_api_final")
        print("\n已保存页面状态：")
        for name, path in artifacts.items():
            print(f"- {name}: {path}")
        print(f"网络日志：{log_path}")


if __name__ == "__main__":
    main()
