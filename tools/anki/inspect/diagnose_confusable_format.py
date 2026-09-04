#!/usr/bin/env python3
"""
Diagnose current ConfusableSet format to understand what we're working with.

Shows sample notes with their current ConfusableSet content to identify the
actual format before making further migration attempts.
"""

import re
import yaml
from pathlib import Path
from typing import Dict


def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter and body from markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None, None
    yaml_content = match.group(1)
    body = match.group(2)
    return yaml_content, body


def load_corpus(lexeme_root):
    """Load all lexeme notes."""
    notes = []
    errors = []

    md_files = list(lexeme_root.glob('**/*.md'))

    for filepath in sorted(md_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_content, body = parse_yaml_frontmatter(content)
            if yaml_content is None:
                continue

            note_data = yaml.safe_load(yaml_content)
            if note_data is None:
                continue

            note_id = note_data.get('note_id') or note_data.get('name')
            confusable_set = note_data.get('fields', {}).get('ConfusableSet', '').strip()

            if confusable_set:
                notes.append({
                    'note_id': note_id,
                    'confusable_set': confusable_set,
                    'filepath': str(filepath)
                })

        except Exception as e:
            errors.append((filepath, str(e)))

    return notes, errors


def main():
    """Main execution."""
    lexeme_root = Path('./domains/ua/anki/notes/lexemes')

    if not lexeme_root.exists():
        print(f"ERROR: Lexeme root not found at {lexeme_root}")
        return 1

    print("Loading corpus...")
    notes_with_confusable, errors = load_corpus(lexeme_root)

    print(f"Found {len(notes_with_confusable)} notes with ConfusableSet populated")

    # Show sample from the 0099/0100/0101/0104 cluster
    target_ids = ['ua-lexeme-0099', 'ua-lexeme-0100', 'ua-lexeme-0101', 'ua-lexeme-0104']

    print("\n" + "=" * 80)
    print("SAMPLE: The 4-item cluster (добре́/непога́но/норма́льно/чудово́)")
    print("=" * 80)

    for note in notes_with_confusable:
        if note['note_id'] in target_ids:
            print(f"\n{note['note_id']}:")
            print(f"  File: {note['filepath']}")
            print(f"  ConfusableSet (raw):")
            print(f"    {repr(note['confusable_set'][:200])}")
            print(f"  ConfusableSet (displayed):")
            for line in note['confusable_set'].split('\n')[:3]:
                if line.strip():
                    print(f"    {line[:100]}")

    # Show another sample: check if note IDs are already there
    print("\n" + "=" * 80)
    print("SAMPLE: Notes that already contain note IDs")
    print("=" * 80)

    with_ids = [n for n in notes_with_confusable if 'ua-lexeme-' in n['confusable_set']]
    print(f"Found {len(with_ids)} notes with ua-lexeme-* references")

    if with_ids:
        for note in with_ids[:3]:
            print(f"\n{note['note_id']}:")
            print(f"  {repr(note['confusable_set'][:150])}")

    # Show samples without note IDs
    print("\n" + "=" * 80)
    print("SAMPLE: Notes with bare lemmas (no note IDs)")
    print("=" * 80)

    without_ids = [n for n in notes_with_confusable if 'ua-lexeme-' not in n['confusable_set']]
    print(f"Found {len(without_ids)} notes without ua-lexeme-* references")

    if without_ids:
        for note in without_ids[:3]:
            print(f"\n{note['note_id']}:")
            print(f"  {repr(note['confusable_set'][:150])}")

    # Analyze format patterns
    print("\n" + "=" * 80)
    print("FORMAT ANALYSIS")
    print("=" * 80)

    has_pipe = sum(1 for n in notes_with_confusable if '|' in n['confusable_set'])
    has_newline = sum(1 for n in notes_with_confusable if '\n' in n['confusable_set'])
    has_semicolon = sum(1 for n in notes_with_confusable if ';' in n['confusable_set'])

    print(f"Notes with pipes (|): {has_pipe}")
    print(f"Notes with newlines (\\n): {has_newline}")
    print(f"Notes with semicolons (;): {has_semicolon}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())