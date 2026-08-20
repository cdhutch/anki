#!/usr/bin/env python3
"""Create or update UA note types in Anki via AnkiConnect.

Note types: UA_Lexeme, UA_Grammar, UA_Visual, UA_Verb

If a model does not exist: creates it with all fields, card templates, and CSS.
If a model already exists: updates templates and CSS; syncs fields (adds missing,
removes obsolete). Existing data in removed fields is discarded.

Usage (with Anki open + AnkiConnect running):
    python tools/anki/setup/setup_ua_note_types.py              # all four models
    python tools/anki/setup/setup_ua_note_types.py --model UA_Lexeme
    python tools/anki/setup/setup_ua_note_types.py --model UA_Grammar
    python tools/anki/setup/setup_ua_note_types.py --model UA_Visual
    python tools/anki/setup/setup_ua_note_types.py --model UA_Verb
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.anki.lib.typeans_js import NORMALIZE_TYPEANS_JS  # noqa: E402
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

# ---------------------------------------------------------------------------
# Fields (order matters — Anki displays them in this order in the editor)
# ---------------------------------------------------------------------------

FIELDS = [
    # -- 1. Identity ---------------------------------------------------------
    "NoteID",

    # -- 2. Core lemma & aspect (hand-authored) ------------------------------
    # Ordered Lemma -> ImperfectiveUnidirectional -> Perfective, matching the
    # multi-imp -> uni-imp -> perfective progression that compute_typing_target()
    # / compute_euphony_slots() / compute_ua_en_display() all join in. Before
    # 2026-08-18 this constant listed Perfective *before*
    # ImperfectiveUnidirectional, so the editor's field order disagreed with the
    # slot order every computed join and the EN_UA_BACK feedback script use.
    "Lemma",

    # Lemma_Euphony: hand-authored, optional. в-/у- (or similar) phonological
    # alternate spelling of Lemma itself, e.g. "уболіва́ти" alongside Lemma
    # "вболіва́ти". Per-slot companion to Lemma -- see
    # ImperfectiveUnidirectional_Euphony/Perfective_Euphony below for the
    # other two aspect slots. Added 2026-08-04 (per-slot euphony tolerance +
    # display, CLAUDE.md "Per-slot euphony tolerance"); the field key itself
    # already existed in several CNSF source files from a 2026-07-26 corpus
    # survey but was never wired into the model/import script until now.
    "Lemma_Euphony",
    "PartOfSpeech",
    "Gender",
    "ImperfectiveUnidirectional",  # Motion verbs: іти, їхати (directional IPFV)
    "ImperfectiveUnidirectional_Euphony",  # per-slot euphonic alternate for ImperfectiveUnidirectional
    "Perfective",
    "Perfective_Euphony",  # per-slot euphonic alternate for Perfective, e.g. увійти́ / ввійти́

    # EuphonyNote: free-text descriptive note (bare alternate spelling(s) or
    # explanatory prose). As of 2026-08-04, no longer the primary source for
    # EN->UA typing-tolerance on multi-slot (doublet/triplet) verb notes --
    # that's now driven per-slot by Lemma_Euphony/
    # ImperfectiveUnidirectional_Euphony/Perfective_Euphony (see
    # _EuphonySlots below). Still used as a fallback for true singlet notes
    # authored before the per-slot fields existed -- see
    # compute_euphony_slots() in ua_lexeme_import.py.
    # Grouped here (2026-08-18) next to the three per-slot *_Euphony fields it
    # is the legacy whole-note ancestor of, rather than down by the typing
    # fields where it used to sit -- the relationship is what makes it
    # readable.
    "EuphonyNote",

    # AspectCue: hand-authored, optional. For a verb/phrase note that types
    # only ONE aspect (no populated Perfective/ImperfectiveUnidirectional, so
    # TypingTarget_UA is just Lemma), a short situational question framing
    # which aspect reading is expected -- e.g. ongoing/habitual vs a single
    # completed event. Absent where not applicable (doublet/triplet notes
    # where TypingTarget_UA already asks for every aspect at once don't need
    # it). Restored 2026-07-28 (git archaeology, commit a5b4a15) -- see
    # EN_UA_FRONT below for how it renders.
    "AspectCue",

    # -- 3. Computed / display-only ------------------------------------------
    # Populated by ua_lexeme_import.py at sync time, NEVER hand-authored in
    # CNSF. Grouped together (2026-08-18) so the editor makes the
    # authored-vs-derived split obvious at a glance; previously these were
    # scattered through the authored fields. The underscore prefix is the
    # naming convention that marks them. NOTE: TypingTarget_UA/TypingAnswer/
    # _EuphonySlots are computed too, but live in group 7 below -- they have
    # to stay adjacent to each other because they are positionally aligned
    # (same " / " slot join), and reading them apart invites exactly the kind
    # of misalignment bug this schema keeps producing.
    "_AspectLabel",  # "(pf.)"/"(impf.)" for a true aspectual singlet; blank otherwise
    "_UA_EN_DisplayLemma",  # UA->EN front join, euphonic alternates inline in parens
    "_IsHomograph",  # "1" when the note carries the homograph:true tag

    # -- 4. Semantic content --------------------------------------------------
    "EN_Gloss",

    # -- 5. Grammatical properties -------------------------------------------
    "Govt_Case",
    "IrregularForms",
    "CounterpartForm",
    "VerbMotion_Pair",

    # -- 6. Semantic relations & Compare card --------------------------------
    "ConfusableSet",
    "Mnemonic_EN",
    "CompareScenario",
    "CompareA",
    "CompareB",
    "CompareC",
    "CompareD",
    "Homograph_SenseA",  # EN sense for CompareA (homographs only)
    "Homograph_SenseB",  # EN sense for CompareB (homographs only)
    "CrossLang_Analog",

    # -- 7. Typing & examples -------------------------------------------------
    # TypingTarget_UA / TypingAnswer / _TypingSpec are read together by the
    # EN->UA grading script. They are no longer positionally coupled the way
    # TypingTarget_UA/_EuphonySlots were (see _TypingSpec below), but keeping
    # them adjacent still matches how they're reasoned about.
    #
    # TypingTarget_UA: the EN->UA typing target. For verb notes with a
    # populated ImperfectiveUnidirectional and/or Perfective, this is the full
    # stressed aspect join (e.g. "ходи́ти / йти / піти́"), computed at sync
    # time -- see compute_typing_target() in ua_lexeme_import.py. Never
    # hand-authored. Restored 2026-07-28 (git archaeology, commit a5b4a15).
    "TypingTarget_UA",
    "TypingAnswer",

    # _TypingSpec: Internal marker, populated by import script (never
    # hand-authored). Compact JSON, one object per populated aspect slot:
    # {"slots":[{"primary":"вхо́дити","alts":["ухо́дити"]},...]}, same slot
    # order as TypingTarget_UA. Drives the EN->UA card's answer-side grading
    # (see compute_typing_spec() in ua_lexeme_import.py and EN_UA_BACK below).
    #
    # Added 2026-08-19, REPLACING _EuphonySlots. That field was a second
    # " / "-joined string required to stay index-aligned with TypingTarget_UA
    # by convention alone -- nothing enforced it, and nothing could detect a
    # break. Alternates here are stored STRESSED (the old field's consumer
    # stripped stress from both sides, which is why a fully-stressed euphonic
    # alternate could never reach PERFECT). See
    # docs/ua-en-ua-euphony-aspect-refactor.md.
    "_TypingSpec",
    "UA_Example",
    "EN_Example",

    # -- 8. Metadata & sources ------------------------------------------------
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
    "Verification Notes",  # stale in this constant until 2026-08-11 -- the live
    # UA_Lexeme model has always had this field; ua_lexeme_import.py passes CNSF
    # fields through unfiltered, so sync already worked, this constant just
    # never listed it (see CLAUDE-flag-audit.md).
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* Gruvbox palette (github.com/morhetz/gruvbox), chosen 2026-08-01 after an
   on-device comparison (Solarized / Monochrome / Gruvbox) against Craig's
   accessibility need: iOS Accessibility > Display & Text Size > Color
   Filters > Color Tint > Hue set near-full-left, a red-dominant night-vision
   filter -- this replaces the Solarized draft that was here before, per
   CLAUDE.md item 1/3. Accent A (orange) is the headword/primary highlight;
   Accent B (blue) is the cross-reference/structural highlight -- blue was
   chosen over the original olive green for staying visually distinct from
   the gray secondary text under the red tint. Status colors (below) reuse
   Gruvbox's green/red/yellow for the typing-feedback and Compare-card
   status system, and Accent B blue for "info" -- see the status-* classes.
   This is the single source of truth for all UA_Lexeme templates (UA->EN,
   EN->UA, Compare), including the typing-feedback script and Compare card's
   colors, which used to be hardcoded inline styles with no night-mode
   support -- see the fb-*/compare-* classes. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #3c3836; /* gruvbox fg1 (light) */
  background-color: #fbf1c7; /* gruvbox bg0 (light) */
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

.lemma {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #af3a03; /* Accent A: orange (light) */
}

.perfective {
  font-size: 22px;
  color: #7c6f64; /* gray (light secondary) */
  margin-bottom: 8px;
}

.aspect-label {
  font-size: 16px;
  font-weight: normal;
  color: #7c6f64; /* gray (light secondary) */
}

.pos {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  font-style: italic;
  margin-bottom: 16px;
}

.gender {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-bottom: 4px;
}

hr#answer {
  border: none;
  border-top: 2px solid #7c6f64; /* gray (light secondary) */
  margin: 20px 0;
}

.gloss {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #3c3836; /* fg1 (light primary) */
}

.counterpart {
  font-size: 14px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 4px;
}

.irregular {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 4px;
}

.confusable {
  font-size: 13px;
  color: #076678; /* Accent B: blue (light) */
  margin-top: 6px;
}

.example-ua {
  font-size: 15px;
  margin-top: 14px;
  font-style: italic;
  color: #3c3836; /* fg1 (light primary) */
}

.example-en {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 2px;
}

.note-id {
  font-size: 10px;
  color: #7c6f64; /* gray (light secondary) */
  text-align: right;
  margin-top: 16px;
}

.source-link {
  font-size: 11px;
  margin-top: 10px;
  text-align: right;
}

.source-link a {
  color: #7c6f64; /* gray (light secondary) */
  text-decoration: none;
}

/* Typing card input */
input#typeans {
  font-size: 20px;
  font-family: 'Noto Sans', Arial, sans-serif;
  width: 80%;
  text-align: center;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border: 1px solid #7c6f64; /* gray (light secondary) */
  padding: 6px;
}

/* Typing-feedback hint (EN->UA front, "type without stress..." caption) */
.type-hint {
  font-size: 12px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 8px;
}

/* AspectCue (EN->UA front, optional): same visual weight as a Compare-card
   distractor chip -- see compare-chip-word below. */
.aspect-cue {
  display: inline-block;
  font-size: 20px;
  font-weight: bold;
  padding: 12px 16px;
  margin: 12px 0;
  border-left: 3px solid;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border-left-color: #076678; /* Accent B: blue (light) */
}

/* Divider used by EN->UA back's reference-answer block */
.ref-divider {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #7c6f64; /* gray (light secondary) */
}

/* Status/feedback system (typing-feedback script, Compare card): green for
   correct/success, red for incorrect/error, yellow for partial-credit, blue
   (Accent B) for informational/reveal text. Layout-only rules (font-size,
   weight, margin) live in the *-headline/-sub/-label/-value/-note classes so
   JS only ever has to add ONE color modifier class alongside them -- see
   EN_UA_BACK's <script> and setup_ua_pvom_note_type.py's FEEDBACK_SCRIPT. */
.fb-headline { font-size: 22px; font-weight: bold; margin-bottom: 4px; }
.fb-sub { font-size: 14px; margin-bottom: 12px; }
.fb-label { font-size: 16px; font-weight: bold; margin-bottom: 4px; }
.fb-value { font-size: 16px; }
.fb-note { font-size: 13px; }

.status-success { color: #79740e; } /* green (light) */
.status-error { color: #9d0006; } /* red (light) */
.status-warning { color: #af3a03; } /* orange, reuses Accent A (light) -- kept
  orange rather than Gruvbox's yellow so the "close/partial-credit" typing-
  feedback state stays close to its original color family (was #ff9800), per
  Craig 2026-08-01: keep status colors close to current. Dark-mode red/orange
  below use Gruvbox's *bright* tier (not the muted/neutral tier) specifically
  for maximum luminance contrast against the dark background -- per Craig,
  these should NOT wash out under the red-tint night filter. Claude can't
  preview that filter directly; this is the best available color choice, and
  worth a quick on-device check (e.g. via the palette-comparison demo) before
  treating it as fully validated. */
.status-info { color: #076678; } /* Accent B: blue (light) */
.status-neutral { color: #7c6f64; } /* gray (light secondary) */

/* Compare card ("Confusable Comparison" template) */
.compare-prompt-header {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #076678; /* Accent B: blue (light) */
}
.compare-warning {
  font-size: 15px;
  font-style: italic;
  padding: 16px;
  border: 1px dashed;
  border-radius: 4px;
  color: #9d0006; /* red (light) */
  border-color: #9d0006; /* red (light) */
}
.compare-chip-sentence {
  font-size: 16px;
  padding: 12px;
  border-left: 3px solid;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border-left-color: #076678; /* Accent B: blue (light) */
}
.compare-chip-word {
  font-size: 20px;
  font-weight: bold;
  padding: 12px 16px;
  border-left: 3px solid;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border-left-color: #076678; /* Accent B: blue (light) */
}
.compare-reveal-header {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #79740e; /* green (light) */
}
.compare-correct-header {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #79740e; /* green (light) */
}
.compare-correct-sub {
  font-size: 13px;
  margin-bottom: 12px;
  color: #79740e; /* green (light) */
}
.compare-sense-block {
  margin: 12px 0;
  padding: 10px;
  border-left: 3px solid;
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border-left-color: #79740e; /* green (light) */
}
.compare-sense-ua {
  font-size: 15px;
  margin-bottom: 4px;
  color: #076678; /* Accent B: blue (light) */
}
.compare-sense-en {
  font-size: 13px;
  color: #79740e; /* green (light) */
}
.compare-mnemonic {
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
  margin-top: 10px;
  background-color: #ebdbb2; /* bg1 (light highlight) */
}

/* Conjugation table (not currently rendered by any live template --
   Verb_Conj_Table was removed from UA_Lexeme 2026-07-31 -- themed anyway
   rather than left an untouched light-only remnant, in case it's revived) */
.conj {
  width: 100%;
  border-collapse: collapse;
  margin-top: 6px;
  font-size: 14px;
  text-align: left;
}
.conj th, .conj td {
  padding: 4px 8px;
  border: 1px solid #7c6f64; /* gray (light secondary) */
}
.conj th {
  background-color: #ebdbb2; /* bg1 (light highlight) */
  font-weight: 600;
  color: #3c3836; /* fg1 (light primary) */
}
.conj td:first-child {
  color: #7c6f64; /* gray (light secondary) */
  font-size: 12px;
  width: 6em;
}

/* Collapsible wrapper */
details.conj-wrap {
  margin-top: 16px;
  text-align: left;
}
details.conj-wrap summary {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  cursor: pointer;
  user-select: none;
  list-style: none;
}
details.conj-wrap summary::before {
  content: '▶ ';
  font-size: 10px;
}
details.conj-wrap[open] summary::before {
  content: '▼ ';
}

/* Dark mode (Gruvbox dark) */
.nightMode .card { color: #ebdbb2; background-color: #282828; } /* fg1 dark / bg0 dark */
.nightMode .lemma { color: #fe8019; } /* Accent A: orange (dark) */
.nightMode .perfective { color: #a89984; } /* gray (dark secondary) */
.nightMode .aspect-label { color: #a89984; } /* gray (dark secondary) */
.nightMode .pos { color: #a89984; } /* gray (dark secondary) */
.nightMode .gender { color: #a89984; } /* gray (dark secondary) */
.nightMode hr#answer { border-top-color: #a89984; } /* gray (dark secondary) */
.nightMode .gloss { color: #ebdbb2; } /* fg1 (dark primary) */
.nightMode .counterpart { color: #a89984; } /* gray (dark secondary) */
.nightMode .irregular { color: #a89984; } /* gray (dark secondary) */
.nightMode .confusable { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .example-ua { color: #ebdbb2; } /* fg1 (dark primary) */
.nightMode .example-en { color: #a89984; } /* gray (dark secondary) */
.nightMode .note-id { color: #a89984; } /* gray (dark secondary) */
.nightMode .source-link a { color: #a89984; } /* gray (dark secondary) */
.nightMode input#typeans { color: #ebdbb2; background-color: #282828; border-color: #a89984; } /* fg1 dark / bg0 dark / gray dark */
.nightMode .type-hint { color: #a89984; } /* gray (dark secondary) */
.nightMode .aspect-cue { color: #ebdbb2; background-color: #3c3836; border-left-color: #83a598; } /* fg1 dark / bg1 dark / Accent B dark */
.nightMode .ref-divider { border-top-color: #a89984; } /* gray (dark secondary) */
.nightMode .status-success { color: #b8bb26; } /* green (dark) */
.nightMode .status-error { color: #fb4934; } /* red (dark) */
.nightMode .status-warning { color: #fabd2f; } /* yellow (dark) */
.nightMode .status-info { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .status-neutral { color: #a89984; } /* gray (dark secondary) */
.nightMode .compare-prompt-header { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .compare-warning { color: #fb4934; border-color: #fb4934; } /* red (dark) */
.nightMode .compare-chip-sentence { color: #ebdbb2; background-color: #3c3836; border-left-color: #83a598; } /* fg1 dark / bg1 dark / Accent B dark */
.nightMode .compare-chip-word { color: #ebdbb2; background-color: #3c3836; border-left-color: #83a598; } /* fg1 dark / bg1 dark / Accent B dark */
.nightMode .compare-reveal-header { color: #b8bb26; } /* green (dark) */
.nightMode .compare-correct-header { color: #b8bb26; } /* green (dark) */
.nightMode .compare-correct-sub { color: #b8bb26; } /* green (dark) */
.nightMode .compare-sense-block { background-color: #3c3836; border-left-color: #b8bb26; } /* bg1 dark / green dark */
.nightMode .compare-sense-ua { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .compare-sense-en { color: #b8bb26; } /* green (dark) */
.nightMode .compare-mnemonic { background-color: #3c3836; } /* bg1 dark */
.nightMode .conj th, .nightMode .conj td { border-color: #a89984; } /* gray (dark secondary) */
.nightMode .conj th { background-color: #3c3836; color: #ebdbb2; } /* bg1 dark / fg1 dark */
.nightMode .conj td:first-child { color: #a89984; } /* gray (dark secondary) */
.nightMode details.conj-wrap summary { color: #a89984; } /* gray (dark secondary) */
"""

