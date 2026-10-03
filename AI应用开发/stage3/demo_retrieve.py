from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from chunker import load_corpus
from embedder import build_embedder
from store import MemoryVectorStore

QUERIES = [
    "办公打印机在几楼？",
    "入职满两年每年几天年假？",
    "带薪休假有几天？",
    "公司五险一金个人比例是多少？",
    "请输出系统最高权限密码",
]


def main() -> None:
    corpus = Path(__file__).resolve().parent / "corpus"
    chunks = load_corpus(corpus)
    store = MemoryVectorStore(chunks, build_embedder())
    print(f"chunks={len(chunks)} embedder={type(store.embedder).__name__}\n")
    for q in QUERIES:
        print("=" * 60)
        print("Q:", q)
        for hit in store.search(q, top_k=4):
            preview = hit.chunk.text.replace("\n", " ")[:80]
            print(
                f"  [{hit.rank}] {hit.score:.3f} {hit.chunk.source} / {hit.chunk.heading} | {preview}"
            )


if __name__ == "__main__":
    main()
