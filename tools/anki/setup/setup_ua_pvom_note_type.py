#!/usr/bin/env python3
"""Create/update UA_PVOM_Infinitive note type in Anki via AnkiConnect.

Each note represents one prefix and drills all four verb-of-motion base
forms it combines with:
  - Walking, multidirectional, imperfective (ходити-family)
  - Walking, unidirectional, perfective (іти-family)
  - Vehicle, multidirectional, imperfective (labeled "їздити" on the card;
    the attested/dictionary-primary surface form is usually -їжджати)
  - Vehicle, unidirectional, perfective (їхати-family)

Front always reads "{Prefix} + {base label}"; the student types the
correctly prefixed/mutated form. Four separate card templates (one per
base) give each form independent FSRS scheduling.
"""

import json
import urllib.request
import sys

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_PVOM_Infinitive"

FIELDS = [
    "NoteID",
    "Prefix",
    "Walking_Multi_UA",
    "Walking_Multi_Typing",
    "Walking_Multi_Euphony",
    "Walking_Uni_UA",
    "Walking_Uni_Typing",
    "Walking_Uni_Euphony",
    "Vehicle_Multi_UA",
    "Vehicle_Multi_Typing",
    "Vehicle_Multi_Euphony",
    "Vehicle_Uni_UA",
    "Vehicle_Uni_Typing",
    "Vehicle_Uni_Euphony",
    "Tags_Ch",
    "Source_Note",
    "Verification Notes",  # unified 2026-08-11, per Craig -- was underscore-only
]

FEEDBACK_SCRIPT = """\
<script>
(function() {
  var feedback = document.getElementById('feedback');
  var withStress = feedback.dataset.withStress;
  var noStress = feedback.dataset.noStress;

  // EuphonyNote acceptance (added 2026-07-25, ported from UA_Lexeme's EN_UA_BACK) --
  // bare/pipe-delimited alternates, stress-stripped + NFC-normalized before comparison.
  function stripStress(s) { return s.replace(/\u0301/g, ''); }

  // Strip Anki's combining-mark isolation artifact out of a reconstructed
  // #typeans string (added 2026-08-18) -- mirror of normalizeTypeansText() in
  // setup_ua_note_types.py's EN_UA_BACK; see that copy for the full writeup.
  // Short version: Anki's isolate_leading_mark() (rslib/src/typeanswer.rs)
  // deliberately prepends U+00A0 to any diff chunk BEGINNING with a combining
  // mark, and that nbsp lands inside a .typeGood/.typeBad span, so the
  // reconstruction below swallows it. Found on UA_Lexeme (ua-lexeme-0532,
  // 2026-08-08); this script uses the identical reconstruction technique, so
  // it has the identical bug -- every PVOM typing answer carries a stress
  // mark, so any stress-position mismatch here hits it too.
  function normalizeTypeansText(s) {
    return s.replace(/\\u00A0([\\u0300-\\u036F])/g, '$1').replace(/\\u00A0/g, ' ');
  }
  var euphonyRaw = feedback.dataset.euphony || '';
  var euphonyAlts = euphonyRaw.split('|')
    .map(function(s) { return stripStress(s.trim()).normalize('NFC'); })
    .filter(function(s) { return s.length > 0; });

  // Anki's own type-answer field replaces the front's <input> with a #typeans
  // diff (spans classed typeGood/typeBad/typeMissed) once the answer side
  // renders -- there is no live <input> to read here. Reconstruct what was
  // typed from that diff for the bonus stress-tier message, but ALWAYS show
  // the plain answer regardless of whether that reconstruction matches
  // Anki's exact markup, so the correct form is never left blank.
  // When the typed answer isn't a perfect match, Anki renders TWO lines
  // inside #typeans: the "what you typed" line, a <span id="typearrow">
  // separator, then the "correct answer" line -- both lines reuse the same
  // typeGood/typeBad classes. We only want the first line; otherwise the
  // correct-answer line's matching chars get concatenated in too, doubling
  // the reconstructed text. (Exact matches render as a single line with no
  // #typearrow at all.)
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
      );
    }
    // Hide Anki's raw per-character diff here (answer side only -- this
    // script never runs on the front, so the front's input box is untouched).
    // It can visually detach combining stress marks from their base letter;
    // the #feedback message above is the intended user-facing display.
    typeansEl.style.display = 'none';
  }

  var html = '';

  if (typedAnswer === withStress) {
    html = '<div class="fb-headline status-success">' +
           withStress + ' ✓ PERFECT</div>' +
           '<div class="fb-sub status-success">Correct with stress marks</div>';
  } else if (typedAnswer === noStress) {
    html = '<div class="fb-headline status-warning">' +
           noStress + ' ~ CORRECT</div>' +
           '<div class="fb-sub status-warning">Correct letters, missing stress</div>' +
           '<div class="fb-label status-info">With stress:</div>' +
           '<div class="fb-value status-info"><b>' + withStress + '</b></div>';
  } else if (typedAnswer !== null && euphonyAlts.indexOf(stripStress(typedAnswer).normalize('NFC')) !== -1) {
    // Accepted alternate spelling (*_Euphony) -- genuinely correct, not just noted.
    html = '<div class="fb-headline status-success">' +
           typedAnswer + ' ✓ CORRECT</div>' +
           '<div class="fb-sub status-success">Accepted alternate spelling</div>' +
           '<div class="fb-label status-info">Primary form:</div>' +
           '<div class="fb-value status-info"><b>' + withStress + '</b></div>';
  } else if (typedAnswer !== null) {
    // Reconstruction succeeded and it's neither of the accepted answers --
    // genuinely wrong.
    html = '<div class="fb-headline status-error">' +
           typedAnswer + ' ✗ INCORRECT</div>' +
           '<div class="fb-sub status-error">Not quite right</div>' +
           '<div class="fb-label status-info">Correct answer:</div>' +
           '<div class="fb-value status-info"><b>' + withStress + '</b></div>';
  } else {
    // Couldn't determine what was typed at all (e.g. #typeans markup ever
    // changes shape) -- show the answer neutrally rather than guessing.
    html = '<div class="fb-headline status-info">' +
           withStress + '</div>' +
           '<div class="fb-note status-neutral">(no stress: ' + noStress + ')</div>';
  }

  feedback.innerHTML = html;
})();
</script>
"""


