#!/usr/bin/env python3
"""Compare every UA note type's live Anki model fields against this repo's
own FIELDS-style constants (the nominal source of truth for what
`setup_ua_note_types.py`/`setup_ua_pvom_note_type.py` push to AnkiConnect).

Written 2026-08-10 as part of the CNSF field-schema checker work (see
CLAUDE.md "UA Domain -- YAML/CNSF schema consistency" queue item). Those
FIELDS constants have already been caught stale relative to the live model
once before (missing `Verification Notes`/`Mnemonic_EN`/`CompareA`/
`CompareB` at the time -- see "Verb_Conj_Table Removal Plan" in CLAUDE.md),
so nothing downstream (the field-presence checker in particular) should
trust them blindly. This script is the reconciliation step: it imports the
constants directly (never a hardcoded copy, so it can't itself go stale) and
diffs each one against modelFieldNames from a live, running Anki + AnkiConnect.

Read-only -- makes no AnkiConnect calls that mutate anything (no
modelFieldAdd/Remove). If it finds drift, fixing setup_ua_note_types.py's
constants (or the live model, or a CNSF-generation bug like
cnsf_canonicalize.py injecting a field the model doesn't have) is a separate,
deliberate follow-up -- not something this script does for you.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/inspect/inspect_note_type_fields.py              # all 5 note types
    python tools/anki/inspect/inspect_note_type_fields.py --model UA_Lexeme
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402
from tools.anki.setup.setup_ua_note_types import (  # noqa: E402
    FIELDS as LEXEME_FIELDS,
    MODEL_NAME as LEXEME_MODEL,
    GRAMMAR_FIELDS,
    GRAMMAR_MODEL_NAME,
    VISUAL_FIELDS,
    VISUAL_MODEL_NAME,
    VERB_FIELDS,
    VERB_MODEL_NAME,
)
from tools.anki.setup.setup_ua_pvom_note_type import (  # noqa: E402
    FIELDS as PVOM_FIELDS,
    MODEL_NAME as PVOM_MODEL,
)

ANKI_URL = "http://127.0.0.1:8765"

# (model name, this repo's nominal FIELDS constant for it, source file for
# that constant -- shown in the report so drift is actionable, not just
# diagnosed)
NOTE_TYPES = [
    (LEXEME_MODEL, LEXEME_FIELDS, "tools/anki/setup/setup_ua_note_types.py:FIELDS"),
    (GRAMMAR_MODEL_NAME, GRAMMAR_FIELDS, "tools/anki/setup/setup_ua_note_types.py:GRAMMAR_FIELDS"),
    (VISUAL_MODEL_NAME, VISUAL_FIELDS, "tools/anki/setup/setup_ua_note_types.py:VISUAL_FIELDS"),
    (VERB_MODEL_NAME, VERB_FIELDS, "tools/anki/setup/setup_ua_note_types.py:VERB_FIELDS"),
    (PVOM_MODEL, PVOM_FIELDS, "tools/anki/setup/setup_ua_pvom_note_type.py:FIELDS"),
]


def check_one(model_name: str, constant_fields: list[str], constant_source: str) -> bool:
    """Print a report for one note type. Returns True if it matches exactly
    (same field set AND same order), False if there's any drift."""
    print(f"=== {model_name}  (constant: {constant_source}) ===")
    try:
        live_fields = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL)
    except Exception as e:
        print(f"  ERROR fetching live fields: {e}")
        return False

    if not live_fields:
        print(f"  ERROR: model {model_name!r} not found in Anki (or has no fields)")
        return False

    live_set = set(live_fields)
    constant_set = set(constant_fields)

    missing_from_constant = [f for f in live_fields if f not in constant_set]
    extra_in_constant = [f for f in constant_fields if f not in live_set]
    order_matches = live_fields == constant_fields

    clean = not missing_from_constant and not extra_in_constant and order_matches

    print(f"  Live model:  {len(live_fields)} fields")
    print(f"  Constant:    {len(constant_fields)} fields")

    if missing_from_constant:
        print(f"  MISSING FROM CONSTANT ({len(missing_from_constant)}) -- live Anki has these, "
              f"the constant doesn't -- every CNSF note that carries one of these keys is "
              f"correct and the constant is stale:")
        for f in missing_from_constant:
            print(f"    - {f}")

    if extra_in_constant:
        print(f"  EXTRA IN CONSTANT ({len(extra_in_constant)}) -- the constant claims these, "
              f"live Anki doesn't have them -- either a dead field the constant never dropped, "
              f"or the live model needs modelFieldAdd (a deliberate, separate decision):")
        for f in extra_in_constant:
            print(f"    - {f}")

    if not missing_from_constant and not extra_in_constant and not order_matches:
        print("  Field SETS match, but ORDER differs (cosmetic in the editor, harmless for sync):")
        print(f"    live:     {live_fields}")
        print(f"    constant: {constant_fields}")

    if clean:
        print("  OK -- constant matches live model exactly (set and order).")

    print()
    return clean


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diff each UA note type's FIELDS constant against its live Anki model."
    )
    parser.add_argument(
        "--model",
        choices=[m for m, _, _ in NOTE_TYPES],
        help="Check only this model (default: all 5)",
    )
    args = parser.parse_args()

    targets = [t for t in NOTE_TYPES if t[0] == args.model] if args.model else NOTE_TYPES

    all_clean = True
    for model_name, constant_fields, constant_source in targets:
        ok = check_one(model_name, constant_fields, constant_source)
        all_clean = all_clean and ok

    if all_clean:
        print("All checked note types match their FIELDS constants exactly.")
        return 0
    print("Drift found -- see MISSING FROM CONSTANT / EXTRA IN CONSTANT above. "
          "Not auto-fixed; decide the fix per-field (this often means the CNSF "
          "generation/canonicalization side needs a look too, not just the constant).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
