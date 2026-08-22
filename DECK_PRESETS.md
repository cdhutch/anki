# Deck Presets — Specification

**This file is the single authority for what deck presets exist and what parameters
they carry.** It supersedes the preset content of `DECK_PRESET_MAPPING.md`,
`CLAUDE-fsrs-deck-configs.md`, `CLAUDE-deck-architecture.md` and
`docs/anki/options/*.md`, which describe four mutually incompatible architectures from
different eras. Those files stay as history; none of them is current.

Built 2026-08-20 from `tools/anki/inspect/survey_deck_presets.py`, run against live Anki:
122 decks, **85 presets** and 11 filtered decks. After the orphan deletion recorded in §7
the collection holds **32 presets** — 9 UA, 7 B737, 15 Legacy, and Anki's `Default`. **Live parameters are the baseline** — per Craig, what Anki
currently does is what the spec records, except where a change is listed under
"Changes to apply" below. The `.md` files above were read for *rationale*, not values.

Rebuild the survey any time with:

    python tools/anki/inspect/survey_deck_presets.py

---

## 0. Tooling

Four tools, and nothing else should touch presets:

| Tool | Direction | Notes |
|---|---|---|
| `tools/anki/inspect/survey_deck_presets.py` | read | Decks, presets, usage, orphans. The only one that can see a preset on zero decks. |
| `tools/anki/inspect/export_deck_presets.py` | Anki → `presets/` | One file per preset, all parameters except FSRS. No timestamp, so re-export + `git diff` is a drift detector. |
| `tools/anki/setup/create_deck_presets.py` | `presets/` → Anki | Idempotent. `--only NAME` to scope. Dry-run by default. |
| `tools/anki/setup/prune_orphan_presets.py` | delete | Zero-deck presets only, by id. Dry-run by default. |

**`presets/<slug>.json` is the source of truth for values.** The tables in §1–§3 are a
human-readable summary of those files; where they disagree, the files win.

**Superseded documents, all bannered rather than deleted:** `DECK_PRESET_MAPPING.md`,
`CLAUDE-fsrs-deck-configs.md`, `CLAUDE-deck-architecture.md`,
`docs/anki/options/b737_limits_options.md`, `docs/anki/options/b737_limits_trivia_options.md`,
`domains/b737/anki/presets/FSRS_Preset__B737_Systems.md`. That last one is worth singling
out: its policy section says *"do not attempt to automate FSRS settings via AnkiConnect"*
and *"this file is the source of truth; Anki is configured manually to match"* — the exact
inverse of what this repo now does. Its banner says so.
`docs/anki/options/anki_card_option_fields.md` is **not** superseded; it is a neutral list
of Anki's option fields and remains accurate.

Bannered 2026-08-21, after a sweep for surviving references: `CLAUDE.md`'s "Deck Presets
and Limit Configuration (2026-07-20)" subsection, which still presented the deleted tools
as a runnable workflow, and both `domains/*/anki/config/deck_limits.yaml`, which no code
reads any more — the two tools that read them were among the 23 deleted. The YAML files
are kept for their commentary; every live limit is a parameter in `presets/<slug>.json`.

**23 superseded tools and data files were deleted 2026-08-20**, none of which was wired
into `make`.
Thirteen wrote to Anki outside this pipeline — including `setup_fsrs_deck_configs.py`,
which recreated `UA FSRS` and `B737 FSRS` after they had been pruned as orphans, and four
`create_*_preset.py` scripts carrying the same clone-without-lookup bug that produced the
53 orphans. Also removed: `verify_b737_deck_configs.py`, which called `saveDeckConfig`
despite its name, and both `preset_definitions.json` files, which specified review limits
of 100/6/8/10/8 against a live 9999.

Kept because they are read-only and still accurate: `audit_ua_decks.py`,
`check_deck_hierarchy.py`, `survey_ua_decks.py`, `analyze_display_order.py`,
`configure_line_flying_decks.py` (read-only despite the name, and the one `make` target).
`query_anki_db.py` is left in place but searches for `collection.db`, a filename modern
Anki has not used in years — it has probably never found a collection.

