"""stage5 的语料加载：复用 stage3 的 chunker 与 corpus 目录。

刻意与 stage3 用不同的切块参数（size=300/overlap=60）：
- stage3 用 180/40，块更碎，关键词容易被切散；
- 块越大，单块的"信息密度"越低，稠密向量越容易糊在一起；
所以在两套参数上都该测一遍 —— 这就是 chunk 大小消融实验（ablation）。

面试常见追问："你 chunk 大小怎么定的？" 正确答法是：
"我把它当超参，用同一套 eval 扫了 180/300/500，看召回率与答案正确率。"
"""

from __future__ import annotations

import sys
from pathlib import Path

STAGE3 = Path(__file__).resolve().parent.parent / "stage3"
sys.path.insert(0, str(STAGE3))

from chunker import Chunk, load_corpus  # noqa: E402

CORPUS_DIR = STAGE3 / "corpus"


def load_chunks(size: int = 300, overlap: int = 60) -> list[Chunk]:
    return load_corpus(CORPUS_DIR, size=size, overlap=overlap)


def chunk_texts(chunks: list[Chunk]) -> tuple[list[str], list[str]]:
    return [c.text for c in chunks], [c.chunk_id for c in chunks]
