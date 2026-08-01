# Demo domain

Standalone proof-of-concept content — not part of the b737 or ua production
domains. Created 2026-07-27 for the Solarized Light/Dark palette capability
demo (see `anki/notes/solarized_palette/`).

## Solarized Palette Demo

**Purpose:** a throwaway deck of 19 notes for evaluating the full Solarized
Light and Solarized Dark palettes on Craig's own devices (Mac, iPhone, iPad),
especially legibility in low-light/mobile use — and for proving out the
correct CSS "control code" (`.nightMode`) that makes a card's appearance
follow the device's light/dark mode on both macOS Anki and AnkiMobile.

**Contents:**
- 8 base-tone swatch notes (`solarized-demo-base03` … `solarized-demo-base3`)
- 8 accent-color swatch notes (`solarized-demo-yellow` … `solarized-demo-green`)
- 1 bonus comparison note (`solarized-demo-repo-dark-bg-vs-canonical`) — this
  repo's existing dark-mode background (`#032029`, used across every legacy
  note type's CSS) versus canonical Solarized base03 (`#002b36`)
- 1 reference-grid note showing the whole palette at a glance
- 1 documentation note walking through the `.nightMode` vs `.night_mode`
  research and how to test it on-device

**Note type:** `Solarized_Palette_Demo` (fields: `NoteID`, `Front`, `Back`).
**Deck:** `Demo::Solarized_Palette`.

**To load into Anki** (Anki must be running with AnkiConnect):

```
python tools/anki/setup/setup_solarized_demo.py --dry-run   # preview, no writes
python tools/anki/setup/setup_solarized_demo.py              # creates model + loads all 19 notes
```

Re-running is idempotent — it looks up each note by its `NoteID` field and
updates in place rather than duplicating.

**Note on the pre-commit hook:** these note files load into Anki via
`tools/anki/setup/setup_solarized_demo.py` directly (not the
`cnsf_to_anki.sh` shell pipeline), but the repo's `cnsf-canonical`
pre-commit hook still runs `cnsf_canonicalize.py --check` against every
staged CNSF file regardless of which loader you use. That canonicalizer's
`_normalize_meta()` unconditionally injects a `Verification Notes` field
default (a hardcoded assumption left over from the b737/ua note types) —
`Solarized_Palette_Demo` has no such field, so it doesn't get pushed to
Anki, but each note's `fields:` block explicitly includes
`Verification Notes: ''` anyway so the hook sees no drift and commits go
through cleanly. (First commit attempt of this deck failed the hook before
this was added — fixed 2026-07-27.)

**Cleanup, once you're done evaluating:** delete the `Solarized_Palette_Demo`
note type and `Demo::Solarized_Palette` deck from Anki (Tools → Manage Note
Types, and the deck list), then remove this `domains/demo/` folder and
`tools/anki/setup/setup_solarized_demo.py` from the repo (`git rm -r`, run by
you per this repo's rules).
