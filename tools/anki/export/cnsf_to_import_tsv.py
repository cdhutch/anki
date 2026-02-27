#!/usr/bin/env python3
"""
CNSF L1→L2→L3: export canonical CNSF notes to an Anki-import TSV (HTML payload).
"""

from __future__ import annotations

import argparse
import csv
import glob
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from tools.anki.cnsf_parse import load_cnsf_note
from tools.anki.md_to_html_mmd import render_cnsf_note_to_html


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def _split_tags(tags: Any) -> List[str]:
    if tags is None:
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    if isinstance(tags, str):
        raw = tags.replace(",", " ").split()
        return [t.strip() for t in raw if t.strip()]
    return [str(tags).strip()] if str(tags).strip() else []


def _stable_extra_field_names(notes: List["CnsfEnvelope"]) -> List[str]:
    keys = set()
    for n in notes:
        for k in (n.fields or {}).keys():
            keys.add(str(k))
    return sorted(keys)


def _require(val: str | None, label: str, path: Path) -> str:
    if val is None or str(val).strip() == "":
        raise ValueError(f"Missing required '{label}' in {path}")
    return str(val)


@dataclass
class CnsfEnvelope:
    path: Path
    note_id: str
    noteId: str
    model: str
    deck: str
    tags: List[str]
    fields: Dict[str, str]


def load_envelope(path: Path, noteid_map: Dict[str, str] | None) -> CnsfEnvelope:
    note = load_cnsf_note(str(path))
    meta = note.meta

    note_id = _require(meta.get("note_id"), "note_id", path)

    anki = meta.get("anki") or {}
    model = _require(anki.get("model"), "anki.model", path)
    deck = _require(anki.get("deck"), "anki.deck", path)

    tags = _split_tags(meta.get("tags"))

    fields = meta.get("fields") or {}
    fields_str = {str(k): "" if v is None else str(v) for k, v in fields.items()}

    noteId = ""
    if noteid_map and note_id in noteid_map:
        noteId = str(noteid_map[note_id]).strip()

    return CnsfEnvelope(
        path=path,
        note_id=note_id,
        noteId=noteId,
        model=model,
        deck=deck,
        tags=tags,
        fields=fields_str,
    )


def read_noteid_map(map_path: Path) -> Dict[str, str]:
    m: Dict[str, str] = {}
    if not map_path.exists():
        return m
    with map_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            nid = (row.get("note_id") or "").strip()
            aid = (row.get("noteId") or "").strip()
            if nid and aid:
                m[nid] = aid
    return m


def expand_inputs(inputs: List[str]) -> List[Path]:
    out: List[Path] = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            out.extend(sorted(p.glob("**/*.md")))
        else:
            matches = glob.glob(inp, recursive=True)
            if matches:
                out.extend(sorted(Path(x) for x in matches))
            elif p.suffix == ".md" and p.exists():
                out.append(p)
    seen = set()
    uniq = []
    for p in out:
        rp = str(p.resolve())
        if rp not in seen:
            uniq.append(p)
            seen.add(rp)
    return uniq


def write_tsv(out_path: Path, notes: List[CnsfEnvelope], extra_field_names: List[str], overwrite: bool) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {out_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    header = ["note_id", "noteId", "model", "deck", "tags", "front_html", "back_html"] + extra_field_names

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()

        def _tsv_safe(v: str) -> str:
            # Keep each TSV record to ONE physical line.
            # HTML can contain newlines/tabs; escape them.
            v = v.replace("\r\n", "\n").replace("\r", "\n")
            v = v.replace("\t", "\\t").replace("\n", "\\n")
            return v

        for env in notes:
            rendered = render_cnsf_note_to_html(str(env.path))
            front_html = _tsv_safe(rendered["front_html"])
            back_html  = _tsv_safe(rendered["back_html"])

            row = {
                "note_id": env.note_id,
                "noteId": env.noteId,
                "model": env.model,
                "deck": env.deck,
                "tags": " ".join(env.tags),
                "front_html": front_html,
                "back_html": back_html,
            }
            for k in extra_field_names:
                row[k] = _tsv_safe(env.fields.get(k, "") or "")
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inputs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--map", default="")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    paths = expand_inputs(args.inputs)
    if not paths:
        eprint("No input files found.")
        return 2

    noteid_map = read_noteid_map(Path(args.map)) if args.map else None

    envs = []
    for p in paths:
        envs.append(load_envelope(p, noteid_map))

    if args.limit:
        envs = envs[: args.limit]

    envs.sort(key=lambda x: x.note_id)
    extra_field_names = _stable_extra_field_names(envs)

    write_tsv(Path(args.out), envs, extra_field_names, args.overwrite)

    print(f"Rows: {len(envs)}")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
