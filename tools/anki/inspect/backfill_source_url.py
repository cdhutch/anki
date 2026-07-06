#!/usr/bin/env python3
"""
backfill_source_url.py

Injects Source_URL and Source_Note fields into all ua_lexeme CNSF notes
that are missing them.

Source_URL is set to the goroh.pp.ua Словозміна page for the bare lemma
(Lemma with U+0301 stress marks stripped).

Source_Note is set to '' (blank) — fill in manually after stress verification.

Usage:
    python tools/anki/inspect/backfill_source_url.py [--dry-run]

Options:
    --dry-run   Print what would change without writing any files.

Notes:
    - Idempotent: skips notes that already have Source_URL set.
    - Reads YAML front matter only; leaves front_md / back_md untouched.
    - Appends the two new fields at the end of the fields: block,
      before the closing --- of the front matter.
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
NOTES_DIR = REPO_ROOT / "domains" / "ua" / "anki" / "notes"
GOROH_BASE = "https://goroh.pp.ua/Словозміна/"

STRESS_MARK = "́"  # U+0301 COMBINING ACUTE ACCENT


def strip_stress(lemma: str) -> str:
    """Remove U+0301 combining acute accent from a string."""
    return lemma.replace(STRESS_MARK, "")


def goroh_url(lemma: str) -> str:
    """Return goroh URL, or empty string for multi-word lemmas (phrases)."""
    bare = strip_stress(lemma)
    if " " in bare:
        return ""   # goroh.pp.ua is for single words only
    return GOROH_BASE + bare


def extract_lemma(content: str) -> str | None:
    """Extract the Lemma value from the fields: block."""
    m = re.search(r"^\s+Lemma:\s+(.+)$", content, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    # Strip surrounding quotes if present
    if (val.startswith("'") and val.endswith("'")) or (
        val.startswith('"') and val.endswith('"')
    ):
        val = val[1:-1]
    return val


def already_has_source_url(content: str) -> bool:
    return bool(re.search(r"^\s+Source_URL:", content, re.MULTILINE))


def inject_source_fields(content: str, url: str) -> str:
    """
    Insert Source_URL and Source_Note after 'Verification Notes:' line,
    or before the closing --- of the front matter if that line is absent.
    """
    url_line = f"  Source_URL: '{url}'\n"
    note_line = "  Source_Note: ''\n"

    # Try to insert after "Verification Notes:" line
    pattern = r"(^  Verification Notes:.*\n)"
    m = re.search(pattern, content, re.MULTILINE)
    if m:
        insert_pos = m.end()
        return content[:insert_pos] + url_line + note_line + content[insert_pos:]

    # Fallback: insert before the closing --- of the front matter
    # Front matter ends at the second occurrence of ---
    fm_end = content.index("---", 3)  # skip opening ---
    return content[:fm_end] + url_line + note_line + content[fm_end:]


def process_file(path: Path, dry_run: bool) -> bool:
    """Return True if the file was (or would be) modified."""
    content = path.read_text(encoding="utf-8")

    if already_has_source_url(content):
        return False

    lemma = extract_lemma(content)
    if not lemma:
        print(f"  WARN: no Lemma found in {path.name} — skipping", file=sys.stderr)
        return False

    url = goroh_url(lemma)
    new_content = inject_source_fields(content, url)

    if dry_run:
        print(f"  DRY-RUN {path.name}: Source_URL → {url}")
    else:
        path.write_text(new_content, encoding="utf-8")
        print(f"  OK {path.name}: {lemma} → {url}")

    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    note_files = sorted(NOTES_DIR.rglob("ua-lexeme-*.md"))
    if not note_files:
        print(f"No ua-lexeme-*.md files found under {NOTES_DIR}", file=sys.stderr)
        sys.exit(1)

    modified = 0
    skipped = 0
    for path in note_files:
        changed = process_file(path, dry_run=args.dry_run)
        if changed:
            modified += 1
        else:
            skipped += 1

    action = "Would modify" if args.dry_run else "Modified"
    print(f"\n{action} {modified} file(s). Skipped {skipped} (already have Source_URL or no Lemma).")


if __name__ == "__main__":
    main()