def make_front(label, typing_field):
    return (
        '<div style="font-size: 26px; margin-bottom: 12px;">{{Prefix}} + '
        + label
        + "</div>\n{{type:" + typing_field + "}}\n"
    )


def make_back(with_stress_field, no_stress_field, euphony_field):
    return (
        "{{FrontSide}}\n"
        '<hr id="answer">\n'
        '<div id="feedback" data-with-stress="{{' + with_stress_field + '}}" '
        'data-no-stress="{{' + no_stress_field + '}}" '
        'data-euphony="{{' + euphony_field + '}}" style="margin-bottom: 16px;"></div>\n'
        + FEEDBACK_SCRIPT
        + '<div class="source-note">\n  {{Source_Note}}\n</div>\n'
    )


CARD_TEMPLATES = [
    {
        "name": "Walking (Multi)",
        # Typing target is the STRESSED field: typing it correctly is then a
        # clean exact match (no insertion); typing without stress becomes a
        # clean omission instead. Both are well-behaved for Anki's diff --
        # the reverse (unstressed target, stressed insertion) is not.
        "Front": make_front("ходити", "Walking_Multi_UA"),
        "Back": make_back("Walking_Multi_UA", "Walking_Multi_Typing", "Walking_Multi_Euphony"),
    },
    {
        "name": "Walking (Uni)",
        "Front": make_front("іти", "Walking_Uni_UA"),
        "Back": make_back("Walking_Uni_UA", "Walking_Uni_Typing", "Walking_Uni_Euphony"),
    },
    {
        "name": "Vehicle (Multi)",
        "Front": make_front("їздити", "Vehicle_Multi_UA"),
        "Back": make_back("Vehicle_Multi_UA", "Vehicle_Multi_Typing", "Vehicle_Multi_Euphony"),
    },
    {
        "name": "Vehicle (Uni)",
        "Front": make_front("їхати", "Vehicle_Uni_UA"),
        "Back": make_back("Vehicle_Uni_UA", "Vehicle_Uni_Typing", "Vehicle_Uni_Euphony"),
    },
]

