"""stage5 评测入口：多种检索策略 x 多套题目的量化对比。

用法（离线、不花钱、不调模型）：
    python run_eval.py                 # 常用套题（15 hit 题）
    python run_eval.py --suite semantic # 同义改写套题（难，lexicon mismatch）
    python run_eval.py --suite all       # 两套一起跑

加生成评测（会调 LLM，20 题逐个请求，约 1~2 分钟）：
    python run_eval.py --with-llm --modes rerank

为什么要分"常用题"和"同义改写题"两套：
小语料上 BM25 会满分，看不出策略差异；同义改写套题才暴露字面检索的天花板。
只报一套数字的评测都是自我安慰。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# stage5 复用 stage3 的 chunker / embedder，必须先把 stage3 挂到 sys.path 上，
# 否则 import metrics -> index -> embedder 会 ModuleNotFoundError。
# 这一行必须在所有本地 import 之前执行。
STAGE3 = Path(__file__).resolve().parent.parent / "stage3"
if str(STAGE3) not in sys.path:
    sys.path.insert(0, str(STAGE3))

from eval_cases import (                                        # noqa: E402
    CASES,
    DISTRACTOR_CASES,
    EvalCase,
    SEMANTIC_CASES,
    hit_cases,
    judge_answer,
)
from metrics import RetrievalScore, score_rankings              # noqa: E402
from pipeline import MODES, RagPipeline                         # noqa: E402

TABLE_HEADER = (
    "| 检索策略 | 题数 | doc R@1 | doc R@3 | doc R@4 | chunk R@4 | doc MRR |\n"
    "| --- | --- | --- | --- | --- | --- | --- |"
)

SUITES = {
    "common": hit_cases,
    "semantic": lambda: list(SEMANTIC_CASES),
    "all": lambda: hit_cases() + list(SEMANTIC_CASES),
}


def gold_chunk_ids(chunks, case: EvalCase) -> set[str]:
    """哪些 chunk 算"正确"。注意：文件里所有 chunk 都算正确，
    因为我们标注的是**文件级** ground truth；chunk 级指标因此天然偏乐观。"""
    gold_docs = set(case.gold_docs)
    return {c.chunk_id for c in chunks if c.source in gold_docs}


def evaluate_retrieval(
    mode: str, cases: list[EvalCase]
) -> tuple[RetrievalScore, list[tuple[EvalCase, list[str]]]]:
    pipe = RagPipeline(mode)
    failures: list[tuple[EvalCase, list[str]]] = []
    rankings = []
    for case in cases:
        hits = pipe.retriever.retrieve(case.question)
        rankings.append(hits)
        top_docs = [h.doc_id for h in hits]
        if not (set(case.gold_docs) & set(top_docs)):
            failures.append((case, top_docs))
    golds = [gold_chunk_ids(pipe.retriever.chunks, case) for case in cases]
    return score_rankings(mode, cases, rankings, golds), failures


def evaluate_generation(mode: str, cases: list[EvalCase]) -> tuple[int, list[str]]:
    pipe = RagPipeline(mode)
    passed = 0
    lines: list[str] = []
    for case in cases:
        result = pipe.ask(case.question)
        ok, reason = judge_answer(case, result.answer)
        passed += int(ok)
        lines.append(
            f"{'PASS' if ok else 'FAIL'} {case.qid} [{case.kind}] {case.question}\n"
            f"     hits={[h.chunk_id for h in result.hits]}\n"
            f"     {reason} | {result.answer[:100]}"
        )
    return passed, lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modes", default="dense,sparse,hybrid,rerank")
    parser.add_argument("--suite", default="common", choices=sorted(SUITES))
    parser.add_argument("--with-llm", action="store_true")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    for mode in modes:
        if mode not in MODES:
            raise SystemExit(f"未知模式 {mode!r}，可选 {MODES}")

    cases = SUITES[args.suite]()
    report: list[str] = []
    print(f"套题={args.suite}  题数={len(cases)}（拒答题不参与检索指标）")
    print(f"语料 chunk 数={len(RagPipeline(modes[0]).retriever.chunks)}\n")
    print(TABLE_HEADER)
    report.append(f"套题={args.suite} 题数={len(cases)}")
    report.append(TABLE_HEADER)

    rows: dict[str, RetrievalScore] = {}
    failure_map: dict[str, list[tuple[EvalCase, list[str]]]] = {}
    for mode in modes:
        score, failures = evaluate_retrieval(mode, cases)
        rows[mode] = score
        failure_map[mode] = failures
        print(score.as_row())
        report.append(score.as_row())

    print("\n=== 未召回（Top-4 里没有正确文件）===")
    for mode in modes:
        failures = failure_map[mode]
        if not failures:
            print(f"[{mode}] 全部召回")
            report.append(f"- [{mode}] 无失败")
            continue
        print(f"[{mode}] {len(failures)} 题：")
        report.append(f"- [{mode}] 失败 {len(failures)} 题")
        for case, top_docs in failures:
            line = f"    {case.qid} {case.question} 期望={list(case.gold_docs)} 实际={top_docs}"
            print(line)
            report.append(line)

    if modes:
        best = max(modes, key=lambda m: (rows[m].doc_mrr, rows[m].doc_recall_1))
        print(f"\nMRR 最高：{best} ({rows[best].doc_mrr:.3f})")
        report.append(f"MRR 最高：{best} ({rows[best].doc_mrr:.3f})")

    if args.with_llm:
        gen_cases = cases + list(DISTRACTOR_CASES)
        print(f"\n=== 生成评测（调用 LLM，含 {len(DISTRACTOR_CASES)} 道干扰项）===")
        for mode in modes:
            passed, lines = evaluate_generation(mode, gen_cases)
            print(f"[{mode}] 答案通过 {passed}/{len(gen_cases)} ({passed / len(gen_cases):.0%})")
            report.append(f"\n### 生成评测 {mode}: {passed}/{len(gen_cases)}\n")
            report.extend(lines)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"\n报告已写入 {out}")


if __name__ == "__main__":
    main()
