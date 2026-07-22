#!/usr/bin/env python3
"""
gen_ua_lexemes_l2_ch09.py

One-shot generator for ua-lexeme CNSF notes covering Book 2, Chapter 9:
Prefixed Verbs of Motion (§9.4), Яблуко textbook.

Outputs:
  domains/ua/anki/notes/lexemes/yabluko-l2/ch-09/ua-lexeme-NNNN.md
  18 notes total: 9 walking (іти / ходити pairs) + 9 vehicle (їхати / їздити pairs)
  NoteIDs: ua-lexeme-0114 through ua-lexeme-0131

All notes are tagged:
  - stress:unverified  (run Горох verification pass after generation)
  - status:draft       (switch to status:verified after stress + content review)

Usage:
    python tools/anki/extract/gen_ua_lexemes_l2_ch09.py [--dry-run]
"""

from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "domains/ua/anki/notes/lexemes/yabluko-l2/ch-09"

STRESS = "́"       # U+0301 COMBINING ACUTE ACCENT
APOSTROPHE = "ʼ"   # U+02BC MODIFIER LETTER APOSTROPHE (Ukrainian)


def strip_stress(s: str) -> str:
    return s.replace(STRESS, "")


def yaml_scalar(s: str) -> str:
    """Return s as a single-quoted YAML scalar, escaping embedded ' by doubling."""
    return "'" + s.replace("'", "''") + "'"


# ---------------------------------------------------------------------------
# Verb data
# Each tuple: (note_num, ipfv, pfv, en_gloss, govt_case,
#              verb_motion_pair, confusable, cross_lang_analog, euphony_note)
#
# Walking verbs (іти / ходити):
#   IPFV stress on -ди- is standard; marked with U+0301.
#   PFV stress on final -ти confirmed by standard paradigm; marked.
#   All tagged stress:unverified for Горох confirmation.
#
# Vehicle verbs (їхати / їздити):
#   IPFV -іжджати stress on -жа- marked.
#   PFV -їхати stress NOT marked — needs Горох verification before adding.
# ---------------------------------------------------------------------------

WALKING_VERBS = [
    # (num, ipfv, pfv, en_gloss, govt_case, vmp, confusable, cross_lang, euphony)
    (
        114,
        "приходи́ти", "прийти́",
        "to come, arrive (on foot)",
        "до + Gen",
        "іти / ходити",
        "відходи́ти",
        "≈ RU: приходить / прийти",
        "",
    ),
    (
        115,
        "входи́ти", "увійти́",
        "to enter, go in (on foot)",
        "в/у + Acc",
        "іти / ходити",
        "виходи́ти",
        "≈ RU: входить / войти",
        "PFV: в- + іти → увійти (also ввійти); у- preferred before й",
    ),
    (
        116,
        "виходи́ти", "вийти́",
        "to go out, exit (on foot)",
        "з + Gen",
        "іти / ходити",
        "входи́ти",
        "≈ RU: выходить / выйти",
        "",
    ),
    (
        117,
        "підходи́ти", "підійти́",
        "to approach, walk up to (on foot)",
        "до + Gen",
        "іти / ходити",
        "доходи́ти",
        "≈ RU: подходить / подойти (під- ≈ под-)",
        "PFV: під- + іти → підійти (epenthetic и before й)",
    ),
    (
        118,
        "відходи́ти", "відійти́",
        "to walk away, leave (on foot)",
        "від + Gen",
        "іти / ходити",
        "приходи́ти",
        "≈ RU: отходить / отойти (від- ≈ от-)",
        "PFV: від- + іти → відійти (epenthetic и before й)",
    ),
    (
        119,
        "доходи́ти", "дійти́",
        "to reach, get to (on foot)",
        "до + Gen",
        "іти / ходити",
        "підходи́ти",
        "≈ RU: доходить / дойти (до- + іти → дійти)",
        "PFV: до- + іти → дійти (о drops before й)",
    ),
    (
        120,
        "проходи́ти", "пройти́",
        "to walk past, pass through (on foot)",
        "через / повз + Acc",
        "іти / ходити",
        "переходи́ти",
        "≈ RU: проходить / пройти",
        "",
    ),
    (
        121,
        "переходи́ти", "перейти́",
        "to cross, go across (on foot)",
        "через + Acc",
        "іти / ходити",
        "проходи́ти",
        "≈ RU: переходить / перейти",
        "",
    ),
    (
        122,
        "заходи́ти", "зайти́",
        "to stop by, drop in (on foot)",
        "до + Gen; в/у + Acc",
        "іти / ходити",
        "заїжджа́ти",
        "≈ RU: заходить / зайти",
        "",
    ),
]

