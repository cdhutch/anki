# EN→UA Euphony + Verbal-Aspect Refactor — Design Scoping

**Status:** ~~design only. No code, no field changes, no template changes.~~ →
**Option B implemented and validated live in Anki, 2026-08-19.** Bugs (a), (b),
(c) and (d) are all closed. Option C remains undecided. §9 records what shipped,
the two bugs the rollout itself introduced, and the validation matrix.
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

> **FIXED 2026-08-18**, standalone per decision 3 below, branch
> `fix/typeans-combining-mark-nbsp`. `normalizeTypeansText()` added to both
> `EN_UA_BACK` and `setup_ua_pvom_note_type.py`'s `FEEDBACK_SCRIPT` (PVOM uses
> the identical reconstruction technique, so it had the identical bug, and every
> PVOM answer carries a stress mark). Covered by
> `tests/ua/test_typeans_normalization.py`. **Not yet on-device validated** —
> needs `make ua-setup-lexeme` + `make ua-setup-pvom`, then a deliberate
> wrong-stress-position answer on ua-lexeme-0532.

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

**DECIDED 2026-08-20 by Craig: this stays authoring guidance. It will not be
built, and it will not become a checker.**

The convention, as scoped 2026-07-29: on a verb-phrase note, `Lemma` carries the
**imperfective** unless the phrase clearly calls for the perfective, and
`Perfective` is filled only where the pair genuinely exists for the phrase as a
whole rather than for the bare verb.

Why it is not enforced in code: enforcement would require detecting aspect
programmatically from the form, which is a harder and less reliable problem than
the one it would be guarding. The reasoning above — that this governs authoring
input rather than grading — is what makes a convention the right instrument.

**Known non-conformance, recorded rather than resolved.** The `make ua-check`
aspect audit lists verb-phrase singlets in both aspects: `ua-lexeme-0299`
(ви́лізти на ске́лю), `0300` (перелеті́ти через рі́чку…) and `0301` (переплисти́
о́зеро) are perfective, while `0302` (підніма́тися на ске́лі) and `0303`
(спуска́тися вниз) are imperfective. Whether the perfective ones violate the
convention or are legitimately perfective phrases is a content question for
Craig, not a mechanical one. They sit on the audit's existing singlet-review
list; this decision does not clear them.

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

**All answered by Craig, 2026-08-18.** Recorded inline below; the questions are
kept rather than replaced so the reasoning that produced each answer stays
readable.

> 1. **Option B.** Build the structured `_TypingSpec`.
> 2. **Yes — a fully-stressed euphonic alternate earns PERFECT.** `ввійти́` is
>    not a lesser answer than `уві́йти`, just a different attested one. This is
>    what forces the data-shape change: the current comparison stress-strips
>    both sides and structurally cannot distinguish a stressed alternate from an
>    unstressed one, so Option A was never actually sufficient.
> 3. **Bug (b) lands standalone, first.** Done — see the status note under §4(b).
> 4. Option C (per-slot cards) — not yet decided; still to be scoped separately.
> 5. The (d) audit — not yet run.

**Consequence of (1)+(2) worth noting before implementation:** the stress-mark
fix and the euphony rewrite touch the same reconstruct-then-compare block in
`EN_UA_BACK`. (b) was deliberately landed as its own `normalizeTypeansText()`
helper rather than inline, so the Option B rewrite can replace the grading logic
around it without swallowing or re-breaking it.

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

---

## 9. What actually shipped (2026-08-19)

Added after implementation. §1–§8 are left as written on 2026-08-18 so the
design reasoning stays readable against what it turned into.

### 9.1 The change

`_EuphonySlots` (a second `" / "`-joined string, index-aligned with
`TypingTarget_UA` by convention only) is gone. `_TypingSpec` replaces it:
compact JSON, one object per populated aspect slot, primary and alternates
travelling together.

```json
{"slots":[{"primary":"вхо́дити","alts":["ухо́дити"]},
          {"primary":"ввійти́","alts":["увійти́"]}]}
```

Alternates are stored **stressed**. That single change is what closes (a): the
old mechanism stripped stress from both sides before comparing, so it could not
distinguish "euphonic alternate, perfectly stressed" from "euphonic alternate,
no stress" — both landed in CORRECT and PERFECT was structurally unreachable.

