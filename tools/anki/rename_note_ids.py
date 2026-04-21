#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("domains/b737/anki/notes/limits")
DEFAULT_MANIFEST = Path("domains/b737/anki/rename_note_ids_manifest.csv")

OLD_STYLE_PATTERNS = [
    re.compile(r"^lim-alt-\d{3}$"),
    re.compile(r"^lim-spd-\d{3}$"),
    re.compile(r"^lim-wind-\d{3}(?:-max)?$"),
    re.compile(r"^lim-wt-\d{3}(?:-max)?$"),
    re.compile(r"^lim-18-\d+(?:-\d+)*-\d{3}(?:-max)?$"),
]

NOTE_ID_RE = re.compile(r"(?m)^note_id:\s*(\S+)\s*$")


def is_old_style(note_id: str) -> bool:
    return any(p.fullmatch(note_id) for p in OLD_STYLE_PATTERNS)


def read_note_id(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = NOTE_ID_RE.search(text)
    if not m:
        raise ValueError(f"{path}: could not find note_id")
    return m.group(1)


def write_note_id(path: Path, new_note_id: str) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, n = NOTE_ID_RE.subn(f"note_id: {new_note_id}", text, count=1)
    if n != 1:
        raise ValueError(f"{path}: failed to rewrite note_id")
    path.write_text(new_text, encoding="utf-8")


def build_manifest(root: Path, manifest: Path) -> int:
    rows = []
    for path in sorted(root.rglob("*.md")):
        note_id = read_note_id(path)
        if is_old_style(note_id):
            rows.append(
                {
                    "path": str(path),
                    "old_note_id": note_id,
                    "new_note_id": "",
                }
            )

    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "old_note_id", "new_note_id"])
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote manifest: {manifest}")
    print(f"Candidates: {len(rows)}")
    return 0


def git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src), str(dst)], check=True)


def apply_manifest(manifest: Path) -> int:
    with manifest.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        src = Path(row["path"])
        old_note_id = row["old_note_id"].strip()
        new_note_id = row["new_note_id"].strip()

        if not new_note_id:
            continue

        if src.stem != old_note_id:
            raise ValueError(
                f"{src}: filename stem does not match old_note_id "
                f"({src.stem!r} != {old_note_id!r})"
            )

        dst = src.with_name(f"{new_note_id}.md")

        if src == dst:
            write_note_id(src, new_note_id)
            print(f"UPDATED note_id only: {src}")
            continue

        git_mv(src, dst)
        write_note_id(dst, new_note_id)
        print(f"RENAMED: {src} -> {dst}")

    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in {"build", "apply"}:
        print(
            "Usage:\n"
            "  tools/anki/rename_note_ids.py build [manifest.csv]\n"
            "  tools/anki/rename_note_ids.py apply [manifest.csv]"
        )
        return 2

    cmd = argv[1]
    manifest = Path(argv[2]) if len(argv) > 2 else DEFAULT_MANIFEST

    if cmd == "build":
        return build_manifest(ROOT, manifest)
    if cmd == "apply":
        return apply_manifest(manifest)

    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))