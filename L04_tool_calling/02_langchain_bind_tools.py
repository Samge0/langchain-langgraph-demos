"""02 · LangChain 工具定义与 bind_tools —— schema 自动生成。

面试考点：
- @tool 装饰器：docstring 即工具描述（会进 prompt，直接影响选择准确率）；
  参数类型注解 + Field description → 自动生成 JSON Schema。
- bind_tools 之后 llm 变成 Runnable；res.tool_calls 是解析好的列表。
- 追问：@tool 的 args_schema 有什么用 → 显式 Pydantic 校验/更强的字段说明。
"""
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from common.config import get_llm

llm = get_llm()


# ---------- 1. 定义工具（类型注解 + description 是给模型看的）----------
class WeatherArgs(BaseModel):
    city: str = Field(description="城市名称，例如：深圳市")
    date: str = Field(description="日期，格式 YYYY-MM-DD")


@tool(description="查询某个城市在指定日期的天气信息", args_schema=WeatherArgs)
def get_weather(city: str, date: str) -> str:
    return f"{city} 在 {date} 的天气：晴，25度。"


class CalcArgs(BaseModel):
    expression: str = Field(description="合法的 Python 算术表达式，例如 2*3+4")


@tool(description="计算一个算术表达式的值，支持加减乘除与括号", args_schema=CalcArgs)
def calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))  # 演示用；生产要沙箱


print("== 框架自动生成的 schema（会翻译成 OpenAI tools JSON）==")
print(get_weather.args_schema.model_json_schema(), "\n")

# ---------- 2. 绑定工具后调用 ----------
tool_llm = llm.bind_tools([get_weather, calculator])

messages = [HumanMessage(content="北京 2026-03-23 天气怎么样？另外帮我算一下 128*8+64。")]
res = tool_llm.invoke(messages)
print("== AIMessage.tool_calls（一次要求两个工具=并行工具调用）==")
for tc in res.tool_calls:
    print(" ", tc["name"], tc["args"], "id=", tc["id"])

# ---------- 3. 执行全部工具并回填 ----------
messages.append(res)
registry = {"get_weather": get_weather, "calculator": calculator}
for tc in res.tool_calls:
    result = registry[tc["name"]].invoke(tc["args"])
    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    print(f"\n[执行] {tc['name']} → {result}")

# ---------- 4. 最终回答 ----------
final = tool_llm.invoke(messages)
print("\n== 最终回答 ==")
print(final.content)
