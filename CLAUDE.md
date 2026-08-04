# CLAUDE.md — Anki Project Context (B737 + Ukrainian)

**Current work**: UA domain -- Ch-09 motion-verb polish punch list (7/7 items) complete as of
2026-07-22; push + PR to main pending Craig's go-ahead. Vocab dedup/homograph audit tooling
built and a full-corpus audit run on `feature/ua-vocab-dedup-homograph` as of 2026-07-24 (see
[CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md)) -- generator-script wiring
(item 0 below) still open. B737 Phase A distractor authoring paused (26/29 systems verified).
2026-07-27: Fixed `audit_legacy_lexeme.py` to filter for chapter 2.9.x notes only (was comparing
against all 569 canonical notes, now correctly compares against 259 ch-09 notes); audit now
shows 59 safe-to-delete legacy vocabulary matches. Created дорогий polysemy split following the
same-lemma pattern (0437 expensive sense + new 0580 dear/affectionate sense, cross-referenced
in Verification_Notes). Tagged ch-08 lexeme notes 0436 (важкий) and 0440 (добрий) with
`needs-confusable-set` marker for future Compare card/confusable-set handling (convergent
synonyms bucket). Batch of ch-08 lexeme note updates staged.
2026-07-28 (evening session): four fixes/additions to `UA_Lexeme`, none yet applied to live
Anki or committed -- Craig has the exact `python`/`make` commands and commit messages from
the session, pending review. (1) `UA_EN_FRONT` now shows `UA_Example` for context (was
back-only); deduped the now-redundant line from `UA_EN_BACK`. (2) Found and fixed a real data-
integrity bug in `ua_lexeme_import.py`: `compute_compare_options()` was unconditionally
overwriting hand-authored `CompareA`/`CompareB` with `(Lemma, raw ConfusableSet text)` on
every re-import -- found via ua-lexeme-0022 (алфавіт/абетка), whose Compare-card front was
showing a full explanatory paragraph instead of a short chip. Now only fires as a fallback
when `CompareA`/`CompareB` aren't already authored -- see "Comparison card" under Card
Template Techniques below. This likely affected every confusable cluster re-imported since
the 2026-07-24 CompareA-D redesign, not just 0022/0023 -- worth a broader re-sync + spot-check.
(3) Compare card now suspends (importer-side) and shows a "should be suspended" notice
(template-side, defensive) when `CompareA`/B/C/D are all blank despite `ConfusableSet` being
populated -- e.g. a `homograph:true` note where Compare fields were never authored. (4) Built
a new bucket-4 convergent-synonym Compare-card cluster: відбивати/забивати/завдавати/набирати
(ua-lexeme-0213/0214/0215/0218) -- see Vocabulary dedup & homograph handling below.
Separately: rolled back `EN_UA_FRONT`/`EN_UA_BACK` to the aspect+euphony design from commit
`a5b4a15` (git archaeology across `main`, since this branch's copy had been reverted past that
point back to a bare `{{Lemma}}`-only typing target with no aspect or euphony handling at
all) -- see "EN→UA aspect+euphony typing" under Card Template Techniques below for the design
and why the 2026-07-25 `881ac25`/`2e93202` redesign (require typing both primary and euphonic
forms together) was abandoned in favor of it.
2026-07-29: Scoped (not yet implemented) a two-part extension to the EN→UA
aspect+euphony typing design: (1) evaluate every populated UA_Lexeme aspect slot
(Lemma/ImperfectiveUnidirectional/Perfective) independently for в-/у- euphony
tolerance, rather than only at the single-lemma level; (2) for verb-phrase notes
where only one aspect fits the idiomatic meaning, default to imperfective and rely
on clearly-worded EN_Gloss rather than a new schema field. See "Per-slot euphony
tolerance + verb-phrase aspect defaulting (planned 2026-07-29)" under Card
Template Techniques for the full design. Execution deferred pending go-ahead.
2026-07-30: **Current task is Ch-08 lexeme verification** — Craig reviewing UA_Lexeme
notes under `domains/ua/anki/notes/lexemes/yabluko-l2/ch-08/` (ua-lexeme-044x–049x
range) against Горох and against each other. Craig has passed over a first punch
list of confusable-set candidates (0447+0465, 0453+зазвичай-cluster, 0463+затор,
0467 joining the existing значно/набагато pair, 0471+вигляд/доглянати,
0477+скільки/декілька), one aspect-pairing gap (0482 дотримуватися missing
Perfective дотриматися), one correction (0484 should be впадати, imperfective,
with впасти as its perfective partner — currently filed as впасти itself), and one
open usage question (0474 раз — counting usage vs. один). None of this is written
into ConfusableSet/CompareA-D fields, Perfective fields, or tooling yet — Claude
flagged some open questions while scoping (see conversation log) and is waiting on
Craig's confirmation before anything gets written to the appropriate docs/notes.
Craig then gave feedback and Claude executed on it same session: (1) built a
`pending-confusable:<lemma>` tag + `tools/anki/inspect/check_pending_confusables.py`
watchlist mechanism (see Vocabulary dedup & homograph handling, bucket 5) and tagged
every currently-not-yet-sourced confusable partner named so far (зазвичай, затор,
забагато, вигляд, доглянати, скільки, декілька, погода/природа/порода off
ua-lexeme-0272 пригода, подорож off ua-lexeme-0330 мандрівка); ua-lexeme-0321
(перепрошувати) tagged with the existing generic `needs-confusable-set` marker
instead, since Craig named an open-ended -прошувати/-просити prefix family rather
than one exact spelling. (2) Extended `audit_verb_aspect_forms.py` to recognize
hand-authored `aspect:imperfective-only`/`aspect:perfective-only` tags — flags only
fire when a verb has ZERO aspectual counterparts populated (a true singlet) and
neither tag is present; doublets/triplets were never flagged and still aren't.
Per Craig, Claude never applies either tag itself — only reads them; Craig alone
decides and hand-tags after checking Горох. Wired both scripts into a new
`make ua-check` target (report-only, STRICT=1 to fail). (3) Re-keyed ua-lexeme-0484
from Lemma=впасти/Perfective=blank to Lemma=впада́ти/Perfective=впа́сти per Craig's
correction — Горох-verified the впадати stress and confirmed via Горох's own
Тлумачення that впадати/впасти (not падати/впасти) is the pair actually used in the
"впасти в очі" idiom (ua-lexeme-0488 already suspected this); updated 0488's and
ua-verb-0079's cross-references to match. Still open on 0484: UA_Example/EN_Example
still show the perfective "впало" (apple falling) rather than an example
demonstrating впадати's own aspect — flagged in Verification Notes, needs Craig's
call, not silently rewritten. Also answered Craig's раз-counting and
мандрівка-vs-подорож questions inline (see conversation log for the full reasoning
and Горох citations).
2026-07-30 (continued): **Compare-card fixes closeout.** Synced the four 2026-07-28
`UA_Lexeme`/`ua_lexeme_import.py` fixes described above. While verifying, found
ua-lexeme-0405/0407 (те́пло adverb "warmly" / тепло́ noun "warmth" — a stress-shift
homograph pair) had never generated a Compare card at all: it only ever had the
lightweight bucket-2 cross-link (bare alternate spelling in `ConfusableSet`, no
Compare fields), and Anki does not create a card whose front template renders
completely empty — this predates the "should be suspended" defensive fallback, so
the gap was silent rather than visibly suspended. Drafted and synced the missing
Shape-1 Compare content (`CompareScenario`/`CompareA`/`Homograph_SenseA`/`CompareB`/
`Homograph_SenseB`) on both notes, mirroring the established мете́лик
(ua-lexeme-0171/0181) pattern. Then ran a full corpus-wide sweep (579 notes, 59 with
`ConfusableSet` populated) confirming тепло was the *only* Compare-content gap in the
entire lexeme corpus — see
[CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md) for the sweep
methodology and results. Also clarified for the record: the `compute_compare_options()`
clobbering bug (found/fixed 2026-07-28) only ever corrupted live Anki data via
`updateNoteFields` — it never touched the CNSF files themselves — so no separate
file-level remediation was needed beyond the normal re-sync.
2026-07-31: **UA→EN front aspect display.** Added `_AspectLabel` (new computed field)
and wired `TypingTarget_UA` (already computed for the EN→UA typing target) into
`UA_EN_FRONT`'s lemma line, so the Recognition card front now shows the full
slash-joined aspect set (e.g. `ходи́ти / йти / піти́`) in one consistent font, with a
small `(pf.)`/`(impf.)` tag next to true singlets where the aspect wouldn't otherwise
be visible. Per Craig 2026-07-31 — see "UA→EN front aspect display" under Card
Template Techniques below for the full design and code. Implemented in
`tools/anki/setup/setup_ua_note_types.py` and `tools/anki/sync/ua_lexeme_import.py`;
synced.
2026-07-31: **Solarized correction.** Craig confirmed live `UA_Lexeme` currently shows
*neither* competing CSS source (see "Pending / Next planned work" item 3 below, rewritten)
— Solarized styling for `UA_Lexeme`'s three card templates (UA→EN, EN→UA, Compare) is
still genuinely future work, not already-partially-done as this doc previously implied.
2026-07-31: **Base motion-verb triplet lexemes drafted.** Per Craig's request, drafted
5 new `ua-lexeme` notes (0581–0585) for the base (unprefixed) motion-verb triplets —
ходити/їздити/літати/плавати/бігати, each spanning multidirectional-imperfective /
unidirectional-imperfective / perfective in one note (`Lemma`/`ImperfectiveUnidirectional`/
`Perfective`). These are the *first* lexeme notes in the corpus to populate
`ImperfectiveUnidirectional` — everything else sourced so far has been a doublet or
singlet — so they're the real-data example the new front-aspect-display feature above
needed. Горох-verified stress throughout; `status:draft` pending Craig's review. Also
added `ua-verb-0086`/`0087` (плисти/поплисти) — while sourcing the плавати triplet,
Craig caught that Горох's плисти́/поплисти́ are valid free-variant headwords of
пливти́/попливти́ (same relationship as йти/іти), and that the swimming group was the
only one of the five missing this variant-pair note (walking already has both
йти/ua-verb-0003 and іти/ua-verb-0002). While sourcing плисти/поплисти, also found —
but per Craig, held for a separate pass, not fixed here — that the *existing*
ua-verb-0009 (пливти) and ua-verb-0010 (попливти) have stored conjugation tables that
don't match their own Lemma (they look like a mixed-up плинути/попити paradigm
instead); see "Remaining Work" below and each note's `Verification Notes` for detail.
2026-08-01: **Gruvbox palette rollout — structural items 1–3 resolved (see "Remaining
Work" below).** Found `feature/anki-mobile-night-mode` already existed with real prior
work (a `.night_mode`→`.nightMode` fix commit, plus a `Solarized_Palette_Demo` proof-of-
concept Craig had built 2026-07-27, commit `aa52393`) — merged both into the working
branch. Resolved item 1 (dual CSS sources): `setup_ua_note_types.py` is now the single
source of truth for all four live UA note types (`UA_Lexeme`/`UA_Grammar`/`UA_Verb`/
`UA_Visual`); `update_legacy_css.py` trimmed to its B737-legacy entries only, per Craig's
decision. Resolved item 2: `.night_mode`→`.nightMode` fixed throughout `VISUAL_CSS`.
Item 3 ("Solarized palette") superseded — mid-task, Craig's actual objective turned out
to be broader: a repo-wide default palette, chosen empirically against his real
accessibility need (iOS Accessibility → Display & Text Size → Color Filters → Color Tint
→ Hue near-full-left, a red-tint "night vision" filter he uses ~10% of the time, vs. ~60%
day / ~30% ordinary night mode). Built `tools/anki/setup/setup_palette_comparison_demo.py`
(`Palette_Comparison_Demo` note type, `Demo::Palette_Comparison` deck, under
`domains/demo/` — see `domains/demo/README.md`) to A/B/C-test three candidates (Solarized
/ Monochrome / Warm-Gruvbox-style) as composite card mockups that live-flip via
`.nightMode`, tested in a three-pass walkthrough (Day mode → Night Mode → Night Mode +
red-tint filter). Craig's verdict: **Gruvbox**, with Accent B corrected from olive green
to blue (`#076678`/`#83a598`) after on-device testing showed green sat too close in hue
to the secondary-text gray. Gruvbox is now rolled out as the actual palette across
`CSS`/`GRAMMAR_CSS`/`VERB_CSS`/`VISUAL_CSS` in `setup_ua_note_types.py` (bg `#fbf1c7`/
`#282828`, primary `#3c3836`/`#ebdbb2`, secondary `#7c6f64`/`#a89984`, Accent A orange
`#af3a03`/`#fe8019`, Accent B blue as above). Scope also expanded per Craig to cover the
Compare card and both typing-feedback scripts (`EN_UA_BACK` in `setup_ua_note_types.py`;
`FEEDBACK_SCRIPT` in `setup_ua_pvom_note_type.py`, previously **completely unthemed, zero
`.nightMode` support**) — their hardcoded inline `style="color:#hex"` attributes are now
`.nightMode`-aware CSS classes (`fb-*`/`status-*` for the typing-feedback success/error/
warning/info states, `compare-*` for the Compare card). Per Craig: status colors stay
close to their pre-existing blue/green/red/orange roles (no new hues introduced); the
"warning" state stayed in the original orange family (`#af3a03`/`#fe8019`, reusing Accent
A) rather than switching to Gruvbox's yellow; dark-mode red/orange use Gruvbox's *bright*
tier, not the muted/neutral tier, for maximum luminance contrast — specifically so they
don't wash out under the red-tint filter, per Craig's explicit request. A 5th demo card
(`palette-compare-status`) was added to `Palette_Comparison_Demo` previewing these exact
shipped colors for Craig to confirm under pass 3 before this is treated as fully
validated. **Status: all code delivered to Craig and written to his checkout; not yet
synced to live Anki or confirmed on-device.** Next step for Craig: `make ua-setup` (all
four UA note types) and `make ua-setup-pvom`, then re-run
`python tools/anki/setup/setup_palette_comparison_demo.py` to pick up the new status-color
demo card and re-test pass 3 specifically for the red/orange legibility question above.
2026-08-01: **PR merged to `main`.** The Gruvbox rollout above (`feature/anki-mobile-
night-mode` → `main`) merged via a regular merge commit (not squash), by design — Craig
wants to keep committing follow-up fixes to `feature/anki-mobile-night-mode` itself while
he runs the on-device validation pass described above, then open a clean follow-up PR
with just the new commits, rather than branching per fix. **The code is now in `main`,
but on-device validation (the `make ua-setup`/`make ua-setup-pvom` sync, the three-pass
Day/Night/red-tint walkthrough, and the `palette-compare-status` red/orange check
specifically) is still outstanding** — nothing above should be read as "confirmed
working" until that pass happens. If validation surfaces fixes, make them on
`feature/anki-mobile-night-mode` (confirm with `git branch -a`/`git status` that it's
still there — the merge-commit choice was specifically so it wouldn't need to be
recreated) and PR that branch into `main` again when ready.
2026-08-04: **UA_Lexeme per-slot euphony tolerance/display + EN→UA example sentence**
(branch `feature/ua-lexeme-aspect-euphony-cards`, based off `main` at the `maint/lexeme-
review` merge, PR #63). Implemented three items from the structural (non-lexeme-content)
task queue: (1) `EN_UA_FRONT` now shows `EN_Example` for context (was back-only) — confirmed
this was genuinely missing, not already-true as the 2026-08-03 note had left open; deduped
the now-redundant `EN_Example` line from `EN_UA_BACK`'s ref-divider, matching the existing
`UA_Example`/`UA_EN_FRONT` precedent from 2026-07-28. (2) Per-slot euphony tolerance: new
`Lemma_Euphony`/`ImperfectiveUnidirectional_Euphony`/`Perfective_Euphony` fields wire up
euphony data that already existed in 7 CNSF notes (0115, 0124, 0153, 0211, 0281, 0377, 0379,
from a 2026-07-26 corpus survey) but was never synced to the live model — dead data until
now. `EN_UA_BACK`'s feedback script now evaluates each aspect slot independently (PERFECT/
CORRECT/INCORRECT per-slot, via new `_EuphonySlots` field) instead of only matching the
whole compound `TypingTarget_UA` string, mirroring `UA_PVOM_Infinitive`'s already-working
single-slot version of the same pattern (`setup_ua_pvom_note_type.py`'s `FEEDBACK_SCRIPT`).
`EuphonyNote` remains a fallback for singlet notes authored before the per-slot fields
existed. Item 2 of the original per-slot-euphony plan (verb-phrase aspect defaulting) is
authoring guidance only ("no new field, authoring discipline"), not implemented as code.
(3) New `_UA_EN_DisplayLemma` field shows euphonic alternates inline on the UA→EN
Recognition front (e.g. "вхо́дити / уві́йти (ввійти́)"), deliberately kept separate from
`TypingTarget_UA` so the EN→UA typing target never grows parentheticals — Claude's proposed
answer to the 2026-08-03 "worth reconciling the two" note, flagged to Craig as a naming/
format decision rather than assumed settled.
Added 12 new unit tests (`tests/ua/test_lexeme_import.py`, `TestComputeEuphonySlots` +
`TestComputeUaEnDisplay`) covering real corpus cases (0115/0124-style doublets, singlet
legacy-`EuphonyNote` fallback, singlet with its own `*_Euphony` field, defensive
unpopulated-slot cases) — all 12 pass, confirmed independently in both Claude's sandbox and
Craig's local run.
**Two pre-existing test failures found and parked, unrelated to this work:** running the
full `tests/ua/test_lexeme_import.py` file surfaces 13 failures that predate this session
(confirmed identical on both Claude's sandbox and Craig's machine). (a) `TestComputeTypingTarget`
(8 failures) tests the shelved 2026-07-25 `Lemma_Euphony` redesign (`881ac25`/`2e93202` —
dict-returning `compute_typing_target()` with `"full"`/`"base"`/`"alt"` keys, `" ; "`-joined
primary+euphonic forms requiring both to be typed together) that this log's 2026-07-28 entry
documents as fully reverted back to the simpler `a5b4a15` tolerance-only design — the one
live today, and the one item (2) above builds on. The test file was apparently never updated
when the redesign was abandoned. (b) `TestPruneOrphansSafetyGate` (5 failures) references
`prune_orphans`/`collect_all_corpus_note_ids`/`all_anki_note_ids`/`delete_notes`, none of
which exist anywhere in `ua_lexeme_import.py` or elsewhere in the repo (grep-confirmed) —
this is the same "`prune_orphans` gap" already flagged in passing on 2026-07-31 (see the
`Verb_Conj_Table` Removal Plan section above), not something new. Both branch and `main` sit
at the `maint/lexeme-review` merge (PR #63) — the likely source of both mismatches (test
file changes merged without matching source changes, or vice versa) — not yet investigated
further. See `CLAUDE-active-status.md` Next Actions for the troubleshooting task.
**Status: code + tests complete, not yet synced to live Anki or on-device validated.** Next:
`make ua-setup-lexeme` + `make ua-lexeme`, then spot-check 0115/0124/0581 and the
`EN_UA_FRONT` example-sentence change in Anki.
2026-08-04 (continued): **0581/0584 spot-check follow-up + ua-verb-0009/0010 fix.** Craig's
spot-check of 0581 (ходити/йти/піти) surfaced a real alternate typing answer, "ходи́ти / іти́
/ піти́" -- йти/іти are free-variant headworks for the same unidirectional imperfective, per
Craig a euphonic (semi-vowel і~й) mutation, same family as the і/й "and" alternation already
cited in 0581's own `EuphonyNote`, not a separate category needing new fields. Populated the
new per-slot `ImperfectiveUnidirectional_Euphony` field on 0581 (`іти́`) and on 0584
(плавати/пливти/попливти triplet, `плисти́` -- same situation, already documented in its own
`EuphonyNote` from 2026-07-31, parallel to 0581's). Checked 0582/0583/0585 (їздити/літати/
бігати triplets) for the same pattern -- none found. Both notes' typing/display now use the
#3/#5 mechanism live rather than the previously-inert `EuphonyNote` prose.
Separately, Craig flagged that пливти and плисти need their own `UA_Verb` conjugation notes
since their present tense is identical but past tense diverges -- already true structurally
(`ua-verb-0009`/`0086` for пливти/плисти, `ua-verb-0010`/`0087` for попливти/поплисти), but
this surfaced that `ua-verb-0009`/`0010`'s stored conjugation data was still the wrong-verb
mismatch found and held open 2026-07-31 (see "Remaining Work" item 11, now resolved). Fixed
both: `0009` (пливти) used the paradigm already Горох-verified and documented in `0086`'s
Verification Notes (present/imperative identical to плисти: пливу́/пливе́ш/пливе́/пливе́м,
пливемо́/пливете́/пливу́ть, пливи́/пливі́м,пливі́мо/пливі́ть; past divergent: плив/пливла́/
пливло́/пливли́). `0010` (попливти) needed fresh sourcing -- `0087`'s 2026-07-31 session had
only verified поплисти itself, not попливти -- fetched live via Claude in Chrome once
reconnected mid-session (goroh.pp.ua/Словозміна/попливти): попливу́/попливе́ш/попливе́/
попливе́м,попливемо́/попливете́/попливу́ть, попливи́/попливі́м,попливі́мо/попливі́ть (turn out
identical to `0087`/поплисти, confirming the same present/imperative-identical pattern),
past попли́в/попливла́/попливло́/попливли́ (masc stressed here, two syllables, unlike пливти's
unstressed monosyllabic плив). Both notes flipped `stress:unverified` → `stress:verified`.
**Status: all four lexeme/verb note fixes written to Craig's checkout, not yet
canonicalized/synced.** Next: `make ua-lexeme-fix` + `make ua-lexeme` (0581/0584), then
`make ua-verb-fix` + `make ua-verb` (0009/0010), then re-check in Anki.
2026-08-04 (continued further): **Craig decided synthetic future tense stays out of `UA_Verb`**
(formation is close to 100% procedural for imperfective verbs -- see "Future tense --
deliberately not a stored field" under Card Template Techniques above for the full note).
**Found a dangling commit with real, independently-authored `ua-verb-0009`/`0010` conjugation
data, predating today's fix.** Craig recalled deleting a branch with "a lot of conjugation
verifications" — reflog search found `f907726`, still live as
`origin/chore/ua-verb-participle-merge-and-stress-pass` (dated 2026-08-02: "Verify stress for
ua-verb-0001-0016," "Merge Participle_Passive_Past_m/_f into one field; fix Past_1pl/Past_3pl
mismatch," touching all 87 `ua-verb-*.md` notes plus `setup_ua_note_types.py`) — tag command
given to Craig: `git tag archive/ua-verb-participle-merge-and-stress-pass f907726` +
`git push origin archive/ua-verb-participle-merge-and-stress-pass` (not yet run as of this
writing). Diffed that commit's `ua-verb-0009`/`0010` against today's fix and cross-checked both
live against Горох. Two real findings: (1) today's fix had left `Lemma` unstressed
(`пливти`/`попливти`) — the dangling branch had it right (`пливти́`/`попливти́`); corrected here,
since an unstressed multisyllable lemma is this project's own documented red flag for a bad
extraction. (2) Горох confirms `Pres_1pl`/`Imperative_1pl` genuinely have free-variant short
(-м) and full (-мо) forms for both verbs (e.g. `пливе́м, пливемо́` / `пливі́м, пливі́мо`) — today's
fix had stored both variants, the dangling branch stores only the -мо form. **Per Craig: "anything
verified from `archive/ua-verb-participle-merge-and-stress-pass` is truth"** — so the -мо-only
form is the adopted project convention (not a correctness question; both forms are valid
Ukrainian, this is a "store one canonical form" choice), and `0009`/`0010`'s `Pres_1pl`/
`Imperative_1pl` were simplified to match (`пливемо́`/`пливі́мо`, `попливемо́`/`попливі́мо`).
Also adopted the dangling branch's `Participle_Adverbial_Present: пливучи́` on `0009` (was
blank; `0010` correctly stays blank, попливти being perfective). **Open follow-ups, deferred to
a full reconciliation of the dangling branch (not attempted here — it also touches
`setup_ua_note_types.py`, which conflicts with today's #3/#4/#5 structural work on the same
file):** whether `ua-verb-0086`/`0087` (плисти/поплисти, sourced 2026-07-31) need the same
-мо-only simplification — they still carry dual-variant `Pres_1pl`/`Imperative_1pl`; and the
dangling branch's `Participle_Passive_Past_m`/`_f` → single-field schema consolidation, not yet
applied to the live model. **Branching decision (per Craig): keep structure and content on
separate branches, not just separate commits on one branch.** `feature/ua-lexeme-aspect-euphony-cards`
stays scoped to the #3/#4/#5 code + tests only (`setup_ua_note_types.py`, `ua_lexeme_import.py`,
`tests/ua/test_lexeme_import.py`, plus only the CLAUDE.md/CLAUDE-active-status.md hunks
describing that code). A second branch, stacked on top after that commit (working name
`content/ua-motion-verb-euphony-and-conjugation-fixes`), carries the lexeme/verb content:
`ua-lexeme-0581`/`0584`'s new `ImperfectiveUnidirectional_Euphony` values, `ua-verb-0009`/`0010`'s
conjugation fix, the Future-tense doc note, and the dangling-branch/-мо-convention material
above. Exact commands given to Craig in the same session; not yet run.
2026-08-04 (continued further still): **Dangling-branch reconciliation landed via git merge,
plus branch cleanup.** The two-branch plan above was executed: `feature/ua-lexeme-aspect-
euphony-cards` got the #3/#4/#5 structural commit; a stacked content commit landed directly
on top of `origin/chore/ua-verb-participle-merge-and-stress-pass` (`f907726` → `a24d6e6`,
fast-forward push, no divergent-history merge needed) carrying `ua-lexeme-0581`/`0584`,
`ua-verb-0009`/`0010`, and the matching doc hunks. Opening a PR for that content branch
into `main` (GitHub PR #2) surfaced real conflicts on two files: `CLAUDE-active-status.md`
(pure add/add — both branches had appended different bullets to the same list; resolved by
keeping both) and `ua-verb-0038.md` (resolved by taking `main`'s side, which had already
picked up proper `ʼ` apostrophes and blank `UA_Example`/`EN_Example` fields via the
`maint/lexeme-review` merge, PR #63 — no actual verb-form data differed, so this was a
formatting/schema pick, not a content-verification call). The repo's `cnsf-canonical`
pre-commit hook then caught a real drift the merge itself hadn't flagged: `ua-verb-0038.md`'s
resolved content still carried the legacy single `Participle_Passive_Past` field instead of
the `_m`/`_f` split every other reconciled note (including `0009`/`0010`) already uses —
fixed by splitting it (both blank, so no data lost) before the merge commit (`2906f8d`) would
pass hooks. Pushed and merged as PR #64. Because the content branch was built directly on
`f907726` (which already carried the full 87-note stress-verification pass from the original
dangling commit, not just 0009/0010), merging `origin/main` back into
`feature/ua-lexeme-aspect-euphony-cards` before opening its own PR pulled that entire
corpus-wide reconciliation through as a side effect — the diff touched all of
`ua-verb-0001.md`–`ua-verb-0087.md`, not just the handful this session touched directly.
That merge was clean (no conflicts). Pushed and merged as PR #65. **Net effect: `main` now
has the dangling branch's full stress-verification content across all 87 `ua-verb-*.md`
notes**, resolving "Remaining Work" item 13's open follow-ups (a) and (c) below, and settling
(b) — the live schema kept the `Participle_Passive_Past_m`/`_f` split rather than migrating
to the dangling branch's single-field proposal, per the `ua-verb-0038.md` resolution above.
Confirmed via a full corpus sync (`make ua-setup-lexeme` → `make ua-lexeme`: 584 lexemes
updated, 0 errors; `make ua-verb-fix` → `make ua-verb`: 87 verbs updated, 0 errors; 15
red/orange-flagged notes correctly kept suspended in both runs) and Craig's on-device
spot-check ("Spot checks are good").
**Branch cleanup, same session:** `feature/anki-mobile-night-mode` deleted (local + remote)
after confirming via `git log main..feature/anki-mobile-night-mode` (empty — fully merged)
and Craig confirming he's happy with the on-device Gruvbox validation, closing out
"Remaining Work" item 3. `feature/ua-lexeme-aspect-euphony-cards`'s now-stale remote deleted
post-PR-#65-merge (repo doesn't auto-delete on merge). `chore/ua-verb-participle-merge-and-
stress-pass` retired in favor of a fresh `maint/verb-review` branch cut from current `main`
(mirroring the existing `maint/lexeme-review` pattern) as the ongoing home for future verb-
corpus review — verified safe via `git merge-base --is-ancestor origin/chore/ua-verb-
participle-merge-and-stress-pass maint/verb-review` (true, zero orphaned commits) before
deleting the old remote. The `archive/ua-verb-participle-merge-and-stress-pass` tag on
`f907726` stays untouched as the permanent historical marker for the original dangling
commit — separate from and unaffected by the new `maint/verb-review` branch.

## Workflow Notes

This repo builds and maintains Anki flashcard decks across three top-level decks:

- **B737** (`domains/b737/`) — type rating study. CNSF markdown notes exported
  to TSV and imported via AnkiConnect. High-stakes professional content.
- **UA** (`domains/ua/`) — formal language learning (Galician/Lviv
  register, Яблуко textbook). Active branch `feature/ua-domain`.
  See `domains/ua/anki/docs/design.md` for full schema and migration plan.
- **Legacy** — archive of older decks. Being systematically migrated or archived.

**FSRS Isolation:** Each top-level deck has completely separate FSRS configuration 
and card history. Cards in B737 do not influence UA scheduling and vice versa.
See [CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md) for parameters.

### The Big 3 Rules (recite verbatim at session start if asked)

1. **Only Craig runs git commands, which Claude provides.** Claude never executes `git`
   itself -- including read-only commands like `status`/`diff`/`log`, even for quick
   investigation. Claude writes the exact command(s); Craig runs them and pastes back the
   output. (A violation on 2026-07-22 -- Claude ran `git status`/`git diff` directly via
   `device_bash` -- left a stale `.git/index.lock` that blocked Craig's own git commands
   until he manually removed it. See CLAUDE-known-issues.md.)
2. **Only Craig deletes files on his computer.** Claude does not delete files via any
   mechanism, even where technically possible. (In practice `device_bash` can't delete
   anyway -- `rm`/`rmdir`/`unlink` fail with "Operation not permitted," only `mv` works --
   but the rule holds regardless of mechanism.)
3. **After each set of commands, Claude waits for Craig to respond before providing
   additional commands.** No stacking multiple rounds of git/shell commands speculatively
   ahead of confirmation.

These extend to `make`, Python scripts that touch AnkiConnect, and any other shell command
in this repo -- all run by Craig, not Claude:

- **Shell commands are run by Craig**, not Claude. Claude provides commands to copy/paste; it does not execute git, make, or Python commands directly. (Claude's sandbox lacks access to the required conda env and git hooks will fail.)
- **Pull requests**: Claude provides the `gh pr create` command; Craig runs it and completes the PR on the GitHub website.

## Reference Files

| Topic | File |
|-------|------|
| **SV field spec** | [CLAUDE-sv-field-conventions.md](CLAUDE-sv-field-conventions.md) |
| **Deck architecture** | [CLAUDE-deck-architecture.md](CLAUDE-deck-architecture.md) |
| **Known issues** | [CLAUDE-known-issues.md](CLAUDE-known-issues.md) |
| **Key paths** | [CLAUDE-key-paths.md](CLAUDE-key-paths.md) |
| **Migration progress** | [CLAUDE-migration-log.md](CLAUDE-migration-log.md) |
| **UA_Verb design** | [CLAUDE-ua-verb-design.md](CLAUDE-ua-verb-design.md) |
| **FSRS deck configs** | [CLAUDE-fsrs-deck-configs.md](CLAUDE-fsrs-deck-configs.md) |
| **Flag audit workflow** | [CLAUDE-flag-audit.md](CLAUDE-flag-audit.md) |
| **Ch-09 vocabulary sourcing workflow** | [CLAUDE-ch09-vocab-workflow.md](CLAUDE-ch09-vocab-workflow.md) |
| **Approved web sources** | [CLAUDE-approved-web-sources.md](CLAUDE-approved-web-sources.md) |
| **Vocab dedup/homograph audit tooling** | [CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md) |
| **Compare card field mapping (homograph vs confusables)** | [CLAUDE-compare-card-field-mapping.md](CLAUDE-compare-card-field-mapping.md) |

---

## Ukrainian Domain (`domains/ua/`)

**Branch:** `feature/ua-domain` (based off `main`)

**Status (as of 2026-07-22):** Вступ (ch-00) complete — 113 notes live, stress verified, examples added.
Book 2 Ch. 9 (`feature/ua-verb-phase2a` branch) imported and polished — 7-item punch list
complete:
  - **18 UA_Lexeme notes** (ua-lexeme-0114–0131, prefixed walking + vehicle motion verbs)
    imported via `make ua-batch BATCH=yabluko-l2/ch-09`. `status:verified`; both UA→EN and
    EN→UA cards active (36 cards). `Compare` card template active for confusable pairs
    (про-/пере- pairs 0120/0121, 0129/0130, plus 0059 from ch-00) via `ConfusableSet` +
    new `Mnemonic_EN`/`CompareA`/`CompareB` fields (see Comparison card section below).
  - **UA_Grammar**: rebuilt from scratch as a real Cloze model (the live model had been a
    stale non-cloze legacy model — see CLAUDE-known-issues.md footgun #5). 9 notes
    (ua-grammar-0001–0009), all `status:draft`/suspended. 0008 (до/в–у/на destination
    prepositions) and 0009 (від/з–із–зі source/departure prepositions) are new, atomically
    clozed and leak-checked — see Cloze design principles below. 0001–0007 still use the
    older "busy" multi-fact-per-cloze pattern and have empty `Source_URL`/`Source_Note`;
    not yet revisited.
  - **UA_Visual**: redesigned from 2 templates (Spatial→UA / UA→Spatial) to a single
    "Prefix + Government" card (front = diagram + blank table, back = same table filled in
    place). 9 notes, 9 cards, `status:verified`, active in `UA::Recognition::Visual`.
  - **UA_PVOM_Infinitive**: reworked from 22 single-form notes to 11 notes × 4 card
    templates (Walking Multi/Uni, Vehicle Multi/Uni) — 44 cards total, each base form
    independently suspendable/leech-trackable.
  - All lexeme + grammar stresses Горох-verified. `Verb_Conj_Table` fully populated for
    all 18 verb pairs (0114–0131).

**UA_Visual card template design (2026-07-10):**
  - Card 1 (Spatial→UA): front = diagram + English meaning; back = Ukrainian prefix, government, verb pairs, example.
  - Card 2 (UA→Spatial): front = Ukrainian prefix + verb pairs; back = diagram + English meaning + government + example.
  - Template redesign fixed & deployed ✅ — `setup_ua_note_types.py` now calls `updateModelTemplates` with all templates in single call (not per-template loop).
  - Templates update correctly via `make ua-setup-visual`.

**Pending / Next planned work (as of 2026-07-23):**
  0. **DONE (2026-07-25).** Integrate the dedup/homograph-check logic directly into the
     vocabulary-generation workflow, not just the standalone `check_lexeme_dedup.py` tool.
     `tools/anki/lib/lexeme_dedup.py` (importable `create_or_link_lexeme()` API implementing
     all three buckets) and `tools/anki/inspect/build_lexeme_index.py` (full-corpus TSV dump
     for audits) were built 2026-07-24 and used for a full 180-note corpus audit — see
     [CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md). The remaining piece
     — an actual `gen_ch09_*.py`-style script calling `create_or_link_lexeme()` — is now
     `tools/anki/extract/gen_ch09_subsection.py` (75 passing tests total across
     `tests/ua/test_lexeme_dedup.py`, `tests/ua/test_build_lexeme_index.py`, and the new
     `tests/ua/test_gen_ch09_subsection.py`). Note on what this script does and doesn't
     automate: Горох verification, phrase/component decomposition, and the new-vs-duplicate-
     vs-homograph *judgment call* itself all still require human/Claude-in-Chrome
     involvement per CLAUDE-ch09-vocab-workflow.md — this script's job is narrower but load-
     bearing: every candidate, once drafted with its dedup decision already made, is routed
     through `create_or_link_lexeme()` before it touches disk, so no note can land in the
     corpus by a hand-written-file path that skips the check. Not yet exercised against a
     real ch.9.3+ batch — that's the next actual use of it.
  1. Continue sourcing and importing UA vocabulary from Yabluko L2 Chapter 9 — subsections
     9.3 onward. (9.1 sourced, reviewed, verified, and synced. 9.2 sourced, drafted,
     canonicalized, and synced as `status:draft` — 18 lexemes ua-lexeme-0163–0180 + 5
     conjugation notes ua-verb-0033–0037.) Keep following the 5 established sourcing rules
     (Горох verification, verb pairing, phrase+component creation, autonomy, draft-until-
     reviewed status).
  2. Craig reviews/validates the ch.9.2 batch and flips `status:draft` → `status:verified`
     once satisfied, same process used for ch.9.1. Re-sync afterward with `make ua-lexeme`
     / `make ua-verb`, or the new `make ua` aggregate target (canonicalizes + syncs every
     UA note type in one pass — see Reference Files).
  3. **Superseded 2026-08-01 — see the dated log entry above and "Remaining Work" items
     1–3 below, all resolved.** Originally scoped as "get the Solarized palette correct
     and consistent"; Craig's actual objective turned out to be broader (a repo-wide
     default palette chosen against his real accessibility need), and the palette itself
     changed from Solarized to **Gruvbox** after an on-device A/B/C comparison. The dual
     CSS-source conflict and the `UA_Visual` `.night_mode`/`.nightMode` bug described below
     are both fixed; kept the paragraphs below for the historical record of how the bugs
     were found. Only `UA_Lexeme`/`UA_Grammar`/`UA_Verb`/`UA_Visual` (the UA domain) were
     touched — B737 note-type CSS/structure was not, per Craig's original instruction to
     keep this CSS-only and UA-scoped; a repo-wide (B737-included) rollout is still future
     work if Craig wants it.
     Two disagreeing CSS sources existed for `UA_Lexeme` (found 2026-07-31): (a)
     `tools/anki/setup/setup_ua_note_types.py`'s own `CSS` constant — plain, non-Solarized,
     the one this doc's setup scripts actually apply — and (b) the separate,
     Makefile-untracked `tools/anki/setup/update_legacy_css.py` — genuinely Solarized
     (`.lemma`/`.perfective`/`.pos` in `#2aa198`/`#93a1a1`, full `.nightMode` dark rules), but
     apparently a manually-run one-off script, not wired into any `make` target. Whichever ran
     most recently against live Anki wins; Craig confirmed today that plain (source a) is
     currently live for all three `UA_Lexeme` templates (UA→EN, EN→UA, Compare) — so Solarized
     for `UA_Lexeme` is genuine future work, not a live-but-partial state, and there's a
     standing decision needed (merge the two scripts, retire one, or wire `update_legacy_css.py`
     into the Makefile) before that work starts, so the two sources don't fight again.
     Separately confirmed 2026-07-30/31: all five of `B737_Checklist`, `B737_Mnemonic`,
     `B737_Structured`, `B737_SV_MCQ`, `B737_SV_TF` already use the correct `.nightMode`
     selector with real Solarized colors (`#268bd2`, `#fdf6e3`, etc.) — the "still need to
     audit" note below was stale; no B737 note type needs the camelCase fix except `UA_Visual`.
     See `.claude/memory/b737-anki-solarized-theme.md` for the original project tracking note.
     Craig wants this kept CSS-only — do not touch B737 note-type structure/fields.

### Remaining Work — Note & Card-Template Structure (as of 2026-07-31, separate from
lexeme-content verification)

This is a structural punch list — note-type schema, card templates, CSS, and tooling —
distinct from chapter-by-chapter vocabulary sourcing/verification tracked elsewhere in
this doc. Roughly in priority order:

1. **Two disagreeing `UA_Lexeme` CSS sources** (found 2026-07-31, see item 3 above) —
   **Resolved, 2026-08-01; merged to `main`.** Decision made: `setup_ua_note_types.py`'s
   `CSS` constant (plus `GRAMMAR_CSS`/`VERB_CSS`/`VISUAL_CSS`) is now the single source of
   truth for all four live UA note types; `update_legacy_css.py` trimmed to its
   B737-legacy entries only (`SV_CLOZE_CSS`/`B737_SYSTEMS_CSS`), per Craig's explicit
   choice. See the 2026-08-01 log entries above.
2. **`UA_Visual`'s `.night_mode`/`.nightMode` CSS bug** (found 2026-07-23) — **Fixed,
   2026-08-01; merged to `main`.** All 13 occurrences in `VISUAL_CSS` converted to
   `.nightMode`; the `.night_mode` duplication is intentionally not carried forward into
   new work (Android isn't one of Craig's devices — see the `.nightMode`/`.night_mode`
   research in `domains/demo/FINDINGS_AND_TESTING.md`), though it's correctly left alone
   in the two B737 legacy CSS blocks that keep both selectors for parity.
3. **`UA_Lexeme` color palette** — **Resolved, 2026-08-04.** Code done and merged to
   `main` 2026-08-01; on-device validation confirmed by Craig 2026-08-04 ("I'm pretty
   happy with the night mode"). Superseded Solarized with **Gruvbox** after an on-device
   A/B/C comparison against Craig's real accessibility need (iOS red-tint Color Filter
   night mode) — see the 2026-08-01 log entries above for the full palette values and the
   `domains/demo/README.md` "Palette Comparison Demo" section for the comparison tooling.
   Rolled out to `CSS`/`GRAMMAR_CSS`/`VERB_CSS`/`VISUAL_CSS`, the Compare card, and both
   typing-feedback scripts (`EN_UA_BACK` here and `setup_ua_pvom_note_type.py`'s
   `FEEDBACK_SCRIPT`, previously unthemed). `feature/anki-mobile-night-mode` (kept alive
   past its original merge specifically for follow-up fixes) deleted 2026-08-04, confirmed
   fully merged into `main` first — no fixes ended up being needed.
4. **`Verb_Conj_Table` field removal** — **Resolved, 2026-07-31.** Field blanked
   corpus-wide 2026-07-22; steps 3-4 of the plan below (strip the field from all 584 CNSF
   lexeme files, canonicalize, update dependent tooling) done 2026-07-31 on branch
   `chore/remove-verb-conj-table`. Steps 1 and 5 turned out to be unnecessary —
   `inspect_ua_lexeme_fields.py` confirmed the live `UA_Lexeme` model never had the field
   to begin with (already gone before this audit), so there was nothing for
   `modelFieldRemove`/a collection backup to act on; only the CNSF source files still
   carried the dead key, which steps 3-4 fixed. Step 6 verification done. Merged to
   `main` via PR #58 (2026-07-31); branch deleted. See "Verb_Conj_Table Removal Plan"
   below for the full writeup — no further action needed, this item was previously
   listed as still requiring Craig's action by mistake (this doc hadn't been updated to
   match the "Resolved"/"Removal plan is effectively complete" notes already sitting in
   that section).
5. **UA→EN front aspect display** — **Done, 2026-07-31**, synced. See "UA→EN front
   aspect display" under Card Template Techniques above.
6. **Compare-card suspend mechanism** (`set_compare_card_suspended()` in
   `ua_lexeme_import.py`) — **Tested and confirmed working (2026-08-01).** Built 3
   deliberately-constructed scratch notes (ua-lexeme-9997/9998/9999, deleted from Anki
   and the repo after verification) to exercise `suspend_compare_card`:
   - **Blank `CompareA` from note creation** (9999, homograph mode, `ConfusableSet`
     populated, `CompareA` never authored): Anki never generates the Compare card at
     all — its own empty-card-generation rule refuses, because the `{{^CompareA}}`
     "should be suspended" warning text in `COMPARISON_FRONT` is pure static template
     text with no field substitution, so the rendered front doesn't count as non-empty.
     This makes that branch of the Python suspend logic dead/unreachable in practice —
     harmless, but the comment above it in `setup_ua_note_types.py` calling it "a
     defensive fallback for previewing/QA" is inaccurate, since the card whose front
     would show the notice never exists to preview. Worth a comment fix; not urgent.
   - **Valid Compare data throughout** (9998): Card 3 generated normally and stayed
     unsuspended, as expected.
   - **Valid → retracted** (9997, two-phase: imported with real `ConfusableSet`/
     `CompareA`/`CompareB` so Anki generated a genuine Compare card, then re-imported
     with those fields cleared): this was the real test of the historical footgun. The
     pre-existing Compare card correctly ended up suspended on re-sync (confirmed via
     AnkiConnect `cardsInfo` `queue:-1` and visually in Anki's browser) while UA→EN/
     EN→UA stayed active. **The footgun does not reproduce here** — suspension does
     stick on a genuinely pre-existing Compare card. Resolved.
7. **Per-slot euphony tolerance + verb-phrase aspect defaulting** — scoped with Craig
   2026-07-29, not built. See the full design under Card Template Techniques above.
   Still open.
8. **Flagged Card Fix Workflow tooling** — **Built and tested, 2026-08-01.**
   `tools/anki/inspect/ua_flag_audit.py` implements Phase 1 (`--query`) and Phase 3
   (`--apply`) of the workflow in "Flagged Card Fix Workflow (Future)" below (Phase 2,
   the interactive review/fix loop, is a conversation with Claude, not something a
   script does). `--query` validated against all 11 real flagged notes currently in the
   corpus -- every one correctly resolved to its canonical CNSF path, including the
   recursive lexeme search across textbook/chapter subdirectories. `--apply` validated
   end-to-end via a disposable synthetic note: found and fixed a real bug along the way
   -- `CLAUDE-flag-audit.md`'s suggested flag-removal call (`anki_request("unmark", ...)`)
   was aspirational and never actually worked (`"unsupported action"` -- there is no
   batch unmark/setFlag action in AnkiConnect). Real mechanism is
   `setSpecificValueOfCard`, one card at a time, with `newValues` as ints (`["0"]`
   silently no-ops; `[0]` actually clears the flag). `--apply` now does a three-pass
   sequence -- sync corrected content (still suspended, still flagged) → clear flags →
   re-sync (picks up the cleared flags, unsuspends) -- so fixed notes end up unsuspended
   within the same `--apply` run rather than deferred to whatever sync happens next.
   `CLAUDE-flag-audit.md` corrected to match. See git history on
   `feature/flagged-card-fix-workflow` for the full test trail.
9. **`gen_ch09_subsection.py` generator-script wiring** — built 2026-07-25, not yet
   exercised against a real ch.9.3+ batch. Unexercised, not broken.
10. **`UA_Grammar` 0001–0007 cloze review pass** — these notes predate the atomicity/
    no-self-leak/no-cross-cloze-substring-leak principles established 2026-07-22 (see
    "Cloze note design principles" below) and haven't been audited against them.
    Needs a decision on whether to revisit.
11. **ua-verb-0009/0010 conjugation-table data mismatch** — **Resolved 2026-08-04.** See
    the dated log entry below for the fix; kept here for the historical record of how the
    bug was found (2026-07-31, both notes' stored `Pres_*`/`Imperative_*`/`Past_*` fields
    matched a different verb family — плинути/попити-adjacent forms — instead of their own
    `Lemma`, пливти/попливти).
12. **New content pending Craig's `status:draft` → `status:verified` review**:
    ua-lexeme-0581–0585 (base motion-verb triplets: ходити/їздити/літати/плавати/
    бігати) and ua-verb-0086/0087 (плисти/поплисти), both drafted 2026-07-31.
13. **Proper reconciliation of `archive/ua-verb-participle-merge-and-stress-pass`** —
    **Resolved, 2026-08-04.** Found earlier the same day as a locally-deleted branch, still
    live as `origin/chore/ua-verb-participle-merge-and-stress-pass` (commit `f907726`,
    tagged for safekeeping), containing a real stress-verification pass across all 87
    `ua-verb-*.md` notes plus a `Participle_Passive_Past` schema question. See the dated
    "2026-08-04 (continued further still)" log entry above for the full mechanics, but in
    short: because the content branch used for today's `ua-verb-0009`/`0010` fixes was built
    directly on top of `f907726`, merging it (and later `main`) through PRs #64 and #65
    carried the *entire* 87-note reconciliation into `main` as a side effect, not just the
    notes this session touched by hand. Confirmed via a clean corpus-wide `make ua-verb-fix`
    + `make ua-verb` sync (87/87 updated, 0 errors) and Craig's on-device spot-check. The
    three items previously left open here are now closed: (a) the -мо-only
    `Pres_1pl`/`Imperative_1pl` convention is corpus-wide, not just on `0009`/`0010`; (b) the
    `Participle_Passive_Past_m`/`_f` split (not the dangling branch's single-field proposal)
    is confirmed as the live schema — the `cnsf-canonical` pre-commit hook now enforces it;
    (c) the rest of the 0002–0087 conjugation data came along in the same merge. The
    `chore/ua-verb-participle-merge-and-stress-pass` branch itself was retired in favor of
    `maint/verb-review`, cut fresh from `main`, as the ongoing home for future verb-corpus
    review (mirroring `maint/lexeme-review`'s pattern). **Not independently re-verified:**
    this session's confirmation was a successful sync run plus Craig's spot-check, not a
    note-by-note read of all 87 files' final stress marks/tags — worth keeping in mind if
    something looks off in the previously-`status:draft` 0033–0085 range during future review.

**Done, for reference (structural work closed out this project so far):** the
CompareA-D/CompareScenario Compare-card redesign (2026-07-24, corrected 2026-07-28),
the `compute_compare_options()` clobbering-bug fix (2026-07-28), the homograph
Compare-card generalization (bucket 2 above, done 2026-07-30), the тепло Compare-card
content gap fix + corpus-wide sweep (2026-07-30), the EN→UA aspect+euphony typing
restoration (2026-07-28, git archaeology), the UA→EN front aspect display
(2026-07-31, item 5 above), the Compare-card suspend mechanism test/confirmation
(2026-08-01, item 6 above), the Flagged Card Fix Workflow tooling
(2026-08-01, item 8 above), and the CSS single-source-of-truth decision + `.night_mode`
selector fix + Gruvbox palette rollout (2026-08-01, items 1–3 above — merged to `main`
via `feature/anki-mobile-night-mode`, on-device validation confirmed and branch deleted
2026-08-04, see item 3), and the `Verb_Conj_Table` field removal (2026-07-31, item 4 above — this list previously
omitted it since item 4 itself was mislabeled as still open; corrected 2026-08-01).

### Current Anki state
- 3,932 existing Ukrainian notes in vanilla Basic / Basic+reversed / Cloze types
- 788 leeches (20%) — triage before bulk migration
- Active deck hierarchy: `UA::Recognition::*` / `UA::Production::*`
- New canonical decks: `UA::Recognition::UA→EN` / `UA::Production::EN→UA`
- Legacy decks: `Ukrainian Active::Яблуко`, `Inactive::Ukrainian Inactive::*`
- Tags in use: `textbook:яблуко`, `ch:2.8.x` (= Level 2, Ch. 8, §x), `leech`, `converted`, `to_convert`

### Primary note type: `UA_Lexeme`

**Fields (20, in semantic order):**

*Identity & Metadata:* `NoteID`

*Core Lemma & Morphology:* `Lemma`, `PartOfSpeech`, `Gender`

*Aspect (verbs only):* `Perfective` (PFV counterpart), `ImperfectiveUnidirectional` (motion verb directional form)

*Semantic Content:* `EN_Gloss`

*Grammatical Properties:* `Govt_Case`, `IrregularForms`, `CounterpartForm` (gender pairs), `VerbMotion_Pair` (base unprefixed form)

*Semantic Relations:* `ConfusableSet`, `CrossLang_Analog`, `EuphonyNote` (alternate spellings: уже/вже, всі/усі)

*Typing & Examples:* `TypingAnswer` (Lemma without stress marks), `UA_Example`, `EN_Example`

*Metadata & Sources:* `Tags_Ch`, `Source_URL`, `Source_Note`

**Aspect convention:** Lemma is always imperfective (base form). Perfective field contains PFV counterpart. Aspect is implicit in field structure (no explicit Aspect field needed). Exception: a genuine perfectiva tantum (no imperfective counterpart exists) has to file Lemma as the perfective form instead — tag it `aspect:perfective-only` when this happens so the exception is documented, not silently inconsistent with the rule.

**Aspect-only tags (`aspect:imperfective-only` / `aspect:perfective-only`, added 2026-07-30):** hand-authored tags marking a verb as confirmed to have no aspectual counterpart (imperfectiva/perfectiva tantum, e.g. мати for imperfective-only). Craig wants to be directly involved in every decision that labels a verb this way, so these tags are **only ever applied by Craig, by hand, after checking Горох** — no script in this repo applies them automatically, and none should in the future without his explicit sign-off. `tools/anki/inspect/audit_verb_aspect_forms.py` (extended 2026-07-30, wired into `make ua-check`) scans every `pos:verb` note and flags it for review only when it has ZERO aspectual counterparts populated (a true singlet — both `ImperfectiveUnidirectional` and `Perfective` blank) and neither aspect-only tag is present; a verb missing just one of two possible counterparts (a doublet) is never flagged, since one populated counterpart already means the pairing is at least partly recorded. See "Vocabulary dedup & homograph handling" bucket 5 below for the parallel `pending-confusable:<lemma>` mechanism, same Craig-decides-not-scripts philosophy.

**Verb conjugations:** `Verb_Conj_Table` field has been fully removed from UA_Lexeme — corpus-wide (all 584 lexeme notes) and confirmed absent from the live model, complete as of 2026-07-31 — see "Verb_Conj_Table Removal Plan (Complete, 2026-07-31)" below. Conjugation morphology lives in the UA_Verb note type as structured fields, one note per lemma's own aspect, linked to the lexeme via matching Lemma text.

### Verb_Conj_Table Removal Plan (Complete, 2026-07-31)

**Status:** Planned, not yet executed. Decided 2026-07-22 after clearing all *content* from the
field on the 18 pre-existing verb lexemes (`ua-lexeme-0114`–`0131`) and the 5 new ch.9.2 verb
lexemes (`ua-lexeme-0176`–`0180`) — this plan covers removing the *field itself* from the
schema/model, corpus-wide.

**Correction of prior doc drift:** this file previously claimed (above) that `Verb_Conj_Table`
had already been removed from `UA_Lexeme` — that was aspirational/incorrect. The field is still
live in the Anki model and present (currently blank) in all ~180 lexeme `.md` files.

**Progress (2026-07-31):** Steps 3-4 executed on branch `chore/remove-verb-conj-table`. The
"~180" estimate above was wrong — the field was present in all 584 lexeme `.md` files
(`domains/ua/anki/notes/lexemes/*/*/*.md`); confirmed via corpus-wide grep before removal,
value uniformly blank (`Verb_Conj_Table: ''`) everywhere, no exceptions. All 584 stripped
and re-canonicalized via `cnsf_canonicalize.py --write` (pure local tool, no AnkiConnect).
Step 4's tooling list undercounted by 3 — besides the 4 files named below,
`tools/anki/extract/gen_ch09_subsection.py` (active, unexercised generator script) and two
more test fixtures (`tests/ua/test_lexeme_dedup.py`, `tests/ua/test_gen_ch09_subsection.py`)
also referenced the field and were updated too. Left alone, per the plan: the four historical
one-off scripts (`patch_ch09_conj_tables.py`, `patch_ch09_stress.py`,
`gen_ua_lexemes_l2_ch09.py`, `gen_ua_lexemes_vstup.py`). Also found but NOT touched (out of
scope for this pass, flagged for Craig): `domains/ua/anki/docs/design.md` still describes
`Verb_Conj_Table` in several places but is broadly stale relative to the live schema
(predates `CounterpartForm`/`AspectCue`/`TypingTarget_UA` etc.) and needs a fuller refresh,
not a one-line fix; and `CLAUDE-active-status.md` claims (as of 2026-07-26) that
`Verb_Conj_Table` was "removed... moved to UA_Verb note type" — which wasn't true before
today's actual removal, a doc-vs-code mismatch in the same family as the `_AspectLabel` and
`prune_orphans` gaps found earlier 2026-07-31.

**Resolved (2026-07-31):** step 1 run — `inspect_ua_lexeme_fields.py` confirms the live
`UA_Lexeme` model's 32 fields do NOT include `Verb_Conj_Table` at all. So
`CLAUDE-active-status.md`'s claim was right about the *model* (already removed there,
predating this doc) — it was only the CNSF *source files* that still carried the dead key,
which today's step 3-4 work fixed. Step 5 (`modelFieldRemove`) is therefore unnecessary —
there's nothing left in the model to remove. Step 2 (backup) is no longer required either,
since no live-model mutation is happening. Step 6 verification: `cnsf_canonicalize --check`
already clean (done above); running `tests/ua/` and a live-card spot-check are optional at
this point, not blocking, since nothing rendered this field and the model was never touched.
**Removal plan is effectively complete.** `chore/remove-verb-conj-table` was reviewed,
merged to `main` via PR #58 (2026-07-31), and the branch deleted (local + remote) —
no further AnkiConnect action needed.

**Rationale:** repo-wide grep confirms no card template anywhere references `{{Verb_Conj_Table}}`
— the field has never been rendered on any card, in any note-type version. It's genuinely dead
data, not just duplicated-but-harmless. Conjugation data belongs on the dedicated `UA_Verb` notes
(structured `Pres_*`/`Imperative_*`/`Past_*` fields).

**Known complication:** `tools/anki/setup/setup_ua_note_types.py`'s `FIELDS` list — the nominal
source of truth for the model definition — does *not* currently include `Verb_Conj_Table`, nor
`Verification Notes`, `Mnemonic_EN`, `CompareA`, or `CompareB`, all of which real notes have. That
script is stale relative to the live Anki model — **don't trust it as ground truth** for this
migration. Before touching the live model, run `tools/anki/inspect/inspect_ua_lexeme_fields.py` to
get the actual field list/order straight from AnkiConnect.

**Migration steps (as originally planned — kept for historical record; see "Progress"/
"Resolved" above for what actually happened, which diverged in a few places: steps 1/2/5
turned out unnecessary since the live model never had the field to remove, and step 3's
scope was 584 files, not the ~180 estimated below):**

1. **Verify live state** (read-only): run `inspect_ua_lexeme_fields.py` to confirm
   `Verb_Conj_Table`'s exact position in the real model and note any other drift from
   `setup_ua_note_types.py`.
2. **Back up the Anki collection** before any schema mutation (File → Export, or Anki's own
   backup) — `modelFieldRemove` is destructive and not easily undone.
3. **Strip the field from all CNSF source files**: delete the `Verb_Conj_Table` key from the
   `fields:` dict in all ~180 `ua_lexeme` `.md` files (`yabluko-l1/` and `yabluko-l2/`), then run
   `python -m tools.anki.cnsf_canonicalize --write` across the whole lexeme corpus. Commit this
   on its own.
4. **Update tooling that references the field:**
   - `tools/anki/extract/mappings/UA_Lexeme.yml` — remove the `f__Verb_Conj_Table` entry.
   - `tools/anki/generate/ua_generate_examples.py` (~line 176) — remove `"Verb_Conj_Table"` from
     its field-order list.
   - `tests/ua/test_verify_stress_goroh.py` (4 fixture occurrences) and
     `tests/ua/test_backfill_source_url.py` (1 occurrence) — hardcode `Verb_Conj_Table: ''` in
     sample note fixtures; update or the tests may fail once real notes stop carrying the key.
     Run the full `tests/ua/` suite after.
   - `tools/anki/extract/gen_ua_lexemes_l2_ch09.py` / `gen_ua_lexemes_vstup.py` are historical
     one-off generation scripts (already run, not part of the live pipeline) — optional cleanup
     only, low priority.
   - `tools/anki/inspect/patch_ch09_conj_tables.py` / `patch_ch09_stress.py` are historical patch
     scripts, already executed — leave as-is, historical record.
5. **Remove the field from the live Anki model**: AnkiConnect `modelFieldRemove` on `UA_Lexeme`
   for `Verb_Conj_Table`. Craig runs this himself (same pattern as all sync/import scripts) —
   probably worth a tiny one-off script that prints the field list before and after, rather than
   a raw API call.
6. **Verify:** re-run `inspect_ua_lexeme_fields.py` to confirm removal; re-run
   `cnsf_canonicalize --check` across the corpus; run `tests/ua/`; spot-check a few `UA_Lexeme`
   cards in the Anki browser (expect zero visual change, since nothing ever rendered this field).

**Historical note:** this "not blocking" framing applied while the plan was still open —
kept here for context on why it sat unexecuted for over a week. The removal itself is
done as of 2026-07-31 (see above).

### Card Template Techniques

**Polysemous word examples (multiple meanings)**

When a UA word has multiple distinct meanings, demonstrate semantic range in the example fields:

```yaml
UA_Example: |
  Example showing meaning 1
  Example showing meaning 2
EN_Example: |
  Translation for meaning 1
  Translation for meaning 2
```

Example: вік (age as measure of time; era/epoch as historical period)
```
UA_Example: У якому віці діти йдуть до школи? | Вони жили в добу Середніх віків.
EN_Example: At what age do children go to school? | They lived during the Middle Ages.
```

This shows the learner that the same Ukrainian word spans multiple semantic domains.

**Comparison card (scenario-based confusable discrimination, redesigned 2026-07-24 for
CompareA-D + CompareScenario -- this section previously described the pre-redesign flat-prose
format; corrected 2026-07-28)**

**See [CLAUDE-compare-card-field-mapping.md](CLAUDE-compare-card-field-mapping.md) for the
full field-by-field spec** (added 2026-07-28 after two authoring bugs were found in the same
session: ua-lexeme-0305 got `ConfusableSet` populated with no `CompareA`/`CompareB` authored,
which the importer's legacy fallback then filled with the raw `ConfusableSet` prose paragraph
-- rendered live, unsuspended, as a fake front-side answer chip; ua-lexeme-0181 had never been
migrated off the pre-dual-mode English-chip format, so its Compare card front was entirely in
English with nothing to recognize in Ukrainian). The short version: decide up front whether a
note is a true homograph (one spelling, split across sibling notes, `CompareA`/`CompareB` hold
Ukrainian *sentences*, `Homograph_SenseA`/`SenseB` hold the English answers) or a confusables
cluster (different spellings, `CompareA`-`D` hold the Ukrainian *words themselves*,
`Homograph_SenseA`/`SenseB` stay blank) -- and never populate `ConfusableSet` without also
hand-authoring real `CompareA`/`CompareB` content in the matching shape, even if you don't
want a live Compare card (there's no supported "cf.-note-only" state; leaving Compare fields
blank triggers the legacy auto-derive fallback instead of suppressing the card).

UA_Lexeme generates a 3rd optional "Compare" card template when `ConfusableSet` is populated:

- **Front:** `CompareScenario` (a situational prompt calibrated to elicit one specific member
  of the cluster, without restating its `EN_Gloss` -- see the добре/непогано/нормально/чудово
  cluster below for why EN_Gloss alone leaks the answer for near-synonyms) plus 2-4 chips
  (`CompareA` required, `CompareB`/`CompareC`/`CompareD` optional) showing the real candidate
  words themselves, not "A or B" text.
- **Back:** Correct word (`Lemma`) + `EN_Gloss` + `Mnemonic_EN` explanation of why it fits.
- **Homograph mode:** when the note is tagged `homograph:true`, `_IsHomograph` (importer-set)
  switches the card to a different layout -- UA sentences on front, student deduces which
  sense; `Homograph_SenseA`/`Homograph_SenseB` on the back. See "Add dual-mode Compare cards"
  in git history (`f6c5127`) for the full design.
- **CompareA/B/C/D population:** for non-homograph (confusables) notes, hand-author these
  directly in the note's CNSF YAML -- do NOT rely on `compute_compare_options()` in
  `ua_lexeme_import.py` to derive them; that function only exists as a fallback for notes that
  predate the 2026-07-24 redesign and have never had CompareA/B authored. **Bug found and
  fixed 2026-07-28:** this function used to run unconditionally on every import, silently
  overwriting hand-authored CompareA/CompareB with `(Lemma, raw ConfusableSet text)` --
  ConfusableSet holds long discriminator prose, not a short chip word, so the whole paragraph
  ended up rendered as a front-side answer option (found via ua-lexeme-0022, алфавіт/абетка).
  Guard it with `already_authored = CompareA and CompareB` before calling it.
- **Empty-Compare-card safeguard (added 2026-07-28):** `CompareA` is "always required" by
  design (`CompareB`/C/D optional) -- if it's blank despite `ConfusableSet` being populated
  (e.g. a homograph note whose Compare fields were never authored), the importer suspends the
  Compare card automatically, and the template itself shows a "should be suspended" notice as
  a defensive fallback for previewing/QA. Don't rely on the notice as the primary safeguard --
  the importer suspension is what actually keeps it out of study.

**ConfusableSet format** — free-text discriminator prose, cross-linking the cluster and
explaining the actual distinction (not shown directly on the Compare card front/back; used as
the populated/blank gate for whether the card renders, and shown verbatim on `UA_EN_BACK` as
`cf. {{ConfusableSet}}`):
```yaml
ConfusableSet: |
  фах (alternative word + brief definition)
  Key distinction: explicit semantic/contextual difference between the cluster members
CompareScenario: A situational prompt whose natural answer is this note's own word
CompareA: слово1
CompareB: слово2
```

Example: професія vs. фах -- CompareScenario for професія: "Asking someone about their job
formally." CompareScenario for фах: "Discussing a plumber's expertise." CompareA/CompareB are
identical (`професія`, `фах`) on both notes -- same chip order regardless of which note it is,
matching the pattern used for every multi-note cluster (see добре/непогано/нормально/чудово
below, or відбивати/забивати/завдавати/набирати).

The "Compare" card only renders real content when `ConfusableSet` AND `CompareA` are both
populated, making it lightweight and self-suppressing when a cluster hasn't been authored yet.

**PVOM prefix drilling (multi-form typing cards)**

`UA_PVOM_Infinitive` (one note per prefix, `domains/ua/anki/notes/pvom/`) drills all four
verb-of-motion base forms a prefix combines with, as four separate card templates rather
than one card with four blanks:

- **Walking (Multi)** — multidirectional, imperfective (ходити-family)
- **Walking (Uni)** — unidirectional, perfective (іти-family)
- **Vehicle (Multi)** — multidirectional, imperfective; labeled "їздити" on the card, but
  the typed answer is the dictionary-primary **-їжджати** surface form (Горох consistently
  redirects "-їздити" entries to "-їжджати" as the canonical headword — both are real, but
  -їжджати is the one attested as primary)
- **Vehicle (Uni)** — unidirectional, perfective (їхати-family)

**Why four separate templates, not one card:** each base form gets independent FSRS
scheduling and leech tracking. The four forms are not equally hard — mutations
(apostrophe insertion: підʼїхати, відʼїхати, надʼїхати, обʼїхати, зʼїхати; epenthetic
-ій-: підійти, відійти, надійти, обійти, зійти; з→с assimilation before voiceless х:
з- + ходити → сходити, not "зходити") make some prefixes much harder to produce than
others, and a student can be solid on the walking forms while still missing vehicle
forms. Separate templates let each be suspended/re-weighted independently without
touching the others.

**Card design — no hints on the front.** Front is just `{{Prefix}} + <base label>` (e.g.
"ви + іти", "під + їздити") — no aspect labels, no mutation hints. The point is for the
student to internalize the prefixation patterns through repeated production, not to be
told the answer's shape in advance.

**Field pattern:** each base has a stressed field (`*_UA`) and an unstressed field
(`*_Typing`); the back-side script compares the reconstructed typed answer against both to
give tiered feedback (perfect-with-stress / correct-no-stress / incorrect) — see "Typing-card
design pattern for Ukrainian text" below for the full mechanics (this is the canonical
implementation the pattern was later copied from into `UA_Lexeme`, 2026-07-25).

**Typing-card design pattern for Ukrainian text (established here; UA_Lexeme's EN→UA card
fixed to match, 2026-07-25).** Any card where the student types Ukrainian and the correct
answer may carry combining stress marks (U+0301) must use this pattern — a naive
`{{type:Field}}` + `document.querySelector('input[type="text"]')` script (what `UA_Lexeme`'s
EN→UA card originally shipped with) is broken two independent ways:

1. **Anki's own native `{{type:Field}}` diff** — auto-rendered wherever `{{FrontSide}}`
   appears on the answer side — wraps every character in its own `<span>`. A combining
   stress mark rendered in isolation visually detaches from its base vowel: it looks like a
   stray apostrophe/tick mark sitting next to the letter, not an accent on top of it. (This
   is what Craig originally reported as "apostrophes... called out as their own character.")
2. **There is no live `<input>` element on the answer side.** Anki replaces it with the diff
   markup above by the time any answer-side script runs, so
   `document.querySelector('input[type="text"]')` always returns `null` — any custom
   feedback block built on that lookup silently never populates.

The fix, implemented in `tools/anki/setup/setup_ua_pvom_note_type.py` (`make_front`/
`make_back`/`FEEDBACK_SCRIPT`) and copied into `setup_ua_note_types.py`'s `EN_UA_FRONT`/
`EN_UA_BACK`:

- **Type the STRESSED field as the `{{type:...}}` target, not the unstressed one** — e.g.
  `{{type:Walking_Multi_UA}}` / `{{type:TypingTarget_UA}}` (UA_Lexeme's EN→UA card types
  `TypingTarget_UA`, not `Lemma` directly — see "EN→UA aspect+euphony typing" below for why),
  not the `*_Typing`/`TypingAnswer` field. Typing the stressed form correctly is then a clean
  exact match for Anki's diff; typing without stress becomes a clean *omission*. Both are
  well-behaved. The reverse (unstressed target, stressed *insertion*) is the case that
  produces the detached-mark artifact.
- **Reconstruct the typed answer from Anki's own `#typeans` diff** instead of a live input:
  walk `#typeans`'s child nodes, collect `.typeGood`/`.typeBad` span text content, and stop
  at `#typearrow` if present (an inexact match renders TWO lines inside `#typeans` — "what
  you typed" then a `#typearrow` separator then "the correct answer" — both reuse the same
  classes, so not stopping at the arrow doubles the reconstructed text).
- **Hide the native diff** (`typeansEl.style.display = 'none'`) and render custom tiered
  feedback (perfect-with-stress / correct-no-stress / incorrect / couldn't-determine) from
  the reconstructed text instead.
- **NFC-normalize before comparing** — the reconstructed text and the reference field values
  can differ in Unicode composition form even when visually identical (combining-diacritic
  text is sensitive to this in a way plain text isn't).

Reference this pattern for any future Ukrainian-typing card — e.g. the UA_Verb production
template noted as "design decision pending" below, if it gets built.

**EN→UA aspect+euphony typing (established as commit `a5b4a15`, 2026-07-25; reverted past
that point at some later merge/edit; restored via git archaeology 2026-07-28 -- do not
re-add the complexity described below without Craig's sign-off, it was tried once already).**

`EN_UA_FRONT` types `{{type:TypingTarget_UA}}`, not `{{type:Lemma}}`. `TypingTarget_UA` /
`TypingAnswer` are computed at sync time by `compute_typing_target()` in
`ua_lexeme_import.py` — never hand-authored — by joining `Lemma`, `ImperfectiveUnidirectional`
(if populated), and `Perfective` (if populated) with `" / "` (e.g. `ходи́ти / йти / піти́` for a
multi-imp/uni-imp/perfective triplet, or `перекида́ти / переки́нути` for an imperfective/
perfective doublet). Returns `None` (caller falls back to `Lemma` alone) when fewer than two
slots are populated — a plain singlet, or any non-verb note.

`EuphonyNote` (bare alternate spelling(s), `|`-delimited, e.g. `уболівати` as an accepted
alternate for `вболівати`) is graded as a **third genuinely-correct tier**, not a "note" and
not a lesser partial-credit outcome: `EN_UA_BACK`'s feedback script reconstructs the typed
answer from Anki's `#typeans` diff (see typing-card pattern above) and checks it against, in
order: `TypingTarget_UA` with stress → PERFECT; `TypingAnswer` (no stress) → CORRECT; a
stress-stripped match against any `EuphonyNote` alternate → CORRECT ("accepted alternate
spelling"); anything else → INCORRECT. `AspectCue` is an optional hand-authored situational
chip (styled like a Compare-card distractor) for notes where `TypingTarget_UA` is a single
aspect and it isn't otherwise obvious which reading is expected from `EN_Gloss` alone.

**Why this note exists:** on 2026-07-25, this design was redesigned (`881ac25` "Lemma_Euphony
as recognition-testing, not tolerance", then `2e93202` "split EN_UA_BACK PARTIAL tier by
stress") into something that required typing *both* the primary and euphonic form together
(`primary ; euphonic`, per aspect slot) to get full credit, via new per-slot
`Lemma_Euphony`/`ImperfectiveUnidirectional_Euphony`/`Perfective_Euphony` fields and computed
`TypingTarget_UA_Base`/`TypingAnswer_Base`/`TypingTarget_UA_AltOnly`/`TypingAnswer_AltOnly`
fields feeding a PARTIAL-credit tier. That redesign — and the aspect+euphony feature
entirely, including the simpler `a5b4a15` version — was later fully reverted on this branch
back to a bare `{{type:Lemma}}` with no `TypingTarget_UA`/`AspectCue`/`EuphonyNote` handling
at all (found 2026-07-28 while investigating why the live template didn't match `main`'s
history despite `git branch --contains` showing the redesign commits as ancestors — appears
to be a merge conflict resolution, not an explicit revert commit). If this template looks
simpler than the git history implies again in the future, check `EN_UA_FRONT`/`EN_UA_BACK`
against `git show a5b4a15:tools/anki/setup/setup_ua_note_types.py` before reintroducing
anything — that commit is the reference "it worked great" state per Craig.

**Verification caveat:** the з- prefix (схо́дити/зійти́) is the one form in this set where
Горох's dictionary entry doesn't cleanly label the aspectual pair the way it does for the
other ten prefixes — its primary listed sense is "ascend," not explicitly "get off/descend."
Treat it as slightly lower-confidence than the rest until cross-checked against the
textbook.

**Per-slot euphony tolerance + verb-phrase aspect defaulting (planned 2026-07-29,
not yet implemented -- discussed and scoped with Craig, execution deferred).**

Extends the aspect+euphony typing design above in two ways, both agreed but not
yet built:

1. **Per-slot в-/у- tolerance for UA_Lexeme.** Today `EuphonyNote`/`*_Euphony`
   companion fields (e.g. `Perfective_Euphony` on ua-lexeme-0115: увійти́ primary
   / ввійти́ euphonic) are only reliably evaluated at the single-lemma level.
   Plan: evaluate **every populated aspect slot** (`Lemma`,
   `ImperfectiveUnidirectional`, `Perfective` -- 1, 2, or 3 slots depending on the
   verb) independently, accepting **either** the в- or у- surface form in
   whichever slot has a documented alternate. Mechanically: split the
   reconstructed `#typeans` answer on the same " / " delimiter used to build
   `TypingTarget_UA`, check each slot's sub-answer against its own {primary,
   `*_Euphony` alternate} pair, and aggregate tiers across slots rather than
   diffing the whole compound string as one unit -- PERFECT only if every
   populated slot matches with correct stress (from either form); CORRECT if
   every slot matches but stress is missing somewhere; INCORRECT if any slot
   fails to match anything acceptable. Reuses the
   `Lemma_Euphony`/`ImperfectiveUnidirectional_Euphony`/`Perfective_Euphony`
   field names from the shelved 2026-07-25 redesign (`881ac25`/`2e93202`) but
   explicitly does **not** revive that redesign's requirement to type both forms
   together -- this is tolerance (accept either), not required dual production,
   matching the "it worked great" `a5b4a15` philosophy, just generalized from one
   lemma to the full aspect-slot set. `AspectCue` stays as-is, kept as a
   rarely-used escape hatch rather than folded away.
2. **Verb-phrase aspect defaulting.** For verb-phrase notes where only one
   aspect is idiomatically correct (e.g. the зробити/заробити очко́ family,
   ua-lexeme-0216/0230), rather than adding a new "aspect required" schema field
   (rejected as unnecessary corpus-wide authoring debt), default
   `TypingTarget_UA` to imperfective when a phrase note doesn't clearly call for
   perfective, and rely on well-worded `EN_Gloss` text to signal when perfective
   is specifically intended, rather than a mechanical flag. No new field --
   authoring discipline, not a schema change.

**Not yet done:** no code, no field backfill, no template changes. Planning note
only -- implementation (feedback-script rewrite in `EN_UA_BACK`,
`Lemma_Euphony`/`ImperfectiveUnidirectional_Euphony` backfill on notes with real
в-/у- alternation, gloss review pass on affected phrase notes) is deferred until
Craig gives the go-ahead to execute.

**UA→EN front aspect display (`_AspectLabel` + `TypingTarget_UA` reuse, added
2026-07-31, synced).** Per Craig: when a verb note's aspect set has more than one
populated slot, the Recognition-card (`UA_EN_FRONT`) lemma line should show every
populated slot — same as the EN→UA typing target — separated by slashes, all in one
font, no per-slot styling differences. When only one slot is populated (a true
singlet), show a small `(pf.)`/`(impf.)` tag next to the word instead, since there's
no slash-joined set to make the aspect visually obvious.

Reuses `TypingTarget_UA` (already computed by `compute_typing_target()` for the EN→UA
card, see above) rather than adding a second independently-authored join — one
source of truth for "what does this note's aspect set look like joined." New
`_AspectLabel` computed field (added to `FIELDS` in `setup_ua_note_types.py`, set in
`import_note()` in `ua_lexeme_import.py`) fires only for the true-singlet case (both
`ImperfectiveUnidirectional` and `Perfective` blank) — doublets/triplets never get a
label, since the slash-joined `TypingTarget_UA` already shows the aspectual range and
a tag would be redundant. Aspect for the singlet case follows the same schema
convention `compute_typing_target()`'s docstring and this doc's "Aspect-only tags"
section already define: `Lemma` is imperfective by default unless the note carries
`aspect:perfective-only` (hand-applied by Craig only, never by scripts) — so an
untagged singlet is correctly labeled `(impf.)`, not left uninferred.

Example front-line output for various configurations:
```
Triplet (multi/uni/perf populated):
  ходи́ти / йти / піти́

Doublet (impf/perf populated):
  перекида́ти / переки́нути

Singlet, untagged (imperfective by schema default):
  ма́ти (impf.)

Singlet, tagged aspect:perfective-only:
  зустрі́ти (pf.)
```

`UA_EN_FRONT`'s lemma line:
```html
<div class="lemma">{{TypingTarget_UA}}{{#_AspectLabel}} <span class="aspect-label">{{_AspectLabel}}</span>{{/_AspectLabel}}</div>
```

New CSS rule (`.aspect-label`, plain-CSS for now — see the Solarized item under
"Pending / Next planned work" above for why this isn't Solarized-colored yet):
```css
.aspect-label {
  font-size: 16px;
  font-weight: normal;
  color: #888;
}
```

Note: there's a pre-existing, unused `.perfective` CSS class in `UA_Lexeme`'s CSS
(orphaned — no current template references it) — left untouched, but flagged as a
landmine if anyone ever reactivates it, since it predates and is unrelated to
`.aspect-label`.

**Cloze note design principles (UA_Grammar, established 2026-07-22)**

- **Atomicity:** each distinct cloze number (`{{c1::}}`, `{{c2::}}`, ...) should test exactly
  one isolated fact. Reusing the same cloze number for multiple unrelated facts in one note
  (the pattern in `ua-grammar-0001`–`0007`) makes a single card "busy" — it forces recall of
  several things at once instead of one clean fact.
- **No self-leak:** nothing outside a cloze span may name the answer being tested inside that
  span. Concrete examples belong in `Extra` (back-side only), not in `Text` next to the
  cloze — a parenthetical like "(зайти до друга)" sitting outside a
  `{{c1::до + genitive}}` span gives the answer away on the very card testing it.
- **No cross-cloze substring leak:** one cloze's answer text must not be a literal substring
  of another cloze's visible answer text on the same note (e.g. "зі" as its own cloze target
  when "з/із/зі" is also shown plainly elsewhere on the card).
- **Don't pad to hit a card-count target.** Atomicity means one card per fact that earns
  independent recall, not maximizing cloze numbers — see `ua-grammar-0009`, trimmed from an
  initial 4-fact draft down to 2 after the extra facts turned out to be low-value trivia.
- **Cloze cards aren't retroactively deleted when a `{{cN::}}` tag is removed from Text.**
  If a stale extra card persists after trimming a note's cloze count, delete the note in
  Anki and let the next sync recreate it with the correct card count — this is expected
  Anki behavior, not a bug to chase.

### Language conventions (critical)
- Dialect: modern Ukrainian, **Galician/Lviv** register
- Apostrophe: **U+02BC `ʼ`** — never ASCII `'`
- Stress marks: **never guess** — verify against Горох (goroh.pp.ua) via Claude in Chrome.
  Tag unverified with `stress:unverified`. Remove tag only after Горох confirms.
- Stress disambiguation: some words have stress-dependent meanings (e.g. му́зика = music,
  музи́ка = musician). Always check before "correcting" based on Горох alone.
- **Two accent marks on one word is valid Горох output** — it means the word has free/variant
  stress (either syllable may be stressed). Do NOT treat this as an extraction bug or garbled
  data; do NOT collapse it to a single mark when transcribing. Record both marks in the Lemma
  field as Горох shows them.
- **Data-quality priority: a multisyllable word with ZERO stress marks is a stronger red flag
  than one with two.** Double-stress is a legitimate linguistic outcome (see above); a missing
  stress mark on a multisyllable lemma is not — that's the pattern that indicates a real
  extraction bug (wrong homograph block, failed fetch, stripped markup) and should block on
  re-verification before the note is trusted.
- `сь` after vowels preferred (дивлюсь, вчусь) — preserve unless correcting
- Grammar explanations always in English

### Stress verification workflow (established)

Горох Словозміна (`goroh.pp.ua/Словозміна/<word>`) returns the full inflection paradigm
with stress marks. Accessible via Claude in Chrome (not via web_fetch — blocked).

Batch verification process:
1. Extract lemmas from notes (Python, strip stress to get bare form)
2. Fetch Горох pages in batch via Chrome JS `Promise.all` (30 at a time to avoid truncation)
3. Strip phonetic markers from Горох output: remove `<sup>...</sup>` WITH content,
   backtick, apostrophe, colons, `{дз}`/`{дж}` → keep content, `ў` stays as non-vowel
4. Compare vowel-index of stress in lemma vs Горох form; flag mismatches
5. Apply corrections; keep `stress:unverified` tag until user confirms

Important: Горох returns the **masculine adjective** form for adjectives (e.g. `-ський`
instead of `-ська`). The vowel-index comparison handles this correctly since the stressed
syllable is the same. The script is embedded in session context — rebuild from the pattern
in `tools/anki/inspect/` when needed as a standalone tool.

### Vocabulary dedup & homograph handling (established 2026-07-23, outcome 4 added 2026-07-24)

As chapter-by-chapter sourcing continues, every new candidate word falls into one of four
buckets. Triage deliberately — do not assume from spelling alone.

1. **Brand new vocabulary.** No existing note has this spelling. Default behavior: Горох-
   verify, create a new `ua-lexeme-NNNN` note per the standard process.

2. **Homograph — same spelling, unrelated meaning** (e.g. EN "blue" the color vs "blue" the
   mood; ГА "коса" braid / scythe / spit-of-land). Горох itself already surfaces this as
   separate `.article-block` entries under distinct H2 labels on the same Словозміна page —
   this is the same multi-homograph-page pattern the "біг"/"Бог" extraction bug taught us to
   handle correctly (match the H2 label text, don't grab the first table). Handling:
     - Create a normal new note (own NoteID/file) — do not merge into the existing one.
     - Cross-link both notes via `ConfusableSet`, explicitly stating "homograph — unrelated
       meaning" plus both glosses, matching the pattern used for алфавіт/абетка (ua-lexeme-
       0022/0023 — note that pair is near-synonyms, not true homographs, but the field
       mechanics are identical).
     - Tag both notes `homograph:true` so the set is queryable later (e.g. for a dedicated
       homograph-review pass or card set).
     - Write `UA_Example` sentences where surrounding context makes the intended sense
       unambiguous.
     - **Done, as of 2026-07-30.** Extended the `Mnemonic_EN`/`CompareA`/`CompareB` fields +
       Comparison card template (originally built for про-/пере- prefix pairs) to lexical
       homographs generally — Shape-1 mode (`_IsHomograph`-driven: UA sentences on front,
       `Homograph_SenseA`/`SenseB` on back) is live for every `homograph:true` pair in the
       corpus. Confirmed via the 2026-07-30 corpus-wide Compare-card sweep (579 notes) — see
       [CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md) — that тепло
       (ua-lexeme-0405/0407) was the only pair still missing this content; now fixed.

3. **True duplicate — same spelling AND same meaning**, encountered again in a later
   chapter. Do NOT create a new note. Instead:
     - Append the new `ch:2.9.X` tag to the note's `tags` list.
     - Append the new chapter to `Tags_Ch` (comma-separated, e.g. `"ch:2.9.1, ch:2.9.2"`).
     - Append a short dated note to `Verification Notes` documenting the reuse.
   This is the exact pattern already used for перегони (ua-lexeme-0144, reused across
   9.1/9.2) — now the standard procedure rather than ad hoc.

4. **Convergent synonyms — multiple UA spellings, overlapping EN gloss** (established
   2026-07-24, Craig). Different spelling from bucket 2/3 (which are keyed on the *same* UA
   spelling) — this bucket catches the opposite drift: several distinct UA words whose
   `EN_Gloss` values overlap enough that the semantic distinction between them gets lost.
   E.g. пожежа/ватра/вогонь all glossing loosely to "fire" in EN, or (found in the
   2026-07-24 audit) добре/непогано/нормально/чудово all glossing to some flavor of
   "good/fine." This is **not spelling-based** and not mechanically detectable — it requires
   reading the whole `EN_Gloss` list and clustering by judgment (semantic, not keyword
   matching). Handling: cross-link the cluster via `ConfusableSet` with scenario-based
   discrimination (same field/format as bucket 2), explaining the actual distinction (e.g. a
   register/enthusiasm scale, or a broader-vs-narrower relationship) rather than tagging
   `homograph:true` (these are related-but-distinct words, not homographs). Run as a
   standalone full-corpus audit periodically, not per-candidate at generation time — see
   [CLAUDE-dedup-homograph-audit.md](CLAUDE-dedup-homograph-audit.md).

   Another cluster type worth naming: not a scale (like добре/непогано/нормально/чудово) but
   **distinct roles sharing one rough EN gloss** — found 2026-07-28, Craig struggling to keep
   verb roots straight (prefixes were fine): відбивати/забивати/завдавати/набирати
   (ua-lexeme-0213/0214/0215/0218), all "ball/impact-game action" verbs that gloss loosely to
   "hit/score" but each answers a different question about where the force ends up
   (відбивати = deflect an incoming ball, defense; забивати = drive the ball into a goal,
   offense; завдавати = land a blow on a person, combat, not a ball at all; набирати = the
   scoreboard number increasing, bookkeeping, no physical trajectory). `ConfusableSet` +
   `Mnemonic_EN` frame this as "roles," not a graded scale; `CompareA`-`CompareD` are the
   same four stressed verbs in the same order on all four notes. Root-level confusion like
   this (as opposed to prefix confusion, which `UA_PVOM_Infinitive` already drills) doesn't
   have a dedicated drill mechanism elsewhere in the corpus, so the Compare card is it — worth
   watching for other root clusters as ch-09+ sourcing continues. `status:verified` kept on
   all four; `Verification Notes` flags the new Compare content "Needs your review" per the
   standing convention (see добре/непогано/нормально/чудово below for the same pattern).

5. **Pending confusable-set watchlist** (added 2026-07-30, Craig, during Ch-08 verification).
   Craig frequently knows a note's future confusable-set partner before that partner word has
   been sourced (e.g. "0463 рух will be in a confusable set with затор" while затор doesn't
   have its own note yet). Rather than relying on memory across sessions, tag the *existing*
   note with `pending-confusable:<bare-spelling>` (stress marks optional — matching is always
   stress-stripped, same rule as bucket 1-4 tooling). `tools/anki/inspect/check_pending_confusables.py`
   (wired into `make ua-check`) scans the whole corpus for these tags and reports when the
   target spelling now exists as its own note, so it can be linked into a proper ConfusableSet
   the same session it's sourced instead of being rediscovered later. The script only detects
   the match — a human (or Claude) still writes the actual `ConfusableSet`/`Mnemonic_EN`/
   `CompareScenario`/`CompareA-D` content once it fires, same division of labor as the
   dedup-check tooling in buckets 1-3. For an open-ended same-root/different-prefix family with
   no single known target spelling (e.g. ua-lexeme-0321 перепрошувати eventually clustering
   with other -прошувати/-просити forms), use the pre-existing generic `needs-confusable-set`
   tag instead (see ua-lexeme-0436/0440) — `check_pending_confusables.py` reports a plain count
   of these as a reminder but doesn't try to resolve them.

**Tooling:**
- `tools/anki/inspect/check_lexeme_dedup.py` — given one or more candidate
  lemmas, stress-strips them (NFD/NFC method) and recursively scans every `ua-lexeme-*.md`
  under `domains/ua/anki/notes/lexemes/` for an exact-spelling match. Reports NoteID, file
  path, current `EN_Gloss`, and `Tags_Ch` for any match, so the new/homograph/duplicate call
  gets made deliberately instead of by ad hoc grep (which produced false negatives earlier
  in this project — see the перегони/перемогти́/програ́ти dedup-check history). Meaning
  comparison (bucket 2 vs. 3) still requires human/Горох judgment — the tool only automates
  the "does this spelling already exist" lookup reliably. Manual, per-candidate, run before
  drafting a batch.
- `tools/anki/lib/lexeme_dedup.py` (new 2026-07-24) — the same spelling-match logic
  packaged as an importable library (`create_or_link_lexeme()`), plus the write-side
  handling for all three spelling-keyed buckets (new/homograph/duplicate): creates the new
  note, or appends the chapter tag + dated verification note to an existing one, or
  cross-links both notes' `ConfusableSet` fields for a homograph pair.
- `tools/anki/extract/gen_ch09_subsection.py` (new 2026-07-25) — the actual generator
  script item 0 called for: takes a batch of already-drafted candidates (lemma, fields,
  and an explicit dedup decision) and routes every one through `create_or_link_lexeme()`
  before it touches disk. Does not automate the Горох verification, phrase/component
  decomposition, or the new-vs-duplicate-vs-homograph judgment call itself — those stay
  human/Claude-in-Chrome-driven per CLAUDE-ch09-vocab-workflow.md — it only guarantees no
  candidate can reach the corpus by a hand-written-file path that skips the check. Not yet
  exercised against a real ch.9.3+ batch.
- `tools/anki/inspect/build_lexeme_index.py` (new 2026-07-24) — dumps the full lexeme
  corpus to `build/ua_lexeme_index.tsv` (gitignored) in one pass, for the bucket-4
  full-corpus audit and for spot-checking bucket-1/2/3 spelling collisions at scale without
  hitting per-file staging rate limits.
- `tools/anki/inspect/check_pending_confusables.py` (new 2026-07-30) — the bucket-5
  watchlist checker: scans for `pending-confusable:<lemma>` tags and reports when the target
  spelling now exists as its own note, reusing `tools/anki/lib/lexeme_dedup.py`'s
  `load_corpus()`/`strip_stress()` rather than a fourth reimplementation of the same
  spelling-match logic. Wired into `make ua-check`.
- `tools/anki/inspect/audit_verb_aspect_forms.py` (new 2026-07-27, extended 2026-07-30) —
  flags `pos:verb` notes with zero populated aspectual counterparts (`ImperfectiveUnidirectional`
  and `Perfective` both blank) and no `aspect:imperfective-only`/`aspect:perfective-only` tag.
  Never applies either tag itself — see "Aspect-only tags" above. Wired into `make ua-check`.

### Deck Presets and Limit Configuration (2026-07-20)

**Strategy:** Differentiated daily limits by cognitive load tier + data-driven preset creation.

**Preset configuration files:**
- `domains/ua/anki/presets/preset_definitions.json` — UA domain presets (6 presets: parent + 5 child tiers)
- `domains/b737/anki/presets/preset_definitions.json` — B737 domain preset (1 preset: review-only)

**Limit configuration files:**
- `domains/ua/anki/config/deck_limits.yaml` — UA domain limit strategy with commentary
- `domains/b737/anki/config/deck_limits.yaml` — B737 domain limit strategy with role-based suspension

**Key concepts:**
- **Parent limit:** 50 new / 100 review per day (UA domain). Child decks cannot exceed this.
- **Cognitive load tiers:**
  - High (PVOM, Lexeme EN→UA): 15–18 new/day (typing/production)
  - Medium (Grammar, Verbs): 20 new/day (recognition + recall)
  - Low (Visual): 25 new/day (recognition)
- **Total child capacity:** 98 new/day (98 > 50 parent), but balanced by selective activation
- **B737 limits:** 0 new / 200 review (review-only, no new cards for type-rating study)
- **Suspension tagging:** Decks suspended with tags documenting reason (role:captain, scope:out-of-scope, etc.)

**Preset creation workflow:**
1. `tools/anki/setup/create_deck_presets.py` — Reads JSON preset definitions, creates/updates presets via AnkiConnect
2. `tools/anki/inspect/update_deck_limits.py` — Reads YAML limits, updates existing deck configs, applies to UA decks
3. `tools/anki/inspect/update_b737_deck_limits.py` — Same pattern for B737 (honors suspension flags)

**Execution order (Craig runs these):**
```bash
python tools/anki/setup/create_deck_presets.py      # Create all presets
python tools/anki/inspect/update_deck_limits.py     # Apply UA limits
python tools/anki/inspect/update_b737_deck_limits.py # Apply B737 limits
```

### Tooling status
| Path | Status | Purpose |
|---|---|---|
| Rename `UA` → `UA_Legacy` in Anki GUI | ✓ done | One-time manual rename; frees UA:: namespace |
| `tools/anki/setup/setup_ua_note_types.py` | ✓ done | Creates/updates UA_Lexeme + UA_Grammar + UA_Visual |
| `tools/anki/setup/create_deck_presets.py` | ✓ new (2026-07-20) | Data-driven preset creation from JSON definitions |
| `tools/anki/sync/ua_lexeme_import.py` | ✓ done | CNSF notes → Anki via AnkiConnect (upsert) |
| `tools/anki/sync/ua_grammar_import.py` | ✓ done | UA_Grammar CNSF notes → Anki (upsert) |
| `tools/anki/sync/ua_visual_import.py` | ✓ done | UA_Visual CNSF notes → Anki (upsert) |
| `tools/anki/extract/gen_ua_lexemes_vstup.py` | ✓ done | One-shot generator for Вступ batch |
| `tools/anki/inspect/update_deck_limits.py` | ✓ new (2026-07-20) | Apply UA domain limits from YAML config |
| `tools/anki/inspect/update_b737_deck_limits.py` | ✓ new (2026-07-20) | Apply B737 domain limits, honor suspension tags |
| `tools/anki/inspect/backfill_source_url.py` | ✓ done | Add Source_URL + Source_Note to all lexeme notes |
| `tools/anki/inspect/verify_stress_goroh.py` | ✓ done | Stress verification vs Горох; Вступ pass complete |
| `tools/anki/inspect/test_preset_creation.py` | ✓ new (2026-07-20) | Diagnostic tool for testing preset creation approaches |
| `tools/anki/generate/ua_generate_examples.py` | ✓ done | Populate UA_Example/EN_Example via Anthropic API |
| `tools/anki/inspect/patch_ch09_conj_tables.py` | ✓ done | One-shot: Verb_Conj_Table for notes 0117–0131 |
| `tools/anki/lib/lexeme_dedup.py` | ✓ new (2026-07-24) | `create_or_link_lexeme()` — dedup/homograph create-or-link API (new/homograph/duplicate) |
| `tools/anki/inspect/build_lexeme_index.py` | ✓ new (2026-07-24) | Full-corpus lexeme → `build/ua_lexeme_index.tsv` dump for audits |
| `tools/anki/extract/gen_ch09_subsection.py` | ✓ new (2026-07-25) | Ch-09 batch driver wiring `create_or_link_lexeme()` into note generation (CLAUDE.md item 0); not yet used on a real batch |
| `tools/anki/inspect/audit_verb_aspect_forms.py` | ✓ new (2026-07-27), extended (2026-07-30) | Flag verb notes with zero aspectual counterparts and no `aspect:*-only` tag; wired into `make ua-check` |
| `tools/anki/inspect/check_pending_confusables.py` | ✓ new (2026-07-30) | Bucket-5 watchlist: report when a `pending-confusable:<lemma>` tag's target now exists in the corpus; wired into `make ua-check` |
| `tools/anki/export/ua_lexeme_md_to_tsv.py` | not written | Canonical notes → TSV (if needed) |
| `tools/anki/extract/export_ua_legacy.py` | not written | Pull existing Anki cards → CNSF skeletons |

### UA_Verb Note Type (Phase 2a, committed 2026-07-12)

**Design:** See [CLAUDE-ua-verb-design.md](CLAUDE-ua-verb-design.md) for complete specification.

**Implementation status (2026-07-12):**
- ✅ UA_Verb note type created in Anki (27 fields: identity, present 6, imperatives 3, past 4, participles 6, metadata)
- ✅ Recognition card template deployed (collapsible details for imperatives, past, participles)
- ✅ ua_verb_import.py + `make ua-verb` target operational
- ✅ 2 base motion verbs authored & imported (ходити ua-verb-0001, їхати ua-verb-0002) — Горох verified
- ✅ ua_verb_export.py created; 69 legacy UA_Verb + 5 UA_Conjugation exported to CNSF, canonicalized
- ⏳ Production template (randomized conjugation drilling): design decision pending

**Key principles:**
- **Separate morphology from vocabulary.** One UA_Verb note (ходити) serves multiple lexemes (ходити, походити, заходити, etc.) via tag linking, not 1:1 coupling.
- **Structured fields, not HTML.** 26 fields store individual conjugation forms (6 pronouns, 3 imperatives, 4 past, 6 participles) + metadata. Templates render as tables. HTML is generated cache, not canonical.
- **CNSF canonical format.** All UA_Verb notes version-controlled as markdown with YAML front matter, imported via AnkiConnect.
- **Tag-based linking.** UA_Lexeme and UA_Verb share tags (e.g., `conj:motion-walking-ходити`) for bidirectional reference without foreign keys.
- **Suspended by default, unsuspend selectively.** Import with `conj:suspended` tag; unsuspend class leaders + irregulars tagged `conj:drill` (~90–100 cards active).

**Phase 2a execution plan (12 steps, in progress 2026-07-13):**
1. ✅ Create `ua_verb_export.py` — Export 69 existing UA_Verb + 5 UA_Conjugation notes to CNSF (backup + version control)
2. ✅ Export all legacy notes to canonical .md files in `domains/ua/anki/notes/verbs/exported/` — 74 notes canonicalized, ready for migration
3. ✅ Build & test Recognition card template for ходити/їхати — Card template designed with block-based layout:
   - **Present tense:** 2-column grid (я/ми, ти/ви, він,вона,воно/вони)
   - **Past tense:** Full-width 4 rows (ч.р., ж.р., с.р., мн.)
   - **Imperative:** Full-width 3 rows (ти, ми, ви)
   - **Participles:** Collapsible section (Act. Pres., Adv. Pres., Pass. Past m/f, Impersonal, Adv. Past)
   - Both ua-verb-0001 (ходити) and ua-verb-0002 (їздити) synced to Anki with correct conjugation data. Template deployed via setup_ua_note_types.py. Created survey_ua_verb.py tool for card verification.
4. Design decision: Production template needed (randomized conjugation drilling) or recognition-only sufficient?
5. Finish ch-09 verbs (Phase 2a) — target 35–50 canonical CNSF notes:
   - **Prefixed motion verbs** (10–14): походити, заходити, виходити, перейходити (ходити base); поїхати, заїхати, виїхати (їхати base). Tag: `conj:motion-walking-ходити` / `conj:motion-vehicle-їхати`
   - **Class leaders** (5–10): писати, читати, казати, робити, жити, говорити, слухати, гуляти, хотіти, etc. Tag: `class:leader, phase:2a, conj:drill`
   - **Irregulars** (8–12): бути, дати/давати, їсти/з'їсти, брати/взяти, ставати/стати, лежати/лягти, сідіти/сісти, etc. Tag: `class:irregular, phase:2a, conj:drill`
6. Create `ua_conjugation_to_verb.py` migration script — Automate 5 UA_Conjugation → UA_Verb CNSF conversion (field mapping: Pres_1S→Pres_1sg, ActPart_Pres→Participle_Active_Present, Gerund→Participle_Adverbial)
7. Run migration — Generate CNSF files in `domains/ua/anki/notes/verbs/migrated/`
8. Field-coverage audit — Compare old vs new structure; flag data loss before sync
9. Verify tags & metadata — Standardize legacy tags to new scheme (phase:2a, conj:drill, conj:suspended)
10. Stage sync in batches:
    - Batch A: 2 new verbs (ходити, їхати) ✓ complete
    - Batch B: New Phase 2a verbs (prefixed, class leaders, irregulars)
    - Batch C: 69 legacy UA_Verb reimported from exported CNSF
    - Batch D: 5 migrated UA_Conjugation → UA_Verb format
11. Final QA — Spot-check in Anki: verify conjugations, tags, deck placement
12. Update CLAUDE.md — Document completion, tools, tagging conventions

**CNSF canonicalization note (2026-07-13):**
- UA_Verb notes use `Verification_Notes` (underscore) not `Verification Notes` (space). The canonicalizer (`tools/anki/cnsf_canonicalize.py`) has been fixed to remove the space variant when processing ua_verb note_type. This prevents duplicate fields in canonical files.

**Participles policy:**
- **Adverbial past participle** (е.g., робивши) — *required*; useful for reading comprehension
- **Passive participle** (e.g., робленный) — *optional*; include if standard/common, else blank

**Future tense — deliberately not a stored field (decided 2026-08-04, per Craig).** Horox's
Словозміна pages show a distinct synthetic future for imperfective verbs (e.g. плисти́ →
плисти́му/плисти́меш/плисти́ме/плисти́мем,плисти́мемо/плисти́мете/плисти́муть) that `UA_Verb`
has never had a field for. Confirmed intentional, not a gap: formation is close to 100%
procedural (infinitive stem + му/меш/еш/etc.) for any imperfective verb, so it doesn't need
per-verb storage or drilling the way genuinely irregular forms (present/imperative/past)
do. Don't add a `Future`/`Fut_*` field family without Craig revisiting this decision.

**UA_Verb sequencing** — *501 Ukrainian Verbs* (book) used as breadth/coverage map, not a to-do list.

- **Phase 2a** — Implement UA_Verb note type; author class leaders + irregulars (~60–70 notes). These are structural skeletons of Ukrainian conjugation.
- **Phase 2b** — High-frequency regulars (~60–100 additional notes) from Яблуко + Ukrainian National Corpus frequency list.
- **Phase 2c (ongoing)** — Expand via *501 Ukrainian Verbs* as curriculum demands. Target total: ~160–220 authored notes, ~90–100 marked for active drill.
- **Prefixed verb variants** inherit base conjugation via tag linking; no separate conjugation notes per prefix.

**LLM example sentence generation** — `tools/anki/generate/ua_generate_examples.py` ✓ written.
Run with `make ua-generate-examples BATCH=yabluko-l1/ch-00 [LIMIT=10]`.
Requires `ANTHROPIC_API_KEY` env var and `pip install anthropic`.
Generated examples tagged `example:generated` until reviewed; then remove tag.

Alternative: **extract examples from the Яблуко textbook PDF directly** — higher
authenticity than generated examples and no hallucination risk. The Level 1 PDF is
at `domains/ua/anki/sources/yabluko/level-1/`. Would require OCR/extraction tooling
and per-lemma lookup; feasible as a future enrichment pass to replace or supplement
generated examples.

**Unit 1–12 lexeme generation** — follow the pattern of `gen_ua_lexemes_vstup.py`,
extracting vocab from Яблуко appendix pages 220–237 unit by unit.

**Legacy card migration** — write `export_ua_legacy.py` to pull existing Basic/Cloze
cards from Anki and generate CNSF skeletons. Enrich with PoS, gender, stress marks
before re-importing. Priority: `to_convert` tagged (13) → Shevchuk → Яблуко ch-by-ch.

**EN translation variant guidance** — When developing UA_Lexeme cards, for English words with multiple UA translations, provide the literal EN translation in addition to the common meaning. This helps learners understand why a single English word might map to different Ukrainian equivalents, showing semantic nuance rather than just glosses.

### Flagged Card Fix Workflow (Future)

**Purpose:** Periodic review and correction of flagged cards (red=errors, orange=confusing).
After each study session, fix all flagged cards and remove flags.

**Workflow:**
1. Query Anki for flagged cards in UA domain → extract NoteIDs
2. For each flagged NoteID:
   - Read canonical CNSF file from repo
   - Show to Claude: full note (fields)
   - Claude asks: "Why flagged?" (with flag color context)
   - You respond with issue/fix
   - Claude suggests if unclear
   - Update CNSF file with correction
3. Batch re-import corrected notes to Anki (via `ua_lexeme_import.py`, `ua_verb_import.py`, etc.)
4. Remove flags from all cards in one query
5. Commit corrected CNSF files to git

**Tools needed:**
- `ua_flag_audit.py` — Query flagged cards, extract NoteIDs, map to canonical file paths
- Integration with existing import scripts (ua_lexeme_import.py, ua_verb_import.py, ua_grammar_import.py, ua_visual_import.py)

**Status:** Phase 1 (`--query`) and Phase 3 (`--apply`) tooling built and tested,
2026-08-01 -- see item 8 in the structural punch list above and
`tools/anki/inspect/ua_flag_audit.py`. Phase 2 (interactive review/fix) is ready to use
whenever Craig wants to work through the current 11 flagged notes.

### Source materials
| Path | Purpose |
|---|---|
| `domains/ua/anki/sources/yabluko/level-1/` | Яблуко Level 1 PDF (good copy available) |
| `domains/ua/anki/sources/yabluko/level-2/` | Яблуко Level 2 OCR'd excerpts: `yabluko-l2-vocabulary.pdf`, `yabluko-l2-grammar-guide.pdf`, `yabluko-l2-verb-dictionary.pdf` |
| `domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/` | 113 ua_lexeme notes — Вступ (= ch-00) |
| `domains/ua/anki/notes/grammar/` | ua_grammar canonical notes (not yet populated) |
| `domains/ua/anki/docs/design.md` | Full schema, deck architecture, migration plan |
| `tools/anki/inspect/survey_ukrainian.py` | AnkiConnect survey script |
