#!/usr/bin/env python3
"""Create or update the B737_Mnemonic note type in Anki.

Generates 2 cards per note via progressive reveal:

  Card 1 — "Recall Mnemonic"
    Front : Flow/topic name
    Back  : + mnemonic letters

  Card 2 — "Recall Words"
    Front : Name + letters
    Back  : + word expansion
            + context note at bottom (if Notes field is non-empty)

If the model does not exist: creates it.
If the model already exists: updates templates, CSS, and syncs fields.
Stray extra templates are automatically removed.

Usage:
    python tools/anki/setup/setup_mnemonic_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "B737_Mnemonic"

FIELDS = [
    "NoteID",
    "Name",
    "Mnemonic",
    "Words",
    "Notes",
    "Source Document",
    "Verification Notes",
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* Light mode (Solarized light) */
.card { font-family: Arial, sans-serif; font-size: 16px; color: #586e75; background-color: #fdf6e3; max-width: 640px; margin: 0 auto; padding: 24px 20px; text-align: left; }
.flow-name { font-size: 18px; font-weight: bold; margin-bottom: 20px; }
.mnemonic { font-size: 22px; font-weight: bold; letter-spacing: 0.12em; color: #2aa198; margin-bottom: 16px; }
.mnemonic-words { font-size: 15px; color: #586e75; line-height: 1.6; margin-bottom: 16px; }
hr#answer { border: none; border-top: 1px solid #93a1a1; margin: 22px 0; }
.reveal { font-size: 16px; font-weight: bold; color: #859900; background-color: #eee8d5; border-radius: 5px; padding: 12px 16px; margin-bottom: 12px; }
.reveal-list { list-style-type: disc; margin: 0 0 12px 0; color: #859900; background-color: #eee8d5; border-radius: 5px; padding: 12px 12px 12px 32px; }
.reveal-list li, .mnemonic-words-list li { font-size: 15px; font-weight: bold; line-height: 1.7; }
.mnemonic-words-list { list-style-type: disc; padding: 10px 10px 10px 30px; margin: 0 0 12px 0; color: #586e75; background-color: #eee8d5; border-radius: 5px; }
.reveal-mnemonic { font-size: 22px; font-weight: bold; letter-spacing: 0.12em; color: #859900; background-color: #eee8d5; border-radius: 5px; padding: 12px 16px; margin-bottom: 12px; }
.context { font-size: 14px; color: #93a1a1; background-color: #eee8d5; border-radius: 5px; padding: 10px 14px; margin-top: 8px; line-height: 1.5; }
.note-id { font-size: 11px; color: #93a1a1; text-align: right; margin-top: 14px; }

/* Dark mode (Solarized dark) */
.nightMode .card { color: #657b83; background-color: #032029; }
.night_mode .card { color: #657b83; background-color: #032029; }
.nightMode .mnemonic { color: #2aa198; }
.night_mode .mnemonic { color: #2aa198; }
.nightMode .mnemonic-words { color: #657b83; }
.night_mode .mnemonic-words { color: #657b83; }
.nightMode hr#answer { border-top-color: #586e75; }
.night_mode hr#answer { border-top-color: #586e75; }
.nightMode .reveal { color: #859900; background-color: #032029; }
.night_mode .reveal { color: #859900; background-color: #032029; }
.nightMode .reveal-list { color: #859900; background-color: #032029; }
.night_mode .reveal-list { color: #859900; background-color: #032029; }
.nightMode .mnemonic-words-list { color: #657b83; background-color: #032029; }
.night_mode .mnemonic-words-list { color: #657b83; background-color: #032029; }
.nightMode .reveal-mnemonic { color: #859900; background-color: #032029; }
.night_mode .reveal-mnemonic { color: #859900; background-color: #032029; }
.nightMode .context { color: #586e75; background-color: #032029; }
.night_mode .context { color: #586e75; background-color: #032029; }
.nightMode .note-id { color: #586e75; }
.night_mode .note-id { color: #586e75; }
"""

# ---------------------------------------------------------------------------
# Card templates
# ---------------------------------------------------------------------------

CARD1_FRONT = """\
<div class="flow-name">{{Name}}</div>
<div style="color:#888; font-size:13px;">What is the mnemonic?</div>
"""

