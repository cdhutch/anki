#!/usr/bin/env python3
"""Create or update the B737_Checklist note type in Anki.

Generates 1 card per note (Challenge / Challenge+Response).

  Front — challenge-only table (tests recall without showing answers)
  Back  — full two-column challenge / response table

If the model does not exist: creates it.
If the model already exists: updates templates, CSS, and syncs fields.

Usage:
    python tools/anki/setup/setup_checklist_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL   = "http://127.0.0.1:8765"
MODEL_NAME = "B737_Checklist"

FIELDS = [
    "NoteID",
    "ChecklistName",
    "Front",
    "Back",
    "Source Document",
    "Verification Notes",
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* Light mode (Solarized light) */
.card {
  font-family: Arial, sans-serif;
  font-size: 16px;
  color: #586e75;
  background-color: #fdf6e3;
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: left;
}

.checklist-name {
  font-size: 18px;
  font-weight: bold;
  color: #2aa198;
  margin-bottom: 16px;
}

table { width: 100%; border-collapse: collapse; font-size: 15px; margin-top: 4px; }
th { background-color: #2aa198; color: #fdf6e3; padding: 8px 14px; text-align: left; font-weight: bold; letter-spacing: 0.03em; }
td { padding: 7px 14px; border-bottom: 1px solid #93a1a1; vertical-align: top; }
tr:nth-child(even) td { background-color: #eee8d5; }

td:first-child { font-weight: 600; width: 50%; }
td:last-child { color: #2aa198; }

tr.sol-hi td { background-color: #cce9e7; }

.note-id { font-size: 11px; color: #93a1a1; text-align: right; margin-top: 14px; }

/* Dark mode (Solarized dark) */
.nightMode .card { color: #657b83; background-color: #032029; }
.night_mode .card { color: #657b83; background-color: #032029; }
.nightMode .checklist-name { color: #2aa198; }
.night_mode .checklist-name { color: #2aa198; }
.nightMode th { background-color: #2aa198; color: #002b36; }
.night_mode th { background-color: #2aa198; color: #002b36; }
.nightMode td { border-bottom-color: #586e75; }
.night_mode td { border-bottom-color: #586e75; }
.nightMode tr:nth-child(even) td { background-color: #032029; }
.night_mode tr:nth-child(even) td { background-color: #032029; }
.nightMode td:last-child { color: #2aa198; }
.night_mode td:last-child { color: #2aa198; }
.nightMode tr.sol-hi td { background-color: #0d3d45; }
.night_mode tr.sol-hi td { background-color: #0d3d45; }
.nightMode .note-id { color: #586e75; }
.night_mode .note-id { color: #586e75; }
"""

# ---------------------------------------------------------------------------
# Card templates
# ---------------------------------------------------------------------------

CARD_FRONT = """\
<div class="checklist-name">{{ChecklistName}}</div>
{{Front}}
"""

CARD_BACK = """\
<div class="checklist-name">{{ChecklistName}}</div>
{{Back}}
<div class="note-id">{{NoteID}}</div>
"""

TEMPLATES = [
    ("Challenge / Response", CARD_FRONT, CARD_BACK),
]

# ---------------------------------------------------------------------------
# Helpers
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
    model_info: dict = anki_request(
        "modelTemplates", {"modelName": model_name}, url=ANKI_URL
    ) or {}
    existing_names = list(model_info.keys())
    desired_names  = [t[0] for t in templates]

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

    print("\nDone. Run create_checklists_preset.py next to set up the deck preset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
