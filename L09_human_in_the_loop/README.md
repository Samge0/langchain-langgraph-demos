# L09 · Human-in-the-Loop —— interrupt / Command(resume)

## 运行
```bash
.venv/Scripts/python.exe -m L09_human_in_the_loop.01_interrupt_basics
.venv/Scripts/python.exe -m L09_human_in_the_loop.02_hitl_middleware
```

## 面试考点

### 1. 为什么要 HITL？（答案模板）
> "Agent 拥有真实世界执行力后，高风险动作（转账/删库/发邮件/下单）必须有人审批。
> LangGraph 的 interrupt() 把图**暂停在节点中间**，状态已持久化，
> 人审批后 Command(resume=...) 从断点恢复 —— 全过程服务可以重启，不丢状态。"

### 2. interrupt() vs 中断异常
- interrupt(payload) 抛出特殊信号 → 图停止 → result["__interrupt__"] 携带 payload。
- 恢复必须带 checkpointer（断点信息存在快照里）—— **没有 checkpointer 就没有 HITL**。
- resume 的值就是 interrupt() 的返回值 —— 语义：仿佛从未中断过。

### 3. 三种审批决策（面试要能说出报文格式）
- approve：`Command(resume={"decision": {"type": "approve"}})`
- edit：`{"type": "edit", "edited_action": {"name":..., "args": {...}}}` —— 人改参数后执行
- reject：拒绝并告知模型原因，让模型向用户解释

### 4. HumanInTheLoopMiddleware（create_agent 层）
- 不用在工具里写 interrupt，声明式 `interrupt_on={"transfer_money": True}`。
- 面试金句："**中间件把审批策略从工具实现里剥离 —— 安全策略集中在 Agent 装配层。**"
