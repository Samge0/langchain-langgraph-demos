# L02 · 提示词工程 + 结构化输出

## 运行
```bash
.venv/Scripts/python.exe -m L02_prompts_structured_output.01_prompt_templates
.venv/Scripts/python.exe -m L02_prompts_structured_output.02_structured_output
.venv/Scripts/python.exe -m L02_prompts_structured_output.03_parsers_and_fewshot
```

## 面试考点

### 1. PromptTemplate vs ChatPromptTemplate？
- Chat 模型一律用 ChatPromptTemplate；**必须用 `("role", "template")` 元组格式**，
  直接塞 SystemMessage 对象不会被当作模板渲染（`{变量}`不替换）—— 高频踩坑题。
- MessagesPlaceholder 承载对话历史/少样本消息列表，是多轮应用的必备件。

### 2. 结构化输出（面试必考）
- `llm.with_structured_output(PydanticModel)` 底层实现有三种：
  1. `function_calling`（默认）：走 tool-calling 协议，约束最强；
  2. `json_schema`：响应格式约束（需要后端支持 structured outputs）；
  3. `json_mode`：只保证是 JSON，不保证 schema，需要校验重试。
- 追问链：模型输出不合法 JSON 怎么办 →（校验失败自动重试 / OutputFixingParser /
  降低温度 / few-shot 给格式示例）→ 为什么 Pydantic 字段描述很重要
  （description 会被序列化进 schema，直接影响抽取准确率）。
- 生产建议：schema 字段少而稳、枚举值用 Literal、嵌套别超过 2 层 —— 小模型深嵌套错误率陡增。

### 3. Few-shot 的两种形态
- prompt 文本内嵌示例（零依赖、token 便宜）；
- MessagesPlaceholder + 示例消息对（规范、可动态挑选，进化为"动态少样本检索"——
  面试亮点：按相似度从示例库挑最相关的 k 条注入）。
