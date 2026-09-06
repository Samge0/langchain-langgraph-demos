"""01 · SummarizationMiddleware：长对话自动压缩（上下文工程核心）。

对照 source middleware/01_summarization_middleware_demo.py，阈值调小便于演示。
面试考点：trigger/keep 参数、压缩后消息形态（一条摘要 + 最近窗口）。
"""
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from common.config import get_llm

agent = create_agent(
    model=get_llm(),
    system_prompt="你是记忆压缩演示助手，每次回答不超过两句话。",
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=get_llm(),
            trigger=("messages", 8),   # 消息数达到 8 → 触发压缩（生产用 tokens 计）
            keep=("messages", 4),      # 保留最近 4 条原文
        )
    ],
)

cfg = {"configurable": {"thread_id": "sum-1"}}
questions = [
    "什么是 LangChain?",
    "什么是 LangGraph?",
    "什么是 Checkpointer?",
    "什么是 Middleware?",
    "什么是 MCP?",
    "我刚才总共问了你几个概念？分别是什么？",   # 早期消息已被压缩成摘要
]

for i, q in enumerate(questions, 1):
    r = agent.invoke({"messages": [{"role": "user", "content": q}]}, cfg)
    n_msgs = len(r["messages"])
    print(f"[第{i}轮] 消息总数={n_msgs}")
    print(f"        答复: {r['messages'][-1].content.strip()[:100]}")

final_state = agent.get_state(cfg)
msgs = final_state.values["messages"]
print("\n== 压缩后的消息序列（验证：出现了 Summary 消息）==")
for m in msgs:
    preview = str(m.content)[:80].replace("\n", " ")
    print(f"- [{m.type}] {preview}")
