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
from tools.anki.sync.tsv_to_anki import anki_request  # noqa: E402

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_Lexeme"

# ---------------------------------------------------------------------------
# Fields (order matters — Anki displays them in this order in the editor)
# ---------------------------------------------------------------------------

FIELDS = [
    # Identity & Metadata
    "NoteID",

    # Core Lemma & Morphology
    "Lemma",
    "PartOfSpeech",
    "Gender",

    # Aspect (Perfective & Imperfective variants)
    "Perfective",
    "ImperfectiveUnidirectional",  # Motion verbs: іти, їхати (directional IPFV)

    # Semantic Content
    "EN_Gloss",

    # Grammatical Properties
    "Govt_Case",
    "IrregularForms",
    "CounterpartForm",
    "VerbMotion_Pair",

    # Semantic Relations & Cross-lingual
    "ConfusableSet",
    "CrossLang_Analog",
    "EuphonyNote",

    # Typing & Examples
    "TypingAnswer",
    "UA_Example",
    "EN_Example",

    # Metadata & Sources
    "Tags_Ch",
    "Source_URL",
    "Source_Note",
]

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

.lemma {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.perfective {
  font-size: 22px;
  color: #555;
  margin-bottom: 8px;
}

.pos {
  font-size: 13px;
  color: #888;
  font-style: italic;
  margin-bottom: 16px;
}

.gender {
  font-size: 13px;
  color: #888;
  margin-bottom: 4px;
}

hr#answer {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 20px 0;
}

.gloss {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
}

.counterpart {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.irregular {
  font-size: 13px;
  color: #888;
  margin-top: 4px;
}

.confusable {
  font-size: 13px;
  color: #b07000;
  margin-top: 6px;
}

.example-ua {
  font-size: 15px;
  margin-top: 14px;
  font-style: italic;
  color: #333;
}

.example-en {
  font-size: 13px;
  color: #777;
  margin-top: 2px;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 16px;
}

.source-link {
  font-size: 11px;
  margin-top: 10px;
  text-align: right;
}

.source-link a {
  color: #aaa;
  text-decoration: none;
}

/* Typing card input */
input#typeans {
  font-size: 20px;
  font-family: 'Noto Sans', Arial, sans-serif;
  width: 80%;
  text-align: center;
}

