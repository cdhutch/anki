#!/usr/bin/env python3
"""
Repair UA_Lexeme note structure on branch feature/ua-lexeme-field-and-tag-audit:
1. Remove all stress:* tags
2. Preserve status:* tags (do not modify them)
3. Ensure all 13 always-present fields exist
4. Identify empty fields that should have content
5. Preserve Cyrillic text using allow_unicode=True in YAML serialization
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict

ALWAYS_PRESENT_FIELDS = [
    'Lemma_Euphony',
    'Perfective_Euphony',
    'ImperfectiveUnidirectional_Euphony',
    'CompareA',
    'CompareB',
    'CompareC',
    'CompareD',
    'CompareScenario',
    'Homograph_SenseA',
    'Homograph_SenseB',
    'AspectCue',
    'Mnemonic_EN',
    'Verification Notes'
]

def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter and body from markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None, None
    yaml_content = match.group(1)
    body = match.group(2)
    return yaml_content, body

def should_have_euphony(note_data, field_name):
    """Check if note should have euphony content."""
    fields = note_data.get('fields', {})
    verification_notes = fields.get('Verification Notes', '').lower()
    confusable_set = fields.get('ConfusableSet', '').lower()

    if 'в-/у-' in verification_notes or 'в- / у-' in verification_notes or 'euphony' in verification_notes:
        return True
    if 'в-/у-' in confusable_set or 'в- / у-' in confusable_set:
        return True

    return False

def check_field_needs_content(note_id, note_data, field_name, field_value):
    """Determine if an empty field should have content."""
    if field_value and field_value.strip():
        return False, None, None

    fields = note_data.get('fields', {})
    confusable_set = fields.get('ConfusableSet', '').strip()
    tags_str = ','.join(note_data.get('tags', []))

    if field_name in ['CompareA', 'CompareB', 'CompareC', 'CompareD', 'CompareScenario']:
        if confusable_set:
            return True, f"Note has ConfusableSet: {confusable_set[:50]}...", "[Content needed - manual review]"

    if field_name in ['Homograph_SenseA', 'Homograph_SenseB']:
        if 'homograph:true' in tags_str:
            return True, "Note tagged homograph:true", "[Content needed - manual review]"

    if field_name in ['Lemma_Euphony', 'Perfective_Euphony', 'ImperfectiveUnidirectional_Euphony']:
        if should_have_euphony(note_data, field_name):
            return True, "Euphony evidence found in note", "[Content needed - manual review]"

    return False, None, None

def process_file(filepath):
    """Process a single lexeme file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    yaml_content, body = parse_yaml_frontmatter(content)
    if yaml_content is None:
        return {'error': f'Could not parse frontmatter in {filepath}'}

    note_data = yaml.safe_load(yaml_content)
    if note_data is None:
        return {'error': f'Could not load YAML in {filepath}'}

    # Extract note_id from YAML (try 'note_id' first, then 'name' for compatibility)
    note_id = note_data.get('note_id') or note_data.get('name')

    if not note_id:
        # Extract from filename: ua-lexeme-0001.md -> ua-lexeme-0001
        filename = Path(filepath).stem
        note_id = filename if filename else 'unknown'

    # Remove stress:* tags only (preserve status:* tags)
    tags = note_data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    else:
        tags = [t.strip() for t in tags if t.strip()]

    original_tag_count = len(tags)
    tags = [t for t in tags if not t.startswith('stress:')]
    removed_stress_tags = original_tag_count - len(tags)

    note_data['tags'] = tags

    # Ensure all 13 always-present fields exist
    fields = note_data.get('fields', {})
    missing_fields = []
    for field_name in ALWAYS_PRESENT_FIELDS:
        if field_name not in fields:
            fields[field_name] = ''
            missing_fields.append(field_name)

    note_data['fields'] = fields

    # Check for fields that should have content
    fields_needing_content = []
    for field_name in ALWAYS_PRESENT_FIELDS:
        field_value = fields.get(field_name, '')
        should_populate, reason, proposed = check_field_needs_content(note_id, note_data, field_name, field_value)
        if should_populate:
            fields_needing_content.append({
                'field': field_name,
                'reason': reason,
                'proposed': proposed
            })

    # Serialize back to YAML with unicode preservation (CRITICAL: allow_unicode=True)
    new_yaml = yaml.dump(note_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_yaml}---\n{body}"

    # Write file back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return {
        'note_id': note_id,
        'filepath': filepath,
        'removed_stress_tags': removed_stress_tags,
        'added_missing_fields': missing_fields,
        'fields_needing_content': fields_needing_content
    }

def main():
    """Main execution."""
    lexeme_root = Path('./domains/ua/anki/notes/lexemes')

    if not lexeme_root.exists():
        print(f"ERROR: Lexeme root not found at {lexeme_root}")
        print(f"Current directory: {Path.cwd()}")
        return

    # Collect all .md files
    md_files = list(lexeme_root.glob('**/*.md'))
    print(f"Found {len(md_files)} lexeme files")

    results = []
    fields_needing_content_summary = defaultdict(list)

    for i, filepath in enumerate(sorted(md_files), 1):
        try:
            result = process_file(filepath)
            results.append(result)

            if 'fields_needing_content' in result and result['fields_needing_content']:
                for item in result['fields_needing_content']:
                    fields_needing_content_summary[item['field']].append({
                        'note_id': result['note_id'],
                        'reason': item['reason'],
                        'proposed': item['proposed']
                    })

            if i % 100 == 0:
                print(f"  Processed {i}/{len(md_files)} files...")
        except Exception as e:
            results.append({'note_id': 'unknown', 'error': str(e), 'filepath': str(filepath)})

    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("UA_LEXEME STRUCTURE REPAIR REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary
    total_files = len(md_files)
    successful = sum(1 for r in results if 'error' not in r)
    errors = sum(1 for r in results if 'error' in r)

    report_lines.append(f"Total files processed: {total_files}")
    report_lines.append(f"Successful: {successful}")
    report_lines.append(f"Errors: {errors}")
    report_lines.append("")

    total_stress_tags_removed = sum(r.get('removed_stress_tags', 0) for r in results if 'error' not in r)
    report_lines.append(f"Total stress:* tags removed: {total_stress_tags_removed}")

    total_fields_added = sum(len(r.get('added_missing_fields', [])) for r in results if 'error' not in r)
    report_lines.append(f"Total missing fields added: {total_fields_added}")
    report_lines.append("")

    # Fields needing content
    if fields_needing_content_summary:
        report_lines.append("=" * 80)
        report_lines.append("FIELDS NEEDING CONTENT")
        report_lines.append("=" * 80)
        report_lines.append("")

        for field_name in sorted(fields_needing_content_summary.keys()):
            items = fields_needing_content_summary[field_name]
            report_lines.append(f"\n{field_name} ({len(items)} notes):")
            report_lines.append("-" * 40)
            for item in sorted(items, key=lambda x: x['note_id']):
                report_lines.append(f"  {item['note_id']}: {item['reason']}")

    # Errors
    if errors > 0:
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("ERRORS")
        report_lines.append("=" * 80)
        report_lines.append("")
        for result in results:
            if 'error' in result:
                report_lines.append(f"{result.get('note_id', 'unknown')}: {result['error']}")

    # Print to console and file
    report_text = "\n".join(report_lines)
    print(report_text)

    with open('./lexeme_repair_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print("")
    print("Report saved to ./lexeme_repair_report.txt")

if __name__ == '__main__':
    main()
