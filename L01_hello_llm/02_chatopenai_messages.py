"""02 · ChatOpenAI：LangChain 的消息模型与统一调用面。

面试考点：
- 四种消息类型：SystemMessage / HumanMessage / AIMessage / ToolMessage。
- .invoke() 是 Runnable 协议的统一入口 —— L02/L03 的链式组合全靠它。
- .content 之外还有 .tool_calls / .additional_kwargs，L04 会用到。
"""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from common.config import get_llm

llm = get_llm()

# 方式一：直接传字符串（框架自动包装成 HumanMessage）
res = llm.invoke("一句话介绍 LangGraph")
print("== 字符串直调 ==")
print(res.content, "\n")

# 方式二：显式消息列表（生产推荐：角色清晰、可精确控制）
messages = [
    SystemMessage(content="你是资深 Agent 架构师，回答带 1 个实际工程建议。"),
    HumanMessage(content="LangGraph 和 LangChain 的关系是什么？"),
]
res2: AIMessage = llm.invoke(messages)
print("== 消息列表 ==")
print(res2.content, "\n")

# 面试考点：AIMessage 的完整结构
print("== AIMessage 结构 ==")
print("content 类型:", type(res2.content))
print("response_metadata.model:", res2.response_metadata.get("model"))
print("usage_metadata:", res2.usage_metadata)
