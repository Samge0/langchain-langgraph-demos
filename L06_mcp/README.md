# L06 · MCP（Model Context Protocol）

## 运行（三个终端或按顺序执行）
```bash
# 1) 先启动 HTTP MCP 服务端（常驻）
.venv/Scripts/python.exe -m L06_mcp.http_mcp_server

# 2) stdio 演示（自带服务端，独立可跑）
.venv/Scripts/python.exe -m L06_mcp.stdio_client_demo

# 3) HTTP 客户端 + Agent（服务端启动后再跑）
.venv/Scripts/python.exe -m L06_mcp.langchain_mcp_agent
```

## 面试考点

### 1. MCP 解决什么问题？
- M×N 集成困境：M 个应用 × N 个工具两两适配 → M+N。
- MCP 把"工具提供"标准化为协议：**Host(应用) 内嵌 Client，与 Server 进程通信**。
- Server 暴露三类能力：tools（可调用函数）、resources（可读数据）、prompts（提示模板）。

### 2. 两种传输方式（面试必考对比）
| | stdio | streamable-http |
|---|---|---|
| 拓扑 | Client 子进程，stdin/stdout 通信 | 独立 HTTP 服务 |
| 场景 | 本地工具（文件、本地DB） | 远程/共享工具服务，多客户端复用 |
| 生命周期 | 随 Client 存亡 | 独立部署、独立扩缩容 |

### 3. 与 LangChain 的结合
- `langchain-mcp-adapters` 的 MultiServerMCPClient.get_tools() 把 MCP tools
  翻译成 LangChain tool 列表 → create_agent 直接使用。
- 面试金句："**MCP 是工具生态的 USB-C：工具方实现一次 Server，所有支持 MCP 的 Agent 都能用。**"
- 追问链：MCP tool 与本地 @tool 在 Agent 视角有区别吗（无区别，都编译成同一 OpenAI tools schema）
  → 权限与安全（工具白名单、HITL 审批 L09）→ 和 OpenAI 的 function calling 关系
  （MCP 是工具分发协议，FC 是单次调用的模型协议，二者互补）。
