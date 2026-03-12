# 737 Limits Model Cards — Follow-Up Notes

Branch: feature/737-limits-model-cards

## Status

Front/back canonical pipeline is working:

canonical.md
→ md_to_html.py
→ html_frontback_to_tsv.py (scoped by <h2 id>)
→ update_notes_from_tsv.py
→ Anki Front + Back updated

737-800 card renders correctly.

## Known Issue (MAX8 card)

Observed behavior:

- 737-800:
  - Front: blank table (___)
  - Back: populated values table + memory anchor

- 737 MAX 8:
  - Front: old/manual HTML formatting (bordered table + <br> style)
  - Back: blank table (___), not populated values

This suggests:

1) MAX8 Front field may still contain legacy HTML.
2) Back field may not have been overwritten by back_html during update.
3) update_notes_from_tsv.py may be:
   - writing answer_html after back_html
   - or not correctly distinguishing front_html/back_html rows

## Next Debug Steps

1. Re-run html_frontback_to_tsv.py with --map and confirm:
   - front_html populated for both notes
   - back_html populated for both notes

2. Dry-run update_notes_from_tsv.py and confirm:
   - both Front and Back fields targeted
   - no duplicate row logic overwriting Back

3. Inspect update_notes_from_tsv.py:
   - ensure front/back mode suppresses answer_html fallback
   - confirm no second update pass overwrites Back

4. If necessary:
   - Add explicit logging of which fields are written per note
   - Ensure per-note updates bundle Front+Back in one update call

## Architectural Decision

Keep canonical markdown as single source of truth.
Never manually edit Front/Back in Anki for these model cards.

