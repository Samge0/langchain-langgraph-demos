"""01 · 离线索引：加载 → 切分 → 嵌入 → FAISS + BM25 双通道落盘。"""
from L11_rag.retriever import build_index

if __name__ == "__main__":
    build_index()
