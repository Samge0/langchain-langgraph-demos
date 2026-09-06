"""common/config.py —— 全部 demo 共用的模型接入层。

面试考点（为什么这样封装）：
1. 所有代码只依赖 OpenAI 兼容协议（OpenAI 兼容已是事实标准：
   vLLM / Ollama / DeepSeek / Qwen / GLM 全部提供该协议），
   换后端只改 .env，代码零改动 —— 这就是"协议解耦"。
2. ChatOpenAI 交给 langchain 管线（LCEL/Agent），原始 openai SDK
   用于教学时展示"没有框架时 tool calling 该怎么手写"。
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# demos 根目录（任何工作目录下运行都能找到 .env / data / models）
DEMO_ROOT = Path(__file__).resolve().parent.parent

# 无论从哪个目录启动，都加载 demos/.env
load_dotenv(DEMO_ROOT / ".env")


def llm_base_url() -> str:
    return os.getenv("OPENAI_BASE_URL", "http://localhost:16869/v1")


def llm_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "EMPTY")


def llm_model() -> str:
    return os.getenv("OPENAI_MODEL", "qwen38")


@lru_cache(maxsize=1)
def get_llm(**overrides):
    """返回绑定了本机 vLLM 的 ChatOpenAI 实例（进程内复用）。"""
    from langchain_openai import ChatOpenAI

    kwargs = dict(
        base_url=llm_base_url(),
        api_key=llm_api_key(),
        model=llm_model(),
        temperature=0.3,
        # qwen3 思考模式已在服务端关闭；这里给一个宽松超时
        timeout=180,
        max_retries=2,
    )
    kwargs.update(overrides)
    return ChatOpenAI(**kwargs)


def knowledge_dir() -> Path:
    return DEMO_ROOT / "data" / "knowledge"


def models_dir() -> Path:
    return DEMO_ROOT / "models"
