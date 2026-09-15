import json
import httpx
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel
from openai import OpenAI

def log_request(request: httpx.Request):
    print("\n=== HTTP REQUEST ===")
    print(request.method, request.url)
    try:
        body = request.content.decode("utf-8")
        data = json.loads(body)
        print(json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        print("! parse body failed:", e)

def log_response(response):
    try:
        response.read()
    except Exception as e:
        print("\n=== HTTP RESPONSE (read failed) ===")
        print("status:", response.status_code, "| error:", repr(e))
        return

    print("\n=== HTTP RESPONSE ===")
    print("status:", response.status_code)
    body = response.text or ""
    print(json.dumps(json.loads(body), indent=4, ensure_ascii=False))

http_client = httpx.Client(
    timeout=60,
    event_hooks={"request": [log_request],
                #  "response": [log_response]
                 },
)


class Item(BaseModel):
    title: str
    year: int
    
@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@tool
def mul(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def test_openai_api():
    client = OpenAI(http_client=http_client)
    class CalendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]
        
    completion = client.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
        ],
        response_format=CalendarEvent,
    )

    print(completion.choices[0].message.parsed)
    
    tools = [convert_to_openai_tool(add), convert_to_openai_tool(mul)]

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "user", "content": "What is (2 + 3) * 4?"},
        ],
        tools=tools,
    )

    print(completion.choices[0].message.tool_calls)


def test_langchain_structured_output():
    llm = ChatOpenAI(
        model="gpt-4o-mini-2024-07-18",  # 选择明确支持 Structured Outputs 的快照
        temperature=0,
        http_client=http_client,
    )

    # structured = llm.with_structured_output(Item, method="json_schema")
    structured = llm.with_structured_output(Item, method="function_calling")
    # structured = llm.with_structured_output(Item, method="json_object")

    out = structured.invoke("《放牛班的春天》的标题和年份")
    print("PARSED:", out)


def test_langchain_function_calling():
    llm = ChatOpenAI(
        model="gpt-4o-mini-2024-07-18",  # 选择明确支持 Structured Outputs 的快照
        temperature=0,
        http_client=http_client,
    )
    tools = [add, mul]
    llm_with_tools = llm.bind_tools(tools)
    res = llm_with_tools.invoke("What is (2 + 3) * 4?")
    print("PARSED:", res)


if __name__ == "__main__":

    assert load_dotenv(find_dotenv(), override=True)

    # test_openai_api()
    # test_langchain_structured_output()
    test_langchain_function_calling()
