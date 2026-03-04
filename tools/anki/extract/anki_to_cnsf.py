#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path
import yaml

def tsv_unescape_cell(s: str) -> str:
    """Inverse of anki_to_l3_tsv.tsv_escape_cell()."""
    if s is None:
        return ""
    # Important: unescape in reverse order of escaping.
    # We escaped backslashes first, so here we unescape \t/\n/\r first,
    # then collapse \\ -> \ at the end.
    s = str(s)
    s = s.replace("\\t", "\t")
    s = s.replace("\\n", "\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\\\", "\\")
    return s

def row_unescape(row: dict) -> dict:
    return {k: tsv_unescape_cell(v) for k, v in row.items()}

def load_mapping(mapping_dir, model):
    path = Path(mapping_dir) / f"{model}.yml"
    if not path.exists():
        raise RuntimeError(f"No mapping file for model: {model}")
    with open(path) as f:
        return yaml.safe_load(f)

def strip_prefix(row):
    out = {}
    for k, v in row.items():
        if k.startswith("f__"):
            out[k[3:]] = v
    return out

def get_identity(fields, mapping):
    for f in mapping["identity_fields"]:
        if f in fields and fields[f]:
            return fields[f]
    return None

def write_note(outdir, mapping, fields, row, note_id):

    front = fields.get(mapping["front_field"], "")
    back = fields.get(mapping["back_field"], "")

    tags = []
    if mapping.get("include_anki_tags"):
        tags += row.get("tags", "").split()

    tags += mapping.get("add_tags", [])

    tags = sorted(set(t for t in tags if t))

    preserve = {}
    for f in mapping.get("preserve_fields", []):
        if f in fields and fields[f]:
            preserve[f] = fields[f]

    md = []

    md.append("---")
    md.append("schema: cnsf/v0")
    md.append(f"domain: {mapping['domain']}")
    md.append(f"note_type: {mapping['note_type']}")
    md.append(f"note_id: {note_id}")
    md.append("anki:")
    md.append(f"  model: {row['model']}")

    if tags:
        md.append("tags:")
        for t in tags:
            md.append(f"- {t}")

    if preserve:
        md.append("fields:")
        for k,v in preserve.items():
            md.append(f"  {k}: {v}")

    md.append("---")
    md.append("")
    md.append("# front_html")
    md.append("")
    md.append(front)
    md.append("")
    md.append("# back_html")
    md.append("")
    md.append(back)
    md.append("")

    outpath = Path(outdir) / f"{note_id}.md"
    with open(outpath, "w") as f:
        f.write("\n".join(md))

def main():

    p = argparse.ArgumentParser()
    p.add_argument("--infile", required=True)
    p.add_argument("--mapping-dir", default="tools/anki/extract/mappings")
    p.add_argument("--outdir", required=True)

    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    with open(args.infile) as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            row = row_unescape(row)

            model = row["model"]

            mapping = load_mapping(args.mapping_dir, model)

            fields = strip_prefix(row)

            note_id = get_identity(fields, mapping)

            if not note_id:
                continue

            write_note(args.outdir, mapping, fields, row, note_id)

if __name__ == "__main__":
    main()
