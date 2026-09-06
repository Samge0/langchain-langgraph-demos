"""03 · 流式 / 异步 / 批量 —— 生产调用的三种姿势。

面试考点：
- stream(): AIMessageChunk 增量拼接，改善首字延迟。
- ainvoke/abatch: 单模型实例 + 事件循环并发，IO 密集场景吞吐高。
- batch(): 底层线程池并发；abatch 异步版。
- 追问链：为什么流式能改善体感但总耗时不变 → chunk 在框架层如何合并
  （AIMessageChunk 重载了 __add__）→ 并发调用的限流怎么做（信号量/批量接口）。
"""
import asyncio

from common.config import get_llm

llm = get_llm()

# ---------- 1. 流式 ----------
print("== 1. stream ==")
chunks = []
for chunk in llm.stream("用三句话介绍 ReAct 模式"):
    chunks.append(chunk)
    print(chunk.content, end="", flush=True)
print("\n拼接后完整内容长度:", len("".join(c.content for c in chunks)), "\n")

# ---------- 2. 异步并发 ----------
async def main():
    results = await asyncio.gather(
        llm.ainvoke("一句话：什么是 Tool Calling?"),
        llm.ainvoke("一句话：什么是 RAG?"),
        llm.ainvoke("一句话：什么是 MCP?"),
    )
    for i, r in enumerate(results, 1):
        print(f"[async {i}] {r.content.strip()[:80]}")

print("== 2. async 并发 ==")
asyncio.run(main())
print()

# ---------- 3. 批量 ----------
print("== 3. batch ==")
answers = llm.batch(["一句话：什么是 Checkpointer?", "一句话：什么是 Middleware?"])
for a in answers:
    print("-", a.content.strip()[:80])