CSS = """\
/* Gruvbox palette (github.com/morhetz/gruvbox) -- see setup_ua_note_types.py's
   CSS constant (UA_Lexeme) for the full palette rationale. This note type
   had ZERO .nightMode support before 2026-08-01; the fb-*/status-* classes
   below are kept in sync (by hand) with setup_ua_note_types.py's identical
   classes so the typing-feedback script here and EN_UA_BACK's script look
   the same across the whole UA domain, day/night/red-tint alike. */
.card {
  font-family: 'Noto Sans', Arial, sans-serif;
  font-size: 18px;
  color: #3c3836; /* fg1 (light primary) */
  background-color: #fbf1c7; /* bg0 (light) */
  max-width: 600px;
  margin: 0 auto;
  padding: 24px 20px;
  text-align: center;
}

hr#answer {
  border: none;
  border-top: 2px solid #7c6f64; /* gray (light secondary) */
  margin: 20px 0;
}

.source-note {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #7c6f64; /* gray (light secondary) */
  font-size: 12px;
  color: #7c6f64; /* gray (light secondary) */
}

/* Status/feedback system -- see FEEDBACK_SCRIPT above. status-warning stays
   orange (not Gruvbox's yellow) so the "close/partial-credit" state keeps
   its original color family (was #ff9800) -- per Craig 2026-08-01: keep
   status colors close to current, while making sure red/orange don't wash
   out under the red-tint night filter, hence using Gruvbox's *bright*-tier
   red/orange for dark mode below (not the muted/neutral tier) for maximum
   luminance contrast against the dark background. */
.fb-headline { font-size: 22px; font-weight: bold; margin-bottom: 4px; }
.fb-sub { font-size: 14px; margin-bottom: 12px; }
.fb-label { font-size: 16px; font-weight: bold; margin-bottom: 4px; }
.fb-value { font-size: 16px; }
.fb-note { font-size: 13px; }

.status-success { color: #79740e; } /* green (light) */
.status-error { color: #9d0006; } /* red (light) */
.status-warning { color: #af3a03; } /* orange (light) */
.status-info { color: #076678; } /* blue (light) */
.status-neutral { color: #7c6f64; } /* gray (light secondary) */

/* Dark mode (Gruvbox dark) */
.nightMode .card { color: #ebdbb2; background-color: #282828; } /* fg1 dark / bg0 dark */
.nightMode hr#answer { border-top-color: #a89984; } /* gray (dark secondary) */
.nightMode .source-note { border-top-color: #a89984; color: #a89984; } /* gray (dark secondary) */
.nightMode .status-success { color: #b8bb26; } /* green, bright tier (dark) */
.nightMode .status-error { color: #fb4934; } /* red, bright tier (dark) */
.nightMode .status-warning { color: #fe8019; } /* orange, bright tier (dark) */
.nightMode .status-info { color: #83a598; } /* blue, bright tier (dark) */
.nightMode .status-neutral { color: #a89984; } /* gray (dark secondary) */
"""


def anki_request(action, params=None):
    """Send request to AnkiConnect."""
    request_body = {"action": action, "version": 6}
    if params:
        request_body["params"] = params

    try:
        response = urllib.request.urlopen(
            urllib.request.Request(
                ANKI_URL,
                data=json.dumps(request_body).encode("utf-8"),
            )
        )
        result = json.loads(response.read())
        if result and result.get("error"):
            print(f"AnkiConnect error: {result['error']}", file=sys.stderr)
        return result
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def sync_field_order(desired_fields):
    """Reposition the live model's fields to match `desired_fields` exactly.

    Added 2026-08-18 -- mirror of sync_field_order() in
    setup_ua_note_types.py; see that function's docstring for the full
    rationale. Short version: `inOrderFields` only applies at createModel, and
    `modelFieldAdd` APPENDS, so before this existed the FIELDS constant above
    had no bearing on an already-created model's field order. Live
    UA_PVOM_Infinitive showed the resulting drift directly -- Tags_Ch /
    Source_Note / Verification Notes sat at positions 3-5 with all four
    *_Euphony fields appended after the typing fields at the very end.

    Guarded: no AnkiConnect calls at all when the order already matches, so
    routine runs don't re-trigger Anki's full-upload prompt. Must run AFTER
    the field-add pass, which changes the live order.

    Note this script's anki_request() returns the raw AnkiConnect envelope
    (not the unwrapped result, unlike setup_ua_note_types.py's import from
    tsv_to_anki) -- hence the .get("result") unwrapping here.
    """
    live = anki_request("modelFieldNames", {"modelName": MODEL_NAME})
    live_fields = live.get("result", []) if live else []
    target = [f for f in desired_fields if f in set(live_fields)]

    # Leading-slice comparison, not filtered relative order -- the constant's
    # fields must occupy indices 0..len(target)-1. This script intentionally
    # leaves stale fields in place (see the stale_fields note in setup_model),
    # so those trail after everything the constant names rather than staying
    # wedged wherever they happen to sit.
    if live_fields[: len(target)] == target:
        return False

    print("  Field order differs from this script's FIELDS constant -- repositioning...")
    print("    NOTE: reordering fields is a schema change. Anki may ask for a full")
    print("    upload on your next AnkiWeb sync. No note data is lost -- values move")
    print("    with their field. Subsequent runs are a no-op once order matches.")
    for index, field in enumerate(target):
        anki_request(
            "modelFieldReposition",
            {"modelName": MODEL_NAME, "fieldName": field, "index": index},
        )
    print(f"    Repositioned {len(target)} field(s).")
    return True


