#!/usr/bin/env python3
"""
Analyze confusable_clusters.yaml registry to see what Compare field data it holds.
Compare against what's currently in CNSF files to identify gaps.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

def load_registry(registry_path: str) -> Dict:
    """Load the confusable_clusters.yaml registry."""
    with open(registry_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def scan_compare_fields_in_cnsf(lexeme_root: str) -> Dict[str, Dict]:
    """Scan all ua-lexeme-*.md files for CompareA/B/C/D/Scenario content."""
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

def analyze_registry_structure(registry: Dict) -> Dict:
    """Analyze what Compare data the registry holds."""
    clusters = registry.get('clusters', {})

    analysis = {
        'total_clusters': len(clusters),
        'clusters_with_compare_fields': 0,
        'sample_cluster': None,
        'fields_present_in_clusters': set(),
    }

    for cluster_name, cluster_data in clusters.items():
        # Check what keys exist in cluster members
        for member in cluster_data.get('members', []):
            for key in member.keys():
                analysis['fields_present_in_clusters'].add(key)

        # Save a sample for inspection
        if not analysis['sample_cluster']:
            analysis['sample_cluster'] = {
                'name': cluster_name,
                'structure': {k: type(v).__name__ for k, v in cluster_data.items()}
            }

    analysis['fields_present_in_clusters'] = sorted(list(analysis['fields_present_in_clusters']))

    return analysis

def main():
    registry_path = 'domains/ua/anki/confusable_clusters.yaml'
    lexeme_root = 'domains/ua/anki/notes/lexemes'

    print("=" * 80)
    print("REGISTRY STRUCTURE ANALYSIS")
    print("=" * 80)

    # Load and analyze registry
    registry = load_registry(registry_path)
    registry_analysis = analyze_registry_structure(registry)

    print(f"\nRegistry Clusters: {registry_analysis['total_clusters']}")
    print(f"Fields present in cluster members: {registry_analysis['fields_present_in_clusters']}")
    print(f"\nSample cluster structure:")
    print(json.dumps(registry_analysis['sample_cluster'], indent=2))

    print("\n" + "=" * 80)
    print("CNSF COMPARE DATA SCAN")
    print("=" * 80)

    # Scan CNSF files
    cnsf_notes = scan_compare_fields_in_cnsf(lexeme_root)

    print(f"\nNotes with Compare/ConfusableSet data: {len(cnsf_notes)}")

    # Categorize by type
    homograph_notes = {k: v for k, v in cnsf_notes.items() if v['is_homograph']}
    confusable_notes = {k: v for k, v in cnsf_notes.items() if v['confusable_set'] and not v['is_homograph']}

    print(f"  - Homograph notes: {len(homograph_notes)}")
    print(f"  - Confusable notes: {len(confusable_notes)}")
    print(f"  - With CompareA/B content: {len({k:v for k,v in cnsf_notes.items() if v['compare_a'] or v['compare_b']})}")

    # Show breakdown of populated Compare fields
    print("\nCompare field population:")
    scenario_count = len([v for v in cnsf_notes.values() if v['compare_scenario']])
    a_count = len([v for v in cnsf_notes.values() if v['compare_a']])
    b_count = len([v for v in cnsf_notes.values() if v['compare_b']])
    c_count = len([v for v in cnsf_notes.values() if v['compare_c']])
    d_count = len([v for v in cnsf_notes.values() if v['compare_d']])

    print(f"  CompareScenario: {scenario_count} notes")
    print(f"  CompareA: {a_count} notes")
    print(f"  CompareB: {b_count} notes")
    print(f"  CompareC: {c_count} notes")
    print(f"  CompareD: {d_count} notes")

    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)

    # Check if registry contains Compare field keys
    registry_has_compare_keys = any('compare' in field.lower() for field in registry_analysis['fields_present_in_clusters'])

    print(f"\nRegistry contains CompareA/B/C/D fields: {registry_has_compare_keys}")
    print(f"Registry field names: {registry_analysis['fields_present_in_clusters']}")

    if registry_has_compare_keys:
        print("\n✓ Registry appears ready for Compare field consolidation")
    else:
        print("\n✗ Registry does NOT contain Compare field data")
        print("  Action needed: Either populate registry with Compare content, or keep fields in CNSF")

    # Show sample notes
    print("\n" + "=" * 80)
    print("SAMPLE NOTES (first 3)")
    print("=" * 80)

    for i, (note_id, note_data) in enumerate(list(cnsf_notes.items())[:3]):
        print(f"\n{i+1}. {note_id}: {note_data['lemma']}")
        if note_data['compare_a']:
            print(f"   CompareA: {note_data['compare_a'][:60]}")
        if note_data['compare_b']:
            print(f"   CompareB: {note_data['compare_b'][:60]}")
        if note_data['homograph_sense_a']:
            print(f"   Homograph_SenseA: {note_data['homograph_sense_a'][:60]}")
        if note_data['homograph_sense_b']:
            print(f"   Homograph_SenseB: {note_data['homograph_sense_b'][:60]}")

if __name__ == '__main__':
    main()