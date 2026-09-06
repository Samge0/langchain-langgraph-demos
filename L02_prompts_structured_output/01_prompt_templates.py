"""01 · ChatPromptTemplate：模板变量、系统提示、对话历史占位。

踩坑点（高频面试题）：必须用 ("role", "text") 元组才能渲染 {变量}。
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from common.config import get_llm

llm = get_llm()

# ---------- 1. 基础模板 ----------
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{name}，一位资深{domain}工程师，回答控制在3句话内。"),
    ("human", "{question}"),
])

rendered = prompt.invoke({"name": "小智", "domain": "后端", "question": "什么是消息队列？"})
print("== 渲染后的 PromptValue ==")
for m in rendered.to_messages():
    print(f"[{m.type}] {m.content}")
print()

res = llm.invoke(rendered)
print("== 模型回复 ==")
print(res.content.strip(), "\n")

# ---------- 2. MessagesPlaceholder：插入完整对话历史 ----------
history_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个上下文连贯的对话助手。"),
    MessagesPlaceholder("chat_history"),   # 这里会被替换成一组消息
    ("human", "{input}"),
])

rendered2 = history_prompt.invoke({
    "chat_history": [
        HumanMessage(content="我叫samge，正在准备Agent面试。"),
        AIMessage(content="好的samge，我会记住你的背景。"),
    ],
    "input": "我的名字是什么？我在准备什么？",
})
res2 = llm.invoke(rendered2)
print("== 带历史的回复 ==")
print(res2.content.strip())
