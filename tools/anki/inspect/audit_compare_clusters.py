#!/usr/bin/env python3
"""
Audit Compare field clusters in UA_Lexeme notes after standardization.

Validates:
1. Cluster size matches required Compare field count (CompareA for 2+, B for 2+, C for 3+, D for 4+)
2. CompareA-D values exist as Lemma fields in referenced notes
3. Pending-confusable tagged notes excluded from cluster size (forward references)

Fixes false positives from prior bare-lemma parsing by using note ID resolution.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict, deque


def strip_stress(text):
    """Remove combining stress mark (U+0301) from text."""
    return text.replace('́', '')


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
    notes_by_id = {}
    parse_errors = []

    md_files = list(lexeme_root.glob('**/*.md'))

    for filepath in sorted(md_files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            yaml_content, body = parse_yaml_frontmatter(content)
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
            }

        except Exception as e:
            parse_errors.append((filepath, str(e)))

    return notes_by_id, parse_errors


def extract_note_ids_from_confusable(confusable_set_text):
    """Extract all note IDs from ConfusableSet text."""
    if not confusable_set_text:
        return []
    note_id_pattern = r'ua-lexeme-\d+'
    return re.findall(note_id_pattern, confusable_set_text)


def bfs_cluster(start_note_id, notes_by_id, exclude_pending=True):
    """
    Find all notes in a cluster via BFS through ConfusableSet references.

    Optionally exclude pending-confusable tagged notes from cluster size.
    """
    visited = set()
    queue = deque([start_note_id])
    cluster = set()

    while queue:
        note_id = queue.popleft()

        if note_id in visited or note_id not in notes_by_id:
            continue

        visited.add(note_id)
        note_data = notes_by_id[note_id]['data']

        # Check if note is pending-confusable tagged (skip if exclude_pending=True)
        tags = note_data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        is_pending = any(t.startswith('pending-confusable:') for t in tags)
        if exclude_pending and is_pending:
            continue

        cluster.add(note_id)

        # Extract referenced notes from ConfusableSet
        confusable_set = note_data.get('fields', {}).get('ConfusableSet', '').strip()
        referenced_ids = extract_note_ids_from_confusable(confusable_set)

        for ref_id in referenced_ids:
            if ref_id not in visited:
                queue.append(ref_id)

    return cluster


def get_required_compare_fields(cluster_size):
    """Determine which Compare fields are required based on cluster size."""
    required = []
    if cluster_size >= 2:
        required.extend(['CompareA', 'CompareB'])
    if cluster_size >= 3:
        required.append('CompareC')
    if cluster_size >= 4:
        required.append('CompareD')
    return required


def get_referenced_lemmas(note_ids, notes_by_id):
    """Get all Lemma values from referenced notes."""
    lemmas = set()
    for note_id in note_ids:
        if note_id in notes_by_id:
            lemma = notes_by_id[note_id]['data'].get('fields', {}).get('Lemma', '').strip()
            if lemma:
                lemmas.add(lemma)
    return lemmas


def audit_note(note_id, note_info, notes_by_id, audited_notes):
    """
    Audit one note's Compare fields.

    Returns (has_confusable, cluster_size, issues)
    """
    if note_id in audited_notes:
        return None  # Already audited as part of another note's cluster

    note_data = note_info['data']
    confusable_set = note_data.get('fields', {}).get('ConfusableSet', '').strip()

    if not confusable_set:
        return None  # No ConfusableSet, no cluster

    # Find full cluster via BFS
    cluster = bfs_cluster(note_id, notes_by_id, exclude_pending=True)
    if not cluster:
        return None

    cluster_size = len(cluster)
    required_fields = get_required_compare_fields(cluster_size)
    referenced_ids = extract_note_ids_from_confusable(confusable_set)
    referenced_lemmas = get_referenced_lemmas(referenced_ids, notes_by_id)

    issues = []

    # Check each required field
    for field_name in required_fields:
        field_value = note_data.get('fields', {}).get(field_name, '').strip()
        if not field_value:
            issues.append({
                'type': 'missing_field',
                'field': field_name,
                'cluster_size': cluster_size,
                'message': f"Required for {cluster_size}-item cluster, missing"
            })
        elif field_value not in referenced_lemmas:
            issues.append({
                'type': 'invalid_value',
                'field': field_name,
                'value': field_value,
                'expected': ', '.join(sorted(referenced_lemmas)),
                'message': f"Value '{field_value}' not in referenced lemmas: {', '.join(sorted(referenced_lemmas))}"
            })

    # Mark all cluster members as audited
    for cid in cluster:
        audited_notes.add(cid)

    return cluster_size, len(issues), issues, cluster


def main():
    """Main execution."""
    lexeme_root = Path('./domains/ua/anki/notes/lexemes')

    if not lexeme_root.exists():
        print(f"ERROR: Lexeme root not found at {lexeme_root}")
        print(f"Current directory: {Path.cwd()}")
        return

    # Load corpus
    print("Loading corpus...")
    notes_by_id, parse_errors = load_corpus(lexeme_root)
    print(f"Loaded {len(notes_by_id)} notes")

    if parse_errors:
        print(f"Parse errors ({len(parse_errors)}):")
        for filepath, error in parse_errors[:5]:
            print(f"  {filepath}: {error}")

    # Audit clusters
    print("\nAuditing Compare field clusters...")
    audited_notes = set()
    cluster_results = []
    total_issues = 0

    for note_id in sorted(notes_by_id.keys(), key=lambda x: int(x.split('-')[-1]) if 'ua-lexeme-' in x else 0):
        if note_id in audited_notes:
            continue

        note_info = notes_by_id[note_id]
        result = audit_note(note_id, note_info, notes_by_id, audited_notes)

        if result:
            cluster_size, issue_count, issues, cluster = result
            if issue_count > 0:
                cluster_results.append({
                    'start_note': note_id,
                    'cluster_size': cluster_size,
                    'cluster': sorted(cluster),
                    'issue_count': issue_count,
                    'issues': issues
                })
                total_issues += issue_count

    # Report
    print("\n" + "=" * 80)
    print("COMPARE FIELD AUDIT RESULTS")
    print("=" * 80)
    print(f"Total clusters audited: {len(set(c['cluster'] for r in cluster_results for c in [r]))}")
    print(f"Clusters with issues: {len(cluster_results)}")
    print(f"Total issues: {total_issues}")

    if cluster_results:
        print("\n" + "=" * 80)
        print("ISSUES FOUND")
        print("=" * 80)

        for result in cluster_results:
            print(f"\nCluster starting at {result['start_note']} (size: {result['cluster_size']}):")
            print(f"  Members: {', '.join(result['cluster'])}")
            print(f"  Issues: {result['issue_count']}")

            for issue in result['issues']:
                if issue['type'] == 'missing_field':
                    print(f"    - {issue['field']}: {issue['message']}")
                elif issue['type'] == 'invalid_value':
                    print(f"    - {issue['field']}: {issue['message']}")
    else:
        print("\n✓ No Compare field issues found!")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"Ready to sync: {len(notes_by_id)} notes")


if __name__ == '__main__':
    main()