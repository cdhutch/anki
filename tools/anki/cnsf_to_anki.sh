#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# Required argument: directory containing CNSF notes
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <cnsf-note-directory> [output-tsv]" >&2
  echo "" >&2
  echo "Example:" >&2
  echo "  $0 domains/b737/anki/notes/limits" >&2
  echo "" >&2
  exit 1
fi

INPUT_DIR="$1"
OUT_TSV="${2:-/tmp/cnsf_to_anki_import.tsv}"
ANKI_URL="${ANKI_URL:-http://127.0.0.1:8765}"
MAP_IN="${MAP_IN:-}"
MAP_OUT="${MAP_OUT:-}"

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Input dir not found: $INPUT_DIR" >&2
  exit 1
fi

echo "==> Repo root: $ROOT_DIR"
echo "==> Input dir : $INPUT_DIR"
echo "==> Output TSV: $OUT_TSV"

NOTE_FILES=()
while IFS= read -r f; do
  NOTE_FILES+=("$f")
done < <(find "$INPUT_DIR" -type f -name "*.md" | sort)

if [[ ${#NOTE_FILES[@]} -eq 0 ]]; then
  echo "No CNSF note files found under: $INPUT_DIR" >&2
  exit 1
fi

echo "==> Canonical check"
python3 tools/anki/cnsf_canonicalize.py --check "${NOTE_FILES[@]}"

echo "==> Export CNSF -> TSV"
EXPORT_CMD=(
  python3 -m tools.anki.export.cnsf_to_import_tsv
  --in "$INPUT_DIR"
  --out "$OUT_TSV"
  --overwrite
)

if [[ -n "$MAP_IN" ]]; then
  EXPORT_CMD+=(--map "$MAP_IN")
fi

"${EXPORT_CMD[@]}"

echo "==> Upload TSV -> Anki"
SYNC_CMD=(
  python3 -m tools.anki.sync.tsv_to_anki
  --tsv "$OUT_TSV"
  --anki-url "$ANKI_URL"
)

if [[ -n "$MAP_IN" ]]; then
  SYNC_CMD+=(--map-in "$MAP_IN")
fi

if [[ -n "$MAP_OUT" ]]; then
  SYNC_CMD+=(--map-out "$MAP_OUT")
fi

"${SYNC_CMD[@]}"

echo "==> Done"
