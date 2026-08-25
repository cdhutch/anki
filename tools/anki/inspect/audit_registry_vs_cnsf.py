#!/usr/bin/env python3
"""
Audit confusable_clusters.yaml registry against CNSF notes.

Checks:
1. Registry members exist in CNSF
2. CNSF notes with Compare data are listed in registry
3. Identify missing CompareScenario
4. Identify incomplete Compare cards
5. Validate lemma consistency
"""

import yaml
from pathlib import Path
from typing import Dict, Set, Tuple

def load_registry(registry_path: str) -> Dict:
    """Load the confusable_clusters.yaml registry."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def scan_cnsf_notes(lexeme_root: str) -> Dict[str, Dict]:
    """Scan all ua-lexeme-*.md files and extract Compare-related data."""
    notes = {}

    for md_file in sorted(Path(lexeme_root).rglob("ua-lexeme-*.md")):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                continue

            parts = content.split('---', 2)
            if len(parts) < 3:
                continue

            yaml_content = parts[1].strip()
            data = yaml.safe_load(yaml_content)

            if not data:
                continue

            note_id = data.get('note_id', '')
            fields = data.get('fields', {})

            # Extract Compare-related fields
            compare_data = {
                'note_id': note_id,
                'lemma': fields.get('Lemma', ''),
                'confusable_set': fields.get('ConfusableSet', '')[:100] if fields.get('ConfusableSet') else '',
                'compare_scenario': fields.get('CompareScenario', ''),
                'compare_a': fields.get('CompareA', ''),
                'compare_b': fields.get('CompareB', ''),
                'compare_c': fields.get('CompareC', ''),
                'compare_d': fields.get('CompareD', ''),
                'homograph_sense_a': fields.get('Homograph_SenseA', ''),
                'homograph_sense_b': fields.get('Homograph_SenseB', ''),
                'is_homograph': 'homograph:true' in data.get('tags', ''),
            }

            # Only include if has Compare data
            if any([
                compare_data['compare_a'],
                compare_data['compare_b'],
                compare_data['compare_c'],
                compare_data['compare_d'],
                compare_data['homograph_sense_a'],
                compare_data['homograph_sense_b'],
                compare_data['confusable_set']
            ]):
                notes[note_id] = compare_data

        except Exception as e:
            print(f"Error parsing {md_file}: {e}", file=__import__('sys').stderr)
            continue

    return notes

def main():
    registry_path = 'domains/ua/anki/confusable_clusters.yaml'
    lexeme_root = 'domains/ua/anki/notes/lexemes'

    print("=" * 80)
    print("REGISTRY VS CNSF AUDIT")
    print("=" * 80)

    # Load data
    registry = load_registry(registry_path)
    cnsf_notes = scan_cnsf_notes(lexeme_root)

    # Extract all note IDs from registry
    registry_note_ids = set()
    registry_by_cluster = {}

    for cluster_name, cluster_data in registry.get('clusters', {}).items():
        registry_by_cluster[cluster_name] = {
            'canonical': cluster_data.get('canonical_note', ''),
            'members': []
        }
        for member in cluster_data.get('members', []):
            note_id = member.get('note_id', '')
            lemma = member.get('lemma', '')
            registry_note_ids.add(note_id)
            registry_by_cluster[cluster_name]['members'].append({
                'note_id': note_id,
                'registry_lemma': lemma
            })

    cnsf_note_ids = set(cnsf_notes.keys())

    print(f"\nRegistry note IDs: {len(registry_note_ids)}")
    print(f"CNSF notes with Compare data: {len(cnsf_note_ids)}")

    # Check 1: Registry members missing from CNSF
    print("\n" + "=" * 80)
    print("CHECK 1: Registry members not found in CNSF")
    print("=" * 80)

    missing_from_cnsf = registry_note_ids - cnsf_note_ids

    if missing_from_cnsf:
        print(f"\n✗ {len(missing_from_cnsf)} registry members not in CNSF:")
        for note_id in sorted(missing_from_cnsf):
            # Find which cluster it's in
            for cluster_name, cluster_info in registry_by_cluster.items():
                if any(m['note_id'] == note_id for m in cluster_info['members']):
                    print(f"  {note_id} (in cluster: {cluster_name})")
                    break
    else:
        print("\n✓ All registry members found in CNSF")

    # Check 2: CNSF notes not in any registry cluster
    print("\n" + "=" * 80)
    print("CHECK 2: CNSF Compare notes not listed in registry")
    print("=" * 80)

    missing_from_registry = cnsf_note_ids - registry_note_ids

    if missing_from_registry:
        print(f"\n✗ {len(missing_from_registry)} CNSF notes not in registry:")
        for note_id in sorted(missing_from_registry):
            lemma = cnsf_notes[note_id]['lemma']
            print(f"  {note_id}: {lemma}")
    else:
        print("\n✓ All CNSF Compare notes are in registry")

    # Check 3: Missing CompareScenario
    print("\n" + "=" * 80)
    print("CHECK 3: Notes missing CompareScenario")
    print("=" * 80)

    missing_scenario = [nid for nid, note in cnsf_notes.items() if not note['compare_scenario']]

    if missing_scenario:
        print(f"\n✗ {len(missing_scenario)} notes missing CompareScenario:")
        for note_id in sorted(missing_scenario):
            lemma = cnsf_notes[note_id]['lemma']
            is_homograph = cnsf_notes[note_id]['is_homograph']
            has_a = bool(cnsf_notes[note_id]['compare_a'])
            has_b = bool(cnsf_notes[note_id]['compare_b'])
            print(f"  {note_id}: {lemma} (homograph={is_homograph}, CompareA={has_a}, CompareB={has_b})")
    else:
        print("\n✓ All notes have CompareScenario")

    # Check 4: Incomplete Compare cards (missing CompareA or B)
    print("\n" + "=" * 80)
    print("CHECK 4: Incomplete Compare cards")
    print("=" * 80)

    incomplete = []
    for note_id, note in cnsf_notes.items():
        if not note['compare_a'] or not note['compare_b']:
            incomplete.append((note_id, note))

    if incomplete:
        print(f"\n✗ {len(incomplete)} notes have incomplete CompareA/B:")
        for note_id, note in sorted(incomplete):
            print(f"  {note_id}: {note['lemma']}")
            if not note['compare_a']:
                print(f"    - Missing CompareA")
            if not note['compare_b']:
                print(f"    - Missing CompareB")
    else:
        print("\n✓ All notes have both CompareA and CompareB")

    # Check 5: Lemma consistency (registry vs CNSF)
    print("\n" + "=" * 80)
    print("CHECK 5: Lemma consistency between registry and CNSF")
    print("=" * 80)

    lemma_mismatches = []
    for cluster_name, cluster_info in registry_by_cluster.items():
        for member in cluster_info['members']:
            note_id = member['note_id']
            registry_lemma = member['registry_lemma']
            if note_id in cnsf_notes:
                cnsf_lemma = cnsf_notes[note_id]['lemma']
                # Compare stress-stripped versions
                if registry_lemma.replace('́', '') != cnsf_lemma.replace('́', ''):
                    lemma_mismatches.append((note_id, registry_lemma, cnsf_lemma, cluster_name))

    if lemma_mismatches:
        print(f"\n✗ {len(lemma_mismatches)} lemma mismatches:")
        for note_id, reg_lemma, cnsf_lemma, cluster in sorted(lemma_mismatches):
            print(f"  {note_id} (cluster: {cluster})")
            print(f"    Registry: {reg_lemma}")
            print(f"    CNSF:     {cnsf_lemma}")
    else:
        print("\n✓ All lemmas match between registry and CNSF")

    # Check 6: Homograph vs non-homograph consistency
    print("\n" + "=" * 80)
    print("CHECK 6: Homograph notes should have Homograph_Sense fields")
    print("=" * 80)

    homograph_issues = []
    for note_id, note in cnsf_notes.items():
        if note['is_homograph']:
            if not note['homograph_sense_a'] or not note['homograph_sense_b']:
                homograph_issues.append((note_id, note))

    if homograph_issues:
        print(f"\n✗ {len(homograph_issues)} homograph notes missing Homograph_Sense fields:")
        for note_id, note in sorted(homograph_issues):
            print(f"  {note_id}: {note['lemma']}")
            if not note['homograph_sense_a']:
                print(f"    - Missing Homograph_SenseA")
            if not note['homograph_sense_b']:
                print(f"    - Missing Homograph_SenseB")
    else:
        print("\n✓ All homograph notes have Homograph_Sense fields")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    issues = [
        ('missing from CNSF', len(missing_from_cnsf)),
        ('missing from registry', len(missing_from_registry)),
        ('missing CompareScenario', len(missing_scenario)),
        ('incomplete Compare cards', len(incomplete)),
        ('lemma mismatches', len(lemma_mismatches)),
        ('homograph issues', len(homograph_issues)),
    ]

    total_issues = sum(count for _, count in issues)

    for issue_type, count in issues:
        status = "✓" if count == 0 else "✗"
        print(f"{status} {issue_type}: {count}")

    if total_issues == 0:
        print("\n✓✓✓ All checks passed! Registry and CNSF are consistent.")
    else:
        print(f"\n✗✗✗ Found {total_issues} issues requiring attention")

if __name__ == '__main__':
    main()
