import requests
from bs4 import BeautifulSoup
import lxml
import threading
import queue

q = queue.Queue()
BASE_URL = "https://www.gushiwen.cn"

def get_poems_list():
    # 结合该网站的目录结构，补全了被截断的 URL 后缀
    XIAOXUE_URL = BASE_URL + '/' + 'gushi/xiaoxue.aspx'
    res = requests.get(XIAOXUE_URL)
    # 解析数据
    soup = BeautifulSoup(res.text, 'lxml')
    poems_list = []
    # 获取所有class=typecont的div标签
    typecont = soup.find_all('div', class_='typecont')
    # 遍历每一组
    for item in typecont:
        # 获取所有typecont下的span
        for poem in item.find_all('span'):
            poem_tag = poem.find('a')
            link = poem_tag.get('href')
            poems_list.append(link) # 追加
    return poems_list

# def get_poem_content(poem_url):
#     url = BASE_URL + poem_url
#     content = requests.get(url)
#     # 处理url，获取唐诗id
#     # ... (注：原图 IDE 中此处代码被折叠，应为具体的正文解析与提取逻辑)
#     print('-'*50)

import re # 建议在文件顶部补充导入正则模块

def get_poem_content(poem_url):
    url = BASE_URL + poem_url
    
    # 增加超时控制，防止因网络波动导致单个线程永久阻塞
    try:
        response = requests.get(url, timeout=10)
        # 动态修正编码，防止中文乱码（详见后文“盲区”部分）
        response.encoding = response.apparent_encoding 
    except requests.exceptions.RequestException as e:
        print(f"网络请求异常: {e}")
        return

    # 1. 处理url，获取唐诗id
    # 古诗文网的 URL 通常形如 "/shiwenv_45c396367f59.aspx"
    # 采用正则表达式提取，相比简单的字符串分割更加鲁棒
    match = re.search(r'_([a-zA-Z0-9]+)\.aspx', poem_url)
    poem_id = match.group(1) if match else "未知ID"

    # 2. 正文解析与提取逻辑
    soup = BeautifulSoup(response.text, 'lxml')
    
    try:
        # 寻找正文区块：古诗的正文通常被包裹在 class="contson" 的 div 中
        contson = soup.find('div', class_='contson')
        # 提取标题：通常在一个包含 h1 标签的区块内
        title_tag = soup.find('h1')
        
        # 清洗数据：剥离 HTML 标签，仅保留纯文本，并去除首尾空白符
        title = title_tag.get_text(strip=True) if title_tag else "未知标题"
        content_text = contson.get_text(strip=True) if contson else "未提取到正文"

        # 格式化输出（实际工程中此处应为入库或写入文件的操作）
        print(f"【ID】: {poem_id}")
        print(f"【标题】: {title}")
        print(f"【摘要】: {content_text[:40]}...") # 截断打印，保持终端输出整洁
        
    except AttributeError as e:
        # 防御性编程：捕获 DOM 节点缺失导致的异常
        print(f"DOM解析异常 (ID: {poem_id}): {e}")
    finally:
        print('-'*50)

def worker():
    while True:
        url = q.get() # 取值
        try:
            get_poem_content(url)
        finally:
            q.task_done()

if __name__ == '__main__':
    # 生产者
    poems_list = get_poems_list()

    for url in poems_list:
        # 加入队列
        q.put(url)

    # 创建多线程
    for i in range(5):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()
    print('爬取完成')