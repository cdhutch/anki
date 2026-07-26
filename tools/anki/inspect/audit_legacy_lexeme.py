#!/usr/bin/env python3
"""Audit UA_Lexeme_Legacy deck to identify notes that can be safely deleted."""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

ANKI_URL = "http://127.0.0.1:8765"


def anki_request(action, params=None, url=ANKI_URL):
    """Call AnkiConnect API."""
    if params is None:
        params = {}
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    try:
        with urllib.request.urlopen(url, payload) as r:
            result = json.loads(r.read())
        if result.get("error"):
            raise Exception(result["error"])
        return result.get("result")
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        raise


def strip_stress(word):
    """Remove combining stress mark (U+0301) from word."""
    if not isinstance(word, str):
        word = str(word)
    return word.replace('́', '')


def get_legacy_notes():
    """Query all notes from UA_Lexeme_Legacy deck."""
    print("Querying UA_Lexeme_Legacy deck from Anki...", file=sys.stderr)
    
    # Try various deck name patterns
    deck_patterns = [
        "deck:UA_Lexeme_Legacy",
        "deck:Ukrainian*Legacy",
        "deck:Inactive*Ukrainian",
        "deck:Legacy*",
    ]
    
    card_ids = []
    found_pattern = None
    for pattern in deck_patterns:
        try:
            card_ids = anki_request("findCards", {"query": pattern})
            if card_ids:
                found_pattern = pattern
                print(f"  Found {len(card_ids)} cards using pattern: {pattern}", file=sys.stderr)
                break
        except:
            continue
    
    legacy_notes = {}
    
    if not card_ids:
        print("No cards found in legacy decks", file=sys.stderr)
        return legacy_notes

    # Get note IDs from cards
    print(f"  Fetching note info...", file=sys.stderr)
    note_ids = anki_request("findNotes", {"query": found_pattern})
    notes_info = anki_request("notesInfo", {"notes": note_ids})

    for note_info in notes_info:
        note_id = note_info.get("noteId")
        if note_id:
            fields_dict = {}
            # notesInfo returns fields as a dict with field names as keys
            for field_name, field_obj in note_info.get("fields", {}).items():
                if isinstance(field_obj, dict):
                    fields_dict[field_name] = {"value": field_obj.get("value", "")}
                else:
                    fields_dict[field_name] = {"value": str(field_obj)}
            legacy_notes[note_id] = fields_dict

    print(f"Found {len(legacy_notes)} unique notes in legacy deck", file=sys.stderr)
    return legacy_notes


def get_canonical_lexemes():
    """Load current UA_Lexeme canonical notes from CNSF files, filtered to 2.9.x only."""
    print("Loading canonical UA_Lexeme notes from CNSF files (2.9.x chapter only)...", file=sys.stderr)

    lexeme_dir = Path(__file__).resolve().parents[3] / "domains" / "ua" / "anki" / "notes" / "lexemes"

    canonical_2_9 = {}
    verified_2_9 = {}

    for md_file in lexeme_dir.rglob("ua-lexeme-*.md"):
        # Only load notes from ch-09 (chapter 2.9.x)
        if "/ch-09/" not in str(md_file):
            continue

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith("---"):
                continue

            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            yaml_section = parts[1]

            lemma = None
            status = None

            for line in yaml_section.split("\n"):
                line_stripped = line.strip()
                if line_stripped.startswith("Lemma:"):
                    lemma = line.split(":", 1)[1].strip()
                elif line_stripped.startswith("status:"):
                    status = line.split(":", 1)[1].strip()
                elif line_stripped.startswith("- status:"):
                    status = 'verified'

            if lemma:
                lemma_base = strip_stress(lemma)
                canonical_2_9[lemma_base] = {
                    'lemma': lemma,
                    'file': str(md_file),
                    'status': status
                }

                if status == 'verified':
                    verified_2_9[lemma_base] = canonical_2_9[lemma_base]
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)
            continue

    print(f"Loaded {len(canonical_2_9)} chapter 2.9 notes ({len(verified_2_9)} verified)", file=sys.stderr)
    return canonical_2_9, verified_2_9


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Write report to file instead of stdout")
    args = parser.parse_args()

    legacy_notes = get_legacy_notes()
    canonical_2_9, verified_2_9 = get_canonical_lexemes()

    if not legacy_notes:
        print("No legacy notes found.", file=sys.stderr)
        return

    safe_to_delete = []
    uncertain = []
    no_match = []

    for note_id, fields in legacy_notes.items():
        lemma = fields.get("Lemma", {}).get("value", "")
        gloss = fields.get("EN_Gloss", {}).get("value", "")

        if not lemma:
            no_match.append((note_id, "NO LEMMA", gloss))
            continue

        lemma_base = strip_stress(lemma)

        if lemma_base in verified_2_9:
            safe_to_delete.append((note_id, lemma, gloss, verified_2_9[lemma_base]['status']))
        elif lemma_base in canonical_2_9:
            uncertain.append((note_id, lemma, gloss, canonical_2_9[lemma_base]['status']))
        else:
            no_match.append((note_id, lemma, gloss))

    lines = []
    lines.append("=" * 80)
    lines.append("UA_Lexeme_Legacy AUDIT REPORT")
    lines.append("=" * 80)
    lines.append("")

    lines.append(f"SUMMARY:")
    lines.append(f"  Total legacy notes: {len(legacy_notes)}")
    lines.append(f"  Safe to delete (verified matches): {len(safe_to_delete)}")
    lines.append(f"  Uncertain (unverified matches): {len(uncertain)}")
    lines.append(f"  No canonical match: {len(no_match)}")
    lines.append("")

    lines.append("=" * 80)
    lines.append(f"SAFE TO DELETE ({len(safe_to_delete)} notes)")
    lines.append("=" * 80)
    for note_id, lemma, gloss, status in sorted(safe_to_delete):
        lines.append(f"  {note_id}: {lemma} — {gloss}")
    if not safe_to_delete:
        lines.append("  (none)")
    lines.append("")

    if uncertain:
        lines.append("=" * 80)
        lines.append(f"UNCERTAIN — REVIEW MANUALLY ({len(uncertain)} notes)")
        lines.append("=" * 80)
        for note_id, lemma, gloss, status in sorted(uncertain)[:50]:
            lines.append(f"  {note_id}: {lemma} ({status}) — {gloss}")
        if len(uncertain) > 50:
            lines.append(f"  ... and {len(uncertain) - 50} more")
        lines.append("")

    if no_match:
        lines.append("=" * 80)
        lines.append(f"NO CANONICAL MATCH ({len(no_match)} notes)")
        lines.append("=" * 80)
        for note_id, lemma, gloss in sorted(no_match)[:50]:
            lines.append(f"  {note_id}: {lemma} — {gloss}")
        if len(no_match) > 50:
            lines.append(f"  ... and {len(no_match) - 50} more")
        lines.append("")

    output = "\n".join(lines)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
