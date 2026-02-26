#!/usr/bin/env python3
"""
Extract per-note AFTER_FRONT and AFTER_BACK HTML blocks from a generated canonical HTML file.

Why:
- The canonical HTML can contain repeated <h3 id="after_front"> / <h3 id="after_back"> across notes.
- So we must scope extraction to each <h2 id="NOTE_ID"> ... </h2> section first.

Output TSV columns (tab-delimited):
  note_id, noteId, front_html, back_html, answer_html

- note_id: from <h2 id="...">
- noteId: optional mapping from a TSV passed via --map (note_id -> noteId)
- answer_html: kept for compatibility (defaults to back_html; falls back to section body if needed)
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple


H2_RE = re.compile(
    r'(?is)<h2\b[^>]*\bid="(?P<id>[^"]+)"[^>]*>.*?</h2>(?P<body>.*?)(?=(<h2\b[^>]*\bid=")|\Z)'
)

# Match an <h3 ...>AFTER_FRONT</h3> (id may repeat; we do NOT rely on it)
AFTER_FRONT_RE = re.compile(r'(?is)<h3\b[^>]*>\s*AFTER_FRONT\s*</h3>')
AFTER_BACK_RE  = re.compile(r'(?is)<h3\b[^>]*>\s*AFTER_BACK\s*</h3>')
HR_RE          = re.compile(r'(?is)<hr\b[^>]*/?>')


def load_noteid_map(map_tsv: Path) -> Dict[str, str]:
    m: Dict[str, str] = {}
    with map_tsv.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        if not rdr.fieldnames:
            return m
        # Accept either noteId or note_id variants
        for r in rdr:
            note_id = (r.get("note_id") or r.get("noteId") or r.get("NoteID") or "").strip()
            noteId  = (r.get("noteId") or r.get("note_id") or "").strip()
            # We expect note_id column to be the canonical string id, and noteId to be numeric.
            # If the user passes a map TSV with only note_id + noteId, this works.
            if note_id and noteId and noteId.isdigit():
                m[note_id] = noteId
    return m


def extract_front_back(section_html: str) -> Tuple[str, str]:
    """
    Given the HTML content *within* a note's h2 section, return (front_html, back_html).
    """
    m_front = AFTER_FRONT_RE.search(section_html)
    m_back  = AFTER_BACK_RE.search(section_html)

    if not m_front and not m_back:
        # Nothing to split
        return ("", "")

    # If AFTER_FRONT exists: start after it; otherwise start at beginning
    start_front = m_front.end() if m_front else 0

    if m_back:
        front_chunk = section_html[start_front:m_back.start()]
        start_back = m_back.end()
        # back until first <hr> (end-of-note marker) or end
        m_hr = HR_RE.search(section_html, pos=start_back)
        back_chunk = section_html[start_back:(m_hr.start() if m_hr else len(section_html))]
    else:
        front_chunk = section_html[start_front:]
        back_chunk = ""

    return (front_chunk.strip(), back_chunk.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input HTML (e.g., domains/**/anki/generated/*__canonical.html)")
    ap.add_argument("--out", dest="out", required=True, help="Output TSV (front+back html)")
    ap.add_argument("--map", dest="map_tsv", default=None, help="Optional TSV mapping note_id -> noteId (numeric).")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    html = inp.read_text(encoding="utf-8", errors="replace")

    noteid_map: Dict[str, str] = {}
    if args.map_tsv:
        noteid_map = load_noteid_map(Path(args.map_tsv))

    rows: List[Dict[str, str]] = []

    for m in H2_RE.finditer(html):
        note_id = (m.group("id") or "").strip()
        body = m.group("body") or ""
        if not note_id:
            continue

        front_html, back_html = extract_front_back(body)

        # Compatibility: answer_html defaults to back_html; if missing, use whatever exists
        answer_html = back_html or front_html or body.strip()

        noteId = noteid_map.get(note_id, "")

        rows.append(
            {
                "note_id": note_id,
                "noteId": noteId,
                "front_html": front_html,
                "back_html": back_html,
                "answer_html": answer_html,
            }
        )

    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["note_id", "noteId", "front_html", "back_html", "answer_html"],
            delimiter="\t",
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Rows: {len(rows)}")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
