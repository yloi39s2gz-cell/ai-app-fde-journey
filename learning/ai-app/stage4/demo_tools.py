from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from tools import calculator, create_ticket, lookup_ticket, reset_tickets, search_handbook


def main() -> None:
    reset_tickets()
    demos = [
        ("search_handbook", search_handbook("办公打印机在几楼")),
        ("calculator", calculator("50*8")),
        ("lookup_ticket", lookup_ticket("T-1001")),
        ("create_ticket", create_ticket("hardware", "键盘失灵", "工位 A12")),
        ("bad_category", create_ticket("salary", "查工资", "")),
        ("unknown_ticket", lookup_ticket("T-9999")),
    ]
    for name, out in demos:
        print("=" * 60)
        print(name)
        print(out)


if __name__ == "__main__":
    main()
