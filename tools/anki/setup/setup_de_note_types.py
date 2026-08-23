#!/usr/bin/env python3
"""Create or update German note types in Anki via AnkiConnect.

Note type: DE_Lexeme

Minimal setup for getting German notes into Anki.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_de_note_types.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# DE_Lexeme
# ---------------------------------------------------------------------------

DE_LEXEME_FIELDS = [
    "NoteID",
    "Lemma",
    "PartOfSpeech",
    "Gender",
    "EN_Gloss",
    "CS_Gloss",
    "FR_Gloss",
    "SK_Gloss",
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
    "DE_Example",
    "EN_Example",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

DE_LEXEME_FRONT = """\
<div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">{{Lemma}}</div>
<div style="font-size: 13px; color: #666;">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
{{#DE_Example}}<div style="font-size: 15px; margin-top: 10px; font-style: italic;">{{DE_Example}}</div>{{/DE_Example}}
"""

DE_LEXEME_BACK = """\
{{FrontSide}}
<hr>
<div style="font-size: 22px; font-weight: bold; margin-bottom: 8px;">{{EN_Gloss}}</div>
{{#CS_Gloss}}<div style="font-size: 14px; color: #666;">CS: {{CS_Gloss}}</div>{{/CS_Gloss}}
{{#FR_Gloss}}<div style="font-size: 14px; color: #666;">FR: {{FR_Gloss}}</div>{{/FR_Gloss}}
{{#SK_Gloss}}<div style="font-size: 14px; color: #666;">SK: {{SK_Gloss}}</div>{{/SK_Gloss}}
{{#UA_Gloss}}<div style="font-size: 14px; color: #666;">UA: {{UA_Gloss}}</div>{{/UA_Gloss}}
{{#RU_Gloss}}<div style="font-size: 14px; color: #666;">RU: {{RU_Gloss}}</div>{{/RU_Gloss}}
{{#EN_Example}}<div style="font-size: 13px; color: #999; margin-top: 10px;">{{EN_Example}}</div>{{/EN_Example}}
<div style="font-size: 10px; color: #999; margin-top: 16px;">{{NoteID}}</div>
"""

EN_DE_FRONT = """\
<div style="font-size: 22px; font-weight: bold; margin-bottom: 8px;">{{EN_Gloss}}</div>
{{#EN_Example}}<div style="font-size: 15px; margin-top: 10px; font-style: italic;">{{EN_Example}}</div>{{/EN_Example}}
"""

EN_DE_BACK = """\
{{FrontSide}}
<hr>
<div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">{{Lemma}}</div>
<div style="font-size: 13px; color: #666;">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
{{#CS_Gloss}}<div style="font-size: 14px; color: #666;">CS: {{CS_Gloss}}</div>{{/CS_Gloss}}
{{#FR_Gloss}}<div style="font-size: 14px; color: #666;">FR: {{FR_Gloss}}</div>{{/FR_Gloss}}
{{#SK_Gloss}}<div style="font-size: 14px; color: #666;">SK: {{SK_Gloss}}</div>{{/SK_Gloss}}
{{#DE_Example}}<div style="font-size: 13px; color: #999; margin-top: 10px;">{{DE_Example}}</div>{{/DE_Example}}
<div style="font-size: 10px; color: #999; margin-top: 16px;">{{NoteID}}</div>
"""

DE_LEXEME_CARD_TEMPLATES = [
    {"Name": "DE→EN", "Front": DE_LEXEME_FRONT, "Back": DE_LEXEME_BACK},
    {"Name": "EN→DE", "Front": EN_DE_FRONT, "Back": EN_DE_BACK},
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
    """Set up DE_Lexeme model."""
    if "DE_Lexeme" in existing:
        update_model("DE_Lexeme", DE_LEXEME_FIELDS, DE_LEXEME_CARD_TEMPLATES)
    else:
        create_model("DE_Lexeme", DE_LEXEME_FIELDS, DE_LEXEME_CARD_TEMPLATES)
    print("Note type 'DE_Lexeme' is ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    existing = get_existing_models()
    setup_lexeme(existing)


if __name__ == "__main__":
    main()