Built by `compute_typing_spec()` in `ua_lexeme_import.py`; consumed by the
grading block in `EN_UA_BACK`. `FIELDS` is unchanged in length (38): a single
in-place swap at index 31. **The CNSF corpus needed no change** — both fields
are computed at import time, and `_EuphonySlots` was populated on 0 of 585
notes.

12 of 585 notes carry euphony data: `0115 0124 0153 0211 0281 0353 0377 0379
0484 0488 0581 0584`. The other 573 get a blank spec and fall through to plain
primary/no-stress comparison.

### 9.2 Bugs (b), (c), (d)

- **(b)** landed standalone first, as planned, on `fix/typeans-combining-mark-nbsp`.
  See 9.3 — it did not survive this refactor unaided.
- **(c)** closed: `splitSlots()` splits on `/\s*\/\s*/`, so `ходити/йти/піти`
  grades the same as `ходити / йти / піти`.
- **(d)** audited and closed. Exactly **one** note corpus-wide reached the
  legacy whole-note `EuphonyNote` fallback: `ua-lexeme-0353`. Its `EuphonyNote`
  held explanatory prose, not a bare alternate, so the fallback was comparing a
  whole sentence as a spelling — matching nothing and warning about nothing.
  Dead tolerance that looked live. 0353 was given a real `Lemma_Euphony`
  (`уве́чері`, lifted verbatim from its own prose) and the fallback was deleted;
  it had zero remaining users.

### 9.3 Two bugs the rollout itself introduced

Both are worth recording because both were **silent**, and because the tests
that should have caught them were the ones that failed.

**A merged fix was reverted by rewriting around it.** §7 notes that (b) was
deliberately landed as its own `normalizeTypeansText()` helper *so that the
Option B rewrite could replace the grading logic without swallowing it*. The
rewrite swallowed it anyway — the helper and its call site both vanished, and
the ua-lexeme-0532 combining-mark bug came back. Nothing in the Python-level
tests noticed. `test_typeans_normalization.py` caught it, because it asserts on
the **emitted JavaScript** rather than on any Python function's return value.
The helper is now restored byte-identical to the surviving copy in
`setup_ua_pvom_note_type.py`, and `test_both_scripts_emit_identical_helper_bodies`
enforces that they stay in sync.

**The spec was shipped in an HTML attribute, which silently truncated it.**
First version used `data-typing-spec="…"` on the `#feedback` div. Anki does
**not** HTML-escape field content — it splices the raw text in — so the JSON's
own double quotes closed the attribute at the first one. The browser saw
`data-typing-spec="{"`, `JSON.parse` threw, and the defensive `catch` degraded
to "no alternates". Every euphonic answer graded INCORRECT.

What made this hard to read: the *correct-answer* lines still rendered
perfectly, because `data-with-stress` and `data-no-stress` sit in **earlier**
attributes that parsed fine. It presented as a grading-logic bug. The tell was
that `ua-lexeme-0219` — one of the 573 notes with a blank spec — graded both
tiers correctly.

The JSON now lives in `<script type="application/json" id="typing-spec">`, read
via `textContent`. No attribute quoting to get wrong.

The original test for this asserted the attribute was **present**, reasoning
that `{{text:}}` avoided HTML-escaping. Exactly backwards, and it passed
happily while the feature was dead. Its replacement,
`test_spec_survives_being_rendered_into_the_template`, renders the real
`EN_UA_BACK` the way Anki does, parses it with an HTML parser, and asserts the
JSON comes back byte-identical and re-parses. No Python-level test of
`compute_typing_spec()` could have caught this: the spec was correct, the
template was wrong.

**Related, found the same day:** a `{{type:...}}` example written inside a
template *comment* broke `updateModelTemplates` outright (`Field '...' not
found`). Anki parses replacements inside comments — JS `//` and HTML `<!-- -->`
alike. An identical brace-wrapped example had been sitting dormant in
`UA_EN_FRONT` since 2026-08-04. `tests/ua/test_template_field_refs.py` now
checks every replacement in all 13 templates across both setup scripts.

### 9.4 Validation (live in Anki, 2026-08-19)

All cases confirmed by Craig against the real cards, matching a node harness run
against the real emitted template.