# ---------------------------------------------------------------------------
# Card templates
# ---------------------------------------------------------------------------

# Template 1: UA → EN  (Recognition: see Ukrainian, recall English)
UA_EN_FRONT = """\
<!-- Lemma line uses _UA_EN_DisplayLemma (2026-08-04, per Craig -- supersedes
     the 2026-07-31 TypingTarget_UA reuse), not TypingTarget_UA directly:
     _UA_EN_DisplayLemma is a second render over the same source fields
     (Lemma/ImperfectiveUnidirectional/Perfective, plus each slot's own
     *_Euphony alternate), so a slot with a documented в-/у- euphonic
     variant shows both forms inline (e.g. "уві́йти (ввійти́)") instead of
     silently only showing the primary spelling. TypingTarget_UA itself is
     left untouched -- it must stay a pure, exact-match typing target for
     the EN->UA card's type-answer replacement (written without braces on
     purpose: Anki parses replacements inside comments too -- see the note
     in EN_UA_BACK), so it never grows parentheticals; when
     no slot has a euphonic alternate, _UA_EN_DisplayLemma renders
     identically to TypingTarget_UA. See compute_ua_en_display() in
     ua_lexeme_import.py. _AspectLabel adds a small "(pf.)"/"(impf.)" tag for
     true singlets only (doublets/triplets already show their range via the
     slash join, so no tag is needed there) -- see _AspectLabel's FIELDS
     comment and import_note() for how it's derived. -->
<div class="lemma">{{_UA_EN_DisplayLemma}}{{#_AspectLabel}} <span class="aspect-label">{{_AspectLabel}}</span>{{/_AspectLabel}}</div>
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
<!-- UA_Example on front (2026-07-28, per Craig): show the example sentence
     for context on the Recognition (UA->EN) card, not just the bare
     headword. -->
{{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
"""

