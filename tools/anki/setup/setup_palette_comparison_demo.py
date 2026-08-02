#!/usr/bin/env python3
"""Palette comparison demo — model + note loader.

Creates (or updates) the `Palette_Comparison_Demo` note type in Anki, then
loads all CNSF v0 notes under
    domains/demo/anki/notes/palette_comparison/*.md
into the `Demo::Palette_Comparison` deck via AnkiConnect.

Built 2026-08-01 alongside the UA-domain Solarized rollout (CLAUDE.md item
1/3), per Craig's request: a side-by-side comparison of three candidate
palettes, organized specifically around legibility under iOS's Color
Filters -> Color Tint -> Hue (near-left = red-dominant) accessibility
setting -- a "red-light night mode" Craig uses to protect night vision.
Since this filter tints the whole display, it's a hue-shift, not just a
darkening -- so the interesting question isn't just "light vs dark" but
"which of these color choices stays distinguishable once a red overlay is
sitting on top of it."

The three candidates (see palette-compare-doc.md for the full writeup):
  1. Solarized -- this repo's current choice (cool-toned: cyan/green
     accents). The thing actually being stress-tested here, since a red
     filter fights hardest against cool hues.
  2. Monochrome -- pure luminance-based, no hue-coded meaning at all
     (accents differentiated by weight/style instead: bold vs italic).
     Can't be hue-shifted away, by construction.
  3. Warm (Gruvbox-style) -- already orange/red/yellow-leaning, on the
     theory that colors close to the filter's own hue might survive it
     better than colors the filter fights against.

Testing is a three-pass walkthrough, in this order (per Craig 2026-08-01):
  1. Day mode (device appearance: Light, red-tint filter off)
  2. Night Mode (device appearance: Dark, red-tint filter off)
  3. Night Mode + the iOS red-tint Color Filter turned on
Deck shape (per Craig 2026-08-01): one card per palette "iteration" -- a
composite mini-mockup of an actual card (lemma/meta/gloss/example/cf line,
mirroring UA_Lexeme's own structure) rendered entirely in that palette --
rather than the palette decomposed into isolated role-by-role swatches.
Colors are applied via CSS classes keyed to `.nightMode` (see the CSS block
below), not fixed inline colors -- so the SAME card face automatically
shows its light or dark variant depending on the device's actual current
appearance, and all three passes look at identical cards rather than a
precomputed front/back comparison. This is a deliberate difference from
Solarized_Palette_Demo, where the swatches are fixed on purpose (that deck
demonstrates the raw palette; this one demonstrates how each candidate
actually renders on something that looks like a real card).

Craig judges the actual result on his own devices under the real filter --
this script and its notes just get the three candidates in front of him
side by side. Same throwaway-demo shape as setup_solarized_demo.py (see
that script's docstring for the CNSF-loading mechanics this one reuses).

A fifth card, palette-compare-status, was added 2026-08-01 after Gruvbox
("Warm" above) was chosen and rolled out to the real UA templates: it
previews the status-color system (success/error/warning/info -- typing-
feedback script + Compare card) using the EXACT classes/hex values shipped
in setup_ua_note_types.py / setup_ua_pvom_note_type.py, specifically to
verify red/error and orange/warning don't wash out under the red-tint
filter -- the one thing Claude can't preview directly and Craig asked to
have confirmed on-device before treating it as final.

Usage:
    python tools/anki/setup/setup_palette_comparison_demo.py [--dry-run] [--anki-url URL]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402
from tools.anki.cnsf_parse import load_cnsf_note  # noqa: E402

ANKI_URL_DEFAULT = "http://127.0.0.1:8765"
MODEL_NAME = "Palette_Comparison_Demo"
DECK_NAME = "Demo::Palette_Comparison"
NOTES_DIR = REPO_ROOT / "domains" / "demo" / "anki" / "notes" / "palette_comparison"

FIELDS = ["NoteID", "Front", "Back"]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
# Card chrome (.card / hr#answer / table / note-id) is deliberately neutral
# gray, NOT tied to any of the three candidate palettes -- a neutral surround
# avoids biasing which one looks best. Everything inside a mini-card or
# ref-block (background AND text) uses the .pc-<palette>-* classes below,
# which DO live-flip via .nightMode -- unlike Solarized_Palette_Demo's raw
# swatches (fixed inline colors on purpose, since that deck shows the raw
# palette). Here the live behavior is the point: Craig's three-pass test
# (Day mode / Night Mode / Night Mode + red-tint filter) needs the same
# card face to actually change with the device's real appearance.
# No .night_mode duplicates -- per Craig 2026-08-01, that duplication was
# purposeless (Android isn't one of his devices) and is being dropped going
# forward rather than carried into new demo content.

CSS = """\
.card {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
  font-size: 17px;
  line-height: 1.5;
  color: #333333;
  background-color: #f5f5f5;
  max-width: 680px;
  margin: 0 auto;
  padding: 22px 24px;
  text-align: left;
}

