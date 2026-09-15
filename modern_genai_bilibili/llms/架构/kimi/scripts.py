import os
import base64
import json
import requests
from dotenv import load_dotenv, find_dotenv

assert load_dotenv(find_dotenv(), override=True)

api_key = os.environ.get("MOONSHOT_API_KEY")
endpoint = "https://api.moonshot.cn/v1/tokenizers/estimate-token-count"
image_path = "licensed-image.jpeg"
 
with open(image_path, "rb") as f:
    image_data = f.read()
 
# 我们使用标准库 base64.b64encode 函数将图片编码成 base64 格式的 image_url
image_url = f"data:image/{os.path.splitext(image_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"
 
payload = {
    "model": "kimi-k2.5",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url", # <-- 使用 image_url 类型来上传图片，内容为使用 base64 编码过的图片内容
                    "image_url": {
                        "url": image_url,
                    },
                },
                {
                    "type": "text",
                    "text": " ", # <-- 使用 text 类型来提供文字指令，例如“描述图片内容”
                },
            ],
        }
    ]
}
 
response = requests.post(
    endpoint,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    data=json.dumps(payload)
)
print(response.text)
print(response.json())