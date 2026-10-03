from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "stage1"))

from parser import ResumeParser
from samples import SAMPLES
from schemas import Resume


def _norm(s: str | None) -> str:
    return (s or "").strip().lower().replace(" ", "")


def _years_ok(got: float | None, exp: float | None) -> bool:
    if exp is None:
        return True
    if got is None:
        return False
    return abs(got - exp) <= 0.6


def _skills_ok(got: list[str], exp: list[str] | None) -> bool:
    if not exp:
        return True
    g = {_norm(x) for x in got}
    hits = sum(1 for x in exp if _norm(x) in g or any(_norm(x) in y or y in _norm(x) for y in g))
    return hits >= max(1, int(round(len(exp) * 0.6)))


def score_one(got: Resume, expected: dict) -> tuple[bool, list[str]]:
    misses: list[str] = []
    if _norm(got.name) != _norm(expected.get("name")):
        misses.append(f"name {got.name!r} != {expected.get('name')!r}")
    if not _years_ok(got.years_experience, expected.get("years_experience")):
        misses.append(f"years {got.years_experience} != {expected.get('years_experience')}")
    if not _skills_ok(got.skills, expected.get("skills")):
        misses.append(f"skills {got.skills} missing {expected.get('skills')}")
    for key in ("latest_title", "latest_company", "education", "email"):
        exp = expected.get(key)
        if not exp:
            continue
        val = getattr(got, key)
        if key == "email":
            if _norm(val) != _norm(exp):
                misses.append(f"{key} {val!r} != {exp!r}")
        elif _norm(exp) not in _norm(val) and _norm(val) not in _norm(exp):
            misses.append(f"{key} {val!r} != {exp!r}")
    return (not misses, misses)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = ResumeParser()
    ok = 0
    total = len(SAMPLES)
    for item in SAMPLES:
        try:
            got = parser.parse(item["text"])
            passed, misses = score_one(got, item["expected"])
        except Exception as exc:
            passed, misses, got = False, [str(exc)], None
        if passed:
            ok += 1
            print(f"[PASS] {item['id']}  {got.name}")
        else:
            print(f"[FAIL] {item['id']}  {misses}")
            if got:
                print(f"       got={got.model_dump()}")
    rate = ok / total
    print(f"\n{ok}/{total} = {rate:.0%}")
    if rate < 0.95:
        raise SystemExit("未达到 95% 过关线，看 FAIL 再改 prompt 或 schema")
    print("过关：结构化抽取 >= 95%")


if __name__ == "__main__":
    main()
