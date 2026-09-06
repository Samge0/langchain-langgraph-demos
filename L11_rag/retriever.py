"""共享检索模块：索引构建 + 稠疏混合检索 + RRF 融合。

被 01/02/03 三个 demo 复用；对应 source 课程 rag/05-07 + Milvus 混合检索的本地化等价实现。
"""
from __future__ import annotations

import json
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

from common.config import DEMO_ROOT, knowledge_dir
from common.embeddings import get_embeddings

STORE_DIR = DEMO_ROOT / "data" / "vector_store"
RANK_K = 60  # RRF 常数，论文经验值


# ---------------- 索引阶段 ----------------

def load_documents() -> list[dict]:
    """加载 data/knowledge 下全部 Markdown。生产换 pypdf/docx loader。"""
    docs = []
    for md in sorted(knowledge_dir().glob("*.md")):
        docs.append({"text": md.read_text(encoding="utf-8"), "source": md.name})
    return docs


def split_documents(docs: list[dict], chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """结构感知切分：先按标题分节，节内再用字符递归切。"""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", "，"],
    )
    chunks = []
    for d in docs:
        for piece in splitter.split_text(d["text"]):
            chunks.append({"text": piece, "source": d["source"]})
    return chunks


def build_index() -> dict:
    """切分 → 嵌入 → FAISS(L2) + BM25 双通道落盘。"""
    from langchain_community.vectorstores import FAISS

    chunks = split_documents(load_documents())
    print(f"切分得到 {len(chunks)} 个 chunk")

    embeddings = get_embeddings()
    texts = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_id": i} for i, c in enumerate(chunks)]

    vs = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    vs.save_local(str(STORE_DIR))

    # BM25 语料与分词一并持久化
    tokenized = [list(jieba.cut_for_search(t)) for t in texts]
    bm25 = BM25Okapi(tokenized)
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    (STORE_DIR / "bm25_corpus.json").write_text(
        json.dumps({"texts": texts, "metadatas": metadatas}, ensure_ascii=False), encoding="utf-8")

    print(f"索引完成：FAISS → {STORE_DIR/'index.faiss'}，BM25 语料 {len(texts)} 条")
    return {"chunks": chunks, "faiss": vs, "bm25": bm25}


# ---------------- 检索阶段 ----------------

def _load_bm25() -> tuple[BM25Okapi, list[str], list[dict]]:
    data = json.loads((STORE_DIR / "bm25_corpus.json").read_text(encoding="utf-8"))
    tokenized = [list(jieba.cut_for_search(t)) for t in data["texts"]]
    return BM25Okapi(tokenized), data["texts"], data["metadatas"]


def dense_search(query: str, top_k: int = 5) -> list[dict]:
    from langchain_community.vectorstores import FAISS

    vs = FAISS.load_local(str(STORE_DIR), get_embeddings(), allow_dangerous_deserialization=True)
    for doc, score in vs.similarity_search_with_score(query, k=top_k):
        yield {"text": doc.page_content, **doc.metadata, "score": float(score), "channel": "dense"}


def sparse_search(query: str, top_k: int = 5) -> list[dict]:
    bm25, texts, metas = _load_bm25()
    scores = bm25.get_scores(list(jieba.cut_for_search(query)))
    ranked = sorted(zip(scores, texts, metas), key=lambda x: -x[0])[:top_k]
    for score, text, meta in ranked:
        yield {"text": text, **meta, "score": float(score), "channel": "sparse"}


def rrf_fuse(result_lists: list[list[dict]], top_k: int = 5) -> list[dict]:
    """Reciprocal Rank Fusion：score = Σ 1/(k + rank)。只用名次，天然规避量纲差异。"""
    pool: dict[int, dict] = {}     # chunk_id → item
    fused: dict[int, float] = {}
    for results in result_lists:
        for rank, item in enumerate(results):
            cid = item["chunk_id"]
            pool.setdefault(cid, {**item, "channels": []})
            pool[cid]["channels"].append(item["channel"])
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (RANK_K + rank + 1)
    ordered = sorted(fused.items(), key=lambda kv: -kv[1])[:top_k]
    return [{**pool[cid], "rrf_score": score} for cid, score in ordered]


def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    """稠密 + 稀疏 双路召回 → RRF 融合（生产标准形态）。"""
    dense = list(dense_search(query, top_k * 2))
    sparse = list(sparse_search(query, top_k * 2))
    return rrf_fuse([dense, sparse], top_k)


def format_context(hits: list[dict]) -> str:
    """把命中块格式化成带引用编号的上下文。"""
    parts = []
    for i, h in enumerate(hits, 1):
        parts.append(f"[{i}] (来源: {h['source']} / 通道:{'+'.join(h['channels'])})\n{h['text']}")
    return "\n\n".join(parts)
