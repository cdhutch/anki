#!/usr/bin/env python3
"""
patch_ch09_stress.py

Apply Горох-verified stress corrections and conjugation tables to ch-09
motion verb notes (ua-lexeme-0114 through ua-lexeme-0131).

Changes applied:
  1. Correct Lemma stress (generator guessed wrong -ди- for walking IPFV)
  2. Add Perfective stress (vehicle PFV had no stress marks)
  3. Fix ConfusableSet references that contained wrong stresses
  4. Fix Source_URL apostrophe (U+02BC → ASCII ' for Горох URLs to work)
  5. Remove stress:unverified tag
  6. Update Source_Note with Горох verification date
  7. Add Verb_Conj_Table HTML to notes 0114, 0115, 0116, 0123

Usage:
    python tools/anki/inspect/patch_ch09_stress.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CH09_DIR = REPO_ROOT / "domains/ua/anki/notes/lexemes/yabluko-l2/ch-09"

APOSTROPHE_UA = "ʼ"   # U+02BC — correct in Lemma/field content
APOSTROPHE_ASCII = "'"  # U+0027 — Горох URLs require this
STRESS = "́"            # U+0301

VERIFICATION_DATE = "2026-07-06"

# ---------------------------------------------------------------------------
# Corrected stress data (all verified against Горох)
# Key: note filename stem (e.g. "ua-lexeme-0114")
# Value: dict of field corrections to apply
# ---------------------------------------------------------------------------

CORRECTIONS = {
    # ── Walking verbs ────────────────────────────────────────────────────────
    "ua-lexeme-0114": {
        "Lemma": "прихо́дити",
        "Perfective": "прийти́",
        "ConfusableSet": "відхо́дити",
    },
    "ua-lexeme-0115": {
        "Lemma": "вхо́дити",
        "Perfective": "увійти́",
        "ConfusableSet": "ви́ходити",
    },
    "ua-lexeme-0116": {
        "Lemma": "ви́ходити",
        "Perfective": "ви́йти",
        "ConfusableSet": "вхо́дити",
    },
    "ua-lexeme-0117": {
        "Lemma": "підхо́дити",
        "Perfective": "підійти́",
        "ConfusableSet": "дохо́дити",
    },
    "ua-lexeme-0118": {
        "Lemma": "відхо́дити",
        "Perfective": "відійти́",
        "ConfusableSet": "прихо́дити",
    },
    "ua-lexeme-0119": {
        "Lemma": "дохо́дити",
        "Perfective": "дійти́",
        "ConfusableSet": "підхо́дити",
    },
    "ua-lexeme-0120": {
        "Lemma": "прохо́дити",
        "Perfective": "пройти́",
        "ConfusableSet": "перехо́дити",
    },
    "ua-lexeme-0121": {
        "Lemma": "перехо́дити",
        "Perfective": "перейти́",
        "ConfusableSet": "прохо́дити",
    },
    "ua-lexeme-0122": {
        "Lemma": "захо́дити",
        "Perfective": "зайти́",
        "ConfusableSet": "заїжджа́ти",  # vehicle counterpart, stress correct
    },
    # ── Vehicle verbs (IPFV stress correct; PFV stress added) ────────────────
    "ua-lexeme-0123": {
        "Lemma": "приїжджа́ти",      # was correct
        "Perfective": "приї́хати",   # added stress
        "ConfusableSet": "прихо́дити",  # corrected
    },
    "ua-lexeme-0124": {
        "Lemma": "вʼїжджа́ти",       # correct; U+02BC preserved in Lemma
        "Perfective": "вʼї́хати",    # added stress; U+02BC preserved
        "ConfusableSet": "виїжджа́ти",  # correct
        "_source_url_word": "в'їжджати",   # ASCII apostrophe for URL
    },
    "ua-lexeme-0125": {
        "Lemma": "виїжджа́ти",
        "Perfective": "ви́їхати",    # ви- prefix stressed (like ви́їхати)
        "ConfusableSet": "вʼїжджа́ти",  # U+02BC, correct
    },
    "ua-lexeme-0126": {
        "Lemma": "підʼїжджа́ти",
        "Perfective": "підʼї́хати",
        "ConfusableSet": "доїжджа́ти",
        "_source_url_word": "під'їжджати",
    },
    "ua-lexeme-0127": {
        "Lemma": "відʼїжджа́ти",
        "Perfective": "відʼї́хати",
        "ConfusableSet": "",
        "_source_url_word": "від'їжджати",
    },
    "ua-lexeme-0128": {
        "Lemma": "доїжджа́ти",
        "Perfective": "дої́хати",
        "ConfusableSet": "підʼїжджа́ти",
    },
    "ua-lexeme-0129": {
        "Lemma": "проїжджа́ти",
        "Perfective": "прої́хати",
        "ConfusableSet": "переїжджа́ти",
    },
    "ua-lexeme-0130": {
        "Lemma": "переїжджа́ти",
        "Perfective": "переї́хати",
        "ConfusableSet": "проїжджа́ти",
    },
    "ua-lexeme-0131": {
        "Lemma": "заїжджа́ти",
        "Perfective": "заї́хати",
        "ConfusableSet": "захо́дити",   # corrected
    },
}

# ---------------------------------------------------------------------------
# Conjugation tables (Горох-verified stress marks)
# Added to: 0114, 0115, 0116, 0123
# ---------------------------------------------------------------------------

def _conj_html(ipfv_label: str, pfv_label: str,
               rows_pres: list[tuple[str, str, str]],
               rows_past: list[tuple[str, str, str]],
               imp_ipfv: str, imp_pfv: str) -> str:
    """Build a compact paired IPFV/PFV conjugation table."""
    th = f'<table class="conj"><tr><th></th><th>IPFV ({ipfv_label})</th><th>PFV ({pfv_label})</th></tr>'
    th += '<tr><th colspan="3">Теп./Майб. (Present / Future)</th></tr>'
    for pro, ipfv_f, pfv_f in rows_pres:
        th += f'<tr><td>{pro}</td><td>{ipfv_f}</td><td>{pfv_f}</td></tr>'
    th += '<tr><th colspan="3">Минулий (Past)</th></tr>'
    for pro, ipfv_f, pfv_f in rows_past:
        th += f'<tr><td>{pro}</td><td>{ipfv_f}</td><td>{pfv_f}</td></tr>'
    th += '<tr><th colspan="3">Наказовий (Imperative)</th></tr>'
    th += f'<tr><td>2sg / 2pl</td><td>{imp_ipfv}</td><td>{imp_pfv}</td></tr>'
    th += '</table>'
    return th


CONJ_TABLES = {
    "ua-lexeme-0114": _conj_html(
        "прихо́дити", "прийти́",
        [
            ("я",           "прихо́джу",   "прийду́"),
            ("ти",          "прихо́диш",   "при́йдеш"),
            ("він/вона",    "прихо́дить",  "при́йде"),
            ("ми",          "прихо́димо",  "при́йдемо"),
            ("ви",          "прихо́дите",  "при́йдете"),
            ("вони",        "прихо́дять",  "при́йдуть"),
        ],
        [
            ("він",   "прихо́див",   "прийшо́в"),
            ("вона",  "прихо́дила",  "прийшла́"),
            ("вони",  "прихо́дили",  "прийшли́"),
        ],
        "прихо́дь / прихо́дьте", "прийди́ / прийді́ть",
    ),
    "ua-lexeme-0115": _conj_html(
        "вхо́дити", "увійти́",
        [
            ("я",           "вхо́джу",    "увійду́"),
            ("ти",          "вхо́диш",    "уві́йдеш"),
            ("він/вона",    "вхо́дить",   "уві́йде"),
            ("ми",          "вхо́димо",   "уві́йдемо"),
            ("ви",          "вхо́дите",   "уві́йдете"),
            ("вони",        "вхо́дять",   "уві́йдуть"),
        ],
        [
            ("він",   "вхо́див",    "увійшо́в"),
            ("вона",  "вхо́дила",   "увійшла́"),
            ("вони",  "вхо́дили",   "увійшли́"),
        ],
        "входь / вхо́дьте", "увійди́ / увійді́ть",
    ),
    "ua-lexeme-0116": _conj_html(
        "ви́ходити", "ви́йти",
        [
            ("я",           "ви́ходжу",   "ви́йду"),
            ("ти",          "ви́ходиш",   "ви́йдеш"),
            ("він/вона",    "ви́ходить",  "ви́йде"),
            ("ми",          "ви́ходимо",  "ви́йдемо"),
            ("ви",          "ви́ходите",  "ви́йдете"),
            ("вони",        "ви́ходять",  "ви́йдуть"),
        ],
        [
            ("він",   "ви́ходив",   "ви́йшов"),
            ("вона",  "ви́ходила",  "ви́йшла"),
            ("вони",  "ви́ходили",  "ви́йшли"),
        ],
        "ви́ходи / ви́ходіть", "ви́йди / ви́йдіть",
    ),
    "ua-lexeme-0123": _conj_html(
        "приїжджа́ти", "приї́хати",
        [
            ("я",           "приїжджа́ю",   "приї́ду"),
            ("ти",          "приїжджа́єш",  "приї́деш"),
            ("він/вона",    "приїжджа́є",   "приї́де"),
            ("ми",          "приїжджа́ємо", "приї́демо"),
            ("ви",          "приїжджа́єте", "приї́дете"),
            ("вони",        "приїжджа́ють", "приї́дуть"),
        ],
        [
            ("він",   "приїжджа́в",   "приї́хав"),
            ("вона",  "приїжджа́ла",  "приї́хала"),
            ("вони",  "приїжджа́ли",  "приї́хали"),
        ],
        "приїжджа́й / приїжджа́йте", "приї́дь / приї́дьте",
    ),
}

# ---------------------------------------------------------------------------
# Patch helpers
# ---------------------------------------------------------------------------

STRESS_RE = re.compile(STRESS)


def yaml_scalar(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def patch_field(content: str, field: str, new_value: str) -> str:
    """Replace the value of a YAML field in the fields: block."""
    pattern = re.compile(
        r"^(\s+" + re.escape(field) + r":\s*)(?:'(?:[^']|'')*'|\"(?:[^\\\"]|\\.)*\"|[^\n]*)\s*$",
        re.MULTILINE,
    )
    new_line = rf"\g<1>{yaml_scalar(new_value)}"
    result, count = pattern.subn(new_line, content)
    if count == 0:
        raise ValueError(f"Field '{field}' not found in note")
    return result


def patch_tag(content: str, old_tag: str, new_tag: str | None) -> str:
    """Remove old_tag line; if new_tag given, replace; else delete the line."""
    pattern = re.compile(r"^  - " + re.escape(old_tag) + r"\s*$\n", re.MULTILINE)
    if new_tag:
        replacement = f"  - {new_tag}\n"
    else:
        replacement = ""
    result, count = pattern.subn(replacement, content)
    if count == 0:
        # tag not present — noop
        pass
    return result


def fix_source_url(content: str, ascii_word: str) -> str:
    """Replace U+02BC apostrophe in Source_URL with ASCII apostrophe."""
    new_url = f"https://goroh.pp.ua/Словозміна/{ascii_word}"
    return patch_field(content, "Source_URL", new_url)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def process_note(path: Path, dry_run: bool) -> int:
    """Apply corrections to one note file. Returns number of changes made."""
    stem = path.stem
    corr = CORRECTIONS.get(stem)
    if not corr:
        return 0

    content = path.read_text(encoding="utf-8")
    original = content
    changes = 0

    # 1. Field corrections
    for field in ("Lemma", "Perfective", "ConfusableSet"):
        if field in corr:
            try:
                content = patch_field(content, field, corr[field])
                changes += 1
            except ValueError as e:
                print(f"  WARN {stem}: {e}")

    # 2. TypingAnswer = Lemma stripped of stress
    if "Lemma" in corr:
        typing = corr["Lemma"].replace(STRESS, "")
        try:
            content = patch_field(content, "TypingAnswer", typing)
            changes += 1
        except ValueError:
            pass

    # 3. Fix Source_URL for apostrophe verbs
    if "_source_url_word" in corr:
        content = fix_source_url(content, corr["_source_url_word"])
        changes += 1

    # 4. Remove stress:unverified tag
    content = patch_tag(content, "stress:unverified", None)

    # 5. Source_Note with verification date
    note_text = f"Stress verified {VERIFICATION_DATE} via Горох."
    try:
        content = patch_field(content, "Source_Note", note_text)
        changes += 1
    except ValueError:
        pass

    # 6. Add conjugation table if we have one
    if stem in CONJ_TABLES:
        try:
            content = patch_field(content, "Verb_Conj_Table", CONJ_TABLES[stem])
            changes += 1
        except ValueError as e:
            print(f"  WARN {stem}: Verb_Conj_Table — {e}")

    if content == original:
        print(f"  SKIP {stem}: no changes")
        return 0

    if dry_run:
        print(f"  DRY-RUN {stem}: {changes} change(s)")
    else:
        path.write_text(content, encoding="utf-8")
        print(f"  OK {stem}: {changes} change(s)")

    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    notes = sorted(CH09_DIR.glob("ua-lexeme-0*.md"))
    if not notes:
        print(f"No notes found in {CH09_DIR}")
        return

    total = 0
    for path in notes:
        total += process_note(path, args.dry_run)

    action = "Would apply" if args.dry_run else "Applied"
    print(f"\n{action} {total} correction(s) across {len(notes)} notes.")
    print("\nNotes with conjugation tables: 0114, 0115, 0116, 0123")
    if not args.dry_run:
        print("\nNext: make ua-batch BATCH=yabluko-l2/ch-09")


if __name__ == "__main__":
    main()
