# Flagged Card Fix Workflow

**Purpose:** Periodic review and correction of flagged Anki cards via Claude + canonical CNSF notes.

**When to use:** End of study session to clean up all flags and fix issues before next session.

## Flag Usage Convention

| Flag Color | Meaning | Examples |
|---|---|---|
| Red | Errors to fix | Typos, wrong stress marks, incorrect definitions, bad examples |
| Orange | Confusing/unclear | Definition too vague, poor example, near-synonym confusion, template issue |
| Other | Flexible (context-dependent) | Use as needed for custom categorization |

## Workflow: Three Phases

### Phase 1: Extract Flags → NoteIDs

```bash
python tools/anki/inspect/ua_flag_audit.py --query
```

Output:
- Query Anki for all flagged cards in UA domain
- Extract `NoteID` from each card
- Group by flag color
- Display summary: "12 flagged cards (8 red errors, 4 orange confusing)"
- Output: JSON or CSV manifest of flagged cards with NoteID + flag color

### Phase 2: Interactive Review & Fix Loop

For each flagged NoteID:

1. **Locate canonical file** — Map NoteID to CNSF file path
   ```
   NoteID: ua-lexeme-0042 → domains/ua/anki/notes/lexemes/.../ua-lexeme-0042.md
   ```

2. **Show note to Claude** — Read CNSF file, display all fields

3. **Claude asks** — "Why did you flag this card?" (with flag color context)

4. **You respond** — Describe the issue or correction needed

5. **Claude clarifies (if needed)** — Suggest interpretations if response is ambiguous
   ```
   Claude: "Did you flag because: (a) the definition is too similar to another word, 
   or (b) the example is confusing?"
   ```

6. **Confirm & fix** — You approve Claude's interpretation and provide correction

7. **Update CNSF** — Correct field(s) in the canonical markdown file

8. **Mark as fixed** — Remove from audit list

### Phase 3: Batch Apply & Clean

```bash
python tools/anki/inspect/ua_flag_audit.py --apply
```

1. **Validate corrected notes** — Check CNSF schema (note_id, fields, tags)

2. **Batch re-import** — Use existing import scripts:
   - `ua_lexeme_import.py` for UA_Lexeme notes
   - `ua_verb_import.py` for UA_Verb notes
   - `ua_grammar_import.py` for UA_Grammar notes
   - `ua_visual_import.py` for UA_Visual notes

3. **Remove flags** — Batch query: remove all flags from cards matching NoteIDs

4. **Commit to git** — Commit all corrected CNSF files with message:
   ```
   fix(ua): resolve flagged card issues (12 cards)
   
   - Red flags (8 errors): typos, stress marks, definitions
   - Orange flags (4 clarity): examples, confusable sets
   ```

5. **Clean state** — All flags removed, ready for next session

## Implementation Details

### Tools

**`tools/anki/inspect/ua_flag_audit.py`** (built and tested 2026-08-01, see CLAUDE.md item 8)
- `--query`: find every red/orange-flagged card in the UA deck tree, group by note, resolve
  each `NoteID` to its canonical CNSF file path (recursive search for lexemes, flat for
  verbs/grammar/visual), print a summary, write a JSON manifest
  (`flagged_cards_manifest.json` by default -- gitignored, transient)
- `--apply`: three-step re-sync so fixed notes actually end up unsuspended in the same
  run, not deferred to some later sync -- (1) re-import corrected CNSF files via the
  right per-note-type import script, while flags are still set (notes stay suspended);
  (2) clear flags via `setSpecificValueOfCard`; (3) re-import the same notes again, so
  each import script's own suspend policy (re-queried fresh from AnkiConnect) sees the
  now-cleared flags and unsuspends. `--no-unmark` skips steps 2-3 for a content-only
  dry-test. `--manifest PATH` to target a non-default manifest.

### File Mapping

NoteID → canonical path pattern:
```
ua-lexeme-0042 → domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/ua-lexeme-0042.md
ua-verb-0001 → domains/ua/anki/notes/verbs/ua-verb-0001.md
ua-grammar-0005 → domains/ua/anki/notes/grammar/ua-grammar-0005.md
ua-visual-0003 → domains/ua/anki/notes/visual/ua-visual-0003.md
```

### Re-import Scripts

All import scripts follow the same pattern:
```bash
python tools/anki/sync/ua_lexeme_import.py domains/ua/anki/notes/lexemes/yabluko-l1/ch-00/ua-lexeme-0042.md
```

They:
- Read CNSF file
- Find or create note in Anki (by NoteID)
- Update all fields
- Preserve tags
- Handle upsert logic

### Flag Removal

**Corrected 2026-08-01** (see CLAUDE.md item 8): the `unmark` action shown in an earlier version
of this doc does not exist in AnkiConnect -- it was an aspirational, never-tested sketch, and
`ua_flag_audit.py` hit a real `"AnkiConnect error for unmark: unsupported action"` when it tried
it. There is no batch flag-clearing action; the real mechanism is `setSpecificValueOfCard`, called
once per card, with `newValues` as actual ints (`["0"]` as a string silently no-ops -- returns
`True` but leaves the flag unchanged; `[0]` actually clears it):
```python
anki_request(
    "setSpecificValueOfCard",
    {"card": card_id, "keys": ["flags"], "newValues": [0]},
    url=ANKI_URL,
)
```
`ua_flag_audit.py --apply` handles this correctly (loops per card_id, ints not strings).

## Workflow Integration

**Recommended flow:**
1. Study session: Flag cards as needed (red=error, orange=confusing)
2. End of session: Run `ua_flag_audit.py --query` to see summary
3. Review loop: Use Claude interactive review for each flagged card
4. Apply fixes: Run `ua_flag_audit.py --apply` to batch re-import + remove flags
5. Commit: Git commit all corrected CNSF files
6. Next session: Clean slate, no flags

## Notes

- All corrections are version-controlled in git (canonical CNSF files)
- Re-import preserves card history in Anki (upsert by NoteID)
- Flags are only removed after fixes are confirmed
- Claude provides interpretation help if user's explanation is unclear
- Works with all UA note types: UA_Lexeme, UA_Verb, UA_Grammar, UA_Visual
