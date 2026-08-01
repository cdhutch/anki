---
schema: cnsf/v0
domain: demo
note_type: solarized_swatch
note_id: solarized-demo-repo-dark-bg-vs-canonical
anki:
  model: Solarized_Palette_Demo
  deck: Demo::Solarized_Palette
tags:
- domain:demo
- topic:solarized-palette
- subtopic:comparison
- status:unverified
fields:
  Verification Notes: ''
---

# front_md

<div class="swatch-title">Repo dark background vs. canonical base03</div>
<div class="legibility-row">
  <div class="legibility-box" style="background-color: #032029; color: #93a1a1;">
    #032029
    <div class="legibility-caption">This repo's current dark-mode background</div>
  </div>
  <div class="legibility-box" style="background-color: #002b36; color: #93a1a1;">
    #002b36
    <div class="legibility-caption">Canonical Solarized base03</div>
  </div>
</div>

# back_md

<div class="swatch-role">
  Every existing note type's CSS in this repo (<code class="inline">update_legacy_css.py</code>,
  <code class="inline">setup_structured_model.py</code>, <code class="inline">setup_table_model.py</code>,
  etc.) sets <code class="inline">.nightMode .card</code> background to <code class="inline">#032029</code>,
  not the canonical Solarized base03 (<code class="inline">#002b36</code>). The two are close but not
  identical &mdash; use the side-by-side swatch on the front of this card to judge whether it's worth
  standardizing the whole repo on the canonical value.
</div>
<div class="meta-row">This demo deck's own card chrome uses the canonical #002b36 in night mode
(see CSS in <code class="inline">tools/anki/setup/setup_solarized_demo.py</code>), specifically so it
reads differently from your existing decks and this comparison is visible.</div>
