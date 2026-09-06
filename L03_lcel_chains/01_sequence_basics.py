"""01 · 顺序链基础：prompt | llm | parser 等价于 RunnableSequence。

面试考点：
- `|` 语法糖 == RunnableSequence(first, middle..., last)。
- 链是一次编译、多次调用；invoke/stream/batch 全支持。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence

from common.config import get_llm

llm = get_llm()

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是资深技术评审，用不超过两句话点评。"),
    ("human", "请点评{topic}在{aspect}方面的优缺点。"),
])
parser = StrOutputParser()

# 三种等价写法 —— 面试要能说出来它们是同一个东西
chain_pipe = prompt | llm | parser
chain_cls = RunnableSequence(prompt, llm, parser)

res = chain_pipe.invoke({"topic": "LangGraph 状态机编排", "aspect": "可维护性"})
print("== pipe 写法 ==")
print(res.strip(), "\n")

res2 = chain_cls.invoke({"topic": "vLLM 部署", "aspect": "吞吐优化"})
print("== RunnableSequence 写法 ==")
print(res2.strip(), "\n")

# 流式在链上直接可用（逐级透传 chunk）
print("== 链上流式 ==")
for chunk in chain_pipe.stream({"topic": "MCP 协议", "aspect": "生态兼容"}):
    print(chunk, end="", flush=True)
print()
