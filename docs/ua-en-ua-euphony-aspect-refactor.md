# EN→UA Euphony + Verbal-Aspect Refactor — Design Scoping

**Status:** design only. No code, no field changes, no template changes.
**Written:** 2026-08-18, by Claude, at Craig's request (CLAUDE-work-queue.md,
"EN→UA euphony + verbal-aspect refactor").
**Decisions needed from Craig** are collected in §7. Nothing in §4–§6 should be
built before those are answered.

---

## 1. Why this document exists

Craig flagged on 2026-08-11 that he recalls abandoning a prior effort in this
area, and wants the whole approach to how euphony and verbal aspect are jointly
managed on the EN→UA production side reconsidered from scratch — not another
incremental patch on top of the existing mechanism.

That instinct is well-founded. This area has now been designed three times:

| Date | Design | Outcome |
|---|---|---|
| 2026-07-25 (`a5b4a15`) | Aspect join + euphony as a third correct tier (tolerance) | "It worked great" per Craig |
| 2026-07-25 (`881ac25`/`2e93202`) | Euphony as *required dual-form production* — type primary **and** euphonic together | Abandoned 2026-07-28 |
| — | Whole feature silently reverted to bare `{{type:Lemma}}` via a merge-conflict resolution | Recovered 2026-07-28 by git archaeology |
| 2026-08-04 | Per-slot euphony tolerance (`*_Euphony` fields, `_EuphonySlots`) | Built; shipped inert until 2026-08-11; **now live and buggy** |

Two abandonments and one accidental revert in three weeks is a signal about the
design, not about the execution. §3 argues the recurring problem is a
*representational* one that each redesign inherited without naming.

---

## 2. What is actually live today

**Data flow.** `ua_lexeme_import.py` computes four fields at sync time from
five hand-authored ones. None are CNSF-authored:

| Computed field | Built from | Consumed by |
|---|---|---|
| `TypingTarget_UA` | `Lemma` / `ImperfectiveUnidirectional` / `Perfective`, `" / "`-joined, populated slots only | `EN_UA_FRONT`'s `{{type:...}}` |
| `TypingAnswer` | same, stress-stripped | `EN_UA_BACK` feedback |
| `_EuphonySlots` | the three `*_Euphony` fields, positionally aligned to the above | `EN_UA_BACK` feedback |
| `_UA_EN_DisplayLemma` | slots with their alternates inline in parens | `UA_EN_FRONT` display |

**Grading.** `EN_UA_BACK`'s script reconstructs what was typed from Anki's
`#typeans` diff, then grades in this order: exact match on `TypingTarget_UA` →
PERFECT; exact match on `TypingAnswer` → CORRECT; otherwise split on `" / "`
and grade slot by slot.

**Coverage.** The per-slot euphony feature it was built for is exercised by
**8 notes out of 585** — `Lemma_Euphony` 6, `Perfective_Euphony` 5,
`ImperfectiveUnidirectional_Euphony` 2 (overlapping). Worth holding in mind
when weighing migration cost against benefit: almost any change here is cheap
on the content side.

---

## 3. The representational problem

`TypingTarget_UA` is a **flat string that three different consumers reparse by
splitting on a delimiter**, and it silently conflates two orthogonal questions:

1. *Which aspect forms must the learner produce?* (aspect)
2. *Which surface spellings count as correct for each form?* (euphony)

Every bug in §4 is downstream of that. The Python side knows the slot structure
perfectly — it just built it — and then throws that structure away by
flattening to a string, forcing the JavaScript to reconstruct it positionally
from two independently-joined strings that must stay index-aligned by
convention alone. Nothing enforces that alignment; nothing detects when it
breaks.

This is also why each redesign has been expensive: changing the grading rules
means changing the *string format*, which means changing every producer and
consumer at once.

---

## 4. Confirmed bugs

All four were found by reading the code and Anki's source, and all are real
today. **(a)** and **(d)** are the two Craig has hit in practice.

### (a) Euphonic alternates can never reach PERFECT — even fully stressed

`EN_UA_BACK`, per-slot loop:

```js
if (typedSlot === stressSlot) { continue; }   // this slot: perfect
everySlotPerfect = false;                     // ← fires BEFORE the euphony check
if (typedSlot === noStressSlot) { continue; }
if (euphonyAltsForSlot(i).indexOf(stripStress(typedSlot)) !== -1) { ... }
```

