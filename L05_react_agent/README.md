# L05 · create_agent 与 ReAct 模式

## 运行
```bash
.venv/Scripts/python.exe -m L05_react_agent.01_first_agent
.venv/Scripts/python.exe -m L05_react_agent.02_agent_anatomy
```

## 面试考点

### 1. create_agent 是什么？
- LangChain 1.x 的官方 Agent 入口（底层就是 LangGraph 编译出的 CompiledGraph，
  内置 AgentLoop：model ↔ tools 循环节点）。
- 与手写 loop 的差别：状态托管（messages reducer 自动累积）、
  流式（values/messages/updates 三种模式）、可挂 middleware/checkpointer。
- 追问链：result["messages"] 里每一类消息的顺序 → system prompt 注入在哪层 →
  什么时候该自己写图而不是用 create_agent（控制流复杂/需要并行分支/子图嵌套时）。

### 2. ReAct 模式（Reason + Act）
- 2022 年论文提出的经典范式：思考→行动→观察 循环。
- 现代 function-calling Agent 是 ReAct 的工程化变体：
  推理隐含在 AIMessage 中，行动=tool_calls，观察=ToolMessage。
- 面试金句："**现代 Agent 框架的循环本质都是 ReAct；区别只在状态管理与控制流的工程化程度。**"

### 3. 流式模式区别
- `values`：每步全量状态；`updates`：每步增量；`messages`：token 级流式（前端打字机效果用这个）。
