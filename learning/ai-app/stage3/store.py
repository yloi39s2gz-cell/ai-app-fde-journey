from __future__ import annotations

from dataclasses import dataclass

from chunker import Chunk
from embedder import Embedder, cosine


@dataclass
class Hit:
    chunk: Chunk
    score: float
    rank: int


class MemoryVectorStore:
    def __init__(self, chunks: list[Chunk], embedder: Embedder) -> None:
        self.chunks = chunks
        self.embedder = embedder
        self.vectors = embedder.embed_many([c.text for c in chunks])

    def search(self, query: str, top_k: int = 4) -> list[Hit]:
        q = self.embedder.embed(query)
        scored = [(cosine(q, v), i) for i, v in enumerate(self.vectors)]
        scored.sort(key=lambda x: x[0], reverse=True)
        hits: list[Hit] = []
        for rank, (score, idx) in enumerate(scored[:top_k], start=1):
            hits.append(Hit(chunk=self.chunks[idx], score=score, rank=rank))
        return hits
