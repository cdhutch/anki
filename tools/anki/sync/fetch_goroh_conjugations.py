#!/usr/bin/env python3
"""Batch fetch Ukrainian verb conjugations from Горох and populate CNSF files."""

import requests
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
import time
import re

# Verb mapping: (note_id, lemma)
VERBS = [
    ("0001", "ходити"),
    ("0002", "іти"),
    ("0003", "йти"),
    ("0004", "піти"),
    ("0005", "їздити"),
    ("0006", "їхати"),
    ("0007", "поїхати"),
    ("0008", "плавати"),
    ("0009", "пливти"),
    ("0010", "попливти"),
    ("0011", "бігати"),
    ("0012", "бігти"),
    ("0013", "побігти"),
    ("0014", "літати"),
    ("0015", "летіти"),
    ("0016", "полетіти"),
    ("0017", "приходити"),
    ("0018", "виходити"),
    ("0019", "підходити"),
    ("0020", "доходити"),
    ("0021", "проходити"),
    ("0022", "переходити"),
    ("0023", "заходити"),
    ("0024", "відходити"),
    ("0025", "приїхати"),
    ("0026", "виїхати"),
    ("0027", "підїхати"),
    ("0028", "доїхати"),
    ("0029", "проїхати"),
    ("0030", "переїхати"),
    ("0031", "заїхати"),
    ("0032", "відїхати"),
]

def fetch_conjugations(lemma):
    """Fetch conjugation data from Горох."""
    url = f"https://goroh.pp.ua/Словозміна/{lemma}"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"  ✗ Error fetching {lemma}: {e}")
        return None

def parse_горох_html(html):
    """Parse Горох HTML and extract conjugation forms."""
    soup = BeautifulSoup(html, 'html.parser')

    # Extract all table cells
    cells = [td.get_text(strip=True) for td in soup.find_all('td')]

    forms = {
        "Pres_1sg": "", "Pres_2sg": "", "Pres_3sg": "",
        "Pres_1pl": "", "Pres_2pl": "", "Pres_3pl": "",
        "Past_1sg_m": "", "Past_1sg_f": "", "Past_1sg_n": "", "Past_3pl": "",
        "Imperative_2sg": "", "Imperative_1pl": "", "Imperative_2pl": "",
        "Participle_Active_Present": "", "Participle_Adverbial_Present": "",
        "Participle_Passive_Past_m": "", "Participle_Passive_Past_f": "",
        "Participle_Impersonal_Past": "", "Participle_Adverbial_Past": "",
    }

    try:
        # Find indices of key sections
        present_idx = next(i for i, c in enumerate(cells) if "Теперішній" in c)
        past_idx = next(i for i, c in enumerate(cells) if "Минулий" in c)
        imperative_idx = next(i for i, c in enumerate(cells) if "Наказовий" in c)

        # Extract Present tense (appears after "Теперішній час")
        present_section = cells[present_idx:past_idx]
        # Pattern: "Теперішній час", "1 особа", [1sg], [1pl], "2 особа", [2sg], [2pl], "3 особа", [3sg], [3pl]
        for i, cell in enumerate(present_section):
            if cell == "1 особа" and i+1 < len(present_section):
                forms["Pres_1sg"] = present_section[i+1].split(',')[0].strip() if present_section[i+1] else ""
                if i+2 < len(present_section) and present_section[i+2] != "2 особа":
                    forms["Pres_1pl"] = present_section[i+2].split(',')[0].strip() if present_section[i+2] else ""
            elif cell == "2 особа" and i+1 < len(present_section):
                forms["Pres_2sg"] = present_section[i+1].split(',')[0].strip() if present_section[i+1] else ""
                if i+2 < len(present_section) and present_section[i+2] != "3 особа":
                    forms["Pres_2pl"] = present_section[i+2].split(',')[0].strip() if present_section[i+2] else ""
            elif cell == "3 особа" and i+1 < len(present_section):
                forms["Pres_3sg"] = present_section[i+1].split(',')[0].strip() if present_section[i+1] else ""
                if i+2 < len(present_section):
                    forms["Pres_3pl"] = present_section[i+2].split(',')[0].strip() if present_section[i+2] else ""

        # Extract Past tense
        past_section = cells[past_idx:imperative_idx] if imperative_idx > past_idx else cells[past_idx:]
        for i, cell in enumerate(past_section):
            if "чол. р." in cell and i+1 < len(past_section):
                forms["Past_1sg_m"] = past_section[i+1].split(',')[0].strip() if past_section[i+1] else ""
            elif "жін. р." in cell and i+1 < len(past_section):
                forms["Past_1sg_f"] = past_section[i+1].split(',')[0].strip() if past_section[i+1] else ""
            elif "сер. р." in cell and i+1 < len(past_section):
                forms["Past_1sg_n"] = past_section[i+1].split(',')[0].strip() if past_section[i+1] else ""

        # Try to find plural past
        for i, cell in enumerate(past_section):
            if cell == "ходили" or (i > 0 and "ли" in cell and past_section[i-1] in ["жін. р.", "сер. р."]):
                forms["Past_3pl"] = cell
                break

        # Extract Imperative
        imp_section = cells[imperative_idx:]
        for i, cell in enumerate(imp_section):
            if cell == "2 особа" and i+1 < len(imp_section):
                forms["Imperative_2sg"] = imp_section[i+1].split(',')[0].strip() if imp_section[i+1] else ""
            elif cell == "1 особа" and i+1 < len(imp_section):
                forms["Imperative_1pl"] = imp_section[i+1].split(',')[0].strip() if imp_section[i+1] else ""
            # 2pl comes after 2sg or another value

    except (StopIteration, IndexError, ValueError):
        pass

    return forms

def update_verb_file(note_id, lemma, conjugations, verbs_dir):
    """Update a ua-verb file with conjugation data."""
    file_path = verbs_dir / f"ua-verb-{note_id}.md"

    if not file_path.exists():
        return False

    # Read existing file
    content = file_path.read_text(encoding="utf-8")
    parts = content.split("---")
    yaml_str = parts[1].strip()
    yaml_data = yaml.safe_load(yaml_str)

    # Update conjugation fields
    for field, value in conjugations.items():
        if value and field in yaml_data.get("fields", {}):
            yaml_data["fields"][field] = value

    # Rebuild YAML
    yaml_output = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{yaml_output}---\n"

    file_path.write_text(new_content, encoding="utf-8")
    return True

def main():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    print(f"Fetching conjugations from Горох for {len(VERBS)} verbs...\n")

    success_count = 0
    for note_id, lemma in VERBS:
        print(f"  [{note_id}] {lemma}... ", end="", flush=True)

        html = fetch_conjugations(lemma)
        if not html:
            print("✗ fetch failed")
            continue

        conjugations = parse_горох_html(html)
        if update_verb_file(note_id, lemma, conjugations, verbs_dir):
            print("✓")
            success_count += 1
        else:
            print("✗ update failed")

        time.sleep(0.2)  # Rate limiting

    print(f"\n✓ Updated {success_count}/{len(VERBS)} verb files.")

if __name__ == "__main__":
    main()
