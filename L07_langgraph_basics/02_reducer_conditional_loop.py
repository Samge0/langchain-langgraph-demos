"""02 · Reducer + 条件边 + 循环 —— 图引擎的核心控制流。

对照 source graph/03_reducer_demo.py + 12_circle_demo.py。
面试考点：
- Annotated[list, add] 累加合并；并行写同一 key 必须有 reducer。
- 条件边 router 返回节点名或 END；回边成环 + recursion_limit 安全阀。
"""
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.constants import END, START
from langgraph.errors import GraphRecursionError
from langgraph.graph import StateGraph


class LoopState(TypedDict):
    question: str
    history: Annotated[list[str], operator.add]   # reducer：各节点追加，不覆盖
    best_score: int                                # 无 reducer → 默认覆盖
    round_no: int


def retriever_node(state: LoopState) -> dict:
    print(f"  [retriever] 第{state['round_no']}轮检索")
    return {"history": [f"round{state['round_no']}:检索到{3+state['round_no']}条"],
            "round_no": state["round_no"] + 1}


def grader_node(state: LoopState) -> dict:
    score = min(95, 60 + state["round_no"] * 20)   # 模拟每轮质量提升
    return {"best_score": score}


def router(state: LoopState) -> Literal["retriever_node", "rewrite_node", END]:
    """条件路由：分数不够且轮次未超 → 重检索；中间轮 → 改写查询；够好 → 结束。"""
    if state["best_score"] >= 90:
        return END
    if state["round_no"] >= 4:
        return END
    return "rewrite_node" if state["round_no"] % 2 == 0 else "retriever_node"


def rewrite_node(state: LoopState) -> dict:
    return {"history": [f"round{state['round_no']}:改写查询为更具体的关键词"]}


builder = StateGraph(LoopState)
builder.add_node(retriever_node)
builder.add_node(grader_node)
builder.add_node(rewrite_node)

builder.add_edge(START, "retriever_node")
builder.add_edge("retriever_node", "grader_node")
builder.add_conditional_edges("grader_node", router)   # 条件边：动态决定去向
builder.add_edge("rewrite_node", "retriever_node")     # 回边 → 成环

graph = builder.compile()

print("== Self-RAG 式循环（检索→评分→不够好就改写再来）==")
res = graph.invoke({"question": "LangGraph 超步原理", "history": [], "best_score": 0, "round_no": 1})
print("轨迹:", *res["history"], sep="\n  ")
print("最终分数:", res["best_score"], "（reducer 让 history 跨轮累积）")

# 安全阀演示：死循环图 + recursion_limit
class Infinite(TypedDict):
    n: int

g2 = (
    StateGraph(Infinite)
    .add_node("bump", lambda s: {"n": s["n"] + 1})
    .add_edge(START, "bump")
    .add_edge("bump", "bump")       # 自己环自己：死循环
    .compile()
)
print("\n== recursion_limit 安全阀 ==")
try:
    g2.invoke({"n": 0}, config={"recursion_limit": 5})
except GraphRecursionError as e:
    print("已拦截死循环:", type(e).__name__)