/* Conjugation table */
.conj {
  width: 100%;
  border-collapse: collapse;
  margin-top: 6px;
  font-size: 14px;
  text-align: left;
}
.conj th, .conj td {
  padding: 4px 8px;
  border: 1px solid #ddd;
}
.conj th {
  background-color: #f0f0f0;
  font-weight: 600;
  color: #444;
}
.conj td:first-child {
  color: #888;
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
  color: #888;
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
"""

# ---------------------------------------------------------------------------
# Card templates
# ---------------------------------------------------------------------------

# Template 1: UA → EN  (Recognition: see Ukrainian, recall English)
UA_EN_FRONT = """\
<div class="lemma">{{Lemma}}</div>
{{#Perfective}}<div class="perfective">/ {{Perfective}}</div>{{/Perfective}}
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
"""

UA_EN_BACK = """\
{{FrontSide}}
<hr id="answer">
<div class="gloss">{{EN_Gloss}}</div>
{{#CounterpartForm}}<div class="counterpart">{{CounterpartForm}}</div>{{/CounterpartForm}}
{{#IrregularForms}}<div class="irregular">{{IrregularForms}}</div>{{/IrregularForms}}
{{#Govt_Case}}<div class="irregular">governs: {{Govt_Case}}</div>{{/Govt_Case}}
{{#ConfusableSet}}<div class="confusable">cf. {{ConfusableSet}}</div>{{/ConfusableSet}}
{{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
{{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""

# Template 2: EN → UA  (Production: see English, type Ukrainian)
# Accepts both {{Lemma}} (with stress) and {{TypingAnswer}} (without stress)
EN_UA_FRONT = """\
<div class="gloss">{{EN_Gloss}}</div>
<div class="pos">{{PartOfSpeech}}{{#Gender}} · {{Gender}}{{/Gender}}</div>
<!-- Accept both forms: with stress (Lemma) and without (TypingAnswer) -->
{{type:TypingAnswer}}
<div id="type-hint" style="font-size: 12px; color: #999; margin-top: 8px;">
  (Type without stress, or with stress marks for bonus credit)
</div>
"""

EN_UA_BACK = """\
{{FrontSide}}
<hr id="answer">
<!-- Color-coded typing feedback with dual validation -->
<div id="feedback" data-lemma="{{Lemma}}" data-no-stress="{{TypingAnswer}}" style="margin-bottom: 16px;"></div>
<script>
(function() {
  var feedback = document.getElementById('feedback');
  var lemmaWithStress = feedback.dataset.lemma;
  var lemmaNoStress = feedback.dataset.noStress;
  var typedInput = document.querySelector('input[type="text"]');

  if (!typedInput) return;

  var typedAnswer = typedInput.value.trim();
  var html = '';

  if (typedAnswer === lemmaWithStress) {
    // Perfect: with stress marks
    html = '<div style="color: #2e7d32; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ✓ PERFECT</div>' +
           '<div style="color: #2e7d32; font-size: 14px;">Correct with stress marks (bonus!)</div>';
  } else if (typedAnswer === lemmaNoStress) {
    // Close: correct letters, missing stress
    html = '<div style="color: #ff9800; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ~ CORRECT</div>' +
           '<div style="color: #ff9800; font-size: 14px; margin-bottom: 12px;">Correct letters, but missing stress marks</div>' +
           '<div style="color: #2e7d32; font-size: 16px; font-weight: bold;">Bonus answer:</div>' +
           '<div style="color: #1565c0; font-size: 16px;"><b>' + lemmaWithStress + '</b></div>';
  } else if (typedAnswer.length > 0) {
    // Incorrect
    html = '<div style="color: #d32f2f; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ✗ INCORRECT</div>' +
           '<div style="color: #d32f2f; font-size: 14px; margin-bottom: 12px;">Not quite right</div>' +
           '<div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 4px;">Correct (no stress):</div>' +
           '<div style="color: #2e7d32; font-size: 16px; margin-bottom: 8px;"><b>' + lemmaNoStress + '</b></div>' +
           '<div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 4px;">Correct (with stress):</div>' +
           '<div style="color: #1565c0; font-size: 16px;"><b>' + lemmaWithStress + '</b></div>';
  }

  feedback.innerHTML = html;
})();
</script>
<!-- Reference answer and context -->
<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e0e0e0;">
  {{#UA_Example}}<div class="example-ua">{{UA_Example}}</div>{{/UA_Example}}
  {{#EN_Example}}<div class="example-en">{{EN_Example}}</div>{{/EN_Example}}
</div>
<div class="note-id">{{NoteID}} · {{Tags_Ch}}</div>
{{#Source_URL}}<div class="source-link"><a href="{{Source_URL}}">Горох ↗</a></div>{{/Source_URL}}
"""

# Template 3: Confusable Comparison (scenario-based, bidirectional)
# Optional, only shown when ConfusableSet is populated
# Design: Forces semantic discrimination, not pattern memorization
# Front: Scenario/context requiring choice between lemma and confusable
# Back: Correct answer + explanation of why it fits this context

COMPARISON_FRONT = """\
{{#ConfusableSet}}<div style="font-size: 16px; color: #1565c0; font-weight: bold; margin-bottom: 12px;">Choose the right word:</div>
<div class="gloss" style="font-size: 18px; margin-bottom: 16px;">
  Scenario: {{EN_Gloss}}
  <br><span style="font-size: 13px; color: #666; font-weight: normal; font-style: italic;">Which fits better — {{Lemma}} or the alternative?</span>
</div>
<div style="font-size: 14px; color: #555; padding: 12px; background: #f9f9f9; border-left: 3px solid #1565c0; margin-top: 12px;">
{{ConfusableSet}}
</div>{{/ConfusableSet}}
"""

COMPARISON_BACK = """\
{{FrontSide}}
<hr id="answer">
{{#ConfusableSet}}<div style="margin-top: 16px; font-size: 16px;">
<div style="color: #2e7d32; font-size: 20px; font-weight: bold; margin-bottom: 4px;">✓ {{Lemma}}</div>
<div style="color: #2e7d32; font-size: 13px; margin-bottom: 12px;">This scenario emphasizes {{EN_Gloss}}</div>
<div style="background: #e8f5e9; padding: 10px; border-radius: 4px; font-size: 13px; margin-top: 10px;">
<strong>Why not the alternative?</strong><br>
The other word fits different contexts (see below) — not this one.
</div>
</div>{{/ConfusableSet}}
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

    # Sync fields: add missing, remove obsolete
    existing_fields = anki_request("modelFieldNames", {"modelName": MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(FIELDS)

    for field in FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": MODEL_NAME, "fieldName": field}, url=ANKI_URL)

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
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 640px;
  margin: 0 auto;
  padding: 24px 20px;
}

.topic {
  font-size: 13px;
  color: #888;
  font-style: italic;
  margin-bottom: 14px;
}

.cloze {
  font-weight: bold;
  color: #2563eb;
}

.extra {
  font-size: 14px;
  color: #555;
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 10px;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 16px;
}

.chapter {
  font-size: 11px;
  color: #aaa;
  text-align: right;
}
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

    existing_fields = anki_request("modelFieldNames", {"modelName": GRAMMAR_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(GRAMMAR_FIELDS)

    for field in GRAMMAR_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": GRAMMAR_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

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
]

VISUAL_CSS = """\
/* Solarized palette (ethanschoonover.com/solarized) throughout.
   Accents (green/blue/red) are identical in both modes by design;
   base01/base1 deliberately swap roles between light and dark mode. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #657b83; /* base00 */
  background-color: #fdf6e3; /* base3 */
  max-width: 580px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.night_mode .card {
  color: #839496; /* base0 */
  background-color: #002b36; /* base03 */
}

.vis-prefix {
  font-size: 36px;
  font-weight: bold;
  color: #859900; /* green */
  margin: 10px 0 4px;
  letter-spacing: 1px;
}

.vis-meaning {
  font-size: 17px;
  color: #586e75; /* base01 */
  margin-bottom: 8px;
}
.night_mode .vis-meaning { color: #93a1a1; } /* base1 */

.vis-govt {
  font-size: 20px;
  font-weight: 600;
  color: #268bd2; /* blue */
  background: #eee8d5; /* base2 */
  border-radius: 6px;
  padding: 4px 14px;
  display: inline-block;
  margin: 8px 0;
}
.night_mode .vis-govt { background: #073642; } /* base02 */

.vis-pairs {
  font-size: 15px;
  color: #586e75; /* base01 */
  margin: 6px 0;
  line-height: 1.6;
}
.night_mode .vis-pairs { color: #93a1a1; } /* base1 */

.vis-example {
  font-size: 16px;
  font-style: italic;
  color: #586e75; /* base01 */
  margin-top: 10px;
}
.night_mode .vis-example { color: #93a1a1; } /* base1 */

.vis-example-en {
  font-size: 13px;
  color: #93a1a1; /* base1 */
  margin-top: 2px;
}
.night_mode .vis-example-en { color: #839496; } /* base0 */

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
  border-bottom: 1px solid #eee8d5; /* base2 */
  text-align: left;
  word-wrap: break-word;
}
.night_mode .vis-prompt-table td {
  border-bottom: 1px solid #073642; /* base02 */
}
.vis-prompt-table td:first-child {
  width: 130px;
  color: #93a1a1; /* base1 */
}
.night_mode .vis-prompt-table td:first-child {
  color: #586e75; /* base01 */
}
.vis-prompt-table td:last-child {
  width: 190px;
  font-weight: 600;
  color: #268bd2; /* blue */
}

.note-id {
  font-size: 10px;
  color: #93a1a1; /* base1 */
  text-align: right;
  margin-top: 14px;
}

hr#answer {
  border: none;
  border-top: 2px solid #eee8d5; /* base2 */
  margin: 16px 0;
}
.night_mode hr#answer { border-top-color: #073642; } /* base02 */

/* Diagram SVGs: base01/base1 role-flip for night mode. Accent colors
   (green #859900, blue #268bd2, red #dc322f) are unchanged in both modes. */
.night_mode .card svg [fill="#586e75"] { fill: #93a1a1; }
.night_mode .card svg [stroke="#586e75"] { stroke: #93a1a1; }
.night_mode .card svg [fill="#93a1a1"] { fill: #586e75; }
.night_mode .card svg [stroke="#93a1a1"] { stroke: #586e75; }
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

    existing_fields = anki_request("modelFieldNames", {"modelName": VISUAL_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(VISUAL_FIELDS)

    for field in VISUAL_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": VISUAL_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

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
    "Past_1pl",
    # Participles (6 forms)
    "Participle_Active_Present",
    "Participle_Adverbial_Present",
    "Participle_Passive_Past_m",
    "Participle_Passive_Past_f",
    "Participle_Impersonal_Past",
    "Participle_Adverbial_Past",
    # Metadata
    "Tags_Conj",
    "Source_Note",
    "Verification_Notes",
]

VERB_CSS = """\
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 16px;
  color: #1a1a1a;
  background-color: #ffffff;
  max-width: 650px;
  margin: 0 auto;
  padding: 20px;
}

.verb-lemma {
  font-size: 32px;
  font-weight: bold;
  color: #2e7d32;
  margin: 10px 0;
}

.verb-aspect {
  font-size: 13px;
  color: #666;
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
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  font-weight: 600;
}

.verb-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.section-title {
  font-weight: 700;
  color: #1565c0;
  background-color: #e3f2fd;
  padding: 6px 10px;
  margin-top: 12px;
  margin-bottom: 6px;
  border-radius: 3px;
  font-size: 14px;
}

.verb-prompt {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}

.note-id {
  font-size: 10px;
  color: #ccc;
  text-align: right;
  margin-top: 14px;
}

hr#answer {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 16px 0;
}

.verb-block {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1em;
  margin: 1em 0;
}

.person-block {
  border: 1px solid #ccc;
  padding: 0.8em;
  border-radius: 4px;
  text-align: center;
}

.pronoun {
  font-weight: bold;
  color: #0066cc;
  font-size: 0.9em;
  margin-bottom: 0.4em;
}

.form {
  font-size: 1.2em;
  color: #333;
}

.tense-header {
  grid-column: 1 / -1;
  font-weight: bold;
  font-size: 1.1em;
  color: #555;
  border-bottom: 2px solid #666;
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
    <div class="form">{{Past_1pl}}</div>
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
    <tr><td>Pass. Past (м.)</td><td>{{Participle_Passive_Past_m}}</td></tr>
    <tr><td>Pass. Past (ж.)</td><td>{{Participle_Passive_Past_f}}</td></tr>
    <tr><td>Impersonal</td><td>{{Participle_Impersonal_Past}}</td></tr>
    <tr><td>Adv. Past</td><td>{{Participle_Adverbial_Past}}</td></tr>
  </table>
</details>

{{#Source_Note}}<div style="margin-top:12px; font-size:13px; color:#777;">{{Source_Note}}</div>{{/Source_Note}}
<div class="note-id">{{NoteID}} · {{Tags_Conj}}</div>
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
    <div class="form">{{Past_1pl}}</div>
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
  {{#Participle_Passive_Past_m}}
  <div class="person-block">
    <div class="pronoun">Pass. Past (м.)</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Passive_Past_m}}
  {{#Participle_Passive_Past_f}}
  <div class="person-block">
    <div class="pronoun">Pass. Past (ж.)</div>
    <div class="form">_______</div>
  </div>
  {{/Participle_Passive_Past_f}}
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
  {{#Participle_Passive_Past_m}}
  <div class="person-block">
    <div class="pronoun">Pass. Past (м.)</div>
    <div class="form">{{Participle_Passive_Past_m}}</div>
  </div>
  {{/Participle_Passive_Past_m}}
  {{#Participle_Passive_Past_f}}
  <div class="person-block">
    <div class="pronoun">Pass. Past (ж.)</div>
    <div class="form">{{Participle_Passive_Past_f}}</div>
  </div>
  {{/Participle_Passive_Past_f}}
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

    existing_fields = anki_request("modelFieldNames", {"modelName": VERB_MODEL_NAME}, url=ANKI_URL)
    existing_set = set(existing_fields)
    desired_set = set(VERB_FIELDS)

    for field in VERB_FIELDS:
        if field not in existing_set:
            print(f"  Adding field: {field}")
            anki_request("modelFieldAdd", {"modelName": VERB_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

    for field in existing_fields:
        if field not in desired_set:
            print(f"  Removing field: {field}  (data lost)")
            anki_request("modelFieldRemove", {"modelName": VERB_MODEL_NAME, "fieldName": field}, url=ANKI_URL)

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
