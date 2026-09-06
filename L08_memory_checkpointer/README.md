# L08 · Checkpointer —— Agent 的记忆系统

## 运行
```bash
.venv/Scripts/python.exe -m L08_memory_checkpointer.01_in_memory_short_term
.venv/Scripts/python.exe -m L08_memory_checkpointer.02_sqlite_long_term
.venv/Scripts/python.exe -m L08_memory_checkpointer.03_time_travel
```

## 面试考点

### 1. 记忆的分层（必考）
| 层级 | 载体 | 生命周期 | 实现 |
|---|---|---|---|
| 短期记忆 | 线程内消息历史 | 会话内 | checkpointer + thread_id |
| 长期记忆 | 跨会话事实 | 永久 | Store / 外部 DB（用户画像等） |
| 上下文压缩 | 摘要替代历史 | 会话内 | SummarizationMiddleware（L10） |

### 2. Checkpointer 的工作机制
- 每个超步结束把**全量 state 快照**持久化，以 `(thread_id, checkpoint_id)` 寻址。
- 换 checkpointer 实现不改业务代码：InMemorySaver（测试）/ SqliteSaver（单机持久）
  / PostgresSaver（生产）/ Redis —— **这是"状态持久化与业务解耦"的面试金句**。
- 面试金句："**thread_id 是会话隔离的钥匙；同一个 agent，不同 thread 记忆互不可见。**"

### 3. 时间旅行（亮点答案）
- get_state_history() 拿到全部历史快照 → 用 checkpoint_id 重放。
- 价值：调试回放、审计、分支推演（"如果当时走另一条边会怎样"）。
- 追问：和事件溯源(Event Sourcing)的关系 —— checkpoint 本质就是 state 的事件溯源。

### 4. SqliteSaver 细节
- `sqlite3.connect(..., check_same_thread=False)`：LangGraph 内部线程池并发访问。
- 生产用 PostgresSaver：并发写安全 + 异步支持（SqliteSaver 无 async）。
