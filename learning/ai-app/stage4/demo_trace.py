from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agent import Agent, format_trace
from tools import reset_tickets


def main() -> None:
    reset_tickets()
    question = " ".join(sys.argv[1:]).strip() or "入职满两年每年有几天年假？"
    result = Agent().run(question)
    print(format_trace(result))


if __name__ == "__main__":
    main()
