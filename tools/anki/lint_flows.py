#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

FLOW_ROOT = Path("domains/b737/anki/notes/triggers_and_flows")

STATE_WORDS = {"ON", "OFF", "SET", "AUTO", "ARM", "CLOSED", "OPEN", "GUARDED", "PARKED"}
LOWER_STATE_PATTERN = re.compile(
    r"\b(on|off|set|auto|arm|closed|open|guarded|parked)\b"
)

DASH_PATTERN = re.compile(r"^[ \t]*-\s*[^:]+?\s-\s")
ASCII_X_PATTERN = re.compile(r"\bx\b")


def iter_back_lines(text: str) -> list[tuple[int, str]]:
    """
    Return only the lines in the # Back section, with original line numbers.
    """
    lines = text.splitlines()
    in_back = False
    result: list[tuple[int, str]] = []

    for i, line in enumerate(lines, start=1):
        if line.strip() == "# Back":
            in_back = True
            continue
        if in_back and line.startswith("# "):
            break
        if in_back:
            result.append((i, line))

    return result


def should_check_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("*Previous:") or stripped.startswith("*Next:"):
        return False
    return True


def lint_file(path: Path) -> list[tuple[int, str]]:
    errors: list[tuple[int, str]] = []
    text = path.read_text(encoding="utf-8")
    back_lines = iter_back_lines(text)

    for line_no, line in back_lines:
        if not should_check_line(line):
            continue

        # Trailing whitespace
        if line.rstrip() != line:
            errors.append((line_no, "Trailing whitespace"))

        # Double spaces inside content, but ignore indentation
        content = line.lstrip()
        if "  " in content:
            errors.append((line_no, "Double space detected"))

        # Dash instead of colon in checklist-style lines
        if DASH_PATTERN.search(line):
            errors.append((line_no, "Use ':' instead of '-'"))

        # ASCII x instead of multiplication sign, only in numeric contexts
        if re.search(r"\b\d+\s+x\s+\d+\b", line, flags=re.IGNORECASE):
            errors.append((line_no, "Use '×' instead of 'x'"))

        # Lowercase state words, only after a colon or semicolon boundary
        for match in LOWER_STATE_PATTERN.finditer(line):
            word = match.group(1)
            prefix = line[: match.start()]
            if ":" in prefix or ";" in prefix:
                errors.append((line_no, f"State '{word}' should be uppercase"))

    return errors


def main() -> int:
    any_errors = False

    for path in sorted(FLOW_ROOT.glob("*.md")):
        errors = lint_file(path)
        if errors:
            any_errors = True
            print(f"\n{path}:")
            for line_no, msg in errors:
                print(f"  Line {line_no}: {msg}")

    return 1 if any_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())