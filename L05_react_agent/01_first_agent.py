"""01 · 第一个 create_agent —— 框架版 ReAct Agent。

对照 source 课程 call_tool_by_create_agent.py，适配本机 vLLM。
面试考点：create_agent 的输入输出形态、中间消息的解读。
"""
from langchain.agents import create_agent
from langchain_core.tools import tool

from common.config import get_llm


@tool(description="查询某个城市在指定日期的天气信息")
def get_weather(city: str, date: str) -> str:
    return f"{city} 在 {date} 的天气：晴，25度。"


@tool(description="查询商品当前库存")
def get_stock(sku: str) -> str:
    return "商品 A001 库存 42 件"


agent = create_agent(
    model=get_llm(),
    tools=[get_weather, get_stock],
    system_prompt="你是电商客服助手。先用工具获取事实，再给出简洁回答。",
)

res = agent.invoke({
    "messages": [{"role": "user", "content": "北京 2026-03-23 天气如何？顺便看下 A001 有没有货。"}]
})

print("== 完整消息轨迹（ReAct：推理→行动→观察→回答）==")
for m in res["messages"]:
    role = m.type
    if role == "ai" and m.tool_calls:
        print(f"[ai+tool_calls] 想调用: {[(tc['name'], tc['args']) for tc in m.tool_calls]}")
    elif role == "tool":
        print(f"[tool] {m.content}")
    else:
        print(f"[{role}] {str(m.content)[:120]}")

print("\n== 最终答案 ==")
print(res["messages"][-1].content)
