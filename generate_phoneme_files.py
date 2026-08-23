#!/usr/bin/env python3
"""
Generate individual phoneme YAML files from the comprehensive superset.

Usage:
    python generate_phoneme_files.py <path_to_superset.yaml> <output_directory>

Example:
    python generate_phoneme_files.py complete_phoneme_superset.yaml domains/ipa/anki/notes/phonemes/
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Any, Dict

import yaml


def sanitize_filename(text: str) -> str:
    """Convert text to valid filename."""
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text.lower()


def load_superset(filepath: str) -> Dict[str, Any]:
    """Load the superset YAML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_phoneme_yaml(phoneme: Dict[str, Any]) -> str:
    """Convert a phoneme dict to YAML string."""
    output = {
        'phoneme_id': phoneme.get('phoneme_id'),
        'ipa': phoneme.get('ipa'),
        'xsampa': phoneme.get('xsampa'),
        'articulation': phoneme.get('articulation'),
        'description': phoneme.get('description'),
    }

    if 'examples' in phoneme:
        examples = {}
        for lang in ['fr', 'de', 'ua', 'ru', 'cs', 'sk']:
            if lang in phoneme['examples']:
                examples[lang] = phoneme['examples'][lang]
        if examples:
            output['representative_words'] = examples

    return yaml.dump(output, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_files(superset_path: str, output_dir: str) -> None:
    """Generate individual phoneme files."""
    superset = load_superset(superset_path)
    phonemes = superset.get('phonemes', [])

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(phonemes)} phoneme files...")

    for i, phoneme in enumerate(phonemes, 1):
        phoneme_id = phoneme.get('phoneme_id', f'phoneme_{i}')
        description = phoneme.get('description', '').lower()

        filename_base = sanitize_filename(description) or phoneme_id
        filename = f"{filename_base}.yaml"
        filepath = output_path / filename

        yaml_content = create_phoneme_yaml(phoneme)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        print(f"  [{i}/{len(phonemes)}] {filename}")

    print(f"\n✓ Generated {len(phonemes)} phoneme files in {output_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('superset', help='Path to complete_phoneme_superset.yaml')
    parser.add_argument('output', help='Output directory (e.g., domains/ipa/anki/notes/phonemes/)')

    args = parser.parse_args()

    if not Path(args.superset).exists():
        print(f"Error: Superset file not found: {args.superset}", file=sys.stderr)
        sys.exit(1)

    generate_files(args.superset, args.output)


if __name__ == '__main__':
    main()
