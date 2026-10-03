from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from eval_set import CASES
from agent import Agent
from tools import reset_tickets


def judge(case, result) -> tuple[bool, str]:
    text = result.answer
    for needle in case.must_include:
        if needle not in text:
            return False, f"答案缺「{needle}」"
    for banned in case.must_not_include:
        if banned in text:
            return False, f"答案不该出现「{banned}」"
    used = result.tool_names
    for name in case.expect_tools:
        if name not in used:
            return False, f"未调用 {name}，实际={used}"
    return True, "ok"


def main() -> None:
    reset_tickets()
    agent = Agent()
    ok = 0
    for case in CASES:
        result = agent.run(case.question)
        passed, reason = judge(case, result)
        ok += int(passed)
        flag = "PASS" if passed else "FAIL"
        print(f"{flag} {case.qid} {case.question}")
        print(f"     tools={result.tool_names} stop={result.stop_reason} steps={len(result.steps)}")
        print(f"     prompt={result.prompt_tokens} completion={result.completion_tokens}")
        print(f"     {reason} | {result.answer[:140].replace(chr(10), ' ')}")
        print()
    total = len(CASES)
    print(f"score={ok}/{total} ({ok / total:.0%})  过关线 70%")
    if ok / total < 0.7:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
