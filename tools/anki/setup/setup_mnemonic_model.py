#!/usr/bin/env python3
"""Create or update the B737_Mnemonic note type in Anki.

Generates 3 cards per note via progressive reveal:

  Card 1 — "Recall Letters"
    Front : Flow/topic name
    Back  : + mnemonic letters

  Card 2 — "Recall Words"
    Front : Name + letters
    Back  : + word expansion

  Card 3 — "Recall Context"  (only generated when Notes field is non-empty)
    Front : Name + letters + words
    Back  : + notes / context

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
/* Solarized palette */
:root {
  --sol-bg:      #fdf6e3;
  --sol-bg-alt:  #eee8d5;
  --sol-text:    #586e75;
  --sol-sub:     #93a1a1;
  --sol-border:  #93a1a1;
  --sol-accent:  #2aa198;
  --sol-acc-fg:  #fdf6e3;
  --sol-green:   #859900;
  --sol-green-bg:#eee8d5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --sol-bg:      #002b36;
    --sol-bg-alt:  #073642;
    --sol-text:    #839496;
    --sol-sub:     #586e75;
    --sol-border:  #586e75;
    --sol-accent:  #2aa198;
    --sol-acc-fg:  #002b36;
    --sol-green:   #859900;
    --sol-green-bg:#073642;
  }
}

.card {
  font-family: Arial, sans-serif;
  font-size: 16px;
  color: var(--sol-text);
  background-color: var(--sol-bg);
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: left;
}

.flow-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
}

.mnemonic {
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 0.12em;
  color: var(--sol-accent);
  margin-bottom: 16px;
}

.mnemonic-words {
  font-size: 15px;
  color: var(--sol-text);
  line-height: 1.6;
  margin-bottom: 16px;
}

hr#answer {
  border: none;
  border-top: 1px solid var(--sol-border);
  margin: 22px 0;
}

.reveal {
  font-size: 16px;
  font-weight: bold;
  color: var(--sol-green);
  background-color: var(--sol-green-bg);
  border-radius: 5px;
  padding: 12px 16px;
  margin-bottom: 12px;
}

.reveal-list {
  list-style-type: disc;
  margin: 0 0 12px 0;
  color: var(--sol-green);
  background-color: var(--sol-green-bg);
  border-radius: 5px;
  padding: 12px 12px 12px 32px;
}

.reveal-list li,
.mnemonic-words-list li {
  font-size: 15px;
  font-weight: bold;
  line-height: 1.7;
}

.mnemonic-words-list {
  list-style-type: disc;
  padding: 10px 10px 10px 30px;
  margin: 0 0 12px 0;
  color: var(--sol-text);
  background-color: var(--sol-bg-alt);
  border-radius: 5px;
}

.reveal-mnemonic {
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 0.12em;
  color: var(--sol-green);
  background-color: var(--sol-green-bg);
  border-radius: 5px;
  padding: 12px 16px;
  margin-bottom: 12px;
}

.context {
  font-size: 14px;
  color: var(--sol-sub);
  background-color: var(--sol-bg-alt);
  border-radius: 5px;
  padding: 10px 14px;
  margin-top: 8px;
  line-height: 1.5;
}

.note-id {
  font-size: 11px;
  color: var(--sol-sub);
  text-align: right;
  margin-top: 14px;
}
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

# Card 2 only generates when Words is non-empty.
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
<div class="note-id">{{NoteID}}</div>
"""

# Card 3 only generates when Notes is non-empty.
CARD3_FRONT = """\
{{#Notes}}
<div class="flow-name">{{Name}}</div>
<div class="mnemonic">{{Mnemonic}}</div>
<ul class="mnemonic-words-list">{{Words}}</ul>
<div style="color:#888; font-size:13px;">Any additional context?</div>
{{/Notes}}
"""

CARD3_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="context">{{Notes}}</div>
<div class="note-id">{{NoteID}}</div>
"""

TEMPLATES = [
    ("Recall Mnemonic", CARD1_FRONT, CARD1_BACK),
    ("Recall Words",    CARD2_FRONT, CARD2_BACK),
    ("Recall Context",  CARD3_FRONT, CARD3_BACK),
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
    stray = [n for n in existing_names if n not in desired_names]
    for stray_name in stray:
        print(f"    ⚠  removing stray template {stray_name!r} ...")
        anki_request(
            "removeCardFromTemplate",
            {"modelName": model_name, "templateName": stray_name},
            url=ANKI_URL,
        )
        print(f"    ✓  removed {stray_name!r}")


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
