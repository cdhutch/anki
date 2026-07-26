#!/usr/bin/env python3
"""Generate UA_Verb CNSF notes from Горох conjugation data and LLM examples.

Fetches conjugation paradigms from Горох (goroh.pp.ua) via Chrome browser,
generates example sentences via Anthropic API, and creates complete CNSF files.

Usage:
    python tools/anki/generate/generate_ua_verb_from_goroh.py --infinitives іти йти піти ...
    python tools/anki/generate/generate_ua_verb_from_goroh.py --file domains/ua/anki/sources/verb_list.txt

Requires:
    - Anki running with AnkiConnect
    - Chrome browser (for Горох fetching)
    - ANTHROPIC_API_KEY environment variable set
"""
from __future__ import annotations

import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

# Constants
ANKI_URL = "http://127.0.0.1:8765"
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"
GOROH_BASE = "https://goroh.pp.ua/Словозміна"

# Chapter 2.9 verb groups from Яблуко textbook
CHAPTER_2_9_VERBS = {
    "2.9.2_base": {
        "description": "Base motion verbs (3-verb groups: multidirectional, unidirectional, perfective)",
        "verbs": [
            # Walking: ходити (multi) / йти (uni) / піти (perf)
            {"infinitive": "йти", "alt_forms": ["іти"], "group": "walking", "type": "unidirectional"},
            {"infinitive": "піти", "group": "walking", "type": "perfective"},
            # Vehicle: їздити (multi) / їхати (uni) / поїхати (perf)
            {"infinitive": "їхати", "group": "vehicle", "type": "unidirectional"},
            {"infinitive": "поїхати", "group": "vehicle", "type": "perfective"},
            # Swimming: плавати (multi) / пливти (uni) / поплисти (perf)
            {"infinitive": "пливти", "group": "swimming", "type": "unidirectional"},
            {"infinitive": "поплисти", "group": "swimming", "type": "perfective"},
            # Running: бігати (multi) / бігти (uni) / побігти (perf)
            {"infinitive": "бігти", "group": "running", "type": "unidirectional"},
            {"infinitive": "побігти", "group": "running", "type": "perfective"},
            # Flying: літати (multi) / летіти (uni) / полетіти (perf)
            {"infinitive": "летіти", "group": "flying", "type": "unidirectional"},
            {"infinitive": "полетіти", "group": "flying", "type": "perfective"},
        ],
    },
    "2.9.4_prefixed": {
        "description": "Prefixed motion verbs (ходити and їхати bases)",
        "verbs": [
            # ходити base with prefixes
            {"infinitive": "приходити", "base": "ходити", "prefix": "при-", "type": "prefixed"},
            {"infinitive": "виходити", "base": "ходити", "prefix": "ви-", "type": "prefixed"},
            {"infinitive": "підходити", "base": "ходити", "prefix": "під-", "type": "prefixed"},
            {"infinitive": "доходити", "base": "ходити", "prefix": "до-", "type": "prefixed"},
            {"infinitive": "проходити", "base": "ходити", "prefix": "про-", "type": "prefixed"},
            {"infinitive": "переходити", "base": "ходити", "prefix": "пере-", "type": "prefixed"},
            {"infinitive": "заходити", "base": "ходити", "prefix": "за-", "type": "prefixed"},
            {"infinitive": "відходити", "base": "ходити", "prefix": "від-", "type": "prefixed"},
            # їхати base with same prefixes
            {"infinitive": "приїхати", "base": "їхати", "prefix": "при-", "type": "prefixed"},
            {"infinitive": "виїхати", "base": "їхати", "prefix": "ви-", "type": "prefixed"},
            {"infinitive": "підїхати", "base": "їхати", "prefix": "під-", "type": "prefixed"},
            {"infinitive": "доїхати", "base": "їхати", "prefix": "до-", "type": "prefixed"},
            {"infinitive": "проїхати", "base": "їхати", "prefix": "про-", "type": "prefixed"},
            {"infinitive": "переїхати", "base": "їхати", "prefix": "пере-", "type": "prefixed"},
            {"infinitive": "заїхати", "base": "їхати", "prefix": "за-", "type": "prefixed"},
            {"infinitive": "відїхати", "base": "їхати", "prefix": "від-", "type": "prefixed"},
        ],
    },
}


