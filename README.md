# LangChain / LangGraph / Agent 学习 Demos

> 🌐 **[在线宣传页](https://samge0.github.io/langchain-langgraph-demos/)** — 12 课路径、面试考点体系、技术栈一页看懂

> LangChain V1.1.0 + LangGraph V1.1.0 课程资料重构，
> 对齐 2026 年 **LangChain 1.x / LangGraph 1.x** 正式版 API（`create_agent`、Middleware、Checkpointer、MCP），
> 每一课都是**可运行、有面试考点注释、可验证输出**的完整 demo。

## 运行环境

| 项 | 值 |
|---|---|
| LLM | 本机 vLLM（Qwen3.8-9B，OpenAI 兼容协议，`http://localhost:16869/v1`，已开 auto-tool-choice + qwen3_coder tool parser） |
| Embedding | 本地 `models/bge-small-zh-v1.5`（512 维，已从 ModelScope 拉取，离线可用） |
| 向量库 | FAISS(cpu) + BM25（无需 Docker 常驻；概念等价于课件里的 Milvus 稠密+稀疏混合检索） |
| Python | 3.11，依赖见 `requirements.txt`（langchain 1.2.3 / langgraph 1.0.5，与课件一致） |

```bash
# 首次使用
cp .env.example .env      # 填入你的 vLLM api-key
uv venv .venv --python 3.11
uv pip install --python .venv/Scripts/python.exe -r requirements.txt \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match
# 每课运行方式（在 demos/ 目录下）
.venv/Scripts/python.exe -m L04_tool_calling.01_raw_openai_tool_call
```

## 学习路线图（建议顺序，每课 30-60 分钟）

```
基础层 ─ 模型会"说话"
 L01 hello_llm ................ 直连 LLM：OpenAI SDK vs ChatOpenAI，流式/异步/批量
 L02 prompts_structured_output . 提示词工程 + Pydantic 结构化输出（面试必考）
 L03 lcel_chains ............... LCEL：声明式管线 | prompt | llm | parser，并行/分支/回退

工具层 ─ 模型会"动手"
 L04 tool_calling .............. 手写 Tool Calling 循环（/raw SDK 与框架版对照，Agent 的原子能力）
 L05 react_agent ............... create_agent + AgentLoop：ReAct 循环、多工具、思维链
 L06 mcp ....................... MCP 协议：stdio / streamable-http 服务端 + 客户端接入 Agent

图引擎层 ─ 模型会"编排"
 L07 langgraph_basics .......... State/Node/Edge/Reducer/条件边/循环：Super-Step 执行模型
 L08 memory_checkpointer ....... Checkpointer：短期记忆→线程→长期记忆→时间旅行
 L09 human_in_the_loop ......... interrupt + Command(resume)：风险动作人工审批（面试高频）

工程化层 ─ 模型会"上线"
 L10 middleware_context ........ Middleware：Summarization 上下文压缩、敏感工具拦截
 L11 rag ....................... 生产级 RAG：切分→FAISS+BM25 混合检索→RRF→引用生成→可评测
 L12 multi_agent ............... Supervisor 多智能体：任务分解、专业 Agent 协作、消息传递
```

## 为什么是这个顺序（对应面试考察体系）

1. **L01-L03** 对应"Model I/O"：面试官确认你懂底层（消息模型、结构化输出原理），而不只是会调包。
2. **L04 是 Agent 的原子能力**：Tool Calling 本质是"模型输出 JSON → 你执行 → 结果回填 messages"。
   面试必考"Agent 的执行循环是什么"，这一课让你能手写它，create_agent 只是把这个循环自动化。
3. **L05-L06** 是"用框架的正确姿势"：create_agent 的 AgentLoop、MCP 工具生态（2025+ 行业标准）。
4. **L07-L09** 对应 LangGraph 核心：状态图 = 可控的 Agent 编排；Checkpointer = 记忆；
   interrupt = 人机协同。**这三点是 Agent 岗面试的最高频考点**。
5. **L10-L12** 对应生产化：上下文工程（token 预算）、RAG 全链路优化、多智能体任务分解。

## 目录结构

```
demos/
├── common/            # 共用配置：模型接入、embedding、路径（面试讲"协议解耦"的活例子）
├── data/knowledge/    # RAG 知识库原始文档（Markdown）
├── models/            # 本地 embedding 模型（bge-small-zh-v1.5）
├── L01_hello_llm/     ... L12_multi_agent/   # 12 课，每课 README + 若干可运行 demo
├── requirements.txt
└── .env.example
```

## 与 source 课程资料的对照

| source 资料 | 本 demos |
|---|---|
| `langchain_1208_demo/model_io/`(13个文件) | L01-L03（重写为 1.x API + 中文注释 + 面试考点） |
| `langchain/agents`、`langgraph/agents` | L04-L06（raw 循环是新增的面试深化内容） |
| `langgraph/graph/`(12个文件) | L07（合并为渐进式一课） |
| `checkpointer/`、`middleware/` | L08-L10（补充时间旅行、token 触发压缩的原理） |
| `rag/`(Milvus+BGE-M3) | L11（FAISS+BM25 等价概念映射，无需 Docker，README 里有对照表） |
| `RAG优化分享.txt` | L11 README 的"RAG 优化军火库"一节（大小块、混合检索、重排、查询改写） |
| 两份 docx 课件 | 各课 README 的"面试考点"小节 |

## 验证状态

全部 demo 已在本机（vLLM qwen38 + CPU embedding）逐一运行验证，回归脚本 `run_all.py` 可随时重跑：

```bash
.venv/Scripts/python.exe run_all.py   # 输出 VERIFICATION.md
```

最近一次回归：**30/30 PASS**（2026-09-06，详见 [VERIFICATION.md](VERIFICATION.md)）。
