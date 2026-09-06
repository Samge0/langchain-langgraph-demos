# -*- coding: utf-8 -*-
"""全量回归：依次运行 L01-L12 全部 demo，收集结果，生成 VERIFICATION.md。"""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"F:\Download\sgg-langchain\demos")
PY = ROOT / ".venv" / "Scripts" / "python.exe"

# (模块, 备注)；06 的 http server 需要外部起，这里单独处理
CASES = [
    ("L01_hello_llm.01_openai_sdk_raw", ""),
    ("L01_hello_llm.02_chatopenai_messages", ""),
    ("L01_hello_llm.03_stream_async_batch", ""),
    ("L02_prompts_structured_output.01_prompt_templates", ""),
    ("L02_prompts_structured_output.02_structured_output", ""),
    ("L02_prompts_structured_output.03_parsers_and_fewshot", ""),
    ("L03_lcel_chains.01_sequence_basics", ""),
    ("L03_lcel_chains.02_parallel_branch_fallback", ""),
    ("L03_lcel_chains.03_custom_runnable", ""),
    ("L04_tool_calling.01_raw_openai_tool_call", ""),
    ("L04_tool_calling.02_langchain_bind_tools", ""),
    ("L04_tool_calling.03_manual_agent_loop", ""),
    ("L05_react_agent.01_first_agent", ""),
    ("L05_react_agent.02_agent_anatomy", ""),
    ("L06_mcp.stdio_client_demo", "stdio 自含 server"),
    ("L07_langgraph_basics.01_state_graph_basics", ""),
    ("L07_langgraph_basics.02_reducer_conditional_loop", ""),
    ("L07_langgraph_basics.03_node_hardening", ""),
    ("L08_memory_checkpointer.01_in_memory_short_term", ""),
    ("L08_memory_checkpointer.02_sqlite_long_term", "先--write再读"),
    ("L08_memory_checkpointer.03_time_travel", ""),
    ("L09_human_in_the_loop.01_interrupt_basics", ""),
    ("L09_human_in_the_loop.02_hitl_middleware", ""),
    ("L10_middleware_context.01_summarization_middleware", ""),
    ("L10_middleware_context.02_custom_middleware", ""),
    ("L11_rag.02_hybrid_retrieval", "需要索引已存在"),
    ("L11_rag.03_rag_agent", "需要索引已存在"),
    ("L12_multi_agent.01_supervisor_team", ""),
]


def run(mod: str, note: str, extra: list[str] | None = None, timeout: int = 240):
    t0 = time.time()
    r = subprocess.run(
        [str(PY), "-m", mod] + (extra or []),
        cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    dt = time.time() - t0
    ok = r.returncode == 0
    return ok, dt, (r.stdout or "")[-400:], (r.stderr or "")[-400:]


def main():
    results = []

    # L06 http：先起 server
    server = subprocess.Popen(
        [str(PY), "-m", "L06_mcp.http_mcp_server"],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(5)
    try:
        results.append(("L06_mcp.langchain_mcp_agent", "需先起 http server", *run("L06_mcp.langchain_mcp_agent", "")))
    finally:
        server.terminate()

    for mod, note in CASES:
        extra = ["--write"] if mod.endswith("02_sqlite_long_term") else None
        if mod.endswith("02_sqlite_long_term"):
            ok, dt, out, err = run(mod, note, ["--write"])
            results.append((mod + " [write]", note, ok, dt, out, err))
            ok, dt, out, err = run(mod, note)
            results.append((mod + " [read]", note, ok, dt, out, err))
            continue
        ok, dt, out, err = run(mod, note, extra)
        results.append((mod, note, ok, dt, out, err))

    # 汇总
    lines = ["# Demos 全量验证报告", "", f"运行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}", "",
             "| # | 模块 | 结果 | 耗时 | 备注 |", "|---|---|---|---|---|"]
    n_pass = n_fail = 0
    for i, (mod, note, ok, dt, out, err) in enumerate(results, 1):
        status = "PASS" if ok else "**FAIL**"
        n_pass += ok
        n_fail += (not ok)
        lines.append(f"| {i} | {mod} | {status} | {dt:.1f}s | {note} |")
        if not ok:
            tail = (err or out).strip().splitlines()[-3:]
            lines.append(f"    - 错误尾部: {' / '.join(tail)}")
    lines += ["", f"**总计 {len(results)} 项：通过 {n_pass}，失败 {n_fail}**", ""]
    report = "\n".join(lines)
    (ROOT / "VERIFICATION.md").write_text(report, encoding="utf-8")
    print(report)

    # MCP http case 的结果补录（它在 server 循环里已 append，无 note 字段——统一处理过了吗?）
    # 注：上面 L06 那条 append 少了 note 字段时不影响打印（tuple 长度对齐校验）
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
