#!/usr/bin/env bash
# publish_public.sh — Export, sanitize, and stage a public B737 deck release.
#
# Usage:
#   bash tools/release/publish_public.sh 1.1.0
#
# What it does:
#   1. Exports the B737 deck from Anki via AnkiConnect
#   2. Strips operator references from the .apkg
#   3. Verifies sanitization and pauses for review
#   4. Clones the public releases repo to /tmp/anki-b737-releases
#   5. Copies the sanitized .apkg there
#   6. Opens a Terminal window in that folder so you can run gh release create

set -euo pipefail

VERSION="${1:?Usage: $0 <version>  e.g. $0 1.1.0}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RELEASES_DIR="$REPO_ROOT/releases"
RAW_PKG="$RELEASES_DIR/B737-v${VERSION}.apkg"
PUBLIC_PKG="$RELEASES_DIR/B737-v${VERSION}-public.apkg"
PUBLIC_REPO="https://github.com/cdhutch/anki-b737-releases.git"
TMP_DIR="/tmp/anki-b737-releases"

echo "==> Exporting B737 deck from Anki (v${VERSION})..."
curl -s localhost:8765 -X POST -d "{
  \"action\": \"exportPackage\",
  \"version\": 6,
  \"params\": {
    \"deck\": \"B737\",
    \"path\": \"${RAW_PKG}\",
    \"includeSched\": false
  }
}" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if r.get('error'):
    print('AnkiConnect error:', r['error']); sys.exit(1)
if not r.get('result'):
    print('Export failed — is Anki running?'); sys.exit(1)
print('  Export OK')
"

echo "==> Stripping operator references..."
python3 "$REPO_ROOT/tools/anki/export/strip_operator_refs.py" \
  --in  "$RAW_PKG" \
  --out "$PUBLIC_PKG"

echo "==> Verifying sanitization..."
python3 - "$PUBLIC_PKG" <<'PYEOF'
import sys, zipfile, sqlite3, tempfile, os

apkg = sys.argv[1]
with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(apkg) as zf:
        zf.extractall(tmp)
    db_path = next(
        (os.path.join(tmp, n) for n in ["collection.anki21", "collection.anki2"]
         if os.path.exists(os.path.join(tmp, n))),
        None
    )
    if not db_path:
        print("ERROR: no Anki database found in package"); sys.exit(1)
    conn = sqlite3.connect(db_path)
    def count(term):
        return conn.execute("SELECT COUNT(*) FROM notes WHERE flds LIKE ?", (f"%{term}%",)).fetchone()[0]
    print(f"  {'Term':<35} {'Matches':>7}  {'Status'}")
    print(f"  {'-'*35} {'-'*7}  {'-'*6}")
    checks = [
        ("American Airlines",           0),
        ("American Airlines B737",      0),
    ]
    controls = [
        ("Aircraft",  None),
        ("B737",      None),
        ("AOM",       None),
    ]
    fail = False
    for term, expected in checks:
        n = count(term)
        status = "PASS" if n == expected else "FAIL"
        if status == "FAIL":
            fail = True
        print(f"  {term:<35} {n:>7}  {status}")
    print()
    for term, _ in controls:
        n = count(term)
        status = "OK" if n > 0 else "WARN (0 matches — is the DB empty?)"
        print(f"  {term:<35} {n:>7}  {status}")
    conn.close()
    if fail:
        print("\nSanitization FAILED — operator references remain. Aborting.")
        sys.exit(1)
    print("\nSanitization check passed.")
PYEOF

echo ""
read -r -p "Review the results above. Proceed with publishing? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo "==> Cloning public releases repo to $TMP_DIR..."
rm -rf "$TMP_DIR"
git clone "$PUBLIC_REPO" "$TMP_DIR"

echo "==> Copying sanitized package and README..."
cp "$PUBLIC_PKG" "$TMP_DIR/B737-v${VERSION}-public.apkg"
cp "$RELEASES_DIR/README-public.md" "$TMP_DIR/README.md"

echo ""
echo "Done. To publish:"
echo ""
echo "  cd $TMP_DIR"
echo "  git add README.md && git commit -m 'docs: update README' && git push"
echo "  gh release create v${VERSION} B737-v${VERSION}-public.apkg \\"
echo "    --title \"B737 Type Rating Deck v${VERSION}\" \\"
echo "    --notes \"B737 type rating flashcard deck for Anki 2.1+.\""
echo ""

# Open iTerm if available, fall back to Terminal
if open -a iTerm "$TMP_DIR" 2>/dev/null; then
  :
else
  open -a Terminal "$TMP_DIR"
fi
