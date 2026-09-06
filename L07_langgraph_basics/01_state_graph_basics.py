"""01 · 最小状态图：并行分支(fan-out) → 汇聚(fan-in)。

对照 source graph/01_start.py + 05_demo.py。
面试考点：State/Input/Output schema 分离；START 多分支扇出、自动汇聚。
"""
from typing import TypedDict

from langgraph.constants import END, START
from langgraph.graph import StateGraph


# 1. 定义状态：Input 是入参白名单，Output 是出参白名单
class MyInput(TypedDict):
    question: str


class MyOutput(TypedDict):
    final_answer: str


class MyState(MyInput, MyOutput):
    rag_result: str
    web_result: str


# 2. 定义节点：接收 state，返回"增量 dict"
def rag_node(state: MyState) -> dict:
    print(f"  [rag_node] 检索: {state['question']}")
    return {"rag_result": f"(RAG命中: LangGraph是状态机编排框架)"}


def web_node(state: MyState) -> dict:
    print(f"  [web_node] 联网搜索: {state['question']}")
    return {"web_result": f"(Web命中: LangGraph 1.x 已GA)"}


def synthesize_node(state: MyState) -> dict:
    print(f"  [synthesize] 合并两路结果")
    return {"final_answer": f"基于 {state['rag_result']} + {state['web_result']} 的综合回答"}


# 3-6. builder → 加节点 → 加边 → 编译
builder = StateGraph(state_schema=MyState, input_schema=MyInput, output_schema=MyOutput)
builder.add_node(rag_node)
builder.add_node(web_node)
builder.add_node(synthesize_node)

builder.add_edge(START, "rag_node")          # 扇出：START 同时连两个节点 → 并行超步
builder.add_edge(START, "web_node")
builder.add_edge("rag_node", "synthesize_node")   # 汇聚
builder.add_edge("web_node", "synthesize_node")
builder.add_edge("synthesize_node", END)

graph = builder.compile()

print("== 并行分支图（rag/web 同一超步并行，然后汇聚）==")
res = graph.invoke({"question": "什么是 LangGraph?"})
print("输出:", res)

# 面试加分：输入 schema 白名单外的字段会被丢弃
print("\n传入 schema 外字段 'hack': 123 →", graph.invoke({"question": "q", "hack": 123}))
