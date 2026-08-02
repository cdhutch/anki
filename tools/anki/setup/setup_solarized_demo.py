#!/usr/bin/env python3
"""Solarized Light/Dark palette capability demo — model + note loader.

Creates (or updates) the `Solarized_Palette_Demo` note type in Anki, then
loads all CNSF v0 notes under
    domains/demo/anki/notes/solarized_palette/*.md
into the `Demo::Solarized_Palette` deck via AnkiConnect.

This is a standalone proof-of-concept script (per Craig, 2026-07-27): it
follows this repo's usual "CNSF markdown -> Anki via AnkiConnect" shape
(YAML front matter + `# front_md` / `# back_md` sections, parsed with the
same `tools.anki.cnsf_parse.load_cnsf_note` used by the real pipeline), but
does NOT run the full L1->L4 shell pipeline (`cnsf_to_anki.sh` /
`cnsf_to_import_tsv.py` / `tsv_to_anki.py`). Two simplifications, both
intentional for a throwaway demo deck:

  1. `front_md` / `back_md` in these particular note files are already raw
     HTML (styled swatch divs), not prose Markdown. The real pipeline runs
     these through MultiMarkdown before import; this script skips that step
     and uses the section text as-is. That's fine for this deck's content
     but would NOT be fine for prose-style CNSF notes.
  2. No note_id -> Anki noteId mapping file is maintained. Instead this
     script looks up each note by its `NoteID` field via AnkiConnect's
     `findNotes` on every run, so re-running is idempotent without needing
     a mapping TSV. Fine at this deck's size (19 notes); the real pipeline
     uses a mapping file because it scales to hundreds/thousands of notes.

Night-mode control code (researched 2026-07-27, see the
"solarized-demo-control-codes" card for the full writeup and sources):
  - macOS Anki desktop AND AnkiMobile (iPhone/iPad) both key off `.nightMode`
    (camelCase). Confirmed via AnkiMobile's own manual and this repo's
    CLAUDE.md finding (2026-07-23 UA_Visual bug audit).
  - `.night_mode` (snake_case) is what AnkiDroid (Android) uses instead —
    not one of Craig's devices, included below only for parity with this
    repo's existing CSS convention (every legacy note type duplicates both
    selectors), not because it's required here.

Usage:
    python tools/anki/setup/setup_solarized_demo.py [--dry-run] [--anki-url URL]
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
MODEL_NAME = "Solarized_Palette_Demo"
DECK_NAME = "Demo::Solarized_Palette"
NOTES_DIR = REPO_ROOT / "domains" / "demo" / "anki" / "notes" / "solarized_palette"

FIELDS = ["NoteID", "Front", "Back"]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* ============================================================
   Solarized_Palette_Demo -- card styling

   Night-mode control code (researched 2026-07-27):
     - macOS Anki desktop AND AnkiMobile (iPhone/iPad) both key off the
       camelCase class `.nightMode`. Confirmed via AnkiMobile's own manual
       (docs.ankimobile.net/night-mode.html: ".card.nightMode {...}" and
       ".nightMode .myclass {...}") and via this repo's own CLAUDE.md
       finding (2026-07-23 UA_Visual bug audit).
     - The snake_case `.night_mode` selector is what AnkiDroid (Android)
       keys off instead (forums.ankiweb.net moderator reply, thread
       "Cards visible night-mode desktop, but not night-mode mobile").
       Craig's devices are Mac + iPhone + iPad only, so `.nightMode` alone
       is sufficient -- `.night_mode` rules below are included only for
       parity with the rest of this repo's CSS (update_legacy_css.py,
       setup_structured_model.py, etc. all duplicate both selectors) in
       case this deck is ever opened on Android.
   ============================================================ */

.card {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
  font-size: 17px;
  line-height: 1.5;
  color: #586e75;
  background-color: #fdf6e3;
  max-width: 640px;
  margin: 0 auto;
  padding: 22px 24px;
  text-align: left;
}

hr#answer {
  border: none;
  border-top: 1px solid #93a1a1;
  margin: 20px 0;
}

.swatch-block {
  height: 110px;
  border-radius: 10px;
  margin: 4px 0 14px 0;
  border: 1px solid rgba(0,0,0,0.15);
}

.swatch-title { font-size: 24px; font-weight: 700; margin-bottom: 2px; color: #073642; }
.swatch-hex { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 15px; color: #657b83; }
.swatch-role { font-size: 15px; margin-top: 6px; }

.legibility-row { display: flex; gap: 10px; margin-top: 16px; }
.legibility-box { flex: 1; border-radius: 8px; padding: 16px 10px; font-size: 15px; text-align: center; border: 1px solid rgba(0,0,0,0.1); }
.legibility-caption { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: #93a1a1; margin-top: 6px; }

.meta-row { font-size: 13px; color: #93a1a1; margin-top: 14px; }
.usage-note { font-size: 14px; margin-top: 10px; }

.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0 16px 0; }
.grid-swatch { border-radius: 6px; padding: 8px 6px; font-size: 11px; text-align: center; border: 1px solid rgba(0,0,0,0.12); color: #002b36; text-shadow: 0 0 3px rgba(255,255,255,0.6); }
.grid-swatch .name { font-weight: 700; }
.grid-swatch .hex  { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.grid-heading { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 14px 0 6px 0; color: #073642; }

table.control-code-table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }
table.control-code-table th, table.control-code-table td { border: 1px solid #93a1a1; padding: 6px 10px; text-align: left; vertical-align: top; }
table.control-code-table th { background-color: #eee8d5; font-weight: 700; }
code.inline { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #eee8d5; padding: 1px 5px; border-radius: 4px; }

.note-id { font-size: 10px; color: #93a1a1; text-align: right; margin-top: 18px; }

/* Dark mode (Solarized dark) -- card chrome only.
   Swatch blocks and legibility boxes use fixed inline background-colors
   (they ARE the thing being demonstrated) so they stay visually constant
   regardless of night mode; only the surrounding chrome re-themes. */
.nightMode .card { color: #93a1a1; background-color: #002b36; }
.night_mode .card { color: #93a1a1; background-color: #002b36; }

.nightMode hr#answer { border-top-color: #586e75; }
.night_mode hr#answer { border-top-color: #586e75; }

.nightMode .swatch-title { color: #eee8d5; }
.night_mode .swatch-title { color: #eee8d5; }
.nightMode .swatch-hex { color: #839496; }
.night_mode .swatch-hex { color: #839496; }
.nightMode .meta-row { color: #586e75; }
.night_mode .meta-row { color: #586e75; }
.nightMode .grid-heading { color: #eee8d5; }
.night_mode .grid-heading { color: #eee8d5; }
.nightMode table.control-code-table th { background-color: #073642; }
.night_mode table.control-code-table th { background-color: #073642; }
.nightMode table.control-code-table th, .nightMode table.control-code-table td { border-color: #586e75; }
.night_mode table.control-code-table th, .night_mode table.control-code-table td { border-color: #586e75; }
.nightMode code.inline { background: #073642; }
.night_mode code.inline { background: #073642; }
.nightMode .note-id { color: #586e75; }
.night_mode .note-id { color: #586e75; }
.nightMode .grid-swatch { text-shadow: 0 0 3px rgba(0,0,0,0.6); }
.night_mode .grid-swatch { text-shadow: 0 0 3px rgba(0,0,0,0.6); }
"""

# ---------------------------------------------------------------------------
# Card template (single template; content is fully pre-rendered per note)
# ---------------------------------------------------------------------------

CARD_FRONT = "{{Front}}\n"
CARD_BACK = "{{FrontSide}}\n<hr id=\"answer\">\n{{Back}}\n<div class=\"note-id\">{{NoteID}}</div>\n"
TEMPLATES = [("Swatch", CARD_FRONT, CARD_BACK)]


# ---------------------------------------------------------------------------
# Model create/update (mirrors tools/anki/setup/setup_structured_model.py)
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
# Note loading
# ---------------------------------------------------------------------------

def _cnsf_tags_to_anki(tags: list[str]) -> list[str]:
    # This demo's tags are already flat "prefix:value" tokens (domain:, topic:,
    # subtopic:, status:) -- no Tags_Ch-style remapping needed here, unlike the
    # b737/ua pipelines. Anki tags can't contain spaces; these don't have any.
    return list(tags)


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
        tags = _cnsf_tags_to_anki(meta.get("tags") or [])

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
