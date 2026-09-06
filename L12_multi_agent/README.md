# L12 · Supervisor 多智能体系统

## 运行
```bash
.venv/Scripts/python.exe -m L12_multi_agent.01_supervisor_team
```

## 面试考点

### 1. 什么时候才用多智能体？（先答这个，避免"为了多而多"）
- 单 Agent 工具过多导致选择准确率下降；不同任务需要**不同的 system prompt/模型档位**；
  需要并行子任务；职责隔离与审计。否则优先单 Agent（成本低、链路简单）。
- 判据："**用多智能体买到的可维护性/准确率提升 > 编排与通信成本**"。

### 2. Supervisor 模式（本课实现）
```
用户 → supervisor(路由/汇总) ─┬→ researcher(检索) ─┐
                            └→ writer(写作) ─────┴→ supervisor → END
```
- supervisor 是普通节点：用结构化输出决定 `next=节点名 或 FINISH`。
- 工人 Agent 各自绑定自己的工具集，消息通过 state 传递（Annotated add reducer 累积）。
- 面试金句："**Supervisor 把'路由'显式化成图节点 —— 相比单 Agent 的隐式工具选择，可控可审计。**"

### 3. 与其他多智能体拓扑的对比
- Supervisor：中心化，易管控（生产首选）。
- Network/Swarm：去中心化，灵活但环路风险高。
- Hierarchical：Supervisor 嵌套 Supervisor（团队扩到 8-10+ Agent 时）。

### 4. 落地要点（高频追问）
- 循环上限：recursion_limit + supervisor 的 max round（防两个 Agent 互相踢皮球）。
- 通信内容：传"结论摘要"而不是全量消息（省 token、防上下文污染）。
- 可观测：每个工人一个 thread_id 前缀，checkpoint 隔离追踪。
