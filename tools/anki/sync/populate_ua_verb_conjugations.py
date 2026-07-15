#!/usr/bin/env python3
"""Parse Горох conjugation data and populate ua-verb CNSF files."""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any

# Verb mapping: lemma → note_id
VERB_MAP = {
    "ходити": "0001", "іти": "0002", "йти": "0003", "піти": "0004",
    "їздити": "0005", "їхати": "0006", "поїхати": "0007",
    "плавати": "0008", "пливти": "0009", "попливти": "0010",
    "бігати": "0011", "бігти": "0012", "побігти": "0013",
    "літати": "0014", "летіти": "0015", "полетіти": "0016",
    "приходити": "0017", "виходити": "0018", "підходити": "0019", "доходити": "0020",
    "проходити": "0021", "переходити": "0022", "заходити": "0023", "відходити": "0024",
    "приїхати": "0025", "виїхати": "0026", "підїхати": "0027", "доїхати": "0028",
    "проїхати": "0029", "переїхати": "0030", "заїхати": "0031", "відїхати": "0032",
}

def parse_cells(cells: List[str]) -> Dict[str, str]:
    """Parse Горох table cells into structured conjugation data."""
    forms = {
        "Pres_1sg": "", "Pres_2sg": "", "Pres_3sg": "",
        "Pres_1pl": "", "Pres_2pl": "", "Pres_3pl": "",
        "Past_1sg_m": "", "Past_1sg_f": "", "Past_1sg_n": "", "Past_3pl": "",
        "Imperative_2sg": "", "Imperative_1pl": "", "Imperative_2pl": "",
        "Participle_Active_Present": "", "Participle_Adverbial_Present": "",
        "Participle_Passive_Past_m": "", "Participle_Passive_Past_f": "",
        "Participle_Impersonal_Past": "", "Participle_Adverbial_Past": "",
    }

    if not cells:
        return forms

    try:
        # Find section markers
        present_idx = next((i for i, c in enumerate(cells) if "Теперішній" in c), -1)
        past_idx = next((i for i, c in enumerate(cells) if "Минулий" in c), -1)
        imperative_idx = next((i for i, c in enumerate(cells) if "Наказовий" in c), -1)

        # ===== PRESENT TENSE =====
        if present_idx >= 0:
            present_section = cells[present_idx:]
            for i, cell in enumerate(present_section):
                if cell == "1 особа" and i+1 < len(present_section):
                    # Extract 1st person singular
                    forms["Pres_1sg"] = present_section[i+1].split(',')[0].strip()
                    # Look for 1st person plural (next non-label cell)
                    for j in range(i+2, min(i+5, len(present_section))):
                        if present_section[j] not in ["2 особа", "3 особа", "Однина", "Множина"]:
                            forms["Pres_1pl"] = present_section[j].split(',')[0].strip()
                            break
                elif cell == "2 особа" and i+1 < len(present_section):
                    # Extract 2nd person singular
                    forms["Pres_2sg"] = present_section[i+1].split(',')[0].strip()
                    # Look for 2nd person plural
                    for j in range(i+2, min(i+5, len(present_section))):
                        if present_section[j] not in ["1 особа", "3 особа", "Однина", "Множина"]:
                            forms["Pres_2pl"] = present_section[j].split(',')[0].strip()
                            break
                elif cell == "3 особа" and i+1 < len(present_section):
                    # Extract 3rd person singular
                    forms["Pres_3sg"] = present_section[i+1].split(',')[0].strip()
                    # Look for 3rd person plural
                    for j in range(i+2, min(i+5, len(present_section))):
                        if present_section[j] not in ["1 особа", "2 особа", "Однина", "Множина", "Теперішній", "Майбутній", "Наказовий", "Минулий"]:
                            forms["Pres_3pl"] = present_section[j].split(',')[0].strip()
                            break

        # ===== PAST TENSE =====
        if past_idx >= 0:
            past_end = imperative_idx if imperative_idx > past_idx else len(cells)
            past_section = cells[past_idx:past_end]

            for i, cell in enumerate(past_section):
                if "чол. р." in cell and i+1 < len(past_section):
                    forms["Past_1sg_m"] = past_section[i+1].split(',')[0].strip()
                elif "жін. р." in cell and i+1 < len(past_section):
                    forms["Past_1sg_f"] = past_section[i+1].split(',')[0].strip()
                elif "сер. р." in cell and i+1 < len(past_section):
                    forms["Past_1sg_n"] = past_section[i+1].split(',')[0].strip()

            # Find plural past (usually a form ending in -ли)
            for i, cell in enumerate(past_section):
                if cell and cell.endswith("ли") and i > 0:
                    if past_section[i-1] in ["жін. р.", "сер. р.", "Однина", "Множина"] or \
                       (i > 1 and "р." in past_section[i-1]):
                        forms["Past_3pl"] = cell
                        break

        # ===== IMPERATIVE =====
        if imperative_idx >= 0:
            imp_section = cells[imperative_idx:]
            for i, cell in enumerate(imp_section):
                if cell == "2 особа" and i+1 < len(imp_section):
                    # 2sg imperative - usually just the form without alternates
                    imp_form = imp_section[i+1].split(',')[0].strip()
                    # Remove the -но suffix variant if present
                    if "-" in imp_form:
                        imp_form = imp_form.split('-')[0].strip()
                    forms["Imperative_2sg"] = imp_form
                elif cell == "1 особа" and i+1 < len(imp_section):
                    # 1pl imperative
                    forms["Imperative_1pl"] = imp_section[i+1].split(',')[0].strip()

            # Find 2pl imperative - often after 1pl or as a separate form
            for i, cell in enumerate(imp_section):
                if i > 0 and imp_section[i-1] == "1 особа" and i+2 < len(imp_section):
                    candidate = imp_section[i+2].split(',')[0].strip()
                    if candidate and not any(x in candidate for x in ["особа", "Однина", "Множина", "Наказовий"]):
                        forms["Imperative_2pl"] = candidate
                        break

        # ===== PARTICIPLES =====
        # This is complex - participles are often at the end after "Дієприкметник" or "Дієслівна форма"
        # Look for common participle forms
        for i, cell in enumerate(cells):
            lower_cell = cell.lower()

            # Active present participle (теперішній дійсний) - ends in -ючий/-ащий
            if "теперішній" in lower_cell and "дійсний" in lower_cell and i+1 < len(cells):
                candidate = cells[i+1].split(',')[0].strip()
                if candidate and not any(x in candidate for x in ["особа", "р."]):
                    forms["Participle_Active_Present"] = candidate

            # Adverbial present participle (деепричастник теперішній) - ends in -ючи/-ачи
            if "деепричастник" in lower_cell and "теперішній" in lower_cell and i+1 < len(cells):
                candidate = cells[i+1].split(',')[0].strip()
                if candidate and not any(x in candidate for x in ["особа", "р."]):
                    forms["Participle_Adverbial_Present"] = candidate

            # Passive past participle (теперішній страдальний) - ends in -ний/-тий
            if "теперішній" in lower_cell and "страдальний" in lower_cell and i+1 < len(cells):
                # This is genitive/nominative - need masculine form
                candidate = cells[i+1].split(',')[0].strip()
                if candidate and not any(x in candidate for x in ["особа"]):
                    forms["Participle_Passive_Past_m"] = candidate
                    # Try to derive feminine form (nominative -на)
                    if candidate.endswith("ний"):
                        forms["Participle_Passive_Past_f"] = candidate[:-3] + "на"
                    elif candidate.endswith("тий"):
                        forms["Participle_Passive_Past_f"] = candidate[:-3] + "та"

            # Adverbial past participle (деепричастник минулий) - ends in -вши
            if "деепричастник" in lower_cell and "минулий" in lower_cell and i+1 < len(cells):
                candidate = cells[i+1].split(',')[0].strip()
                if candidate and not any(x in candidate for x in ["особа", "р."]):
                    forms["Participle_Adverbial_Past"] = candidate

    except (StopIteration, IndexError, ValueError, AttributeError):
        pass

    return forms

