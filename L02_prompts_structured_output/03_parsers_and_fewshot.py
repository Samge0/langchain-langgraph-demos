"""03 · 输出解析器 + Few-shot：让不可靠的文本输出变得可控。

面试考点：
- StrOutputParser：最常用，把 AIMessage 变纯字符串接进链。
- 解析失败怎么办：OutputFixingParser（用模型修复）→ 但更根本的是结构化输出（02课）。
- Few-shot 文本内嵌 vs 消息对注入的写法与取舍。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from common.config import get_llm

llm = get_llm()

# ---------- 1. StrOutputParser ----------
chain = llm | StrOutputParser()   # LCEL 预告：L03 详解
print("== str 输出 ==")
print(chain.invoke("两句话解释什么是Embedding")[:100], "...\n")

# ---------- 2. Few-shot（消息对形态）----------
# 期望模型学会"先给结论，再给理由"的稳定格式
examples = [
    {"input": "微服务拆分应该很细吗？", "output": "结论：不是越细越好。理由：拆分粒度要匹配团队规模和部署能力，过细会放大运维与一致性问题。"},
    {"input": "缓存应该设置越长越好吗？", "output": "结论：不是。理由：TTL 需在命中率与一致性间权衡，长缓存会放大脏读窗口。"},
]
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"), ("ai", "{output}"),
])
few_shot = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt, examples=examples,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你按固定格式回答技术判断题：先给结论，再给理由，共两句话。"),
    few_shot,
    ("human", "{input}"),
])

chain2 = final_prompt | llm | StrOutputParser()
print("== Few-shot 稳定格式输出 ==")
print(chain2.invoke({"input": "RAG 里 chunk 是越大越好吗？"}).strip())
