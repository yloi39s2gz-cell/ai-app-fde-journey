from llm_client import LLMClient


def main() -> None:
    client = LLMClient()
    print("非流式：")
    result = client.chat(
        [{"role": "user", "content": "用十个字以内解释 token 是什么。"}],
        max_tokens=60,
    )
    print(result.content)
    print(
        f"耗时 {result.latency_ms} ms | "
        f"prompt={result.prompt_tokens} completion={result.completion_tokens}"
    )

    print("\n流式（字是一个一个出来的）：")
    for piece in client.chat_stream(
        [{"role": "user", "content": "用一句话说明为什么 RAG 不能消灭幻觉。"}],
        max_tokens=80,
    ):
        print(piece, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
