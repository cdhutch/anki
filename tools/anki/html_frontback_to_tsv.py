#!/usr/bin/env python3
"""
Extract AFTER_FRONT and AFTER_BACK blocks from canonical HTML into a TSV for Anki updates.

Input: HTML generated from canonical markdown (md_to_html.py)
Assumptions:
- Each note starts with an H2: <h2>NOTE_ID</h2>
- Canonical sections are headed by <h3>AFTER_FRONT</h3> and <h3>AFTER_BACK</h3>
- Content for a section is the HTML between that <h3> heading and the next <h3> or <h2>.

Output TSV columns:
note_id, field, answer_html, prompt, noteId

- note_id: the canonical NoteID (string from the H2)
- field: "Front" or "Back" (Anki field name)
- answer_html: HTML snippet to put into that field
- prompt: kept for compatibility (blank by default)
- noteId: optional; if provided (via a mapping TSV), enables direct update_notes_from_tsv.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.IGNORECASE | re.DOTALL)

TAG_RE = re.compile(r"<[^>]+>")

def _strip_tags(s: str) -> str:
    # Remove HTML tags and collapse whitespace
    t = TAG_RE.sub("", s)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _unescape_basic(s: str) -> str:
    # Enough for headings produced by typical markdown engines
    return (
        s.replace("&amp;", "&")
         .replace("&lt;", "<")
         .replace("&gt;", ">")
         .replace("&quot;", '"')
         .replace("&#39;", "'")
         .replace("&nbsp;", " ")
    )

def _find_heading_positions(html: str):
    """
    Return a list of tuples:
    (level, title_text, start_idx, end_idx)
    where end_idx is end of the heading tag.
    """
    items = []
    for m in H2_RE.finditer(html):
        title = _strip_tags(_unescape_basic(m.group(1)))
        items.append(("h2", title, m.start(), m.end()))
    for m in H3_RE.finditer(html):
        title = _strip_tags(_unescape_basic(m.group(1)))
        items.append(("h3", title, m.start(), m.end()))
    items.sort(key=lambda x: x[2])
    return items

def _slice_section(html: str, headings, idx_start: int) -> str:
    """
    Given headings list and the index of a heading, return content until next h2/h3.
    """
    start = headings[idx_start][3]
    end = len(html)
    for j in range(idx_start + 1, len(headings)):
        # Stop at next heading of any level
        end = headings[j][2]
        break
    return html[start:end].strip()

def load_noteid_map(path: Path) -> dict[str, str]:
    """
    Optional TSV mapping canonical note_id -> Anki noteId (numeric).
    Expected columns: note_id, noteId (others ignored)
    """
    mp: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            k = (r.get("note_id") or "").strip()
            v = (r.get("noteId") or "").strip()
            if k and v:
                mp[k] = v
    return mp

def main():
    ap = argparse.ArgumentParser(description="Extract AFTER_FRONT/AFTER_BACK blocks from canonical HTML to TSV.")
    ap.add_argument("--in", dest="inp", required=True, help="Input canonical HTML file")
    ap.add_argument("--out", required=True, help="Output TSV path")
    ap.add_argument("--map", dest="map_tsv", default=None, help="Optional TSV mapping note_id -> noteId")
    ap.add_argument("--front-field", default="Front", help="Anki field name for front (default: Front)")
    ap.add_argument("--back-field", default="Back", help="Anki field name for back (default: Back)")
    args = ap.parse_args()

    html = Path(args.inp).read_text(encoding="utf-8")
    headings = _find_heading_positions(html)

    note_map = load_noteid_map(Path(args.map_tsv)) if args.map_tsv else {}

    rows = []
    cur_note_id: str | None = None

    # Walk headings; track current H2 note id; capture H3 sections
    for i, (lvl, title, _s, _e) in enumerate(headings):
        if lvl == "h2":
            cur_note_id = title
            continue
        if lvl != "h3" or not cur_note_id:
            continue

        title_norm = title.strip().upper()
        if title_norm not in {"AFTER_FRONT", "AFTER_BACK"}:
            continue

        section_html = _slice_section(html, headings, i)
        if not section_html:
            continue

        if title_norm == "AFTER_FRONT":
            field = args.front_field
        else:
            field = args.back_field

        rows.append(
            {
                "note_id": cur_note_id,
                "noteId": note_map.get(cur_note_id, ""),
                "prompt": "",
                "field": field,
                "answer_html": section_html,
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["note_id", "noteId", "prompt", "field", "answer_html"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Rows: {len(rows)}")
    print(f"Output: {out_path}")

if __name__ == "__main__":
    main()
