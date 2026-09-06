"""02 · 并行 / 分支 / 回退 —— LCEL 的工程价值所在。

面试考点：
- RunnableParallel：广播输入、按 key 收拢输出，I/O 并发省时延。
- with_fallbacks：确定性失败的自动降级；with_retry：瞬时错误重试。
- 面试金句："并行是把延迟预算花在刀刃上，fallback 是把可用性写进编排层。"
"""
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from common.config import get_llm

llm = get_llm()
parser = StrOutputParser()

# ---------- 1. 并行：同一路况出三个视角 ----------
pros = ChatPromptTemplate.from_template("用一句话说明 {tech} 的优点") | llm | parser
cons = ChatPromptTemplate.from_template("用一句话说明 {tech} 的缺点") | llm | parser
use_case = ChatPromptTemplate.from_template("用一句话给出 {tech} 的典型使用场景") | llm | parser

parallel = RunnableParallel(pros=pros, cons=cons, use_case=use_case)

t0 = time.time()
r = parallel.invoke({"tech": "RAG"})
print("== 并行三链（串行约 3 倍耗时，这里并行）==")
for k, v in r.items():
    print(f"[{k}] {v.strip()[:70]}")
print(f"耗时 {time.time()-t0:.1f}s\n")

# ---------- 2. 分支路由：RunnableLambda 按条件返回不同子链 ----------
simple_chain = ChatPromptTemplate.from_template("一句话回答：{q}") | llm | parser
detail_chain = ChatPromptTemplate.from_template("用3个要点回答：{q}") | llm | parser

def router(d: dict):
    """路由函数：返回将要执行的 Runnable（分支在运行时才确定）。"""
    return detail_chain if d["mode"] == "detail" else simple_chain

branch = RunnableLambda(router)
print("== 分支路由(detail) ==")
print(branch.invoke({"mode": "detail", "q": "什么是向量数据库"}))
print()
print("== 分支路由(simple) ==")
print(branch.invoke({"mode": "simple", "q": "什么是向量数据库"}), "\n")

# ---------- 3. Fallback：主链指向一个不存在的端口，自动切备用 ----------
from langchain_openai import ChatOpenAI
from common.config import llm_api_key, llm_model

broken_llm = ChatOpenAI(
    base_url="http://localhost:9/v1", api_key=llm_api_key(),
    model=llm_model(), timeout=3, max_retries=0,
)
main_chain = ChatPromptTemplate.from_template("一句话：{q}") | broken_llm | parser
backup_chain = ChatPromptTemplate.from_template("一句话：{q}") | llm | parser
robust = main_chain.with_fallbacks([backup_chain])

print("== fallback（主链必挂→备用链接管）==")
print(robust.invoke({"q": "什么是 Agent Loop"}).strip())
