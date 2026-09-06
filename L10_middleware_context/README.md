# L10 · Middleware 与上下文工程

## 运行
```bash
.venv/Scripts/python.exe -m L10_middleware_context.01_summarization_middleware
.venv/Scripts/python.exe -m L10_middleware_context.02_custom_middleware
```

## 面试考点

### 1. 为什么需要 SummarizationMiddleware（上下文工程必考）
- 问题：长会话 messages 无限增长 → token 成本上升 + 上下文窗口溢出 + 噪声降低质量。
- 方案：token 阈值触发 → 把旧消息压缩为一条摘要 → 保留最近 keep 窗口。
- `trigger=("tokens", N)` 预估输入 token 达标即压缩；`keep=("tokens", M)` 保留最近窗口。
- 追问链：摘要丢失细节怎么办（关键事实外置到 Store/结构化记忆，见 L08 分层表）→
  与 KV-cache 的关系（前缀截断会破坏缓存命中，生产要平衡压缩频率）→
  滑动窗口 vs 摘要 vs 混合（窗口省 token 但丢早期信息，摘要保语义但有压缩损耗）。

### 2. Middleware 的钩子模型
- 请求前（改 prompt/注入上下文）、响应后（审计）、模型调用前后（重试/降级）、工具执行前后（HITL/脱敏）。
- 自定义中间件继承 AgentMiddleware，实现 before_model/after_model/wrap_model_call 等钩子。
- 面试金句："**Middleware 是 Agent 的 AOP：横切关注点（记忆、安全、审计、降级）与业务解耦。**"

### 3. 动态 System Prompt
- dynamic_prompt=True 的中间件可以在每次模型调用前把 state 里的信息（用户画像等）注入 prompt
  —— 这是"个性化上下文工程"的标准做法。
