#!/usr/bin/env python3
"""
Backfill Compare card fields in confusable_clusters.yaml from CNSF markdown files.
Maps CompareScenario -> compare_scenario, CompareA -> compare_a, etc.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import yaml

def extract_yaml_frontmatter(markdown_content: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n', markdown_content, re.DOTALL)
    if not match:
        return {}
    
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}

def load_cnsf_files(lexeme_root: Path) -> Dict[str, Dict[str, str]]:
    """Load all CNSF markdown files and extract Compare fields."""
    cnsf_data = {}
    
    for md_file in lexeme_root.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            yaml_data = extract_yaml_frontmatter(content)
            
            note_id = yaml_data.get('note_id')
            fields = yaml_data.get('fields', {})
            
            if note_id and isinstance(fields, dict):
                compare_fields = {
                    'compare_scenario': fields.get('CompareScenario', ''),
                    'compare_a': fields.get('CompareA', ''),
                    'compare_b': fields.get('CompareB', ''),
                    'compare_c': fields.get('CompareC', ''),
                    'compare_d': fields.get('CompareD', ''),
                    'homograph_sense_a': fields.get('Homograph_SenseA', ''),
                    'homograph_sense_b': fields.get('Homograph_SenseB', ''),
                }
                cnsf_data[note_id] = compare_fields
        except Exception as e:
            print(f"Warning: Error reading {md_file}: {e}", file=sys.stderr)
    
    return cnsf_data

def backfill_registry(registry_path: Path, lexeme_root: Path) -> Tuple[Dict, int, int, int]:
    """
    Backfill confusable_clusters.yaml with Compare fields from CNSF files.
    Returns: (modified_registry, clusters_processed, members_updated, cnsf_files_found)
    """
    # Load CNSF data
    cnsf_data = load_cnsf_files(lexeme_root)
    found = len(cnsf_data)
    
    # Load registry
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f) or {}
    
    clusters = registry.get('clusters', {})
    updates = 0
    
    # Backfill each member
    for cluster_name, cluster in clusters.items():
        members = cluster.get('members', [])
        for member in members:
            note_id = member.get('note_id')
            if note_id in cnsf_data:
                for field, value in cnsf_data[note_id].items():
                    # Only update if field is empty or missing
                    if not member.get(field):
                        member[field] = value
                        updates += 1
    
    return registry, len(clusters), updates, found

def apply_backfill(registry_path: Path, lexeme_root: Path, dry_run: bool = False) -> None:
    """Apply backfill and save to YAML file."""
    registry, clusters, updates, found = backfill_registry(registry_path, lexeme_root)
    
    print(f"Backfill complete:")
    print(f"  Clusters processed: {clusters}")
    print(f"  Fields updated: {updates}")
    print(f"  CNSF files found: {found}")
    
    # Count populated scenarios
    total_members = sum(len(c.get('members', [])) for c in registry.get('clusters', {}).values())
    populated = sum(
        1 for c in registry.get('clusters', {}).values()
        for m in c.get('members', [])
        if m.get('compare_scenario')
    )
    print(f"  Populated scenarios: {populated}/{total_members}")
    
    if dry_run:
        print("\n[DRY RUN MODE] — No changes written to file")
        return
    
    # Write back to file
    with open(registry_path, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print("\nRegistry saved to disk")

if __name__ == '__main__':
    repo_root = Path(__file__).parent
    registry_path = repo_root / 'domains/ua/anki/confusable_clusters.yaml'
    lexeme_root = repo_root / 'domains/ua/anki/notes/lexemes'
    
    dry_run = '--dry-run' in sys.argv
    
    if not registry_path.exists():
        print(f"Error: Registry file not found: {registry_path}", file=sys.stderr)
        sys.exit(1)
    
    if not lexeme_root.exists():
        print(f"Error: Lexeme directory not found: {lexeme_root}", file=sys.stderr)
        sys.exit(1)
    
    apply_backfill(registry_path, lexeme_root, dry_run=dry_run)
