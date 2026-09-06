"""02 · HumanInTheLoopMiddleware：声明式工具审批（create_agent 层）。

对照 source checkpointer/03_human_in_the_loop_middleware_demo.py。
面试考点：interrupt_on 白名单；decisions 报文；审批策略与工具实现解耦。
"""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from common.config import get_llm


@tool(description="查询某个城市在指定日期的天气")
def get_weather(city: str, date: str) -> str:
    return f"{city} 在 {date} 的天气：晴，25度。"


@tool(description="向指定账户转账指定金额（敏感操作，需人工审批）")
def transfer_money(amount: int, to_account: str) -> str:
    print(f"    !!! 真实执行转账: {amount} 元 -> {to_account} !!!")
    return f"成功转账 {amount} 元给 {to_account}"


agent = create_agent(
    model=get_llm(),
    tools=[transfer_money, get_weather],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"transfer_money": True, "get_weather": False},   # 策略集中在装配层
    )],
    checkpointer=InMemorySaver(),
    system_prompt="你是银行助手。执行资金操作前必须调用 transfer_money 工具。",
)

cfg = {"configurable": {"thread_id": "hitl-1"}}

print("== 用户发起转账 → 中间件拦截 ==")
r1 = agent.invoke({"messages": [{"role": "user", "content": "给张三转账 5000 元"}]}, cfg)
iv = r1["__interrupt__"][0].value
print("拦截到的动作请求:", [(a["name"], a["args"]) for a in iv["action_requests"]])

print("\n== 人工决策：edit（改成 500 元）后批准 ==")
decisions = [{"type": "edit",
              "edited_action": {"name": "transfer_money", "args": {"amount": 500, "to_account": "张三"}}}]
r2 = agent.invoke(Command(resume={"decisions": decisions}), cfg)
print("最终回复:", r2["messages"][-1].content.strip()[:120])

print("\n== 对照组：查天气（白名单外）不触发审批 ==")
r3 = agent.invoke({"messages": [{"role": "user", "content": "查北京 2026-10-01 的天气"}]}, cfg)
print("无 __interrupt__，直接完成:", "天气" in r3["messages"][-1].content)
