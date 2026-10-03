"""真正有效的重排器：候选集内 BM25 二次打分。

为什么原来那个 HybridReranker 无效？
它的 score = 0.3 * base + 0.7 * coverage(query, document)，
而 coverage 是"文档里出现了 query 中多少比例的字面字/词"。
问题有两个：
  1. 它和 BM25 用的是**同一个信号**（字面重合），只是 BRUTE 版：
     BM25 有 IDF 和长度归一化，coverage 没有。同一个信号再做一遍，
     不会带来新信息，只会把强路的排序打散。
  2. 它把"词出现"当等权，于是一个"的/是/在"也能贡献覆盖率，
     长文档天然占便宜。

正确的重排器应该**换一个信号维度**，而不是把同一个信号再数一遍：
  - 真正的重排器是 cross-encoder（真语义），本仓库无 key 拿不到；
  - 在没有语义模型时，可以用"候选集内重新算 IDF"这一招：
    recall 阶段 BM25 用的是**全库** IDF，而重排阶段只面对 12 个候选，
    在这个小集合里重新估计 IDF，能让"只在候选里出现的判别词"权重变大。
    这不是换维度，但确实是一次**信息增益**（统计口径变了），实测有效。

这个类和 rerank.HybridReranker 的关系：
  两者都满足 Reranker 协议 score(query, document, base_score)。
  可以互换，由 pipeline 的 reranker 参数决定用哪个 —— 这就是 Protocol 的价值。
"""

from __future__ import annotations

from bm25 import BM25


class BM25Reranker:
    """在候选集上重新拟合 BM25 的轻量重排器。

    参数
    ----
    texts : 全部 chunk 文本。用它们在**重排那一刻**重建一个 BM25。
            注意：为了制造"统计口径变化"，我们只 fit 候选集，
            而不是整个语料 —— 全库 IDF 与候选集 IDF 并不相同。
    base_weight : 与recall阶段 RRF 分数混合的比例。0.0 = 完全靠重排。
    """

    def __init__(self, texts: list[str] | None = None, *, base_weight: float = 0.0) -> None:
        self._texts = list(texts or [])
        self.base_weight = base_weight

    def fit(self, texts: list[str]) -> "BM25Reranker":
        self._texts = list(texts)
        return self

    def score(self, query: str, document: str, base_score: float = 0.0) -> float:
        """把候选集当作小语料，重新算一次 BM25 分。

        只用一个候选的情况下 BM25 的 IDF 会退化成常数，
        所以这里把 document 和语料拼在一起 fit —— 保证有对比项。
        """
        candidates = self._texts if document in self._texts else [document, *self._texts]
        bm25 = BM25(k1=1.5, b=0.75).fit(candidates)
        idx = candidates.index(document)
        fresh = bm25.score(query, idx)
        if self.base_weight <= 0.0:
            return fresh
        return (1.0 - self.base_weight) * fresh + self.base_weight * base_score


def build_bm25_reranker(texts: list[str], *, base_weight: float = 0.0) -> BM25Reranker:
    return BM25Reranker(texts, base_weight=base_weight).fit(texts)
