# L01 · Hello LLM —— 一切从"模型会说话"开始

## 运行
```bash
cd demos
.venv/Scripts/python.exe -m L01_hello_llm.01_openai_sdk_raw
.venv/Scripts/python.exe -m L01_hello_llm.02_chatopenai_messages
.venv/Scripts/python.exe -m L01_hello_llm.03_stream_async_batch
```

## 面试考点

### 1. OpenAI SDK 与 LangChain 的关系？
- `openai` SDK 是**协议客户端**；LangChain 是**应用编排框架**，底层仍走同一协议。
- ChatOpenAI 传 `base_url` 即可指向任何 OpenAI 兼容后端（vLLM/DeepSeek/Qwen/GLM），
  这是"协议解耦"：换模型不改代码。
- 追问链：消息模型（System/User/Assistant/Tool 四种角色）→ 为什么 Chat 范式赢了
  （对齐 RLHF 是按对话轮训练的）→ token 计费与上下文窗口的关系。

### 2. 流式输出的原理？
- SSE（Server-Sent Events）：HTTP 长连接上分块推送 JSON，每个 chunk 含增量 token。
- 框架里 `stream()` 返回 AIMessageChunk 迭代器，chunk 会自动拼接。
- 追问：为什么 LLM 逐 token 生成（自回归采样）→ 首 token 延迟(TTFT)由什么决定
  （prefill 计算量 + KV cache）→ 为什么流式能改善体感（首字时间从秒级降到百毫秒级）。
