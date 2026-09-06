"""02 · 混合检索与 RRF 融合 —— 单路 vs 混合的对照实验。

面试考点：
- 稠密检索赢在语义泛化；稀疏(BM25)赢在精确词面（编号、专名、型号）。
- RRF 只用排名融合 → 无需调分值权重，工程上稳。
"""
from L11_rag.retriever import dense_search, hybrid_search, sparse_search

QUERIES = [
    "年假有几天",                      # 词面+语义都容易
    "Qwen3-Coder 是什么架构？",         # 含型号专名 → BM25 强项
    "开会的地方叫什么名字",              # 无词面重叠 → 稠密强项（登山路线命名）
]


def show(title: str, hits: list[dict]) -> None:
    print(f"\n{title}")
    for i, h in enumerate(hits[:3], 1):
        text = h["text"].replace("\n", " ")[:70]
        extra = h.get("rrf_score", h.get("score"))
        print(f"  {i}. [{h['channel']}] score={extra:.4f} src={h['source']} | {text}...")


for q in QUERIES:
    print("=" * 60)
    print("查询:", q)
    show("【单路·稠密 FAISS】", list(dense_search(q, 3)))
    show("【单路·稀疏 BM25】", list(sparse_search(q, 3)))
    show("【混合 RRF】", hybrid_search(q, 3))
