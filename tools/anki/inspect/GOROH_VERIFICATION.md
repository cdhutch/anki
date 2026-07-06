# Горох Stress Verification — Chrome DevTools Guide

This guide explains how to run the Горох batch fetch step of the stress
verification workflow. The Python scripts handle extraction and comparison;
Chrome handles the actual page fetches because goroh.pp.ua is not accessible
to automated HTTP clients.

---

## Overview of the full workflow

```
Step 1  Python  verify_stress_goroh.py --extract
Step 2  Chrome  Paste goroh_fetch.js in DevTools console  ← this guide
Step 3  Python  verify_stress_goroh.py --compare goroh_cache.json
Step 4  Manual  Review goroh_mismatches.tsv
Step 5  Python  verify_stress_goroh.py --apply goroh_mismatches.tsv
```

Or run everything in one go with the interactive wizard:

```bash
python tools/anki/inspect/run_stress_verification.py
```

---

## Step-by-step Chrome instructions

### 1. Run the extract step first (Python)

```bash
python tools/anki/inspect/verify_stress_goroh.py \
    --extract --out-dir /tmp/goroh
```

This writes two files:
- `/tmp/goroh/goroh_input.json` — the list of forms to verify
- `/tmp/goroh/goroh_fetch.js` — the Chrome script to paste

### 2. Navigate to goroh.pp.ua in Chrome

Open Chrome and go to:

```
https://goroh.pp.ua/Словозміна/водій
```

**Why this page?** The fetch script requests URLs on goroh.pp.ua. Running it
from within the goroh.pp.ua origin avoids cross-origin (CORS) restrictions.
The specific page doesn't matter — any goroh.pp.ua page works.

### 3. Open Chrome DevTools

Use one of these methods:

| Method | Mac | Windows / Linux |
|--------|-----|-----------------|
| Keyboard shortcut | `Cmd + Option + I` | `F12` or `Ctrl + Shift + I` |
| Menu | Chrome menu → More Tools → Developer Tools | Chrome menu → More Tools → Developer Tools |
| Right-click | Right-click anywhere on the page → Inspect | Right-click anywhere → Inspect |

DevTools opens as a panel — usually docked to the bottom or right side of
the window. Either position works.

### 4. Open the Console tab

Click the **Console** tab in the DevTools panel. It is usually the second tab,
after Elements.

You should see a `>` prompt at the bottom of the console.

### 5. Copy the fetch script

Copy the entire contents of `/tmp/goroh/goroh_fetch.js`.

**Mac quick-copy from Terminal:**

```bash
cat /tmp/goroh/goroh_fetch.js | pbcopy
```

This copies the script to your clipboard without opening a text editor.

### 6. Paste and run the script

Click inside the Console input area (next to the `>` prompt).

Paste with `Cmd + V` (Mac) or `Ctrl + V` (Windows/Linux).

> **Important — multi-line paste warning:**
> Chrome may show a yellow warning: *"Warning: Don't paste code you don't
> trust..."*. This is a standard security prompt. Type `allow pasting` and
> press Enter, then paste the script again. You only need to do this once per
> DevTools session.

Press **Enter** to run the script.

### 7. Watch the progress

The console prints a progress line after each batch of 25 lemmas:

```
Batch 1 / 5 done
Batch 2 / 5 done
...
✓ goroh_cache.json downloaded (123 lemmas)
```

With a fast connection, each batch takes 2–5 seconds. The full run for 123
lemmas takes under a minute.

### 8. Save the downloaded file

Chrome automatically downloads `goroh_cache.json` to your default Downloads
folder when the script finishes.

Move it to the output directory you used in Step 1:

```bash
mv ~/Downloads/goroh_cache.json /tmp/goroh/
```

### 9. Continue with the Python comparison

```bash
python tools/anki/inspect/verify_stress_goroh.py \
    --compare /tmp/goroh/goroh_cache.json \
    --out-dir /tmp/goroh
```

---

## Troubleshooting

### "Allow pasting" prompt

Chrome blocks pasting into the console for security. Type `allow pasting`
at the prompt and press Enter, then paste the script.

### CORS error in the console

```
Access to fetch at 'https://goroh.pp.ua/...' has been blocked by CORS policy
```

You are running the script from a page other than goroh.pp.ua. Navigate to
`https://goroh.pp.ua/Словозміна/водій` first, then re-open DevTools and
try again.

### "net::ERR_NAME_NOT_RESOLVED" or similar network errors

goroh.pp.ua is unreachable. Check your internet connection, or try again
later — the site is occasionally down for maintenance.

### Script appears to hang / no output

The script runs asynchronously. Check that you pressed Enter after pasting.
If nothing happens after 30 seconds, the console may have swallowed the
script silently — click in the console, press `Ctrl + A` to select all, and
press Delete, then paste again.

### Only some batches complete before an error

The script fetches 25 lemmas at a time. If it errors partway through, the
`goroh_cache.json` download may not have triggered. Reload the page (which
resets the console) and run the script again — it fetches all lemmas fresh.
Partial caches are not supported.

### The downloaded file is empty or 0 bytes

The `Blob` download mechanism can fail on some Chrome security settings.
As a fallback, you can print the result to the console and copy it:

```javascript
// At the end of the script run, type this in the console:
copy(JSON.stringify(window._gorohResults, null, 2))
```

Then paste into a text editor and save as `goroh_cache.json`.

> Note: For this fallback to work, add `window._gorohResults = results;`
> near the end of goroh_fetch.js before the Blob download line.

---

## What the script does (for reference)

`goroh_fetch.js` does three things:

1. **Fetches** each Горох Словозміна page for a list of bare lemmas (no
   stress marks). Each fetch is a plain `GET` request — no login, no
   cookies, no data sent.

2. **Parses** the HTML response: strips footnote markers (`<sup>` tags),
   phonetic punctuation (backticks, colons), and special character sequences
   (`{дз}`, `{дж}`). Extracts the case table rows (Називний → nom,
   Родовий → gen, etc.) and all stressed word tokens.

3. **Downloads** the structured results as `goroh_cache.json` — a JSON
   object mapping each bare lemma to its parsed paradigm.

No data is sent to any server. All processing happens in your browser.

---

## Variable stress notes

Some Ukrainian words have two accepted stress positions (e.g. до́ма / дома́).
Горох lists both forms. The comparison script flags these as `variable`
(stored form is one valid option) or `variable_mismatch` (stored form is
neither option). For `variable` cases, review `goroh_mismatches.tsv` and
choose the canonical form for your cards by filling in the `correction`
column.
