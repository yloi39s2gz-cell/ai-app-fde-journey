from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
_STAGE3 = str(ROOT / "stage3")
# append 而不是 insert(0)：否则 stage3/eval_set.py 会盖掉本目录同名模块。
if _STAGE3 not in sys.path:
    sys.path.append(_STAGE3)

from chunker import load_corpus
from embedder import build_embedder
from store import MemoryVectorStore

CATEGORIES = ("hardware", "vpn", "access", "hr", "other")
_ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Load,
)

_handbook: MemoryVectorStore | None = None
_tickets: dict[str, dict[str, str]] = {}
_next_ticket = 2000


def reset_tickets() -> None:
    global _tickets, _next_ticket
    _next_ticket = 2000
    _tickets = {
        "T-1001": {
            "ticket_id": "T-1001",
            "category": "hardware",
            "title": "工位显示器支架申请",
            "status": "处理中",
            "owner": "IT-张磊",
        },
        "T-1002": {
            "ticket_id": "T-1002",
            "category": "vpn",
            "title": "VPN 无法登录",
            "status": "已关闭",
            "owner": "IT-王倩",
        },
        "T-1003": {
            "ticket_id": "T-1003",
            "category": "access",
            "title": "门禁卡丢失补办",
            "status": "待领取",
            "owner": "行政-刘芳",
        },
    }


reset_tickets()


def _store() -> MemoryVectorStore:
    global _handbook
    if _handbook is None:
        corpus = ROOT / "stage3" / "corpus"
        _handbook = MemoryVectorStore(load_corpus(corpus), build_embedder())
    return _handbook


def search_handbook(query: str, top_k: int = 3) -> str:
    q = (query or "").strip()
    if not q:
        return json.dumps({"ok": False, "error": "query 不能为空"}, ensure_ascii=False)
    hits = _store().search(q, top_k=top_k)
    rows = []
    for hit in hits:
        rows.append(
            {
                "rank": hit.rank,
                "score": round(hit.score, 3),
                "source": hit.chunk.source,
                "heading": hit.chunk.heading,
                "text": hit.chunk.text[:240],
            }
        )
    return json.dumps({"ok": True, "query": q, "hits": rows}, ensure_ascii=False)


def _safe_eval(expression: str) -> float | int:
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST):
            raise ValueError(f"不允许的表达式: {expression}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise ValueError("只允许数字运算")
    value = eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, {})
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def calculator(expression: str) -> str:
    expr = (expression or "").strip()
    if not expr:
        return json.dumps({"ok": False, "error": "expression 不能为空"}, ensure_ascii=False)
    try:
        value = _safe_eval(expr)
    except Exception as exc:
        return json.dumps(
            {"ok": False, "error": f"计算失败: {exc}", "expression": expr},
            ensure_ascii=False,
        )
    return json.dumps({"ok": True, "expression": expr, "value": value}, ensure_ascii=False)


def lookup_ticket(ticket_id: str) -> str:
    tid = (ticket_id or "").strip().upper()
    if not tid:
        return json.dumps({"ok": False, "error": "ticket_id 不能为空"}, ensure_ascii=False)
    row = _tickets.get(tid)
    if not row:
        return json.dumps({"ok": False, "error": f"找不到工单 {tid}"}, ensure_ascii=False)
    return json.dumps({"ok": True, **row}, ensure_ascii=False)


def create_ticket(category: str, title: str, detail: str = "") -> str:
    global _next_ticket
    cat = (category or "").strip().lower()
    ttl = (title or "").strip()
    if cat not in CATEGORIES:
        return json.dumps(
            {"ok": False, "error": f"category 必须是 {list(CATEGORIES)} 之一"},
            ensure_ascii=False,
        )
    if not ttl:
        return json.dumps({"ok": False, "error": "title 不能为空"}, ensure_ascii=False)
    _next_ticket += 1
    tid = f"T-{_next_ticket}"
    row = {
        "ticket_id": tid,
        "category": cat,
        "title": ttl,
        "detail": (detail or "").strip(),
        "status": "已受理",
        "owner": "IT-值班",
    }
    _tickets[tid] = row
    return json.dumps({"ok": True, **row}, ensure_ascii=False)


HANDLERS: dict[str, Callable[..., str]] = {
    "search_handbook": search_handbook,
    "calculator": calculator,
    "lookup_ticket": lookup_ticket,
    "create_ticket": create_ticket,
}

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_handbook",
            "description": "检索星河科技员工手册。查假期、报销、IT、入职、福利时必须先调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索问句，尽量用手册里可能出现的原词，例如年假、打印机、餐补",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算加减乘除。餐补合计、天数换算时使用。只接受纯算术表达式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "例如 50*5 或 (10+15)/2",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_ticket",
            "description": "按工单号查询状态。工单号形如 T-1001。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "工单号，例如 T-1001"}
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "创建 IT/行政工单。category 只能是 hardware/vpn/access/hr/other。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "title": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["category", "title"],
            },
        },
    },
]


def execute_tool(name: str, arguments: str) -> tuple[str, bool]:
    if name not in HANDLERS:
        return (
            json.dumps(
                {
                    "ok": False,
                    "error": f"未知工具: {name}",
                    "allowed": sorted(HANDLERS),
                },
                ensure_ascii=False,
            ),
            False,
        )
    try:
        args: Any = json.loads(arguments or "{}")
        if not isinstance(args, dict):
            raise ValueError("arguments 必须是 JSON 对象")
    except (json.JSONDecodeError, ValueError) as exc:
        return (
            json.dumps({"ok": False, "error": f"参数不是合法 JSON: {exc}"}, ensure_ascii=False),
            False,
        )
    try:
        output = HANDLERS[name](**args)
    except TypeError as exc:
        return (
            json.dumps({"ok": False, "error": f"参数错误: {exc}"}, ensure_ascii=False),
            False,
        )
    return output, True
