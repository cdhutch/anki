#!/usr/bin/env python3
"""Create/update UA_PVOM_Infinitive note type in Anki via AnkiConnect."""

import json
import urllib.request
import sys

ANKI_URL = "http://127.0.0.1:8765"
MODEL_NAME = "UA_PVOM_Infinitive"

FIELDS = [
    "NoteID",
    "Prefix",
    "Base_Form_Label",
    "Infinitive_UA",
    "TypingAnswer",
    "Tags_Ch",
    "Source_Note",
    "Verification_Notes",
]

# Typing template with JavaScript feedback (matches UA_Lexeme pattern)
FRONT = """\
<div style="font-size: 24px; margin-bottom: 12px;">{{Prefix}}<span style="font-size: 18px; color: #666;"> [{{Base_Form_Label}}]</span></div>
{{type:TypingAnswer}}
<div style="font-size: 12px; color: #999; margin-top: 8px;">(Type the prefixed infinitive)</div>
"""

BACK = """\
{{FrontSide}}
<hr id="answer">
<div id="feedback" data-with-stress="{{Infinitive_UA}}" data-no-stress="{{TypingAnswer}}" style="margin-bottom: 16px;"></div>
<script>
(function() {
  var feedback = document.getElementById('feedback');
  var withStress = feedback.dataset.withStress;
  var noStress = feedback.dataset.noStress;
  var typedInput = document.querySelector('input[type="text"]');

  if (!typedInput) return;

  var typedAnswer = typedInput.value.trim();
  var html = '';

  if (typedAnswer === withStress) {
    html = '<div style="color: #2e7d32; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ✓ PERFECT</div>' +
           '<div style="color: #2e7d32; font-size: 14px;">Correct with stress marks</div>';
  } else if (typedAnswer === noStress) {
    html = '<div style="color: #ff9800; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ~ CORRECT</div>' +
           '<div style="color: #ff9800; font-size: 14px; margin-bottom: 12px;">Correct letters, missing stress</div>' +
           '<div style="color: #1565c0; font-size: 16px; font-weight: bold;">With stress:</div>' +
           '<div style="color: #1565c0; font-size: 18px;"><b>' + withStress + '</b></div>';
  } else if (typedAnswer.length > 0) {
    html = '<div style="color: #d32f2f; font-size: 22px; font-weight: bold; margin-bottom: 4px;">' +
           typedAnswer + ' ✗ INCORRECT</div>' +
           '<div style="color: #d32f2f; font-size: 14px; margin-bottom: 12px;">Not quite right</div>' +
           '<div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 4px;">Correct answer:</div>' +
           '<div style="color: #1565c0; font-size: 18px;"><b>' + withStress + '</b></div>';
  }

  feedback.innerHTML = html;
})();
</script>
<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #999;">
  {{Source_Note}}
</div>
"""

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
    # Check if model exists
    existing = anki_request("modelNames")
    model_names = existing.get("result", []) if existing else []

    if MODEL_NAME in model_names:
        # Update existing model
        print(f"✓ Model '{MODEL_NAME}' exists, updating...")

        # Add missing fields
        existing_fields = anki_request("modelFieldNames", {"modelName": MODEL_NAME})
        existing_fields = existing_fields.get("result", []) if existing_fields else []
        for field in FIELDS:
            if field not in existing_fields:
                print(f"  Adding field: {field}")
                anki_request("modelFieldAdd", {"modelName": MODEL_NAME, "fieldName": field})

        # Update templates
        templates_dict = {
            "PVOM Infinitive": {"Front": FRONT, "Back": BACK}
        }
        anki_request(
            "updateModelTemplates",
            {"model": {"name": MODEL_NAME, "templates": templates_dict}},
        )

        # Update CSS
        anki_request(
            "updateModelStyling",
            {"model": {"name": MODEL_NAME, "css": CSS}},
        )

        print(f"✓ Updated '{MODEL_NAME}' templates and styling")
        return True

    else:
        # Create new model
        print(f"Creating model '{MODEL_NAME}'...")
        model_spec = {
            "modelName": MODEL_NAME,
            "inOrderFields": FIELDS,
            "cardTemplates": [
                {
                    "name": "PVOM Infinitive",
                    "Front": FRONT,
                    "Back": BACK,
                }
            ],
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
