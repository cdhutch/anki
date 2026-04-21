# Anki pipeline (repo tooling)

Goal: make the workflow reproducible and domain-agnostic:

1) Export from Anki (via AnkiConnect)
2) Produce a canonical Markdown review/edit file
3) Edit Markdown manually
4) Generate import TSV for AnkiConnect updates

Rendering option (HTML intermediate):
- Support converting Markdown/MultiMarkdown to HTML as an intermediate step.
- Prefer MultiMarkdown 6 if available; fall back to a pure-Python/markdown renderer if not.

Non-goals:
- Hardcoding a specific domain (e.g., systems-electrical).
- One-off console snippets; everything should be runnable as scripts in this repo.
