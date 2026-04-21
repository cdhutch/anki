#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


def normalize_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    prompt = re.sub(r"\bdoes (.+?) consists of\?", r"does \1 consist of?", prompt, flags=re.IGNORECASE)
    return prompt


def tsv_unescape(s: str | None) -> str:
    if s is None:
        return ""
    s = str(s)
    return (
        s.replace("\\t", "\t")
         .replace("\\n", "\n")
         .replace("\\r", "\r")
         .replace("\\\\", "\\")
    )


def slugify_value(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def yaml_quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def html_list_to_md(text: str) -> str:
    text = tsv_unescape(text).strip()
    if not text:
        return ""

    text = html.unescape(text)

    # paragraphs
    text = re.sub(r"(?is)<p>\s*", "", text)
    text = re.sub(r"(?is)\s*</p>", "\n\n", text)

    # list items
    text = re.sub(r"(?is)<li>\s*", "- ", text)
    text = re.sub(r"(?is)\s*</li>", "\n", text)

    # strip list containers
    text = re.sub(r"(?is)</?(ul|ol)>\s*", "", text)

    # basic inline tags
    text = re.sub(r"(?is)<strong>(.*?)</strong>", r"**\1**", text)
    text = re.sub(r"(?is)<b>(.*?)</b>", r"**\1**", text)
    text = re.sub(r"(?is)<em>(.*?)</em>", r"*\1*", text)
    text = re.sub(r"(?is)<i>(.*?)</i>", r"*\1*", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)

    # remove any remaining tags conservatively
    text = re.sub(r"(?is)<[^>]+>", "", text)

    # normalize whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n\s*\n(?=- )", "\n", text)
    text = re.sub(r"(?m)^- (.+)\n\s*\n(?=- )", r"- \1\n", text)
    return text.strip()


def prompt_to_front(system: str, subsystem: str, prompt: str) -> str:
    title_parts = [p for p in [system, subsystem] if p.strip()]
    title = " — ".join(title_parts).upper() if title_parts else "B737 SYSTEMS"
    return f"**{title}**\n\n{normalize_prompt(prompt)}"


def classify_note_type(function_type: str, panel_name: str, failure_logic: str) -> str:
    ft = function_type.strip().lower()
    if failure_logic.strip():
        return "system_failure_logic"
    if panel_name.strip():
        return "system_panel_item"
    if ft in {"failure-logic", "failure_logic"}:
        return "system_failure_logic"
    if ft in {"concept"}:
        return "system_concept"
    if ft in {"switch-logic", "switch_logic"}:
        return "system_switch_logic"
    return "system_general"


def normalize_tags(raw_tags: str, system: str, subsystem: str) -> list[str]:
    tags = [
        "domain:b737",
        "topic:systems",
    ]

    sys_slug = slugify_value(system.replace("B737 ", ""))
    sub_slug = slugify_value(subsystem)
    if sys_slug:
        tags.append(f"system:{sys_slug}")
    if sub_slug:
        tags.append(f"subsystem:{sub_slug}")

    raw = [t.strip() for t in raw_tags.split() if t.strip()]
    for t in raw:
        if t == "systems":
            continue
        if t == "common":
            tags.append("scope:common")
        elif t == "verbatim":
            tags.append("style:verbatim")
        elif t == "format_bullets":
            tags.append("format:bullets")
        elif t == "lights-switches":
            tags.append("subtopic:lights_switches")
        elif t == "llights-switches":
            tags.append("subtopic:lights_switches")
        else:
            tags.append(t)

    tags.append("status:unverified")

    # dedupe preserve order
    out: list[str] = []
    seen: set[str] = set()
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def row_to_markdown(row: dict[str, str]) -> str:
    note_id = tsv_unescape(row.get("canonical_note_id") or row.get("f__note_id") or "").strip()
    system = tsv_unescape(row.get("f__system") or "").strip()
    subsystem = tsv_unescape(row.get("f__subsystem") or "").strip()
    panel_group = tsv_unescape(row.get("f__panel_group") or "").strip()
    panel_name = tsv_unescape(row.get("f__panel_name") or "").strip()
    function_type = tsv_unescape(row.get("f__function_type") or "").strip()
    prompt = tsv_unescape(row.get("f__prompt") or "").strip()
    answer = tsv_unescape(row.get("f__answer") or "").strip()
    normal_state = tsv_unescape(row.get("f__normal_state") or "").strip()
    failure_logic = tsv_unescape(row.get("f__failure_logic") or "").strip()
    affects_bus = tsv_unescape(row.get("f__affects_bus") or "").strip()
    powered_by = tsv_unescape(row.get("f__powered_by") or "").strip()
    interacts_with = tsv_unescape(row.get("f__interacts_with") or "").strip()
    notes = tsv_unescape(row.get("f__notes") or "").strip()
    source_doc = tsv_unescape(row.get("f__source") or "").strip()
    source_loc = tsv_unescape(row.get("f__ref_section") or "").strip()
    raw_tags = tsv_unescape(row.get("f__tags") or row.get("tags") or "").strip()

    note_type = classify_note_type(function_type, panel_name, failure_logic)
    tags = normalize_tags(raw_tags, system, subsystem)

    front_md = prompt_to_front(system, subsystem, prompt)
    back_md = html_list_to_md(answer)

    lines: list[str] = []
    lines.append("---")
    lines.append("schema: cnsf/v0")
    lines.append("domain: b737")
    lines.append(f"note_type: {note_type}")
    lines.append(f"note_id: {note_id}")
    lines.append("anki:")
    lines.append("  model: B737_Systems")
    lines.append("  deck: B737::Systems")
    lines.append("tags:")
    for tag in tags:
        lines.append(f"- {tag}")

    lines.append("")
    lines.append(f"system: {yaml_quote(system)}")
    lines.append(f"subsystem: {yaml_quote(subsystem)}")
    lines.append(f"panel_group: {yaml_quote(panel_group)}")
    lines.append(f"panel_name: {yaml_quote(panel_name)}")
    lines.append(f"function_type: {yaml_quote(function_type)}")
    lines.append(f"normal_state: {yaml_quote(normal_state)}")
    lines.append(f"failure_logic: {yaml_quote(failure_logic)}")
    lines.append(f"affects_bus: {yaml_quote(affects_bus)}")
    lines.append(f"powered_by: {yaml_quote(powered_by)}")
    lines.append(f"interacts_with: {yaml_quote(interacts_with)}")
    lines.append(f"notes: {yaml_quote(notes)}")

    lines.append("")
    lines.append("fields:")
    lines.append(f"  Source Document: {yaml_quote(source_doc)}")
    lines.append(f"  Source Location: {yaml_quote(source_loc)}")
    lines.append('  Verification Notes: ""')
    lines.append("---")
    lines.append("")
    lines.append("# front_md")
    lines.append("")
    lines.append(front_md)
    lines.append("")
    lines.append("# back_md")
    lines.append("")
    lines.append(back_md)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    infile = Path(args.infile)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with infile.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        count = 0
        for row in reader:
            note_id = tsv_unescape(row.get("canonical_note_id") or row.get("f__note_id") or "").strip()
            if not note_id:
                continue

            md = row_to_markdown(row)
            outpath = outdir / f"{note_id}.md"
            outpath.write_text(md, encoding="utf-8")
            print(f"WROTE: {outpath}")
            count += 1
            if args.limit and count >= args.limit:
                break

    print(f"Done. files={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())