# Vehicle PFV forms: stress NOT marked — pending Горох verification.
VEHICLE_VERBS = [
    (
        123,
        "приїжджа́ти", "приїхати",
        "to arrive (by vehicle)",
        "до + Gen",
        "їхати / їздити",
        "приходи́ти",
        "≈ RU: приезжать / приехать",
        "",
    ),
    (
        124,
        "вʼїжджа́ти", "вʼїхати",
        "to drive in/into (by vehicle)",
        "в/у + Acc",
        "їхати / їздити",
        "виїжджа́ти",
        "≈ RU: въезжать / въехать (ʼ corresponds to RU ъ)",
        "apostrophe after в- before ї: вʼїхати; cf. RU въехать",
    ),
    (
        125,
        "виїжджа́ти", "виїхати",
        "to drive out (by vehicle)",
        "з + Gen",
        "їхати / їздити",
        "вʼїжджа́ти",
        "≈ RU: выезжать / выехать",
        "",
    ),
    (
        126,
        "підʼїжджа́ти", "підʼїхати",
        "to drive up to (by vehicle)",
        "до + Gen",
        "їхати / їздити",
        "доїжджа́ти",
        "≈ RU: подъезжать / подъехать (ʼ corresponds to RU ъ)",
        "apostrophe after під- before ї: підʼїхати",
    ),
    (
        127,
        "відʼїжджа́ти", "відʼїхати",
        "to drive away (by vehicle)",
        "від + Gen",
        "їхати / їздити",
        "",
        "≈ RU: отъезжать / отъехать (ʼ corresponds to RU ъ)",
        "apostrophe after від- before ї: відʼїхати",
    ),
    (
        128,
        "доїжджа́ти", "доїхати",
        "to reach, get to (by vehicle)",
        "до + Gen",
        "їхати / їздити",
        "підʼїжджа́ти",
        "≈ RU: доезжать / доехать",
        "",
    ),
    (
        129,
        "проїжджа́ти", "проїхати",
        "to drive past, pass through (by vehicle)",
        "через / повз + Acc",
        "їхати / їздити",
        "переїжджа́ти",
        "≈ RU: проезжать / проехать",
        "",
    ),
    (
        130,
        "переїжджа́ти", "переїхати",
        "to cross (by vehicle); to relocate",
        "через + Acc",
        "їхати / їздити",
        "проїжджа́ти",
        "≈ RU: переезжать / переехать",
        "",
    ),
    (
        131,
        "заїжджа́ти", "заїхати",
        "to stop by (by vehicle)",
        "до + Gen; в/у + Acc",
        "їхати / їздити",
        "заходи́ти",
        "≈ RU: заезжать / заехать",
        "",
    ),
]


# ---------------------------------------------------------------------------
# Note template
# ---------------------------------------------------------------------------


def make_note(
    num: int,
    ipfv: str,
    pfv: str,
    en_gloss: str,
    govt_case: str,
    verb_motion_pair: str,
    confusable: str,
    cross_lang: str,
    euphony: str,
) -> str:
    note_id = f"ua-lexeme-{num:04d}"
    typing_answer = strip_stress(ipfv)
    bare_lemma = strip_stress(ipfv)
    source_url = f"https://goroh.pp.ua/Словозміна/{bare_lemma}"

    lines = [
        "---",
        "schema: cnsf/v0",
        "note_type: ua_lexeme",
        f"note_id: {note_id}",
        "anki:",
        "  model: UA_Lexeme",
        "  deck: UA::Recognition::UA→EN",
        "tags:",
        "  - domain:ua",
        "  - topic:vocabulary",
        "  - textbook:яблуко",
        "  - ch:2.9.4",
        "  - pos:verb",
        "  - motion:prefixed",
        "  - stress:unverified",
        "  - status:draft",
        "fields:",
        f"  NoteID: {note_id}",
        f"  Lemma: {yaml_scalar(ipfv)}",
        "  PartOfSpeech: verb",
        "  Gender: ''",
        f"  Perfective: {yaml_scalar(pfv)}",
        f"  EN_Gloss: {yaml_scalar(en_gloss)}",
        f"  Govt_Case: {yaml_scalar(govt_case)}",
        "  CounterpartForm: ''",
        "  IrregularForms: ''",
        f"  VerbMotion_Pair: {yaml_scalar(verb_motion_pair)}",
        f"  ConfusableSet: {yaml_scalar(confusable)}",
        f"  CrossLang_Analog: {yaml_scalar(cross_lang)}",
        f"  EuphonyNote: {yaml_scalar(euphony)}",
        f"  TypingAnswer: {yaml_scalar(typing_answer)}",
        "  UA_Example: ''",
        "  EN_Example: ''",
        "  Verb_Conj_Table: ''",
        "  Tags_Ch: ch:2.9.4",
        f"  Source_URL: {yaml_scalar(source_url)}",
        "  Source_Note: 'stress:unverified — verify via Горох before switching to status:verified'",
        "---",
        "",  # trailing newline
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print filenames only; don't write")
    args = parser.parse_args()

    all_verbs = WALKING_VERBS + VEHICLE_VERBS

    if not args.dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    for row in all_verbs:
        num, ipfv, pfv, en_gloss, govt_case, vmp, confusable, cross_lang, euphony = row
        note_id = f"ua-lexeme-{num:04d}"
        content = make_note(num, ipfv, pfv, en_gloss, govt_case, vmp, confusable, cross_lang, euphony)
        path = OUT_DIR / f"{note_id}.md"

        if args.dry_run:
            print(f"  DRY-RUN: {path.name}  {ipfv} / {pfv}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  OK: {path.name}  {ipfv} / {pfv}")

    if not args.dry_run:
        print(f"\nCreated {len(all_verbs)} notes in {OUT_DIR.relative_to(REPO_ROOT)}")
        print("\nNext steps:")
        print("  1. Run Горох stress verification: make ua-stress")
        print("  2. Review and approve notes")
        print("  3. Switch tags from status:draft → status:verified")
        print("  4. Import: make ua-batch BATCH=yabluko-l2/ch-09")


if __name__ == "__main__":
    main()