`everySlotPerfect` is cleared the moment a slot doesn't equal the *primary*
stressed form, before the euphonic branch runs. Craig confirmed this live on
`ua-lexeme-0115`: `вхо́дити / ввійти́` — both forms fully and correctly stressed,
the second being the dictionary-attested `Perfective_Euphony` — grades CORRECT,
never PERFECT.

There is a **second, independent** defect in the same three lines:
`euphonyAltsForSlot()` stress-strips the stored alternates, and the comparison
stress-strips the typed slot too. So even after fixing the ordering, the code
*cannot distinguish* "euphonic alternate, perfectly stressed" from "euphonic
alternate, no stress at all." Both collapse to the same bucket. Fixing (a)
properly means storing and comparing stressed alternates as well as stripped
ones — i.e. a data-shape change, not a line reorder. This is the single
strongest argument for §5's structured representation.

### (b) The detached stress mark — root cause found, no DevTools needed

The work queue's top bug (`ua-lexeme-0532`, `розве́дення ове́ць` misjudged
INCORRECT with the accent rendering detached and one position late) is Anki's
output, not the reconstruction loop. From Anki's `rslib/src/typeanswer.rs`:

```rust
/// Prefixes a leading mark character with a non-breaking space to prevent it
/// from joining the previous token.
fn isolate_leading_mark(text: &str) -> Cow<'_, str> {
    if text.chars().next().is_some_and(|c| GeneralCategory::of(c).is_mark()) {
        Cow::Owned(format!("\u{a0}{text}"))
    } else {
        Cow::Borrowed(text)
    }
}
```

When Anki's character-level diff splits a chunk such that the chunk *begins*
with U+0301, Anki prepends U+00A0. That nbsp sits inside a `.typeGood` /
`.typeBad` span, so `chunks.map(el => el.textContent).join('')` swallows it into
`typedAnswer` — which then matches nothing, and renders with a visible gap
before the accent. Exactly the reported symptom, and it explains why a
*stress-position* mismatch triggers it while other mismatches don't: only a
position shift causes the diff to split mid-grapheme.

The queue lists this as needing on-device DevTools diagnosis. It doesn't.
Normalising U+00A0 out of the reconstruction closes it. Note the two cases
differ — an nbsp *followed by a combining mark* is Anki's isolation artifact and
should be dropped outright; any other nbsp should become an ordinary space
(today's Anki preserves real spaces via `white-space: pre-wrap` rather than
entity-encoding them, but that's an implementation detail worth not depending
on). This bug is **independent of aspect and euphony** and could be fixed on its
own at any time.

### (c) Separator spacing is load-bearing

`typedSlots.length === stressSlots.length` gates the entire per-slot path, and
the split is on the literal `" / "`. A learner who types `ходити/йти/піти` —
same letters, no spaces around the slashes — fails the length check and is
graded INCORRECT outright. Normalising whitespace around separators before
splitting would fix it. Unconfirmed on-device, but it follows from the code.

### (d) Prose `EuphonyNote` produces silent dead tolerance

`compute_euphony_slots()` falls back to the raw whole-note `EuphonyNote` for
singlets with no per-slot field. `EuphonyNote` is documented as free text —
"bare alternate spelling(s) **or explanatory prose**." When it holds prose, the
JS splits it on `|`, strips stress, and compares the whole paragraph as a
candidate spelling. It never matches, so the note has *no* euphony tolerance
while appearing to have some. Nothing warns. Worth an audit of how many singlets
carry prose vs. bare alternates.

---

## 5. Options

### Option A — Fix the bugs, keep the design

Patch (a)–(d) in place. Cheapest, and (b)/(c) are worth doing under any option.
But (a) can't be fully fixed without carrying stressed *and* stripped forms of
each alternate, which means changing `_EuphonySlots`' format anyway — at which
point most of Option B's cost is already paid, without its benefits.

### Option B — Structured typing spec (recommended)

Replace the two positionally-aligned strings with **one computed JSON field**,
say `_TypingSpec`, that carries the structure Python already has:

```json
{"slots": [
  {"primary": "вхо́дити", "alts": []},
  {"primary": "уві́йти",  "alts": ["ввійти́"]}
]}
```

