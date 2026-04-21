#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-domains/b737/anki/notes/limits}"

if [[ ! -d "$ROOT" ]]; then
  echo "Not found: $ROOT" >&2
  exit 1
fi

echo "Scanning: $ROOT"
echo

echo "== Non-ASCII bullets (•) =="
grep -RIn '•' "$ROOT" || true
echo

echo "== Smart quotes / curly apostrophes =="
grep -RIn '[“”‘’]' "$ROOT" || true
echo

echo "== HTML list tags (<ul>, <ol>, <li>) =="
grep -RInE '</?(ul|ol|li)\b' "$ROOT" || true
echo

echo "== Tab characters =="
grep -RIn $'\t' "$ROOT" || true
echo

echo "Done."