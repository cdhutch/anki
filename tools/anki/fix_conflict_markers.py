#!/usr/bin/env python3
"""Strip git conflict markers from files, keeping HEAD (ours) content.

Run from repo root after a merge that left conflict markers in working tree:
    python3 tools/anki/fix_conflict_markers.py
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    # Keep HEAD (ours) section, discard theirs
    new_text = re.sub(
        r"<<<<<<< [^\n]+\n(.*?)=======\n.*?>>>>>>> [^\n]+\n?",
        r"\1",
        text,
        flags=re.DOTALL,
    )
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    result = subprocess.run(
        ["grep", "-rl", "<<<<<<< HEAD", "domains/"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    files = [f for f in result.stdout.strip().split("\n") if f]
    print(f"Found {len(files)} files with conflict markers")

    fixed = 0
    errors = []
    for fp in files:
        p = REPO_ROOT / fp
        try:
            if fix_file(p):
                fixed += 1
        except Exception as e:
            errors.append((fp, str(e)))

    print(f"Fixed  : {fixed}")
    print(f"Skipped: {len(files) - fixed - len(errors)}")
    if errors:
        print(f"Errors : {len(errors)}")
        for fp, err in errors:
            print(f"  {fp}: {err}")

    # Verify none remain
    result2 = subprocess.run(
        ["grep", "-rl", "<<<<<<< HEAD", "domains/"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    remaining = [f for f in result2.stdout.strip().split("\n") if f]
    if remaining:
        print(f"\nWARNING: {len(remaining)} files still have conflict markers:")
        for f in remaining[:10]:
            print(f"  {f}")
    else:
        print("\nAll conflict markers cleared.")


if __name__ == "__main__":
    main()
