# Demos 全量验证报告

运行时间: 2026-09-06 19:08:52

| # | 模块 | 结果 | 耗时 | 备注 |
|---|---|---|---|---|
| 1 | L06_mcp.langchain_mcp_agent | PASS | 8.4s | 需先起 http server |
| 2 | L01_hello_llm.01_openai_sdk_raw | PASS | 5.1s |  |
| 3 | L01_hello_llm.02_chatopenai_messages | PASS | 15.3s |  |
| 4 | L01_hello_llm.03_stream_async_batch | PASS | 11.3s |  |
| 5 | L02_prompts_structured_output.01_prompt_templates | PASS | 6.8s |  |
| 6 | L02_prompts_structured_output.02_structured_output | PASS | 10.3s |  |
| 7 | L02_prompts_structured_output.03_parsers_and_fewshot | PASS | 6.8s |  |
| 8 | L03_lcel_chains.01_sequence_basics | PASS | 8.0s |  |
| 9 | L03_lcel_chains.02_parallel_branch_fallback | PASS | 14.1s |  |
| 10 | L03_lcel_chains.03_custom_runnable | PASS | 18.7s |  |
| 11 | L04_tool_calling.01_raw_openai_tool_call | PASS | 7.2s |  |
| 12 | L04_tool_calling.02_langchain_bind_tools | PASS | 7.3s |  |
| 13 | L04_tool_calling.03_manual_agent_loop | PASS | 9.4s |  |
| 14 | L05_react_agent.01_first_agent | PASS | 7.5s |  |
| 15 | L05_react_agent.02_agent_anatomy | PASS | 10.2s |  |
| 16 | L06_mcp.stdio_client_demo | PASS | 2.1s | stdio 自含 server |
| 17 | L07_langgraph_basics.01_state_graph_basics | PASS | 1.3s |  |
| 18 | L07_langgraph_basics.02_reducer_conditional_loop | PASS | 1.3s |  |
| 19 | L07_langgraph_basics.03_node_hardening | PASS | 3.0s |  |
| 20 | L08_memory_checkpointer.01_in_memory_short_term | PASS | 6.7s |  |
| 21 | L08_memory_checkpointer.02_sqlite_long_term [write] | PASS | 6.1s | 先--write再读 |
| 22 | L08_memory_checkpointer.02_sqlite_long_term [read] | PASS | 5.9s | 先--write再读 |
| 23 | L08_memory_checkpointer.03_time_travel | PASS | 1.1s |  |
| 24 | L09_human_in_the_loop.01_interrupt_basics | PASS | 1.1s |  |
| 25 | L09_human_in_the_loop.02_hitl_middleware | PASS | 8.9s |  |
| 26 | L10_middleware_context.01_summarization_middleware | PASS | 11.3s |  |
| 27 | L10_middleware_context.02_custom_middleware | PASS | 15.2s |  |
| 28 | L11_rag.02_hybrid_retrieval | PASS | 11.2s | 需要索引已存在 |
| 29 | L11_rag.03_rag_agent | PASS | 17.5s | 需要索引已存在 |
| 30 | L12_multi_agent.01_supervisor_team | PASS | 8.5s |  |

**总计 30 项：通过 30，失败 0**
