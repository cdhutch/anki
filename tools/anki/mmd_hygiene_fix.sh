#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-domains/b737/anki/notes/limits}"

if [[ ! -d "$ROOT" ]]; then
  echo "Not found: $ROOT" >&2
  exit 1
fi

echo "Fixing Markdown hygiene in: $ROOT"

find "$ROOT" -name "*.md" \
  -exec sed -i '' 's/^[[:space:]]*• /- /g' {} +

find "$ROOT" -name "*.md" \
  -exec sed -i '' \
  -e 's/“/"/g' \
  -e 's/”/"/g' \
  -e "s/‘/'/g" \
  -e "s/’/'/g" {} +

echo "Done. Review with: git diff"