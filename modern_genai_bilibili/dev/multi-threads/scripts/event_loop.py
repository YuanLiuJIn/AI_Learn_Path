# import asyncio
# import time

# async def toast_bread():
#     print("开始烤面包...")
#     await asyncio.sleep(3) 
#     print("面包烤好了")

# async def brew_coffee():
#     print("开始冲咖啡...")
#     await asyncio.sleep(1)
#     print("咖啡冲好了")

# async def main():
#     start_time = time.time()  # 记录开始时间
    
#     # 并发运行
#     await asyncio.gather(toast_bread(), brew_coffee())
    
#     end_time = time.time()    # 记录结束时间
#     print(f"------------\n总耗时: {end_time - start_time:.2f} 秒")

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import threading  # 引入线程模块用来查看ID
# import time

# async def toast_bread():
#     # 打印当前线程 ID
#     print(f"[面包] 正在运行，线程 ID: {threading.get_ident()}")
#     print("开始烤面包...")
#     await asyncio.sleep(3) 
#     print(f"[面包] 烤好了，线程 ID: {threading.get_ident()}")

# async def brew_coffee():
#     # 打印当前线程 ID
#     print(f"[咖啡] 正在运行，线程 ID: {threading.get_ident()}")
#     print("开始冲咖啡...")
#     await asyncio.sleep(1)
#     print(f"[咖啡] 冲好了，线程 ID: {threading.get_ident()}")

# async def main():
#     print(f"[主程序] 正在运行，线程 ID: {threading.get_ident()}")
#     await asyncio.gather(toast_bread(), brew_coffee())

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
import httpx  # 需要 pip install httpx
import time

# 模拟真实的请求函数
async def fetch_price(platform_name, url, sleep_time):
    print(f"1. [发送请求] 正在连接 {platform_name}...")
    
    # -------------------------------------------------------------
    # 核心替换：这里不再是假的 sleep，而是真实的 HTTP 请求
    # 这里的 await 表示：请求发出去后，网络数据要在光缆里跑一会儿
    # CPU 不需要跟着跑，所以把控制权交还给 Loop
    # -------------------------------------------------------------
    async with httpx.AsyncClient() as client:
        # 为了演示效果，我们强制让这个真实请求“慢”一点 (模拟服务器响应慢)
        # 在真实世界里，这里就是 await client.get(url)
        resp = await client.get(f"https://httpbin.org/delay/{sleep_time}")
        
    print(f"2. [接收响应] 拿到 {platform_name} 的价格了！")
    return f"{platform_name}: 99元"

async def main():
    start = time.time()
    
    print("--- 开始比价 ---")
    # 同时向三家电商发出请求
    # Loop 会在发完第一个请求后，立刻发第二个，不用等第一个回来
    results = await asyncio.gather(
        fetch_price("京东", "jd.com", 3),   # 模拟延时3秒
        fetch_price("淘宝", "taobao.com", 2), # 模拟延时2秒
        fetch_price("拼多多", "pdd.com", 1)   # 模拟延时1秒
    )
    
    print("--- 比价结束 ---")
    for r in results:
        print(r)
        
    print(f"总耗时: {time.time() - start:.2f} 秒")

if __name__ == "__main__":
    asyncio.run(main())