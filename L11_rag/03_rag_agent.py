"""03 · 引用溯源 RAG 问答 + 拒答 —— 生产形态的完整闭环。

面试考点：
- prompt 强约束：仅依据上下文回答 + 每个事实标 [编号] + 无答案必须拒答。
- 引用清单：答案与来源 chunk 一一对应（合规刚需）。
- 追问：检索质量差时怎么办 → 评测集监控 + 重排序 + 查询改写，而不是调 prompt 掩盖。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from common.config import get_llm
from L11_rag.retriever import format_context, hybrid_search

llm = get_llm()

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是企业知识库助手。严格规则：
1. 仅依据下方上下文回答，禁止使用任何外部知识。
2. 答案中每个事实性陈述后面标注引用编号，如 [1] 或 [2][3]。
3. 如果上下文不足以回答，只回复："知识库中没有相关信息。"
4. 回答末尾单独一行：来源: [1] 文件名, [2] 文件名（只列实际引用的编号）。

上下文：
{context}"""),
    ("human", "{question}"),
])


def retrieve(question: str) -> str:
    return format_context(hybrid_search(question, top_k=4))


rag_chain = (
    {
        "context": RunnableLambda(retrieve),
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

QUESTIONS = [
    "入职配的电脑是什么？年假有多少天？",
    "公司差旅住宿标准是多少？",
    "智栈科技的竞争对手是谁？",          # 知识库没有 → 应拒答
]

for q in QUESTIONS:
    print("=" * 60)
    print("问:", q)
    print("答:", rag_chain.invoke(q).strip())
