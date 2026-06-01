#!/usr/bin/env python3
"""Compare CSS between two note types via AnkiConnect."""

import json
import urllib.request

ANKI_URL = "http://127.0.0.1:8765"

def anki_request(action, params):
    """Make an AnkiConnect request."""
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI_URL, payload, {"Content-Type": "application/json"})
    try:
        result = json.loads(urllib.request.urlopen(req).read())
        return result.get("result")
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_css(model_name):
    """Get CSS for a note type."""
    return anki_request("modelStyling", {"modelName": model_name})

def main():
    models = ["B737_Structured", "B737_Checklist"]
    css_dict = {}

    for model in models:
        css = get_css(model)
        if css:
            css_dict[model] = css
            print(f"\n{'='*60}")
            print(f"{model}")
            print(f"{'='*60}\n{css}\n")
        else:
            print(f"Could not retrieve CSS for {model}")

if __name__ == "__main__":
    main()
