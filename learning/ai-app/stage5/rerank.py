"""重排器（reranker）接口 + 一个可离线运行的教学实现。

真实生产用的是 cross-encoder：
    输入 (query, doc) 一对，模型直接输出相关度分数。
    慢但准 —— 只在候选集（10~50 条）上跑。
对比 bi-encoder（embedding）：
    先把 query 和 doc 各自压成向量，再算余弦。快，但 query 与 doc 从未"见面"。

实测差距通常体现在：query 说「带薪休假」，文档写「年假」。
- bi-encoder 靠语义空间拉近，能召回，但排序常不稳；
- cross-encoder 看到两个词的上下文，排序更准。

本文件提供两个实现：
1. HybridReranker —— 纯 Python 打分，无依赖、可离线跑，用
   「原分数 + 覆盖率加权」重排。教学用。
2. CrossEncoderReranker —— 真 cross-encoder（BGE-reranker-base 等）
   的接入点。装好 sentence-transformers 后把 RERANK_* 环境变量配上即可。
"""

from __future__ import annotations

import os
from typing import Protocol

from tokenizer import tokenize


class Reranker(Protocol):
    name: str

    def score(self, query: str, document: str) -> float: ...


class HybridReranker:
    """教学用：把「检索阶段的分数」和「词覆盖证据」混合起来。

    score = 0.3 * 归一化后的原始分数 + 0.7 * 覆盖率
    覆盖率 = |query token 与 doc token 的交集| / |query token|

    为什么这样能提升：原始分数由向量/BM25 产生，粒度粗；
    覆盖率直接回答"用户问的词，这段文本到底出现了几个"，
    对中文短问句特别有效。
    """

    name = "hybrid-coverage"

    def __init__(self, base_weight: float = 0.3) -> None:
        # base_weight 表示"给检索阶段原分数留多少话语权"，其余给词覆盖证据。
        # 0.3 是个保守起点：检索分数仍有影响，但覆盖证据能把它掀翻。
        self.base_weight = base_weight

    def coverage(self, query: str, document: str) -> float:
        q_tokens = set(tokenize(query))
        if not q_tokens:
            return 0.0
        d_tokens = set(tokenize(document))
        return len(q_tokens & d_tokens) / len(q_tokens)

    def score(self, query: str, document: str, base_score: float = 0.0) -> float:
        """供检索层直接调用：base_score 必须已归一化到 0~1。"""
        return self.blend(self.coverage(query, document), base_score)

    def blend(self, coverage: float, base_score: float) -> float:
        return (1 - self.base_weight) * coverage + self.base_weight * base_score


class CrossEncoderReranker:
    """真 cross-encoder 接入点。默认需要外部模型，未配置时构造会报错。

    用法：
        pip install sentence-transformers
        设置 RERANK_MODEL=BAAI/bge-reranker-base
        from rerank import CrossEncoderReranker
        rr = CrossEncoderReranker()
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
        try:
            from sentence_transformers import CrossEncoder  # type: ignore
        except ImportError as exc:  # pragma: no cover - 取决于本机环境
            raise SystemExit(
                "未安装 sentence-transformers，无法使用真 cross-encoder。\n"
                "  pip install sentence-transformers\n"
                "或改用 HybridReranker（无需依赖）。"
            ) from exc
        self.name = f"cross-encoder:{self.model_name}"
        self._model = CrossEncoder(self.model_name)

    def score(self, query: str, document: str) -> float:  # pragma: no cover
        return float(self._model.predict([(query, document)])[0])


def build_reranker() -> Reranker:
    """有 RERANK_MODEL 且装了依赖就用真模型，否则退回教学实现。"""
    if os.getenv("RERANK_MODEL", "").strip():
        return CrossEncoderReranker()  # type: ignore[return-value]
    return HybridReranker()  # type: ignore[return-value]
