from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from eval_set import CASES
from rag import RagPipeline


def judge(case, answer: str, hit_sources: list[str]) -> tuple[bool, str]:
    text = answer.strip()
    for needle in case.must_include:
        if needle not in text:
            return False, f"缺「{needle}」"
    for banned in case.must_not_include:
        if banned in text:
            return False, f"不该出现「{banned}」"
    if case.kind == "hit" and case.source_hint:
        if case.source_hint not in hit_sources:
            return False, f"召回未包含 {case.source_hint}"
    if case.kind == "refuse" and "资料未提及" not in text:
        return False, "拒答失败"
    return True, "ok"


def main() -> None:
    rag = RagPipeline()
    ok = 0
    print(f"embedder={type(rag.store.embedder).__name__} chunks={len(rag.store.chunks)}\n")
    for case in CASES:
        result = rag.ask(case.question)
        sources = [h.chunk.source for h in result.hits]
        passed, reason = judge(case, result.answer, sources)
        ok += int(passed)
        flag = "PASS" if passed else "FAIL"
        print(f"{flag} {case.qid} [{case.kind}] {case.question}")
        print(f"     hits={sources} prompt={result.prompt_tokens} completion={result.completion_tokens}")
        print(f"     {reason} | {result.answer[:120].replace(chr(10), ' ')}")
        print()
    total = len(CASES)
    print(f"score={ok}/{total} ({ok / total:.0%})  过关线 80%")
    if ok / total < 0.8:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