The grading script parses it once and compares against real objects. This:

- removes positional alignment as a correctness requirement — the alignment bug
  class disappears rather than being avoided by convention;
- lets each candidate be compared **both** stressed and stripped, so (a)'s
  second defect is fixed by construction and a stressed euphonic alternate can
  legitimately earn PERFECT;
- makes future grading changes a JS-only edit, since the data shape stops
  encoding the grading rules;
- keeps `TypingTarget_UA` / `TypingAnswer` exactly as they are for
  `{{type:...}}` and the reference display — no change to the front card.

Cost: one new computed field, one rewrite of the feedback script's grading
block, new unit tests. **No CNSF authoring changes** — the three `*_Euphony`
fields stay exactly as authored; only the derived representation changes. Given
only 8 notes carry euphony data, content risk is near zero.

`_EuphonySlots` would be retired once `_TypingSpec` lands.

### Option C — Split EN→UA into one card per aspect slot

The deeper question Craig's "reconsider from scratch" invites. Today one EN→UA
card demands the entire triplet in one answer, so a learner solid on
`ходи́ти`/`піти́` but shaky on `йти` fails the whole card and re-drills all three.

The repo already rejected this pattern once, deliberately, for
`UA_PVOM_Infinitive` — 11 notes × 4 templates rather than one card with four
blanks, on the stated grounds that "the four forms are not equally hard" and
separate templates let each be suspended and leech-tracked independently.
**That reasoning applies verbatim to aspect slots.**

This is a much larger change (new templates, FSRS history implications for 585
notes, deck-limit rebalancing) and should be decided on its own merits, not
folded into a grading-logic fix. Flagged, not recommended for now.

### Verb-phrase aspect defaulting (2026-07-29 item 2)

Still uncoded, still authoring-guidance-only. It is genuinely independent of
(a)–(d) and of Options A–C — it governs *what goes in* `Lemma`/`Perfective` on
phrase notes, not how the result is graded. Recommend keeping it separate and
deciding it on its own; folding it in is what made the 2026-07-29 plan feel
like one project when it was always two.

---

## 6. Recommended sequence

1. **Fix (b) alone, now.** Independent of everything else, closes the top
   work-queue bug, small and self-contained.
2. **Decide Option B.** If yes: build `_TypingSpec`, rewrite the grading block,
   retire `_EuphonySlots`, unit-test the tier matrix (primary/euphonic ×
   stressed/unstressed × per-slot).
3. **Fix (c) and audit (d)** as part of step 2's rewrite.
4. **Decide Option C separately**, on its own timeline.

Steps 1–3 leave the CNSF corpus untouched and are reversible by re-running
`make ua-setup-lexeme` from an earlier commit.

---

## 7. Decisions needed from Craig

1. **Option B — build it, or just patch in place (Option A)?** Recommendation is
   B; A cannot fully fix (a) without paying most of B's cost anyway.
2. **Should a fully-stressed euphonic alternate earn PERFECT?** This design
   assumes yes — that `ввійти́` is not a lesser answer than `уві́йти`, just a
   different attested one. If euphonic forms should instead be *acceptable but
   never top-tier*, say so; it changes the tier matrix, and it was arguably the
   unstated premise behind the abandoned 2026-07-25 redesign.
3. **Fix (b) now as a standalone commit, or hold it for the refactor?**
4. **Option C — worth scoping separately, or is the compound card right?**
5. **Audit (d)?** Needs a pass over singlet notes with a populated `EuphonyNote`
   to see how many hold prose rather than bare alternates.

---

## 8. Reading list before implementing

- `CLAUDE.md` → "EN→UA aspect+euphony typing" (the `a5b4a15` reference design,
  with Craig's explicit "do not re-add the complexity without sign-off")
- `CLAUDE.md` → "Per-slot euphony tolerance + verb-phrase aspect defaulting"
- `CLAUDE.md` → "Typing-card design pattern for Ukrainian text" (why the
  `#typeans` reconstruction exists at all — directly relevant to (b))
- `tools/anki/setup/setup_ua_pvom_note_type.py` → `FEEDBACK_SCRIPT`, the
  single-slot version of this same mechanism, and the precedent for Option C
- `git show a5b4a15:tools/anki/setup/setup_ua_note_types.py`
