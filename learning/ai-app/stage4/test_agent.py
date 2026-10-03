from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "stage1"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent import Agent, truncate
from llm_client import ChatResult, ToolCall
from tools import calculator, create_ticket, execute_tool, lookup_ticket, reset_tickets, search_handbook


class ScriptedClient:
    def __init__(self, results: list[ChatResult]) -> None:
        self.results = list(results)
        self.calls: list[dict] = []

    def chat(self, messages, **kwargs) -> ChatResult:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        if not self.results:
            raise AssertionError("ScriptedClient 没有更多回复")
        return self.results.pop(0)


def _text(text: str) -> ChatResult:
    return ChatResult(text, 1, 1, 1, "stop")


def _tools(*pairs: tuple[str, str]) -> ChatResult:
    calls = [
        ToolCall(id=f"call_{i}", name=name, arguments=args)
        for i, (name, args) in enumerate(pairs, start=1)
    ]
    return ChatResult("", 1, 1, 1, "tool_calls", tool_calls=calls)


def test_calculator_allows_arithmetic():
    out = json.loads(calculator("50*5"))
    assert out["ok"] is True
    assert out["value"] == 250


def test_calculator_rejects_code():
    out = json.loads(calculator("__import__('os').system('echo hi')"))
    assert out["ok"] is False


def test_unknown_tool_is_rejected():
    raw, ok = execute_tool("delete_all", "{}")
    assert ok is False
    assert "未知工具" in raw


def test_bad_json_arguments():
    raw, ok = execute_tool("calculator", "{not json")
    assert ok is False
    assert "JSON" in raw


def test_lookup_and_create_ticket():
    reset_tickets()
    row = json.loads(lookup_ticket("T-1001"))
    assert row["status"] == "处理中"
    created = json.loads(create_ticket("hardware", "键盘失灵"))
    assert created["ok"] is True
    assert created["ticket_id"].startswith("T-")
    bad = json.loads(create_ticket("salary", "查工资"))
    assert bad["ok"] is False


def test_search_handbook_printer():
    raw = json.loads(search_handbook("办公打印机在几楼"))
    assert raw["ok"] is True
    assert raw["hits"][0]["source"] == "IT与办公.md"


def test_truncate():
    text = "x" * 50
    cut = truncate(text, 30)
    assert cut.endswith("...[truncated]")
    assert len(cut) == 30


def test_agent_two_step_loop():
    client = ScriptedClient(
        [
            _tools(("calculator", '{"expression":"1+1"}')),
            _text("1+1 等于 2。"),
        ]
    )
    result = Agent(client=client, max_steps=4).run("1+1 等于几？")
    assert result.stop_reason == "completed"
    assert result.tool_names == ["calculator"]
    assert result.answer == "1+1 等于 2。"
    assert len(client.calls) == 2
    tool_msg = client.calls[1]["messages"][-1]
    assert tool_msg["role"] == "tool"
    assert '"value": 2' in tool_msg["content"]


def test_agent_whitelist_blocks_tool():
    client = ScriptedClient(
        [
            _tools(("lookup_ticket", '{"ticket_id":"T-1001"}')),
            _text("不能查工单。"),
        ]
    )
    result = Agent(
        client=client,
        allowed=("calculator",),
        max_steps=4,
    ).run("查 T-1001")
    assert result.tool_names == ["lookup_ticket"]
    obs = result.steps[0].observations[0]
    assert "白名单" in obs
    assert result.answer == "不能查工单。"


def test_agent_max_steps():
    always = _tools(("calculator", '{"expression":"1"}'))
    client = ScriptedClient([always, always, always])
    result = Agent(client=client, max_steps=3).run("无限循环")
    assert result.stop_reason == "max_steps"
    assert len(result.steps) == 3
    assert "最大步数" in result.answer
