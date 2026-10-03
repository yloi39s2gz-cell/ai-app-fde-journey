from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError

for env_path in (
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / "stage0" / ".env",
):
    if env_path.exists():
        load_dotenv(env_path)
        break

logger = logging.getLogger("llm")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass
class ChatResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    finish_reason: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def assistant_message(self) -> dict:
        msg: dict = {"role": "assistant", "content": self.content or None}
        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.arguments},
                }
                for call in self.tool_calls
            ]
        elif msg["content"] is None:
            msg["content"] = ""
        return msg


class LLMClient:
    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 0.8,
    ) -> None:
        api_key = os.getenv("LLM_API_KEY", "").strip()
        base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
        self.model = os.getenv("LLM_MODEL", "deepseek-chat").strip()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        if not api_key or api_key.startswith("sk-替换"):
            raise SystemExit("未配置 LLM_API_KEY。请先填 stage0/.env 或 stage1/.env")
        # 客户端建一次、后面反复用。timeout 防止请求挂死。
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def _should_retry(self, exc: Exception) -> bool:
        # 过一会儿可能好的错误才重试；参数写错重试没有意义。
        if isinstance(exc, (RateLimitError, APITimeoutError, APIConnectionError)):
            return True
        if isinstance(exc, APIStatusError):
            return (exc.status_code or 0) >= 500
        return False

    def _create(self, **kwargs):
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries and self._should_retry(exc):
                    time.sleep(self.retry_backoff * attempt)
                    continue
                raise
        raise last_error  # pragma: no cover

    def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.0,
        max_tokens: int = 400,
        tools: list[dict] | None = None,
        tool_choice: str | dict | None = None,
    ) -> ChatResult:
        t0 = time.perf_counter()
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if tools:
            kwargs["tools"] = tools
            if tool_choice is not None:
                kwargs["tool_choice"] = tool_choice
        resp = self._create(**kwargs)
        choice = resp.choices[0]
        usage = resp.usage
        message = choice.message
        tool_calls: list[ToolCall] = []
        for raw in getattr(message, "tool_calls", None) or []:
            fn = raw.function
            tool_calls.append(
                ToolCall(
                    id=raw.id,
                    name=fn.name,
                    arguments=fn.arguments or "{}",
                )
            )
        result = ChatResult(
            content=(message.content or "").strip(),
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            finish_reason=choice.finish_reason,
            tool_calls=tool_calls,
        )
        logger.info(
            "chat done latency_ms=%s prompt=%s completion=%s tools=%s",
            result.latency_ms,
            result.prompt_tokens,
            result.completion_tokens,
            [c.name for c in tool_calls] or "-",
        )
        return result

    def chat_stream(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.0,
        max_tokens: int = 400,
    ) -> Iterator[str]:
        stream = self._create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
