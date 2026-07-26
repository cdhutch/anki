#!/usr/bin/env python3
"""Reformat ua-verb CNSF files (0003-0034) to match 0001/0002 schema."""

import yaml
from pathlib import Path

def reformat_files():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    # Mapping of old tag format to new
    tag_mapping = {
        "motion:walking": ["domain:ua", "motion:walking", "phase:2a", "ch:2.9"],
        "motion:vehicle": ["domain:ua", "motion:vehicle", "phase:2a", "ch:2.9"],
        "motion:swimming": ["domain:ua", "motion:swimming", "phase:2a", "ch:2.9"],
        "motion:running": ["domain:ua", "motion:running", "phase:2a", "ch:2.9"],
        "motion:flying": ["domain:ua", "motion:flying", "phase:2a", "ch:2.9"],
    }

    # Aspect mapping
    aspect_mapping = {
        "aspect:imperfective-multidirectional": "imperfective",
        "aspect:imperfective-unidirectional": "imperfective",
        "aspect:perfective": "perfective",
    }

    # Match ua-verb-0003 through ua-verb-0034
    files = [f for f in sorted(verbs_dir.glob("ua-verb-????.md"))
             if 3 <= int(f.stem.split("-")[-1]) <= 34]

    print(f"Reformatting {len(files)} files to match 0001/0002 schema...\n")

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")

        # Parse existing YAML
        parts = content.split("---")
        yaml_str = parts[1].strip()
        yaml_data = yaml.safe_load(yaml_str)

        # Extract data
        note_id = yaml_data.get("note_id", "")
        lemma = yaml_data.get("fields", {}).get("Lemma", "")
        en_gloss = yaml_data.get("fields", {}).get("EN_Gloss", "")
        old_tags = yaml_data.get("tags", [])

        # Determine aspect and motion type
        aspect = "imperfective"
        motion_type = ""
        for tag in old_tags:
            if tag.startswith("aspect:"):
                aspect = aspect_mapping.get(tag, "imperfective")
            if tag.startswith("motion:"):
                motion_type = tag

        # Build new tags
        new_tags = []
        if motion_type in tag_mapping:
            new_tags = tag_mapping[motion_type][:]
        else:
            new_tags = ["domain:ua", "phase:2a", "ch:2.9"]

        # Add phonetic-variant or prefixed tags if present
        if "phonetic-variant" in old_tags:
            new_tags.append("phonetic-variant")
        if "prefixed" in old_tags:
            new_tags.append("class:prefixed")
        else:
            new_tags.append("conj:drill")  # Default for non-prefixed

        # Build new YAML structure
        new_yaml = {
            "schema": "cnsf/v0",
            "note_type": "ua_verb",
            "note_id": note_id,
            "anki": {
                "model": "UA_Verb",
                "deck": "UA::Verbs",
            },
            "tags": new_tags,
            "fields": {
                "NoteID": note_id,
                "Lemma": lemma,
                "Aspect": aspect,
                "VerbClass": f"motion-{motion_type.split(':')[1]}-new" if motion_type else "motion-new",
                "FreqSource": "ch:2.9",
                "Pres_1sg": "",
                "Pres_2sg": "",
                "Pres_3sg": "",
                "Pres_1pl": "",
                "Pres_2pl": "",
                "Pres_3pl": "",
                "Imperative_2sg": "",
                "Imperative_1pl": "",
                "Imperative_2pl": "",
                "Past_1sg_m": "",
                "Past_1sg_f": "",
                "Past_1sg_n": "",
                "Past_3pl": "",
                "Participle_Active_Present": "",
                "Participle_Adverbial_Present": "",
                "Participle_Passive_Past_m": "",
                "Participle_Passive_Past_f": "",
                "Participle_Impersonal_Past": "",
                "Participle_Adverbial_Past": "",
                "UA_Example": "",
                "EN_Example": "",
                "Verification_Notes": "",
            },
        }

        # Write reformatted YAML
        yaml_output = yaml.dump(new_yaml, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_output}---\n"

        file_path.write_text(new_content, encoding="utf-8")
        print(f"✓ {file_path.name}")

    print(f"\n✓ Reformatted {len(files)} files to match 0001/0002 schema.")

if __name__ == "__main__":
    reformat_files()
