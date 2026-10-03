from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
    if not api_key or api_key.startswith("sk-替换"):
        raise SystemExit(
            "还没有配置 API Key。\n"
            "1. 打开 https://platform.deepseek.com/ 注册并创建一个 Key\n"
            "2. 复制 stage0/.env.example 为 stage0/.env\n"
            "3. 把 LLM_API_KEY 改成你的 Key"
        )
    return OpenAI(api_key=api_key, base_url=base_url)


def get_model() -> str:
    return os.getenv("LLM_MODEL", "deepseek-chat").strip()


def chat(
    messages: list[dict],
    *,
    temperature: float = 0.0,
    max_tokens: int = 400,
) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=get_model(),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()
