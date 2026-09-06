"""stdio 传输：MCP Client 把 Server 作为子进程拉起，stdin/stdout 通信。

一把梭：本脚本同时内嵌 server 代码（用当前解释器重启动自身 --as-server）。
面试考点：stdio 是"本地工具进程"模式；生命周期跟随 Client。
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters, stdio_client

THIS_FILE = __file__
PYTHON = sys.executable

stdio_params = StdioServerParameters(
    command=PYTHON,
    args=[THIS_FILE, "--as-server"],
)


async def main() -> None:
    async with stdio_client(stdio_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()                      # 握手：交换协议版本与能力
            tools = await session.list_tools()              # 发现工具（自描述）
            print("== 服务端暴露的工具 ==")
            for t in tools.tools:
                print(f"- {t.name}: {t.description}")

            res = await session.call_tool("get_weather", {"city": "深圳", "date": "2026-09-10"})
            print("\n== call_tool 结果 ==")
            print(res.content[0].text)


def run_server() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stdio_demo_server")

    @mcp.tool()
    def get_weather(city: str, date: str) -> str:
        """查询某个城市在指定日期的天气"""
        return f"{city} 在 {date} 的天气：多云，28度。"

    mcp.run(transport="stdio")


if __name__ == "__main__":
    if "--as-server" in sys.argv:
        run_server()
    else:
        asyncio.run(main())
