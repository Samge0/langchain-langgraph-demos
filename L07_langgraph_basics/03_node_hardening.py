"""03 · 节点工程化：重试(RetryPolicy) + 运行时配置(RunnableConfig)。

对照 source graph/06_node_input_demo.py + 08_node_retry_demo.py。
面试考点：
- RetryPolicy：指数退避重试瞬时故障；超过 max_attempts 才真正抛错。
- config["configurable"]：运行时注入参数（user_id/租户/trace），业务无感。
"""
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy


class LlmState(TypedDict):
    query: str
    answer: str


attempts = {"n": 0}


def flaky_llm_node(state: LlmState) -> dict:
    """前 2 次调用必失败，第 3 次成功 —— 模拟 LLM 网关抖动。"""
    attempts["n"] += 1
    if attempts["n"] < 3:
        raise ConnectionError(f"模拟LLM网关抖动 (第{attempts['n']}次)")
    return {"answer": f"回答: {state['query']}"}


def greet_node(state: LlmState, config: RunnableConfig) -> dict:
    user = config["configurable"].get("user_id", "anonymous")
    print(f"  [greet] 面向用户 {user} 个性化问候")
    return {}


builder = StateGraph(LlmState)
builder.add_node("flaky", flaky_llm_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.2))
builder.add_node("greet", greet_node)
builder.add_edge(START, "flaky")
builder.add_edge("flaky", "greet")
builder.add_edge("greet", END)

graph = builder.compile()

print("== RetryPolicy：连续失败自动重试直到成功 ==")
res = graph.invoke({"query": "什么是 PagedAttention"},
                   config={"configurable": {"user_id": "samge"}})
print("结果:", res["answer"])
