"""01 · interrupt + Command(resume)：图级断点与恢复。

对照 source graph/11_node_interrupt_demo.py。
面试考点：interrupt payload、__interrupt__ 返回结构、resume 值成为 interrupt() 返回值。
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt


class TransferState(TypedDict):
    amount: int
    to_account: str
    audit_status: str
    execute_status: str


def audit_node(state: TransferState) -> dict:
    """人工审核节点：中断点，等待审批。"""
    decision = interrupt({                              # ← 图在这里暂停
        "title": "转账审核",
        "detail": f"向 {state['to_account']} 转账 {state['amount']} 元",
        "options": ["approve", "reject", "edit"],
    })
    d = decision["decision"]["type"]
    if d == "approve":
        return {"audit_status": "approved"}
    if d == "reject":
        return {"audit_status": "rejected"}
    edited = decision["decision"].get("edited_action", {})
    return {"audit_status": f"edited→amount={edited.get('args', {}).get('amount')}"}


def execute_node(state: TransferState) -> dict:
    if state["audit_status"] == "rejected":
        return {"execute_status": "未执行（已拒绝）"}
    return {"execute_status": f"已执行转账，审核状态={state['audit_status']}"}


builder = StateGraph(TransferState)
builder.add_node("audit", audit_node)
builder.add_node("execute", execute_node)
builder.add_edge(START, "audit")
builder.add_edge("audit", "execute")
builder.add_edge("execute", END)

graph = builder.compile(checkpointer=InMemorySaver())   # HITL 必须有 checkpointer
cfg = {"configurable": {"thread_id": "tx-001"}}

print("== 第一次 invoke：在 audit 节点暂停 ==")
r1 = graph.invoke({"amount": 5000, "to_account": "张三", "audit_status": "", "execute_status": ""}, cfg)
interrupt_info = r1["__interrupt__"][0].value
print("审批请求:", interrupt_info)
print("此时 execute 未执行，状态已持久化\n")

print("== 人工审批：修改金额后批准（edit）==")
r2 = graph.invoke(Command(resume={
    "decision": {"type": "edit",
                 "edited_action": {"name": "audit", "args": {"amount": 500, "to_account": "张三"}}}
}), cfg)
print("恢复后从断点继续 →", r2["execute_status"])
