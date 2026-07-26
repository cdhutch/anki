#!/usr/bin/env python3
"""Create UA_Verb CNSF skeleton files for batch authoring.

Generates CNSF template files with metadata and example sentences,
ready for manual population of conjugation forms from Горох.

Usage:
    python tools/anki/generate/generate_ua_verb_skeleton.py --chapter 2.9.2
    python tools/anki/generate/generate_ua_verb_skeleton.py --chapter 2.9.4

Workflow:
    1. Run this script to generate skeleton files
    2. Open each file and fill in conjugation forms from Горох
    3. Import to Anki via ua_verb_import.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Chapter 2.9 verb groups
CHAPTER_2_9_VERBS = {
    "2.9.2_base": {
        "description": "Base motion verbs (3-verb groups: multidirectional, unidirectional, perfective)",
        "verbs": [
            # Walking: ходити (multi) / йти (uni) / піти (perf)
            # Note: ходити already exists as ua-verb-0001, retag for phase 2a
            {"lemma": "ходити", "type": "multidirectional", "group": "walking", "en_gloss": "to walk (habitual)", "tags": ["motion:walking", "aspect:imperfective-multidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "іти", "type": "unidirectional", "group": "walking", "alt_lemma": "йти", "en_gloss": "to go (on foot, direction)", "tags": ["motion:walking", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "йти", "type": "unidirectional", "group": "walking", "alt_lemma": "іти", "en_gloss": "to go (on foot, direction) — phonetic variant", "tags": ["motion:walking", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2", "phonetic-variant"]},
            {"lemma": "піти", "type": "perfective", "group": "walking", "base": "йти", "en_gloss": "to go (on foot, perfective)", "tags": ["motion:walking", "aspect:perfective", "phase:2a", "chapter:2.9.2"]},
            # Vehicle: їздити (multi) / їхати (uni) / поїхати (perf)
            {"lemma": "їздити", "type": "multidirectional", "group": "vehicle", "en_gloss": "to ride/drive (habitual)", "tags": ["motion:vehicle", "aspect:imperfective-multidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "їхати", "type": "unidirectional", "group": "vehicle", "en_gloss": "to ride/drive (direction)", "tags": ["motion:vehicle", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "поїхати", "type": "perfective", "group": "vehicle", "base": "їхати", "en_gloss": "to go (by vehicle, perfective)", "tags": ["motion:vehicle", "aspect:perfective", "phase:2a", "chapter:2.9.2"]},
            # Swimming: плавати (multi) / пливти (uni) / поплисти (perf)
            {"lemma": "плавати", "type": "multidirectional", "group": "swimming", "en_gloss": "to swim (habitual)", "tags": ["motion:swimming", "aspect:imperfective-multidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "пливти", "type": "unidirectional", "group": "swimming", "en_gloss": "to swim (direction)", "tags": ["motion:swimming", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "поплисти", "type": "perfective", "group": "swimming", "base": "пливти", "en_gloss": "to swim (perfective)", "tags": ["motion:swimming", "aspect:perfective", "phase:2a", "chapter:2.9.2"]},
            # Running: бігати (multi) / бігти (uni) / побігти (perf)
            {"lemma": "бігати", "type": "multidirectional", "group": "running", "en_gloss": "to run (habitual)", "tags": ["motion:running", "aspect:imperfective-multidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "бігти", "type": "unidirectional", "group": "running", "en_gloss": "to run (direction)", "tags": ["motion:running", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "побігти", "type": "perfective", "group": "running", "base": "бігти", "en_gloss": "to run (perfective)", "tags": ["motion:running", "aspect:perfective", "phase:2a", "chapter:2.9.2"]},
            # Flying: літати (multi) / летіти (uni) / полетіти (perf)
            {"lemma": "літати", "type": "multidirectional", "group": "flying", "en_gloss": "to fly (habitual)", "tags": ["motion:flying", "aspect:imperfective-multidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "летіти", "type": "unidirectional", "group": "flying", "en_gloss": "to fly (direction)", "tags": ["motion:flying", "aspect:imperfective-unidirectional", "phase:2a", "chapter:2.9.2"]},
            {"lemma": "полетіти", "type": "perfective", "group": "flying", "base": "летіти", "en_gloss": "to fly (perfective)", "tags": ["motion:flying", "aspect:perfective", "phase:2a", "chapter:2.9.2"]},
        ],
    },
    "2.9.4_prefixed": {
        "description": "Prefixed motion verbs (ходити and їхати bases with standard prefixes)",
        "verbs": [
            # ходити base with prefixes
            {"lemma": "приходити", "base": "ходити", "prefix": "при-", "en_gloss": "to arrive (on foot)", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "виходити", "base": "ходити", "prefix": "ви-", "en_gloss": "to exit", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "підходити", "base": "ходити", "prefix": "під-", "en_gloss": "to approach", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "доходити", "base": "ходити", "prefix": "до-", "en_gloss": "to reach (on foot)", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "проходити", "base": "ходити", "prefix": "про-", "en_gloss": "to pass through", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "переходити", "base": "ходити", "prefix": "пере-", "en_gloss": "to cross", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "заходити", "base": "ходити", "prefix": "за-", "en_gloss": "to stop by (on foot)", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "відходити", "base": "ходити", "prefix": "від-", "en_gloss": "to depart", "tags": ["motion:walking", "prefixed", "phase:2a", "chapter:2.9.4"]},
            # їхати base with same prefixes
            {"lemma": "приїхати", "base": "їхати", "prefix": "при-", "en_gloss": "to arrive (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "виїхати", "base": "їхати", "prefix": "ви-", "en_gloss": "to leave (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "підїхати", "base": "їхати", "prefix": "під-", "en_gloss": "to drive up to", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "доїхати", "base": "їхати", "prefix": "до-", "en_gloss": "to reach (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "проїхати", "base": "їхати", "prefix": "про-", "en_gloss": "to drive through", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "переїхати", "base": "їхати", "prefix": "пере-", "en_gloss": "to cross (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "заїхати", "base": "їхати", "prefix": "за-", "en_gloss": "to stop by (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
            {"lemma": "відїхати", "base": "їхати", "prefix": "від-", "en_gloss": "to depart (by vehicle)", "tags": ["motion:vehicle", "prefixed", "phase:2a", "chapter:2.9.4"]},
        ],
    },
}


def create_ua_verb_cnsf_skeleton(
    note_id: str,
    lemma: str,
    en_gloss: str,
    tags: list[str] | None = None,
) -> str:
    """Create CNSF template for a UA_Verb note (skeleton with empty conjugation fields).

    Returns YAML string ready to write to file.
    """
    tags = tags or ["status:draft", "phase:2a"]

    yaml_dict = {
        "note_id": note_id,
        "note_type": "ua_verb",
        "deck": "UA::Verbs",
        "tags": tags,
        "fields": {
            "Lemma": lemma,
            "EN_Gloss": en_gloss,
            # Conjugation fields (EMPTY — to be filled from Горох)
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
            "UA_Example": "",
            "EN_Example": "",
            "Verification_Notes": f"Conjugation forms to be filled from Горох (goroh.pp.ua/{lemma})",
            "Source_URL": f"https://goroh.pp.ua/Словозміна/{lemma}",
        },
    }

    # Build YAML frontmatter (preserve Cyrillic characters)
    yaml_lines = ["---"]
    yaml_lines.append(f"note_id: {json.dumps(yaml_dict['note_id'], ensure_ascii=False)}")
    yaml_lines.append(f"note_type: {json.dumps(yaml_dict['note_type'], ensure_ascii=False)}")
    yaml_lines.append(f"deck: {json.dumps(yaml_dict['deck'], ensure_ascii=False)}")
    yaml_lines.append(f"tags: {json.dumps(yaml_dict['tags'], ensure_ascii=False)}")
    yaml_lines.append("fields:")
    for field_name, field_value in yaml_dict["fields"].items():
        yaml_lines.append(f"  {field_name}: {json.dumps(field_value, ensure_ascii=False)}")
    yaml_lines.append("---\n")

    return "\n".join(yaml_lines)


def generate_skeletons(chapter: str = "all", dry_run: bool = False):
    """Generate UA_Verb skeleton CNSF files."""
    output_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"Generating UA_Verb skeleton files for Chapter {chapter}")
    print(f"{'='*80}\n")

    # Collect verbs to generate
    verbs_to_gen = []
    if chapter == "2.9.2":
        verbs_to_gen = CHAPTER_2_9_VERBS["2.9.2_base"]["verbs"]
    elif chapter == "2.9.4":
        verbs_to_gen = CHAPTER_2_9_VERBS["2.9.4_prefixed"]["verbs"]
    else:  # all
        verbs_to_gen = (
            CHAPTER_2_9_VERBS["2.9.2_base"]["verbs"]
            + CHAPTER_2_9_VERBS["2.9.4_prefixed"]["verbs"]
        )

    # Find max existing note ID to auto-increment
    existing_ids = list(output_dir.glob("ua-verb-*.md"))
    if existing_ids:
        max_id = max(int(f.stem.split("-")[-1]) for f in existing_ids)
        next_id = max_id + 1
    else:
        next_id = 3  # Start after 0001 (ходити) and 0002 (їхати)

    generated = 0
    skipped = 0

    for verb_data in verbs_to_gen:
        lemma = verb_data["lemma"]
        en_gloss = verb_data.get("en_gloss", f"to [action: {lemma}]")
        tags = verb_data.get("tags", ["status:draft", "phase:2a"])

        note_id = f"ua-verb-{next_id:04d}"
        print(f"[{next_id}] {lemma:20s} → {note_id}")

        # Create CNSF skeleton
        cnsf_content = create_ua_verb_cnsf_skeleton(
            note_id=note_id,
            lemma=lemma,
            en_gloss=en_gloss,
            tags=tags,
        )

        # Write file
        output_file = output_dir / f"{note_id}.md"
        if not dry_run:
            output_file.write_text(cnsf_content, encoding="utf-8")
            print(f"       Created: {output_file.name}")
        else:
            print(f"       DRY RUN: Would create {output_file.name}")

        generated += 1
        next_id += 1

    print(f"\n✓ Done: {generated} skeletons created, {skipped} skipped.")
    print(f"\nNext steps:")
    print(f"  1. Open each file in domains/ua/anki/notes/verbs/")
    print(f"  2. Fill conjugation fields from Горох (goroh.pp.ua/Словозміна/[lemma])")
    print(f"  3. Add example sentences in UA_Example and EN_Example fields")
    print(f"  4. Change status:draft → status:verified when complete")
    print(f"  5. Run: python tools/anki/sync/ua_verb_import.py domains/ua/anki/notes/verbs/")


def main():
    parser = argparse.ArgumentParser(description="Generate UA_Verb skeleton CNSF files")
    parser.add_argument(
        "--chapter",
        choices=["2.9.2", "2.9.4", "all"],
        default="all",
        help="Chapter to generate skeletons for (default: all)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    args = parser.parse_args()

    generate_skeletons(chapter=args.chapter, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
