"""BM25（Okapi BM25）—— 稀疏检索的行业标准，自己写一遍。

公式（面试要能写出来）：

    score(q, d) = Σ_t IDF(t) * [ f(t,d) * (k1 + 1) ]
                              / [ f(t,d) + k1 * (1 - b + b * |d| / avgdl) ]

    IDF(t) = ln( 1 + (N - n(t) + 0.5) / (n(t) + 0.5) )

其中：
- f(t,d)  = 词 t 在文档 d 里的出现次数（tf）
- |d|     = 文档长度（token 数），avgdl = 全部文档平均长度
- N       = 文档总数，n(t) = 含 t 的文档数
- k1      = 词频饱和系数（1.2~2.0）。tf 很大时收益递减，k1 控制饱和速度
- b       = 长度归一化强度（0~1，通常 0.75）。b=1 完全按长度惩罚，b=0 不惩罚

关键直觉：
- 长文档天然容易撞上更多词，所以要按长度惩罚 -> b
- 一个词出现 10 次不等于相关度是出现 1 次的 10 倍 -> k1 让 tf 饱和
- 越罕见的词信息量越大 -> IDF
"""

from __future__ import annotations

import math
from collections import Counter

from tokenizer import tokenize


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.doc_tokens: list[list[str]] = []
        self.doc_freqs: list[Counter[str]] = []
        self.df: Counter[str] = Counter()
        self.avgdl: float = 0.0
        self._idf_cache: dict[str, float] = {}

    def fit(self, documents: list[str]) -> "BM25":
        self.doc_tokens = [tokenize(doc) for doc in documents]
        self.doc_freqs = [Counter(tokens) for tokens in self.doc_tokens]
        self.df = Counter()
        for freqs in self.doc_freqs:
            self.df.update(freqs.keys())
        self.avgdl = (
            sum(len(tokens) for tokens in self.doc_tokens) / len(self.doc_tokens)
            if self.doc_tokens
            else 0.0
        )
        self._idf_cache.clear()
        return self

    @property
    def n_docs(self) -> int:
        return len(self.doc_tokens)

    def idf(self, term: str) -> float:
        if term in self._idf_cache:
            return self._idf_cache[term]
        n = self.df.get(term, 0)
        value = math.log(1 + (self.n_docs - n + 0.5) / (n + 0.5))
        self._idf_cache[term] = value
        return value

    def score(self, query: str, doc_index: int) -> float:
        freqs = self.doc_freqs[doc_index]
        length = len(self.doc_tokens[doc_index]) or 1
        norm = self.k1 * (1 - self.b + self.b * length / (self.avgdl or 1))
        total = 0.0
        for term in tokenize(query):
            tf = freqs.get(term, 0)
            if not tf:
                continue
            total += self.idf(term) * tf * (self.k1 + 1) / (tf + norm)
        return total

    def ranking(self, query: str) -> list[tuple[int, float]]:
        """返回按分数降序的 (doc_index, score)。分数为 0 的文档直接丢掉。"""
        scored = [(i, self.score(query, i)) for i in range(self.n_docs)]
        scored = [pair for pair in scored if pair[1] > 0]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored
