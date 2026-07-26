#!/usr/bin/env python3
"""Survey note types and card templates in UA domain via AnkiConnect."""

import json
import urllib.request
import sys

ANKI_URL = "http://127.0.0.1:8765"


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
        return result
    except Exception as e:
        print(f"AnkiConnect error: {e}", file=sys.stderr)
        return None


def get_model_names():
    """Get all model (note type) names."""
    result = anki_request("modelNames")
    if result and not result.get("error"):
        return result.get("result", [])
    return []


def get_model_info(model_name):
    """Get detailed info about a model."""
    result = anki_request("modelFieldNames", {"modelName": model_name})
    fields = result.get("result", []) if result and not result.get("error") else []

    # Get templates by trying modelTemplates directly
    result = anki_request("modelTemplates", {"modelName": model_name})
    if result and not result.get("error") and result.get("result"):
        templates = list(result.get("result", {}).keys())
    else:
        templates = []

    return {"fields": fields, "templates": templates}


def get_model_templates(model_name):
    """Get full template content for a model."""
    result = anki_request("modelTemplates", {"modelName": model_name})
    return result.get("result", {}) if result else {}


def main():
    print("Ukrainian Note Types & Card Templates Survey")
    print("=" * 70)

    model_names = get_model_names()
    ua_models = sorted([m for m in model_names if m.startswith("UA")])

    if not ua_models:
        print("No UA_* note types found")
        return

    print(f"\nFound {len(ua_models)} UA note types:\n")

    for model_name in ua_models:
        print(f"\n{'=' * 70}")
        print(f"Model: {model_name}")
        print("=" * 70)

        # Get fields
        info = get_model_info(model_name)
        fields = info.get("fields", [])
        templates = info.get("templates", [])

        print(f"\nFields ({len(fields)}):")
        for i, field in enumerate(fields, 1):
            print(f"  {i}. {field}")

        if templates:
            print(f"\nCard Templates ({len(templates)}):")
            for template_name in templates:
                print(f"  • {template_name}")
        else:
            print(f"\nCard Templates: (none found or legacy model)")

        # Get template details
        template_content = get_model_templates(model_name)

        if not template_content:
            print("  (No template details available)")
            continue

        for template_name in (templates or []):
            if template_name in template_content:
                tmpl = template_content[template_name]
                front = tmpl.get("Front", "")
                back = tmpl.get("Back", "")

                print(f"\n  Template: {template_name}")
                print(f"  {'-' * 66}")

                # Analyze front
                print(f"  Front side:")
                if not front:
                    print(f"    (empty or not accessible)")
                else:
                    if "{{type:" in front:
                        try:
                            typing_field = front.split("{{type:")[1].split("}}")[0]
                            print(f"    • Uses typing field: {typing_field}")
                        except (IndexError, ValueError):
                            pass
                    if "{{cloze:" in front:
                        print(f"    • Uses cloze deletion")
                    if "{{#" in front:
                        try:
                            parts = front.split("{{#")
                            conditionals = []
                            for part in parts[1:]:
                                if "}}" in part:
                                    conditional = part.split("}}")[0]
                                    conditionals.append(conditional)
                            if conditionals:
                                print(f"    • Conditional fields: {', '.join(conditionals[:3])}")
                        except (IndexError, ValueError):
                            pass

                # Analyze back
                print(f"  Back side:")
                if not back:
                    print(f"    (empty or not accessible)")
                else:
                    if "FrontSide" in back:
                        print(f"    • Carries to back side (FrontSide)")
                    if "{{type:" in back:
                        try:
                            typing_field = back.split("{{type:")[1].split("}}")[0]
                            print(f"    • Uses typing field: {typing_field}")
                        except (IndexError, ValueError):
                            pass
                    if "<script" in back:
                        print(f"    • Has JavaScript (custom feedback)")
                    if "{{#" in back:
                        try:
                            parts = back.split("{{#")
                            conditionals = []
                            for part in parts[1:]:
                                if "}}" in part:
                                    conditional = part.split("}}")[0]
                                    conditionals.append(conditional)
                            if conditionals:
                                print(f"    • Conditional fields: {', '.join(conditionals[:3])}")
                        except (IndexError, ValueError):
                            pass

        print()

    # Summary analysis
    print("\n" + "=" * 70)
    print("Template Analysis Summary")
    print("=" * 70)

    typing_models = []
    cloze_models = []
    recognition_models = []

    for model_name in ua_models:
        template_content = get_model_templates(model_name)
        if template_content:
            all_template_text = json.dumps(template_content)

            if "{{type:" in all_template_text:
                typing_models.append(model_name)
            elif "{{cloze:" in all_template_text:
                cloze_models.append(model_name)
            else:
                recognition_models.append(model_name)
        else:
            # No template data available
            recognition_models.append(model_name)

    print(f"\nTyping/Production templates (require typed input):")
    for model in typing_models:
        print(f"  • {model}")

    print(f"\nCloze deletion templates:")
    for model in cloze_models:
        print(f"  • {model}")

    print(f"\nRecognition templates (flip to see answer):")
    for model in recognition_models:
        if model not in typing_models:
            print(f"  • {model}")

    print("\n" + "=" * 70)
    print("Recommendations for Deck Limits:")
    print("=" * 70)

    print(f"""
Based on template types:

Typing/Production (UA_Lexeme, UA_PVOM_Infinitive):
  • More cognitively demanding (requires recall + spelling)
  • Slower to review (user types answer)
  • Suggest: Lower new card limit (10-15/day) to avoid cognitive overload
  • Suggest: Higher learning limit (if used) to reinforce typing

Recognition (UA_Visual, UA_Grammar, UA_Verb):
  • Lower cognitive load (recognize vs recall)
  • Faster to review (flip/recognize)
  • Suggest: Higher new card limit (20-30/day)

Separate by deck type:
  • UA::Recognition::PVOM (typing): 15 new/day
  • UA::Recognition::Visual (recognition): 25 new/day
  • UA::Recognition::Grammar (recognition): 20 new/day
  • UA::Recognition::UA→EN (typing): 15 new/day
  """)


if __name__ == "__main__":
    main()
