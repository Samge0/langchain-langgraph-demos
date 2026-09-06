# L11 · 生产级 RAG 全流程

## 运行
```bash
.venv/Scripts/python.exe -m L11_rag.01_index_build            # 离线索引（切分→嵌入→FAISS+BM25）
.venv/Scripts/python.exe -m L11_rag.02_hybrid_retrieval       # 混合检索 + RRF 融合（可独立跑）
.venv/Scripts/python.exe -m L11_rag.03_rag_agent              # 引用溯源问答（需先跑 01）
```

## 面试考点

### 1. 索引阶段（对应课件《RAG优化分享》）
- 切分原则：**保持语义完整性**。RecursiveCharacterTextSplitter 按 `\n\n → \n → 。`
  递归降级切分；chunk_size/overlap 是精度-成本旋钮（本例 300/50）。
- 进阶策略（说出即加分）：父子块（小块检索回大块内容）、按文档结构切 Markdown 标题、
  语义切分（embedding 相邻句突变点）、LLM 摘要入索引。

### 2. 混合检索（本课核心实现）
| 通道 | 实现 | 强项 |
|---|---|---|
| 稠密 | bge-small-zh + FAISS (L2) | 语义泛化（同义改写） |
| 稀疏 | jieba 分词 + BM25 | 精确关键词/编号/专名 |

- **RRF 融合**：`score = Σ 1/(k + rank_i)`，k=60。只用排名不用分值 → 天然规避两路分数量纲差异。
- 与 Milvus 混合检索的概念映射：`vector 字段≈FAISS 稠密`、`sparse_vector 字段≈BM25 稀疏`、
  `RRFRanker≈本课 rrf_fuse()`。概念等价，实现去 Docker 化。

### 3. 生成阶段
- 引用溯源：答案附带 `[1][2]` 编号 + 来源清单 —— 生产 RAG 的合规刚需。
- 拒答：检索分数过低/上下文无答案时明确说不知道（防幻觉的正确姿势是"检索质量+拒答"，不是提示词硬憋）。

### 4. 评测（面试区分度最高）
- 建黄金问答集（问题→应命中片段），跑 Recall@k / MRR；
- 上线标准示例：Recall@5 ≥ 0.85；检索不到≠失败，正确拒答也算通过。

### 5. RAG 优化军火库（课件总结，面试清单题）
查询侧：改写/拆解/HyE 补充/多路召回；索引侧：父子块/结构化切分/摘要索引；
检索侧：混合+RRF+重排序（bge-reranker/LLM rerank）；生成侧：引用+拒答+压缩。
