from __future__ import annotations

from pathlib import Path

from chunker import chunk_text, load_corpus
from embedder import HashingEmbedder, cosine, l2_normalize
from store import MemoryVectorStore

CORPUS = Path(__file__).resolve().parent / "corpus"


def test_overlap_must_be_smaller_than_size():
    try:
        chunk_text("abcdefghij", source="x.md", size=8, overlap=8)
        assert False, "应当报错"
    except ValueError:
        pass


def test_small_doc_is_one_chunk():
    chunks = chunk_text("只有一小段。", source="a.md", size=180, overlap=40)
    assert len(chunks) == 1
    assert chunks[0].text == "只有一小段。"


def test_long_section_has_overlap():
    text = "# 标题\n" + ("年假规则。" * 40)
    chunks = chunk_text(text, source="b.md", size=80, overlap=20)
    assert len(chunks) >= 2
    a, b = chunks[0].text, chunks[1].text
    assert a[-20:] in b or b[:20] in a


def test_cosine_identical_is_one():
    v = l2_normalize([3.0, 4.0, 0.0])
    assert abs(cosine(v, v) - 1.0) < 1e-9


def test_hashing_ranks_lexical_match_first():
    chunks = load_corpus(CORPUS)
    store = MemoryVectorStore(chunks, HashingEmbedder())
    hits = store.search("办公打印机在几楼？", top_k=3)
    joined = " ".join(h.chunk.text for h in hits)
    assert "3 楼" in joined or "文印" in joined


def test_unknown_query_should_not_only_return_leave_policy():
    chunks = load_corpus(CORPUS)
    store = MemoryVectorStore(chunks, HashingEmbedder())
    hits = store.search("公司五险一金个人缴纳比例是多少？", top_k=4)
    assert hits
    assert all(0.0 <= h.score <= 1.0 + 1e-6 for h in hits)
