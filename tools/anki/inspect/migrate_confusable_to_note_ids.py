#!/usr/bin/env python3
"""
Migrate ConfusableSet fields from bare lemmas to standardized note ID format.

Before: "непога́но, норма́льно, чудово́" (bare lemmas with stress marks)
After:  "ua-lexeme-0100, ua-lexeme-0101, ua-lexeme-0102" (note IDs only)

Also adds pending-confusable:<lemma> tags for any lemmas that don't resolve.

CRITICAL: Uses yaml.dump(allow_unicode=True) to preserve Cyrillic text.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict


def strip_stress(text):
    """Remove combining stress mark (U+0301) from text."""
    return text.replace('́', '')


def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter and body from markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None, None, None
    yaml_content = match.group(1)
    body = match.group(2)
    return yaml_content, body, content


def load_corpus(lexeme_root):
    """Load all lexeme notes, return {note_id: note_data, lemma_index: {lemma_stripped: note_id}}."""
    notes_by_id = {}
    lemma_index = {}
    parse_errors = []

    md_files = list(lexeme_root.glob('**/*.md'))

    for filepath in sorted(md_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_content, body, _ = parse_yaml_frontmatter(content)
            if yaml_content is None:
                parse_errors.append((filepath, "Could not parse frontmatter"))
                continue

            note_data = yaml.safe_load(yaml_content)
            if note_data is None:
                parse_errors.append((filepath, "Could not load YAML"))
                continue

            # Extract note_id
            note_id = note_data.get('note_id') or note_data.get('name')
            if not note_id:
                filename = Path(filepath).stem
                note_id = filename if filename else 'unknown'

            notes_by_id[note_id] = {
                'data': note_data,
                'filepath': filepath,
                'yaml_content': yaml_content,
                'body': body,
                'full_content': content
            }

            # Add to lemma index (stress-stripped)
            lemma = note_data.get('fields', {}).get('Lemma', '').strip()
            if lemma:
                lemma_stripped = strip_stress(lemma)
                lemma_index[lemma_stripped] = note_id

        except Exception as e:
            parse_errors.append((filepath, str(e)))

    return notes_by_id, lemma_index, parse_errors


def extract_confusable_lemmas(confusable_set_text):
    """
    Extract bare lemmas and note IDs from ConfusableSet text.

    ConfusableSet can contain mixed format:
    - Bare lemmas: непога́но, норма́льно
    - Note IDs: ua-lexeme-0100, ua-lexeme-0101
    - Mix of both, with prose discriminator text

    Returns (note_ids_found, bare_lemmas_found, raw_text)
    """
    if not confusable_set_text or not confusable_set_text.strip():
        return [], [], confusable_set_text

    # Extract all note IDs (already in target format)
    note_id_pattern = r'ua-lexeme-\d+'
    note_ids = re.findall(note_id_pattern, confusable_set_text)

    # Extract bare lemmas (not note IDs, word-like)
    # Simple heuristic: Cyrillic words that aren't note IDs
    # This is approximate — we rely on manual structure mostly
    bare_lemmas = []
    words = re.findall(r'[а-яА-ЯїЇєЄґҐʼ\']+', confusable_set_text)
    for word in words:
        word_stripped = strip_stress(word)
        # Skip if it looks like part of a note ID or is too short
        if not word_stripped.startswith('ua-lexeme') and len(word_stripped) > 2:
            bare_lemmas.append(word_stripped)

    return note_ids, bare_lemmas, confusable_set_text


def migrate_note(note_id, note_info, lemma_index):
    """
    Migrate one note's ConfusableSet field from bare lemmas to note IDs.

    Returns (modified, changes_summary, new_pending_confusable_tags)
    """
    note_data = note_info['data']
    fields = note_data.get('fields', {})
    confusable_set = fields.get('ConfusableSet', '').strip()

    if not confusable_set:
        return False, None, []

    # Extract components
    note_ids_found, bare_lemmas, raw_text = extract_confusable_lemmas(confusable_set)

    # Resolve bare lemmas to note IDs
    resolved_ids = list(note_ids_found)  # Start with already-present note IDs
    unresolved_lemmas = []
    new_pending_tags = []

    for lemma in set(bare_lemmas):  # Deduplicate
        if lemma in lemma_index:
            resolved_ids.append(lemma_index[lemma])
        else:
            unresolved_lemmas.append(lemma)
            # Mark for pending-confusable tag
            new_pending_tags.append(f'pending-confusable:{lemma}')

    if not resolved_ids and not unresolved_lemmas:
        # No changes needed
        return False, None, []

    # Deduplicate and sort resolved IDs for stable output
    resolved_ids = sorted(set(resolved_ids), key=lambda x: int(x.split('-')[-1]))

    # Build new ConfusableSet with note IDs only, preserve prose if present
    # Simple strategy: replace the line with just the note IDs
    new_confusable_set = ', '.join(resolved_ids)

    # If there was prose discriminator text (beyond just lemmas), try to preserve it
    # This is best-effort; actual discrimination prose should be in Mnemonic_EN
    if raw_text and not all(c in 'абвгґджезийіїклмнопрстуфхцчшщъьюяʼ,. \n\t' for c in raw_text):
        # There's likely prose in there; keep it as comment
        new_confusable_set = raw_text.split('\n')[0] + '\n' + new_confusable_set

    # Update the note
    fields['ConfusableSet'] = new_confusable_set
    note_data['fields'] = fields

    # Add pending-confusable tags to the note
    tags = note_data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    else:
        tags = [t.strip() for t in tags if t.strip()]

    tags.extend(new_pending_tags)
    note_data['tags'] = tags

    return True, {
        'note_id': note_id,
        'resolved_ids': resolved_ids,
        'unresolved_lemmas': unresolved_lemmas,
        'pending_tags_added': new_pending_tags
    }, new_pending_tags


def main():
    """Main execution."""
    lexeme_root = Path('./domains/ua/anki/notes/lexemes')

    if not lexeme_root.exists():
        print(f"ERROR: Lexeme root not found at {lexeme_root}")
        print(f"Current directory: {Path.cwd()}")
        return

    # Load corpus
    print("Loading corpus...")
    notes_by_id, lemma_index, parse_errors = load_corpus(lexeme_root)
    print(f"Loaded {len(notes_by_id)} notes")
    print(f"Built lemma index with {len(lemma_index)} stress-stripped lemmas")

    if parse_errors:
        print(f"\nParse errors ({len(parse_errors)}):")
        for filepath, error in parse_errors[:5]:  # Show first 5
            print(f"  {filepath}: {error}")
        if len(parse_errors) > 5:
            print(f"  ... and {len(parse_errors) - 5} more")

    # Migrate notes
    print("\nMigrating ConfusableSet fields...")
    migrated = []
    unresolved_summary = defaultdict(list)

    for note_id in sorted(notes_by_id.keys(), key=lambda x: int(x.split('-')[-1]) if 'ua-lexeme-' in x else 0):
        note_info = notes_by_id[note_id]
        modified, changes, pending_tags = migrate_note(note_id, note_info, lemma_index)

        if modified:
            migrated.append((note_id, changes))
            if changes and changes['unresolved_lemmas']:
                for lemma in changes['unresolved_lemmas']:
                    unresolved_summary[lemma].append(note_id)

    print(f"Modified {len(migrated)} notes with ConfusableSet fields")

    # Write migrated notes back
    print("\nWriting migrated files...")
    for note_id, changes in migrated:
        note_info = notes_by_id[note_id]
        note_data = note_info['data']
        filepath = note_info['filepath']

        # Serialize back to YAML with unicode preservation (CRITICAL)
        new_yaml = yaml.dump(note_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_yaml}---\n{note_info['body']}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # Report
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total notes migrated: {len(migrated)}")

    if unresolved_summary:
        print(f"\nUnresolved lemmas ({len(unresolved_summary)}):")
        for lemma, note_ids in sorted(unresolved_summary.items()):
            print(f"  {lemma}: referenced by {', '.join(note_ids)}")
            print(f"    → pending-confusable:{lemma} tags added")

    print("\nNext steps:")
    print("1. Run audit: python tools/anki/inspect/audit_compare_clusters.py")
    print("2. Review output for any remaining issues")
    print("3. Commit: 'Standardize ConfusableSet format: bare lemmas → note IDs (585 notes)'")


if __name__ == '__main__':
    main()