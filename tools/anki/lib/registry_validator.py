#!/usr/bin/env python3
"""
Multi-layer validator for confusable_clusters.yaml registry.
Validates syntax, structure, fields, types, integrity, and coverage.
Can be run standalone for deployment verification.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple


class RegistryValidator:
    """Comprehensive validator for confusable_clusters.yaml"""
    
    def __init__(self, registry_path: Path, lexeme_root: Path):
        self.registry_path = registry_path
        self.lexeme_root = lexeme_root
        self.errors = []
        self.warnings = []
        self.stats = {
            'clusters': 0,
            'members': 0,
            'populated_scenarios': 0,
        }
    
    def validate_all(self) -> bool:
        """Run all validation layers. Returns True if all checks pass."""
        print("Validating confusable_clusters.yaml...")
        print()
        
        # Layer 1: Syntax
        print("Layer 1: YAML Syntax...")
        if not self._validate_syntax():
            return False
        
        # Layer 2: Structure
        print("Layer 2: Cluster Structure...")
        if not self._validate_structure():
            return False
        
        # Layer 3: Fields
        print("Layer 3: Field Definitions...")
        if not self._validate_fields():
            return False
        
        # Layer 4: Types
        print("Layer 4: Field Types...")
        if not self._validate_types():
            return False
        
        # Layer 5: Integrity
        print("Layer 5: Corpus Integrity...")
        if not self._validate_integrity():
            return False
        
        # Layer 6: Coverage
        print("Layer 6: Compare Field Coverage...")
        if not self._validate_coverage():
            return False
        
        # Report results
        self._report_results()
        return len(self.errors) == 0
    
    def _validate_syntax(self) -> bool:
        """Validate YAML syntax."""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = yaml.safe_load(f)
            print("  ✓ YAML syntax valid")
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML Syntax Error: {e}")
            print(f"  ✗ YAML syntax error: {e}")
            return False
    
    def _validate_structure(self) -> bool:
        """Validate cluster and member structure."""
        if not isinstance(self.registry, dict):
            self.errors.append("Registry root must be a dict")
            return False
        
        if 'clusters' not in self.registry:
            self.errors.append("Registry missing 'clusters' key")
            return False
        
        if not isinstance(self.registry['clusters'], dict):
            self.errors.append("'clusters' must be a dict")
            return False
        
        # Check cluster structure
        for cluster_name, cluster_data in self.registry['clusters'].items():
            required = {'description', 'canonical_note', 'members'}
            missing = required - set(cluster_data.keys())
            if missing:
                self.errors.append(f"Cluster '{cluster_name}' missing: {missing}")
            
            if not isinstance(cluster_data.get('members'), list):
                self.errors.append(f"Cluster '{cluster_name}' members must be a list")
            
            if not cluster_data.get('members'):
                self.errors.append(f"Cluster '{cluster_name}' has no members")
            
            self.stats['clusters'] += 1
        
        print(f"  ✓ Structure valid ({self.stats['clusters']} clusters)")
        return len(self.errors) == 0
    
    def _validate_fields(self) -> bool:
        """Validate that all required fields exist.

        compare_a/b/c/d and homograph_sense_a/b were removed from the schema
        2026-08-27 (dead data superseded by the CompareMembers JSON field,
        computed at import time from compare_scenario + lemma alone -- see
        get_cluster_compare_members_json() in ua_lexeme_import.py).
        """
        required_member_fields = {'note_id', 'lemma', 'status', 'chapter'}
        compare_fields = {'compare_scenario'}
        
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for i, member in enumerate(cluster_data['members']):
                self.stats['members'] += 1
                
                # Check required fields
                missing = required_member_fields - set(member.keys())
                if missing:
                    self.errors.append(f"Cluster '{cluster_name}' member {i} missing: {missing}")
                
                # Check Compare fields
                missing_compare = compare_fields - set(member.keys())
                if missing_compare:
                    self.errors.append(f"Cluster '{cluster_name}' member {i} missing Compare fields: {missing_compare}")
        
        print(f"  ✓ Fields valid ({self.stats['members']} members)")
        return len(self.errors) == 0
    
    def _validate_types(self) -> bool:
        """Validate field types."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for i, member in enumerate(cluster_data['members']):
                for field in ['compare_scenario']:
                    value = member.get(field)
                    if value is not None and not isinstance(value, str):
                        self.errors.append(
                            f"Cluster '{cluster_name}' member {i} field '{field}' "
                            f"must be string, got {type(value).__name__}"
                        )
        
        print("  ✓ Field types valid")
        return len(self.errors) == 0
    
    def _validate_integrity(self) -> bool:
        """Validate corpus integrity (note IDs exist, lemmas match)."""
        # Build corpus index
        corpus_notes = {}
        for md_file in self.lexeme_root.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                if not content.startswith('---'):
                    continue
                parts = content.split('---', 2)
                if len(parts) < 3:
                    continue
                data = yaml.safe_load(parts[1])
                if not data:
                    continue
                note_id = data.get('note_id')
                lemma = data.get('fields', {}).get('Lemma', '')
                if note_id:
                    corpus_notes[note_id] = lemma
            except Exception:
                pass
        
        # Check integrity
        for cluster_name, cluster_data in self.registry['clusters'].items():
            canonical_id = cluster_data.get('canonical_note')
            if canonical_id not in corpus_notes:
                self.errors.append(f"Cluster '{cluster_name}' canonical note '{canonical_id}' not found")
            
            for member in cluster_data['members']:
                note_id = member.get('note_id')
                if note_id not in corpus_notes:
                    self.errors.append(f"Member '{note_id}' not found in corpus")
        
        print(f"  ✓ Corpus integrity valid ({len(corpus_notes)} CNSF files)")
        return len(self.errors) == 0
    
    def _validate_coverage(self) -> bool:
        """Validate Compare field coverage and population."""
        for cluster_name, cluster_data in self.registry['clusters'].items():
            for member in cluster_data['members']:
                if member.get('compare_scenario', '').strip():
                    self.stats['populated_scenarios'] += 1
        
        # Check 100% scenario coverage
        if self.stats['populated_scenarios'] < self.stats['members']:
            unpopulated = self.stats['members'] - self.stats['populated_scenarios']
            self.errors.append(f"Missing {unpopulated} compare_scenario fields (100% coverage required)")
        
        print("  ✓ Coverage validation complete")
        return len(self.errors) == 0
    
    def _report_results(self):
        """Report validation results."""
        print()
        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        
        print("\nRegistry Statistics:")
        print(f"  Clusters: {self.stats['clusters']}")
        print(f"  Total members: {self.stats['members']}")
        print(f"  Compare scenarios: {self.stats['populated_scenarios']}/{self.stats['members']} ({int(self.stats['populated_scenarios']/self.stats['members']*100 if self.stats['members'] else 0)}%)")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        
        print()


def main():
    repo_root = Path(__file__).parent.parent.parent.parent
    registry_path = repo_root / 'domains/ua/anki/confusable_clusters.yaml'
    lexeme_root = repo_root / 'domains/ua/anki/notes/lexemes'
    
    if not registry_path.exists():
        print(f"Error: Registry not found: {registry_path}")
        return 1
    
    if not lexeme_root.exists():
        print(f"Error: Lexeme directory not found: {lexeme_root}")
        return 1
    
    validator = RegistryValidator(registry_path, lexeme_root)
    success = validator.validate_all()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
