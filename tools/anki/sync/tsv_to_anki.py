"""Minimal stub for tsv_to_anki imports used by ua_lexeme_import.py"""

# Flag constants
FLAG_RED = 1
FLAG_ORANGE = 2

# UA deck tree query — the full UA domain tree
UA_DECK_TREE = "deck:UA::*"

def anki_request(action, **params):
    """Stub AnkiConnect request (would connect to real Anki)"""
    pass

def describe_note_ids(note_ids, note_type=None):
    """Convert note IDs to human-readable format"""
    return ', '.join(str(id) for id in note_ids)

def flag_query_for_model(model_name, deck_query=None):
    """Return deck query string for flagged cards of a specific note type
    
    When deck_query is None (default): returns a flagged-card query scoped to
    the model and the UA deck tree, e.g. "deck:UA::* note:UA_Lexeme flag>=1"
    
    When deck_query is provided: returns a simple scoped query WITHOUT the
    flag>=1 condition, e.g. "deck:Scratch note:UA_Lexeme". This is useful
    for non-flagged queries like audit or test queries.
    
    Args:
        model_name: Note type name (e.g., "UA_Lexeme")
        deck_query: Optional deck query to use instead of UA_DECK_TREE.
                   If provided, flag>=1 is NOT added.
    
    Returns:
        Query string like "deck:UA::* note:UA_Lexeme flag>=1" or
        "deck:Scratch note:UA_Verb" (without flag>=1 when deck_query is provided)
    """
    if deck_query is None:
        # Default: full flagged-card query scoped to this model
        return f"{UA_DECK_TREE} note:{model_name} flag>=1"
    else:
        # Override: simple scoped query without flag condition
        return f"{deck_query} note:{model_name}"

def get_flagged_note_ids_by_color():
    """Return empty dict (stub implementation)"""
    return {FLAG_RED: set(), FLAG_ORANGE: set()}
