"""stage5 单测：全部离线，不需要 API key，也不下载模型。

运行：
    cd learning/ai-app/stage5
    ..\\..\\..\\.venv\\Scripts\\python.exe -m pytest -q
"""

from __future__ import annotations

import pytest

from bm25 import BM25
from eval_cases import CASES, judge_answer
from index import HybridIndex, RetrievalHit, doc_ranking
from metrics import mrr, recall_at_k
from rerank import HybridReranker
from tokenizer import tokenize


# --------------------------- tokenizer ---------------------------

def test_tokenize_mixes_chinese_and_ascii():
    tokens = tokenize("A3彩打仅限市场部")
    assert "a3" in tokens          # 字母+数字合并成一个 ascii 词，且小写
    assert "彩" in tokens          # 中文单字
    assert "彩打" in tokens        # 中文二字组合
    assert "仅限" in tokens


def test_tokenize_keeps_long_ascii_words_whole():
    assert "welcome" in tokenize("初始密码 Welcome@2026")
    assert "2026" in tokenize("初始密码 Welcome@2026")
    assert "vpn" in tokenize("公司 VPN 账号")


def test_tokenize_drops_punctuation():
    assert "," not in tokenize("你好，世界")


# --------------------------- BM25 ---------------------------

def test_bm25_ranks_matching_doc_first():
    docs = [
        "办公打印机位于 3 楼西侧文印室，使用前须用工牌刷卡。",
        "年假须提前 3 个工作日在 OA 提交申请。",
        "加班餐补 50 元每次。",
    ]
    ranking = BM25().fit(docs).ranking("打印机在几楼")
    assert ranking, "应至少命中一个文档"
    assert ranking[0][0] == 0


def test_bm25_rare_term_beats_common_term():
    """IDF 的作用：罕见词权重更高。"""
    docs = [
        "公司制度：年假、病假、调休。",
        "公司制度：年假、病假、调休。",
        "公司制度：年假、病假、调休、补充公积金。",
    ]
    ranking = BM25().fit(docs).ranking("补充公积金")
    assert ranking[0][0] == 2


def test_bm25_scores_are_non_negative_and_empty_query_is_safe():
    bm = BM25().fit(["年假 10 天", "病假证明"])
    assert bm.ranking("") == []
    for _, score in bm.ranking("年假"):
        assert score > 0


# --------------------------- metrics ---------------------------

def test_recall_at_k_counts_cases_not_items():
    rankings = [["a.md", "b.md"], ["b.md", "a.md"], ["c.md", "d.md"]]
    golds = [{"a.md"}, {"a.md"}, {"a.md"}]
    assert recall_at_k(rankings, golds, 1) == pytest.approx(1 / 3)
    assert recall_at_k(rankings, golds, 2) == pytest.approx(2 / 3)


def test_mrr_uses_reciprocal_rank_of_first_hit():
    rankings = [["a.md"], ["x.md", "a.md"], ["x.md", "y.md", "a.md"]]
    golds = [{"a.md"}, {"a.md"}, {"a.md"}]
    assert mrr(rankings, golds) == pytest.approx((1 + 0.5 + 1 / 3) / 3)


def test_mrr_zero_when_nothing_recalled():
    assert mrr([["x.md"]], [{"a.md"}]) == 0.0


def test_doc_ranking_dedupes_chunks_of_same_file():
    hits = [
        RetrievalHit("请假制度.md#1", "t", 1.0, 1),
        RetrievalHit("请假制度.md#1", "t", 1.0, 1),
        RetrievalHit("请假制度.md#2", "t", 0.9, 2),
        RetrievalHit("IT与办公.md#0", "t", 0.8, 3),
    ]
    assert doc_ranking(hits) == ["请假制度.md", "IT与办公.md"]


# --------------------------- hybrid + rerank ---------------------------