---

## 1. Shared baseline

Every UA preset carries these identically — 44 of 46 parameters. The five modern B737
presets match except where their own table notes a difference. A preset that deviates
from the baseline without a documented reason is drift.

**Daily limits**

| Parameter | Value |
|---|---|
| `rev.perDay` | `9999` |

**New cards**

| Parameter | Value |
|---|---|
| `new.delays` | `[15.0, 180.0]` |
| `new.order` | `1` |
| `new.ints` | `[1, 4, 0]` |
| `new.initialFactor` | `2500` |
| `new.separate` | `true` |
| `newPerDayMinimum` | `0` |

**Lapses**

| Parameter | Value |
|---|---|
| `lapse.delays` | `[10.0]` |
| `lapse.leechAction` | `1` |
| `lapse.leechFails` | `8` |
| `lapse.minInt` | `1` |
| `lapse.mult` | `0.0` |

**Display order**

| Parameter | Value |
|---|---|
| `newGatherPriority` | `3` |
| `newSortOrder` | `4` |
| `newMix` | `0` |
| `interdayLearningMix` | `0` |
| `reviewOrder` | `0` |

**FSRS**

| Parameter | Value |
|---|---|
| `desiredRetention` | `0.9` |
| `ignoreRevlogsBeforeDate` | `"1970-01-01"` |
| `easyDaysPercentages` | `[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]` |
| `weightSearch` | `""` |

**Burying**

| Parameter | Value |
|---|---|
| `new.bury` | `true` |
| `rev.bury` | `true` |
| `buryInterdayLearning` | `false` |

**Timers**

| Parameter | Value |
|---|---|
| `maxTaken` | `60` |
| `timer` | `0` |
| `stopTimerOnAnswer` | `false` |

**Auto advance**

| Parameter | Value |
|---|---|
| `secondsToShowQuestion` | `0.0` |
| `secondsToShowAnswer` | `0.0` |
| `questionAction` | `0` |
| `answerAction` | `0` |

**Advanced**

| Parameter | Value |
|---|---|
| `rev.maxIvl` | `36500` |
| `rev.ease4` | `1.3` |
| `rev.hardFactor` | `1.2` |
| `rev.ivlFct` | `1.0` |
| `rev.fuzz` | `0.05` |
| `rev.minSpace` | `1` |
| `sm2Retention` | `0.9` |

**Audio**

| Parameter | Value |
|---|---|
| `autoplay` | `true` |
| `replayq` | `true` |
| `waitForAudio` | `false` |

**Display-order enum values, pinned against live Anki 2026-08-20** by reading the GUI
labels back off two presets. The decode table in `inspect_deck_configs.py` is stale — it
maps only values 0–2 for gather priority — so use these:

| Field | `0` | `3` | `4` |
|---|---|---|---|
| `newGatherPriority` | Deck | Random Notes | — |
| `newSortOrder` | Card type, then order gathered | — | Random |
| `reviewOrder` | Due date, then random | Ascending intervals | — |
| `newMix` / `interdayLearningMix` | Mix with reviews | — | — |

Values not listed were not observed and must not be guessed at — read the label in the
GUI and add it here.

`new.perDay` and `fsrsParams6` are deliberately per-preset and are listed below.
`fsrsWeights` and `fsrsParams5` are legacy keys, empty everywhere — **this Anki stores
FSRS parameters in `fsrsParams6`.** Reading the old keys makes it look as though FSRS
has never been optimized, which is how that error got into an earlier report.

---

## 2. UA presets

Nine presets, one per deck plus two pass-throughs. Structure matches
`DECK_PRESET_MAPPING.md` exactly, and every `new.perDay` matches it too. **Review limits
do not** — that file specifies 8/6/10/100, live is 9999 everywhere. Live wins per Craig.

