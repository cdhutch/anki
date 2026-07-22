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
    "Walking_Uni_UA",
    "Walking_Uni_Typing",
    "Vehicle_Multi_UA",
    "Vehicle_Multi_Typing",
    "Vehicle_Uni_UA",
    "Vehicle_Uni_Typing",
    "Tags_Ch",
    "Source_Note",
    "Verification_Notes",
]

FEEDBACK_SCRIPT = """\
<script>
(function() {
  var feedback = document.getElementById('feedback');
  var withStress = feedback.dataset.withStress;
  var noStress = feedback.dataset.noStress;

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
      typedAnswer = chunks.map(function(el) { return el.textContent; }).join('');
    }
    // Hide Anki's raw per-character diff here (answer side only -- this
    // script never runs on the front, so the front's input box is untouched).
    // It can visually detach combining stress marks from their base letter;
    // the #feedback message above is the intended user-facing display.
    typeansEl.style.display = 'none';
  }

  var html = '';

  if (typedAnswer === withStress) {
    html = '<div style="color: #2e7d32; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           withStress + ' ✓ PERFECT</div>' +
           '<div style="color: #2e7d32; font-size: 14px;">Correct with stress marks</div>';
  } else if (typedAnswer === noStress) {
    html = '<div style="color: #ff9800; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           noStress + ' ~ CORRECT</div>' +
           '<div style="color: #ff9800; font-size: 14px; margin-bottom: 12px;">Correct letters, missing stress</div>' +
           '<div style="color: #1565c0; font-size: 16px; font-weight: bold;">With stress:</div>' +
           '<div style="color: #1565c0; font-size: 18px;"><b>' + withStress + '</b></div>';
  } else if (typedAnswer !== null) {
    // Reconstruction succeeded and it's neither of the accepted answers --
    // genuinely wrong.
    html = '<div style="color: #d32f2f; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ✗ INCORRECT</div>' +
           '<div style="color: #d32f2f; font-size: 14px; margin-bottom: 12px;">Not quite right</div>' +
           '<div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 4px;">Correct answer:</div>' +
           '<div style="color: #1565c0; font-size: 18px;"><b>' + withStress + '</b></div>';
  } else {
    // Couldn't determine what was typed at all (e.g. #typeans markup ever
    // changes shape) -- show the answer neutrally rather than guessing.
    html = '<div style="color: #1565c0; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           withStress + '</div>' +
           '<div style="color: #999; font-size: 13px;">(no stress: ' + noStress + ')</div>';
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


def make_back(with_stress_field, no_stress_field):
    return (
        "{{FrontSide}}\n"
        '<hr id="answer">\n'
        '<div id="feedback" data-with-stress="{{' + with_stress_field + '}}" '
        'data-no-stress="{{' + no_stress_field + '}}" style="margin-bottom: 16px;"></div>\n'
        + FEEDBACK_SCRIPT
        + '<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e0e0e0; '
        'font-size: 12px; color: #999;">\n  {{Source_Note}}\n</div>\n'
    )


CARD_TEMPLATES = [
    {
        "name": "Walking (Multi)",
        # Typing target is the STRESSED field: typing it correctly is then a
        # clean exact match (no insertion); typing without stress becomes a
        # clean omission instead. Both are well-behaved for Anki's diff --
        # the reverse (unstressed target, stressed insertion) is not.
        "Front": make_front("ходити", "Walking_Multi_UA"),
        "Back": make_back("Walking_Multi_UA", "Walking_Multi_Typing"),
    },
    {
        "name": "Walking (Uni)",
        "Front": make_front("іти", "Walking_Uni_UA"),
        "Back": make_back("Walking_Uni_UA", "Walking_Uni_Typing"),
    },
    {
        "name": "Vehicle (Multi)",
        "Front": make_front("їздити", "Vehicle_Multi_UA"),
        "Back": make_back("Vehicle_Multi_UA", "Vehicle_Multi_Typing"),
    },
    {
        "name": "Vehicle (Uni)",
        "Front": make_front("їхати", "Vehicle_Uni_UA"),
        "Back": make_back("Vehicle_Uni_UA", "Vehicle_Uni_Typing"),
    },
]

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

hr#answer {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 20px 0;
}
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
