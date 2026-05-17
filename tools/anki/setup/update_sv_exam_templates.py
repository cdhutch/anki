#!/usr/bin/env python3
"""Create or update B737_SV_MCQ and B737_SV_TF note types in Anki.

If the model does not exist: creates it with the correct fields, card template,
and CSS styling in a single createModel call.

If the model already exists: updates templates, CSS, and syncs fields
(adds missing fields, removes obsolete fields). Existing note data in fields
that are being removed is discarded — re-import from TSV after running this.

Usage:
    python tools/anki/setup/update_sv_exam_templates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# Shared CSS
# ---------------------------------------------------------------------------

SHARED_CSS = """\
.card {
  font-family: Arial, sans-serif;
  font-size: 16px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: left;
}

.question,
.statement {
  font-size: 18px;
  font-weight: bold;
  line-height: 1.5;
  margin-bottom: 20px;
}

/* MCQ / T/F choices */
.choices {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.choice {
  padding: 9px 14px;
  background-color: #f2f4f6;
  border-radius: 5px;
  line-height: 1.4;
}

.choice-label {
  font-weight: bold;
  margin-right: 6px;
}

/* Answer reveal (back of card) */
hr#answer {
  border: none;
  border-top: 2px solid #d0d0d0;
  margin: 22px 0;
}

.answer-table {
  width: 100%;
  border-collapse: collapse;
}

.answer-letter {
  font-size: 20px;
  font-weight: bold;
  color: #1a6e1a;
  background-color: #eaf5ea;
  border-radius: 5px 0 0 5px;
  padding: 12px 16px;
  text-align: center;
  width: 48px;
  vertical-align: middle;
}

.answer-text {
  font-size: 16px;
  font-weight: bold;
  color: #1a6e1a;
  background-color: #eaf5ea;
  border-radius: 0 5px 5px 0;
  padding: 12px 16px;
  vertical-align: middle;
}

.note-id {
  font-size: 11px;
  color: #aaa;
  text-align: right;
  margin-top: 14px;
}
"""

# ---------------------------------------------------------------------------
# B737_SV_MCQ
# ---------------------------------------------------------------------------

MCQ_FIELDS = [
    "NoteID",
    "Text",
    "Source Document",
    "OriginalNoteID",
    "Choice1",
    "Choice2",
    "Choice3",
    "Choice4",
    "CorrectLetter",
    "CorrectText",
]

MCQ_FRONT = """\
<div class="question">{{Text}}</div>
<div class="choices">
  <div class="choice"><span class="choice-label">A.</span>{{Choice1}}</div>
  <div class="choice"><span class="choice-label">B.</span>{{Choice2}}</div>
  {{#Choice3}}<div class="choice"><span class="choice-label">C.</span>{{Choice3}}</div>{{/Choice3}}
  {{#Choice4}}<div class="choice"><span class="choice-label">D.</span>{{Choice4}}</div>{{/Choice4}}
</div>
"""

MCQ_BACK = """\
{{FrontSide}}
<hr id="answer">
<table class="answer-table">
  <tr>
    <td class="answer-letter">{{CorrectLetter}}</td>
    <td class="answer-text">{{CorrectText}}</td>
  </tr>
</table>
<div class="note-id">{{NoteID}}</div>
"""

# ---------------------------------------------------------------------------
# B737_SV_TF
# ---------------------------------------------------------------------------

TF_FIELDS = [
    "NoteID",
    "Text",
    "Source Document",
    "OriginalNoteID",
    "CorrectLetter",
    "CorrectText",
]

TF_FRONT = """\
<div class="statement">{{Text}}</div>
<div class="choices">
  <div class="choice"><span class="choice-label">A.</span>True</div>
  <div class="choice"><span class="choice-label">B.</span>False</div>
</div>
"""

TF_BACK = """\
{{FrontSide}}
<hr id="answer">
<table class="answer-table">
  <tr>
    <td class="answer-letter">{{CorrectLetter}}</td>
    <td class="answer-text">{{CorrectText}}</td>
  </tr>
</table>
<div class="note-id">{{NoteID}}</div>
"""

# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def _sync_fields(model_name: str, desired: list[str]) -> None:
    """Add fields missing from the model; remove fields no longer needed."""
    current = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL) or []
    current_set = set(current)
    desired_set = set(desired)

    to_add = [f for f in desired if f not in current_set]
    to_remove = [f for f in current if f not in desired_set]

    for field in to_add:
        anki_request("modelFieldAdd", {"modelName": model_name, "fieldName": field}, url=ANKI_URL)
        print(f"    + field: {field}")

    for field in to_remove:
        anki_request("modelFieldRemove", {"modelName": model_name, "fieldName": field}, url=ANKI_URL)
        print(f"    - field: {field}")

    if not to_add and not to_remove:
        print("    fields: no changes")


def sync_model(
    model_name: str,
    fields: list[str],
    template_name: str,
    front: str,
    back: str,
    css: str,
) -> None:
    existing = anki_request("modelNames", {}, url=ANKI_URL) or []

    if model_name not in existing:
        anki_request(
            "createModel",
            {
                "modelName": model_name,
                "inOrderFields": fields,
                "css": css,
                "isCloze": False,
                "cardTemplates": [
                    {
                        "Name": template_name,
                        "Front": front,
                        "Back": back,
                    }
                ],
            },
            url=ANKI_URL,
        )
        print(f"  CREATED: {model_name}")
        return

    print(f"  UPDATE:  {model_name}")
    _sync_fields(model_name, fields)

    # Discover the actual template name Anki is using (may differ from our
    # desired name, e.g. Anki defaults to "Card 1" on first createModel).
    model_info = anki_request("modelTemplates", {"modelName": model_name}, url=ANKI_URL) or {}
    existing_template_names = list(model_info.keys())
    if template_name in existing_template_names:
        actual_template_name = template_name
    elif existing_template_names:
        actual_template_name = existing_template_names[0]
        print(f"    template name in Anki is {actual_template_name!r}, not {template_name!r} — using existing name")
    else:
        actual_template_name = template_name
        print(f"    warning: could not determine template name, trying {template_name!r}")

    anki_request(
        "updateModelTemplates",
        {
            "model": {
                "name": model_name,
                "templates": {actual_template_name: {"Front": front, "Back": back}},
            }
        },
        url=ANKI_URL,
    )
    print(f"    templates: updated ({actual_template_name!r})")
    anki_request(
        "updateModelStyling",
        {"model": {"name": model_name, "css": css}},
        url=ANKI_URL,
    )
    print(f"    css: updated")


def main() -> int:
    version = anki_request("version", {}, url=ANKI_URL)
    print(f"AnkiConnect version: {version}\n")

    print("Syncing B737_SV_MCQ ...")
    sync_model(
        model_name="B737_SV_MCQ",
        fields=MCQ_FIELDS,
        template_name="MCQ Card",
        front=MCQ_FRONT,
        back=MCQ_BACK,
        css=SHARED_CSS,
    )

    print("Syncing B737_SV_TF ...")
    sync_model(
        model_name="B737_SV_TF",
        fields=TF_FIELDS,
        template_name="TF Card",
        front=TF_FRONT,
        back=TF_BACK,
        css=SHARED_CSS,
    )

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
