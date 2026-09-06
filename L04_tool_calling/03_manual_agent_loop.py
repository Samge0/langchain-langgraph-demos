"""03 · 手写 Agent Loop —— create_agent 的内核（面试能写出来的程度）。

面试考点：
- Agent = LLM + 工具 + 循环 + 停止条件（无 tool_calls 或达到 max_steps）。
- 每轮把 AIMessage(tool_calls) 和所有 ToolMessage 都 append 进消息历史。
- 生产必须加：步数上限（防死循环）、工具异常捕获（异常文本也回给模型让它自适应）。
"""
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from common.config import get_llm

llm = get_llm()


@tool(description="查询某个城市在指定日期的天气")
def get_weather(city: str, date: str) -> str:
    return f"{city} 在 {date} 天晴 25 度"


@tool(description="计算算术表达式的值")
def calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))


@tool(description="查询商品当前库存数量")
def get_stock(sku: str) -> str:
    fake_db = {"A001": 42, "B002": 0}
    return f"商品 {sku} 库存 {fake_db.get(sku, '不存在')}"


REGISTRY = {t.name: t for t in [get_weather, calculator, get_stock]}


def agent_loop(question: str, max_steps: int = 6, must_use: list[str] | None = None) -> str:
    """最小可用 Agent：循环到模型不再要求调用工具为止。

    must_use: 强制要求用到的工具名 —— 演示"关键计算不许模型心算"的生产实践：
    第一轮若模型没调用指定工具，注入提醒消息纠偏（等价于工具约束路由的简化版）。
    """
    messages = [
        {"role": "system", "content": "你是电商客服助手，先用工具获取事实，再回答。"},
        HumanMessage(content=question),
    ]
    for step in range(1, max_steps + 1):
        ai_msg = llm.bind_tools(list(REGISTRY.values())).invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:              # 停止条件：模型不再要工具
            # 关键计算纠偏：模型想心算却没调用指定工具时，打回去重做
            if must_use and step == 1:
                names_used = {tc["name"] for tc in messages[-1].tool_calls} if messages[-1].tool_calls else set()
                missing = [m for m in must_use if m not in names_used]
                if missing:
                    messages.append({"role": "user",
                                     "content": f"数字必须用工具计算，禁止心算。请务必调用 {missing} 工具后重答。"})
                    print(f"[loop] 纠偏：模型试图心算，打回要求调用 {missing}")
                    continue
            print(f"[loop] 第{step}轮：无工具调用，输出最终答案")
            return ai_msg.content

        print(f"[loop] 第{step}轮：请求工具 {[tc['name'] for tc in ai_msg.tool_calls]}")
        for tc in ai_msg.tool_calls:
            try:
                result = REGISTRY[tc["name"]].invoke(tc["args"])
            except Exception as e:              # 工具异常也回给模型（自愈）
                result = f"工具执行失败: {e}"
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            print(f"        └─ {tc['name']}({tc['args']}) → {result}")
    return "达到最大步数，强制终止（防止死循环）"


if __name__ == "__main__":
    print("== 场景1：单工具 ==")
    print(agent_loop("北京 2026-03-23 的天气适合洗车吗？"), "\n")
    print("== 场景2：多工具串联（查库存→算总价，禁止心算）==")
    print(agent_loop("A001 库存有多少？如果全部按单价 299 元买下，总价是多少？",
                     must_use=["calculator"]))
