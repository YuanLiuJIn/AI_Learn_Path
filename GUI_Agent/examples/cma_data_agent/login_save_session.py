from __future__ import annotations

from cma_agent.common import STORAGE_FILE, browser_context, ensure_dirs, goto, pause_for_user


def main() -> None:
    ensure_dirs()
    with browser_context(headless=False, use_storage=False) as (_, _, context, page):
        goto(page)
        print("\n已打开中国气象数据网。")
        print("请在浏览器中手动完成登录/扫码/验证码等操作。")
        print("注意：脚本不会尝试绕过验证码，也不会保存你的明文密码。")
        pause_for_user("确认页面已经登录成功后，回到这里按 Enter 保存登录态...")
        context.storage_state(path=str(STORAGE_FILE))
        print(f"\n登录态已保存到：{STORAGE_FILE}")
        print("后续脚本会自动复用这个 storage state。")


if __name__ == "__main__":
    main()