| Note | Typed | Tier |
|---|---|---|
| 0115 | `вхо́дити / ввійти́` | PERFECT |
| 0115 | `ухо́дити / увійти́` | PERFECT ← the case Option B exists for |
| 0115 | `ухо́дити / ввійти́` | PERFECT (mixed alt + primary) |
| 0115 | `вхо́дити/ввійти́` | PERFECT (bug (c)) |
| 0115 | `уходити / увійти` | CORRECT |
| 0115 | `вхо́дити / зайти́` | INCORRECT |
| 0379 | `встано́влювати / встанови́ти` | PERFECT |
| 0379 | `устано́влювати / установи́ти` | PERFECT |
| 0581 | `ходи́ти / іти́ / піти́` | PERFECT ← alternate on the MIDDLE slot |
| 0581 | `ходи́ти / йти / піти́` | PERFECT |
| 0581 | `ходити / іти / піти` | CORRECT |
| 0219 | `перекида́ти / переки́нути` | PERFECT (blank spec, control) |
| 0219 | `перекидати / перекинути` | CORRECT |
| 0532 | `розве́дення ове́ць` | PERFECT (bug (b) regression check) |

`0581` matters disproportionately: it is the only note whose alternate sits on
`ImperfectiveUnidirectional`, so it is the sole test that slot indexing is
genuinely positional rather than accidentally working because every other
alternate happened to sit on slot 0 or slot 2.

### 9.5 Open, deferred

- **Option C** (per-slot cards) — **deferred 2026-08-20 by Craig, blocked behind
  the deck-preset cleanup.** Option C is an FSRS-scheduling change to the UA
  tree, and that tree's preset architecture is unresolved as of 2026-08-20:
  `UA FSRS` sits on 0 decks, `B737 FSRS Core` on 14 under a name no document
  mentions, and `CLAUDE-fsrs-deck-configs.md` and `DECK_PRESET_MAPPING.md`
  specify incompatible designs for the same decks. Deciding per-slot cards
  before knowing which preset those cards live under stacks two unknowns on the
  same notes.

  **Correction to this document's own cost estimate, in Option C's favour.** §5
  says "FSRS history implications for 585 notes." The 2026-08-20 aspect audit
  gives the real shape: **61 doublets + 5 triplets = 66 multi-slot notes.** The
  other 519 lexemes and 21 single-slot verbs generate one EN→UA card either way,
  so the change adds roughly **71 new cards across 66 notes** — provided the
  existing EN→UA template keeps its ordinal, so current cards survive as slot 1.
  That ordinal-preservation assumption is Claude's reasoning about Anki's card
  generation and **must be verified against Anki before acting on it**. The
  precedent argument from §5 is unchanged and still favours doing this
  eventually.
- **Port `_TypingSpec` to `UA_PVOM_Infinitive`.** That note type still uses the
  older single-slot `EuphonyNote`/`data-euphony` mechanism, and its
  `normalizeTypeansText()` is a hand-maintained copy rather than a shared
  source. Craig scoped UA_Lexeme first, PVOM as a follow-up.
- **62 notes where CNSF `TypingAnswer` disagrees with the stress-stripped slot
  join** (e.g. `ua-lexeme-0114` holds `приходити`, should be
  `приходити / прийти`; `0488` holds the Perfective instead of the Lemma). Not
  a live bug — `import_note()` overwrites `TypingAnswer` from
  `compute_typing_target()[1]` for every doublet/triplet, so Anki has always had
  the right value. The drift is confined to the CNSF files, which is awkward
  only because CNSF is meant to be the source of truth. Candidate for a
  `cnsf_canonicalize.py` pass, which already computes the same join.
- **`ua-lexeme-0153` / `0379` example sentences.** Both notes had their headword
  direction flipped to в- on 2026-08-19. Their `UA_Example` sentences still use
  the у- form, deliberately left alone: в/у alternation is phonetically
  conditioned, and in `0379` ("Технік установлює…") the у- form is arguably the
  *correct* choice after a consonant. Needs Craig's call, not a mechanical edit.
- **`Source_URL` on `0153` / `0379`** still points at the у- spellings while the
  house pattern points it at the `Lemma`. Left unchanged rather than assert a
  URL that has not been opened.