| Preset | Deck | new/day | FSRS params |
|---|---|---|---|
| `UA` | `UA` | 50 | shared vector |
| `UA Production Pass-through` | `UA::Production` | 9999 | shared vector |
| `UA Recognition Pass-through` | `UA::Recognition` | 9999 | shared vector |
| `UA Lexeme EN→UA` | `UA::Production::EN→UA` | 15 | **own vector** |
| `UA PVOM` | `UA::Recognition::PVOM` | 18 | shared vector |
| `UA->EN` | `UA::Recognition::UA→EN` | 20 | shared vector |
| `UA Visual` | `UA::Recognition::Visual` | 25 | shared vector |
| `UA Grammar` | `UA::Recognition::Grammar` | 20 | shared vector |
| `UA Verbs` | `UA::Verbs` | 20 | shared vector |

The two pass-throughs sit at 9999 new/day on purpose: they are middle parents whose job
is to *not* throttle, so their children's explicit limits govern.

---

## 3. B737 presets

Seven presets. Craig, 2026-08-20: **almost all B737 notes are in review and the rest are
suspended**, so `new.perDay` here is largely inert — do not read it as an intake budget.

| Preset | Decks | new/day | learn steps | Shape |
|---|---|---|---|---|
| `B737` | 2 | 0 | `[15.0, 180.0]` | modern |
| `B737 FSRS Core` | 14 | 20 | `[10.0, 1440.0]` | older — normalize |
| `B737 FSRS Core (0n_200r)` | 3 | 0 | `[10.0, 1440.0]` | older — normalize |
| `B737 SV Exam` | 4 | 100 | `[15.0, 180.0]` | modern |
| `B737 Cats and Dogs` | 1 | 10 | `[15.0, 180.0]` | modern |
| `B737 Checklists` | 1 | 10 | `[15.0, 180.0]` | modern |
| `B737 Mnemonics` | 1 | 0 | `[15.0, 180.0]` | modern |

Every B737 preset carries its **own** `fsrsParams6` except `B737`, which shares the UA
vector — see §6. `B737 Checklists` carries the FSRS-6 stock defaults.

---

## 4. Legacy presets — NOT YET SPECIFIED

15 further presets are live under the `Legacy::` tree and are **out of scope
until Craig decides**. The tree is mixed: `Legacy::Flight Training Active` is genuinely
active (11 decks), while `Legacy::Inactive::*` is dormant. Listing them so the gap is
explicit rather than silent:

- `American Cram` — 10 deck(s)
- `American Review` — 1 deck(s)
- `Inactive` — 1 deck(s)
- `Legacy FSRS` — 1 deck(s)
- `UA - Countainer (DO NOT STUDY)` — 1 deck(s)
- `UA - Grammar - Production` — 2 deck(s)
- `UA - Production` — 1 deck(s)
- `UA - Production (Mobile) [3]` — 1 deck(s)
- `UA - Production (Typing) [1]` — 1 deck(s)
- `UA - Recognition` — 2 deck(s)
- `UA_Comparatives` — 1 deck(s)
- `UA_Grammar - Required Form` — 2 deck(s)
- `UA_Lexeme - Government` — 1 deck(s)
- `Ukrainian` — 1 deck(s)
- `Weeks 0 - 2` — 1 deck(s)

`Default` (49 decks) is Anki's built-in and cannot be deleted.

---

## 5. Changes to apply

The delta between live Anki and this spec. Nothing here has been applied yet.

**5.1 Normalize the two older B737 presets** to the modern shape (Craig, 2026-08-20).
Seven fields, on `B737 FSRS Core` and `B737 FSRS Core (0n_200r)`:

| Field | Current | Target | Effect |
|---|---|---|---|
| `new.separate` | `null` | `true` | shape only |
| `rev.fuzz` | `null` | `0.05` | shape only |
| `rev.minSpace` | `null` | `1` | shape only |
| `waitForAudio` | `true` | `false` | shape only |
| `reviewOrder` | `3` | `0` | **Ascending intervals → Due date, then random** |

**Corrected 2026-08-20.** An earlier draft of this list also normalized
`newGatherPriority 0→3` and `newSortOrder 0→4`. **Both are removed** — those values mean
*Random Notes* and *Random*, so "normalizing" would have set B737's new cards to random
order. `B737 FSRS Core` is already on Deck / Card-type-then-order-gathered; it is the nine
UA presets that carry the random settings. Do not re-add them by analogy with the other
five B737 presets.

