"""阶段 0：LLM 心智模型。先跑，再对照笔记想「为什么」。"""

from __future__ import annotations

import argparse
import sys
import textwrap

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from llm_client import chat

QUESTION = "用一句话解释什么是 RAG。不要举例。"

HANDBOOK = """\
内部制度摘录（完整）：
1. 工位预约通过 OA 提交，提前一天。
2. 打印机在 3 楼茶水间旁，需工牌刷卡。
3. 出差交通按经济舱报销，需保留发票。
"""


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def exp1_temperature() -> None:
    banner("实验1  temperature=0 vs 0.8  各 5 次")
    print("同一问题、同一模型。看哪边更稳、哪边更花。\n")
    for temp in (0.0, 0.8):
        print(f"\n--- temperature={temp} ---")
        answers = []
        for i in range(5):
            ans = chat(
                [{"role": "user", "content": QUESTION}],
                temperature=temp,
                max_tokens=80,
            )
            answers.append(ans)
            print(f"[{i + 1}] {ans}")
        unique = len(set(answers))
        print(f"\n不重复答案数：{unique}/5  （越接近 1 越稳）")


def _haystack(needle: str, position: str, filler_chars: int = 3500) -> str:
    filler = ("会议室预订走前台登记。" * 200)[:filler_chars]
    if position == "start":
        return needle + "\n" + filler
    if position == "end":
        return filler + "\n" + needle
    mid = len(filler) // 2
    return filler[:mid] + "\n" + needle + "\n" + filler[mid:]


def exp2_context() -> None:
    banner("实验2  上下文不是无限的，中间还容易丢")
    needle = "【关键事实】服务器机房门禁密码是 7492，仅运维组可知。"
    ask = "资料里的服务器机房门禁密码是多少？只答数字，找不到就说不知道。"

    sample = _haystack(needle, "middle")
    approx_tokens = int(len(sample) * 1.6)
    print(f"本实验文本约 {len(sample)} 字，粗估 {approx_tokens} tokens。")
    print("真实 API 到上限会报 context_length_exceeded；我们不烧钱撞墙。")
    print("更关键的工程事实：长文中间的信息，模型经常看不见。\n")

    for pos in ("start", "middle", "end"):
        doc = _haystack(needle, pos)
        ans = chat(
            [
                {
                    "role": "system",
                    "content": "只根据用户给的资料回答。资料没有就说不知道。",
                },
                {"role": "user", "content": f"资料：\n{doc}\n\n问题：{ask}"},
            ],
            temperature=0,
            max_tokens=50,
        )
        print(f"关键句在文档【{pos:6}】时，模型答：{ans}")


def exp3_hallucination() -> None:
    banner("实验3  资料没有的东西，模型会不会编")
    system = (
        "你是公司制度助手。必须引用资料原句回答。"
        "如果资料里没有，必须回答：资料未提及，不能确定。"
        "禁止使用常识补全。"
    )

    cases = [
        ("资料里有的", "打印机在几楼？"),
        ("资料里没有的", "我们公司年假有多少天？"),
    ]
    for label, question in cases:
        ans = chat(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"资料：\n{HANDBOOK}\n\n问题：{question}",
                },
            ],
            temperature=0,
            max_tokens=120,
        )
        print(f"\n[{label}] {question}")
        print(textwrap.fill(ans, width=56))


def main() -> None:
    parser = argparse.ArgumentParser(description="阶段0 三个实验")
    parser.add_argument(
        "which",
        nargs="?",
        default="all",
        choices=["all", "1", "2", "3"],
        help="跑全部或指定某一个",
    )
    args = parser.parse_args()
    mapping = {"1": exp1_temperature, "2": exp2_context, "3": exp3_hallucination}
    if args.which == "all":
        exp1_temperature()
        exp2_context()
        exp3_hallucination()
    else:
        mapping[args.which]()
    print("\n跑完后打开 stage0/notes.md 把观察填进去。")


if __name__ == "__main__":
    main()
