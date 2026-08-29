---
title: Card Activation and FSRS Tutorial
tags: [anki, ua, tutorial, fsrs, workflow]
aliases: [Activating New Cards, FSRS Management Tutorial, Release Wave Tutorial]
updated: 2026-08-29
related: ["[[Make_UA_Commands_Reference]]", "[[DECK_PRESETS]]"]
---

# Card Activation and FSRS Tutorial

How a note goes from freshly authored `.md` file to a live, scheduled Anki
card — and how to seed old-but-forgotten material with a realistic interval
instead of re-earning it from scratch. Command-by-command detail lives in
[[Make_UA_Commands_Reference]]; this is the walkthrough that ties them
together in order.

> [!info] The big picture
> A note clears **two independent gates** before its cards are unsuspended
> in Anki, and picks up a **third, optional** marker if it's re-releasing
> material you already know:
>
> 1. **`status:`** — content quality. `draft` → `verified`, set by hand when
>    you're satisfied with the note's content.
> 2. **`release:`** — study pacing. `pending` → `active`, set in bulk by
>    `release_wave.py` per the batch sizes in `release_plan.yaml`. This is
>    what stops a fully-verified 500-note chapter from dumping into FSRS all
>    at once.
> 3. **`relearn:`** — mature-interval seeding, independent of both of the
>    above. `pending` → `seeded`, only present on notes released from a
>    `type: relearn` group. Deliberately its own tag namespace, not a third
>    `release:` value — see [[#Why relearn is a separate tag namespace]].
>
> **Both `status:verified` and `release:active` are required to unsuspend a
> note's cards.** Either one missing keeps every card on that note
> suspended — the gate fails closed. This is enforced identically across all
> five note-type import scripts (`tools/anki/sync/ua_*_import.py`).

---

## Part 1 — Activating new cards

### Step 1: Author and verify

Write the note as `status:draft`. When you're satisfied with its content —
correct lemma, good examples, right tags — flip it to `status:verified` by
hand. This is a content judgment; nothing automates it.

At this point the note is verified but **still suspended**, because it's
still `release:pending` (every note starts there — see the migration note
in [[#Gotchas and edge cases]] if you're looking at a note authored before
2026-08-29).

### Step 2: Decide what to release, and how fast

Open `domains/ua/anki/config/release_plan.yaml`. Each group is a name, a
list of tag-glob patterns (matched against every tag on a note — typically
`ch:<level>.<chapter>.<section>`), and a `batch_size`: the max number of
that group's still-`release:pending` notes promoted per run.

```yaml
groups:
  - name: "L1 vstup remainder (ch 1.1-1.12; 1.0 already released)"
    type: relearn        # optional — see Part 2
    match:
      - "ch:1.1.*"
      - "ch:1.2.*"
      # ...
    batch_size: 20
```

Raise or lower `batch_size` for the next slice you want to bring in. A
group with nothing left pending is a safe no-op — leave it or delete it,
either way.

> [!warning] `batch_size: 0` is a deliberate no-op, not a bug
> If a group shows `0 this run` in `release_wave.py`'s output, check its
> `batch_size` before assuming something's broken.

### Step 3: Preview, then apply

```bash
python tools/anki/release_wave.py --dry-run     # preview, touches nothing
python tools/anki/release_wave.py               # apply
```

This is a plain Python script, **not** a `make` target. Applying flips
`release:pending` → `release:active` on up to `batch_size` notes per group
(oldest `NoteID` first), and — for any group carrying `type: relearn` —
also inserts a `relearn:pending` tag right after `release:active`.

### Step 4: Sync — this is what actually unsuspends the cards

`release_wave.py` only edited `.md` files. Nothing changes in Anki until
you sync:

```bash
make ua-lexeme     # or: make ua, to sync all five note types
```

The sync scripts re-evaluate the suspend policy on every note they touch,
declaratively: `status:verified AND release:active` → unsuspend;
anything else → suspend. This is self-healing — a re-sync always converges
to the correct state regardless of any manual suspend/unsuspend you did
in Anki directly.

### Step 5 (only for `type: relearn` groups): seed the mature interval

If the group you promoted in Step 3 had `type: relearn`, its notes are now
unsuspended but sitting as **fresh Learning cards** — exactly what this
step avoids. See Part 2.

### Step 6: Verify

Open Anki. The notes you promoted should now be unsuspended and appearing
in study. `make ua-unverified` (runs automatically at the end of `make ua`)
will loudly flag anything still `status:draft` or with unverified stress,
as a sanity check that you promoted what you meant to.

---

## Part 2 — Mature-interval seeding for relearn notes

**The problem this solves:** a `type: relearn` group is re-releasing
material you already know (an old chapter, or content — like Вступ — that
predates this whole pacing system). Letting those cards start as fresh
Learning cards means re-earning a practical review interval on words
you've already learned, which wastes review time on material you don't
actually need drilled from zero.

**The fix:** seed each newly-active relearn note's cards with a realistic
starting interval via AnkiConnect's `setDueDate`, then let FSRS take over
scheduling from the first real review onward. This is a one-time nudge,
not a permanent interval — normal review behavior (Again/Hard/Good/Easy)
governs everything after that first review, same as any other card.

### Running it

```bash
make ua-seed-mature-dry-run    # preview — requires live AnkiConnect even for this
make ua-seed-mature            # apply
```

Both require Anki open with AnkiConnect running. Dry-run isn't a pure
file check here (unlike most `-check` targets elsewhere in this repo) — it
queries Anki for real per-note card counts so the preview is accurate,
it just skips the `setDueDate` calls and the tag write.

### What gets seeded, and by how much

| Card | Deck | Seeded interval |
|---|---|---|
| EN→UA (typing / production) | `UA::Production::EN→UA` | **14 days** (`--typing-days`) |
| UA→EN (recognition) | `UA::Recognition::UA→EN` | **21 days** (`--recognition-days`) |

Typing gets the shorter interval because production is harder and more
likely to have actually decayed than recognition. Both are overridable:

```bash
make ua-seed-mature   # or, for a one-off different interval:
python tools/anki/seed_mature_interval.py --typing-days 10 --recognition-days 18
```

> [!warning] The Compare card is never seeded
> Card 3 (homograph/confusable drilling) is deliberately excluded — its
> suspend state is already governed independently by `ConfusableSet` (see
> `ua_lexeme_import.py`), not by this feature.

### Selection logic — and why it's always safe to re-run

`seed_mature_interval.py` only touches a note if **all three** are true:

- `release:active` (already synced and unsuspended)
- `relearn:pending` (came from a `type: relearn` promotion, or a
  one-time backfill — see [[#Gotchas and edge cases]])
- **not** already `relearn:seeded`

A successful seed immediately flips the note's tag from `relearn:pending`
to `relearn:seeded` — git-tracked, in the note's own file, same pattern as
`release:pending` → `release:active`. Re-running the command is always
safe: already-seeded notes are simply skipped, and a note that hasn't been
synced to Anki yet is skipped with a warning rather than silently marked
done.

### Why `relearn:` is a separate tag namespace

Early in building this feature, the plan was a third `release:*` value
(`release:relearn`, then `release:seeded`). **Don't do that** — multiple
`release:*` tags on one note reads as ambiguous, since `release:` is
supposed to be a clean single-value gate (`pending` XOR `active`).
`relearn:pending`/`relearn:seeded` is its own independent single-value
marker answering a different question ("has this note's mature interval
been seeded yet?"), and should stay in its own namespace if it's ever
extended further.

---

## Part 3 — Managing FSRS settings

**[[DECK_PRESETS]] (`DECK_PRESETS.md` at the repo root) is the single
authority here** — generated directly from live Anki, and explicitly
supersedes every older FSRS/preset document in this repo (including
`CLAUDE-fsrs-deck-configs.md` and `CLAUDE-deck-architecture.md`, both
banned from being treated as current). This section is an orientation, not
a replacement — read `DECK_PRESETS.md` itself before changing anything.

### The four tools, and nothing else should touch presets

| Tool | Direction | Use it to... |
|---|---|---|
| `tools/anki/inspect/survey_deck_presets.py` | read | See every deck, its preset, usage, and orphans. |
| `tools/anki/inspect/export_deck_presets.py` | Anki → `presets/` | Snapshot every preset (minus FSRS weights) to one file each. Re-export + `git diff` is a drift detector. |
| `tools/anki/setup/create_deck_presets.py` | `presets/` → Anki | Idempotent apply, `--only NAME` to scope one preset. Dry-run by default. |
| `tools/anki/setup/prune_orphan_presets.py` | delete | Remove zero-deck presets, by id (never by name — some names collide between a live preset and an orphan). Dry-run by default. |

`presets/<slug>.json` is the source of truth for values — the tables in
`DECK_PRESETS.md` are a human-readable summary; where they disagree, the
JSON files win.

### Where UA sits today

Nine UA presets exist (one per deck, plus two pass-throughs). All nine
share one FSRS parameter vector with **`desiredRetention: 0.9`** — this is
the number to change if you want Anki asking for reviews more or less
often across the whole UA tree. Per-deck `new.perDay` limits differ (see
`DECK_PRESETS.md` §2); the FSRS vector itself doesn't.

> [!note] That shared vector is currently mis-optimized
> `DECK_PRESETS.md` §6 flags that eight UA presets and one B737 preset
> share a bit-identical FSRS parameter vector — evidence it was cloned
> across presets rather than optimized against each preset's own review
> history. Re-optimizing per preset is called out there as a separate,
> not-yet-done job.

### Adjusting retention

1. Check actual retention in Anki: **Deck → Study → Stats → Retention %.**
2. Compare to the configured `desiredRetention` (0.9 for UA, per above).
3. Actual retention 5%+ above target → you're over-reviewing; consider
   lowering `desiredRetention`. 5%+ below target → you're forgetting too
   much; consider raising it. Adjust in small increments (0.02–0.03), not
   all at once.
4. To actually change it: edit the relevant `presets/<slug>.json`, then
   `python tools/anki/setup/create_deck_presets.py --only "<preset name>"`.
   Don't edit FSRS settings directly in Anki's UI and expect it to stick —
   the JSON files are the source of truth going forward, and a manual Anki
   edit will look like drift on the next `export_deck_presets.py` run.

### Don't

- Don't hand-run any of the 23 tools `DECK_PRESETS.md` §0 lists as deleted
  (`setup_fsrs_deck_configs.py` and friends) — they predate the
  survey/export/create/prune workflow and reintroduce the exact
  orphan-preset bug that produced 53 stray presets, cleaned up 2026-08-20.
- Don't treat `CLAUDE-fsrs-deck-configs.md`'s specific numbers (0.93–0.95
  for B737, 0.85–0.90 for UA) as current targets — they're the original
  *reasoning*, kept for that, but live values are what `DECK_PRESETS.md`
  records (UA is 0.9 flat, not a range).

---

## Gotchas and edge cases

> [!warning] EN→UA cards may be gated behind UA→EN reaching "Easy"
> `setup_ua_note_types.py` configures the EN→UA (production) template as
> "Dependent on" UA→EN reaching Easy, in Anki's card-dependency feature. If
> that's still in effect, a seeded EN→UA card's due date is set correctly
> underneath, but the card itself may not surface in study until its
> UA→EN sibling clears that gate. Worth a live spot-check the first time
> you run `ua-seed-mature` for real.

> [!note] `verbs/exported/` is excluded from sync, on purpose
> `ua-verb`'s sync target explicitly excludes `*/exported/*` — an inert
> archival subdirectory of legacy verb stubs, not part of the active
> pipeline. Running `cnsf_canonicalize.py --write` recursively over the
> whole notes tree (rather than the specific root a `make` target scopes
> to) will reformat those files as a side effect; if that happens, `git
> checkout -- domains/ua/anki/notes/verbs/exported/` reverts it.

> [!note] Notes authored before 2026-08-29 may lack a `release:` tag
> The two-axis AND-gate (`status:` × `release:`) was backfilled across the
> whole corpus on 2026-08-29: every then-`status:verified` note got
> `release:active`, every `status:draft` note got `release:pending`. A note
> that somehow has no `release:` tag at all fails closed (stays suspended)
> under the same AND-gate logic — it isn't a special case, just the gate
> doing its job on incomplete data.

> [!note] ch:1.0 (Вступ) was backfilled directly, not via `release_wave.py`
> Вступ was already fully `release:active` before this pacing system
> existed, so it never goes through `release_wave.py`'s promotion path. Its
> 114 notes were tagged `relearn:pending` directly in a one-time backfill
> instead, since it's "book 1" material already known — they're eligible
> for `ua-seed-mature` the same as any `release_wave.py`-promoted relearn
> note.

---

## Quick reference — full sequence

```bash
git checkout main && git pull

python tools/anki/release_wave.py --dry-run     # preview
python tools/anki/release_wave.py               # apply

make ua                                          # sync everything, unsuspend

make ua-seed-mature-dry-run                      # preview seeding
make ua-seed-mature                              # apply seeding

git add -A
git commit -m "Release wave + mature-interval seeding: <what you promoted>"
git push
```

See [[Make_UA_Commands_Reference]] for every command's individual detail.
