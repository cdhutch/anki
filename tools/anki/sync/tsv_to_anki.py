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
    """Stub AnkiConnect request (would connect to real Anki)"""
    pass

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