`reviewOrder 3→0` is retained and is the one behavioural change in this list: it moves 17
B737 decks off *Ascending intervals* onto *Due date, then random*.

`new.perDay`, `new.delays` and `fsrsParams6` are **deliberately left alone** — those are
real choices, not artifacts.

**`fsrs` is deliberately NOT normalized.** It is `null` on `B737`, `B737 FSRS Core` and
`B737 FSRS Core (0n_200r)`, and `true` on the other four — a split that does not follow
the old/modern line, since `B737` is modern-shaped. Every one of them has a populated
`fsrsParams6` and a `desiredRetention`, so FSRS is evidently operating and the `null` is
more likely an absent key than a disabled flag. Setting it blind could change scheduling
on 17 decks. **Open question — confirm in Anki's own deck options before touching it.**

**5.2 Rename `B737 FSRS Core (0n_200r)`** (Craig, 2026-08-20). The name promises 200
reviews/day; the preset is set to 9999. Proposed name: **`B737 Core (review only)`** —
Claude's suggestion, not Craig's word. No scheduling change. Affects
`B737::Core::Limits::Non-Trivia`, `B737::Core::Procedures::Inflight_Maneuvers`, `B737::Core::QRC`.

**5.3 Delete 53 orphan presets** — **DONE 2026-08-20.** See §7.

**5.4 Make `create_deck_presets.py` idempotent** — see §6. Until this is done, cleanup
re-accumulates on the next run.

---

## 6. Why there are 53 orphans

Sorting orphan ids by their embedded timestamps puts them in six batches, each about one
second wide, each minting the same set of preset names:

| Batch | id prefix | presets created |
|---|---|---|
| 178456092… | 7 |  |
| 178456186… | 7 |  |
| 178456206… | 7 |  |
| 178456238… | 7 |  |
| 178456273… | 8 |  |
| 178456302… | 10 |  |

`create_deck_presets.py` **creates rather than finds-or-creates**, so every run abandons
the previous set. That accounts for roughly 45 of the 53; the rest are genuinely old
(`Cram`, `German bidirectional`, `UA_Mobile`, `B737 Systems (FSRS)`, `UA FSRS`…).

A consequence worth knowing: the nine live UA presets come from **five different batches**
— whichever run happened to be current when each deck was assigned. They are nonetheless
parameter-identical apart from `new.perDay`, which is why adopting them wholesale is safe.

**FSRS parameter contamination.** Eight UA presets and `B737` share one bit-identical
21-value `fsrsParams6` vector. A genuine optimization runs against a preset's own review
history, so identical vectors across Ukrainian vocabulary *and* a B737 preset cannot be
that — `cloneDeckConfigId` copies parameters, and batch F created `B737` alongside the UA
set. Those nine are scheduling on parameters optimized for something else, and
`B737 Checklists` is on stock defaults. **Re-optimize per preset once the target set is
settled** — separate job, not part of this cleanup.

---

## 7. Orphans — deleted 2026-08-20

**All 53 removed** via `tools/anki/setup/prune_orphan_presets.py`, taking the collection
from 85 presets to 32. Verified two ways: the preset dropdown in Anki's deck options shows
32 entries with no duplicates, and a fresh survey reports `122 decks · 32 presets ·
0 orphan(s)` with all 122 decks still holding a config. A `.colpkg` backup was taken first
and a full AnkiWeb upload followed, since deleting a config is a schema modification.

Deletion was **by id, never by name** — eight names below existed both as a live preset and
as one or more orphans, so a name-keyed delete would have hit the wrong one. The live `B737`
(`1784563030430`) and live `UA` (`1784560928203`) were confirmed absent from the delete list
before applying.

Two bugs in the pruner were caught by its own `--expect` guard rather than by luck, and are
recorded because both would have been silent:

- An earlier version skipped any config whose **name matched a deck name**, intending to
  protect filtered decks. `B737` and `UA` are real deck names *and* real preset names, so
  the rule silently protected ten genuine orphans. Filtered decks live in the `decks` table
  and never appear in `deck_config`, so the guard was unnecessary as well as wrong.
- Its post-run check re-read `collection.anki2` immediately after deleting and reported
  `remaining: 84 (was 84)`, reading as a failed delete. Anki had not flushed to disk yet.
  The check now prints an expected count and points at the GUI.

The list below is retained as the record of what was removed.

| id | name |
|---|---|
| `1771597460093` | `A: 737 Critical (Limits / Memory Items / Numbers)` |
| `1784560929326` | `B737` |
| `1784561861788` | `B737` |
| `1784562063491` | `B737` |
| `1784562383020` | `B737` |
| `1784562736301` | `B737` |
| `1775400407886` | `B737 - Limits` |
| `1775400554723` | `B737 - Limits - Trivia` |
| `1771206019264` | `B737 FSRS` |
| `1783736564210` | `B737 FSRS` |
| `1779239336593` | `B737 FSRS Flows` |
| `1774213424514` | `B737 Systems (FSRS)` |
| `1777637147023` | `B737 Systems SV (FSRS)` |
| `1568252433942` | `Cram` |
| `1770049277893` | `EN->UA` |
| `1770049131013` | `EN->UA Typing` |
| `1535334148631` | `German bidirectional` |
| `1784562240142` | `TEST_Diagnostic` |
| `1784561860715` | `UA` |
| `1784562062441` | `UA` |
| `1784562381948` | `UA` |
| `1784562735076` | `UA` |
| `1784563028856` | `UA` |
| `1783736564716` | `UA FSRS` |
| `1784560928973` | `UA Grammar` |
| `1784561861435` | `UA Grammar` |
| `1784562063138` | `UA Grammar` |
| `1784562382668` | `UA Grammar` |
| `1784563029551` | `UA Grammar` |
| `1784561861100` | `UA Lexeme EN→UA` |
| `1784562062798` | `UA Lexeme EN→UA` |
| `1784562382323` | `UA Lexeme EN→UA` |
| `1784562735431` | `UA Lexeme EN→UA` |
| `1784563029214` | `UA Lexeme EN→UA` |
| `1784560928463` | `UA PVOM` |
| `1784562062616` | `UA PVOM` |
| `1784562382155` | `UA PVOM` |
| `1784562735261` | `UA PVOM` |
| `1784563029034` | `UA PVOM` |
| `1784560929148` | `UA Verbs` |
| `1784561861613` | `UA Verbs` |
| `1784562063315` | `UA Verbs` |
| `1784562736124` | `UA Verbs` |
| `1784563029904` | `UA Verbs` |
| `1784560928798` | `UA Visual` |
| `1784562062968` | `UA Visual` |
| `1784562382503` | `UA Visual` |
| `1784562735610` | `UA Visual` |
| `1784563029383` | `UA Visual` |
| `1770049061650` | `UA->EN` |
| `1784562735950` | `UA->EN` |
| `1770049171215` | `UA->EN Mobile1770049163` |
| `1769989240642` | `UA_Mobile` |

---

## 8. Not presets

`getDeckConfig` on a **filtered deck** returns the deck itself where a config would be, so
these **11** appear in a naive survey as presets named after their deck. They are not
presets, cannot be deleted as orphans, and are why an early count said 96 rather than 85.
`survey_deck_presets.py` now reports them separately:

- `Filtered Deck 19:21`
- `Legacy::Flight Training Active::American::CQT`
- `Legacy::Flight Training Active::American::Cram Flows`
- `Legacy::Flight Training Active::American::Cram Triggers`
- `Legacy::Flight Training Active::American::Custom Study Session`
- `Legacy::Flight Training Active::American::Non-ILS Actions and Callouts`
- `Legacy::Import Airbus Limits`
- `Legacy::Inactive::Ukrainian Inactive::Verbs of Motion`
- `Legacy::Old::B737::Limits::Trivia`
- `Legacy::Old::Boldface`
- `Legacy::Old::Good-to-Know`