def fetch_goroh_conjugation_via_chrome(infinitives: list[str]) -> dict:
    """Batch fetch conjugation paradigms from Горох via Claude in Chrome.

    Returns dict mapping infinitive → conjugation data.

    Note: Requires Claude in Chrome extension to be running.
    This function is a placeholder - actual implementation uses browser automation.
    """
    print("\n" + "="*80)
    print("STEP 1: Fetch conjugations from Горох via Chrome")
    print("="*80)
    print(f"\nInfinitives to fetch: {infinitives}")
    print("\nTo implement: Use Claude in Chrome to fetch each infinitive's conjugation page")
    print("and extract the conjugation paradigm from the table.\n")

    # Placeholder: return empty dict for now
    # In production, this would use claude-in-chrome tools to:
    # 1. Navigate to Горох
    # 2. Fetch each verb's conjugation page
    # 3. Parse the conjugation table
    # 4. Extract Present 1-6, Past m/f/n/pl, Imperative 2sg/1pl/2pl, Participles

    return {}


def generate_examples_via_llm(infinitive: str, en_gloss: str, num_examples: int = 2) -> dict:
    """Generate Ukrainian and English example sentences via Anthropic API.

    Returns dict with "ua_example" and "en_example" keys.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        print("  Warning: anthropic package not installed. Skipping example generation.")
        return {"ua_example": "", "en_example": ""}

    client = Anthropic()
    prompt = f"""Generate {num_examples} example sentences in Ukrainian using the verb "{infinitive}" ({en_gloss}).

Provide the examples in this format:
UA: [sentence 1]
EN: [translation 1]
UA: [sentence 2]
EN: [translation 2]

