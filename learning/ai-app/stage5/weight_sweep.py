"""权重消融：RRF 融合权重 + 重排基准权重。

这个脚本要回答一个"面试官会追问、而大多数人答不上来"的问题：

    "混合检索一定比单路好吗？"

答案是不一定。RRF 默认 1:1 融合，前提是两路检索**质量相当**。
如果一路明显更弱（本仓库里哈希稠密向量在同义改写题上只有 47%，
BM25 有 87%），1:1 融合会把强的那一路的排名拉下水：
弱路的 Top-1 拿到和强路 Top-1 相同的票，一条噪声就能压掉一条正确证据。

正确做法不是"因为我用了混合检索所以更好"，
而是**加权**——让弱的那路只贡献一部分票。下面就把权重扫出来。

用法：
    python weight_sweep.py                 # 同义改写套题（默认）
    python weight_sweep.py --suite common
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STAGE3 = Path(__file__).resolve().parent.parent / "stage3"
if str(STAGE3) not in sys.path:
    sys.path.insert(0, str(STAGE3))

from corpus import load_chunks, chunk_texts                    # noqa: E402
from embedder import build_embedder                            # noqa: E402
from eval_cases import hit_cases, SEMANTIC_CASES               # noqa: E402
from index import HybridIndex                                  # noqa: E402
from metrics import score_rankings                             # noqa: E402
from bm25_rerank import build_bm25_reranker                    # noqa: E402
from rerank import build_reranker                              # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="semantic", choices=("common", "semantic"))
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    cases = hit_cases() if args.suite == "common" else list(SEMANTIC_CASES)
    chunks = load_chunks(size=args.chunk_size, overlap=max(1, args.chunk_size // 5))
    texts, ids = chunk_texts(chunks)
    embedder = build_embedder()
    index = HybridIndex(texts, ids, embedder)
    reranker = build_bm25_reranker(texts)

    emit(f"embedder={type(embedder).__name__}  reranker={type(reranker).__name__}")
    emit(f"suite={args.suite}  题数={len(cases)}  chunk_size={args.chunk_size}  chunks={len(chunks)}")
    emit()

    golds = [{c.chunk_id for c in chunks if c.source in set(case.gold_docs)} for case in cases]

    def evaluate(label: str, fn) -> None:
        rankings = [fn(case.question) for case in cases]
        score = score_rankings(label, cases, rankings, golds)
        emit(
            f"{label:<28} R@1 {score.doc_recall_1:>4.0%}  R@3 {score.doc_recall_3:>4.0%}  "
            f"MRR {score.doc_mrr:.3f}"
        )

    emit("--- 单路基线 ---")
    evaluate("dense", lambda q: index.dense_search(q, top_k=4))
    evaluate("sparse (BM25)", lambda q: index.bm25_search(q, top_k=4))

    emit()
    emit("--- RRF 权重（w_sparse : w_dense）---")
    for w_sparse, w_dense in ((1.0, 1.0), (2.0, 1.0), (3.0, 1.0), (1.0, 0.5), (1.0, 0.25), (4.0, 1.0)):
        evaluate(
            f"hybrid {w_sparse:g}:{w_dense:g}",
            lambda q, a=w_sparse, b=w_dense: index.hybrid_search(
                q, top_k=4, recall_k=12, w_sparse=a, w_dense=b
            ),
        )

    emit()
    emit("--- 重排：候选集内重算 BM25（top-4 全重排）---")
    for base_weight in (0.0, 0.15, 0.3, 0.5, 0.7, 1.0):
        evaluate(
            f"rerank base={base_weight:g}",
            lambda q, w=base_weight: index.reranked_search(
                q, top_k=4, recall_k=12, base_weight=w, reranker=reranker.score
            ),
        )

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"报告已写入 {out}")


if __name__ == "__main__":
    main()
