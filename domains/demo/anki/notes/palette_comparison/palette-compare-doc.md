---
schema: cnsf/v0
domain: demo
note_type: palette_compare
note_id: palette-compare-doc
anki:
  model: Palette_Comparison_Demo
  deck: Demo::Palette_Comparison
tags:
- domain:demo
- topic:palette-comparison
- subtopic:documentation
- status:unverified
fields:
  Verification Notes: ''
---

# front_md

<div class="swatch-title">Demo: Solarized+ Palettes — how to test this deck</div>
<div class="usage-note">(Tap/click to flip for the three-pass walkthrough.)</div>

# back_md

<div class="swatch-role">Three candidate palettes, one question: which stays most
legible once a red-tint filter sits on top of it? Solarized (this repo's current choice,
cool-toned), Monochrome (no hue at all — differentiates by weight/style instead), and a
Warm/Gruvbox-style palette (already orange/red/yellow-leaning). See palette-compare-reference
for the full hex table.</div>
<div class="usage-note">Three "iteration" cards — palette-compare-solarized,
palette-compare-monochrome, palette-compare-warm — each a composite mini-mockup of an
actual card (lemma/meta/gloss/example/cf line) rendered entirely in that one palette,
plus palette-compare-reference showing all three palettes' roles stacked in one place.
Gruvbox ("Warm") was chosen from these four after the first round of testing — a fifth
card, palette-compare-status, was added afterward to preview the status-color system
(typing-feedback script + Compare card: success/error/warning/info) using the exact
classes and hex values now shipped in setup_ua_note_types.py / setup_ua_pvom_note_type.py.
All of them render live off your device's actual current appearance — same
<code class="inline">.nightMode</code> control code as every other note type in this repo —
so the same card face is what you re-view in each of the three passes below, not a
precomputed side-by-side.</div>
<table class="control-code-table">
  <tr><th>Pass</th><th>Device state</th><th>What you're checking</th></tr>
  <tr><td>1. Demo Solarized+ Palettes in Day mode</td>
      <td>System appearance: Light. Red-tint Color Filter: off.</td>
      <td>Baseline legibility — all three palettes should read fine here; this pass is
          mostly to confirm the deck itself is working before the modes that matter.</td></tr>
  <tr><td>2. Demo Solarized+ Palettes in Night Mode</td>
      <td>System appearance: Dark. Red-tint Color Filter: off.</td>
      <td>Ordinary dark-mode legibility, no filter yet — isolates whether a palette has
          problems in the dark before adding the filter on top.</td></tr>
  <tr><td>3. Demo Solarized+ Palettes in Night Mode with Red-light filter</td>
      <td>System appearance: Dark. Settings → Accessibility → Display &amp; Text Size →
          Color Filters → Color Tint → Hue: near-full-left (red-dominant). Filter: on.</td>
      <td>The actual target scenario — protecting night vision. This is the pass that
          decides it: which palette (and which specific role — background/primary,
          secondary, Accent A, Accent B) is still comfortably readable once the red tint
          is sitting on top of the dark-mode colors from pass 2?</td></tr>
</table>
<div class="usage-note">Go through all five cards (the three iterations, the reference, and
status) in each pass, in the order above, on the same device — the point is comparing the
*same* cards across the three device states, not comparing devices. Note which palette wins
overall in pass 3 specifically; passes 1–2 are context, not the decision. For
palette-compare-status specifically, pass 3 is the one that matters most — that card exists
to confirm the shipped red (error) and orange (warning) status colors stay distinguishable
and don't wash out under the red-tint filter, not to pick a palette.</div>
