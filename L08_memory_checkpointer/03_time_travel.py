"""03 · 时间旅行：get_state_history + checkpoint 回放（调试利器）。

面试考点：
- 每个超步都有快照；history 是"倒序"的快照列表。
- 旧 checkpoint 上以更新后的 state 再次 invoke → 从那一刻分叉重放。
- 价值场景：故障审计、回归调试、A/B 决策对比。
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph


class State(TypedDict):
    steps: Annotated[list[str], operator.add]
    path: str


def node_a(state: State) -> dict:
    return {"steps": ["A"], "path": "went-A"}


def node_b(state: State) -> dict:
    return {"steps": ["B"], "path": "went-B"}


def node_end(state: State) -> dict:
    return {"steps": ["END"]}


builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("end", node_end)
builder.add_edge(START, "a")
builder.add_edge("a", "end")
builder.add_edge("b", "end")
builder.add_edge("end", END)

graph = builder.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "tt-1"}}

graph.invoke({"steps": [], "path": ""}, cfg)

print("== 全部历史快照（倒序）==")
history = list(graph.get_state_history(cfg))
for s in history:
    cfg_id = s.config["configurable"]["checkpoint_id"]
    print(f"- checkpoint={cfg_id[:8]}... next={s.next} values={s.values}")

# 找到"A 刚执行完"的快照，从那一刻"改写历史"：假装当时走的是 B
past = next(s for s in history if s.next == ("end",) and s.values.get("path") == "went-A")
print("\n== 分叉重放：在 A 的快照上提交 B 的更新（as_node='b'）==")
fork_cfg = {
    "configurable": dict(past.config["configurable"])   # 带全 thread_id/checkpoint_id/checkpoint_ns
}
graph.update_state(fork_cfg, {"steps": ["B"], "path": "went-B"}, as_node="b")

print("回放后的时间线（新分支已追加）:")
for s in graph.get_state_history(cfg):
    print(f"- next={s.next} values={s.values}")
print("\n面试表述：checkpoint 本质是 state 的事件溯源，可以回放、审计、分支推演。")
