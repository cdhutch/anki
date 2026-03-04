#!/usr/bin/env python3
"""
diff_cnsf_vs_anki.py

Drift detector:
Compare canonical CNSF notes (L1 -> L2 HTML via md_to_html_mmd.py) against
Anki-extracted wide TSV (L4 -> L3 via anki_to_l3_tsv.py --format wide).

- Canonical source of truth remains CNSF markdown.
- This tool is read-only and never mutates canonical notes or Anki.
- We compare *HTML payload equivalents* (Front/Back), because Anki stores HTML.

Key expectations in this repo:
- Canonical notes live in: domains/<domain>/anki/notes/**.md
- Forward renderer tool: tools/anki/md_to_html_mmd.py
  which writes:
    <out-dir>/<note_id>__front.html
    <out-dir>/<note_id>__back.html
- Anki extraction TSV is produced by:
    tools/anki/extract/anki_to_l3_tsv.py --format wide
  and includes model name and f__<FieldName> columns.

We use per-model mappings:
  tools/anki/extract/mappings/<ModelName>.yml

Mapping format (minimum):
  front_field: Front
  back_field: Back
  note_id_field: NoteID   # optional; used only as fallback
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

US = "\u241f"  # Unit Separator (for stable concatenation)


def eprint(*args) -> None:
    print(*args, file=sys.stderr)


def sha256_short(s: str, n: int = 12) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def tsv_unescape_cell(s: str) -> str:
    """Invert TSV escaping used by our export tools."""
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\\\", "\\")
    return s


def normalize_html_for_hash(html: str) -> str:
    """Normalize HTML to prevent drift from trivial differences.

    We normalize away:
      - renderer provenance comments
      - platform line endings
      - TSV/pretty-print artifacts (literal '\\n', leading '\\ ' before tags, backslash-only lines)
      - insignificant whitespace between tags
    """
    if html is None:
        return ""
    h = str(html)

    # Remove renderer provenance comments
    h = re.sub(r"<!--\s*renderer:.*?-->", "", h, flags=re.IGNORECASE)

    # Normalize line endings
    h = h.replace("\r\n", "\n").replace("\r", "\n")

    # Convert literal backslash-n sequences to real newlines (TSV artifacts)
    h = h.replace("\\n", "\n")

    # Remove trailing backslash line-continuations (common in pretty-printed exports)
    h = re.sub(r"(?m)\\\s*$", "", h)

    # Remove lines that are exactly a backslash (optionally with spaces)
    h = re.sub(r"(?m)^\s*\\\s*$", "", h)


    # Drop common pretty-print prefix: "\ <tag>" at start of line
    h = re.sub(r"(?m)^\\\s+(?=<)", "", h)

    # Remove lines that are just a backslash (optionally with spaces)
    h = re.sub(r"(?m)^\s*\\\s*$", "", h)

    # Remove stray fenced-code markers
    h = re.sub(r"(?m)^\s*```\s*$", "", h)

    # Collapse whitespace between tags
    h = re.sub(r">\s+<", "><", h)

    # Normalize colgroup variants (MultiMarkdown version differences):
    # - remove empty <colgroup></colgroup>
    # - normalize <col> tag to <col />
    h = re.sub(r"<colgroup>\s*</colgroup>", "", h, flags=re.IGNORECASE)
    h = re.sub(r"<col\s*>", "<col />", h, flags=re.IGNORECASE)

    # Collapse repeated whitespace
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\n{2,}", "\n", h)

    return h.strip()


def parse_cnsf_yaml(md_text: str) -> Tuple[dict, str]:
    if not md_text.startswith("---"):
        raise ValueError("CNSF note missing YAML front matter")
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid YAML front matter delimiters")
    meta = yaml.safe_load(parts[1].strip()) or {}
    body = parts[2].lstrip("\n")
    return meta, body


def find_cnsf_notes(notes_root: Path) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    for p in notes_root.rglob("*.md"):
        try:
            meta, _body = parse_cnsf_yaml(p.read_text(encoding="utf-8"))
            nid = meta.get("note_id")
            if nid:
                out[str(nid)] = p
        except Exception:
            continue
    return out


def load_mapping(mapping_dir: Path, model: str) -> dict:
    path = mapping_dir / f"{model}.yml"
    if not path.exists():
        raise RuntimeError(f"No mapping file for model: {model} ({path} missing)")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def read_wide_tsv(tsv_path: Path) -> List[dict]:
    with tsv_path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        rows = []
        for row in r:
            rows.append({k: tsv_unescape_cell(v) for k, v in row.items()})
        return rows


def strip_f_prefix(row: dict) -> dict:
    return {k[3:]: v for k, v in row.items() if k.startswith("f__")}


def run_forward_render(note_id: str, note_path: Path, tool_md_to_html: Path, out_dir: Path) -> Tuple[str, str]:
    """Render a single CNSF note to __front.html/__back.html and return their contents."""
    out_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())  # repo root

    cmd = [
        sys.executable,
        str(tool_md_to_html),
        "--note",
        str(note_path),
        "--out-dir",
        str(out_dir),
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(
            "Forward render failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{r.stdout}\n"
            f"stderr:\n{r.stderr}\n"
        )

    f_front = out_dir / f"{note_id}__front.html"
    f_back = out_dir / f"{note_id}__back.html"
    if not f_front.exists() or not f_back.exists():
        raise RuntimeError(f"Renderer did not produce expected files: {f_front.name}, {f_back.name}")

    return f_front.read_text(encoding="utf-8"), f_back.read_text(encoding="utf-8")


def compute_payload_hash(front: str, back: str) -> str:
    s = normalize_html_for_hash(front) + US + normalize_html_for_hash(back)
    return sha256_short(s)


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect drift between canonical CNSF and Anki-extracted TSV.")
    ap.add_argument("--domain", default="b737", help="Domain name, e.g. b737")
    ap.add_argument("--notes-root", default="domains", help="Root containing domains/<domain>/anki/notes/")
    ap.add_argument("--mapping-dir", default="tools/anki/extract/mappings")
    ap.add_argument(
        "--anki-wide-tsv",
        default="domains/b737/anki/tmp/extract_b737_wide__B737_Structured.tsv",
        help="Wide TSV exported from Anki (split-by-model file).",
    )
    ap.add_argument("--md-to-html-tool", default="tools/anki/md_to_html_mmd.py", help="Forward renderer tool path.")
    ap.add_argument("--out", default="domains/b737/anki/tmp/drift_report_b737_structured.json", help="Output report JSON path.")
    ap.add_argument("--render-dir", default="domains/b737/anki/tmp/_drift_render_cmp3", help="Temp dir for canonical HTML renders.")
    args = ap.parse_args()

    domain = args.domain
    notes_root = Path(args.notes_root) / domain / "anki" / "notes"
    mapping_dir = Path(args.mapping_dir)
    tool_md_to_html = Path(args.md_to_html_tool)
    tsv_path = Path(args.anki_wide_tsv)
    out_path = Path(args.out)
    render_dir = Path(args.render_dir)

    canonical = find_cnsf_notes(notes_root)
    rows = read_wide_tsv(tsv_path)

    counts = {
        "UNCHANGED": 0,
        "DRIFTED_IN_ANKI": 0,
        "MISSING_IN_ANKI": 0,
        "NEW_IN_ANKI": 0,
        "NO_ID": 0,
        "NO_MAPPING": 0,
        "RENDER_FAIL": 0,
    }

    report = {
        "domain": domain,
        "tsv": str(tsv_path),
        "notes_root": str(notes_root),
        "counts": counts,
        "items": [],
    }

    seen_note_ids = set()

    for row in rows:
        model = (row.get("model") or "").strip()
        fields = strip_f_prefix(row)

        note_id = (row.get("canonical_note_id") or "").strip()
        if not note_id:
            # fallbacks: note_id field name varies by model
            note_id = (fields.get("NoteID") or fields.get("note_id") or "").strip()

        if not note_id:
            counts["NO_ID"] += 1
            report["items"].append({"status": "NO_ID", "anki_note_id": row.get("anki_note_id"), "model": model})
            continue

        seen_note_ids.add(note_id)

        try:
            mapping = load_mapping(mapping_dir, model)
        except Exception as ex:
            counts["NO_MAPPING"] += 1
            report["items"].append({"status": "NO_MAPPING", "note_id": note_id, "model": model, "error": str(ex)})
            continue

        front_field = mapping.get("front_field", "Front")
        back_field = mapping.get("back_field", "Back")

        anki_front = fields.get(front_field, "") or ""
        anki_back = fields.get(back_field, "") or ""
        anki_hash = compute_payload_hash(anki_front, anki_back)

        if note_id not in canonical:
            counts["NEW_IN_ANKI"] += 1
            report["items"].append({"status": "NEW_IN_ANKI", "note_id": note_id, "model": model, "anki_hash": anki_hash})
            continue

        try:
            canon_front, canon_back = run_forward_render(note_id, canonical[note_id], tool_md_to_html, render_dir)
            canon_hash = compute_payload_hash(canon_front, canon_back)
        except Exception as ex:
            counts["RENDER_FAIL"] += 1
            report["items"].append(
                {"status": "RENDER_FAIL", "note_id": note_id, "model": model, "error": str(ex), "canonical_path": str(canonical[note_id])}
            )
            continue

        status = "UNCHANGED" if canon_hash == anki_hash else "DRIFTED_IN_ANKI"
        counts[status] += 1
        report["items"].append(
            {
                "status": status,
                "note_id": note_id,
                "model": model,
                "anki_hash": anki_hash,
                "canonical_hash": canon_hash,
                "canonical_path": str(canonical[note_id]),
            }
        )

    for nid, path in canonical.items():
        if nid not in seen_note_ids:
            counts["MISSING_IN_ANKI"] += 1
            report["items"].append({"status": "MISSING_IN_ANKI", "note_id": nid, "canonical_path": str(path)})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    eprint(f"Wrote report: {out_path}")
    eprint(f"Counts: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
