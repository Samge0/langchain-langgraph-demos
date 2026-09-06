# L03 · LCEL 声明式链（LangChain Expression Language）

## 运行
```bash
.venv/Scripts/python.exe -m L03_lcel_chains.01_sequence_basics
.venv/Scripts/python.exe -m L03_lcel_chains.02_parallel_branch_fallback
.venv/Scripts/python.exe -m L03_lcel_chains.03_custom_runnable
```

## 面试考点

### 1. LCEL 是什么？为什么比"函数顺序调用"好？
- `|` 把 Runnable 组成 RunnableSequence，一次 `.invoke()` 驱动全链。
- 免费获得：流式（逐级透传 chunk）、异步（自动 a 前缀）、批量、重试
  （`.with_retry()`）、fallback（`.with_fallbacks()`）、LangSmith 追踪。
- 面试金句：**"LCEL 把编排从命令式变成声明式，可观测和容错成为链的属性而不是业务代码。"**

### 2. 并行与分支
- RunnableParallel（或直接写字典）同时跑多条链，输入广播、输出按 key 收拢。
- 典型生产模式：**RAG 答案链与引用链并行**；多评审并行再合成。

### 3. fallback 为什么是面试亮点
- 演示主链挂掉自动切备用链（如 vLLM 不可达 → 备用端点）。
- 追问：重试与降级的区别 → 重试针对瞬时错误（网络抖动），fallback 针对确定性失败（服务下线）。

### 4. RunnableLambda / RunnablePassthrough
- 自定义逻辑进链、以及 **passthrough 常用于 RAG 中"原文 + 检索结果"一起下传**（L11 会再次出现）。
