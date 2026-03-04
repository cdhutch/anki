#!/usr/bin/env python3
"""
Reverse pipeline Phase 1: Anki (L4) -> L3 TSV extraction via AnkiConnect.

Goals:
- Read-only (never modifies Anki).
- Deterministic output (stable ordering, stable headers).
- General for unknown models/fields.
- Supports known "front/back" shape used by B737_Structured.

Formats:
  wide (default): common columns + one column per Anki field (f__<FieldName>).
                  Use --split-by-model for stable headers.
  frontback: note_id, noteId, front_html, back_html (+ optional verification columns).

Identity:
  Prefer fields in order: note_id, NoteID (configurable via --identity-fields).
  Never invent note_id unless --derive-note-id is set.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests

DEFAULT_ANKICONNECT_URL = "http://127.0.0.1:8765"
ANKICONNECT_VERSION = 6


# -------------------------
# helpers
# -------------------------

def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def tsv_escape_cell(value: Any) -> str:
    """Keep TSV single-row-per-note deterministically and reversibly."""
    if value is None:
        return ""
    s = str(value)
    # Escape backslashes first so we can safely use \t, \n, \r literals
    s = s.replace("\\", "\\\\")
    s = s.replace("\t", "\\t")
    s = s.replace("\r", "\\r")
    s = s.replace("\n", "\\n")
    return s


def stable_join(items: Iterable[str], sep: str) -> str:
    return sep.join(sorted({x for x in items if x}))


def sha256_short(s: str, n: int = 12) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


# -------------------------
# AnkiConnect
# -------------------------

class AnkiConnectError(RuntimeError):
    pass


class AnkiConnectClient:
    def __init__(self, url: str) -> None:
        self.url = url

    def call(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        payload = {"action": action, "version": ANKICONNECT_VERSION, "params": params or {}}
        try:
            r = requests.post(self.url, json=payload, timeout=30)
            r.raise_for_status()
        except requests.RequestException as ex:
            raise AnkiConnectError(f"AnkiConnect request failed: {ex}") from ex

        try:
            data = r.json()
        except json.JSONDecodeError as ex:
            raise AnkiConnectError(f"Invalid JSON from AnkiConnect: {ex}") from ex

        if "error" not in data or "result" not in data:
            raise AnkiConnectError(f"Malformed AnkiConnect response: {data}")

        if data["error"] is not None:
            raise AnkiConnectError(f"AnkiConnect error for '{action}': {data['error']}")

        return data["result"]

    def find_notes(self, query: str) -> List[int]:
        return self.call("findNotes", {"query": query})

    def notes_info(self, note_ids: Sequence[int]) -> List[Dict[str, Any]]:
        return self.call("notesInfo", {"notes": list(note_ids)})

    def cards_of_note(self, note_id: int) -> List[int]:
        """Return card ids for a note.

        Some AnkiConnect builds do not support 'cardsOfNote'. In that case,
        fall back to 'findCards' with query 'nid:<note_id>'.
        """
        try:
            return self.call("cardsOfNote", {"note": note_id})
        except AnkiConnectError as ex:
            msg = str(ex).lower()
            if "unsupported action" in msg and "cardsofnote" in msg:
                return self.call("findCards", {"query": f"nid:{note_id}"})
            raise

    def cards_info(self, card_ids: Sequence[int]) -> List[Dict[str, Any]]:
        return self.call("cardsInfo", {"cards": list(card_ids)})

    def model_field_names(self, model_name: str) -> List[str]:
        return self.call("modelFieldNames", {"modelName": model_name})


# -------------------------
# data model
# -------------------------

@dataclass(frozen=True)
class NoteExtract:
    noteId: int
    model: str
    tags: List[str]
    fields: Dict[str, str]
    mod: Optional[int]
    usn: Optional[int]
    card_ids: List[int]
    deck_names: List[str]


def resolve_identity(fields: Dict[str, str], identity_fields: Sequence[str]) -> str:
    for k in identity_fields:
        v = fields.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def derive_note_id_from_text(text: str) -> str:
    """Only used if --derive-note-id is enabled. Conservative slugger."""
    t = text.strip().lower()
    t = re.sub(r"<[^>]+>", " ", t)       # strip HTML tags
    t = re.sub(r"[^\w\s-]+", "", t)      # remove punctuation
    t = re.sub(r"\s+", "-", t).strip("-")
    t = re.sub(r"-+", "-", t)
    return t[:80]


def extract_notes(
    client: AnkiConnectClient,
    note_ids: Sequence[int],
    identity_fields: Sequence[str],
    derive_note_id: bool,
    derive_source_field: Optional[str],
) -> List[NoteExtract]:
    infos = client.notes_info(note_ids)

    # Collect cards + decks deterministically
    note_to_cards: Dict[int, List[int]] = {}
    all_card_ids: List[int] = []
    for ni in infos:
        nid = int(ni["noteId"])
        cids = sorted(int(x) for x in client.cards_of_note(nid))
        note_to_cards[nid] = cids
        all_card_ids.extend(cids)

    card_id_to_deck: Dict[int, str] = {}
    if all_card_ids:
        CHUNK = 200
        for i in range(0, len(all_card_ids), CHUNK):
            chunk = all_card_ids[i:i+CHUNK]
            for c in client.cards_info(chunk):
                card_id_to_deck[int(c["cardId"])] = str(c.get("deckName", "") or "")

    out: List[NoteExtract] = []
    for ni in infos:
        nid = int(ni["noteId"])
        model = str(ni.get("modelName", "") or "")
        tags = sorted(str(t) for t in (ni.get("tags", []) or []))
        fields_obj = ni.get("fields", {}) or {}

        fields: Dict[str, str] = {}
        for fname, meta in fields_obj.items():
            v = meta.get("value", "")
            fields[str(fname)] = "" if v is None else str(v)

        # Optional derivation (OFF by default)
        if not resolve_identity(fields, identity_fields) and derive_note_id:
            src = derive_source_field
            if src and fields.get(src, "").strip():
                fields[identity_fields[0]] = derive_note_id_from_text(fields[src])
            else:
                for guess in ("Front", "prompt", "Title", "system"):
                    if fields.get(guess, "").strip():
                        fields[identity_fields[0]] = derive_note_id_from_text(fields[guess])
                        break

        cids = note_to_cards.get(nid, [])
        decks = stable_join((card_id_to_deck.get(cid, "") for cid in cids), sep="|")
        deck_names = decks.split("|") if decks else []

        out.append(
            NoteExtract(
                noteId=nid,
                model=model,
                tags=tags,
                fields=fields,
                mod=ni.get("mod", None),
                usn=ni.get("usn", None),
                card_ids=cids,
                deck_names=deck_names,
            )
        )

    out.sort(key=lambda x: x.noteId)
    return out


# -------------------------
# writers
# -------------------------

WIDE_COMMON_COLUMNS = [
    "anki_note_id",
    "canonical_note_id",
    "model",
    "tags",
    "deck_names",
    "card_ids",
    "mod",
    "usn",
    "fields_hash",
]


def write_tsv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(rows)


def notes_to_wide_rows(
    notes: List[NoteExtract],
    field_order: List[str],
    identity_fields: Sequence[str],
) -> Tuple[List[str], List[List[str]]]:
    header = WIDE_COMMON_COLUMNS + [f"f__{n}" for n in field_order]
    rows: List[List[str]] = []

    for n in notes:
        canonical = resolve_identity(n.fields, identity_fields)
        tags_s = stable_join(n.tags, sep=" ")
        decks_s = stable_join(n.deck_names, sep="|")
        cards_s = stable_join((str(cid) for cid in n.card_ids), sep="|")
        ordered_vals = [n.fields.get(fn, "") for fn in field_order]
        fields_hash = sha256_short("\u241f".join(ordered_vals))

        row = [
            tsv_escape_cell(n.noteId),
            tsv_escape_cell(canonical),
            tsv_escape_cell(n.model),
            tsv_escape_cell(tags_s),
            tsv_escape_cell(decks_s),
            tsv_escape_cell(cards_s),
            tsv_escape_cell("" if n.mod is None else int(n.mod)),
            tsv_escape_cell("" if n.usn is None else int(n.usn)),
            tsv_escape_cell(fields_hash),
        ]
        for fn in field_order:
            row.append(tsv_escape_cell(n.fields.get(fn, "")))
        rows.append(row)

    return header, rows


FRONTBACK_BASE_HEADER = ["note_id", "noteId", "front_html", "back_html"]
FRONTBACK_EXTRAS = [
    ("Source Document", "source_document"),
    ("Source Location", "source_location"),
    ("Verification Notes", "verification_notes"),
]


def notes_to_frontback_rows(
    notes: List[NoteExtract],
    identity_fields: Sequence[str],
    front_field: str,
    back_field: str,
    include_verification: bool,
) -> Tuple[List[str], List[List[str]]]:
    header = list(FRONTBACK_BASE_HEADER)
    if include_verification:
        header.extend([col for _, col in FRONTBACK_EXTRAS])

    rows: List[List[str]] = []
    for n in notes:
        canonical = resolve_identity(n.fields, identity_fields)
        front = n.fields.get(front_field, "")
        back = n.fields.get(back_field, "")

        row = [
            tsv_escape_cell(canonical),
            tsv_escape_cell(n.noteId),
            tsv_escape_cell(front),
            tsv_escape_cell(back),
        ]
        if include_verification:
            for field_name, _col in FRONTBACK_EXTRAS:
                row.append(tsv_escape_cell(n.fields.get(field_name, "")))
        rows.append(row)

    return header, rows


# -------------------------
# CLI
# -------------------------

def build_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query

    parts: List[str] = []
    if args.model:
        parts.append(f'note:"{args.model}"')
    if args.deck:
        parts.append(f'deck:"{args.deck}"')

    if not parts:
        raise SystemExit("Provide --query or at least one of --noteIds, --model, --deck.")
    return " ".join(parts)


def ensure_not_exists(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise SystemExit(f"Refusing to overwrite existing file: {path} (use --overwrite)")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract Anki notes to L3 TSV via AnkiConnect.")
    p.add_argument("--anki-url", default=DEFAULT_ANKICONNECT_URL, help="AnkiConnect URL (default http://127.0.0.1:8765).")

    p.add_argument("--query", help="Anki search query (findNotes).")
    p.add_argument("--noteIds", nargs="*", type=int, help="Explicit Anki noteIds to extract.")
    p.add_argument("--model", help='Model filter (translated to note:"<model>" if no --query).')
    p.add_argument("--deck", help='Deck filter (translated to deck:"<deck>" if no --query).')

    p.add_argument("--out", required=True, help="Output TSV path (or base path when --split-by-model).")
    p.add_argument("--format", default="wide", choices=["wide", "frontback"], help="Output format.")
    p.add_argument("--split-by-model", action="store_true", help="Wide format: write one TSV per model.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing output file(s).")

    p.add_argument("--identity-fields", nargs="*", default=["note_id", "NoteID"],
                   help="Field names to search for canonical note_id (priority order).")
    p.add_argument("--derive-note-id", action="store_true",
                   help="If no identity field present, derive note_id from content (OFF by default).")
    p.add_argument("--derive-source-field",
                   help="Field name to derive from if deriving is enabled (e.g. Front, prompt).")

    p.add_argument("--front-field", default="Front", help="Front field name for frontback format (default: Front).")
    p.add_argument("--back-field", default="Back", help="Back field name for frontback format (default: Back).")
    p.add_argument("--include-verification", action="store_true",
                   help="Include Source Document/Location/Verification Notes columns (frontback format).")

    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    client = AnkiConnectClient(args.anki_url)

    if args.noteIds and len(args.noteIds) > 0:
        note_ids = sorted(set(int(x) for x in args.noteIds))
    else:
        query = build_query(args)
        note_ids = sorted(set(int(x) for x in client.find_notes(query)))

    if not note_ids:
        eprint("No notes found.")
        return 0

    notes = extract_notes(
        client=client,
        note_ids=note_ids,
        identity_fields=args.identity_fields,
        derive_note_id=args.derive_note_id,
        derive_source_field=args.derive_source_field,
    )

    out_path = Path(args.out)

    if args.format == "frontback":
        kept: List[NoteExtract] = []
        missing: List[int] = []
        for n in notes:
            if args.front_field in n.fields and args.back_field in n.fields:
                kept.append(n)
            else:
                missing.append(n.noteId)

        if missing:
            eprint(f"WARNING: {len(missing)} notes missing {args.front_field}/{args.back_field}; skipped.")
        header, rows = notes_to_frontback_rows(
            kept,
            identity_fields=args.identity_fields,
            front_field=args.front_field,
            back_field=args.back_field,
            include_verification=args.include_verification,
        )
        ensure_not_exists(out_path, args.overwrite)
        write_tsv(out_path, header, rows)
        eprint(f"Wrote {out_path} ({len(rows)} rows).")
        return 0

    # wide format
    if args.split_by_model:
        by_model: Dict[str, List[NoteExtract]] = {}
        for n in notes:
            by_model.setdefault(n.model or "UNKNOWN_MODEL", []).append(n)

        base = out_path
        base_dir = base.parent
        base_stem = base.stem
        base_suffix = base.suffix or ".tsv"

        for model, group in sorted(by_model.items(), key=lambda x: x[0]):
            if model != "UNKNOWN_MODEL":
                field_order = client.model_field_names(model)
            else:
                field_order = sorted({k for n in group for k in n.fields.keys()})

            header, rows = notes_to_wide_rows(group, field_order, args.identity_fields)
            safe_model = re.sub(r"[^A-Za-z0-9._-]+", "_", model)[:80]
            path = base_dir / f"{base_stem}__{safe_model}{base_suffix}"
            ensure_not_exists(path, args.overwrite)
            write_tsv(path, header, rows)
            eprint(f"Wrote {path} ({len(rows)} rows).")
        return 0

    # single wide file with superset header
    all_fields = sorted({k for n in notes for k in n.fields.keys()})
    header = WIDE_COMMON_COLUMNS + [f"f__{n}" for n in all_fields]

    rows: List[List[str]] = []
    for n in notes:
        canonical = resolve_identity(n.fields, args.identity_fields)
        tags_s = stable_join(n.tags, sep=" ")
        decks_s = stable_join(n.deck_names, sep="|")
        cards_s = stable_join((str(cid) for cid in n.card_ids), sep="|")
        ordered_vals = [n.fields.get(fn, "") for fn in all_fields]
        fields_hash = sha256_short("\u241f".join(ordered_vals))

        row = [
            tsv_escape_cell(n.noteId),
            tsv_escape_cell(canonical),
            tsv_escape_cell(n.model),
            tsv_escape_cell(tags_s),
            tsv_escape_cell(decks_s),
            tsv_escape_cell(cards_s),
            tsv_escape_cell("" if n.mod is None else int(n.mod)),
            tsv_escape_cell("" if n.usn is None else int(n.usn)),
            tsv_escape_cell(fields_hash),
        ]
        for fn in all_fields:
            row.append(tsv_escape_cell(n.fields.get(fn, "")))
        rows.append(row)

    ensure_not_exists(out_path, args.overwrite)
    write_tsv(out_path, header, rows)
    eprint(f"Wrote {out_path} ({len(rows)} rows).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