hr#answer {
  border: none;
  border-top: 1px solid #bbbbbb;
  margin: 20px 0;
}

.swatch-title { font-size: 22px; font-weight: 700; margin-bottom: 10px; }
.usage-note { font-size: 14px; margin-top: 10px; }
.swatch-role { font-size: 15px; margin-top: 6px; }

.grid-heading { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 14px 0 6px 0; color: #073642; }

/* Reference card: same "colored text on colored background" technique as
   the mini-card mockups above -- per Craig 2026-08-01, not a flat swatch
   grid ("it doesn't need to be a grid; iterations of colored text on
   color backgrounds would be the best use case"). Reuses .mini-card as
   the per-palette background wrapper; .ref-line is one labeled text
   sample per role within it. */
.ref-block { margin-bottom: 14px; }
.ref-name { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.ref-line { font-size: 15px; margin: 4px 0; }

table.control-code-table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }
table.control-code-table th, table.control-code-table td { border: 1px solid #bbbbbb; padding: 6px 10px; text-align: left; vertical-align: top; }
table.control-code-table th { background-color: #e8e8e8; font-weight: 700; }
code.inline { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #e8e8e8; padding: 1px 5px; border-radius: 4px; }

.note-id { font-size: 10px; color: #999999; text-align: right; margin-top: 18px; }

/* Dark mode -- chrome only (neutral gray, not tied to any candidate palette) */
.nightMode .card { color: #cccccc; background-color: #1e1e1e; }
.nightMode hr#answer { border-top-color: #444444; }
.nightMode .grid-heading { color: #dddddd; }
.nightMode table.control-code-table th { background-color: #2a2a2a; }
.nightMode table.control-code-table th, .nightMode table.control-code-table td { border-color: #444444; }
.nightMode code.inline { background: #2a2a2a; }
.nightMode .note-id { color: #777777; }

/* ------------------------------------------------------------------------
   Mini-card mockup -- one composite "what would an actual card look like"
   preview per palette, rather than the palette broken into isolated role
   swatches. Per Craig 2026-08-01: "I see a demo deck with multiple cards,
   each with their own iteration of the palette. From that we choose the
   best iteration for all three modes." Structural roles (lemma/meta/gloss/
   example/cf) mirror the live UA_Lexeme card's own .lemma/.pos+.gender/
   .gloss/.example-ua/.confusable classes.
   ------------------------------------------------------------------------ */

.mini-card { border-radius: 12px; padding: 20px 22px; border: 1px solid rgba(0,0,0,0.15); }
.mini-lemma { font-size: 26px; font-weight: bold; margin-bottom: 4px; }
.mini-meta { font-size: 13px; font-style: italic; margin-bottom: 12px; }
.mini-gloss { font-size: 19px; font-weight: bold; margin-bottom: 6px; }
.mini-example { font-size: 15px; font-style: italic; margin-bottom: 10px; }
.mini-cf { font-size: 14px; font-style: italic; }

/* ------------------------------------------------------------------------
   Palette color classes -- these are what actually live-flip with device
   appearance via .nightMode, unlike the fixed-inline-color swatches in
   Solarized_Palette_Demo. The point of THIS deck is a real three-pass
   walkthrough (Day mode -> Night Mode -> Night Mode + iOS red-tint Color
   Filter, per Craig 2026-08-01): each iteration card renders its light or
   dark variant automatically based on whatever mode the device is
   actually in when you view it, so all three passes look at the exact
   same card face, not a precomputed side-by-side. Background and text
   roles are separate classes (not bundled) so the same mini-card markup
   composes them freely per element.
   ------------------------------------------------------------------------ */

/* Solarized (this repo's current choice) */
.pc-solarized-bg        { background-color: #fdf6e3; }
.pc-solarized-primary   { color: #586e75; }
.pc-solarized-secondary { color: #93a1a1; }
.pc-solarized-accent-a  { color: #2aa198; }
.pc-solarized-accent-b  { color: #859900; }
.nightMode .pc-solarized-bg        { background-color: #032029; }
.nightMode .pc-solarized-primary   { color: #657b83; }
.nightMode .pc-solarized-secondary { color: #586e75; }
/* accents keep the same hex in both modes by Solarized design -- no override */

/* Monochrome (hue-independent -- accents differentiated by weight/style, not color) */
.pc-mono-bg        { background-color: #fafafa; }
.pc-mono-primary   { color: #1a1a1a; }
.pc-mono-secondary { color: #666666; }
.pc-mono-accent-a  { color: #000000; }
.pc-mono-accent-b  { color: #333333; }
.nightMode .pc-mono-bg        { background-color: #121212; }
.nightMode .pc-mono-primary   { color: #e8e8e8; }
.nightMode .pc-mono-secondary { color: #a0a0a0; }
.nightMode .pc-mono-accent-a  { color: #ffffff; }
.nightMode .pc-mono-accent-b  { color: #cccccc; }

/* Warm (Gruvbox-style -- already orange/red/yellow-leaning). Accent B was
   originally Gruvbox green (#79740e/#b8bb26), matching Solarized's green
   for a same-hue cross-palette comparison -- but per Craig 2026-08-01, it
   sat too close in hue to the warm-gray secondary to stay distinct,
   especially under a hue-shifting filter. Switched to Gruvbox blue
   (#076678/#83a598), the hue furthest from both secondary's warm gray and
   Accent A's orange. */
.pc-warm-bg        { background-color: #fbf1c7; }
.pc-warm-primary   { color: #3c3836; }
.pc-warm-secondary { color: #7c6f64; }
.pc-warm-accent-a  { color: #af3a03; }
.pc-warm-accent-b  { color: #076678; }
.nightMode .pc-warm-bg        { background-color: #282828; }
.nightMode .pc-warm-primary   { color: #ebdbb2; }
.nightMode .pc-warm-secondary { color: #a89984; }
.nightMode .pc-warm-accent-a  { color: #fe8019; }
.nightMode .pc-warm-accent-b  { color: #83a598; }

/* ------------------------------------------------------------------------
   Status colors -- added 2026-08-01, after Gruvbox ("Warm" above) was
   chosen and rolled out to the real UA templates (setup_ua_note_types.py /
   setup_ua_pvom_note_type.py). These are copied VERBATIM (same class names,
   same hex values) from that production CSS, not re-derived here -- the
   point of this card is to preview the exact colors that shipped, not an
   approximation. Per Craig 2026-08-01: keep the Compare card / typing-
   feedback status colors close to their pre-existing blue/green/red/orange
   roles, but make sure red and orange specifically do NOT wash out under
   the red-tint night filter -- dark-mode red/orange below use Gruvbox's
   *bright* tier (not the muted/neutral tier) for maximum luminance contrast
   against the dark background, which is the actual thing this card exists
   to validate. Rendered against a Gruvbox mini-card background (reusing
   .pc-warm-bg) rather than this deck's neutral gray chrome, since that's
   what these colors will actually sit on in production. */
.fb-headline { font-size: 20px; font-weight: bold; margin-bottom: 4px; }
.fb-sub { font-size: 14px; margin-bottom: 10px; }
.fb-label { font-size: 15px; font-weight: bold; margin-bottom: 4px; }
.fb-value { font-size: 15px; margin-bottom: 10px; }
.fb-note { font-size: 13px; }

.status-success { color: #79740e; }
.status-error { color: #9d0006; }
.status-warning { color: #af3a03; }
.status-info { color: #076678; }
.status-neutral { color: #7c6f64; }
.nightMode .status-success { color: #b8bb26; }
.nightMode .status-error { color: #fb4934; }
.nightMode .status-warning { color: #fe8019; }
.nightMode .status-info { color: #83a598; }
.nightMode .status-neutral { color: #a89984; }

/* Compare-card roles (same source: setup_ua_note_types.py's COMPARISON_FRONT/BACK) */
.compare-prompt-header { font-size: 15px; font-weight: bold; margin-bottom: 8px; color: #076678; }
.nightMode .compare-prompt-header { color: #83a598; }
.compare-warning { font-size: 14px; font-style: italic; padding: 10px 12px; border: 1px dashed; border-radius: 4px; color: #9d0006; border-color: #9d0006; margin-bottom: 10px; }
.nightMode .compare-warning { color: #fb4934; border-color: #fb4934; }
.compare-chip-word { font-size: 16px; font-weight: bold; padding: 8px 12px; border-left: 3px solid; color: #3c3836; background-color: #ebdbb2; border-left-color: #076678; display: inline-block; margin-bottom: 10px; }
.nightMode .compare-chip-word { color: #ebdbb2; background-color: #3c3836; border-left-color: #83a598; }
.compare-reveal-header { font-size: 16px; font-weight: bold; margin-bottom: 4px; color: #79740e; }
.nightMode .compare-reveal-header { color: #b8bb26; }
.compare-correct-sub { font-size: 13px; color: #79740e; }
.nightMode .compare-correct-sub { color: #b8bb26; }

.status-demo-block { margin-bottom: 16px; }
"""

# ---------------------------------------------------------------------------
# Card template (single template; content is fully pre-rendered per note)
# ---------------------------------------------------------------------------

CARD_FRONT = "{{Front}}\n"
CARD_BACK = "{{FrontSide}}\n<hr id=\"answer\">\n{{Back}}\n<div class=\"note-id\">{{NoteID}}</div>\n"
TEMPLATES = [("Compare", CARD_FRONT, CARD_BACK)]


# ---------------------------------------------------------------------------
# Model create/update (mirrors setup_solarized_demo.py)
# ---------------------------------------------------------------------------

def _sync_fields(model_name: str, desired: list[str], url: str) -> None:
    existing: list[str] = anki_request("modelFieldNames", {"modelName": model_name}, url=url) or []
    to_add = [f for f in desired if f not in existing]
    to_remove = [f for f in existing if f not in desired]
    if not to_add and not to_remove:
        print("    fields: no changes")
        return
    print(f"    ⚠  field changes needed -- delete and recreate {model_name} in Anki, then re-run.")
    for field in to_add:
        print(f"       + add   : {field}")
    for field in to_remove:
        print(f"       - remove: {field}")
    raise RuntimeError(
        f"Cannot add/remove fields on existing model '{model_name}' via AnkiConnect. "
        f"Delete the model in Anki (Tools -> Manage Note Types) and re-run."
    )


def _sync_templates(model_name: str, templates: list[tuple[str, str, str]], url: str) -> None:
    model_info: dict = anki_request("modelTemplates", {"modelName": model_name}, url=url) or {}
    existing_names = list(model_info.keys())
    desired_names = [t[0] for t in templates]

    for name, front, back in templates:
        if name in existing_names or (not existing_names and name == desired_names[0]):
            actual = name if name in existing_names else existing_names[0]
            anki_request(
                "updateModelTemplates",
                {"model": {"name": model_name, "templates": {actual: {"Front": front, "Back": back}}}},
                url=url,
            )
            print(f"    templates: updated {actual!r}")
        else:
            anki_request(
                "addCardToModel",
                {"modelName": model_name, "cardName": name, "qfmt": front, "afmt": back},
                url=url,
            )
            print(f"    templates: added {name!r}")

    stray = [n for n in existing_names if n not in desired_names]
    for stray_name in stray:
        print(f"    ⚠  removing stray template {stray_name!r} ...")
        anki_request("removeCardFromTemplate", {"modelName": model_name, "templateName": stray_name}, url=url)


def ensure_model(url: str) -> None:
    existing_models = anki_request("modelNames", {}, url=url) or []
    if MODEL_NAME not in existing_models:
        anki_request(
            "createModel",
            {
                "modelName": MODEL_NAME,
                "inOrderFields": FIELDS,
                "css": CSS,
                "isCloze": False,
                "cardTemplates": [{"Name": n, "Front": f, "Back": b} for n, f, b in TEMPLATES],
            },
            url=url,
        )
        print(f"CREATED model: {MODEL_NAME}")
    else:
        print(f"UPDATE model:  {MODEL_NAME}")
        _sync_fields(MODEL_NAME, FIELDS, url)
        _sync_templates(MODEL_NAME, TEMPLATES, url)
        anki_request("updateModelStyling", {"model": {"name": MODEL_NAME, "css": CSS}}, url=url)
        print("    css: updated")


def ensure_deck(url: str) -> None:
    anki_request("createDeck", {"deck": DECK_NAME}, url=url)
    print(f"OK deck: {DECK_NAME}")


# ---------------------------------------------------------------------------
# Note loading (identical mechanics to setup_solarized_demo.py)
# ---------------------------------------------------------------------------

def load_notes(url: str, dry_run: bool) -> None:
    if not NOTES_DIR.is_dir():
        raise SystemExit(f"Notes directory not found: {NOTES_DIR}")

    note_files = sorted(NOTES_DIR.glob("*.md"))
    if not note_files:
        raise SystemExit(f"No .md note files found under: {NOTES_DIR}")

    print(f"\nFound {len(note_files)} CNSF note file(s) under {NOTES_DIR}\n")

    created = 0
    updated = 0

    for path in note_files:
        note = load_cnsf_note(path)
        meta = note.meta
        note_id = meta["note_id"]
        anki_meta = meta.get("anki") or {}
        model = anki_meta.get("model", MODEL_NAME)
        deck = anki_meta.get("deck", DECK_NAME)
        tags = list(meta.get("tags") or [])

        fields = {
            "NoteID": note_id,
            "Front": note.front_md,
            "Back": note.back_md,
        }

        if dry_run:
            print(f"[dry-run] would sync note_id={note_id} model={model} deck={deck} tags={tags}")
            continue

        existing_ids = anki_request("findNotes", {"query": f'"NoteID:{note_id}"'}, url=url) or []

        if existing_ids:
            anki_note_id = existing_ids[0]
            anki_request(
                "updateNoteFields",
                {"note": {"id": anki_note_id, "fields": fields}},
                url=url,
            )
            current_tags = anki_request("getNoteTags", {"note": anki_note_id}, url=url) or []
            if current_tags:
                anki_request("removeTags", {"notes": [anki_note_id], "tags": " ".join(current_tags)}, url=url)
            if tags:
                anki_request("addTags", {"notes": [anki_note_id], "tags": " ".join(tags)}, url=url)
            print(f"UPDATED note_id={note_id} (Anki noteId={anki_note_id})")
            updated += 1
        else:
            new_id = anki_request(
                "addNote",
                {
                    "note": {
                        "deckName": deck,
                        "modelName": model,
                        "fields": fields,
                        "tags": tags,
                        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
                    }
                },
                url=url,
            )
            print(f"CREATED note_id={note_id} (Anki noteId={new_id})")
            created += 1

    print(f"\nDone. Created {created}, updated {updated}, total {len(note_files)}.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anki-url", default=ANKI_URL_DEFAULT, help="AnkiConnect URL")
    ap.add_argument("--dry-run", action="store_true", help="Parse and print what would happen; no AnkiConnect calls that mutate state")
    args = ap.parse_args()

    if not args.dry_run:
        version = anki_request("version", {}, url=args.anki_url)
        print(f"AnkiConnect version: {version}\n")
        ensure_model(args.anki_url)
        ensure_deck(args.anki_url)
    else:
        print("[dry-run] skipping model/deck creation and AnkiConnect version check\n")

    load_notes(args.anki_url, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
