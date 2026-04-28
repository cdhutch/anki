#!/usr/bin/env python3
"""Create B737_SV_MCQ and B737_SV_TF note types in Anki as Standard (non-Cloze) types.

Creates each model with the correct fields, card template, and CSS styling in a
single createModel call. Idempotent: skips creation if the model already exists.

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

/* MCQ choices */
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

.choice-num {
  font-weight: bold;
  margin-right: 6px;
}

/* T/F prompt */
.tf-prompt {
  font-size: 15px;
  color: #555;
  font-style: italic;
  margin-top: -8px;
  margin-bottom: 4px;
}

/* Answer reveal (back of card) */
hr#answer {
  border: none;
  border-top: 2px solid #d0d0d0;
  margin: 22px 0;
}

.correct-answer {
  font-size: 18px;
  font-weight: bold;
  color: #1a6e1a;
  background-color: #eaf5ea;
  border-radius: 5px;
  padding: 12px 16px;
  text-align: center;
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
    "CorrectChoice",
]

MCQ_FRONT = """\
<div class="question">{{Text}}</div>
<div class="choices">
  <div class="choice"><span class="choice-num">1.</span>{{Choice1}}</div>
  <div class="choice"><span class="choice-num">2.</span>{{Choice2}}</div>
  <div class="choice"><span class="choice-num">3.</span>{{Choice3}}</div>
  <div class="choice"><span class="choice-num">4.</span>{{Choice4}}</div>
</div>
"""

MCQ_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="correct-answer">{{CorrectChoice}}</div>
"""

# ---------------------------------------------------------------------------
# B737_SV_TF
# ---------------------------------------------------------------------------

TF_FIELDS = [
    "NoteID",
    "Text",
    "Source Document",
    "OriginalNoteID",
    "CorrectAnswer",
]

TF_FRONT = """\
<div class="statement">{{Text}}</div>
<div class="tf-prompt">True or False?</div>
"""

TF_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="correct-answer">{{CorrectAnswer}}</div>
"""

# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_model(
    model_name: str,
    fields: list[str],
    template_name: str,
    front: str,
    back: str,
    css: str,
) -> None:
    # Check if model already exists
    existing = anki_request("modelNames", {}, url=ANKI_URL) or []
    if model_name in existing:
        print(f"  SKIP: {model_name} already exists.")
        return

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
    print(f"  OK: {model_name} created.")


def main() -> int:
    version = anki_request("version", {}, url=ANKI_URL)
    print(f"AnkiConnect version: {version}\n")

    print("Creating B737_SV_MCQ ...")
    create_model(
        model_name="B737_SV_MCQ",
        fields=MCQ_FIELDS,
        template_name="MCQ Card",
        front=MCQ_FRONT,
        back=MCQ_BACK,
        css=SHARED_CSS,
    )

    print("Creating B737_SV_TF ...")
    create_model(
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
