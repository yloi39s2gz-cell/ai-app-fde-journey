from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import openai
import pytest

from llm_client import ChatResult, LLMClient


def _fake_response(text: str = "hello", prompt=3, completion=2, reason="stop"):
    usage = SimpleNamespace(prompt_tokens=prompt, completion_tokens=completion)
    choice = SimpleNamespace(
        message=SimpleNamespace(content=text),
        finish_reason=reason,
    )
    return SimpleNamespace(choices=[choice], usage=usage)


def _client_with_mock():
    with patch.dict(
        "os.environ",
        {
            "LLM_API_KEY": "sk-test-key-123456",
            "LLM_BASE_URL": "https://example.invalid",
            "LLM_MODEL": "fake-model",
        },
        clear=False,
    ):
        with patch("llm_client.OpenAI") as mock_openai:
            mock_create = MagicMock()
            mock_openai.return_value.chat.completions.create = mock_create
            client = LLMClient(timeout=5.0, max_retries=3, retry_backoff=0.0)
            return client, mock_openai, mock_create


def test_openai_client_created_with_timeout():
    client, mock_openai, _ = _client_with_mock()
    mock_openai.assert_called()
    kwargs = mock_openai.call_args.kwargs
    assert kwargs["api_key"] == "sk-test-key-123456"
    assert kwargs["base_url"] == "https://example.invalid"
    assert kwargs["timeout"] == 5.0
    assert client.model == "fake-model"


def test_chat_returns_usage_and_latency():
    client, _, mock_create = _client_with_mock()
    mock_create.return_value = _fake_response("RAG 是检索增强生成")
    result = client.chat([{"role": "user", "content": "hi"}])
    assert isinstance(result, ChatResult)
    assert result.content == "RAG 是检索增强生成"
    assert result.prompt_tokens == 3
    assert result.completion_tokens == 2
    assert result.finish_reason == "stop"
    assert result.latency_ms >= 0
    mock_create.assert_called()
    assert mock_create.call_args.kwargs["stream"] is False


def test_retry_on_rate_limit_then_success():
    client, _, mock_create = _client_with_mock()
    mock_create.side_effect = [
        openai.RateLimitError("slow down", response=MagicMock(status_code=429), body=None),
        _fake_response("ok"),
    ]
    result = client.chat([{"role": "user", "content": "hi"}])
    assert result.content == "ok"
    assert mock_create.call_count == 2


def test_do_not_retry_bad_request():
    client, _, mock_create = _client_with_mock()
    err = openai.APIStatusError(
        "bad",
        response=MagicMock(status_code=400, headers={}),
        body=None,
    )
    mock_create.side_effect = err
    with pytest.raises(openai.APIStatusError):
        client.chat([{"role": "user", "content": "hi"}])
    assert mock_create.call_count == 1


def test_chat_forwards_tools_and_parses_calls():
    client, _, mock_create = _client_with_mock()
    fn = SimpleNamespace(name="calculator", arguments='{"expression":"1+1"}')
    raw = SimpleNamespace(id="call_1", function=fn)
    usage = SimpleNamespace(prompt_tokens=1, completion_tokens=1)
    choice = SimpleNamespace(
        message=SimpleNamespace(content=None, tool_calls=[raw]),
        finish_reason="tool_calls",
    )
    mock_create.return_value = SimpleNamespace(choices=[choice], usage=usage)
    tools = [{"type": "function", "function": {"name": "calculator"}}]
    result = client.chat([{"role": "user", "content": "1+1"}], tools=tools)
    assert result.finish_reason == "tool_calls"
    assert result.tool_calls[0].name == "calculator"
    assert result.tool_calls[0].arguments == '{"expression":"1+1"}'
    assert mock_create.call_args.kwargs["tools"] == tools
    msg = result.assistant_message()
    assert msg["tool_calls"][0]["id"] == "call_1"
    assert msg["content"] is None


def test_stream_yields_deltas():
    client, _, mock_create = _client_with_mock()

    def chunk(text):
        return SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content=text))]
        )

    mock_create.return_value = [chunk("你"), chunk("好"), chunk(None)]
    pieces = list(client.chat_stream([{"role": "user", "content": "hi"}]))
    assert pieces == ["你", "好"]
    assert mock_create.call_args.kwargs["stream"] is True
