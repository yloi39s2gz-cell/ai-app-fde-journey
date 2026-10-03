from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rag import RagPipeline


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or "入职满两年每年有几天年假？"
    rag = RagPipeline()
    result = rag.ask(question)
    print("Q:", result.question)
    print()
    print("检索：")
    for hit in result.hits:
        preview = hit.chunk.text.replace("\n", " ")[:70]
        print(f"  [{hit.rank}] {hit.score:.3f} {hit.chunk.source} / {hit.chunk.heading} | {preview}")
    print()
    print("A:", result.answer)
    print()
    print(
        f"prompt_tokens={result.prompt_tokens} "
        f"completion_tokens={result.completion_tokens} "
        f"latency_ms={result.latency_ms}"
    )


if __name__ == "__main__":
    main()
