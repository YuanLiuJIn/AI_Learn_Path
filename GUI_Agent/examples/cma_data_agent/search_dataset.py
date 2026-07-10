from __future__ import annotations

import argparse

from cma_agent.common import (
    attach_network_logger,
    browser_context,
    click_by_text,
    dump_text,
    extract_table_text,
    fill_keyword_input,
    goto,
    pause_for_user,
    record_basic_artifacts,
)

ADVANCED_SEARCH_TEXTS = ["高级检索", "高级搜索", "检索", "搜索"]
QUERY_TEXTS = ["查询", "搜索", "检索", "提交"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search datasets on data.cma.cn using DOM-first Playwright automation.")
    parser.add_argument("--keyword", required=True, help="Keyword to search, e.g. 降水 / 气温 / 地面气象")
    parser.add_argument("--url", default=None, help="Start URL. Defaults to config base_url.")
    parser.add_argument("--no-storage", action="store_true", help="Do not load saved login state.")
    parser.add_argument("--skip-open-advanced", action="store_true", help="Do not click advanced search first.")
    parser.add_argument("--manual-before-query", action="store_true", help="Pause before clicking query, for manual field adjustment.")
    args = parser.parse_args()

    with browser_context(headless=False, use_storage=not args.no_storage) as (_, _, _, page):
        network_log = attach_network_logger(page)
        goto(page, args.url)

        if not args.skip_open_advanced:
            clicked = click_by_text(page, ADVANCED_SEARCH_TEXTS)
            if clicked:
                print(f"已点击入口：{clicked}")
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
            else:
                print("未自动找到“高级检索/搜索”入口。将继续在当前页尝试填写关键词。")

        filled = fill_keyword_input(page, args.keyword)
        if not filled:
            print("未自动找到关键词输入框。")
            pause_for_user("请在浏览器中手动输入关键词和筛选条件，然后按 Enter 继续点击查询...")

        if args.manual_before_query:
            pause_for_user("请检查/调整筛选条件。准备点击查询时按 Enter...")

        clicked_query = click_by_text(page, QUERY_TEXTS)
        if clicked_query:
            print(f"已点击查询按钮：{clicked_query}")
        else:
            print("未自动找到查询按钮。请在浏览器中手动点击查询。")
            pause_for_user("手动点击查询并等待结果出现后，按 Enter 继续提取结果...")

        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass

        artifacts = record_basic_artifacts(page, "search_result")
        table_text = extract_table_text(page)
        result_path = dump_text(table_text or "未提取到明显结果文本。", "search_result_text.md")

        print("\n搜索流程完成。输出文件：")
        for name, path in artifacts.items():
            print(f"- {name}: {path}")
        print(f"- result_text: {result_path}")
        print(f"- network_log: {network_log}")
        print("\n如果 network_log 中出现稳定 API，可把后续批量下载改成 requests。")


if __name__ == "__main__":
    main()
