#!/usr/bin/env python3
"""Query Anki collection.db directly to find deck→config mapping."""

import sqlite3
import json
from pathlib import Path

# Find Anki collection.db
home = Path.home()
anki_paths = [
    home / "AppData/Roaming/Anki2/User 1/collection.db",  # Windows
    home / "Library/Application Support/Anki2/User 1/collection.db",  # macOS
    home / ".local/share/Anki2/User 1/collection.db",  # Linux
]

collection_path = None
for path in anki_paths:
    if path.exists():
        collection_path = path
        break

if not collection_path:
    print("Error: Could not find Anki collection.db")
    print("Searched:")
    for path in anki_paths:
        print(f"  - {path}")
    exit(1)

print(f"Found Anki collection at: {collection_path}")
print("=" * 70)

try:
    conn = sqlite3.connect(str(collection_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query deck→config mapping
    print("\nDeck → Config Mapping (UA decks):")
    print("-" * 70)

    cursor.execute(
        """
        SELECT d.id, d.name, d.conf
        FROM decks d
        WHERE d.name LIKE 'UA%'
        ORDER BY d.name
        """
    )

    decks = cursor.fetchall()

    for deck in decks:
        deck_id = deck["id"]
        deck_name = deck["name"]
        config_id = deck["conf"]

        parts = deck_name.split("::")
        indent = "  " * (len(parts) - 1)

        # Get config details
        cursor.execute(
            "SELECT id, name, data FROM dconf WHERE id = ?",
            (config_id,),
        )
        config = cursor.fetchone()

        if config:
            config_name = config["name"]
            config_data = json.loads(config["data"])

            new_limit = config_data.get("new", {}).get("perDay", "?")
            lrn_limit = config_data.get("lrn", {}).get("perDay", "?")
            rev_limit = config_data.get("rev", {}).get("perDay", "?")

            print(
                f"{indent}{deck_name:<50} "
                f"{config_name:<20} {new_limit}/{lrn_limit}/{rev_limit}"
            )
        else:
            print(
                f"{indent}{deck_name:<50} "
                f"[Config {config_id} not found]"
            )

    print("\n" + "=" * 70)
    print("Analysis: Deck Hierarchy & Limits")
    print("=" * 70)

    # Show parent-child relationships
    print("\nHierarchy chain (from root → PVOM):")
    ua_root = next((d for d in decks if d["name"] == "UA"), None)
    ua_recognition = next((d for d in decks if d["name"] == "UA::Recognition"), None)
    ua_pvom = next(
        (d for d in decks if d["name"] == "UA::Recognition::PVOM"), None
    )

    if ua_root:
        cursor.execute(
            "SELECT name, data FROM dconf WHERE id = ?", (ua_root["conf"],)
        )
        root_config = cursor.fetchone()
        if root_config:
            root_data = json.loads(root_config["data"])
            print(
                f"\n  UA (config: {root_config['name']})"
                f"\n    New/Lrn/Rev: {root_data.get('new',{}).get('perDay')}"
                f"/{root_data.get('lrn',{}).get('perDay')}"
                f"/{root_data.get('rev',{}).get('perDay')}"
            )

    if ua_recognition:
        cursor.execute(
            "SELECT name, data FROM dconf WHERE id = ?", (ua_recognition["conf"],)
        )
        rec_config = cursor.fetchone()
        if rec_config:
            rec_data = json.loads(rec_config["data"])
            print(
                f"  └─ UA::Recognition (config: {rec_config['name']})"
                f"\n     New/Lrn/Rev: {rec_data.get('new',{}).get('perDay')}"
                f"/{rec_data.get('lrn',{}).get('perDay')}"
                f"/{rec_data.get('rev',{}).get('perDay')}"
            )

    if ua_pvom:
        cursor.execute(
            "SELECT name, data FROM dconf WHERE id = ?", (ua_pvom["conf"],)
        )
        pvom_config = cursor.fetchone()
        if pvom_config:
            pvom_data = json.loads(pvom_config["data"])
            print(
                f"     └─ UA::Recognition::PVOM (config: {pvom_config['name']})"
                f"\n        New/Lrn/Rev: {pvom_data.get('new',{}).get('perDay')}"
                f"/{pvom_data.get('lrn',{}).get('perDay')}"
                f"/{pvom_data.get('rev',{}).get('perDay')}"
            )

            # Check if using parent config or own config
            if ua_recognition and ua_pvom["conf"] == ua_recognition["conf"]:
                print("\n  ⚠ PVOM is using parent (UA::Recognition) config!")
                print("    Set PVOM to its own config to override parent limits.")
            elif ua_pvom["conf"] == ua_root["conf"]:
                print("\n  ⚠ PVOM is using root (UA) config!")
                print("    Set PVOM to its own config for independent limits.")
            else:
                print("\n  ✓ PVOM has its own independent config")

    conn.close()

except Exception as e:
    print(f"Error querying database: {e}")
    import traceback

    traceback.print_exc()
