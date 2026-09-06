# L04 · Tool Calling —— Agent 的原子能力（面试核心课）

## 运行
```bash
.venv/Scripts/python.exe -m L04_tool_calling.01_raw_openai_tool_call
.venv/Scripts/python.exe -m L04_tool_calling.02_langchain_bind_tools
.venv/Scripts/python.exe -m L04_tool_calling.03_manual_agent_loop
```

## 面试考点（这课是"Agent 是什么"的标准答案来源）

### 1. 一次 Tool Calling 的完整时序（必须能白板画出来）
```
User → LLM(带 tools schema) → AIMessage(tool_calls=[{name,args,id}])
     → 你执行本地函数 → ToolMessage(result, tool_call_id)
     → 再发给 LLM → AIMessage(最终自然语言回答)
```
- 关键不变式：**tool_call_id 必须一一对应**；ToolMessage 必须紧跟对应的 AIMessage。
- 模型不执行任何函数！它只输出"想调用什么+参数 JSON"，执行永远在你的进程里。
- 追问链：args 是模型生成的 JSON，怎么保证合法（schema 约束+解析校验+重试）→
  并行工具调用（一次 AIMessage 带多个 tool_calls）→ 强制调用（tool_choice）→
  工具越多越好吗（选择准确率下降，>20 个应分组/路由/RAG 选工具）。

### 2. vLLM/OpenAI 兼容后端要开什么
- 服务端：`--enable-auto-tool-choice --tool-call-parser qwen3_coder`（对应模型族）。
- 客户端：ChatOpenAI.bind_tools(...)，LangChain 把 @tool 的 Pydantic schema
  翻译成 OpenAI tools JSON —— 这就是 01 和 02 在协议层完全一致的原因。

### 3. 手写 Agent Loop（03 课）
- while 循环：invoke → 有 tool_calls 就执行并回填 → 直到没有 tool_calls 或达到步数上限。
- create_agent（L05）＝ 把这个循环产品化：加上了状态管理、checkpoint、中间件、流式。
- 面试金句："**Agent = LLM + 工具 + 循环 + 停止条件**。"
