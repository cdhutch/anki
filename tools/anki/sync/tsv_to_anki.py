"""Minimal stub for tsv_to_anki imports used by ua_lexeme_import.py"""

# Flag constants
FLAG_RED = 1
FLAG_ORANGE = 2

# UA deck tree structure
UA_DECK_TREE = {
    "UA": {
        "Recognition": {
            "UA→EN": None,
        },
        "Production": {
            "EN→UA": None,
        },
    }
}

def anki_request(action, params=None, url="http://localhost:8765"):
    """Make an HTTP POST request to AnkiConnect and return the response."""
    import json
    import urllib.request

    request_body = {
        "jsonrpc": "2.0",
        "action": action,
        "version": 6
    }
    if params:
        request_body["params"] = params

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(request_body).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("error"):
                print(f"AnkiConnect error: {result['error']}")
                return None
            return result.get("result")
    except Exception as e:
        print(f"AnkiConnect request failed: {e}")
        return None

def describe_note_ids(note_ids, note_type=None):
    """Convert note IDs to human-readable format"""
    return ', '.join(str(id) for id in note_ids)

def flag_query_for_model(model_name, deck_query=None):
    """Return deck query string for flagged cards of a specific note type"""
    if deck_query is None:
        deck_query = "deck:UA::*"
    return f"{deck_query} note:{model_name}"

def get_flagged_note_ids_by_color(query, url):
    """Return dict of flagged note IDs by color (stub implementation)"""
    return {FLAG_RED: set(), FLAG_ORANGE: set()}