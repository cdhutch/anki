#!/usr/bin/env python3
"""tools/anki/inspect/mine_legacy_clozes.py — Non-destructive AnkiConnect crawl of the
legacy cloze decks, for confusable-word discovery.

New 2026-09-01, Craig. Craig used cloze deletions extensively in the old
`Legacy::UA_Legacy::*` and `Legacy::Ukrainian Active::*` deck trees to drill confusable-word
distinctions before the CNSF confusable-cluster registry (`confusable_clusters.yaml`)
existed. This script crawls those two deck trees via AnkiConnect (read-only actions only --
`findNotes` and `notesInfo`, no `updateNoteFields`/`deleteNotes`/anything mutating) and dumps
every note that contains cloze markup (`{{cN::...}}`, any note type -- not just notes whose
model is literally named "Cloze") to a scratch JSON file for a separate Claude pass to read,
cross-reference against the registry, and report confusable-pair candidates not yet captured.
This script does NOT write to confusable_clusters.yaml or any lexeme note itself -- see
CLAUDE.md "Big 3 Rules": Craig runs this, and any registry changes it turns up go through the
normal Claude-drafts/Craig-reviews-and-commits flow, not an automated write.

Output lands in `domains/ua/anki/tmp/` (gitignored scratch space, see .gitignore
`domains/**/anki/tmp/`), one JSON file per run, timestamped so repeat runs don't clobber each
other.

Usage (Craig runs this -- see CLAUDE.md Big 3 Rules):

    python tools/anki/inspect/mine_legacy_clozes.py

Options:

    --decks "Legacy::UA_Legacy" "Legacy::Ukrainian Active"   override the deck-tree roots
    --out PATH                                                override the output file path
    --url http://127.0.0.1:8765                               override the AnkiConnect URL
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DECKS = ["Legacy::UA_Legacy", "Legacy::Ukrainian Active"]
DEFAULT_OUT_DIR = REPO_ROOT / "domains/ua/anki/tmp"
ANKICONNECT_URL = "http://127.0.0.1:8765"
ANKICONNECT_VERSION = 6

CLOZE_RE = re.compile(r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def anki_request(url: str, action: str, params: dict | None = None) -> dict:
    body = {"action": action, "version": ANKICONNECT_VERSION}
    if params:
        body["params"] = params
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError as exc:
        print(
            f"error: could not reach AnkiConnect at {url} ({exc}). "
            "Is Anki running with the AnkiConnect add-on installed?",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if result.get("error"):
        print(f"error: AnkiConnect action {action!r} failed: {result['error']}", file=sys.stderr)
        raise SystemExit(2)
    return result["result"]


def strip_html(value: str) -> str:
    """Best-effort plain-text rendering of an Anki HTML field, for readability only --
    the raw field value is always preserved alongside this in the output."""
    text = value.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    return WS_RE.sub(" ", text).strip()


def extract_clozes(value: str) -> list[dict]:
    """Return every {{cN::text::hint}} span found in a raw field value."""
    spans = []
    for m in CLOZE_RE.finditer(value):
        cloze_num, cloze_text, hint = m.group(1), m.group(2), m.group(3)
        spans.append(
            {
                "cloze_num": int(cloze_num),
                "cloze_text": strip_html(cloze_text),
                "hint": strip_html(hint) if hint else None,
                "raw": m.group(0),
            }
        )
    return spans


def build_deck_query(deck_roots: list[str]) -> str:
    # `deck:"X"` already matches X and every subdeck in Anki's search syntax --
    # no wildcard needed. Quote each root (may contain spaces, e.g. "Ukrainian Active").
    clauses = [f'deck:"{root}"' for root in deck_roots]
    return " or ".join(clauses)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decks", nargs="+", default=DEFAULT_DECKS, help="Deck-tree roots to crawl (default: the two legacy trees)")
    ap.add_argument("--out", default=None, help="Output JSON path (default: domains/ua/anki/tmp/legacy_cloze_mine_<timestamp>.json)")
    ap.add_argument("--url", default=ANKICONNECT_URL, help="AnkiConnect URL (default: http://127.0.0.1:8765)")
    args = ap.parse_args()

    version = anki_request(args.url, "version")
    print(f"AnkiConnect version: {version}", file=sys.stderr)

    query = build_deck_query(args.decks)
    print(f"Query: {query}", file=sys.stderr)
    note_ids = anki_request(args.url, "findNotes", {"query": query})
    print(f"Notes found in {args.decks}: {len(note_ids)}", file=sys.stderr)

    if not note_ids:
        print("Nothing to mine -- check deck names with `deckNames` if this looks wrong.", file=sys.stderr)
        return 0

    notes_info = anki_request(args.url, "notesInfo", {"notes": note_ids})

    results = []
    for note in notes_info:
        fields = note.get("fields", {})
        cloze_by_field = {}
        for field_name, field_data in fields.items():
            value = field_data.get("value", "")
            spans = extract_clozes(value)
            if spans:
                cloze_by_field[field_name] = spans
        if not cloze_by_field:
            continue
        results.append(
            {
                "note_id": note["noteId"],
                "model_name": note.get("modelName"),
                "tags": note.get("tags", []),
                "cloze_fields": cloze_by_field,
                "all_fields": {
                    name: {
                        "raw": data.get("value", ""),
                        "text": strip_html(data.get("value", "")),
                    }
                    for name, data in fields.items()
                },
            }
        )

    print(f"Notes containing cloze markup: {len(results)} / {len(note_ids)}", file=sys.stderr)

    if args.out:
        out_path = Path(args.out)
    else:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = DEFAULT_OUT_DIR / f"legacy_cloze_mine_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "decks_queried": args.decks,
        "query": query,
        "note_count_total": len(note_ids),
        "note_count_with_clozes": len(results),
        "notes": results,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(REPO_ROOT) if REPO_ROOT in out_path.parents else out_path}", file=sys.stderr)
    print("This file is scratch output (gitignored) -- nothing in Anki or the CNSF corpus was modified.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
