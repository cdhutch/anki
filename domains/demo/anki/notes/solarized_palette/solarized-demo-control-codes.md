---
schema: cnsf/v0
domain: demo
note_type: solarized_doc
note_id: solarized-demo-control-codes
anki:
  model: Solarized_Palette_Demo
  deck: Demo::Solarized_Palette
tags:
- domain:demo
- topic:solarized-palette
- subtopic:documentation
- status:unverified
fields:
  Verification Notes: ''
---

# front_md

<div class="swatch-title">How does this deck detect light/dark mode?</div>
<div class="usage-note">(Tap/click to flip &mdash; this card documents the CSS control codes
this whole demo relies on.)</div>

# back_md

<table class="control-code-table">
  <tr><th>Platform</th><th>Selector Anki applies</th><th>Source</th></tr>
  <tr><td>macOS Anki (desktop)</td><td><code class="inline">.nightMode</code></td>
      <td>This repo's CLAUDE.md finding (2026-07-23, UA_Visual bug audit)</td></tr>
  <tr><td>AnkiMobile (iPhone / iPad)</td><td><code class="inline">.nightMode</code> (same as macOS)</td>
      <td>docs.ankimobile.net/night-mode.html (official AnkiMobile manual)</td></tr>
  <tr><td>AnkiDroid (Android &mdash; not one of Craig's devices)</td>
      <td><code class="inline">.night_mode</code> (underscore)</td>
      <td>forums.ankiweb.net moderator reply, "night-mode desktop, but not night-mode mobile"</td></tr>
</table>
<div class="swatch-role">
  The original assumption going into this demo was that AnkiMobile needs a
  <em>different</em> control code than the macOS client. Research for this deck found the
  opposite: iOS/iPadOS AnkiMobile and macOS desktop Anki both key off the same
  <code class="inline">.nightMode</code> class. The real platform split is Apple
  (<code class="inline">.nightMode</code>) vs. Android (<code class="inline">.night_mode</code>) &mdash;
  and Android isn't one of Craig's devices, so a single <code class="inline">.nightMode</code>
  rule set is sufficient. This deck's CSS still includes commented-out-in-spirit
  <code class="inline">.night_mode</code> duplicate rules purely for parity with the rest of
  this repo's existing CSS convention (every legacy note type duplicates both selectors),
  not because they're required here.
</div>
<div class="usage-note">
  To test: toggle System Settings &rarr; Appearance (macOS) or Settings &rarr; Display &amp;
  Brightness (iOS/iPadOS) between Light and Dark &mdash; or use Anki's/AnkiMobile's own
  in-app night-mode toggle if "follow system" isn't enabled &mdash; then re-open this deck.
  The card chrome (background/text outside the swatch blocks) should flip between Solarized
  Light and Solarized Dark; the swatch blocks themselves are fixed inline colors and won't
  change, since showing the raw palette is the point.
</div>
