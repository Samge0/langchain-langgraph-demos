"""langchain-mcp-adapters：把 MCP 工具接入 create_agent（先启动 http_mcp_server）。

面试考点：
- MultiServerMCPClient 支持同时挂多个 server（stdio + http 混合）。
- get_tools() 返回的 LangChain tool 与本地 @tool 无差别 —— Agent 视角协议透明。
- transport 写法注意：新版本 streamable_http（带下划线）。
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from common.config import get_llm


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "ecommerce": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8765/mcp",
            }
        }
    )
    tools = await client.get_tools()
    print("== 从 MCP Server 拿到的工具 ==")
    for t in tools:
        print(f"- {t.name}: {t.description}")

    agent = create_agent(
        model=get_llm(),
        tools=tools,
        system_prompt="你是电商助手：先查库存与价格，再回答。",
    )
    res = await agent.ainvoke({
        "messages": [{"role": "user",
                      "content": "A001 现在有货吗？多少钱？另外深圳 2026-09-10 天气怎么样，适合运动吗？"}]
    })
    print("\n== 工具调用轨迹 ==")
    for m in res["messages"]:
        if m.type == "ai" and m.tool_calls:
            print(f"[ai] 调用 {[(tc['name'], tc['args']) for tc in m.tool_calls]}")
        elif m.type == "tool":
            print(f"[tool] {m.content}")
    print("\n== 最终回答 ==")
    print(res["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
