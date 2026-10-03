from __future__ import annotations

import hashlib
import math
import os
from typing import Protocol


def l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("向量维度不一致")
    return sum(x * y for x, y in zip(a, b))


class Embedder(Protocol):
    dim: int

    def embed(self, text: str) -> list[float]: ...

    def embed_many(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """字符 n-gram 哈希向量。不下载模型、不调 API，用来看清单词重合。

    它不是语义模型：「年假」和「带薪休假」几乎对不上。这是后面要换成真 embedding 的原因。
    """

    def __init__(self, dim: int = 256, ngrams: tuple[int, ...] = (2, 3)) -> None:
        self.dim = dim
        self.ngrams = ngrams

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        compact = "".join(text.split())
        if not compact:
            return vec
        for n in self.ngrams:
            if len(compact) < n:
                continue
            for i in range(len(compact) - n + 1):
                gram = compact[i : i + n]
                digest = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
                idx = int.from_bytes(digest, "little") % self.dim
                sign = 1.0 if digest[-1] % 2 == 0 else -1.0
                vec[idx] += sign
        return l2_normalize(vec)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class OpenAICompatibleEmbedder:
    def __init__(self) -> None:
        from openai import OpenAI

        api_key = os.getenv("EMBEDDING_API_KEY", "").strip()
        base_url = os.getenv("EMBEDDING_BASE_URL", "").strip()
        self.model = os.getenv("EMBEDDING_MODEL", "").strip()
        if not api_key or not base_url or not self.model:
            raise SystemExit("要用 API embedding，请配置 EMBEDDING_API_KEY / BASE_URL / MODEL")
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=30)
        self.dim = 0

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        vectors = [l2_normalize(list(item.embedding)) for item in resp.data]
        self.dim = len(vectors[0]) if vectors else 0
        return vectors

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]


def build_embedder() -> Embedder:
    if os.getenv("EMBEDDING_API_KEY", "").strip():
        return OpenAICompatibleEmbedder()
    return HashingEmbedder()
