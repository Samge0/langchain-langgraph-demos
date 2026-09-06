"""02 · Agent 解剖：graph 拓扑、消息演化、三种流式模式。

面试考点：
- create_agent 返回 CompiledGraph：agent.get_graph().draw_ascii() 能看到
  agent↔tools 循环 —— "create_agent 底层就是 LangGraph"的最直接证据。
- stream 三模式：values（全量）/ updates（增量）/ messages（token 级）。
"""
import io
from contextlib import redirect_stdout

from langchain.agents import create_agent
from langchain_core.tools import tool

from common.config import get_llm


@tool(description="计算算术表达式")
def calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}))


agent = create_agent(
    model=get_llm(),
    tools=[calculator],
    system_prompt="数值计算必须用 calculator 工具。",
)

# ---------- 1. 图拓扑：暴露 agent↔tools 循环 ----------
buf = io.StringIO()
with redirect_stdout(buf):
    print(agent.get_graph().draw_ascii())
print("== AgentLoop 图拓扑（agent ↔ tools 循环）==")
print("图节点:", list(agent.get_graph().nodes.keys()))

# ---------- 2. updates 模式：每步增量 ----------
print("\n== stream(updates)：每步谁更新了什么 ==")
for update in agent.stream(
    {"messages": [{"role": "user", "content": "计算 (128+64)*3"}]},
    stream_mode="updates",
):
    for node, payload in update.items():
        if node == "model":
            ai = payload["messages"][-1]
            if ai.tool_calls:
                print(f"[model] 请求工具 {[(t['name'], t['args']) for t in ai.tool_calls]}")
            else:
                print(f"[model] 最终回答: {str(ai.content)[:80]}")
        elif node == "tools":
            for m in payload["messages"]:
                print(f"[tools] {m.content}")

# ---------- 3. messages 模式：token 级打字机 ----------
print("\n== stream(messages)：token 级流式 ==")
for msg_chunk, meta in agent.stream(
    {"messages": [{"role": "user", "content": "计算 7*8，并一句话总结"}]},
    stream_mode="messages",
):
    if msg_chunk.content and meta.get("langgraph_node") == "model":
        print(msg_chunk.content, end="", flush=True)
print()
