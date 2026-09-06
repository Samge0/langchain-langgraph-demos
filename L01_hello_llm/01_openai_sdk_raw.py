"""01 · 最原始的 OpenAI SDK 直连 —— 看清没有框架时发生了什么。

面试考点：
- messages 列表是 LLM API 的通用数据结构（role + content）。
- stateless：服务端不保存对话，多轮 = 你把全部历史再发一遍。
  （这直接引出后面的 Checkpointer/记忆管理为什么必要）
"""
from openai import OpenAI

from common.config import llm_api_key, llm_base_url, llm_model

client = OpenAI(base_url=llm_base_url(), api_key=llm_api_key())

messages = [
    {"role": "system", "content": "你是一个简洁的中文技术助手，回答不超过两句话。"},
    {"role": "user", "content": "什么是大语言模型？"},
]

resp = client.chat.completions.create(model=llm_model(), messages=messages, temperature=0.3)

print("== 第一次回复 ==")
print(resp.choices[0].message.content)

# 关键点：多轮对话必须手动拼接全部历史（服务端无状态）
messages.append({"role": "assistant", "content": resp.choices[0].message.content})
messages.append({"role": "user", "content": "用它写一句自我介绍。"})

resp2 = client.chat.completions.create(model=llm_model(), messages=messages)
print("\n== 第二次回复（带历史）==")
print(resp2.choices[0].message.content)

# 展示用量统计 —— 面试常问"你怎么控制成本"
print("\n== token 用量 ==")
print(resp2.usage)
