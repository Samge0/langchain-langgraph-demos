"""03 · 自定义 Runnable：业务逻辑融进 LCEL 体系。

面试考点：
- RunnableLambda 把普通函数变成 Runnable（可进链、可 stream/batch）。
- RunnablePassthrough：原样下传输入 —— RAG 中"问题+检索结果"并存的经典用法。
- itemgetter dict 组合：给链的不同分支抽取不同字段（RAG 标准写法）。
"""
from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from common.config import get_llm

llm = get_llm()

# ---------- 1. RunnableLambda：清洗逻辑进链 ----------
def normalize(question: str) -> str:
    return question.strip().replace("？", "?")

chain = RunnableLambda(normalize) | llm | StrOutputParser()
print("== lambda 进链 ==")
print(chain.invoke("  什么是 A2A 协议？")[:80], "...\n")

# ---------- 2. RunnablePassthrough + itemgetter：RAG 端到端雏形 ----------
# 模拟一个检索器（L11 会换成真实向量检索）
fake_retriever = RunnableLambda(lambda q: f"[检索片段] 关于「{q}」的知识：LangGraph 是基于图的任务编排引擎。")

rag_chain = (
    {
        "context": fake_retriever,                      # 输入问题 → 检索文本
        "question": RunnablePassthrough(),              # 原样透传问题
    }
    | ChatPromptTemplate.from_messages([
        ("system", "仅依据以下上下文回答，上下文没有就说不知道：\n{context}"),
        ("human", "{question}"),
    ])
    | llm
    | StrOutputParser()
)
print("== RAG 雏形（可回答）==")
print(rag_chain.invoke("LangGraph 是什么").strip(), "\n")

print("== RAG 雏形（拒答）==")
print(rag_chain.invoke("马斯克 latest 推文说了什么").strip())
