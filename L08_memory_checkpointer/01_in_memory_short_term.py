"""01 · InMemorySaver 短期记忆：thread_id 隔离会话。

对照 source checkpointer/01_in_memory_saver_demo.py。
面试考点：同一 thread 自动带历史；不同 thread 互不可见。
"""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from common.config import get_llm

agent = create_agent(
    model=get_llm(),
    system_prompt="你是记忆测试助手，回答不超过两句话。",
    checkpointer=InMemorySaver(),          # 关键：有 checkpointer 才有记忆
    tools=[],
)

cfg_t1 = {"configurable": {"thread_id": "thread-1"}}
cfg_t2 = {"configurable": {"thread_id": "thread-2"}}

print("== thread-1：先自我介绍 ==")
r1 = agent.invoke({"messages": [{"role": "user", "content": "记住：我最喜欢的数字是 42。"}]}, cfg_t1)
print(r1["messages"][-1].content.strip(), "\n")

print("== thread-1：追问（应记得 42）==")
r2 = agent.invoke({"messages": [{"role": "user", "content": "我最喜欢的数字是多少？"}]}, cfg_t1)
print(r2["messages"][-1].content.strip(), "\n")

print("== thread-2：新会话（应不记得）==")
r3 = agent.invoke({"messages": [{"role": "user", "content": "我最喜欢的数字是多少？"}]}, cfg_t2)
print(r3["messages"][-1].content.strip(), "\n")

# 看看线程里到底存了什么
state = agent.get_state(cfg_t1)
print("== thread-1 当前快照里的消息条数 ==", len(state.values["messages"]))
print("checkpoint 元信息:", {k: state.config["configurable"].get(k) for k in ["thread_id", "checkpoint_id"]})
