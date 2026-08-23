#!/usr/bin/env python3
"""Create or update IPA note types in Anki via AnkiConnect.

Note type: IPA_Phoneme

Minimal setup for getting IPA phoneme notes into Anki.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_ipa_note_types.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# IPA_Phoneme
# ---------------------------------------------------------------------------

IPA_PHONEME_FIELDS = [
    "NoteID",
    "Phoneme",
    "IPA_Symbol",
    "Type",
    "Description",
    "Manner_of_Articulation",
    "Place_of_Articulation",
    "Voicing",
    "Airflow",
    "Example_Words",
    "Language_Analogs",
    "Minimal_Pairs",
    "Confusable_With",
    "Mnemonic_EN",
    "EN_Gloss",
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

IPA_PHONEME_FRONT = """\
<div style="font-size: 48px; font-weight: bold; text-align: center; margin-bottom: 16px;">{{IPA_Symbol}}</div>
<div style="font-size: 18px; text-align: center; margin-bottom: 8px;">{{Phoneme}}</div>
<div style="font-size: 13px; text-align: center; color: #999;">{{Type}}</div>
"""

IPA_PHONEME_BACK = """\
{{FrontSide}}
<hr>
{{#Description}}<div style="font-size: 16px; margin-bottom: 12px;">{{Description}}</div>{{/Description}}
{{#Manner_of_Articulation}}<div style="font-size: 13px; color: #666;"><strong>Manner:</strong> {{Manner_of_Articulation}}</div>{{/Manner_of_Articulation}}
{{#Place_of_Articulation}}<div style="font-size: 13px; color: #666;"><strong>Place:</strong> {{Place_of_Articulation}}</div>{{/Place_of_Articulation}}
{{#Voicing}}<div style="font-size: 13px; color: #666;"><strong>Voicing:</strong> {{Voicing}}</div>{{/Voicing}}
{{#Airflow}}<div style="font-size: 13px; color: #666;"><strong>Airflow:</strong> {{Airflow}}</div>{{/Airflow}}
{{#Example_Words}}<div style="font-size: 13px; margin-top: 12px;"><strong>Examples:</strong> {{Example_Words}}</div>{{/Example_Words}}
{{#Language_Analogs}}<div style="font-size: 12px; color: #999; margin-top: 8px;">{{Language_Analogs}}</div>{{/Language_Analogs}}
<div style="font-size: 10px; color: #999; margin-top: 16px;">{{NoteID}}</div>
"""

IPA_PHONEME_CARD_TEMPLATES = [
    {"Name": "Recognition", "Front": IPA_PHONEME_FRONT, "Back": IPA_PHONEME_BACK},
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


def setup_phoneme(existing: list[str]):
    """Set up IPA_Phoneme model."""
    if "IPA_Phoneme" in existing:
        update_model("IPA_Phoneme", IPA_PHONEME_FIELDS, IPA_PHONEME_CARD_TEMPLATES)
    else:
        create_model("IPA_Phoneme", IPA_PHONEME_FIELDS, IPA_PHONEME_CARD_TEMPLATES)
    print("Note type 'IPA_Phoneme' is ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    existing = get_existing_models()
    setup_phoneme(existing)


if __name__ == "__main__":
    main()
