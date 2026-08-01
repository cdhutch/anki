---
schema: cnsf/v0
domain: demo
note_type: palette_compare
note_id: palette-compare-status
anki:
  model: Palette_Comparison_Demo
  deck: Demo::Palette_Comparison
tags:
- domain:demo
- topic:palette-comparison
- subtopic:status-colors
- status:unverified
fields:
  Verification Notes: ''
---

# front_md

<div class="swatch-title">Status colors: typing-feedback &amp; Compare card</div>
<div class="mini-card pc-warm-bg">
  <div class="status-demo-block">
    <div class="fb-headline status-success">яблуко ✓ PERFECT</div>
    <div class="fb-sub status-success">Correct with stress marks (bonus!)</div>
  </div>
  <div class="status-demo-block">
    <div class="fb-headline status-warning">яблуко ~ CORRECT</div>
    <div class="fb-sub status-warning">Correct letters, but missing stress marks</div>
    <div class="fb-label status-success">Bonus answer:</div>
    <div class="fb-value status-info"><b>я́блуко</b></div>
  </div>
  <div class="status-demo-block">
    <div class="fb-headline status-error">яблуня ✗ INCORRECT</div>
    <div class="fb-sub status-error">Not quite right</div>
    <div class="fb-label status-success">Correct (no stress):</div>
    <div class="fb-value status-success"><b>яблуко</b></div>
    <div class="fb-label status-info">Correct (with stress):</div>
    <div class="fb-value status-info"><b>я́блуко</b></div>
  </div>
  <div class="status-demo-block">
    <div class="compare-prompt-header">Choose the right word:</div>
    <div class="compare-chip-word">студентка</div>
  </div>
  <div class="status-demo-block">
    <div class="compare-warning">⚠ Compare card has no CompareA/B/C/D authored yet -- this card should be suspended.</div>
  </div>
  <div class="status-demo-block">
    <div class="compare-reveal-header">✓ студентка</div>
    <div class="compare-correct-sub">female student</div>
  </div>
</div>

# back_md

<div class="swatch-role">Every block above uses the SAME class names and hex values as the
production CSS in setup_ua_note_types.py / setup_ua_pvom_note_type.py -- this is a preview of
the shipped colors, not an approximation. Five roles: green (status-success / compare-reveal /
compare-correct), orange (status-warning -- kept in the original #ff9800 color family rather
than switched to Gruvbox's yellow), blue (status-info / compare-prompt-header -- Accent B,
already vetted via the iteration cards), red (status-error / compare-warning), rendered on a
Gruvbox card background (reusing pc-warm-bg) since that's what these colors actually sit on in
production.</div>
<div class="usage-note">This is the card that matters most for pass 3 (Night Mode +
red-tint filter) -- see palette-compare-doc. Dark-mode red and orange specifically use
Gruvbox's "bright" tier (#fb4934 / #fe8019), not the muted/neutral tier, chosen for maximum
luminance contrast against the dark background. That's the best choice Claude could make
without being able to preview the filter directly -- if red (INCORRECT) or orange (CORRECT,
no stress) reads as washed-out or hard to distinguish from the background or from each other
in pass 3, that's the signal this card exists to catch.</div>