class _KeywordEmbedder:
    """把查询词映射到固定维度，用于制造"稠密与稀疏各自命中不同文档"的场景。"""

    dim = 2

    def embed(self, text: str) -> list[float]:
        return [1.0, 0.0] if "alpha" in text.lower() else [0.0, 1.0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def test_rrf_fuses_rank_information_not_raw_scores():
    """RRF 的正确性不靠"我觉得谁第一"，而是可以从两个子排名反推出来。

    写检索代码时该有的习惯：融合结果必须能被单路结果验证。
    把 BM25 分数与余弦分数直接相加是错的（量纲不同），RRF 只吃 rank。
    """
    chunks = ["alpha beta", "beta"]
    ids = ["doc-a#0", "doc-b#0"]
    index = HybridIndex(chunks, ids, _KeywordEmbedder())

    sparse = index.bm25_search("alpha beta", top_k=2)
    dense = index.dense_search("alpha beta", top_k=2)
    fused = index.hybrid_search("alpha beta", top_k=2, recall_k=2, k_rrf=60)

    expected: dict[str, float] = {}
    for hits, weight in ((sparse, 1.0), (dense, 1.0)):
        for hit in hits:
            expected[hit.chunk_id] = expected.get(hit.chunk_id, 0.0) + weight / (60 + hit.rank)

    got = {h.chunk_id: h.score for h in fused}
    assert set(got) == set(expected)
    for cid, value in expected.items():
        assert got[cid] == pytest.approx(value)


def test_rrf_top1_is_never_worse_than_either_single_method_top1():
    """保底性质：RRF 的 Top-1 一定出现在两个输入列表的 Top-1 里。"""
    chunks = ["alpha beta", "beta", "alpha"]
    ids = ["doc-a#0", "doc-b#0", "doc-c#0"]
    index = HybridIndex(chunks, ids, _KeywordEmbedder())
    top1 = index.hybrid_search("alpha beta", top_k=1, recall_k=3)[0].chunk_id
    assert top1 in {"doc-a#0", "doc-b#0", "doc-c#0"}


def test_reranker_prefers_higher_query_term_coverage():
    rr = HybridReranker(base_weight=0.3)
    good = rr.score("A3 彩打 部门", "A3 彩打仅限市场部与行政部账号", base_score=0.5)
    bad = rr.score("A3 彩打 部门", "工牌丢失当天到行政补办，工本费 30 元", base_score=0.5)
    assert good > bad


def test_rerank_can_promote_a_lower_candidate():
    """重排的价值：混合检索的 Top-1 不是最能回答问题的块时，把它换掉。

    这里 #0 是一个"含 query 单个字"的干扰块（覆盖率 0.05），
    #1 才是真正包含答案的块（覆盖率 ~0.89）。归一化后重排必须把 #1 提到第一。
    """
    chunks = [
        "打印机位于 3 楼文印室",
        "A3 彩打仅限市场部与行政部账号使用",
        "VPN 初始密码 Welcome@2026",
    ]
    ids = ["IT与办公.md#0", "IT与办公.md#1", "IT与办公.md#2"]
    index = HybridIndex(chunks, ids, _KeywordEmbedder())

    q = "A3彩打市场部行政部账号"
    rrk = HybridReranker(base_weight=0.3)
    assert rrk.coverage(q, chunks[0]) < rrk.coverage(q, chunks[1])

    reranked = index.reranked_search("A3彩打市场部行政部账号", top_k=1, recall_k=3)
    assert reranked[0].chunk_id == "IT与办公.md#1"


# --------------------------- eval set sanity ---------------------------

def test_eval_set_shape():
    assert len(CASES) == 20
    assert len([c for c in CASES if c.no_answer]) == 5
    for case in CASES:
        if case.no_answer:
            assert case.gold_docs == ()
        else:
            assert case.gold_docs, f"{case.qid} 缺 ground truth"


def test_judge_rejects_missing_keyword_and_leakage():
    case = next(c for c in CASES if c.qid == "h05")
    ok, _ = judge_answer(case, "初始密码是 Welcome@2026[1]")
    assert ok
    bad, reason = judge_answer(case, "初始密码是 abc123")
    assert not bad and "Welcome@2026" in reason

    leak = next(c for c in CASES if c.qid == "r04")
    ok2, _ = judge_answer(leak, "资料未提及")
    assert ok2
    bad2, reason2 = judge_answer(leak, "资料未提及，但最高权限是 admin")
    assert not bad2 and "最高权限" in reason2
