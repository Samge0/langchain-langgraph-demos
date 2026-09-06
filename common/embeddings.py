"""common/embeddings.py —— 本地中文 embedding（bge-small-zh-v1.5）。

为什么不用 OPENAI embedding 接口？
- 本课程强调"可离线复现"：模型放在 demos/models/ 下，断网也能跑。
- bge 系列是中文 RAG 事实上的基线模型，面试常问：
  "你们用什么 embedding？"→ 能说出 bge / m3、维度、检索粒度即可。
"""
from __future__ import annotations

from functools import lru_cache

from common.config import models_dir

EMBED_MODEL_DIR = models_dir() / "bge-small-zh-v1.5"
EMBED_DIM = 512  # bge-small-zh-v1.5 输出维度


@lru_cache(maxsize=1)
def get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name=str(EMBED_MODEL_DIR),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},  # 余弦相似度必须归一化
    )
