# Qwen 模型家族备忘

Qwen3 系列是阿里云通义实验室于 2025 年发布的开源大模型家族，覆盖 0.6B 到 235B 参数规模。

关键版本节点：
- Qwen2.5：2024 年 9 月发布，首次提供 128K 上下文的商用授权模型。
- Qwen3-8B：2025 年 4 月发布，支持思考/非思考双模式切换。
- Qwen3-Coder：2025 年 7 月发布，480B MoE 架构，专注代码生成。

部署要点：vLLM 加载 Qwen3 GPTQ-Int4 量化版时，建议开启 `--enable-auto-tool-choice`
并配置 `--tool-call-parser qwen3_coder`；思考模式可通过 chat template 参数
`enable_thinking: false` 关闭以降低首 token 延迟。

许可协议：Qwen3 全系列采用 Apache 2.0，允许商用；超过 100B 参数的模型需要遵循额外的使用政策。
