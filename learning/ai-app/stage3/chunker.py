from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    chunk_id: str
    source: str
    heading: str
    text: str
    start: int
    end: int


def _split_headings(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    current_heading = "文首"
    buf: list[str] = []
    for line in text.splitlines(keepends=True):
        if re.match(r"^#{1,3} ", line):
            body = "".join(buf).strip()
            if body:
                parts.append((current_heading, body))
            current_heading = line.lstrip("#").strip()
            buf = []
        else:
            buf.append(line)
    body = "".join(buf).strip()
    if body:
        parts.append((current_heading, body))
    return parts or [("文首", text.strip())]


def chunk_text(
    text: str,
    *,
    source: str,
    size: int = 180,
    overlap: int = 40,
) -> list[Chunk]:
    if overlap >= size:
        raise ValueError("overlap 必须小于 size，否则窗口不会前进")
    chunks: list[Chunk] = []
    seq = 0
    for heading, body in _split_headings(text):
        if len(body) <= size:
            chunks.append(
                Chunk(
                    chunk_id=f"{source}#{seq}",
                    source=source,
                    heading=heading,
                    text=body,
                    start=0,
                    end=len(body),
                )
            )
            seq += 1
            continue
        start = 0
        while start < len(body):
            end = min(start + size, len(body))
            piece = body[start:end].strip()
            if piece:
                chunks.append(
                    Chunk(
                        chunk_id=f"{source}#{seq}",
                        source=source,
                        heading=heading,
                        text=piece,
                        start=start,
                        end=end,
                    )
                )
                seq += 1
            if end >= len(body):
                break
            start = end - overlap
    return chunks


def load_corpus(corpus_dir: Path, *, size: int = 180, overlap: int = 40) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(corpus_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(chunk_text(text, source=path.name, size=size, overlap=overlap))
    return chunks