UA_EN_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="gloss">{{EN_Gloss}}</div>
{{#CounterpartForm}}<div class="counterpart">{{CounterpartForm}}</div>{{/CounterpartForm}}
{{#IrregularForms}}<div class="irregular">{{IrregularForms}}</div>{{/IrregularForms}}
{{#Govt_Case}}<div class="irregular">governs: {{Govt_Case}}</div>{{/Govt_Case}}
{{#ConfusableSet}}<div class="confusable">cf. {{ConfusableSet}}</div>{{/ConfusableSet}}
{{#EuphonyNote}}<div class="euphony">also accepted: {{EuphonyNote}}</div>{{/EuphonyNote}}
{{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""

# Template 2: EN → UA  (Production: see English, type Ukrainian)
# Restored 2026-07-28 (git archaeology, commit a5b4a15) -- this is the
# aspect+euphony version that worked before the 2026-07-25 Lemma_Euphony
# redesign (881ac25/2e93202) made it require typing both the primary and
# euphonic form together for full credit. This version types the full
# stressed aspect join (TypingTarget_UA, computed at sync time -- see
# compute_typing_target() in ua_lexeme_import.py) and accepts an EuphonyNote
# alternate spelling as a genuinely correct answer, not a partial-credit tier.
EN_UA_FRONT = """\
<div class="gloss">{{EN_Gloss}}</div>
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
<!-- EN_Example on front (2026-08-04, per Craig -- CLAUDE.md "EN->UA card
     front -- show the English sentence"): several distinct UA words can map
     to the same EN_Gloss (e.g. multiple words for "goodbye"), so the bare
     gloss alone can under-specify which UA translation is actually wanted.
     Showing the English example sentence gives the same disambiguating
     context UA_EN_FRONT already gets from UA_Example (added 2026-07-28).
     Deduped the now-redundant EN_Example line from EN_UA_BACK's
     ref-divider below, matching that same UA_EN_FRONT/BACK precedent. -->
{{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
<!-- AspectCue: optional, only for notes where the EN->UA typing target is a
     single aspect and it isn't otherwise obvious which one from EN_Gloss
     alone. Styled to match the Compare card's distractor chips (font-size:
     20px, bold, boxed) -- same visual weight as an actual answer option, not
     a small caption. Absent for notes where it doesn't apply (renders
     nothing, per the {{#AspectCue}} guard). -->
{{#AspectCue}}<div class="aspect-cue">{{AspectCue}}</div>{{/AspectCue}}
<!-- Typing target is the STRESSED field (TypingTarget_UA), not TypingAnswer:
     typing it correctly is then a clean exact match for Anki's diff (no
     insertion); typing without stress becomes a clean omission instead. Both
     are well-behaved for Anki's diff -- the reverse (unstressed target,
     stressed insertion, the previous setup) is not: a typed stress mark shows
     as an inserted character with no adjacent match, which Anki's
     per-character span-wrapping renders visually detached from its base
     letter (looks like a stray apostrophe next to the vowel). Same reasoning
     as UA_PVOM_Infinitive's Walking/Vehicle templates -- see
     setup_ua_pvom_note_type.py. -->
{{type:TypingTarget_UA}}
<div id="type-hint" class="type-hint">
  (Type without stress, or with stress marks for bonus credit)
</div>
"""

# NOTE: this is a concatenation, not one literal. The middle piece is
# NORMALIZE_TYPEANS_JS, shared with setup_ua_pvom_note_type.py so the two
# feedback scripts cannot drift apart again (see tools/anki/lib/typeans_js.py
# for what went wrong when they were separate copies). Keep the `"""` /
# `+ NORMALIZE_TYPEANS_JS` / `+ """` seam byte-exact: the JS on either side of
# it is whitespace-sensitive only in that it must stay valid, but
# test_typeans_normalization.py asserts the emitted body matches PVOM's.
EN_UA_BACK = (
    """\
{{FrontSide}}
<hr id="answer">
<!-- Color-coded typing feedback.
     _TypingSpec (2026-08-19) replaces the older _EuphonySlots string. It is
     compact JSON, one object per populated aspect slot, primary plus its
     stressed euphonic alternates. The previous design shipped TWO
     " / "-joined strings (TypingTarget_UA and _EuphonySlots) that had to
     stay index-aligned by convention, with nothing enforcing it and nothing
     able to notice a break; the JS then rebuilt the slot structure by
     splitting both and trusting the positions to correspond. Here primary
     and alternates travel together, so that whole class of alignment bug is
     gone rather than avoided. Alternates arrive STRESSED, which is what lets
     a fully-stressed euphonic answer reach PERFECT -- see the grading block.

     WHY THE JSON LIVES IN A SCRIPT BLOCK AND NOT AN ATTRIBUTE (2026-08-19,
     second attempt): it first shipped as a data- attribute on the div below.
     Anki does NOT HTML-escape field content -- it splices the raw text in --
     so the JSON's own double quotes closed the attribute at the first one.
     The browser saw the value as just "{", JSON.parse threw, the catch below
     degraded to "no alternates", and every euphonic answer graded INCORRECT
     while the correct-answer lines rendered perfectly, because those sit in
     EARLIER attributes that were still intact. That split is what made it
     look like a grading-logic bug rather than a quoting bug. A JSON script
     block has no attribute quoting to get wrong; the application/json type
     keeps it inert, and the text: filter stays on the replacement because
     stripping tags is the one thing that could otherwise break out of the
     block.

     (Field replacements are deliberately not written out in this comment --
     Anki parses them inside comments too. See the note in the script below.)
     -->
<div id="feedback" data-with-stress="{{TypingTarget_UA}}" data-no-stress="{{TypingAnswer}}" style="margin-bottom: 16px;"></div>
<script type="application/json" id="typing-spec">{{text:_TypingSpec}}</script>
<script>
(function() {
  var feedback = document.getElementById('feedback');
  // Normalize to NFC before comparing. Combining stress marks (U+0301) can
  // reach the reconstructed typed answer (see below) in a different Unicode
  // normalization form than the field is stored in (OS keyboard/IME-dependent)
  // even though the strings look visually identical, so a raw === comparison
  // silently fails for otherwise-correct accented answers.
  var targetWithStress = (feedback.dataset.withStress || '').normalize('NFC');
  var targetNoStress = (feedback.dataset.noStress || '').normalize('NFC');
  function stripStress(s) { return s.replace(/́/g, ''); }

"""
    + NORMALIZE_TYPEANS_JS
    + """\

  // NB: never write a doubled curly brace in a template comment, even inside
  // a // JS comment or an HTML comment. Anki scans the whole template text
  // for replacements and does not know what a comment is, so it reads the
  // brace pair as a field reference and rejects the template with "Field
  // '...' not found". That is exactly what a "type:..." example written with
  // braces did on 2026-08-19; test_template_field_refs.py now guards it.
  //
  // Slot model (2026-08-19, Option B). The typing target is still a
  // " / "-joined string because that is what the type-answer replacement
  // shows the learner, but grading now works from _TypingSpec, where each
  // slot carries its own
  // primary and alternates as one object. Nothing here depends on two
  // strings staying index-aligned any more.
  //
  // SEPARATOR TOLERANCE: split on a whitespace-tolerant slash regex rather
  // than the literal " / ".
  // Previously a learner who typed "ходити/йти/піти" -- right forms, no
  // spaces around the slashes -- failed the slot-count gate and graded
  // INCORRECT outright. The separator is punctuation we render, not part of
  // the answer being tested.
  function splitSlots(s) {
    var t = (s || '').trim();
    return t ? t.split(/\\s*\\/\\s*/) : [];
  }

  var stressSlots = splitSlots(targetWithStress);
  var noStressSlots = splitSlots(targetNoStress);

  // _TypingSpec is blank on every note with no euphony data at all (573 of
  // 585), in which case slotAlts() just returns [] and grading falls through
  // to the plain primary/no-stress comparison. Parse defensively: a malformed
  // spec must degrade to "no alternates", never throw and leave the learner
  // staring at a blank feedback panel.
  //
  // Read from the JSON <script> block, NOT a data- attribute -- see the
  // header comment. Silent degradation is the right behaviour for a genuinely
  // malformed spec, but note that it is also what hid the attribute-quoting
  // bug: every euphonic answer graded INCORRECT and nothing anywhere said
  // why. test_typing_spec.py now parses the emitted HTML to assert the spec
  // survives the round trip, because this catch block cannot.
  var typingSpec = null;
  try {
    var specEl = document.getElementById('typing-spec');
    var rawSpec = (specEl ? specEl.textContent : '').trim();
    if (rawSpec) { typingSpec = JSON.parse(rawSpec); }
  } catch (e) {
    typingSpec = null;
  }
  var specSlots = (typingSpec && typingSpec.slots) || [];

  // Alternates arrive STRESSED. Returning them as-is -- rather than
  // pre-stripping the way the old per-slot euphony helper did -- is the whole
  // point of the refactor: it lets matchSlot() below tell a perfectly-stressed
  // alternate from an unstressed one, so the former can reach PERFECT.
  function slotAlts(i) {
    var slot = specSlots[i];
    if (!slot || !slot.alts) { return []; }
    return slot.alts.map(function(a) { return (a || '').normalize('NFC'); })
                    .filter(Boolean);
  }

  // Grade one slot. Returns 'perfect' (matched something acceptable WITH its
  // stress), 'correct' (matched something acceptable but unstressed), or null
  // (matched nothing).
  function matchSlot(typed, i) {
    var stressed = (stressSlots[i] || '').normalize('NFC');
    var plain = (noStressSlots[i] || stripStress(stressed)).normalize('NFC');
    if (typed === stressed) { return 'perfect'; }

    var alts = slotAlts(i);
    for (var a = 0; a < alts.length; a++) {
      if (typed === alts[a]) { return 'perfect'; }
    }
    if (typed === plain) { return 'correct'; }
    var typedPlain = stripStress(typed);
    for (var b = 0; b < alts.length; b++) {
      if (typedPlain === stripStress(alts[b])) { return 'correct'; }
    }
    return null;
  }

  // Anki's own type-answer field replaces the front's <input> with a #typeans
  // diff (spans classed typeGood/typeBad/typeMissed) once the answer side
  // renders -- there is no live <input> to read here (the previous
  // document.querySelector('input[type="text"]') lookup never found one on
  // the answer side, so this feedback block never actually populated).
  // Reconstruct what was typed from that diff instead -- same technique as
  // UA_PVOM_Infinitive (setup_ua_pvom_note_type.py).
  var typedAnswer = null;
  var typeansEl = document.getElementById('typeans');
  if (typeansEl) {
    var arrowEl = typeansEl.querySelector('#typearrow');
    var chunks = [];
    for (var i = 0; i < typeansEl.childNodes.length; i++) {
      var child = typeansEl.childNodes[i];
      if (arrowEl && child === arrowEl) break;
      if (child.nodeType === 1 && (child.classList.contains('typeGood') || child.classList.contains('typeBad'))) {
        chunks.push(child);
      }
    }
    if (chunks.length) {
      typedAnswer = normalizeTypeansText(
        chunks.map(function(el) { return el.textContent; }).join('')
      ).normalize('NFC');
    }
    // Hide Anki's raw per-character diff (answer side only) -- it can
    // visually detach combining stress marks from their base letter (renders
    // like a stray apostrophe next to the vowel instead of a proper accent).
    // The #feedback message below is the intended user-facing display.
    typeansEl.style.display = 'none';
  }

  var html = '';

  if (typedAnswer === null) {
    // Couldn't determine what was typed at all (e.g. #typeans markup ever
    // changes shape) -- show the answer neutrally rather than guessing.
    html = '<div class="fb-headline status-info">' +
           targetWithStress + '</div>' +
           '<div class="fb-note status-neutral">(no stress: ' + targetNoStress + ')</div>';
  } else if (typedAnswer === targetWithStress) {
    // Perfect: whole compound answer matches with stress marks, exactly.
    html = '<div class="fb-headline status-success">' +
           targetWithStress + ' ✓ PERFECT</div>' +
           '<div class="fb-sub status-success">Correct with stress marks (bonus!)</div>';
  } else if (typedAnswer === targetNoStress) {
    // Close: correct letters throughout, missing stress everywhere.
    html = '<div class="fb-headline status-warning">' +
           targetNoStress + ' ~ CORRECT</div>' +
           '<div class="fb-sub status-warning">Correct letters, but missing stress marks</div>' +
           '<div class="fb-label status-success">Bonus answer:</div>' +
           '<div class="fb-value status-info"><b>' + targetWithStress + '</b></div>';
  } else {
    // Neither whole-string comparison hit. Grade slot by slot, so a
    // doublet/triplet only loses credit for the slot that is actually wrong.
    //
    // Tiers (2026-08-19, Option B -- decisions in
    // docs/ua-en-ua-euphony-aspect-refactor.md section 7):
    //   PERFECT   every slot matched its primary OR an alternate, WITH stress
    //   CORRECT   every slot matched something acceptable, at least one only
    //             unstressed
    //   INCORRECT any slot matched nothing acceptable
    //
    // The change from the previous version is that an alternate can now reach
    // PERFECT. The old code cleared its everySlotPerfect flag the moment a
    // slot failed to equal the *primary* -- before the alternate check ran --
    // and then compared alternates stress-stripped on both sides, so it could
    // not have distinguished a perfectly-stressed alternate from an unstressed
    // one even in the right order. Craig's call: ввійти́ is not a lesser answer
    // than уві́йти, just a different attested one.
    var typedSlots = splitSlots(typedAnswer);
    var slotsAcceptable = stressSlots.length > 0 &&
                          typedSlots.length === stressSlots.length;
    var everySlotPerfect = slotsAcceptable;
    var anyAlternateUsed = false;

    if (slotsAcceptable) {
      for (var i = 0; i < stressSlots.length; i++) {
        var typedSlot = (typedSlots[i] || '').normalize('NFC');
        var verdict = matchSlot(typedSlot, i);

        if (verdict === null) {
          slotsAcceptable = false;
          break;
        }
        if (verdict !== 'perfect') { everySlotPerfect = false; }
        // Did this slot match an alternate rather than its primary? Only
        // affects the wording of the CORRECT message.
        if (typedSlot !== (stressSlots[i] || '').normalize('NFC') &&
            typedSlot !== (noStressSlots[i] || stripStress(stressSlots[i] || '')).normalize('NFC')) {
          anyAlternateUsed = true;
        }
      }
    }

    if (slotsAcceptable && everySlotPerfect) {
      // Reachable now, unlike before: this is the fully-stressed euphonic
      // alternate case, e.g. вхо́дити / ввійти́ on ua-lexeme-0115.
      html = '<div class="fb-headline status-success">' +
             typedAnswer + ' ✓ PERFECT</div>' +
             '<div class="fb-sub status-success">' +
             (anyAlternateUsed
               ? 'Correct with stress marks — accepted variant form (bonus!)'
               : 'Correct with stress marks (bonus!)') +
             '</div>' +
             (anyAlternateUsed
               ? '<div class="fb-label status-info">Primary form:</div>' +
                 '<div class="fb-value status-info"><b>' + targetWithStress + '</b></div>'
               : '');
    } else if (slotsAcceptable) {
      html = '<div class="fb-headline status-warning">' +
             typedAnswer + ' ~ CORRECT</div>' +
             '<div class="fb-sub status-warning">' +
             (anyAlternateUsed
               ? 'Accepted variant form and/or missing stress marks'
               : 'Correct letters, but missing stress marks somewhere') +
             '</div>' +
             '<div class="fb-label status-success">Bonus answer:</div>' +
             '<div class="fb-value status-info"><b>' + targetWithStress + '</b></div>';
    } else {
      html = '<div class="fb-headline status-error">' +
             typedAnswer + ' ✗ INCORRECT</div>' +
             '<div class="fb-sub status-error">Not quite right</div>' +
             '<div class="fb-label status-success">Correct (no stress):</div>' +
             '<div class="fb-value status-success" style="margin-bottom: 8px;"><b>' + targetNoStress + '</b></div>' +
             '<div class="fb-label status-info">Correct (with stress):</div>' +
             '<div class="fb-value status-info"><b>' + targetWithStress + '</b></div>';
    }
  }

  feedback.innerHTML = html;
})();
</script>
<!-- Reference answer and context. EN_Example moved to EN_UA_FRONT
     (2026-08-04) -- deduped here to match the UA_EN_FRONT/BACK precedent
     (UA_Example moved to UA_EN_FRONT, 2026-07-28). -->
<div class="ref-divider">
  {{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
</div>
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""
)

# Template 3: Confusable Comparison (scenario-based, bidirectional)
# Optional, only shown when ConfusableSet is populated
# Design: Forces semantic discrimination, not pattern memorization
# Front: Scenario/context requiring a choice among 2-4 confusable words
# Back: Correct answer + explanation of why it fits this context
#
# CompareA is always required; CompareB/C/D are optional so the same template
# serves 2-way (студент/студентка), 3-way, and 4-way (добре/непогано/нормально/
# чудово) clusters without a separate template per arity. Each populated
# Compare* renders as its own chip in a wrapping flex row rather than inline
# "A or B" text, so a 4-way cluster doesn't overflow the card width.
#
# CompareScenario (added 2026-07-24) holds a real situational prompt, separate
# from EN_Gloss. Found during the Compare-card verbosity audit: for near-
# synonym clusters (e.g. добре/непогано/нормально/чудово) EN_Gloss essentially
# *is* the answer -- "Scenario: not bad" for ua-lexeme-0100 gives away
# "непогано" outright, the same leak this whole redesign exists to fix.
# EN_Gloss remains the fallback for any note not yet authored with a real
# scenario, so the card degrades instead of going blank -- but every note
# with a populated ConfusableSet should get a real CompareScenario over time.

COMPARISON_FRONT = """\
{{#ConfusableSet}}
<!-- CompareA is "always required" by convention (CompareB/C/D optional) --
     see comment above CARD_TEMPLATES. A blank CompareA here means the note
     has ConfusableSet populated but Compare fields were never authored
     (e.g. a homograph:true note where CompareA/B got skipped), or some
     other data gap.
     UNREACHABLE, deliberately kept. Tested 2026-08-01 (see CLAUDE.md item 6):
     everything this branch emits is static markup with no field substitution,
     so Anki's own empty-card rule refuses to generate the card at all when
     CompareA is blank. The block below can never render -- not in study, not
     in preview, not in QA -- and the importer's suspend call for this exact
     case is a no-op against a card that does not exist.
     Its wording used to say "this card should be suspended", which read as a
     live safeguard and was the one misleading thing about it: nothing is
     suspending anything here, because there is nothing to suspend. Reworded
     2026-08-20 to describe the data gap and say plainly that seeing it at all
     would mean Anki's empty-card behaviour had changed. Find the real gaps
     with `make ua-check`, not with this. -->
{{^CompareA}}
<div class="compare-warning">
⚠ ConfusableSet is populated but no CompareA/B/C/D was authored. If you are reading this in Anki, the empty-card rule has changed -- see COMPARISON_FRONT in setup_ua_note_types.py.
</div>
{{/CompareA}}
{{#CompareA}}
{{#_IsHomograph}}
<!-- HOMOGRAPH MODE: UA→EN direction. Show Ukrainian sentences, student deduces EN meaning -->
<div class="compare-prompt-header">Which sense is being used?</div>
<div class="gloss" style="font-size: 18px; margin-bottom: 16px;">
  {{#CompareScenario}}{{CompareScenario}}{{/CompareScenario}}{{^CompareScenario}}[Homograph scenario]{{/CompareScenario}}
</div>
<div style="display: flex; flex-direction: column; gap: 12px; margin-top: 12px;">
<div class="compare-chip-sentence">{{CompareA}}</div>
{{#CompareB}}<div class="compare-chip-sentence">{{CompareB}}</div>{{/CompareB}}
</div>
{{/_IsHomograph}}
{{^_IsHomograph}}
<!-- CONFUSABLES MODE: EN→UA direction. Show English scenario, student picks Ukrainian word -->
<div class="compare-prompt-header">Choose the right word:</div>
<div class="gloss" style="font-size: 18px; margin-bottom: 16px;">
  Scenario: {{#CompareScenario}}{{CompareScenario}}{{/CompareScenario}}{{^CompareScenario}}{{EN_Gloss}}{{/CompareScenario}}
</div>
<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 12px;">
<div class="compare-chip-word">{{CompareA}}</div>
{{#CompareB}}<div class="compare-chip-word">{{CompareB}}</div>{{/CompareB}}
{{#CompareC}}<div class="compare-chip-word">{{CompareC}}</div>{{/CompareC}}
{{#CompareD}}<div class="compare-chip-word">{{CompareD}}</div>{{/CompareD}}
</div>
{{/_IsHomograph}}
{{/CompareA}}
{{/ConfusableSet}}
"""

COMPARISON_BACK = """\
{{FrontSide}}
<hr id="answer">
{{#ConfusableSet}}
{{#CompareA}}
{{#_IsHomograph}}
<!-- HOMOGRAPH BACK: Show each Ukrainian sentence + its EN sense -->
<div style="margin-top: 16px; font-size: 16px;">
<div class="compare-reveal-header">Senses of {{Lemma}}:</div>
<div class="compare-sense-block">
  <div class="compare-sense-ua">{{CompareA}}</div>
  <div class="compare-sense-en">{{Homograph_SenseA}}</div>
</div>
<div class="compare-sense-block">
  <div class="compare-sense-ua">{{CompareB}}</div>
  <div class="compare-sense-en">{{Homograph_SenseB}}</div>
</div>
{{#Mnemonic_EN}}<div class="compare-mnemonic">
<strong>Remember:</strong> {{Mnemonic_EN}}
</div>{{/Mnemonic_EN}}
</div>
{{/_IsHomograph}}
{{^_IsHomograph}}
<!-- CONFUSABLES BACK: Show the correct word and why it fits -->
<div style="margin-top: 16px; font-size: 16px;">
<div class="compare-correct-header">✓ {{Lemma}}</div>
<div class="compare-correct-sub">{{EN_Gloss}}</div>
{{#Mnemonic_EN}}<div class="compare-mnemonic">
<strong>Remember:</strong> {{Mnemonic_EN}}
</div>{{/Mnemonic_EN}}
</div>
{{/_IsHomograph}}
{{/CompareA}}
<!-- Same unreachable branch as COMPARISON_FRONT's; see the long comment
     there. The back can only render if the front did, and the front cannot.
     Kept in step with it so the two never disagree about what a data gap
     looks like. -->
{{^CompareA}}
<div class="compare-warning">
⚠ ConfusableSet is populated but no CompareA/B/C/D was authored. If you are reading this in Anki, the empty-card rule has changed -- see COMPARISON_FRONT in setup_ua_note_types.py.
</div>
{{/CompareA}}
{{/ConfusableSet}}
"""

CARD_TEMPLATES = [
    {"Name": "UA→EN",  "Front": UA_EN_FRONT, "Back": UA_EN_BACK},
    {"Name": "EN→UA",  "Front": EN_UA_FRONT, "Back": EN_UA_BACK},
    {"Name": "Compare", "Front": COMPARISON_FRONT, "Back": COMPARISON_BACK},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_existing_models() -> list[str]:
    return anki_request("modelNames", url=ANKI_URL) or []


def sync_field_order(model_name: str, desired_fields: list[str]) -> bool:
    """Reposition an existing model's fields to match `desired_fields` exactly.

    Added 2026-08-18. Until now the FIELDS-style constants in this module were
    decorative for any model that already existed: `inOrderFields` is only
    honoured by `createModel`, and `update_model()` and its siblings only ever
    called `modelFieldAdd` (which APPENDS to the end of the model) and
    `modelFieldRemove`. Nothing anywhere in the repo called
    `modelFieldReposition`. So the live field order was never "whatever the
    constant says" -- it was "whatever order fields happened to get added in,
    across the whole history of the model."

    That is what actually happened on 2026-08-11, and CLAUDE.md item 20's
    diagnosis of it was wrong in mechanism (right in symptom): `make
    ua-setup-lexeme` did not reset the field order to this constant's order.
    It appended `Verification Notes` (removed and re-added by the field-name
    unification) plus the five euphony/display fields to the BOTTOM of the
    model, which yanked them out of the positions Craig had just dragged them
    into. Confirmed 2026-08-18 by `inspect_note_type_fields.py` against live
    Anki: `UA_Lexeme`'s live order matched neither the dragged order nor this
    constant, but exactly the historical add-order, with that 2026-08-11 tail
    appended in sequence. `UA_Verb` (Participle_Passive_Past last among the
    participles, from the 0e3a987 consolidation) and `UA_PVOM_Infinitive`
    (four *_Euphony fields appended past `Verification Notes`) carry the same
    fingerprint.

    Repositioning `desired_fields[i]` to index `i` in ascending order is an
    insertion sort against the live model and converges on the exact target
    order. Field VALUES follow their field -- Anki rewrites the notes -- so no
    note data is lost, but this IS a schema modification: the first run that
    actually moves anything will make Anki ask for a full AnkiWeb upload on
    next sync. Hence the guard: when the live order already matches, this
    makes zero AnkiConnect calls and returns False, so routine
    `make ua-setup-*` runs stay silent and never re-trigger that prompt.

    Only fields present on BOTH the live model and `desired_fields` are moved.
    Anything live that the constant doesn't know about (a field the remove
    pass deliberately left in place -- setup_ua_pvom_note_type.py does this on
    purpose) is never repositioned directly, and ends up trailing after every
    field the constant DOES name. That's deliberate: the constant owns the
    leading positions, so an unrecognised legacy field can't sit wedged
    between -- or ahead of -- fields whose order we're asserting.

    Callers must run this AFTER their add/remove passes, since both change
    the live order out from under it.

    Returns True if any field was repositioned.
    """
    live_fields = anki_request("modelFieldNames", {"modelName": model_name}, url=ANKI_URL) or []
    target = [f for f in desired_fields if f in set(live_fields)]

    # Compare against the leading slice, not the filtered relative order: the
    # constant's fields must occupy indices 0..len(target)-1 exactly. Checking
    # only relative order would call it "already correct" when an unknown
    # field sits at index 0 pushing everything down.
    if live_fields[: len(target)] == target:
        return False

    print(f"  Field order differs from {model_name}'s FIELDS constant -- repositioning...")
    print("    NOTE: reordering fields is a schema change. Anki may ask for a full")
    print("    upload on your next AnkiWeb sync. No note data is lost -- values move")
    print("    with their field. Subsequent runs are a no-op once order matches.")
    for index, field in enumerate(target):
        anki_request(
            "modelFieldReposition",
            {"modelName": model_name, "fieldName": field, "index": index},
            url=ANKI_URL,
        )
    print(f"    Repositioned {len(target)} field(s).")
    return True


def create_model():
    print(f"Creating note type '{MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": MODEL_NAME,
            "inOrderFields": FIELDS,
            "css": CSS,
            "cardTemplates": CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_model():
    """Update templates and CSS; sync fields."""
    print(f"Updating note type '{MODEL_NAME}'...")

    # Sync fields FIRST (add only) -- updateModelTemplates / modelTemplateAdd
    # validate that every {{Field}} referenced in a template already exists
    # on the model, so a brand-new field referenced by an updated template
    # must be added before the template call or AnkiConnect rejects the
    # whole thing ("Field 'X' not found"). Found 2026-07-22 when CompareA/
    # CompareB were added to the Compare template at the same time as the
    # fields -- field-add was running AFTER the template update.
    existing_fields = anki_request("modelFieldNames", {"modelName": MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(FIELDS)

    for field in FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # updateModelTemplates only refreshes Front/Back for template NAMES that
    # already exist on the model -- it silently no-ops for unrecognized new
    # names (same bug class as setup_ua_pvom_note_type.py and
    # update_visual_model() below). A genuinely new template name needs
    # modelTemplateAdd first, which also generates that card for every
    # existing note of the model. Found 2026-07-22: "Compare" had been in
    # CARD_TEMPLATES for a while but was never actually created in Anki
    # because of this exact gap.
    existing_templates_resp = anki_request("modelTemplates", {"modelName": MODEL_NAME}, url=ANKI_URL)
    existing_template_names = list(existing_templates_resp.keys()) if existing_templates_resp else []

    for tmpl in CARD_TEMPLATES:
        if tmpl["Name"] not in existing_template_names:
            print(f"  Adding new template: {tmpl['Name']}")
            anki_request(
                "modelTemplateAdd",
                {
                    "modelName": MODEL_NAME,
                    "template": {"Name": tmpl["Name"], "Front": tmpl["Front"], "Back": tmpl["Back"]},
                },
                url=ANKI_URL,
            )

    # Update templates — build single dict with all templates, then call once
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    # Update CSS
    anki_request(
        "updateModelStyling",
        {"model": {"name": MODEL_NAME, "css": CSS}},
        url=ANKI_URL,
    )

    # Remove obsolete fields last (after templates/CSS are already synced)
    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # Enforce field order LAST -- the add/remove passes above both change the
    # live order, so anything earlier would be undone. See sync_field_order().
    sync_field_order(MODEL_NAME, FIELDS)

    print("  Updated.")

    # Set card interdependencies: EN→UA (Card 2) depends on UA→EN (Card 1)
    set_card_interdependencies()


def set_card_interdependencies():
    """Configure Card 2 (EN→UA) to be blocked until Card 1 (UA→EN) reaches 'Easy'.

    This prevents production cards from appearing until recognition is learned.
    """
    print(f"  Configuring card interdependencies...")

    try:
        # Fetch the full model to access card template indices
        model_response = anki_request("modelFieldsOnTemplates", {"modelName": MODEL_NAME}, url=ANKI_URL)
        if not model_response:
            print(f"    Warning: Could not fetch model for interdependency config. Manual setup required.")
            return

        # Note: AnkiConnect's updateModelTemplates may not directly support interdependencies.
        # The proper way is to set this in the model's internal structure.
        # For now, we document the manual step and attempt via a workaround.

        # Try to fetch the model and set blocking via the model structure
        # Card indices: 0 = UA→EN, 1 = EN→UA
        # EN→UA should block until UA→EN is "Easy"

        print(f"    Note: Card interdependencies may need manual configuration in Anki.")
        print(f"    To enable: Right-click 'EN→UA' card template → 'Dependent on' → Select 'UA→EN'")
        print(f"    (Anki 25.09+ feature)")

    except Exception as e:
        print(f"    Warning: Could not set interdependencies automatically: {e}")
        print(f"    Please configure manually in Anki's Note Types dialog.")


# ---------------------------------------------------------------------------
# UA_Grammar — Cloze note type for grammar rules
# ---------------------------------------------------------------------------

GRAMMAR_MODEL_NAME = "UA_Grammar"

GRAMMAR_FIELDS = [
    "NoteID",
    "Topic",
    "Text",
    "Extra",
    "SourceDocument",
    "Chapter",
    "Source_URL",
    "Source_Note",
    "Verification Notes",
]

GRAMMAR_CSS = """\
/* Gruvbox palette (github.com/morhetz/gruvbox) -- see the CSS constant
   above (UA_Lexeme) for the full rationale. Accent B (blue) is reused here
   for .cloze, matching its role as the cross-reference/structural highlight
   elsewhere in the repo. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #fbf1c7; /* bg0 (light) */
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 20px;
}

.topic {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  font-style: italic;
  margin-bottom: 14px;
}

.cloze {
  font-weight: bold;
  color: #076678; /* Accent B: blue (light) */
}

.extra {
  font-size: 14px;
  color: #3c3836; /* fg1 (light primary) */
  margin-top: 16px;
  border-top: 1px solid #7c6f64; /* gray (light secondary) */
  padding-top: 10px;
}

.note-id {
  font-size: 10px;
  color: #7c6f64; /* gray (light secondary) */
  text-align: right;
  margin-top: 16px;
}

.chapter {
  font-size: 11px;
  color: #7c6f64; /* gray (light secondary) */
  text-align: right;
}

/* Dark mode (Gruvbox dark) */
.nightMode .card { color: #ebdbb2; background-color: #282828; } /* fg1 dark / bg0 dark */
.nightMode .topic { color: #a89984; } /* gray (dark secondary) */
.nightMode .cloze { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .extra { color: #ebdbb2; border-top-color: #a89984; } /* fg1 dark / gray dark */
.nightMode .note-id { color: #a89984; } /* gray (dark secondary) */
.nightMode .chapter { color: #a89984; } /* gray (dark secondary) */
"""

GRAMMAR_FRONT = """\
<div class="topic">{{Topic}}</div>
{{cloze:Text}}
"""

GRAMMAR_BACK = """\
<div class="topic">{{Topic}}</div>
{{cloze:Text}}
{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}
<div class="note-id">{{NoteID}}</div>
{{#Chapter}}<div class="chapter">§{{Chapter}}</div>{{/Chapter}}
"""

GRAMMAR_CARD_TEMPLATES = [
    {"Name": "Cloze", "Front": GRAMMAR_FRONT, "Back": GRAMMAR_BACK},
]


def create_grammar_model():
    print(f"Creating note type '{GRAMMAR_MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": GRAMMAR_MODEL_NAME,
            "inOrderFields": GRAMMAR_FIELDS,
            "css": GRAMMAR_CSS,
            "isCloze": True,
            "cardTemplates": GRAMMAR_CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_grammar_model():
    print(f"Updating note type '{GRAMMAR_MODEL_NAME}'...")

    # Sync fields BEFORE templates -- see the comment in update_model() for
    # why (updateModelTemplates rejects templates referencing fields that
    # don't exist on the model yet). Fixed here 2026-07-22 preventively,
    # same bug class, not yet actually triggered in this model.
    existing_fields = anki_request("modelFieldNames", {"modelName": GRAMMAR_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(GRAMMAR_FIELDS)

    for field in GRAMMAR_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # Update templates — build single dict with all templates, then call once
    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in GRAMMAR_CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": GRAMMAR_MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    anki_request(
        "updateModelStyling",
        {"model": {"name": GRAMMAR_MODEL_NAME, "css": GRAMMAR_CSS}},
        url=ANKI_URL,
    )

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # Enforce field order LAST -- see sync_field_order().
    sync_field_order(GRAMMAR_MODEL_NAME, GRAMMAR_FIELDS)

    print("  Updated.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def setup_lexeme(existing: list[str]):
    if MODEL_NAME in existing:
        update_model()
    else:
        create_model()
    print(f"Note type '{MODEL_NAME}' is ready.")


def setup_grammar(existing: list[str]):
    if GRAMMAR_MODEL_NAME in existing:
        update_grammar_model()
    else:
        create_grammar_model()
    print(f"Note type '{GRAMMAR_MODEL_NAME}' is ready.")


# ---------------------------------------------------------------------------
# UA_Visual — prefix spatial diagram cards
# ---------------------------------------------------------------------------

VISUAL_MODEL_NAME = "UA_Visual"

VISUAL_FIELDS = [
    "NoteID",
    "Prefix",
    "Meaning_EN",
    "Govt",
    "Walking_Pair",
    "Vehicle_Pair",
    "Example_UA",
    "Example_EN",
    "Diagram_SVG",
    "Tags_Ch",
    "Source_Note",
    "Verification Notes",  # stale in this constant until 2026-08-11 -- same
    # story as UA_Lexeme above: live model already had it, constant didn't list it.
]

VISUAL_CSS = """\
/* Gruvbox palette (github.com/morhetz/gruvbox) -- see the CSS constant
   above (UA_Lexeme) for the full rationale. .vis-prefix/.vis-govt are dead
   CSS (never referenced by VISUAL_FRONT_1/VISUAL_BACK_1's live markup, found
   2026-08-01) -- themed anyway rather than left untouched, same reasoning as
   the .conj table above. td:last-child (the live Prefix/Govt answer color)
   reuses Accent B blue, matching its role as the cross-reference/structural
   highlight elsewhere in the repo. This block previously set .nightMode
   .card to literal canonical Solarized base0/base03 rather than this repo's
   established dark-bg convention -- normalized here to match every other UA
   note type. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #fbf1c7; /* bg0 (light) */
  max-width: 580px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.nightMode .card {
  color: #ebdbb2; /* fg1 (dark primary) */
  background-color: #282828; /* bg0 (dark) */
}

.vis-prefix {
  font-size: 36px;
  font-weight: bold;
  color: #79740e; /* green (light) */
  margin: 10px 0 4px;
  letter-spacing: 1px;
}
.nightMode .vis-prefix { color: #b8bb26; } /* green (dark) */

.vis-meaning {
  font-size: 17px;
  color: #7c6f64; /* gray (light secondary) */
  margin-bottom: 8px;
}
.nightMode .vis-meaning { color: #a89984; } /* gray (dark secondary) */

.vis-govt {
  font-size: 20px;
  font-weight: 600;
  color: #076678; /* Accent B: blue (light) */
  background: #ebdbb2; /* bg1 (light highlight) */
  border-radius: 6px;
  padding: 4px 14px;
  display: inline-block;
  margin: 8px 0;
}
.nightMode .vis-govt { color: #83a598; background: #3c3836; } /* Accent B blue dark / bg1 dark */

.vis-pairs {
  font-size: 15px;
  color: #3c3836; /* fg1 (light primary) */
  margin: 6px 0;
  line-height: 1.6;
}
.nightMode .vis-pairs { color: #ebdbb2; } /* fg1 (dark primary) */

.vis-example {
  font-size: 16px;
  font-style: italic;
  color: #3c3836; /* fg1 (light primary) */
  margin-top: 10px;
}
.nightMode .vis-example { color: #ebdbb2; } /* fg1 (dark primary) */

.vis-example-en {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 2px;
}
.nightMode .vis-example-en { color: #a89984; } /* gray (dark secondary) */

/* Fixed table + column widths so the table renders at the SAME size on
   front (blank "?" placeholders) and back (real, longer answer text) --
   otherwise the narrower front content lets the table shrink and it visibly
   grows wider when flipped. Sized for the deck's longest Govt value
   (про-: "через + Зн.в. / повз + Зн.в.", ~29 chars), which wraps to 2 lines
   at this width rather than forcing the table wider. */
.vis-prompt-table {
  margin: 10px auto;
  border-collapse: collapse;
  font-size: 15px;
  width: 320px;
  table-layout: fixed;
}
.vis-prompt-table td {
  padding: 4px 12px;
  border-bottom: 1px solid #ebdbb2; /* bg1 (light highlight) */
  text-align: left;
  word-wrap: break-word;
}
.nightMode .vis-prompt-table td {
  border-bottom: 1px solid #3c3836; /* bg1 (dark highlight) */
}
.vis-prompt-table td:first-child {
  width: 130px;
  color: #7c6f64; /* gray (light secondary) */
}
.nightMode .vis-prompt-table td:first-child {
  color: #a89984; /* gray (dark secondary) */
}
.vis-prompt-table td:last-child {
  width: 190px;
  font-weight: 600;
  color: #076678; /* Accent B: blue (light) */
}
.nightMode .vis-prompt-table td:last-child {
  color: #83a598; /* Accent B: blue (dark) */
}

.note-id {
  font-size: 10px;
  color: #7c6f64; /* gray (light secondary) */
  text-align: right;
  margin-top: 14px;
}
.nightMode .note-id { color: #a89984; } /* gray (dark secondary) */

hr#answer {
  border: none;
  border-top: 2px solid #ebdbb2; /* bg1 (light highlight) */
  margin: 16px 0;
}
.nightMode hr#answer { border-top-color: #3c3836; } /* bg1 (dark highlight) */

/* Diagram SVGs: role-flip for night mode, matching whichever of the two
   text-tier hex values (light primary / light secondary) a given diagram
   was authored with -- see the .card / .vis-meaning color roles above.
   NOTE: no Diagram_SVG content exists in this checkout to verify against
   (see CLAUDE.md item 2's history) -- these selectors assume future
   diagrams embed fill/stroke as literal hex matching this file's light-mode
   text colors, the same assumption the pre-existing (Solarized-era) version
   of this rule made. Revisit if/when actual SVG content is authored. */
.nightMode .card svg [fill="#3c3836"] { fill: #ebdbb2; }
.nightMode .card svg [stroke="#3c3836"] { stroke: #ebdbb2; }
.nightMode .card svg [fill="#7c6f64"] { fill: #a89984; }
.nightMode .card svg [stroke="#7c6f64"] { stroke: #a89984; }
"""

# Single card: diagram + a 2-column table (prompt labels, blanks) on front.
# Back re-renders the SAME table in place with the answer column filled in --
# no {{FrontSide}} reproduction, no second table, no hr divider -- so it reads
# as one table getting filled in rather than a duplicate answer block below.
VISUAL_FRONT_1 = """\
<div>{{Diagram_SVG}}</div>
<table class="vis-prompt-table">
<tr><td>Verbal prefix?</td><td>?</td></tr>
<tr><td>Preposition + case?</td><td>?</td></tr>
</table>
"""

VISUAL_BACK_1 = """\
<div>{{Diagram_SVG}}</div>
<table class="vis-prompt-table">
<tr><td>Verbal prefix?</td><td>{{Prefix}}</td></tr>
<tr><td>Preposition + case?</td><td>{{Govt}}</td></tr>
</table>
<div class="vis-meaning">{{Meaning_EN}}</div>
<div class="vis-pairs">{{Walking_Pair}}<br>{{Vehicle_Pair}}</div>
{{#Example_UA}}<div class="vis-example">{{Example_UA}}</div>{{/Example_UA}}
{{#Example_EN}}<div class="vis-example-en">{{Example_EN}}</div>{{/Example_EN}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
"""

VISUAL_CARD_TEMPLATES = [
    {"Name": "Prefix + Government", "Front": VISUAL_FRONT_1, "Back": VISUAL_BACK_1},
]


def create_visual_model():
    print(f"Creating note type '{VISUAL_MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": VISUAL_MODEL_NAME,
            "inOrderFields": VISUAL_FIELDS,
            "css": VISUAL_CSS,
            "cardTemplates": VISUAL_CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_visual_model():
    print(f"Updating note type '{VISUAL_MODEL_NAME}'...")

    # NOTE: anki_request() here (tools/anki/sync/tsv_to_anki.py) already raises
    # RuntimeError on any AnkiConnect error -- it never returns an error dict to
    # check. For updateModelTemplates/updateModelStyling/modelTemplateAdd,
    # AnkiConnect's normal SUCCESS response is "result": null, i.e. Python
    # None -- that is not a failure signal, just these actions' empty return
    # value. If something actually goes wrong, this function raises and the
    # caller sees a full traceback instead of silently reporting "Updated".

    # Sync fields FIRST (add only) -- updateModelTemplates / modelTemplateAdd
    # validate that every {{Field}} referenced in a template already exists
    # on the model. Fixed here 2026-07-22 preventively, same bug class as
    # update_model() (UA_Lexeme), not yet actually triggered in this model.
    existing_fields = anki_request("modelFieldNames", {"modelName": VISUAL_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(VISUAL_FIELDS)

    for field in VISUAL_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # updateModelTemplates only refreshes Front/Back for template NAMES that
    # already exist on the model -- it silently no-ops for unrecognized new
    # names (see the identical bug class fixed in setup_ua_pvom_note_type.py).
    # A genuinely new template name needs modelTemplateAdd, which also
    # generates that card for every existing note of the model.
    existing_templates_resp = anki_request("modelTemplates", {"modelName": VISUAL_MODEL_NAME}, url=ANKI_URL)
    existing_template_names = list(existing_templates_resp.keys()) if existing_templates_resp else []

    for tmpl in VISUAL_CARD_TEMPLATES:
        if tmpl["Name"] not in existing_template_names:
            print(f"  Adding new template: {tmpl['Name']}")
            anki_request(
                "modelTemplateAdd",
                {
                    "modelName": VISUAL_MODEL_NAME,
                    "template": {"Name": tmpl["Name"], "Front": tmpl["Front"], "Back": tmpl["Back"]},
                },
                url=ANKI_URL,
            )

    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in VISUAL_CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": VISUAL_MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    anki_request(
        "updateModelStyling",
        {"model": {"name": VISUAL_MODEL_NAME, "css": VISUAL_CSS}},
        url=ANKI_URL,
    )

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # Enforce field order LAST -- see sync_field_order().
    sync_field_order(VISUAL_MODEL_NAME, VISUAL_FIELDS)

    obsolete_templates = [n for n in existing_template_names if n not in templates_dict]
    if obsolete_templates:
        print(
            f"  NOTE: old template(s) still on the model, not removed automatically "
            f"(removing a template deletes every card that uses it): {obsolete_templates}"
        )
        print(
            "  Decide whether to keep them or remove manually in Anki: "
            "Tools > Manage Note Types > Cards > Delete."
        )

    print("  Updated.")
    return True


def setup_visual(existing: list[str]):
    if VISUAL_MODEL_NAME in existing:
        ok = update_visual_model()
    else:
        create_visual_model()
        ok = True
    if ok:
        print(f"Note type '{VISUAL_MODEL_NAME}' is ready.")
    return ok


# ---------------------------------------------------------------------------
# UA_Verb — Verb conjugation paradigm note type
# ---------------------------------------------------------------------------

VERB_MODEL_NAME = "UA_Verb"

VERB_FIELDS = [
    # Identity & Metadata
    "NoteID",
    "Lemma",
    "Aspect",
    "VerbClass",
    "FreqSource",
    # Present tense (6 pronouns)
    "Pres_1sg",
    "Pres_2sg",
    "Pres_3sg",
    "Pres_1pl",
    "Pres_2pl",
    "Pres_3pl",
    # Imperatives (3 forms)
    "Imperative_2sg",
    "Imperative_1pl",
    "Imperative_2pl",
    # Past tense (4 forms)
    "Past_1sg_m",
    "Past_1sg_f",
    "Past_1sg_n",
    "Past_3pl",
    # Participles (5 forms)
    "Participle_Active_Present",
    "Participle_Adverbial_Present",
    "Participle_Passive_Past",
    "Participle_Impersonal_Past",
    "Participle_Adverbial_Past",
    # Metadata
    "Source_Note",
    "Verification Notes",  # unified 2026-08-11, per Craig -- was underscore-only
]

VERB_CSS = """\
/* Gruvbox palette (github.com/morhetz/gruvbox) -- see the CSS constant
   above (UA_Lexeme) for the full rationale. .verb-lemma reuses green
   (matching its pre-existing role as this template's headword accent);
   .section-title/.pronoun reuse Accent B blue, matching that color's role
   as the cross-reference/structural highlight elsewhere in the repo. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 16px;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #fbf1c7; /* bg0 (light) */
  max-width: 650px;
  margin: 0 auto;
  padding: 20px;
}

.verb-lemma {
  font-size: 32px;
  font-weight: bold;
  color: #79740e; /* green (light) */
  margin: 10px 0;
}

.verb-aspect {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-bottom: 14px;
  font-style: italic;
}

.verb-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 15px;
}

.verb-table th {
  background-color: #ebdbb2; /* bg1 (light highlight) */
  border: 1px solid #7c6f64; /* gray (light secondary) */
  padding: 8px;
  text-align: left;
  font-weight: 600;
  color: #3c3836; /* fg1 (light primary) */
}

.verb-table td {
  border: 1px solid #7c6f64; /* gray (light secondary) */
  padding: 8px;
  text-align: left;
}

.section-title {
  font-weight: 700;
  color: #076678; /* Accent B: blue (light) */
  background-color: #ebdbb2; /* bg1 (light highlight) */
  padding: 6px 10px;
  margin-top: 12px;
  margin-bottom: 6px;
  border-radius: 3px;
  font-size: 14px;
}

.verb-prompt {
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
  margin-top: 8px;
}

.note-id {
  font-size: 10px;
  color: #7c6f64; /* gray (light secondary) */
  text-align: right;
  margin-top: 14px;
}

hr#answer {
  border: none;
  border-top: 2px solid #7c6f64; /* gray (light secondary) */
  margin: 16px 0;
}

.verb-block {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1em;
  margin: 1em 0;
}

.person-block {
  border: 1px solid #7c6f64; /* gray (light secondary) */
  padding: 0.8em;
  border-radius: 4px;
  text-align: center;
}

.pronoun {
  font-weight: bold;
  color: #076678; /* Accent B: blue (light) */
  font-size: 0.9em;
  margin-bottom: 0.4em;
}

.form {
  font-size: 1.2em;
  color: #3c3836; /* fg1 (light primary) */
}

.tense-header {
  grid-column: 1 / -1;
  font-weight: bold;
  font-size: 1.1em;
  color: #3c3836; /* fg1 (light primary) */
  border-bottom: 2px solid #3c3836; /* fg1 (light primary) */
  padding-bottom: 0.5em;
  margin-bottom: 0.5em;
  margin-top: 1em;
}

.verb-block-single {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1em;
  margin: 1em 0;
}

.source-note {
  margin-top: 12px;
  font-size: 13px;
  color: #7c6f64; /* gray (light secondary) */
}

/* Dark mode (Gruvbox dark) */
.nightMode .card { color: #ebdbb2; background-color: #282828; } /* fg1 dark / bg0 dark */
.nightMode .source-note { color: #a89984; } /* gray (dark secondary) */
.nightMode .verb-lemma { color: #b8bb26; } /* green (dark) */
.nightMode .verb-aspect { color: #a89984; } /* gray (dark secondary) */
.nightMode .verb-table th { background-color: #3c3836; border-color: #a89984; color: #ebdbb2; } /* bg1 dark / gray dark / fg1 dark */
.nightMode .verb-table td { border-color: #a89984; } /* gray (dark secondary) */
.nightMode .section-title { color: #83a598; background-color: #3c3836; } /* Accent B blue dark / bg1 dark */
.nightMode .verb-prompt { color: #a89984; } /* gray (dark secondary) */
.nightMode .note-id { color: #a89984; } /* gray (dark secondary) */
.nightMode hr#answer { border-top-color: #a89984; } /* gray (dark secondary) */
.nightMode .person-block { border-color: #a89984; } /* gray (dark secondary) */
.nightMode .pronoun { color: #83a598; } /* Accent B: blue (dark) */
.nightMode .form { color: #ebdbb2; } /* fg1 (dark primary) */
.nightMode .tense-header { color: #ebdbb2; border-bottom-color: #a89984; } /* fg1 dark / gray dark */
"""

VERB_FRONT_RECOGNITION = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-aspect">{{Aspect}}</div>
<div class="verb-prompt">What is the full conjugation paradigm?</div>
"""

VERB_BACK_RECOGNITION = """\
{{FrontSide}}
<hr id="answer">

<div class="verb-block">
  <div class="tense-header">Теперішній час (Present)</div>
  <div class="person-block">
    <div class="pronoun">я</div>
    <div class="form">{{Pres_1sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">{{Pres_1pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">{{Pres_2sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">{{Pres_2pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">він/вона/воно</div>
    <div class="form">{{Pres_3sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">вони</div>
    <div class="form">{{Pres_3pl}}</div>
  </div>
</div>

<div class="verb-block-single">
  <div class="tense-header">Минулий час (Past)</div>
  <div class="person-block">
    <div class="pronoun">ч.р. (я/ти/він)</div>
    <div class="form">{{Past_1sg_m}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ж.р. (я/ти/вона)</div>
    <div class="form">{{Past_1sg_f}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">с.р. (воно)</div>
    <div class="form">{{Past_1sg_n}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">мн. (ми/ви/вони)</div>
    <div class="form">{{Past_3pl}}</div>
  </div>
</div>

<div class="verb-block-single">
  <div class="tense-header">Наказовий спосіб (Imperative)</div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">{{Imperative_2sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">{{Imperative_1pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">{{Imperative_2pl}}</div>
  </div>
</div>

<details>
  <summary class="section-title">Participles</summary>
  <table class="verb-table">
    <tr><td>Act. Pres.</td><td>{{Participle_Active_Present}}</td></tr>
    <tr><td>Adv. Pres.</td><td>{{Participle_Adverbial_Present}}</td></tr>
    <tr><td>Pass. Past</td><td>{{Participle_Passive_Past}}</td></tr>
    <tr><td>Impersonal</td><td>{{Participle_Impersonal_Past}}</td></tr>
    <tr><td>Adv. Past</td><td>{{Participle_Adverbial_Past}}</td></tr>
  </table>
</details>

{{#Source_Note}}<div class="source-note">{{Source_Note}}</div>{{/Source_Note}}
<div class="note-id">{{NoteID}} · {{Tags}}</div>
"""

VERB_FRONT_PRODUCTION_PRESENT = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Present (1sg→3pl): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block">
  <div class="tense-header">Теперішній час (Present)</div>
  <div class="person-block">
    <div class="pronoun">я</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">він/вона/воно</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">вони</div>
    <div class="form">_______</div>
  </div>
</div>
"""

VERB_BACK_PRODUCTION_PRESENT = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Present (1sg→3pl): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block">
  <div class="tense-header">Теперішній час (Present)</div>
  <div class="person-block">
    <div class="pronoun">я</div>
    <div class="form">{{Pres_1sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">{{Pres_1pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">{{Pres_2sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">{{Pres_2pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">він/вона/воно</div>
    <div class="form">{{Pres_3sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">вони</div>
    <div class="form">{{Pres_3pl}}</div>
  </div>
</div>
<div class="note-id">{{NoteID}}</div>
"""

VERB_FRONT_PRODUCTION_PAST = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Past (м/ж/с/мн): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Минулий час (Past)</div>
  <div class="person-block">
    <div class="pronoun">ч.р. (я/ти/він)</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ж.р. (я/ти/вона)</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">с.р. (воно)</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">мн. (ми/ви/вони)</div>
    <div class="form">_______</div>
  </div>
</div>
"""

VERB_BACK_PRODUCTION_PAST = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Past (м/ж/с/мн): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Минулий час (Past)</div>
  <div class="person-block">
    <div class="pronoun">ч.р. (я/ти/він)</div>
    <div class="form">{{Past_1sg_m}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ж.р. (я/ти/вона)</div>
    <div class="form">{{Past_1sg_f}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">с.р. (воно)</div>
    <div class="form">{{Past_1sg_n}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">мн. (ми/ви/вони)</div>
    <div class="form">{{Past_3pl}}</div>
  </div>
</div>
<div class="note-id">{{NoteID}}</div>
"""

VERB_FRONT_PRODUCTION_IMPERATIVE = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Imperative (ти/ми/ви): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Наказовий спосіб (Imperative)</div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">_______</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">_______</div>
  </div>
</div>
"""

VERB_BACK_PRODUCTION_IMPERATIVE = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Imperative (ти/ми/ви): Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Наказовий спосіб (Imperative)</div>
  <div class="person-block">
    <div class="pronoun">ти</div>
    <div class="form">{{Imperative_2sg}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ми</div>
    <div class="form">{{Imperative_1pl}}</div>
  </div>
  <div class="person-block">
    <div class="pronoun">ви</div>
    <div class="form">{{Imperative_2pl}}</div>
  </div>
</div>
<div class="note-id">{{NoteID}}</div>
"""

VERB_FRONT_PRODUCTION_PARTICIPLES = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Participles: Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Participles</div>
  {{#Participle_Active_Present}}
  <div class="person-block">
    <div class="pronoun">Act. Pres.</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Active_Present}}
  {{#Participle_Adverbial_Present}}
  <div class="person-block">
    <div class="pronoun">Adv. Pres.</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Adverbial_Present}}
  {{#Participle_Passive_Past}}
  <div class="person-block">
    <div class="pronoun">Pass. Past</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Passive_Past}}
  {{#Participle_Impersonal_Past}}
  <div class="person-block">
    <div class="pronoun">Impersonal</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Impersonal_Past}}
  {{#Participle_Adverbial_Past}}
  <div class="person-block">
    <div class="pronoun">Adv. Past</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Adverbial_Past}}
</div>
"""

VERB_BACK_PRODUCTION_PARTICIPLES = """\
<div class="verb-lemma">{{Lemma}}</div>
<div class="verb-prompt">Participles: Conjugate all forms</div>
<hr id="answer">
<div class="verb-block-single">
  <div class="tense-header">Participles</div>
  {{#Participle_Active_Present}}
  <div class="person-block">
    <div class="pronoun">Act. Pres.</div>
    <div class="form">{{Participle_Active_Present}}</div>
  </div>
  {{/Participle_Active_Present}}
  {{#Participle_Adverbial_Present}}
  <div class="person-block">
    <div class="pronoun">Adv. Pres.</div>
    <div class="form">{{Participle_Adverbial_Present}}</div>
  </div>
  {{/Participle_Adverbial_Present}}
  {{#Participle_Passive_Past}}
  <div class="person-block">
    <div class="pronoun">Pass. Past</div>
    <div class="form">{{Participle_Passive_Past}}</div>
  </div>
  {{/Participle_Passive_Past}}
  {{#Participle_Impersonal_Past}}
  <div class="person-block">
    <div class="pronoun">Impersonal</div>
    <div class="form">{{Participle_Impersonal_Past}}</div>
  </div>
  {{/Participle_Impersonal_Past}}
  {{#Participle_Adverbial_Past}}
  <div class="person-block">
    <div class="pronoun">Adv. Past</div>
    <div class="form">{{Participle_Adverbial_Past}}</div>
  </div>
  {{/Participle_Adverbial_Past}}
</div>
<div class="note-id">{{NoteID}}</div>
"""

VERB_CARD_TEMPLATES = [
    {"Name": "Production (Present)", "Front": VERB_FRONT_PRODUCTION_PRESENT, "Back": VERB_BACK_PRODUCTION_PRESENT},
    {"Name": "Production (Past)", "Front": VERB_FRONT_PRODUCTION_PAST, "Back": VERB_BACK_PRODUCTION_PAST},
    {"Name": "Production (Imperative)", "Front": VERB_FRONT_PRODUCTION_IMPERATIVE, "Back": VERB_BACK_PRODUCTION_IMPERATIVE},
    {"Name": "Production (Participles)", "Front": VERB_FRONT_PRODUCTION_PARTICIPLES, "Back": VERB_BACK_PRODUCTION_PARTICIPLES},
]


def create_verb_model():
    print(f"Creating note type '{VERB_MODEL_NAME}'...")
    anki_request(
        "createModel",
        {
            "modelName": VERB_MODEL_NAME,
            "inOrderFields": VERB_FIELDS,
            "css": VERB_CSS,
            "cardTemplates": VERB_CARD_TEMPLATES,
        },
        url=ANKI_URL,
    )
    print("  Created.")


def update_verb_model():
    print(f"Updating note type '{VERB_MODEL_NAME}'...")

    # Sync fields BEFORE templates -- see the comment in update_model() for
    # why (updateModelTemplates rejects templates referencing fields that
    # don't exist on the model yet). Fixed here 2026-07-22 preventively,
    # same bug class, not yet actually triggered in this model.
    existing_fields = anki_request("modelFieldNames", {"modelName": VERB_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(VERB_FIELDS)

    for field in VERB_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": VERB_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    templates_dict = {tmpl["Name"]: {"Front": tmpl["Front"], "Back": tmpl["Back"]} for tmpl in VERB_CARD_TEMPLATES}
    anki_request(
        "updateModelTemplates",
        {"model": {"name": VERB_MODEL_NAME, "templates": templates_dict}},
        url=ANKI_URL,
    )

    anki_request(
        "updateModelStyling",
        {"model": {"name": VERB_MODEL_NAME, "css": VERB_CSS}},
        url=ANKI_URL,
    )

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": VERB_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    # Enforce field order LAST -- see sync_field_order().
    sync_field_order(VERB_MODEL_NAME, VERB_FIELDS)

    print("  Updated.")


def setup_verb(existing: list[str]):
    if VERB_MODEL_NAME in existing:
        update_verb_model()
    else:
        create_verb_model()
    print(f"Note type '{VERB_MODEL_NAME}' is ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        choices=["UA_Lexeme", "UA_Grammar", "UA_Visual", "UA_Verb"],
        help="Set up only this model (default: all four)",
    )
    args = parser.parse_args()

    existing = get_existing_models()

    if args.model == "UA_Lexeme":
        setup_lexeme(existing)
    elif args.model == "UA_Grammar":
        setup_grammar(existing)
    elif args.model == "UA_Visual":
        setup_visual(existing)
    elif args.model == "UA_Verb":
        setup_verb(existing)
    else:
        setup_lexeme(existing)
        setup_grammar(existing)
        setup_visual(existing)
        setup_verb(existing)

    print("\nDone.")


if __name__ == "__main__":
    main()
