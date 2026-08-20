#!/usr/bin/env python3
"""Single source for the JavaScript shared by the two UA typing-feedback scripts.

Both `setup_ua_note_types.py`'s `EN_UA_BACK` and `setup_ua_pvom_note_type.py`'s
`FEEDBACK_SCRIPT` reconstruct what the learner typed out of Anki's `#typeans`
diff, and both therefore need the same `normalizeTypeansText()` helper. Until
2026-08-20 that helper was a hand-maintained *copy* in each script, kept honest
only by a test comparing the two emitted bodies.

That arrangement had already come within one test of failing: the 2026-08-19
Option B rewrite of `EN_UA_BACK` silently deleted the lexeme copy, reverting a
fix that had merged the day before. `test_typeans_normalization.py` caught it,
but only because it checks the emitted JS rather than the Python. This module
removes the duplication instead of guarding it — there is now one body, and
"the two copies drifted" stops being a reachable state.

Why the escaping looks the way it does: these constants are non-raw Python
strings that are embedded verbatim into an Anki card template. `\\u00A0` here
is a two-character Python escape producing a backslash followed by `u00A0`,
which is what JavaScript's regex engine must receive. Writing a literal NBSP
(invisible in an editor and in a diff) or `\\\\u00A0` (a regex matching a
literal backslash, which never matches anything) are the two failure modes
`test_typeans_normalization.py` pins down. Do not "simplify" them.
"""
from __future__ import annotations

# The comment travels with the code deliberately: it is the only place the
# rationale is visible from inside a card template, and a maintainer reading
# the emitted JS in Anki's template editor has no access to this file.
NORMALIZE_TYPEANS_JS = """\
  // Strip Anki's combining-mark isolation artifact out of a reconstructed
  // #typeans string (added 2026-08-18; hoisted to tools/anki/lib/typeans_js.py
  // 2026-08-20 so UA_Lexeme and UA_PVOM_Infinitive share one body rather than
  // two hand-synced copies -- the Option B rewrite dropped the lexeme copy on
  // 2026-08-19 and silently reverted a merged fix).
  // Anki's isolate_leading_mark() (rslib/src/typeanswer.rs) deliberately
  // prepends U+00A0 to any diff chunk BEGINNING with a combining mark, so
  // the mark renders on its own instead of stacking onto the previous
  // chunk's last letter. That nbsp lands INSIDE a .typeGood/.typeBad span,
  // so the reconstruction below swallows it into the typed answer and an
  // otherwise-perfect answer compares unequal. Found on ua-lexeme-0532
  // (2026-08-08). Restore the mark to its base letter; any remaining bare
  // nbsp was a real space.
  function normalizeTypeansText(s) {
    return s.replace(/\\u00A0([\\u0300-\\u036F])/g, '$1').replace(/\\u00A0/g, ' ');
  }
"""
