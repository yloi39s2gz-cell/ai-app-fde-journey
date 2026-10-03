"""消融实验：chunk 大小 x 检索策略。

面试官最爱追问的两句话，这里都能用数字回答：
1. "chunk 大小怎么选的？" -> 扫 150/300/500，看召回与 MRR 怎么变
2. "混合检索真的有用吗？" -> 同一张表里比较 dense / sparse / hybrid / rerank

用法：
    python ablation.py
    python ablation.py --sizes 150,300,500 --suite semantic
"""

from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from corpus import load_chunks                                  # noqa: E402
from embedder import build_embedder                             # noqa: E402
from eval_cases import hit_cases, SEMANTIC_CASES                # noqa: E402
from index import HybridIndex                                   # noqa: E402
from metrics import score_rankings                              # noqa: E402
from rerank import build_reranker                               # noqa: E402

HEADER = (
    "| chunk_size | 策略 | chunks | doc R@1 | doc R@3 | doc R@4 | chunk R@4 | doc MRR |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |"
)


def run(size: int, cases, overlap: int = 0) -> list[str]:
    chunks = load_chunks(size=size, overlap=overlap or max(1, size // 5))
    texts = [c.text for c in chunks]
    ids = [c.chunk_id for c in chunks]
    index = HybridIndex(texts, ids, build_embedder())

    strategies = {
        "dense": lambda q: index.dense_search(q, top_k=4),
        "sparse": lambda q: index.bm25_search(q, top_k=4),
        "hybrid": lambda q: index.hybrid_search(q, top_k=4, recall_k=12),
        "rerank": lambda q: index.reranked_search(q, top_k=4, recall_k=12, reranker=build_reranker().score),
    }
    rows = []
    for label, fn in strategies.items():
        rankings = [fn(case.question) for case in cases]
        golds = [{c.chunk_id for c in chunks if c.source in set(case.gold_docs)} for case in cases]
        score = score_rankings(label, cases, rankings, golds)
        rows.append(
            f"| {size} | {label} | {len(chunks)} | {score.doc_recall_1:.0%} | {score.doc_recall_3:.0%} "
            f"| {score.doc_recall_4:.0%} | {score.chunk_recall_4:.0%} | {score.doc_mrr:.3f} |"
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="150,300,500")
    parser.add_argument("--suite", default="common", choices=("common", "semantic"))
    args = parser.parse_args()

    cases = hit_cases() if args.suite == "common" else list(SEMANTIC_CASES)
    print(f"embedder={type(build_embedder()).__name__} reranker={type(build_reranker()).__name__} "
          f"suite={args.suite} 题数={len(cases)}\n")
    print(HEADER)
    for raw in args.sizes.split(","):
        raw = raw.strip()
        if not raw:
            continue
        for row in run(int(raw), cases):
            print(row)


if __name__ == "__main__":
    main()
