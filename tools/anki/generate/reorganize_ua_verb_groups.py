#!/usr/bin/env python3
"""Reorganize ua-verb files to group by verb family and renumber sequentially."""

import shutil
import yaml
from pathlib import Path

def reorganize():
    verbs_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "verbs"

    # Define verb groups in order (keeping 0001, 0002 as anchors)
    verb_groups = [
        # Walking group (ходити already 0001)
        {
            "id": "0001",
            "lemma": "ходити",
            "note": "existing - multidirectional walking",
        },
        {
            "source_id": "0004",  # was 0004, becomes 0002
            "lemma": "іти",
            "note": "unidirectional walking",
        },
        {
            "source_id": "0005",  # was 0005, becomes 0003
            "lemma": "йти",
            "note": "phonetic variant - unidirectional walking",
        },
        {
            "source_id": "0006",  # was 0006, becomes 0004
            "lemma": "піти",
            "note": "perfective walking",
        },
        # Vehicle group (їздити already 0002, but becomes 0005 after reshuffle)
        {
            "id": "0002",
            "lemma": "їздити",
            "note": "existing - multidirectional vehicle",
        },
        {
            "source_id": "0008",  # was 0008, becomes 0006
            "lemma": "їхати",
            "note": "unidirectional vehicle",
        },
        {
            "source_id": "0009",  # was 0009, becomes 0007
            "lemma": "поїхати",
            "note": "perfective vehicle",
        },
        # Swimming group
        {
            "source_id": "0010",  # was 0010, becomes 0008
            "lemma": "плавати",
            "note": "multidirectional swimming",
        },
        {
            "source_id": "0011",  # was 0011, becomes 0009
            "lemma": "пливти",
            "note": "unidirectional swimming",
        },
        {
            "source_id": "0012",  # was 0012, becomes 0010
            "lemma": "поплисти",
            "note": "perfective swimming",
        },
        # Running group
        {
            "source_id": "0013",  # was 0013, becomes 0011
            "lemma": "бігати",
            "note": "multidirectional running",
        },
        {
            "source_id": "0014",  # was 0014, becomes 0012
            "lemma": "бігти",
            "note": "unidirectional running",
        },
        {
            "source_id": "0015",  # was 0015, becomes 0013
            "lemma": "побігти",
            "note": "perfective running",
        },
        # Flying group
        {
            "source_id": "0016",  # was 0016, becomes 0014
            "lemma": "літати",
            "note": "multidirectional flying",
        },
        {
            "source_id": "0017",  # was 0017, becomes 0015
            "lemma": "летіти",
            "note": "unidirectional flying",
        },
        {
            "source_id": "0018",  # was 0018, becomes 0016
            "lemma": "полетіти",
            "note": "perfective flying",
        },
        # Prefixed verbs (0019-0034 become 0017-0032)
        {
            "source_id": "0019",
            "lemma": "приходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0020",
            "lemma": "виходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0021",
            "lemma": "підходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0022",
            "lemma": "доходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0023",
            "lemma": "проходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0024",
            "lemma": "переходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0025",
            "lemma": "заходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0026",
            "lemma": "відходити",
            "note": "prefixed ходити",
        },
        {
            "source_id": "0027",
            "lemma": "приїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0028",
            "lemma": "виїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0029",
            "lemma": "підїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0030",
            "lemma": "доїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0031",
            "lemma": "проїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0032",
            "lemma": "переїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0033",
            "lemma": "заїхати",
            "note": "prefixed їхати",
        },
        {
            "source_id": "0034",
            "lemma": "відїхати",
            "note": "prefixed їхати",
        },
    ]

    print("Reorganizing and renumbering verb groups...\n")

    # Process each verb
    for new_index, verb_info in enumerate(verb_groups, start=1):
        new_id = f"{new_index:04d}"

        if "id" in verb_info:
            # Keep existing files as-is (0001, 0002)
            print(f"  {new_id}: {verb_info['lemma']} (keep existing)")
            continue

        source_id = verb_info["source_id"]
        lemma = verb_info["lemma"]
        old_file = verbs_dir / f"ua-verb-{source_id}.md"
        new_file = verbs_dir / f"ua-verb-{new_id}.md"

        if not old_file.exists():
            print(f"  ✗ {new_id}: {lemma} (source file not found: {old_file.name})")
            continue

        # Read old file
        content = old_file.read_text(encoding="utf-8")

        # Update note_id and NoteID field in YAML
        content = content.replace(f'note_id: ua-verb-{source_id}', f'note_id: ua-verb-{new_id}')
        content = content.replace(f'NoteID: ua-verb-{source_id}', f'NoteID: ua-verb-{new_id}')

        # Write to new location
        new_file.write_text(content, encoding="utf-8")

        # Note: old file will be deleted via git rm (sandbox permission issue)

        print(f"  ✓ {new_id}: {lemma}")

    print(f"\n✓ Reorganized and renumbered all verbs.")
    print(f"\nVerb grouping:")
    print(f"  0001-0004: Walking (ходити, іти, йти, піти)")
    print(f"  0005-0007: Vehicle (їздити, їхати, поїхати)")
    print(f"  0008-0010: Swimming (плавати, пливти, поплисти)")
    print(f"  0011-0013: Running (бігати, бігти, побігти)")
    print(f"  0014-0016: Flying (літати, летіти, полетіти)")
    print(f"  0017-0032: Prefixed verbs (8 ходити-based + 8 їхати-based)")

if __name__ == "__main__":
    reorganize()
