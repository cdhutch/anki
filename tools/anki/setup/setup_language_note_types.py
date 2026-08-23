#!/usr/bin/env python3
"""Create or update language note types in Anki via AnkiConnect.

Parameterized setup for any language domain (CS, SK, DE, UA, IPA).
Reads domain configuration from YAML and generates note types and card templates.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_language_note_types.py cs
    python tools/anki/setup/setup_language_note_types.py sk
    python tools/anki/setup/setup_language_note_types.py de
    python tools/anki/setup/setup_language_note_types.py ua
    python tools/anki/setup/setup_language_note_types.py ipa
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"

# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------

def load_domain_config(domain: str) -> dict:
    """Load domain configuration from YAML."""
    config_path = Path(__file__).resolve().parent.parent / "config" / "domains" / f"{domain}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Domain config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Template generation
# ---------------------------------------------------------------------------

def get_foreign_glosses(note_type_name: str, fields: list[str], domain: str, domain_config: dict) -> list[str]:
    """Determine which foreign language glosses to show in templates.

    Returns a list of gloss field names (e.g., ['CS_Gloss', 'SK_Gloss', 'DE_Gloss'])
    that exist in the fields and should be displayed.
    """
    gloss_order = ["CS_Gloss", "SK_Gloss", "DE_Gloss", "FR_Gloss", "PL_Gloss", "RU_Gloss", "UA_Gloss"]
    available_glosses = [g for g in gloss_order if g in fields]

    # Don't include the current domain's gloss or UA unless it's a Ukrainian note
    if domain.upper() not in ["UA"]:
        available_glosses = [g for g in available_glosses if g != "UA_Gloss"]

    return available_glosses


def get_domain_example_field(domain: str) -> str:
    """Get the domain-specific example field name."""
    return f"{domain.upper()}_Example"


def build_lexeme_templates(note_type_name: str, fields: list[str], domain: str, domain_config: dict) -> list[dict]:
    """Build bidirectional lexeme templates (XX→EN and EN→XX)."""
    domain_upper = domain.upper()
    example_field = get_domain_example_field(domain)
    foreign_glosses = get_foreign_glosses(note_type_name, fields, domain, domain_config)

    # Determine gender/article field names
    gender_field = "Gender" if "Gender" in fields else None
    article_field = "Article" if "Article" in fields else None

    # Build XX→EN template (domain word → English meaning)
    xx_to_en_front = "<div style=\"font-size: 28px; font-weight: bold; margin-bottom: 8px;\">{{Lemma}}</div>\n"
    xx_to_en_front += "<div style=\"font-size: 13px; color: #666;\">{{PartOfSpeech}}"
    if gender_field:
        xx_to_en_front += "{{#Gender}} · {{Gender}}{{/Gender}}"
    if article_field:
        xx_to_en_front += "{{#Article}} · {{Article}}{{/Article}}"
    xx_to_en_front += "</div>\n"
    xx_to_en_front += "{{#" + example_field + "}}<div style=\"font-size: 15px; margin-top: 10px; font-style: italic;\">{{" + example_field + "}}</div>{{/" + example_field + "}}\n"

    xx_to_en_back = "{{FrontSide}}\n<hr>\n"
    xx_to_en_back += "<div style=\"font-size: 22px; font-weight: bold; margin-bottom: 8px;\">{{EN_Gloss}}</div>\n"

    # Add foreign glosses to back
    for gloss in foreign_glosses:
        lang_code = gloss.replace("_Gloss", "")
        xx_to_en_back += "{{#" + gloss + "}}<div style=\"font-size: 14px; color: #666;\">" + lang_code + ": {{" + gloss + "}}</div>{{/" + gloss + "}}\n"

    xx_to_en_back += "{{#EN_Example}}<div style=\"font-size: 13px; color: #999; margin-top: 10px;\">{{EN_Example}}</div>{{/EN_Example}}\n"
    xx_to_en_back += "<div style=\"font-size: 10px; color: #999; margin-top: 16px;\">{{NoteID}}</div>\n"

    # Build EN→XX template (English meaning → domain word)
    en_to_xx_front = "<div style=\"font-size: 22px; font-weight: bold; margin-bottom: 8px;\">{{EN_Gloss}}</div>\n"
    en_to_xx_front += "{{#EN_Example}}<div style=\"font-size: 15px; margin-top: 10px; font-style: italic;\">{{EN_Example}}</div>{{/EN_Example}}\n"

    en_to_xx_back = "{{FrontSide}}\n<hr>\n"
    en_to_xx_back += "<div style=\"font-size: 28px; font-weight: bold; margin-bottom: 8px;\">{{Lemma}}</div>\n"
    en_to_xx_back += "<div style=\"font-size: 13px; color: #666;\">{{PartOfSpeech}}"
    if gender_field:
        en_to_xx_back += "{{#Gender}} · {{Gender}}{{/Gender}}"
    if article_field:
        en_to_xx_back += "{{#Article}} · {{Article}}{{/Article}}"
    en_to_xx_back += "</div>\n"

    # Add foreign glosses to EN→XX back
    for gloss in foreign_glosses:
        lang_code = gloss.replace("_Gloss", "")
        en_to_xx_back += "{{#" + gloss + "}}<div style=\"font-size: 14px; color: #666;\">" + lang_code + ": {{" + gloss + "}}</div>{{/" + gloss + "}}\n"

    en_to_xx_back += "{{#" + example_field + "}}<div style=\"font-size: 13px; color: #999; margin-top: 10px;\">{{" + example_field + "}}</div>{{/" + example_field + "}}\n"
    en_to_xx_back += "<div style=\"font-size: 10px; color: #999; margin-top: 16px;\">{{NoteID}}</div>\n"

    return [
        {"Name": domain_upper + "→EN", "Front": xx_to_en_front, "Back": xx_to_en_back},
        {"Name": "EN→" + domain_upper, "Front": en_to_xx_front, "Back": en_to_xx_back},
    ]


def build_alphabet_templates(note_type_name: str, fields: list[str], domain: str, domain_config: dict) -> list[dict]:
    """Build alphabet recognition template."""
    front = "<div style=\"font-size: 48px; font-weight: bold; text-align: center; margin-bottom: 16px;\">{{Letter}}</div>\n"
    front += "<div style=\"font-size: 18px; text-align: center; color: #666;\">[{{IPA_Symbol}}]</div>\n"
    front += "<div style=\"font-size: 13px; text-align: center; color: #999; margin-top: 8px;\">{{Type}}</div>\n"

    back = "{{FrontSide}}\n<hr>\n"
    back += "<div style=\"font-size: 16px; margin-bottom: 8px;\">{{Description}}</div>\n"
    back += "{{#Example_Word}}<div style=\"font-size: 14px; font-weight: bold; margin-top: 8px;\">{{Example_Word}}</div>{{/Example_Word}}\n"
    back += "{{#EN_Gloss}}<div style=\"font-size: 13px; color: #666;\">{{EN_Gloss}}</div>{{/EN_Gloss}}\n"
    back += "{{#Language_Analogs}}<div style=\"font-size: 13px; color: #999; margin-top: 8px;\">{{Language_Analogs}}</div>{{/Language_Analogs}}\n"
    back += "<div style=\"font-size: 10px; color: #999; margin-top: 16px;\">{{NoteID}}</div>\n"

    return [
        {
            "Name": "Recognition",
            "Front": front,
            "Back": back,
        }
    ]


def build_phoneme_templates(note_type_name: str, fields: list[str], domain: str, domain_config: dict) -> list[dict]:
    """Build IPA phoneme recognition template."""
    front = "<div style=\"font-size: 48px; font-weight: bold; text-align: center; margin-bottom: 16px;\">{{IPA_Symbol}}</div>\n"
    front += "<div style=\"font-size: 18px; text-align: center; margin-bottom: 8px;\">{{Phoneme}}</div>\n"
    front += "<div style=\"font-size: 13px; text-align: center; color: #999;\">{{Type}}</div>\n"

    back = "{{FrontSide}}\n<hr>\n"
    back += "{{#Description}}<div style=\"font-size: 16px; margin-bottom: 12px;\">{{Description}}</div>{{/Description}}\n"
    back += "{{#Manner_of_Articulation}}<div style=\"font-size: 13px; color: #666;\"><strong>Manner:</strong> {{Manner_of_Articulation}}</div>{{/Manner_of_Articulation}}\n"
    back += "{{#Place_of_Articulation}}<div style=\"font-size: 13px; color: #666;\"><strong>Place:</strong> {{Place_of_Articulation}}</div>{{/Place_of_Articulation}}\n"
    back += "{{#Voicing}}<div style=\"font-size: 13px; color: #666;\"><strong>Voicing:</strong> {{Voicing}}</div>{{/Voicing}}\n"
    back += "{{#Airflow}}<div style=\"font-size: 13px; color: #666;\"><strong>Airflow:</strong> {{Airflow}}</div>{{/Airflow}}\n"
    back += "{{#Example_Words}}<div style=\"font-size: 13px; margin-top: 12px;\"><strong>Examples:</strong> {{Example_Words}}</div>{{/Example_Words}}\n"
    back += "{{#Language_Analogs}}<div style=\"font-size: 12px; color: #999; margin-top: 8px;\">{{Language_Analogs}}</div>{{/Language_Analogs}}\n"
    back += "<div style=\"font-size: 10px; color: #999; margin-top: 16px;\">{{NoteID}}</div>\n"

    return [
        {
            "Name": "Recognition",
            "Front": front,
            "Back": back,
        }
    ]


def generate_templates(note_type_name: str, fields: list[str], domain: str, domain_config: dict) -> list[dict]:
    """Generate card templates based on note type pattern."""
    # Determine template type based on note_type_name suffix
    if "lexeme" in note_type_name:
        return build_lexeme_templates(note_type_name, fields, domain, domain_config)
    elif "alphabet" in note_type_name:
        return build_alphabet_templates(note_type_name, fields, domain, domain_config)
    elif "phoneme" in note_type_name:
        return build_phoneme_templates(note_type_name, fields, domain, domain_config)
    else:
        # Default: single recognition card for unknown types
        return [
            {
                "Name": "Recognition",
                "Front": "<div>{{Lemma}}</div>",
                "Back": "{{FrontSide}}<hr>{{EN_Gloss}}",
            }
        ]


# ---------------------------------------------------------------------------
# Shared Anki functions
# ---------------------------------------------------------------------------

def get_existing_models() -> list[str]:
    """Get list of existing note type names in Anki."""
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


# ---------------------------------------------------------------------------
# Main setup
# ---------------------------------------------------------------------------

def setup_domain(domain: str, domain_config: dict, existing_models: list[str]):
    """Set up all note types for a domain."""
    display_name = domain_config.get("display_name", domain.upper())
    print(f"\nSetting up {display_name} domain...")

    note_types = domain_config.get("note_types", {})

    for note_type_key, note_type_def in note_types.items():
        # Convert note_type_key to model name (e.g., cs_lexeme → CS_Lexeme)
        parts = note_type_key.split("_")
        model_name = "_".join([parts[0].upper()] + [p.capitalize() for p in parts[1:]])

        fields = note_type_def.get("fields", [])
        templates = generate_templates(note_type_key, fields, domain, domain_config)

        if model_name in existing_models:
            update_model(model_name, fields, templates)
        else:
            create_model(model_name, fields, templates)

        print(f"Note type '{model_name}' is ready.")

    print(f"{display_name} domain setup complete.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "domain",
        choices=["cs", "sk", "de", "ua", "ipa"],
        help="Language domain to set up",
    )
    args = parser.parse_args()

    try:
        domain_config = load_domain_config(args.domain)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    existing_models = get_existing_models()
    setup_domain(args.domain, domain_config, existing_models)


if __name__ == "__main__":
    main()
