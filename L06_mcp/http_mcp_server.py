"""HTTP 传输的 MCP 服务端：独立进程，供 langchain_mcp_agent 连接。

启动：.venv/Scripts/python.exe -m L06_mcp.http_mcp_server
面试考点：FastMCP 的 @mcp_server.tool() 装饰器自动生成 schema；
streamable-http 让工具成为"独立部署的服务"。
"""
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP(
    name="ecommerce_mcp_server",
    host="127.0.0.1",
    port=8765,
    streamable_http_path="/mcp",
)


@mcp_server.tool()
def get_weather(city: str, date: str) -> str:
    """查询某个城市在指定日期的天气"""
    return f"{city} 在 {date} 的天气：晴，25度。"


@mcp_server.tool()
def get_stock(sku: str) -> str:
    """查询商品当前库存"""
    return f"商品 {sku} 库存 42 件"


@mcp_server.tool()
def get_price(sku: str) -> str:
    """查询商品当前售价"""
    prices = {"A001": "299.00", "B002": "1299.00"}
    return f"商品 {sku} 售价 {prices.get(sku, '未知')} 元"


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http")
