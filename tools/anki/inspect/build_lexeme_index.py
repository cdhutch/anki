#!/usr/bin/env python3
"""tools/anki/inspect/build_lexeme_index.py — Regenerate a flat UA_Lexeme master index.

New 2026-07-24. Scanning ~200 individual `ua-lexeme-NNNN.md` files one at a time (via
YAML frontmatter parsing) is fine for a single dedup lookup, but expensive for a
whole-corpus audit — every note has to be opened and parsed just to compare a handful
of fields. This script does that scan once and writes the result as a single flat TSV,
so a corpus-wide review (mechanical UA-spelling-collision detection, or a human/Claude
read-through of every EN_Gloss to spot convergent-synonym clusters — see CLAUDE.md
"Vocabulary dedup & homograph handling") only has to read one file instead of ~200.

This index is a **regenerable build artifact, not canonical data** — same status as
everything else under `build/` (gitignored via `build/*`). The individual
`ua-lexeme-NNNN.md` files remain the single source of truth; nothing reads this index
back into Anki or treats it as authoritative. In particular, `tools/anki/lib/
lexeme_dedup.py`'s `create_or_link_lexeme()` deliberately does NOT use this index —
it always re-scans the live corpus, because writing a note based on a stale cached
index would risk a silent duplicate. Regenerate before every audit pass:

    python tools/anki/inspect/build_lexeme_index.py

Craig runs this (see CLAUDE.md Big 3 Rules — Claude does not run scripts in this repo
itself); the resulting build/ua_lexeme_index.tsv is small enough to hand back for
review in one file instead of staging every note individually.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.cnsf_canonicalize import split_frontmatter  # noqa: E402
from tools.anki.lib.lexeme_dedup import strip_stress  # noqa: E402

DEFAULT_LEXEME_ROOT = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes"
DEFAULT_OUT = REPO_ROOT / "build" / "ua_lexeme_index.tsv"

COLUMNS = [
    "NoteID",
    "LemmaStripped",
    "Lemma",
    "PartOfSpeech",
    "Gender",
    "EN_Gloss",
    "ConfusableSet",
    "VerbMotion_Pair",
    "CrossLang_Analog",
    "Tags_Ch",
    "Tags",
    "Homograph",
    "Status",
    "Path",
]


def _tsv_escape(s: str) -> str:
    # TSV cells: collapse embedded tabs/newlines so the table stays one-row-per-note.
    return (s or "").replace("\t", " ").replace("\r", " ").replace("\n", " \\n ").strip()


def _relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def build_rows(lexeme_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(lexeme_root.resolve().rglob("ua-lexeme-*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            fm = split_frontmatter(text, path)
        except ValueError as e:
            print(f"WARNING: skipping {path} — {e}", file=sys.stderr)
            continue
        meta = yaml.safe_load(fm.yaml_text) or {}
        if not isinstance(meta, dict):
            print(f"WARNING: skipping {path} — frontmatter is not a mapping", file=sys.stderr)
            continue

        fields = meta.get("fields", {}) or {}
        tags = meta.get("tags", []) or []
        lemma = fields.get("Lemma", "")
        status = next((t.split(":", 1)[1] for t in tags if isinstance(t, str) and t.startswith("status:")), "")

        rows.append(
            {
                "NoteID": fields.get("NoteID", path.stem),
                "LemmaStripped": strip_stress(lemma),
                "Lemma": lemma,
                "PartOfSpeech": fields.get("PartOfSpeech", ""),
                "Gender": fields.get("Gender", ""),
                "EN_Gloss": fields.get("EN_Gloss", ""),
                "ConfusableSet": fields.get("ConfusableSet", ""),
                "VerbMotion_Pair": fields.get("VerbMotion_Pair", ""),
                "CrossLang_Analog": fields.get("CrossLang_Analog", ""),
                "Tags_Ch": fields.get("Tags_Ch", ""),
                "Tags": ";".join(t for t in tags if isinstance(t, str)),
                "Homograph": "yes" if "homograph:true" in tags else "",
                "Status": status,
                "Path": _relpath(path),
            }
        )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(COLUMNS)]
    for row in rows:
        lines.append("\t".join(_tsv_escape(row[c]) for c in COLUMNS))
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lexeme-root", type=Path, default=DEFAULT_LEXEME_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = build_rows(args.lexeme_root)
    write_tsv(rows, args.out)

    n_homograph = sum(1 for r in rows if r["Homograph"] == "yes")
    lemma_counts: dict[str, int] = {}
    for r in rows:
        lemma_counts[r["LemmaStripped"]] = lemma_counts.get(r["LemmaStripped"], 0) + 1
    n_collisions = sum(1 for c in lemma_counts.values() if c > 1)

    print(f"Wrote {len(rows)} notes to {_relpath(args.out)}")
    print(f"  {n_homograph} already tagged homograph:true")
    print(f"  {n_collisions} distinct spelling(s) shared by more than one note (candidates for the new/duplicate/homograph audit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
