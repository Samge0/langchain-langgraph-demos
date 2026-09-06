"""02 · 自定义 Middleware：动态 prompt 注入 + 审计日志（AOP 思想）。

面试考点：
- AgentMiddleware 的 @before_model 钩子：模型调用前改写/注入状态。
- 动态 system prompt：把 state 中的用户画像注入每次调用（个性化上下文工程）。
- @after_model 钩子：响应审计（生产：敏感词、合规留痕）。
"""
from typing import TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from common.config import get_llm


class AuditState(TypedDict, total=False):
    user_profile: str
    audit_log: list[str]


class ProfileAuditMiddleware(AgentMiddleware):
    """请求前注入用户画像；响应后写审计日志。dynamic_prompt=True 才会启用 {占位符} 填充。"""

    def __init__(self, dynamic_prompt: bool = False):
        super().__init__()
        self.dynamic_prompt = dynamic_prompt

    def before_model(self, state: AuditState, runtime) -> dict | None:
        profile = state.get("user_profile", "")
        if profile:
            return {"user_profile": profile}   # 与 dynamic_prompt 配合注入
        return None

    def after_model(self, state: AuditState, runtime) -> dict | None:
        reply = state["messages"][-1].content
        return {"audit_log": [f"回复长度={len(reply)}"]}   # list 需 reducer；演示用简化写法


@tool(description="查询会员积分余额")
def get_points(user_id: str) -> str:
    return f"用户 {user_id} 当前积分 12,800，黄金会员。"


agent = create_agent(
    model=get_llm(),
    tools=[get_points],
    middleware=[
        ProfileAuditMiddleware(dynamic_prompt=True),   # dynamic_prompt: before_model 的字段拼进 system
    ],
    system_prompt="你是会员服务助手。用户画像如下：{user_profile}",   # 占位符会被填充
    checkpointer=InMemorySaver(),
)

cfg = {"configurable": {"thread_id": "mw-1"}}
r = agent.invoke({
    "messages": [{"role": "user", "content": "我是 samge，查一下我的积分，然后告诉我能换什么"}],
    "user_profile": "黄金会员，近期关注旅行兑换",
}, cfg)
print("== 回复 ==")
print(r["messages"][-1].content.strip()[:150])

print("\n== 工具调用轨迹 ==")
for m in r["messages"]:
    if m.type == "ai" and getattr(m, "tool_calls", None):
        print(f"[ai] {[(tc['name'], tc['args']) for tc in m.tool_calls]}")
    elif m.type == "tool":
        print(f"[tool] {str(m.content)[:60]}")