def update_verb_file(note_id: str, lemma: str, conjugations: Dict[str, str], verbs_dir: Path) -> bool:
    """Update a ua-verb YAML file with conjugation data."""
    file_path = verbs_dir / f"ua-verb-{note_id}.md"

    if not file_path.exists():
        return False

    try:
        # Read existing file
        content = file_path.read_text(encoding="utf-8")
        parts = content.split("---")

        if len(parts) < 3:
            return False

        yaml_str = parts[1].strip()
        yaml_data = yaml.safe_load(yaml_str)

        if not yaml_data or "fields" not in yaml_data:
            return False

        # Update conjugation fields
        for field, value in conjugations.items():
            if value:  # Only update non-empty values
                yaml_data["fields"][field] = value

        # Rebuild YAML
        yaml_output = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_output}---\n"

        file_path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"    Error updating {file_path.name}: {e}")
        return False

def main():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    # Load the fetched data from Chrome (pasted into a JSON file or dict)
    # For now, we'll use a placeholder and explain the flow

    print("Ukrainian Verb Conjugation Populator")
    print("=" * 50)
    print()
    print("This script requires conjugation data from Горох (goroh.pp.ua).")
    print("The data should be in the format fetched via Chrome JavaScript.")
    print()
    print("Expected data structure (from window.allVerbData):")
    print("{")
    print('  "lemma": {')
    print('    "cells": [array of cell text],')
    print('    "status": "ok"')
    print("  },")
    print("  ...")
    print("}")
    print()

    # Try to load data from a JSON file if it exists
    data_file = Path(__file__).resolve().parent / "goroh_data.json"

    if data_file.exists():
        print(f"Loading data from {data_file}...")
        with open(data_file, 'r', encoding='utf-8') as f:
            verb_data = json.load(f)
    else:
        print(f"Data file not found: {data_file}")
        print()
        print("To use this script:")
        print("1. Run the Chrome JavaScript to fetch all verbs from Горох")
        print("2. Export window.allVerbData as JSON")
        print("3. Save to: tools/anki/sync/goroh_data.json")
        print()
        return

    # Process each verb
    success_count = 0
    error_count = 0

    for lemma, note_id in sorted(VERB_MAP.items(), key=lambda x: int(x[1])):
        print(f"  [{note_id}] {lemma:15s} ... ", end="", flush=True)

        if lemma not in verb_data or verb_data[lemma].get("status") != "ok":
            print("✗ (no data)")
            error_count += 1
            continue

        cells = verb_data[lemma].get("cells", [])
        conjugations = parse_cells(cells)

        if update_verb_file(note_id, lemma, conjugations, verbs_dir):
            print("✓")
            success_count += 1
        else:
            print("✗ (file not found)")
            error_count += 1

    print()
    print(f"✓ Updated {success_count}/{len(VERB_MAP)} verb files")
    if error_count > 0:
        print(f"✗ {error_count} errors")
    print()
    print("Next steps:")
    print("1. Verify conjugations in updated files")
    print("2. Run: tools/anki/sync/ua_verb_import.py")
    print("3. Commit: git add domains/ua/anki/notes/verbs/")
    print("           git commit -m 'Phase 2a step 5: Populate motion verb conjugations from Горох'")

if __name__ == "__main__":
    main()