def ensure_deck():
    """Ensure the deck exists."""
    anki_request("createDeck", {"deck": "UA::Recognition::PVOM"})
    print("✓ Deck UA::Recognition::PVOM ensured")


def setup_model():
    """Create or update UA_PVOM_Infinitive model."""
    existing = anki_request("modelNames")
    model_names = existing.get("result", []) if existing else []

    templates_dict = {t["name"]: {"Front": t["Front"], "Back": t["Back"]} for t in CARD_TEMPLATES}

    if MODEL_NAME in model_names:
        print(f"✓ Model '{MODEL_NAME}' exists, updating...")

        existing_fields = anki_request("modelFieldNames", {"modelName": MODEL_NAME})
        existing_fields = existing_fields.get("result", []) if existing_fields else []
        for field in FIELDS:
            if field not in existing_fields:
                print(f"  Adding field: {field}")
                anki_request("modelFieldAdd", {"modelName": MODEL_NAME, "fieldName": field})

        stale_fields = [f for f in existing_fields if f not in FIELDS]
        if stale_fields:
            print(
                "  NOTE: these fields are no longer used by this script and were left "
                f"in place (AnkiConnect can't safely auto-remove fields with existing "
                f"card data): {stale_fields}"
            )
            print(
                "  If you want them gone, remove manually in Anki: "
                "Tools > Manage Note Types > Fields > Delete."
            )

        # Enforce field order AFTER the add pass above (which appends, and so
        # changes the live order out from under this). Stale fields the script
        # deliberately leaves in place settle at the end. See sync_field_order().
        sync_field_order(FIELDS)

        # updateModelTemplates only refreshes Front/Back for templates that ALREADY
        # exist under that exact name -- it silently does nothing for names it doesn't
        # recognize. Genuinely new templates need modelTemplateAdd, which (unlike
        # fields) DOES trigger Anki to generate the new card for every existing note
        # of this model automatically -- that's normal Anki template-add behavior.
        existing_templates_resp = anki_request("modelTemplates", {"modelName": MODEL_NAME})
        existing_template_names = (
            list(existing_templates_resp.get("result", {}).keys()) if existing_templates_resp else []
        )

        ok = True

        for t in CARD_TEMPLATES:
            if t["name"] not in existing_template_names:
                print(f"  Adding new template: {t['name']}")
                result = anki_request(
                    "modelTemplateAdd",
                    {
                        "modelName": MODEL_NAME,
                        "template": {"Name": t["name"], "Front": t["Front"], "Back": t["Back"]},
                    },
                )
                if not result or result.get("error"):
                    ok = False

        result = anki_request(
            "updateModelTemplates",
            {"model": {"name": MODEL_NAME, "templates": templates_dict}},
        )
        if not result or result.get("error"):
            ok = False

        result = anki_request(
            "updateModelStyling",
            {"model": {"name": MODEL_NAME, "css": CSS}},
        )
        if not result or result.get("error"):
            ok = False

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

        if not ok:
            print(
                f"✗ One or more AnkiConnect calls failed (see 'AnkiConnect error' lines "
                f"above) -- '{MODEL_NAME}' templates/styling were NOT fully updated.",
                file=sys.stderr,
            )
            return False

        print(f"✓ Updated '{MODEL_NAME}' templates and styling")
        return True

    else:
        print(f"Creating model '{MODEL_NAME}'...")
        model_spec = {
            "modelName": MODEL_NAME,
            "inOrderFields": FIELDS,
            "cardTemplates": CARD_TEMPLATES,
            "css": CSS,
        }

        result = anki_request("createModel", model_spec)
        if result and not result.get("error"):
            print(f"✓ Created model '{MODEL_NAME}'")
            return True
        else:
            print(f"✗ Failed to create model: {result}", file=sys.stderr)
            return False


if __name__ == "__main__":
    ensure_deck()
    if setup_model():
        print(f"\n✓ UA_PVOM_Infinitive note type ready")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to set up note type", file=sys.stderr)
        sys.exit(1)
