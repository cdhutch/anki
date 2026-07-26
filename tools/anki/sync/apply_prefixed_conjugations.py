#!/usr/bin/env python3
"""Apply conjugations to prefixed motion verbs and mark all files as unverified."""

import yaml
from pathlib import Path

# Base verb conjugations (from Горох)
BASE_CONJUGATIONS = {
    "ходити": {
        "Pres_1sg": "ходжу́",
        "Pres_2sg": "хо́диш",
        "Pres_3sg": "хо́дить",
        "Pres_1pl": "хо́дим",
        "Pres_2pl": "хо́дите",
        "Pres_3pl": "хо́дять",
        "Past_1sg_m": "ходи́в",
        "Past_1sg_f": "ходи́ла",
        "Past_1sg_n": "ходи́ло",
        "Past_3pl": "ходи́ли",
        "Imperative_2sg": "ходи́",
        "Imperative_1pl": "ході́м",
        "Imperative_2pl": "ході́ть",
    },
    "їхати": {
        "Pres_1sg": "ї́ду",
        "Pres_2sg": "їде́ш",
        "Pres_3sg": "їде́",
        "Pres_1pl": "їде́м",
        "Pres_2pl": "їдете́",
        "Pres_3pl": "ї́дуть",
        "Past_1sg_m": "їхав",
        "Past_1sg_f": "їха́ла",
        "Past_1sg_n": "їха́ло",
        "Past_3pl": "їха́ли",
        "Imperative_2sg": "їдь",
        "Imperative_1pl": "їдімте́",
        "Imperative_2pl": "їдіть",
    },
}

# Prefixed verb mapping: (note_id, lemma, prefix, base_verb)
PREFIXED_VERBS = [
    ("0017", "приходити", "при", "ходити"),
    ("0018", "виходити", "ви", "ходити"),
    ("0019", "підходити", "під", "ходити"),
    ("0020", "доходити", "до", "ходити"),
    ("0021", "проходити", "про", "ходити"),
    ("0022", "переходити", "пере", "ходити"),
    ("0023", "заходити", "за", "ходити"),
    ("0024", "відходити", "від", "ходити"),
    ("0025", "приїхати", "при", "їхати"),
    ("0026", "виїхати", "ви", "їхати"),
    ("0027", "підїхати", "під", "їхати"),
    ("0028", "доїхати", "до", "їхати"),
    ("0029", "проїхати", "про", "їхати"),
    ("0030", "переїхати", "пере", "їхати"),
    ("0031", "заїхати", "за", "їхати"),
    ("0032", "відїхати", "від", "їхати"),
]

def apply_prefix(prefix: str, base_form: str) -> str:
    """Apply prefix to a conjugated verb form (with stress marks preserved)."""
    # Simple concatenation - stress marks and phonetic weirdness will need manual review
    return prefix + base_form

def update_file_with_conjugations_and_mark_unverified(note_id: str, conjugations: dict, verbs_dir: Path) -> bool:
    """Update a ua-verb file with conjugations and add stress:unverified tag."""
    file_path = verbs_dir / f"ua-verb-{note_id}.md"

    if not file_path.exists():
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        parts = content.split("---")

        if len(parts) < 3:
            return False

        yaml_str = parts[1].strip()
        yaml_data = yaml.safe_load(yaml_str)

        if not yaml_data:
            return False

        # Add stress:unverified tag if not present
        tags = yaml_data.get("tags", [])
        if "stress:unverified" not in tags:
            tags.append("stress:unverified")
            yaml_data["tags"] = tags

        # Update conjugation fields
        if "fields" in yaml_data:
            for field, value in conjugations.items():
                if value:
                    yaml_data["fields"][field] = value

        # Rebuild YAML
        yaml_output = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{yaml_output}---\n"

        file_path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"    Error: {e}")
        return False

def main():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    print("Applying prefixed conjugations and marking all files as unverified")
    print("=" * 70)
    print()

    # First, mark ALL files as unverified (0001-0032)
    all_files = sorted(verbs_dir.glob("ua-verb-????.md"))
    print(f"Step 1: Mark all {len(all_files)} verb files as stress:unverified")
    print()

    marked_count = 0
    for file_path in all_files:
        note_id = file_path.stem.split("-")[-1]
        print(f"  [{note_id}] ... ", end="", flush=True)

        try:
            content = file_path.read_text(encoding="utf-8")
            parts = content.split("---")
            yaml_str = parts[1].strip()
            yaml_data = yaml.safe_load(yaml_str)

            tags = yaml_data.get("tags", [])
            if "stress:unverified" not in tags:
                tags.append("stress:unverified")
                yaml_data["tags"] = tags

                yaml_output = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{yaml_output}---\n"
                file_path.write_text(new_content, encoding="utf-8")
                print("✓")
                marked_count += 1
            else:
                print("- (already tagged)")
        except Exception as e:
            print(f"✗ ({e})")

    print()
    print(f"✓ Marked {marked_count}/{len(all_files)} files as stress:unverified")
    print()

    # Step 2: Apply prefixed conjugations
    print("Step 2: Apply prefixed conjugations to ua-verb-0017..0032")
    print()

    applied_count = 0
    for note_id, lemma, prefix, base_verb in PREFIXED_VERBS:
        print(f"  [{note_id}] {lemma:15s} ({prefix} + {base_verb:8s}) ... ", end="", flush=True)

        if base_verb not in BASE_CONJUGATIONS:
            print("✗ (base not found)")
            continue

        # Apply prefix to each conjugation form
        base_conj = BASE_CONJUGATIONS[base_verb]
        prefixed_conj = {}
        for field, form in base_conj.items():
            prefixed_conj[field] = apply_prefix(prefix, form)

        if update_file_with_conjugations_and_mark_unverified(note_id, prefixed_conj, verbs_dir):
            print("✓")
            applied_count += 1
        else:
            print("✗ (file update failed)")

    print()
    print(f"✓ Applied prefixed conjugations to {applied_count}/{len(PREFIXED_VERBS)} files")
    print()
    print("⚠️  All conjugations marked stress:unverified")
    print("    Review each form for phonetic correctness:")
    print("    - Stress mark placement may be wrong")
    print("    - Vowel elision or assimilation may occur")
    print("    - Consonant cluster shifts may happen")
    print()
    print("Next: Verify in Anki or against Горох; remove stress:unverified tag when confirmed")

if __name__ == "__main__":
    main()
