"""混合检索索引：稀疏（BM25）+ 稠密（embedding）+ RRF 融合 + 重排。

这是本阶段的核心产物，也是简历/面试里最有说服力的一段话的载体：

    "单哈希向量 Top-1 命中 X%，换成 BM25 后 Y%，RRF 混合后 Z%，
     加重排后 W%，同一套 20 题 eval 测出来的。"

关键概念：

1) 稀疏 vs 稠密
   - 稀疏（BM25）：靠"词是否出现"。专有名词、编号、密码这类
     字面量强的 query 很准；换一种说法就崩（"带薪休假" vs "年假"）。
   - 稠密（embedding）：靠语义距离。换说法能召回；但会漏掉
     精确字面量（A3、Welcome@2026），且排序粒度粗。

2) RRF（Reciprocal Rank Fusion）
       fused(d) = Σ_r  w_r / (k + rank_r(d))
   只吃排名不吃分数 —— 因为 BM25 分数和余弦相似度**量纲完全不同**，
   直接加权相加是错的（这是新人最常犯的错）。RRF 天然免疫量纲问题，
   是工业界默认的融合手段，k 一般取 60。

3) 两阶段检索（recall-then-rerank）
   召回阶段要"宽"（top_k 大，宁滥勿缺），重排阶段要"准"。
   常见坑：只召回 4 条然后重排 4 条 —— 重排没有可动空间，
   提升必然接近 0。所以 recall_k=12、rerank 后取 4。

4) 为什么还要 document 级指标
   chunk 级命中会骗人：一段话被切成 3 块，只要 1 块进 Top-4 就算命中。
   真实业务关心"文件对不对"，所以同时统计文档级 Recall@k 与 MRR。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from bm25 import BM25
from embedder import Embedder, l2_normalize, cosine


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    text: str
    score: float
    rank: int
    stage: str = "dense"

    @property
    def doc_id(self) -> str:
        """chunk_id 形如 '请假制度.md#3'，取文件名字段。"""
        return self.chunk_id.split("#", 1)[0]


class HybridIndex:
    """把 BM25 与稠密向量索引封装在同一份 chunk 列表上。"""

    def __init__(self, chunks: list[str], chunk_ids: list[str], embedder: Embedder) -> None:
        if len(chunks) != len(chunk_ids):
            raise ValueError("chunks 与 chunk_ids 长度必须一致")
        self.chunks = list(chunks)
        self.chunk_ids = list(chunk_ids)
        self.embedder = embedder
        self.bm25 = BM25(k1=1.5, b=0.75).fit(self.chunks)
        self._doc_vectors = [l2_normalize(embedder.embed(c)) for c in self.chunks]

    # ---------- 稀疏 ----------
    def bm25_search(self, query: str, top_k: int = 10) -> list[RetrievalHit]:
        ranked = self.bm25.ranking(query)[:top_k]
        return [
            RetrievalHit(self.chunk_ids[i], self.chunks[i], score, rank, "sparse")
            for rank, (i, score) in enumerate(ranked, start=1)
        ]

    # ---------- 稠密 ----------
    def dense_search(self, query: str, top_k: int = 10) -> list[RetrievalHit]:
        qv = l2_normalize(self.embedder.embed(query))
        scored = [(i, cosine(qv, dv)) for i, dv in enumerate(self._doc_vectors)]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return [
            RetrievalHit(self.chunk_ids[i], self.chunks[i], score, rank, "dense")
            for rank, (i, score) in enumerate(scored[:top_k], start=1)
        ]

    # ---------- 融合 ----------
    def hybrid_search(
        self,
        query: str,
        top_k: int = 4,
        recall_k: int = 12,
        k_rrf: int = 60,
        w_sparse: float = 1.0,
        w_dense: float = 1.0,
    ) -> list[RetrievalHit]:
        sparse = self.bm25_search(query, top_k=recall_k)
        dense = self.dense_search(query, top_k=recall_k)

        fused: dict[str, float] = {}
        payload: dict[str, RetrievalHit] = {}
        for weight, hits in ((w_sparse, sparse), (w_dense, dense)):
            for hit in hits:
                fused[hit.chunk_id] = fused.get(hit.chunk_id, 0.0) + weight / (k_rrf + hit.rank)
                payload.setdefault(hit.chunk_id, hit)

        ordered = sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))[:top_k]
        return [
            RetrievalHit(cid, payload[cid].text, score, rank, "hybrid")
            for rank, (cid, score) in enumerate(ordered, start=1)
        ]

    # ---------- 重排 ----------
    def reranked_search(
        self,
        query: str,
        top_k: int = 4,
        recall_k: int = 12,
        reranker: Callable[[str, str, float], float] | None = None,
        base_weight: float = 0.3,
        w_sparse: float = 1.0,
        w_dense: float = 1.0,
    ) -> list[RetrievalHit]:
        candidates = self.hybrid_search(
            query, top_k=recall_k, recall_k=recall_k, w_sparse=w_sparse, w_dense=w_dense
        )
        if reranker is None:
            from rerank import HybridReranker

            reranker = HybridReranker(base_weight=base_weight).score
        # 归一化：RRF 原始分数是 ~1/61 量级，而覆盖率是 0~1。
        # 不归一化的话 base_score 项几乎不起作用，混合权重就成了摆设 ——
        # 这是实际工程里非常容易埋下的静默 bug，所以单独写一行注释标出来。
        # 协议：reranker(query, document, base_score)
        #   - query 永远是用户原始问题（写成 hit.text 就变成"自己和自己比对覆盖率"，恒等于 1，
        #     重排会静默失效 —— 这个 bug 我在这里踩过一次，注释留下）
        #   - base_score 已归一化到 0~1，由 reranker 决定与"词覆盖证据"如何加权
        # 归一化是必须的：RRF 原始分数是 ~1/61 量级，而覆盖率是 0~1；
        # 不归一化的话 base_score 项几乎不起作用，混合权重就成了摆设。
        top_score = candidates[0].score if candidates else 1.0
        rescored = sorted(
            (
                (reranker(query, hit.text, hit.score / (top_score or 1.0)), hit)
                for hit in candidates
            ),
            key=lambda pair: (-pair[0], pair[1].chunk_id),
        )
        return [
            RetrievalHit(hit.chunk_id, hit.text, score, rank, "rerank")
            for rank, (score, hit) in enumerate(rescored[:top_k], start=1)
        ]


def doc_ranking(hits: Sequence[RetrievalHit]) -> list[str]:
    """把 chunk 排名压成文档排名（同一文档只保留最靠前的一次）。"""
    seen: list[str] = []
    for hit in hits:
        if hit.doc_id not in seen:
            seen.append(hit.doc_id)
    return seen
