#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ANKI_URL = "http://127.0.0.1:8765"

CANDIDATE_ANSWER_FIELDS = [
    # most common
    "Answer",
    "Back",
    "answer",
    "back",
    # repo-ish variants
    "answer_md",
    "answer_html",
    "Answer_md",
    "Answer_html",
    "Back_md",
    "Back_html",
]


def anki_request(action: str, params: dict[str, Any] | None = None, url: str = DEFAULT_ANKI_URL) -> dict[str, Any]:
    payload: dict[str, Any] = {"action": action, "version": 6}
    if params is not None:
        payload["params"] = params

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    out = json.loads(raw)

    if "error" not in out or "result" not in out:
        raise RuntimeError(f"Unexpected AnkiConnect response: {out}")
    if out["error"] is not None:
        raise RuntimeError(f"AnkiConnect error for action={action}: {out['error']}")
    return out


def _nl(s: str) -> str:
    # TSVs sometimes store literal "\n" sequences
    return (s or "").replace("\\n", "\n")


def read_import_html_tsv(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f, delimiter="\t")

        # Minimal required identity columns
        required = {"note_id", "noteId"}
        missing = required - set(rdr.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required TSV columns: {sorted(missing)} in {path}")

        # Content columns:
        # - legacy: answer_html (usually Back)
        # - new: front_html / back_html (Front+Back)
        content_cols = {"answer_html", "front_html", "back_html"}
        present = set(rdr.fieldnames or [])
        if not (present & content_cols):
            raise ValueError(
                f"TSV must include at least one content column from {sorted(content_cols)}; "
                f"found columns: {sorted(present)}"
            )

        for r in rdr:
            if not any((v or "").strip() for v in r.values()):
                continue
            rows.append({k: (v or "") for k, v in r.items()})
    return rows


def choose_answer_field(note_fields: dict[str, Any], preferred: str | None) -> str:
    keys = list(note_fields.keys())

    if preferred:
        if preferred in note_fields:
            return preferred
        raise ValueError(f"--field {preferred!r} not present on note. Available: {keys}")

    for cand in CANDIDATE_ANSWER_FIELDS:
        if cand in note_fields:
            return cand

    if len(keys) == 2:
        return keys[1]

    raise ValueError(
        "Could not auto-detect answer field. "
        f"Available fields: {keys}. "
        "Pass --field explicitly."
    )


def resolve_note_ids_from_note_id_field(
    rows: list[dict[str, str]],
    *,
    anki_url: str,
    note_id_field: str = "NoteID",
) -> dict[str, int]:
    """
    For rows missing 'noteId', resolve noteId by searching Anki for a note
    whose field `note_id_field` exactly matches row['note_id'].

    Returns mapping: note_id -> noteId (int)
    """
    mapping: dict[str, int] = {}

    for r in rows:
        note_id = (r.get("note_id") or "").strip()
        noteId_s = (r.get("noteId") or "").strip()

        if not note_id or noteId_s:
            continue

        # Exact match query on the NoteID field
        # Quote value to handle punctuation safely.
        query = f'{note_id_field}:"{note_id}"'
        found = anki_request("findNotes", {"query": query}, url=anki_url)["result"] or []

        if not found:
            continue

        if len(found) > 1:
            print(f"WARNING: multiple notes match {query!r}; using first: {found[0]}")

        mapping[note_id] = int(found[0])

    return mapping


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Update Anki notes from a TSV. Supports answer_html (legacy) or front_html/back_html (front+back)."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Input TSV (e.g. __import_html.tsv)")
    ap.add_argument("--anki-url", default=DEFAULT_ANKI_URL, help=f"AnkiConnect URL (default: {DEFAULT_ANKI_URL})")

    # Legacy single-field mode (answer_html)
    ap.add_argument("--field", default=None, help="Target Anki field name for answer_html (default: auto-detect)")

    # Front/back mode
    ap.add_argument("--front-field", default=None, help="Target Anki field name for front_html (default: Front)")
    ap.add_argument(
        "--back-field",
        default=None,
        help="Target Anki field name for back_html (default: auto-detect Back/Answer variants)",
    )

    ap.add_argument("--dry-run", action="store_true", help="Do not write changes; just show what would happen")
    ap.add_argument("--limit", type=int, default=0, help="Only process first N rows (0 = all)")
    args = ap.parse_args()

    tsv_path = Path(args.inp)
    if not tsv_path.exists():
        raise FileNotFoundError(tsv_path)

    rows = read_import_html_tsv(tsv_path)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    # Ensure AnkiConnect reachable
    try:
        ver = anki_request("version", url=args.anki_url)["result"]
    except Exception as e:
        print(f"ERROR: Unable to reach AnkiConnect at {args.anki_url}: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"AnkiConnect version: {ver}")
    print(f"Rows to process: {len(rows)}")

    # # Collect noteIds, fetch info once
    # note_ids: list[int] = []
    # for r in rows:
    #     noteId_s = (r.get("noteId") or "").strip()
    #     if noteId_s:
    #         note_ids.append(int(noteId_s))

    # info = anki_request("notesInfo", {"notes": note_ids}, url=args.anki_url)["result"]
    # info_map: dict[int, dict[str, Any]] = {int(n["noteId"]): n for n in info if n and "noteId" in n}

    # Resolve missing noteId values by searching NoteID:"<note_id>"
    resolved = resolve_note_ids_from_note_id_field(rows, anki_url=args.anki_url, note_id_field="NoteID")

    # Collect noteIds (explicit + resolved), fetch info once
    note_ids: list[int] = []
    for r in rows:
        note_id = (r.get("note_id") or "").strip()
        noteId_s = (r.get("noteId") or "").strip()

        if noteId_s:
            note_ids.append(int(noteId_s))
            continue

        if note_id and note_id in resolved:
            note_ids.append(int(resolved[note_id]))

    # De-dupe (preserve order)
    seen: set[int] = set()
    note_ids = [n for n in note_ids if not (n in seen or seen.add(n))]

    info = anki_request("notesInfo", {"notes": note_ids}, url=args.anki_url)["result"]
    info_map: dict[int, dict[str, Any]] = {int(n["noteId"]): n for n in info if n and "noteId" in n}






    updates: list[dict[str, Any]] = []
    skipped = 0

    for r in rows:
        # note_id = (r.get("note_id") or "").strip()
        # noteId_s = (r.get("noteId") or "").strip()

        # if not noteId_s:
        #     print(f"SKIP (no noteId): {note_id}")
        #     skipped += 1
        #     continue

        note_id = (r.get("note_id") or "").strip()
        noteId_s = (r.get("noteId") or "").strip()

        if not noteId_s and note_id and note_id in resolved:
            noteId_s = str(resolved[note_id])

        if not noteId_s:
            print(f"SKIP (no noteId and could not resolve): {note_id}")
            skipped += 1
            continue

        noteId = int(noteId_s)
        ninfo = info_map.get(noteId)
        if not ninfo:
            print(f"SKIP (noteId not found in Anki): {note_id} ({noteId})")
            skipped += 1
            continue

        fields = ninfo.get("fields", {}) or {}
        fields_to_update: dict[str, str] = {}

        ans = _nl(r.get("answer_html", ""))
        front_html = _nl(r.get("front_html", ""))
        back_html = _nl(r.get("back_html", ""))

        # Prefer front/back mode if any of those cols are present with content
        if front_html or back_html:
            # FRONT
            if front_html:
                front_target = args.front_field or "Front"
                if front_target not in fields:
                    print(
                        f"SKIP (front field missing): {note_id} ({noteId}) -> "
                        f"{front_target!r} not in {list(fields.keys())}"
                    )
                    skipped += 1
                    continue
                fields_to_update[front_target] = front_html

            # BACK
            if back_html:
                try:
                    back_target = choose_answer_field(fields, args.back_field)
                except Exception as e:
                    print(f"SKIP (back field detect error): {note_id} ({noteId}) -> {e}")
                    skipped += 1
                    continue
                fields_to_update[back_target] = back_html

        else:
            # Legacy answer_html mode
            if not ans:
                print(f"SKIP (no content): {note_id} ({noteId})")
                skipped += 1
                continue
            try:
                target_field = choose_answer_field(fields, args.field)
            except Exception as e:
                print(f"SKIP (field detect error): {note_id} ({noteId}) -> {e}")
                skipped += 1
                continue
            fields_to_update[target_field] = ans

        if not fields_to_update:
            print(f"SKIP (no content): {note_id} ({noteId})")
            skipped += 1
            continue

        updates.append({"id": noteId, "fields": fields_to_update})

    print(f"Prepared updates: {len(updates)}")
    print(f"Skipped: {skipped}")

    if args.dry_run:
        for u in updates[:3]:
            fid = u["id"]
            items = list(u["fields"].items())
            for field_name, value in items:
                snippet = (value or "")[:120].replace("\n", "\\n")
                print(f"DRY RUN: noteId={fid} field={field_name} value[:120]={snippet}")
        print("Dry-run complete (no changes sent).")
        return

    if not updates:
        print("Nothing to update.")
        return

    for note in updates:
        anki_request("updateNoteFields", {"note": note}, url=args.anki_url)

    print("✅ updateNoteFields complete (no error).")


if __name__ == "__main__":
    main()
