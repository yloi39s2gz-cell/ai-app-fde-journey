"""中文友好分词：单字 + 相邻二字组合（bi-gram）。

为什么要这样做：
- 中文没有空格，按空格切词会把整句当成一个 token。
- 分词器（jieba）能切词，但会引入第三方依赖，而且对「A3 彩打」「VPN」这类
  中英混排的短词不一定比 n-gram 稳。
- 教学目的下，单字 + 二字组合是「够用且完全透明」的方案：
  "A3彩打仅限市场部" -> ["a","3","彩","打","仅","限","市","场","部","a3","3彩","彩打","打仅",...]

面试要点：这是 sparse（稀疏）检索的 token 化层。生产上你会换成
jieba / IK / 或直接把 BM25 换成 BM25F、Splade 等；但衡量口径不变：
召回率、MRR。换 tokenizer 前后必须跑同一套 eval。
"""

from __future__ import annotations

import re

# 用 chr() 拼出中日韩统一表意文字区间，避免源码里写 unicode 转义（可读性差且易抄错）
CJK_START = chr(0x4E00)
CJK_END = chr(0x9FFF)

# 只保留：连续的汉字 / 连续的字母 / 连续的数字。标点与空白自然成为切分边界。
_TOKEN_RE = re.compile(f"[{CJK_START}-{CJK_END}]+|[a-zA-Z0-9]+")


def normalize(text: str) -> str:
    """小写化，供英文/数字词使用。中文不受影响。"""
    return (text or "").lower()


def tokenize(text: str) -> list[str]:
    """返回 token 列表：英文/数字整词 + 中文单字 + 中文相邻二字组合。"""
    tokens: list[str] = []
    for match in _TOKEN_RE.finditer(normalize(text)):
        piece = match.group(0)
        if not piece:
            continue
        if piece.isascii():
            # [a-zA-Z0-9]+ 让字母与数字在"连续"时属于同一 token：
            #   "A3"           -> ["a3"]              编号作为一个整体（否则会被拆成 "a"+"3"，
            #                                           BM25 会当成两个极常见词，IDF 失灵）
            #   "Welcome@2026" -> ["welcome","2026"] 被 @ 隔开，词与数字分开
            tokens.append(piece)
            continue
        # 中文：单字 + 相邻二字组合
        tokens.extend(piece)
        tokens.extend(piece[i : i + 2] for i in range(len(piece) - 1))
    return tokens
