# Solarized Palette Demo — Findings & Testing Guide

Built 2026-07-27 on branch `feature/anki-mobile-night-mode`. Covers the
Solarized Light/Dark capability demo under `domains/demo/anki/notes/solarized_palette/`
and `tools/anki/setup/setup_solarized_demo.py`. See `domains/demo/README.md`
for a shorter usage/cleanup summary — this doc is the full writeup.

**2026-08-01 update:** the `.nightMode`/`.night_mode` platform research below (section
1.1) is still the authoritative finding and is now applied throughout the UA domain's
CSS. The palette itself, however, changed — Solarized was superseded by **Gruvbox**
after a follow-up on-device comparison (see `domains/demo/README.md`'s "Palette
Comparison Demo" section and CLAUDE.md's 2026-08-01 log entry). This doc's palette
table (section 1.2) and canonical-vs-repo dark-bg comparison (section 1.3) remain
accurate for Solarized specifically, just no longer describe the repo's chosen palette.

---

## 1. Findings

### 1.1 The "AnkiMobile needs a different control code" premise was wrong

The task started from the assumption that AnkiMobile (iOS/iPadOS) requires a
different CSS selector than the macOS desktop client to detect night mode.
Research says otherwise:

| Platform | Selector Anki applies | Source |
|---|---|---|
| macOS Anki (desktop) | `.nightMode` (camelCase) | This repo's `CLAUDE.md`, 2026-07-23 `UA_Visual` bug audit |
| AnkiMobile (iPhone / iPad) | `.nightMode` — **same as macOS** | [AnkiMobile manual, Night Mode Styling](https://docs.ankimobile.net/night-mode.html) — shows `.card.nightMode {...}` and `.nightMode .myclass {...}` |
| AnkiDroid (Android — not one of Craig's devices) | `.night_mode` (snake_case) | [forums.ankiweb.net thread](https://forums.ankiweb.net/t/cards-visible-night-mode-desktop-but-not-night-mode-mobile/58229) — moderator reply: "desktop seems to prefer `nightMode`... AnkiDroid seems to prefer `night_mode`" |

**Conclusion:** the real platform split is Apple (`.nightMode`) vs. Android
(`.night_mode`), not macOS vs. AnkiMobile. Since Craig's devices are Mac,
iPhone, and iPad only, a single `.nightMode` rule set is sufficient. This
matches what this repo's own CLAUDE.md already found independently on
2026-07-23 (the `UA_Visual` note type's dark-mode rules were dead on every
platform because they used `.night_mode` instead of `.nightMode`).

The demo's CSS (`setup_solarized_demo.py`) uses `.nightMode` as the
operative selector. It also duplicates every rule under `.night_mode`,
**not because it's needed for Craig's devices**, but purely for parity with
the rest of this repo's existing CSS convention — `update_legacy_css.py`,
`setup_structured_model.py`, and every other legacy note type's styling
already duplicate both selectors on every rule.

### 1.2 Canonical Solarized palette

Confirmed against the original Solarized project (Ethan Schoonover,
[altercation/solarized](https://github.com/altercation/solarized)):

| Name | Hex | Role (canonical / this repo's current usage) |
|---|---|---|
| base03 | `#002b36` | Dark-mode background (canonical). This repo currently uses `#032029` instead — see 1.3. |
| base02 | `#073642` | Dark-mode background highlights (table headers, etc.) |
| base01 | `#586e75` | Light-mode body text (this repo's convention) |
| base00 | `#657b83` | Dark-mode body text (this repo's convention) |
| base0  | `#839496` | Canonical dark-mode body/emphasis alternative (unused in this repo) |
| base1  | `#93a1a1` | Light-mode secondary/comment text, captions, borders |
| base2  | `#eee8d5` | Light-mode background highlights (table headers, etc.) |
| base3  | `#fdf6e3` | Light-mode background (this repo's convention) |
| yellow | `#b58900` | Accent — unused in this repo |
| orange | `#cb4b16` | Accent — unused in this repo |
| red    | `#dc322f` | Accent — unused in this repo |
| magenta| `#d33682` | Accent — unused in this repo |
| violet | `#6c71c4` | Accent — unused in this repo |
| blue   | `#268bd2` | Accent — unused in this repo |
| cyan   | `#2aa198` | Accent — **already this repo's primary highlight color** (lemma/title/subsystem headers across all 7 legacy note types) |
| green  | `#859900` | Accent — **already this repo's "confusable" highlight color** (`UA_Lexeme`) |

By design, the 8 base tones swap roles between light and dark mode
(base03↔base3, base02↔base2, base01↔base1, base00↔base0); the 8 accent
colors keep the same hex value in both modes.

### 1.3 Repo's dark background is a near-canonical variant, not exact

Every existing note type's CSS in this repo
(`update_legacy_css.py`, `setup_structured_model.py`, `setup_table_model.py`,
etc.) sets the dark-mode card background to `#032029`, not canonical
Solarized base03 (`#002b36`). Close, but not identical. The demo includes a
dedicated comparison card (`solarized-demo-repo-dark-bg-vs-canonical`) with
both swatches side by side so this is easy to judge visually — the demo
deck's own chrome intentionally uses the canonical `#002b36` so the
difference is visible when you compare it against your other decks.

### 1.4 CNSF v0 quirk: `Verification Notes` auto-injection (hit this for real)

`tools/anki/cnsf_canonicalize.py`'s `_normalize_meta()` unconditionally adds
a `Verification Notes` field default to every note's `fields:` block unless
`note_type == "ua_verb"`. That's a hardcoded holdover from the b737/ua note
types and doesn't generalize — the `Solarized_Palette_Demo` model has no
such field, so it's never sent to Anki.

Original assumption was that this only mattered if you ran these files
through `cnsf_canonicalize.py --write` or `cnsf_to_anki.sh` by hand, since
`setup_solarized_demo.py` reads the files directly and doesn't invoke the
canonicalizer. That assumption was wrong: this repo's `cnsf-canonical`
**pre-commit hook** runs `cnsf_canonicalize.py --check` on every staged CNSF
file automatically, regardless of which loader you use — and the first
commit attempt of this deck failed that hook on all 19 note files for
exactly this reason.

**Fix applied:** every note's `fields:` block now explicitly sets
`Verification Notes: ''` instead of leaving it empty. Since
`_normalize_meta()` uses `setdefault()`, the key already being present
means no drift, and `cnsf_canonicalize.py --check` passes cleanly. Verified
locally against the actual `cnsf_canonicalize.py` before redelivering the
files (0/19 drift). The field still isn't pushed to Anki — it's inert
metadata that only exists to satisfy the hook.

### 1.5 The attached Claude Project's architecture doc doesn't match this repo

The "Anki Automation Architecture" document attached to this session's
Claude Project describes a `Tags_Ch` semicolon-separated tag field with
`src:`/`topic:`/`wf:` prefix governance. **The actual implemented pipeline
is different**: CNSF v0 (`docs/anki/contracts/CNSF_Spec_v0.md`), which uses
a YAML `tags:` *list* of already-prefixed strings (`domain:`, `topic:`,
`subtopic:`, `status:`), parsed by `tools/anki/cnsf_parse.py`. No `Tags_Ch`
field exists anywhere in the current repo. This demo follows the real,
implemented CNSF v0 convention. Worth reconciling the Project description
with reality at some point, or treating `CLAUDE.md` + the CNSF contracts
docs as the authoritative source going forward.

---

## 2. What's in the demo

- **Note type:** `Solarized_Palette_Demo` (fields: `NoteID`, `Front`, `Back`; one card template, "Swatch")
- **Deck:** `Demo::Solarized_Palette`
- **19 notes** under `domains/demo/anki/notes/solarized_palette/`:
  - 8 base-tone swatches (`solarized-demo-base03` … `solarized-demo-base3`)
  - 8 accent swatches (`solarized-demo-yellow` … `solarized-demo-green`)
  - 1 comparison card (`solarized-demo-repo-dark-bg-vs-canonical`)
  - 1 reference grid (`solarized-demo-reference-grid`) — all 16 canonical colors at a glance
  - 1 documentation card (`solarized-demo-control-codes`) — the 1.1 writeup, in-app

Each swatch card's **front** shows the color as a large block plus its name
and hex. The **back** shows the same hex rendered as *text* against both a
fixed light chip (`#fdf6e3`) and a fixed dark chip (`#002b36`), so you can
judge legibility in both contexts on one card without needing to toggle your
device's appearance mode. The swatch blocks and legibility chips use fixed
inline colors (deliberately not affected by night mode — showing the raw
palette is the point). Only the surrounding card chrome (background/text
outside those blocks) switches via `.nightMode` when your device's
appearance mode changes — that's what's actually being capability-tested.

---

## 3. Testing instructions

### 3.1 Load the deck

Anki must be open with AnkiConnect running (usually automatic once the
AnkiConnect add-on is installed).

```bash
cd /Users/craig/Documents/GitHub/anki
python tools/anki/setup/setup_solarized_demo.py --dry-run   # preview only, makes no changes
python tools/anki/setup/setup_solarized_demo.py              # creates the note type + loads all 19 notes
```

Expected output: `CREATED model: Solarized_Palette_Demo`, `OK deck:
Demo::Solarized_Palette`, then 19 `CREATED note_id=...` lines. Re-running is
safe — it looks up each note by its `NoteID` field and updates in place
(`UPDATED note_id=...`) instead of duplicating.

### 3.2 Test on macOS Anki (desktop)

1. Open the `Demo::Solarized_Palette` deck and study through a few cards in
   **light mode** first (System Settings → Appearance → Light, and Anki's
   own night-mode setting off or set to follow system).
2. Switch **System Settings → Appearance → Dark** (or toggle Anki's own
   night-mode preference directly if it doesn't follow the system).
3. Re-view the same cards. The card background/text should flip to
   Solarized Dark; the swatch blocks and legibility chips should look
   unchanged (they're fixed colors by design).
4. Check the `solarized-demo-reference-grid` and
   `solarized-demo-repo-dark-bg-vs-canonical` cards for the side-by-side
   comparisons, and `solarized-demo-control-codes` for the in-app writeup.

### 3.3 Test on AnkiMobile (iPhone / iPad)

1. Sync the deck to your device (AnkiWeb sync, same as any other deck).
2. Repeat the same light → dark comparison using Settings → Display &
   Brightness → Light/Dark (or Automatic), and AnkiMobile's own appearance
   setting if it doesn't follow the system automatically.
3. This is the core thing being demonstrated: since AnkiMobile and macOS
   both key off `.nightMode` (section 1.1), the card chrome should behave
   identically on both platforms — same flip behavior, same colors.
4. This is also the practical point of the deck: flip through the 16
   individual swatch + legibility cards specifically in a dim/low-light
   room on your phone or iPad, and note which colors read comfortably vs.
   which strain — that's the judgment call this demo exists to support.

### 3.4 Cleanup, once you're done evaluating

- In Anki: Tools → Manage Note Types → delete `Solarized_Palette_Demo`
  (this also removes its cards); delete the `Demo::Solarized_Palette` deck
  from the deck list.
- In the repo: remove `domains/demo/` and
  `tools/anki/setup/setup_solarized_demo.py` (`git rm -r`, run by you per
  this repo's rules — see `CLAUDE.md`'s "Big 3 Rules").
