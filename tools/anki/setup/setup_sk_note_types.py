#!/usr/bin/env python3
"""Create or update Slovak note types in Anki via AnkiConnect.

Note types: SK_Lexeme, SK_Alphabet

Minimal setup for getting Slovak notes into Anki.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_sk_note_types.py              # both models
    python tools/anki/setup/setup_sk_note_types.py --model SK_Lexeme
    python tools/anki/setup/setup_sk_note_types.py --model SK_Alphabet
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# SK_Lexeme
# ---------------------------------------------------------------------------

SK_LEXEME_FIELDS = [
    "NoteID",
    "Lemma",
    "PartOfSpeech",
    "Gender",
    "EN_Gloss",
    "CS_Gloss",
    "DE_Gloss",
    "FR_Gloss",
    "UA_Gloss",
    "RU_Gloss",
    "Govt_Case",
    "IrregularForms",
    "Mnemonic_EN",
    "ConfusableSet",
    "CompareScenario",
    "CompareA",
    "CompareB",
    "CompareC",
    "CompareD",
    "SK_Example",
    "EN_Example",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

SK_LEXEME_FRONT = """\
<div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">{{Lemma}}</div>
<div style="font-size: 13px; color: #666;">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
{{#SK_Example}}<div style="font-size: 15px; margin-top: 10px; font-style: italic;">{{SK_Example}}</div>{{/SK_Example}}
"""

SK_LEXEME_BACK = """\
{{FrontSide}}
<hr>
<div style="font-size: 22px; font-weight: bold; margin-bottom: 8px;">{{EN_Gloss}}</div>
{{#CS_Gloss}}<div style="font-size: 14px; color: #666;">CS: {{CS_Gloss}}</div>{{/CS_Gloss}}
{{#DE_Gloss}}<div style="font-size: 14px; color: #666;">DE: {{DE_Gloss}}</div>{{/DE_Gloss}}
{{#FR_Gloss}}<div style="font-size: 14px; color: #666;">FR: {{FR_Gloss}}</div>{{/FR_Gloss}}
{{#UA_Gloss}}<div style="font-size: 14px; color: #666;">UA: {{UA_Gloss}}</div>{{/UA_Gloss}}
{{#RU_Gloss}}<div style="font-size: 14px; color: #666;">RU: {{RU_Gloss}}</div>{{/RU_Gloss}}
{{#EN_Example}}<div style="font-size: 13px; color: #999; margin-top: 10px;">{{EN_Example}}</div>{{/EN_Example}}
<div style="font-size: 10px; color: #999; margin-top: 16px;">{{NoteID}}</div>
"""

SK_LEXEME_CARD_TEMPLATES = [
    {"Name": "Recognition", "Front": SK_LEXEME_FRONT, "Back": SK_LEXEME_BACK},
]

# ---------------------------------------------------------------------------
# SK_Alphabet
# ---------------------------------------------------------------------------

SK_ALPHABET_FIELDS = [
    "NoteID",
    "Letter",
    "IPA_Symbol",
    "Type",
    "Description",
    "Example_Word",
    "EN_Gloss",
    "Language_Analogs",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

SK_ALPHABET_FRONT = """\
<div style="font-size: 48px; font-weight: bold; text-align: center; margin-bottom: 16px;">{{Letter}}</div>
<div style="font-size: 18px; text-align: center; color: #666;">[{{IPA_Symbol}}]</div>
<div style="font-size: 13px; text-align: center; color: #999; margin-top: 8px;">{{Type}}</div>
"""

SK_ALPHABET_BACK = """\
{{FrontSide}}
<hr>
<div style="font-size: 16px; margin-bottom: 8px;">{{Description}}</div>
{{#Example_Word}}<div style="font-size: 14px; font-weight: bold; margin-top: 8px;">{{Example_Word}}</div>{{/Example_Word}}
{{#EN_Gloss}}<div style="font-size: 13px; color: #666;">{{EN_Gloss}}</div>{{/EN_Gloss}}
{{#Language_Analogs}}<div style="font-size: 13px; color: #999; margin-top: 8px;">{{Language_Analogs}}</div>{{/Language_Analogs}}
<div style="font-size: 10px; color: #999; margin-top: 16px;">{{NoteID}}</div>
"""

SK_ALPHABET_CARD_TEMPLATES = [
    {"Name": "Recognition", "Front": SK_ALPHABET_FRONT, "Back": SK_ALPHABET_BACK},
]

# ---------------------------------------------------------------------------
# Shared functions
# ---------------------------------------------------------------------------

def get_existing_models() -> list[str]:
    return anki_request("modelNames", url=ANKI_URL) or []


def sync_field_order(model_name: str, desired_fields: list[str]) -> bool:
    """Reposition model fields to match desired_fields order."""
    live_fields = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL) or []
    target = [f for f in desired_fields if f in set(live_fields)]

    if live_fields[: len(target)] == target:
        return False

    print(f"  Field order differs -- repositioning...")
    for index, field in enumerate(target):
        anki_request(
            "modelFieldReposition",
            {"modelName": model_name, "fieldName": field, "index": index},
            url=ANKI_URL,
        )
    print(f"    Repositioned {len(target)} field(s).")
    return True


def create_model(model_name: str, fields: list[str], templates: list[dict]):
    """Create a new note type in Anki."""
    print(f"Creating note type '{model_name}'...")
    anki_request(
        "createModel",
        {
            "modelName": model_name,
            "inOrderFields": fields,
            "css": ".card { font-family: Arial; font-size: 16px; }",
            "cardTemplates": templates,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_model(model_name: str, fields: list[str], templates: list[dict]):
    """Update an existing note type."""
    print(f"Updating note type '{model_name}'...")

    # Sync fields (add missing)
    existing_fields = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL)
    existing_set = set(existing_fields)

    for field in fields:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": model_name, "fieldName": field}, url=ANKI_URL)

    # Add new templates if needed
    existing_templates_resp = anki_request("modelTemplates", {"modelName": model_name}, url=ANKI_URL)
    existing_template_names = list(existing_templates_resp.keys()) if existing_templates_resp else []

    for tmpl in templates:
        if tmpl["Name"] not in existing_template_names:
            print(f"  Adding new template: {tmpl['Name']}")
            anki_request(
                "modelTemplateAdd",
                {
                    "modelName": model_name,
                    "template": {"Name": tmpl["Name"], "Front": tmpl["Front"], "Back": tmpl["Back"]},
                },
                url=ANKI_URL,
            )

    # Update templates
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in templates}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": model_name, "templates": templates_dict}},
        url=ANKI_URL,
    )

    # Sync field order
    sync_field_order(model_name, fields)

    print("  Updated.")


def setup_lexeme(existing: list[str]):
    """Set up SK_Lexeme model."""
    if "SK_Lexeme" in existing:
        update_model("SK_Lexeme", SK_LEXEME_FIELDS, SK_LEXEME_CARD_TEMPLATES)
    else:
        create_model("SK_Lexeme", SK_LEXEME_FIELDS, SK_LEXEME_CARD_TEMPLATES)
    print("Note type 'SK_Lexeme' is ready.")


def setup_alphabet(existing: list[str]):
    """Set up SK_Alphabet model."""
    if "SK_Alphabet" in existing:
        update_model("SK_Alphabet", SK_ALPHABET_FIELDS, SK_ALPHABET_CARD_TEMPLATES)
    else:
        create_model("SK_Alphabet", SK_ALPHABET_FIELDS, SK_ALPHABET_CARD_TEMPLATES)
    print("Note type 'SK_Alphabet' is ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=["SK_Lexeme", "SK_Alphabet"],
        help="Set up only this model (default: both)",
    )
    args = parser.parse_args()

    existing = get_existing_models()

    if args.model == "SK_Lexeme":
        setup_lexeme(existing)
    elif args.model == "SK_Alphabet":
        setup_alphabet(existing)
    else:
        setup_lexeme(existing)
        setup_alphabet(existing)


if __name__ == "__main__":
    main()