Guidelines:
- Use natural, conversational Ukrainian (Lviv/Galician register if applicable)
- Show different uses or contexts
- Keep examples clear and pedagogically useful for learners
- Use modern Ukrainian orthography
- Stress marks: verify against Горох (goroh.pp.ua)"""

    try:
        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
        return {"ua_example": text, "en_example": "", "generated": True}
    except Exception as e:
        print(f"  Error generating examples: {e}")
        return {"ua_example": "", "en_example": "", "generated": False}


def create_ua_verb_cnsf(
    note_id: str,
    lemma: str,
    en_gloss: str,
    alt_forms: list[str] | None = None,
    tags: list[str] | None = None,
    conjugation_data: dict | None = None,
    example_data: dict | None = None,
) -> str:
    """Create CNSF YAML frontmatter for a UA_Verb note.

    Returns YAML string ready to write to file.
    """
    tags = tags or []
    alt_forms = alt_forms or []

    yaml_fields = {
        "note_id": note_id,
        "note_type": "ua_verb",
        "deck": "UA::Verbs",
        "tags": tags,
        "fields": {
            "Lemma": lemma,
            "EN_Gloss": en_gloss,
            "Alternative_Forms": " | ".join(alt_forms) if alt_forms else "",
            # Conjugation fields (placeholder - will be populated from Горох)
            "Pres_1sg": "",
            "Pres_2sg": "",
            "Pres_3sg": "",
            "Pres_1pl": "",
            "Pres_2pl": "",
            "Pres_3pl": "",
            "Imperative_2sg": "",
            "Imperative_1pl": "",
            "Imperative_2pl": "",
            "Past_Masculine": "",
            "Past_Feminine": "",
            "Past_Neuter": "",
            "Past_Plural": "",
            "Participle_Active_Present": "",
            "Participle_Adverbial_Present": "",
            "Participle_Passive_Past_Masculine": "",
            "Participle_Passive_Past_Feminine": "",
            "Participle_Impersonal_Past": "",
            "Participle_Adverbial_Past": "",
            "UA_Example": example_data.get("ua_example", "") if example_data else "",
            "EN_Example": example_data.get("en_example", "") if example_data else "",
            "Verification_Notes": "",
            "Source_URL": f"{GOROH_BASE}/{lemma}" if lemma else "",
        },
    }

    # Build YAML
    yaml_lines = ["---"]
    for key in ["note_id", "note_type", "deck"]:
        yaml_lines.append(f"{key}: {json.dumps(yaml_fields[key])}")
    yaml_lines.append(f"tags: {json.dumps(yaml_fields['tags'])}")
    yaml_lines.append("fields:")
    for field_name, field_value in yaml_fields["fields"].items():
        # Use block literal for multi-line fields
        if "\n" in str(field_value):
            yaml_lines.append(f"  {field_name}: |-")
            for line in str(field_value).split("\n"):
                yaml_lines.append(f"    {line}")
        else:
            yaml_lines.append(f"  {field_name}: {json.dumps(field_value)}")
    yaml_lines.append("---\n")

    return "\n".join(yaml_lines)


def generate_verbs(infinitives: list[str], chapter: str = "2.9", dry_run: bool = False):
    """Generate UA_Verb CNSF files for given infinitives."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"Generating UA_Verb notes for Chapter {chapter}")
    print(f"{'='*80}\n")

    generated = 0
    skipped = 0

    for i, infinitive in enumerate(infinitives, start=1):
        note_id = f"ua-verb-000{1000 + i}"  # Will need to adjust to actual ID range
        print(f"[{i}/{len(infinitives)}] {infinitive}")

        # Fetch from Горох
        goroh_data = fetch_goroh_conjugation(infinitive)
        if not goroh_data:
            print(f"  SKIP: Could not fetch from Горох")
            skipped += 1
            continue

        # Generate examples (placeholder)
        en_gloss = f"to [action related to {infinitive}]"  # Placeholder
        example_data = {"ua_example": "[Example to be generated]", "en_example": "[Translation]"}

        # Create CNSF content
        cnsf_content = create_ua_verb_cnsf(
            note_id=note_id,
            lemma=infinitive,
            en_gloss=en_gloss,
            tags=["phase:2a", f"chapter:{chapter}"],
            conjugation_data=goroh_data,
            example_data=example_data,
        )

        # Write file
        output_file = OUTPUT_DIR / f"{note_id}.md"
        if not dry_run:
            output_file.write_text(cnsf_content, encoding="utf-8")
            print(f"  CREATED: {output_file.name}")
        else:
            print(f"  DRY RUN: Would create {output_file.name}")

        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped.")
    return generated, skipped


def main():
    parser = argparse.ArgumentParser(description="Generate UA_Verb CNSF notes from Горох + LLM")
    parser.add_argument(
        "--chapter",
        choices=["2.9.2", "2.9.4", "all"],
        default="all",
        help="Chapter to generate (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument(
        "--infinitives",
        nargs="*",
        help="Specific infinitives to generate (overrides --chapter)",
    )
    args = parser.parse_args()

    # Collect infinitives
    infinitives_to_generate = []
    if args.infinitives:
        infinitives_to_generate = args.infinitives
    elif args.chapter == "2.9.2":
        infinitives_to_generate = [v["infinitive"] for v in CHAPTER_2_9_VERBS["2.9.2_base"]["verbs"]]
    elif args.chapter == "2.9.4":
        infinitives_to_generate = [v["infinitive"] for v in CHAPTER_2_9_VERBS["2.9.4_prefixed"]["verbs"]]
    else:  # all
        infinitives_to_generate = (
            [v["infinitive"] for v in CHAPTER_2_9_VERBS["2.9.2_base"]["verbs"]]
            + [v["infinitive"] for v in CHAPTER_2_9_VERBS["2.9.4_prefixed"]["verbs"]]
        )

    print(f"Infinitives to generate: {infinitives_to_generate}")
    generate_verbs(infinitives_to_generate, chapter=args.chapter or "2.9", dry_run=args.dry_run)


if __name__ == "__main__":
    main()
