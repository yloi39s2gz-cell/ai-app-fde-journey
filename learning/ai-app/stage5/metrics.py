"""检索指标：纯函数、可单测、不依赖任何模型。

指标定义（面试要能口述）：
- Recall@k  : top-k 里包含 ground truth 的题目比例。关心"有没有漏"。
- MRR       : 每题第一个正确结果的排名倒数，再平均。关心"排得靠不靠前"。
              第 1 位=1.0，第 2 位=0.5，第 4 位=0.25，没召回=0。
- Doc-level : 同一文件被切成多块，任一块命中即该文件命中。业务上更接近真实需求。
- Chunk-level: 具体那一块。更严格，用来发现"文件对了但段落错了"。

两个都要报的原因：
只报 chunk 级会高估（文件里 5 块，随便中 1 块就算对）；
只报 doc 级会掩盖"召回了文件，但还是喂给模型错误的段落"。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from eval_cases import EvalCase
from index import RetrievalHit, doc_ranking


def recall_at_k(rankings: Sequence[Sequence[str]], golds: Sequence[set[str]], k: int) -> float:
    if not rankings:
        return 0.0
    hit = sum(1 for ranking, gold in zip(rankings, golds) if gold & set(ranking[:k]))
    return hit / len(rankings)


def mrr(rankings: Sequence[Sequence[str]], golds: Sequence[set[str]]) -> float:
    if not rankings:
        return 0.0
    total = 0.0
    for ranking, gold in zip(rankings, golds):
        for rank, item in enumerate(ranking, start=1):
            if item in gold:
                total += 1.0 / rank
                break
    return total / len(rankings)


@dataclass(frozen=True)
class RetrievalScore:
    label: str
    n_cases: int
    doc_recall_1: float
    doc_recall_3: float
    doc_recall_4: float
    chunk_recall_4: float
    doc_mrr: float

    def as_row(self) -> str:
        return (
            f"| {self.label} | {self.n_cases} | {self.doc_recall_1:.0%} | {self.doc_recall_3:.0%} "
            f"| {self.doc_recall_4:.0%} | {self.chunk_recall_4:.0%} | {self.doc_mrr:.3f} |"
        )


def score_rankings(
    label: str,
    cases: Sequence[EvalCase],
    rankings: Sequence[Sequence[RetrievalHit]],
    gold_chunk_ids: Sequence[set[str]],
) -> RetrievalScore:
    """只应传入 hit 类题目；拒答题没有 ground truth，必须排除。"""
    doc_lists = [doc_ranking(hits) for hits in rankings]
    chunk_lists = [[h.chunk_id for h in hits] for hits in rankings]
    gold_docs = [set(case.gold_docs) for case in cases]
    return RetrievalScore(
        label=label,
        n_cases=len(doc_lists),
        doc_recall_1=recall_at_k(doc_lists, gold_docs, 1),
        doc_recall_3=recall_at_k(doc_lists, gold_docs, 3),
        doc_recall_4=recall_at_k(doc_lists, gold_docs, 4),
        chunk_recall_4=recall_at_k(chunk_lists, [set(g) for g in gold_chunk_ids], 4),
        doc_mrr=mrr(doc_lists, gold_docs),
    )
