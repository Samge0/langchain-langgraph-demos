"""02 · SqliteSaver 长期记忆：进程重启后记忆仍在。

对照 source checkpointer/02_sqllite_saver_demo.py。
面试考点：checkpointer 实现可替换（内存/SQLite/Postgres），业务代码零改动。
"""
import sqlite3
from pathlib import Path

from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

from common.config import get_llm

DB_PATH = Path(__file__).parent / "agent_memory.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)   # 框架内部多线程访问
saver = SqliteSaver(conn)

agent = create_agent(
    model=get_llm(),
    system_prompt="你是记忆测试助手，回答不超过两句话。",
    checkpointer=saver,
)

cfg = {"configurable": {"thread_id": "persistent-1"}}

import sys
if "--write" in sys.argv:
    # 第一步：写入记忆（运行一次）
    r = agent.invoke({"messages": [{"role": "user",
                                    "content": "记住两件事：1.我在准备Agent面试 2.我的目标城市是深圳"}]}, cfg)
    print("[写入] ", r["messages"][-1].content.strip())
else:
    # 第二步：新进程只读（模拟"重启后"）—— 直接跑本脚本即可
    r = agent.invoke({"messages": [{"role": "user",
                                    "content": "我上次让你记住了哪两件事？"}]}, cfg)
    print("[跨进程读取] ", r["messages"][-1].content.strip())

print("\nDB 文件:", DB_PATH, "大小:", DB_PATH.stat().st_size, "bytes")
print("面试表述：把 SqliteSaver 换成 PostgresSaver 即生产化，业务代码零改动。")
