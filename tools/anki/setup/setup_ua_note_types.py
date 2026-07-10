#!/usr/bin/env python3
"""Create or update UA_Lexeme and UA_Grammar note types in Anki via AnkiConnect.

If a model does not exist: creates it with all fields, card templates, and CSS.
If a model already exists: updates templates and CSS; syncs fields (adds missing,
removes obsolete). Existing data in removed fields is discarded.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_ua_note_types.py              # both models
    python tools/anki/setup/setup_ua_note_types.py --model UA_Lexeme
    python tools/anki/setup/setup_ua_note_types.py --model UA_Grammar
"""
from __future__ import annotations

import argparse
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

/* Conjugation table */
.conj {
  width: 100%;
  border-collapse: collapse;
  margin-top: 6px;
  font-size: 14px;
  text-align: left;
}
.conj th, .conj td {
  padding: 4px 8px;
  border: 1px solid #ddd;
}
.conj th {
  background-color: #f0f0f0;
  font-weight: 600;
  color: #444;
}
.conj td:first-child {
  color: #888;
  font-size: 12px;
  width: 6em;
}

/* Collapsible wrapper */
details.conj-wrap {
  margin-top: 16px;
  text-align: left;
}
details.conj-wrap summary {
  font-size: 13px;
  color: #888;
  cursor: pointer;
  user-select: none;
  list-style: none;
}
details.conj-wrap summary::before {
  content: '▶ ';
  font-size: 10px;
}
details.conj-wrap[open] summary::before {
  content: '▼ ';
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
{{#Verb_Conj_Table}}<details class="conj-wrap"><summary>Conjugation</summary>{{Verb_Conj_Table}}</details>{{/Verb_Conj_Table}}
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
{{#Verb_Conj_Table}}<details class="conj-wrap"><summary>Conjugation</summary>{{Verb_Conj_Table}}</details>{{/Verb_Conj_Table}}
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

    # Update templates — build single dict with all templates, then call once
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": MODEL_NAME, "templates": templates_dict}},
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
# UA_Grammar — Cloze note type for grammar rules
# ---------------------------------------------------------------------------

GRAMMAR_MODEL_NAME = "UA_Grammar"

GRAMMAR_FIELDS = [
    "NoteID",
    "Topic",
    "Text",
    "Extra",
    "SourceDocument",
    "Chapter",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

GRAMMAR_CSS = """\
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 20px;
}

.topic {
  font-size: 13px;
  color: #888;
  font-style: italic;
  margin-bottom: 14px;
}

.cloze {
  font-weight: bold;
  color: #2563eb;
}

.extra {
  font-size: 14px;
  color: #555;
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 10px;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 16px;
}

.chapter {
  font-size: 11px;
  color: #aaa;
  text-align: right;
}
"""

GRAMMAR_FRONT = """\
<div class="topic">{{Topic}}</div>
{{cloze:Text}}
"""

GRAMMAR_BACK = """\
<div class="topic">{{Topic}}</div>
{{cloze:Text}}
{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}
<div class="note-id">{{NoteID}}</div>
{{#Chapter}}<div class="chapter">§{{Chapter}}</div>{{/Chapter}}
"""

GRAMMAR_CARD_TEMPLATES = [
    {"Name": "Cloze", "Front": GRAMMAR_FRONT, "Back": GRAMMAR_BACK},
]


def create_grammar_model():
    print(f"Creating note type '{GRAMMAR_MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": GRAMMAR_MODEL_NAME,
            "inOrderFields": GRAMMAR_FIELDS,
            "css": GRAMMAR_CSS,
            "isCloze": True,
            "cardTemplates": GRAMMAR_CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_grammar_model():
    print(f"Updating note type '{GRAMMAR_MODEL_NAME}'...")

    # Update templates — build single dict with all templates, then call once
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in GRAMMAR_CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": GRAMMAR_MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    anki_request(
        "updateModelStyling",
        {"model": {"name": GRAMMAR_MODEL_NAME, "css": GRAMMAR_CSS}},
        url=ANKI_URL,
    )

    existing_fields = anki_request("modelFieldNames", {"modelName": GRAMMAR_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(GRAMMAR_FIELDS)

    for field in GRAMMAR_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    print("  Updated.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def setup_lexeme(existing: list[str]):
    if MODEL_NAME in existing:
        update_model()
    else:
        create_model()
    print(f"Note type '{MODEL_NAME}' is ready.")


def setup_grammar(existing: list[str]):
    if GRAMMAR_MODEL_NAME in existing:
        update_grammar_model()
    else:
        create_grammar_model()
    print(f"Note type '{GRAMMAR_MODEL_NAME}' is ready.")


# ---------------------------------------------------------------------------
# UA_Visual — prefix spatial diagram cards
# ---------------------------------------------------------------------------

VISUAL_MODEL_NAME = "UA_Visual"

VISUAL_FIELDS = [
    "NoteID",
    "Prefix",
    "Meaning_EN",
    "Govt",
    "Walking_Pair",
    "Vehicle_Pair",
    "Example_UA",
    "Example_EN",
    "Diagram_SVG",
    "Tags_Ch",
    "Source_Note",
]

VISUAL_CSS = """\
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 580px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.vis-prefix {
  font-size: 36px;
  font-weight: bold;
  color: #2e7d32;
  margin: 10px 0 4px;
  letter-spacing: 1px;
}

.vis-meaning {
  font-size: 17px;
  color: #555;
  margin-bottom: 8px;
}

.vis-govt {
  font-size: 20px;
  font-weight: 600;
  color: #1565c0;
  background: #e3f2fd;
  border-radius: 6px;
  padding: 4px 14px;
  display: inline-block;
  margin: 8px 0;
}

.vis-pairs {
  font-size: 15px;
  color: #555;
  margin: 6px 0;
  line-height: 1.6;
}

.vis-example {
  font-size: 16px;
  font-style: italic;
  color: #333;
  margin-top: 10px;
}

.vis-example-en {
  font-size: 13px;
  color: #777;
  margin-top: 2px;
}

.vis-prompt {
  font-size: 13px;
  color: #bbb;
  margin-top: 10px;
  font-style: italic;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 14px;
}

hr#answer {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 16px 0;
}
"""

# Card 1 (Spatial→UA): diagram + English meaning on front; Ukrainian on back
VISUAL_FRONT_1 = """\
<div>{{Diagram_SVG}}</div>
<div class="vis-meaning">{{Meaning_EN}}</div>
<div class="vis-prompt">What prefix? What government?</div>
"""

VISUAL_BACK_1 = """\
{{FrontSide}}
<hr id="answer">
<div class="vis-prefix">{{Prefix}}</div>
<div class="vis-govt">{{Govt}}</div>
<div class="vis-pairs">{{Walking_Pair}}<br>{{Vehicle_Pair}}</div>
{{#Example_UA}}<div class="vis-example">{{Example_UA}}</div>{{/Example_UA}}
{{#Example_EN}}<div class="vis-example-en">{{Example_EN}}</div>{{/Example_EN}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
"""

# Card 2 (UA→Spatial): Ukrainian prefix + verbs on front; diagram + English on back
VISUAL_FRONT_2 = """\
<div class="vis-prefix">{{Prefix}}</div>
<div class="vis-pairs">{{Walking_Pair}}<br>{{Vehicle_Pair}}</div>
<div class="vis-prompt">What does this prefix mean? What government?</div>
"""

VISUAL_BACK_2 = """\
{{FrontSide}}
<hr id="answer">
<div style="margin-top:4px">{{Diagram_SVG}}</div>
<div class="vis-meaning">{{Meaning_EN}}</div>
<div class="vis-govt">{{Govt}}</div>
{{#Example_UA}}<div class="vis-example">{{Example_UA}}</div>{{/Example_UA}}
{{#Example_EN}}<div class="vis-example-en">{{Example_EN}}</div>{{/Example_EN}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
"""

VISUAL_CARD_TEMPLATES = [
    {"Name": "Spatial→UA", "Front": VISUAL_FRONT_1, "Back": VISUAL_BACK_1},
    {"Name": "UA→Spatial", "Front": VISUAL_FRONT_2, "Back": VISUAL_BACK_2},
]


def create_visual_model():
    print(f"Creating note type '{VISUAL_MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": VISUAL_MODEL_NAME,
            "inOrderFields": VISUAL_FIELDS,
            "css": VISUAL_CSS,
            "cardTemplates": VISUAL_CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_visual_model():
    print(f"Updating note type '{VISUAL_MODEL_NAME}'...")

    # Update templates — build single dict with all templates, then call once
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in VISUAL_CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": VISUAL_MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    anki_request(
        "updateModelStyling",
        {"model": {"name": VISUAL_MODEL_NAME, "css": VISUAL_CSS}},
        url=ANKI_URL,
    )

    existing_fields = anki_request("modelFieldNames", {"modelName": VISUAL_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(VISUAL_FIELDS)

    for field in VISUAL_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    print("  Updated.")


def setup_visual(existing: list[str]):
    if VISUAL_MODEL_NAME in existing:
        update_visual_model()
    else:
        create_visual_model()
    print(f"Note type '{VISUAL_MODEL_NAME}' is ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=["UA_Lexeme", "UA_Grammar", "UA_Visual"],
        help="Set up only this model (default: all three)",
    )
    args = parser.parse_args()

    existing = get_existing_models()

    if args.model == "UA_Lexeme":
        setup_lexeme(existing)
    elif args.model == "UA_Grammar":
        setup_grammar(existing)
    elif args.model == "UA_Visual":
        setup_visual(existing)
    else:
        setup_lexeme(existing)
        setup_grammar(existing)
        setup_visual(existing)

    print("\nDone.")


if __name__ == "__main__":
    main()
