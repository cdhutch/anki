#!/usr/bin/env python3
"""fix_vstup_audit.py

Applies targeted fixes to Вступ lexeme notes based on deep consistency audit.

Changes made:
  1. Adjectives 0087–0098: convert feminine → masculine lemma, update Gender,
     TypingAnswer, Source_URL
  2. Interjection 0105 (приві́т): PartOfSpeech phrase → interjection, tag fix
  3. IrregularForms fills for 8 nouns (вікно, мі́сто, сімʼя́, число́, ве́чір,
     вчи́тель, воді́й, пра́пор)
  4. CounterpartForm: воді́й (0003) → f: воді́йка
  5. ува́га (0066): clear spurious IrregularForms

Usage:
    python tools/anki/inspect/fix_vstup_audit.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
NOTES_DIR = REPO_ROOT / "domains" / "ua" / "anki" / "notes" / "lexemes" / "yabluko-l1" / "vstup"
GOROH_BASE = "https://goroh.pp.ua/Словозміна/"
STRESS_MARK = "́"  # U+0301 COMBINING ACUTE ACCENT


def strip_stress(s: str) -> str:
    return s.replace(STRESS_MARK, "")


def goroh_url(lemma: str) -> str:
    bare = strip_stress(lemma)
    if " " in bare:
        return ""
    return GOROH_BASE + bare


# ---------------------------------------------------------------------------
# Low-level field setters (operate on raw file text via regex)
# ---------------------------------------------------------------------------

def set_field(text: str, field: str, value: str) -> str:
    """Replace the value of a YAML field inside the fields: block."""
    # Match '  FieldName: <anything to end of line>'
    pattern = rf"(^  {re.escape(field)}:) .*$"
    if value == "":
        replacement = rf"\1 ''"
    else:
        # Quote if value contains : or starts with special chars
        needs_quoting = any(c in value for c in (":", "#", "[", "]", "{", "}"))
        if needs_quoting:
            replacement = rf"\1 '{value}'"
        else:
            replacement = rf"\1 {value}"
    new_text, n = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if n == 0:
        raise ValueError(f"Field '{field}' not found in note")
    return new_text


def set_tag(text: str, old_tag: str, new_tag: str) -> str:
    """Replace a tag value in the YAML tags list (handles any indentation)."""
    pattern = rf"(^\s*- ){re.escape(old_tag)}$"
    new_text, n = re.subn(pattern, rf"\1{new_tag}", text, flags=re.MULTILINE)
    if n == 0:
        raise ValueError(f"Tag '{old_tag}' not found in note")
    return new_text


# ---------------------------------------------------------------------------
# Per-note fix functions
# ---------------------------------------------------------------------------

def fix_adjective(path: Path, dry_run: bool) -> bool:
    """Convert feminine adjective lemma to masculine."""
    text = path.read_text(encoding="utf-8")

    # Extract current lemma
    m = re.search(r"^  Lemma: (.+)$", text, re.MULTILINE)
    if not m:
        print(f"  WARN: no Lemma in {path.name}", file=sys.stderr)
        return False

    fem = m.group(1).strip().strip("'\"")
    if not fem.endswith("а"):
        print(f"  SKIP {path.name}: lemma {fem!r} doesn't end in а (already masculine?)")
        return False

    # Feminine → masculine: strip final а, add ий
    masc = fem[:-1] + "ий"
    typing = strip_stress(masc)
    url = goroh_url(masc)

    if dry_run:
        print(f"  DRY {path.name}: {fem} → {masc}  typing={typing}")
        return True

    text = set_field(text, "Lemma", masc)
    text = set_field(text, "Gender", "m")
    text = set_field(text, "TypingAnswer", typing)
    text = set_field(text, "Source_URL", url)
    path.write_text(text, encoding="utf-8")
    print(f"  FIX {path.name}: {fem} → {masc}")
    return True


def fix_interjection(path: Path, dry_run: bool) -> bool:
    """Change PartOfSpeech from phrase to interjection for приві́т."""
    text = path.read_text(encoding="utf-8")

    if dry_run:
        print(f"  DRY {path.name}: PartOfSpeech phrase → interjection; pos:phrase → pos:interjection")
        return True

    text = set_field(text, "PartOfSpeech", "interjection")
    text = set_tag(text, "pos:phrase", "pos:interjection")
    path.write_text(text, encoding="utf-8")
    print(f"  FIX {path.name}: interjection")
    return True


def fix_irregular_forms(path: Path, value: str, dry_run: bool) -> bool:
    """Set IrregularForms to value."""
    text = path.read_text(encoding="utf-8")

    if dry_run:
        print(f"  DRY {path.name}: IrregularForms → {value!r}")
        return True

    text = set_field(text, "IrregularForms", value)
    path.write_text(text, encoding="utf-8")
    print(f"  FIX {path.name}: IrregularForms = {value!r}")
    return True


def fix_counterpart(path: Path, value: str, dry_run: bool) -> bool:
    """Set CounterpartForm."""
    text = path.read_text(encoding="utf-8")

    if dry_run:
        print(f"  DRY {path.name}: CounterpartForm → {value!r}")
        return True

    text = set_field(text, "CounterpartForm", value)
    path.write_text(text, encoding="utf-8")
    print(f"  FIX {path.name}: CounterpartForm = {value!r}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def note_path(n: int) -> Path:
    return NOTES_DIR / f"ua-lexeme-{n:04d}.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run
    if dry:
        print("DRY RUN — no files will be written.\n")

    changes = 0

    # ------------------------------------------------------------------
    # 1. Adjectives: feminine → masculine (0087–0098)
    # ------------------------------------------------------------------
    print("=== Adjectives: feminine → masculine ===")
    for n in range(87, 99):
        if fix_adjective(note_path(n), dry):
            changes += 1

    # ------------------------------------------------------------------
    # 2. Interjection: приві́т 0105
    # ------------------------------------------------------------------
    print("\n=== Interjection fix ===")
    if fix_interjection(note_path(105), dry):
        changes += 1

    # ------------------------------------------------------------------
    # 3. IrregularForms fills
    #
    # Values chosen for pedagogical usefulness (notable gen.pl / stem alternations).
    # Stress marks omitted where uncertain — all notes carry stress:unverified
    # and will be validated against Горох in the next pass.
    # ------------------------------------------------------------------
    print("\n=== IrregularForms fills ===")

    irregular_fills = {
        # note#: (lemma for reference, irregular forms text)
        3:   ("воді́й",   "gen.pl. воді́їв"),
        20:  ("вчи́тель", "gen.pl. вчителів (stress shifts)"),
        29:  ("ве́чір",   "gen.sg. вечора (stem vowel і→о in oblique cases)"),
        31:  ("вікно́",   "gen.pl. вікон (zero ending)"),
        44:  ("мі́сто",   "gen.pl. міст (zero ending)"),
        # 56 пра́пор: regular hard-stem declension — nothing to note
        62:  ("сімʼя́",   "gen.pl. сімей"),
        69:  ("число́",   "gen.pl. чисел (fleeting е, stress shifts)"),
    }

    for n, (lemma, value) in irregular_fills.items():
        if fix_irregular_forms(note_path(n), value, dry):
            changes += 1

    # 66 ува́га — clear spurious IrregularForms
    print("\n=== Clear spurious IrregularForms ===")
    if fix_irregular_forms(note_path(66), "", dry):
        changes += 1

    # ------------------------------------------------------------------
    # 4. CounterpartForm: воді́й → f: воді́йка
    # ------------------------------------------------------------------
    print("\n=== CounterpartForm additions ===")
    if fix_counterpart(note_path(3), "f: воді́йка", dry):
        changes += 1

    print(f"\n{'Would make' if dry else 'Made'} {changes} changes.")
    if not dry:
        print("\nNext steps:")
        print("  python -m tools.anki.cnsf_canonicalize --write domains/ua/anki/notes/lexemes/yabluko-l1/vstup/")
        print("  python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/vstup/")


if __name__ == "__main__":
    main()
