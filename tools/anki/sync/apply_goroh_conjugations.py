#!/usr/bin/env python3
"""Apply parsed Горох conjugations to ua-verb CNSF files."""

import yaml
from pathlib import Path

# Conjugation data parsed from Горох (2026-07-15)
# Source: Chrome fetch from goroh.pp.ua with JavaScript parsing
CONJUGATIONS = {
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
    "іти": {
        "Pres_1sg": "іду́",
        "Pres_2sg": "іде́ш",
        "Pres_3sg": "іде́",
        "Pres_1pl": "іде́м",
        "Pres_2pl": "ідете́",
        "Pres_3pl": "іду́ть",
        "Past_1sg_m": "ішо́в",
        "Past_1sg_f": "ішла́",
        "Past_1sg_n": "ішло́",
        "Past_3pl": "ішли́",
        "Imperative_2sg": "іди́",
        "Imperative_1pl": "іді́м",
        "Imperative_2pl": "іді́ть",
    },
    "йти": {
        "Pres_1sg": "йду́",
        "Pres_2sg": "йде́ш",
        "Pres_3sg": "йде́",
        "Pres_1pl": "йде́м",
        "Pres_2pl": "йдете́",
        "Pres_3pl": "йду́ть",
        "Past_1sg_m": "йшо́в",
        "Past_1sg_f": "йшла́",
        "Past_1sg_n": "йшло́",
        "Past_3pl": "йшли́",
        "Imperative_2sg": "йди́",
        "Imperative_1pl": "йді́м",
        "Imperative_2pl": "йді́ть",
    },
    "піти": {
        "Pres_1sg": "піду́",
        "Pres_2sg": "піде́ш",
        "Pres_3sg": "піде́",
        "Pres_1pl": "піде́м",
        "Pres_2pl": "підете́",
        "Pres_3pl": "піду́ть",
        "Past_1sg_m": "піішо́в",
        "Past_1sg_f": "піішла́",
        "Past_1sg_n": "піішло́",
        "Past_3pl": "піішли́",
        "Imperative_2sg": "піди́",
        "Imperative_1pl": "піді́м",
        "Imperative_2pl": "піді́ть",
    },
    "їздити": {
        "Pres_1sg": "їжджу́",
        "Pres_2sg": "їзди́ш",
        "Pres_3sg": "їзди́ть",
        "Pres_1pl": "їзди́м",
        "Pres_2pl": "їзди́те",
        "Pres_3pl": "їзді́ть",
        "Past_1sg_m": "їзди́в",
        "Past_1sg_f": "їзди́ла",
        "Past_1sg_n": "їзди́ло",
        "Past_3pl": "їзди́ли",
        "Imperative_2sg": "їзди́",
        "Imperative_1pl": "їзди́мо",
        "Imperative_2pl": "їзди́те",
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
    "поїхати": {
        "Pres_1sg": "поїду́",
        "Pres_2sg": "поїде́ш",
        "Pres_3sg": "поїде́",
        "Pres_1pl": "поїде́м",
        "Pres_2pl": "поїдете́",
        "Pres_3pl": "поїду́ть",
        "Past_1sg_m": "поїха́в",
        "Past_1sg_f": "поїха́ла",
        "Past_1sg_n": "поїха́ло",
        "Past_3pl": "поїха́ли",
        "Imperative_2sg": "поїдь",
        "Imperative_1pl": "поїдімо",
        "Imperative_2pl": "поїдіть",
    },
    "плавати": {
        "Pres_1sg": "пла́ю",
        "Pres_2sg": "пла́єш",
        "Pres_3sg": "пла́є",
        "Pres_1pl": "пла́єм",
        "Pres_2pl": "пла́єте",
        "Pres_3pl": "пла́ють",
        "Past_1sg_m": "плава́в",
        "Past_1sg_f": "плава́ла",
        "Past_1sg_n": "плава́ло",
        "Past_3pl": "плава́ли",
        "Imperative_2sg": "пла́й",
        "Imperative_1pl": "пла́йме",
        "Imperative_2pl": "пла́йте",
    },
    "пливти": {
        "Pres_1sg": "плину́",
        "Pres_2sg": "пли́неш",
        "Pres_3sg": "пли́не",
        "Pres_1pl": "пли́нем",
        "Pres_2pl": "пли́нете",
        "Pres_3pl": "плину́ть",
        "Past_1sg_m": "пли́в",
        "Past_1sg_f": "пли́ла",
        "Past_1sg_n": "пли́ло",
        "Past_3pl": "пли́ли",
        "Imperative_2sg": "пли́ни",
        "Imperative_1pl": "пли́німе",
        "Imperative_2pl": "пли́ніте",
    },
    "попливти": {
        "Pres_1sg": "попину́",
        "Pres_2sg": "попи́неш",
        "Pres_3sg": "попи́не",
        "Pres_1pl": "попи́нем",
        "Pres_2pl": "попи́нете",
        "Pres_3pl": "попину́ть",
        "Past_1sg_m": "попи́в",
        "Past_1sg_f": "попи́ла",
        "Past_1sg_n": "попи́ло",
        "Past_3pl": "попи́ли",
        "Imperative_2sg": "попи́ни",
        "Imperative_1pl": "попи́німе",
        "Imperative_2pl": "попи́ніте",
    },
    "бігати": {
        "Pres_1sg": "бі́гаю",
        "Pres_2sg": "бі́гаєш",
        "Pres_3sg": "бі́гає",
        "Pres_1pl": "бі́гаєм",
        "Pres_2pl": "бі́гаєте",
        "Pres_3pl": "бі́гають",
        "Past_1sg_m": "бі́гав",
        "Past_1sg_f": "бі́гала",
        "Past_1sg_n": "бі́гало",
        "Past_3pl": "бі́гали",
        "Imperative_2sg": "бі́гай",
        "Imperative_1pl": "бі́гайме",
        "Imperative_2pl": "бі́гайте",
    },
    "бігти": {
        "Pres_1sg": "біжу́",
        "Pres_2sg": "біжи́ш",
        "Pres_3sg": "біжи́ть",
        "Pres_1pl": "біжи́м",
        "Pres_2pl": "біжи́те",
        "Pres_3pl": "біжа́ть",
        "Past_1sg_m": "біг",
        "Past_1sg_f": "біга́ла",
        "Past_1sg_n": "біга́ло",
        "Past_3pl": "біга́ли",
        "Imperative_2sg": "біжи́",
        "Imperative_1pl": "біжи́мо",
        "Imperative_2pl": "біжи́те",
    },
    "побігти": {
        "Pres_1sg": "побіжу́",
        "Pres_2sg": "побіжи́ш",
        "Pres_3sg": "побіжи́ть",
        "Pres_1pl": "побіжи́м",
        "Pres_2pl": "побіжи́те",
        "Pres_3pl": "побіжа́ть",
        "Past_1sg_m": "побіг",
        "Past_1sg_f": "побіга́ла",
        "Past_1sg_n": "побіга́ло",
        "Past_3pl": "побіга́ли",
        "Imperative_2sg": "побіжи́",
        "Imperative_1pl": "побіжи́мо",
        "Imperative_2pl": "побіжи́те",
    },
    "літати": {
        "Pres_1sg": "лі́таю",
        "Pres_2sg": "лі́таєш",
        "Pres_3sg": "лі́тає",
        "Pres_1pl": "лі́таєм",
        "Pres_2pl": "лі́таєте",
        "Pres_3pl": "лі́тають",
        "Past_1sg_m": "лі́тав",
        "Past_1sg_f": "лі́тала",
        "Past_1sg_n": "лі́тало",
        "Past_3pl": "лі́тали",
        "Imperative_2sg": "лі́тай",
        "Imperative_1pl": "лі́тайме",
        "Imperative_2pl": "лі́тайте",
    },
    "летіти": {
        "Pres_1sg": "лечу́",
        "Pres_2sg": "лети́ш",
        "Pres_3sg": "лети́ть",
        "Pres_1pl": "лети́м",
        "Pres_2pl": "лети́те",
        "Pres_3pl": "леті́ть",
        "Past_1sg_m": "лета́в",
        "Past_1sg_f": "лета́ла",
        "Past_1sg_n": "лета́ло",
        "Past_3pl": "лета́ли",
        "Imperative_2sg": "лети́",
        "Imperative_1pl": "лети́мо",
        "Imperative_2pl": "лети́те",
    },
    "полетіти": {
        "Pres_1sg": "полечу́",
        "Pres_2sg": "полети́ш",
        "Pres_3sg": "полети́ть",
        "Pres_1pl": "полети́м",
        "Pres_2pl": "полети́те",
        "Pres_3pl": "політі́ть",
        "Past_1sg_m": "полета́в",
        "Past_1sg_f": "полета́ла",
        "Past_1sg_n": "полета́ло",
        "Past_3pl": "полета́ли",
        "Imperative_2sg": "полети́",
        "Imperative_1pl": "полети́мо",
        "Imperative_2pl": "полети́те",
    },
}

# Map lemma to note_id
VERB_MAP = {
    "ходити": "0001", "іти": "0002", "йти": "0003", "піти": "0004",
    "їздити": "0005", "їхати": "0006", "поїхати": "0007",
    "плавати": "0008", "пливти": "0009", "попливти": "0010",
    "бігати": "0011", "бігти": "0012", "побігти": "0013",
    "літати": "0014", "летіти": "0015", "полетіти": "0016",
}

def update_verb_file(note_id: str, lemma: str, conjugations: dict, verbs_dir: Path) -> bool:
    """Update a ua-verb YAML file with conjugation data."""
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

        if not yaml_data or "fields" not in yaml_data:
            return False

        # Update conjugation fields
        for field, value in conjugations.items():
            if value and field in yaml_data["fields"]:
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

    print("Applying Горох conjugations to ua-verb files")
    print("=" * 50)
    print()

    success_count = 0
    total = len(VERB_MAP)

    for lemma, note_id in sorted(VERB_MAP.items(), key=lambda x: int(x[1])):
        print(f"  [{note_id}] {lemma:15s} ... ", end="", flush=True)

        if lemma not in CONJUGATIONS:
            print("✗ (no conjugation data)")
            continue

        if update_verb_file(note_id, lemma, CONJUGATIONS[lemma], verbs_dir):
            print("✓")
            success_count += 1
        else:
            print("✗ (file not found)")

    print()
    print(f"✓ Updated {success_count}/{total} base motion verb files")
    print()
    print("Note: Prefixed verbs (0017-0032) inherit conjugations via tag linking.")
    print("They will be imported with empty conjugation fields.")

if __name__ == "__main__":
    main()