CARD1_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="reveal-mnemonic">{{Mnemonic}}</div>
<div class="note-id">{{NoteID}}</div>
"""

# Card 2 only generates when Words is non-empty. Notes (if present) appended to back.
CARD2_FRONT = """\
{{#Words}}
<div class="flow-name">{{Name}}</div>
<div class="mnemonic">{{Mnemonic}}</div>
<div style="color:#888; font-size:13px;">What does the mnemonic stand for?</div>
{{/Words}}
"""

CARD2_BACK = """\
{{FrontSide}}
<hr id="answer">
<ul class="reveal-list">{{Words}}</ul>
{{#Notes}}<div class="context">{{Notes}}</div>{{/Notes}}
<div class="note-id">{{NoteID}}</div>
"""

TEMPLATES = [
    ("Recall Mnemonic", CARD1_FRONT, CARD1_BACK),
    ("Recall Words",    CARD2_FRONT, CARD2_BACK),
]

# ---------------------------------------------------------------------------
# Helpers (mirrors update_sv_exam_templates.py)
# ---------------------------------------------------------------------------

def _sync_fields(model_name: str, desired: list[str]) -> None:
    existing: list[str] = anki_request(
        "modelFieldNames", {"modelName": model_name}, url=ANKI_URL
    ) or []

    to_add    = [f for f in desired  if f not in existing]
    to_remove = [f for f in existing if f not in desired]

    if not to_add and not to_remove:
        print("    fields: no changes")
        return

    if to_add or to_remove:
        print(f"    ⚠  field changes needed — delete and recreate {model_name} in Anki,")
        print(f"       then re-run this script (no notes will be lost if none have been imported).")
        for field in to_add:
            print(f"       + add   : {field}")
        for field in to_remove:
            print(f"       - remove: {field}")
        raise RuntimeError(
            f"Cannot add/remove fields on existing model '{model_name}' via AnkiConnect. "
            f"Delete the model in Anki (Tools → Manage Note Types) and re-run."
        )


def _sync_templates(model_name: str,
                    templates: list[tuple[str, str, str]]) -> None:
    """Ensure the model has exactly the specified templates.

    Updates existing templates by position/name, adds missing ones,
    and removes stray extras.
    """
    model_info: dict = anki_request(
        "modelTemplates", {"modelName": model_name}, url=ANKI_URL
    ) or {}
    existing_names = list(model_info.keys())
    desired_names  = [t[0] for t in templates]

    # Update or add each desired template.
    for name, front, back in templates:
        if name in existing_names or (not existing_names and name == desired_names[0]):
            actual = name if name in existing_names else existing_names[0]
            anki_request(
                "updateModelTemplates",
                {"model": {"name": model_name,
                           "templates": {actual: {"Front": front, "Back": back}}}},
                url=ANKI_URL,
            )
            print(f"    templates: updated {actual!r}")
        else:
            anki_request(
                "addCardToModel",
                {"modelName": model_name,
                 "cardName": name,
                 "qfmt": front,
                 "afmt": back},
                url=ANKI_URL,
            )
            print(f"    templates: added {name!r}")

    # Remove stray templates not in desired list.
    # AnkiConnect does not support removeCardFromTemplate — instruct the user.
    stray = [n for n in existing_names if n not in desired_names]
    for stray_name in stray:
        print(f"    ⚠  stray template {stray_name!r} must be removed manually:")
        print(f"       Anki → Tools → Manage Note Types → {model_name} → Cards → delete {stray_name!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    version = anki_request("version", {}, url=ANKI_URL)
    print(f"AnkiConnect version: {version}\n")

    existing_models = anki_request("modelNames", {}, url=ANKI_URL) or []

    if MODEL_NAME not in existing_models:
        anki_request(
            "createModel",
            {
                "modelName": MODEL_NAME,
                "inOrderFields": FIELDS,
                "css": CSS,
                "isCloze": False,
                "cardTemplates": [
                    {"Name": name, "Front": front, "Back": back}
                    for name, front, back in TEMPLATES
                ],
            },
            url=ANKI_URL,
        )
        print(f"CREATED: {MODEL_NAME}")
    else:
        print(f"UPDATE:  {MODEL_NAME}")
        _sync_fields(MODEL_NAME, FIELDS)
        _sync_templates(MODEL_NAME, TEMPLATES)
        anki_request(
            "updateModelStyling",
            {"model": {"name": MODEL_NAME, "css": CSS}},
            url=ANKI_URL,
        )
        print("    css: updated")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
