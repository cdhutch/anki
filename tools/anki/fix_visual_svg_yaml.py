#!/usr/bin/env python3
"""
Fix YAML escaping in UA_Visual note SVG fields.

The Diagram_SVG field contains SVG strings with Unicode characters (→, ←, ↔)
that can break YAML parsing during canonicalization. This script wraps all
SVG strings in single quotes to protect them from YAML interpretation.

Usage:
    python tools/anki/fix_visual_svg_yaml.py VISUAL_DIR/
    python tools/anki/fix_visual_svg_yaml.py domains/ua/anki/notes/visual/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def fix_svg_yaml(filepath: Path) -> bool:
    """Wrap SVG strings in single quotes to protect from YAML parsing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    pattern = r'(  Diagram_SVG: )(<svg[\s\S]*?</svg>)'

    def wrap_svg(match):
        svg = match.group(2)
        if not svg.startswith("'") and not svg.startswith('"'):
            return f'{match.group(1)}\'{svg}\''
        return match.group(0)

    modified = re.sub(pattern, wrap_svg, original, flags=re.DOTALL)

    if modified != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Fix YAML escaping in UA_Visual SVG fields'
    )
    parser.add_argument(
        'visual_dir',
        type=Path,
        help='Path to visual notes directory'
    )

    args = parser.parse_args()

    if not args.visual_dir.is_dir():
        print(f"Error: {args.visual_dir} is not a directory", file=sys.stderr)
        return 1

    count = 0
    for filepath in sorted(args.visual_dir.glob('ua-visual-*.md')):
        try:
            if fix_svg_yaml(filepath):
                print(f"✓ {filepath.name}")
                count += 1
        except Exception as e:
            print(f"✗ {filepath.name}: {e}", file=sys.stderr)
            return 1

    if count > 0:
        print(f"\n✓ Fixed {count} visual cards")
    else:
        print("No changes needed")

    return 0


if __name__ == '__main__':
    sys.exit(main())
