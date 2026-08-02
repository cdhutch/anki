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

## Palette Comparison Demo

**Purpose:** built 2026-08-01, after the Solarized demo above, once it became
clear Craig's actual objective was a repo-wide default palette rather than
Solarized specifically. A three-way A/B/C comparison (Solarized / Monochrome /
Warm-Gruvbox-style) of composite card mockups — not raw swatches like the
Solarized demo above — organized around Craig's real accessibility need: iOS
Settings → Accessibility → Display & Text Size → Color Filters → Color Tint →
Hue set near-full-left, a red-dominant "night vision" filter Craig uses ~10%
of the time (vs. ~60% ordinary day mode, ~30% ordinary night mode). Since that
filter is a hue-shift across the whole display, not just a darkening, the
interesting question is which palette stays distinguishable once a red
overlay sits on top of it — see `anki/notes/palette_comparison/palette-compare-doc.md`
for the full three-pass testing methodology.

**Outcome:** Craig tested all candidates on-device and chose **Gruvbox**
("Warm" in the note files/CSS), with Accent B corrected from Gruvbox's olive
green to Gruvbox blue (`#076678`/`#83a598`) after testing showed green sat too
close in hue to the secondary-text gray to stay distinct. Gruvbox has since
been rolled out as the actual production palette for the UA domain — see
`tools/anki/setup/setup_ua_note_types.py` and `setup_ua_pvom_note_type.py`,
and CLAUDE.md's 2026-08-01 log entry for the full writeup.

**Contents (6 notes)** under `anki/notes/palette_comparison/`:
- 3 "iteration" cards (`palette-compare-solarized`, `-monochrome`, `-warm`) —
  each a composite mini-mockup of an actual `UA_Lexeme` card (lemma/meta/
  gloss/example/cf line) rendered entirely in one candidate palette
- 1 reference card (`palette-compare-reference`) — all three palettes' roles
  stacked in one place for a fast side-by-side glance
- 1 status-colors card (`palette-compare-status`, added after Gruvbox was
  chosen and rolled out) — previews the typing-feedback/Compare-card status
  system (success/error/warning/info) using the exact classes and hex values
  shipped in production, specifically so Craig can confirm the red (error)
  and orange (warning) colors don't wash out under the red-tint filter before
  treating that choice as final
- 1 documentation card (`palette-compare-doc`) — the three-pass testing order
  and what to check in each pass, in-app

Unlike the Solarized demo above, colors here are applied via CSS classes keyed
to `.nightMode` (`.pc-<palette>-bg/primary/secondary/accent-a/accent-b`, plus
`fb-*`/`status-*`/`compare-*` for the status-colors card) rather than fixed
inline colors — the same card face live-flips with the device's actual
current appearance, so all three test passes look at the identical card
rather than a precomputed side-by-side.

**Note type:** `Palette_Comparison_Demo` (fields: `NoteID`, `Front`, `Back`).
**Deck:** `Demo::Palette_Comparison`.

**To load into Anki** (Anki must be running with AnkiConnect):

```
python tools/anki/setup/setup_palette_comparison_demo.py --dry-run   # preview, no writes
python tools/anki/setup/setup_palette_comparison_demo.py              # creates model + loads all 6 notes
```

Re-running is idempotent, same mechanism as the Solarized demo above.

**Cleanup, once you're done evaluating:** delete the `Palette_Comparison_Demo`
note type and `Demo::Palette_Comparison` deck from Anki, then remove
`anki/notes/palette_comparison/` and
`tools/anki/setup/setup_palette_comparison_demo.py` from the repo (`git rm -r`,
run by you per this repo's rules). If both demos in this file are being
cleaned up together, `domains/demo/` itself can go too.
