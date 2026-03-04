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

def write_note(outdir, mapping, fields, row, canonical_note_id):
    # front/back placeholders
    front = fields.get(mapping.get("front_field", ""), "")
    back = fields.get(mapping.get("back_field", ""), "")

    tags = []
    if mapping.get("include_anki_tags"):
        tags += row.get("tags", "").split()
    tags += mapping.get("add_tags", [])
    tags = sorted(set(t for t in tags if t))

    # Preserve all fields listed in mapping['preserve_fields']
    preserve = {}
    for f in mapping.get("preserve_fields", []):
        value = row.get(f, "") or fields.get(f, "")
        if value:
            preserve[f] = value

    md = []
    md.append("---")
    md.append("schema: cnsf/v0")
    md.append(f"domain: {mapping['domain']}")
    md.append(f"note_type: {mapping['note_type']}")
    md.append(f"canonical_note_id: {canonical_note_id}")
    md.append(f"anki_note_id: {row.get('anki_note_id', '')}")
    md.append("anki:")
    md.append(f"  model: {row['model']}")

    if tags:
        md.append("tags:")
        for t in tags:
            md.append(f"- {t}")

    if preserve:
        md.append("fields:")
        for k, v in preserve.items():
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

    outpath = Path(outdir) / f"{canonical_note_id}.md"
    with open(outpath, "w") as f:
        f.write("\n".join(md))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--infile", required=True)
    p.add_argument("--mapping-dir", default="tools/anki/extract/mappings")
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    ua_counter = 1
    processed_anki_ids = set()   # track exported Anki note IDs

    with open(args.infile) as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            row = row_unescape(row)

            anki_id = row.get("anki_note_id", "")
            if anki_id in processed_anki_ids:
                continue  # skip duplicates
            if anki_id:
                processed_anki_ids.add(anki_id)

            model = row["model"]
            mapping = load_mapping(args.mapping_dir, model)
            fields = strip_prefix(row)

            # Determine canonical_note_id
            match = get_identity(fields, mapping)
            if not match and row["model"] == "UA_Lexeme":
                inbox = Path(args.outdir)
                # generate unique ua-lexeme-XXX that doesn't exist yet
                while True:
                    candidate = f"ua-lexeme-{ua_counter:03d}"
                    ua_counter += 1
                    if not (inbox / f"{candidate}.md").exists():
                        break
                match = candidate

            canonical_note_id = match
            if not canonical_note_id:
                continue

            write_note(args.outdir, mapping, fields, row, canonical_note_id)
if __name__ == "__main__":
    main()