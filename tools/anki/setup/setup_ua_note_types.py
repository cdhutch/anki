#!/usr/bin/env python3
"""Create or update the UA_Lexeme note type in Anki via AnkiConnect.

If the model does not exist: creates it with all fields, card templates, and CSS.
If the model already exists: updates templates and CSS; syncs fields (adds missing,
removes obsolete). Existing data in removed fields is discarded.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_ua_note_types.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

# ---------------------------------------------------------------------------
# Fields (order matters — Anki displays them in this order in the editor)
# ---------------------------------------------------------------------------

FIELDS = [
    "NoteID",
    "Lemma",
    "PartOfSpeech",
    "Gender",
    "Perfective",
    "EN_Gloss",
    "Govt_Case",
    "CounterpartForm",
    "IrregularForms",
    "VerbMotion_Pair",
    "ConfusableSet",
    "CrossLang_Analog",
    "EuphonyNote",
    "TypingAnswer",
    "UA_Example",
    "EN_Example",
    "Verb_Conj_Table",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

.lemma {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.perfective {
  font-size: 22px;
  color: #555;
  margin-bottom: 8px;
}

.pos {
  font-size: 13px;
  color: #888;
  font-style: italic;
  margin-bottom: 16px;
}

.gender {
  font-size: 13px;
  color: #888;
  margin-bottom: 4px;
}

hr#answer {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 20px 0;
}

.gloss {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
}

.counterpart {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.irregular {
  font-size: 13px;
  color: #888;
  margin-top: 4px;
}

.confusable {
  font-size: 13px;
  color: #b07000;
  margin-top: 6px;
}

.example-ua {
  font-size: 15px;
  margin-top: 14px;
  font-style: italic;
  color: #333;
}

.example-en {
  font-size: 13px;
  color: #777;
  margin-top: 2px;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 16px;
}

.source-link {
  font-size: 11px;
  margin-top: 10px;
  text-align: right;
}

.source-link a {
  color: #aaa;
  text-decoration: none;
}

/* Typing card input */
input#typeans {
  font-size: 20px;
  font-family: 'Noto Sans', Arial, sans-serif;
  width: 80%;
  text-align: center;
}
"""

# ---------------------------------------------------------------------------
# Card templates
# ---------------------------------------------------------------------------

# Template 1: UA → EN  (Recognition: see Ukrainian, recall English)
UA_EN_FRONT = """\
<div class="lemma">{{Lemma}}</div>
{{#Perfective}}<div class="perfective">/ {{Perfective}}</div>{{/Perfective}}
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
"""

UA_EN_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="gloss">{{EN_Gloss}}</div>
{{#CounterpartForm}}<div class="counterpart">{{CounterpartForm}}</div>{{/CounterpartForm}}
{{#IrregularForms}}<div class="irregular">{{IrregularForms}}</div>{{/IrregularForms}}
{{#Govt_Case}}<div class="irregular">governs: {{Govt_Case}}</div>{{/Govt_Case}}
{{#ConfusableSet}}<div class="confusable">cf. {{ConfusableSet}}</div>{{/ConfusableSet}}
{{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
{{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""

# Template 2: EN → UA  (Production: see English, type Ukrainian without stress marks)
EN_UA_FRONT = """\
<div class="gloss">{{EN_Gloss}}</div>
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
{{type:TypingAnswer}}
"""

EN_UA_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="lemma">{{Lemma}}</div>
{{#Perfective}}<div class="perfective">/ {{Perfective}}</div>{{/Perfective}}
{{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
{{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""

CARD_TEMPLATES = [
    {"Name": "UA→EN",  "Front": UA_EN_FRONT, "Back": UA_EN_BACK},
    {"Name": "EN→UA",  "Front": EN_UA_FRONT, "Back": EN_UA_BACK},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_existing_models() -> list[str]:
    return anki_request("modelNames", url=ANKI_URL) or []


def create_model():
    print(f"Creating note type '{MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": MODEL_NAME,
            "inOrderFields": FIELDS,
            "css": CSS,
            "cardTemplates": CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_model():
    """Update templates and CSS; sync fields."""
    print(f"Updating note type '{MODEL_NAME}'...")

    # Update templates
    for tmpl in CARD_TEMPLATES:
        anki_request(
            "updateModelTemplates",
            {"model": {"name": MODEL_NAME, "templates": {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]}}}},
            url=ANKI_URL,
        )

    # Update CSS
    anki_request(
        "updateModelStyling",
        {"model": {"name": MODEL_NAME, "css": CSS}},
        url=ANKI_URL,
    )

    # Sync fields: add missing, remove obsolete
    existing_fields = anki_request("modelFieldNames", {"modelName": MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(FIELDS)

    for field in FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    print("  Updated.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    existing = get_existing_models()
    if MODEL_NAME in existing:
        update_model()
    else:
        create_model()
    print(f"\nDone. Note type '{MODEL_NAME}' is ready.")


if __name__ == "__main__":
    main()
