"""01 · Supervisor 多智能体：主管路由 + 两个专业工人（检索/写作）。

面试考点：
- supervisor 用 with_structured_output 输出路由决策（next / FINISH）。
- 工人 = create_agent 小封装，各自独立工具集与 system prompt。
- 工人结果以"结论摘要"写回共享 state（省 token 的通信纪律）。
"""
import operator
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field

from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from common.config import get_llm

llm = get_llm()


# ---------------- 共享状态 ----------------
class TeamState(TypedDict):
    task: str
    transcript: Annotated[list[str], operator.add]   # 各成员发言累积（reducer！）
    next: str                                        # supervisor 的路由决定


# ---------------- 工人 1：研究员（检索工具） ----------------
@tool(description="在公司知识库中检索指定主题的资料")
def search_knowledge(topic: str) -> str:
    """模拟知识库检索（生产 = L11 的混合检索）。"""
    fake_kb = {
        "Qwen": "Qwen3-8B 是 2025 年 4 月发布的开源模型，Apache 2.0 协议，支持双模式切换。",
        "福利": "智栈科技年假 15 天起，学习基金每年 8000 元。",
    }
    for k, v in fake_kb.items():
        if k.lower() in topic.lower():
            return v
    return "知识库未命中"


researcher = create_agent(
    model=llm,
    tools=[search_knowledge],
    system_prompt="你是研究员：用工具检索事实，输出 2 句以内的纯事实结论，不带立场。",
)


# ---------------- 工人 2：作者（纯写作，无工具） ----------------
writer = create_agent(
    model=llm,
    tools=[],
    system_prompt="你是技术作者：基于给定事实写 3 句以内的中文短文，语气正式。",
)


def run_researcher(state: TeamState) -> dict:
    res = researcher.invoke({"messages": [{"role": "user", "content": f"调研主题：{state['task']}"}]})
    conclusion = res["messages"][-1].content.strip()
    print(f"  [researcher] {conclusion[:80]}")
    return {"transcript": [f"研究员结论: {conclusion}"]}


def run_writer(state: TeamState) -> dict:
    facts = "\n".join(t for t in state["transcript"] if t.startswith("研究员结论"))
    res = writer.invoke({"messages": [{"role": "user", "content": f"任务：{state['task']}\n可用事实：\n{facts}"}]})
    article = res["messages"][-1].content.strip()
    print(f"  [writer] {article[:80]}")
    return {"transcript": [f"作者成稿: {article}"]}


# ---------------- Supervisor：结构化输出路由 ----------------
class Route(BaseModel):
    """主管的路由决策。"""
    next: Literal["researcher", "writer", "FINISH"] = Field(
        description="下一步交给谁：researcher=还需要检索事实；writer=事实够了可以成稿；FINISH=任务完成")
    reason: str = Field(description="一句话决策理由")


ROUNDS = {"n": 0}   # supervisor 决策轮次计数（演示防打转的生产安全阀）


supervisor_llm = llm.with_structured_output(Route)


def supervisor_node(state: TeamState) -> dict:
    ROUNDS["n"] += 1
    progress = "\n".join(state["transcript"]) or "(尚无进展)"
    route: Route = supervisor_llm.invoke(
        f"总任务：{state['task']}\n当前进展：\n{progress}\n"
        f"已决策轮次：{ROUNDS['n']}（超过3轮必须FINISH）\n请决定下一步。")
    print(f"  [supervisor] → {route.next}  ({route.reason[:40]})")
    nxt = route.next
    if ROUNDS["n"] >= 4:      # 安全阀：阻止 writer 无限重写
        print("  [supervisor] 达到决策上限，强制结束")
        nxt = "FINISH"
    return {"next": nxt}


# ---------------- 组图 ----------------
builder = StateGraph(TeamState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", run_researcher)
builder.add_node("writer", run_writer)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor", lambda s: s["next"],
    {"researcher": "researcher", "writer": "writer", "FINISH": END},  # FINISH→END 显式映射
)
builder.add_edge("researcher", "supervisor")   # 工人干完都回主管
builder.add_edge("writer", "supervisor")
# supervisor 的 FINISH → END 由条件边处理
graph = builder.compile()

if __name__ == "__main__":
    print("== 任务：写一段介绍 Qwen3-8B 的公司内网公告 ==")
    final = graph.invoke(
        {"task": "写一段介绍 Qwen3-8B 的公司内网公告", "transcript": [], "next": "supervisor"},
        config={"recursion_limit": 12},
    )
    article = [t for t in final["transcript"] if t.startswith("作者成稿")][-1]
    print("\n== 最终成稿 ==")
    print(article.replace("作者成稿: ", ""))
