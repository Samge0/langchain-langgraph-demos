# L07 · LangGraph 基础 —— State / Node / Edge / Reducer / 循环

## 运行
```bash
.venv/Scripts/python.exe -m L07_langgraph_basics.01_state_graph_basics
.venv/Scripts/python.exe -m L07_langgraph_basics.02_reducer_conditional_loop
.venv/Scripts/python.exe -m L07_langgraph_basics.03_node_hardening
```

## 面试考点

### 1. LangGraph 三要素与编码七步
- 状态(State)：节点间传递的数据（TypedDict schema）；节点(Node)：函数 `(state) -> state增量`；
  边(Edge)：连接节点，含条件边。
- 七步：定义状态 → 定义节点 → builder → add_node → add_edge → compile → invoke。
- **节点返回的是"增量"**，框架负责按 reducer 合并 —— 这是与普通函数调用的本质区别。

### 2. Reducer（面试高频）
- `Annotated[list, operator.add]`：同名 key 多个节点同时写时如何合并。
- 默认行为是"覆盖"；并行分支写同一 key 必须声明 reducer，否则 InvalidUpdateError。
- 追问：为什么需要它 → **Super-Step 执行模型**：同一超步内并行节点产生的写入，
  在超步边界统一 reduce 后广播 —— 这是 BSP（ Bulk Synchronous Parallel ）模型。

### 3. 条件边与循环
- `add_conditional_edges(node, router_fn)`：router 返回下一节点名/END。
- 循环 = 回边；**必须设 recursion_limit 防失控**（面试必提的生产安全阀）。

### 4. 节点工程化
- RetryPolicy：瞬时错误重试（指数退避）。
- RunnableConfig：`config["configurable"]` 传运行时参数（如 user_id）。
- 一句话总结：**"LangGraph 把 Agent 从'隐式循环'升级为'显式状态机'，可控、可观测、可恢复。"**
