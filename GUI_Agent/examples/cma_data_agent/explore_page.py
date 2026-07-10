from __future__ import annotations

import argparse

from cma_agent.common import browser_context, dump_json, dump_text, elements_to_markdown, extract_interactive_elements, goto, record_basic_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore current DOM structure of data.cma.cn pages.")
    parser.add_argument("--url", default=None, help="Page URL. Defaults to config base_url.")
    parser.add_argument("--no-storage", action="store_true", help="Do not load saved login state.")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode.")
    args = parser.parse_args()

    with browser_context(headless=args.headless, use_storage=not args.no_storage) as (_, _, _, page):
        goto(page, args.url)
        elements = extract_interactive_elements(page)
        json_path = dump_json(elements, "explore_interactive_elements.json")
        md_path = dump_text(elements_to_markdown(elements), "explore_interactive_elements.md")
        artifacts = record_basic_artifacts(page, "explore")

        print("\n已提取当前页面可交互元素。")
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")
        print("附加产物：")
        for name, path in artifacts.items():
            print(f"- {name}: {path}")

        print("\n前 30 个可交互元素：")
        for el in elements[:30]:
            print(f"[{el['index']}] <{el['tag']}> {el.get('text') or ''} {el.get('href') or ''}")


if __name__ == "__main__":
    main()
