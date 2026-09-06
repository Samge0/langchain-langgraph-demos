"""01 · 裸 OpenAI SDK 手写 tool calling —— 看清协议层发生了什么。

对照 source 课程的 call_tool_by_openai.py，适配本机 vLLM。
面试考点：tools schema 的 JSON 结构、tool_calls 解析、ToolMessage 回填。
"""
import json

from openai import OpenAI

from common.config import llm_api_key, llm_base_url, llm_model

client = OpenAI(base_url=llm_base_url(), api_key=llm_api_key())


# 1. 真实执行的本地函数
def get_weather(city: str, date: str) -> str:
    return f"{city} 在 {date} 的天气：晴，25度，适合外出。"


# 2. 工具 schema —— 模型只能"看到"这个 JSON，看不到函数体
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询某个城市在指定日期的天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名，如：北京"},
                "date": {"type": "string", "description": "日期，YYYY-MM-DD"},
            },
            "required": ["city", "date"],
        },
    },
}]

messages = [{"role": "user", "content": "帮我查北京 2026-03-23 的天气，然后建议穿什么。"}]

# 3. 第一次调用：模型决定"调用什么工具"
resp = client.chat.completions.create(
    model=llm_model(), messages=messages, tools=tools,
)
msg = resp.choices[0].message
print("== 第一次 AIMessage ==")
print("content:", msg.content)
print("tool_calls:", msg.tool_calls and [
    {"name": tc.function.name, "args": tc.function.arguments, "id": tc.id}
    for tc in msg.tool_calls
])

if msg.tool_calls:
    # 4. 你来执行（模型不执行任何代码！）
    messages.append(msg)  # AIMessage 必须原样回填进历史
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        result = get_weather(**args) if tc.function.name == "get_weather" else "未知工具"
        # 5. 结果以 ToolMessage 回填，tool_call_id 严格对应
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps({"result": result}, ensure_ascii=False),
        })
        print(f"\n== 已执行 {tc.function.name}({args}) → {result}")

    # 6. 第二次调用：模型看到工具结果，生成最终回答
    resp2 = client.chat.completions.create(model=llm_model(), messages=messages)
    print("\n== 最终回答 ==")
    print(resp2.choices[0].message.content)
