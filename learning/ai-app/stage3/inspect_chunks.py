from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from chunker import load_corpus


def main() -> None:
    corpus = Path(__file__).resolve().parent / "corpus"
    for size, overlap in ((180, 40), (80, 20), (400, 40)):
        chunks = load_corpus(corpus, size=size, overlap=overlap)
        lengths = [len(c.text) for c in chunks]
        by_src = Counter(c.source for c in chunks)
        print(f"size={size} overlap={overlap} n={len(chunks)} avg_len={sum(lengths)/len(lengths):.0f}")
        print("  ", dict(by_src))
        longest = max(chunks, key=lambda c: len(c.text))
        print(f"  longest: {longest.source}/{longest.heading} len={len(longest.text)}")
        print()


if __name__ == "__main__":
    main()
