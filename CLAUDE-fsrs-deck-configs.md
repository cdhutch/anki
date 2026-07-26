# FSRS Deck Configurations — B737, UA, Legacy

**Principle:** Each top-level deck has completely isolated FSRS parameters. Cards in one deck tree do not influence scheduling algorithm for another.

---

## Overview

FSRS (Free Spaced Repetition Scheduling) v4.5 is now native to Anki 23.10+. Each deck config has:
- **Desired retention** (0.70–0.97): How many cards should you remember? (0.90 = 90%)
- **Learning steps** (minutes): e.g., [1m, 10m] — must complete same day; FSRS optimizes from here
- **Relearning steps** (minutes): e.g., [10m] — when a lapsed card is reviewed
- **Maximum interval** (days): Cap on longest spacing (36500 days ≈ 100 years is typical default)
- **Easy/Hard multipliers**: FSRS-specific (minimal tuning needed)

---

## B737 — Professional Type Rating (High Stakes)

**Context:** Aviation safety depends on recall. High stakes → high retention target.

### Recommended Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Desired retention** | 0.93–0.95 | Safety-critical; minimize forgetting. 0.95 = 95% recall target. High end of professional certification range. |
| **Learning steps** | 1m 10m | Standard same-day learning. FSRS will optimize intervals between/after. |
| **Relearning steps** | 10m | Single step; FSRS handles most of the scheduling. |
| **Maximum interval** | 365–730 days | Optional: cap at 1–2 years to maintain currency (aircraft procedures change). Default 36500 is fine if you don't mind very long gaps. |
| **Easy bonus** | 1.3 | FSRS default (minor adjustment). |
| **Hard penalty** | 1.2 | FSRS default. |
| **Lapse multiplier** | 0.9 | FSRS default; cards that lapse maintain slightly reduced interval. |

### Notes

- At 0.95 desired retention, daily reviews may be heavy (~30–50 cards/day depending on deck size), but this is acceptable for high-stakes material.
- If workload becomes unsustainable, reduce to 0.92–0.93 after 2–3 weeks of real data.
- Consider increasing to 0.97–0.98 only in final weeks before a checkride or rating exam.

---

## UA — Language Learning (Active Production/Comprehension)

**Context:** Language has context clues and variability. Slightly lower retention is acceptable and more sustainable.

### Recommended Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Desired retention** | 0.85–0.90 | Language is learnable with context. 0.85 if high daily volume; 0.90 if more leisurely. 25% reduction in reviews vs. 0.95 target. |
| **Learning steps** | 1m 10m | Standard for language; FSRS optimizes intervals. |
| **Relearning steps** | 10m | Single step; let FSRS schedule. |
| **Maximum interval** | 36500 days | Long spacing is actually beneficial for language; no need to cap. |
| **Easy bonus** | 1.3 | FSRS default. |
| **Hard penalty** | 1.2 | FSRS default. |
| **Lapse multiplier** | 0.9 | FSRS default. |

### Notes

- Research shows 85–90% is optimal for language learning (~25% fewer reviews than 0.95 while maintaining fluency).
- UA is organized into recognition (UA→EN) and production (EN→UA) subdecks; both share this config.
- Longer intervals (100+ days) are acceptable for vocabulary; spaced exposure + context = retention.
- If you find yourself forgetting too much (< 85% actual retention), bump to 0.90. If reviews spike, reduce to 0.85.

---

## Legacy — Archive/Reference (Low Priority)

**Context:** Existing older decks; most suspended or low-priority. Minimal active study.

### Recommended Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Desired retention** | 0.80–0.85 | Not actively studied; conservative settings. If cards are mostly suspended, this is largely moot. |
| **Learning steps** | 10m 1d | Slower consolidation; not a daily focus. |
| **Relearning steps** | 1d | More conservative for lapsed cards. |
| **Maximum interval** | 180–365 days | Optional: shorter cap to keep archived material somewhat current if occasionally reviewed. Default 36500 is fine. |
| **Easy bonus** | 1.3 | FSRS default. |
| **Hard penalty** | 1.2 | FSRS default. |
| **Lapse multiplier** | 0.9 | FSRS default. |

### Notes

- Legacy decks are primarily a holding pattern; most cards will be suspended or tagged for later migration.
- As Legacy content is mined and migrated to active decks (B737, UA), those cards move to the appropriate deck config.
- The 0.80 target ensures Legacy cards don't consume daily review budget if accidentally unsuspended.

---

## Implementation Steps

1. **Create deck configs in Anki:**
   - Deck → Manage → New config
   - Name each: "B737 FSRS", "UA FSRS", "Legacy FSRS"
   - Set desired retention, learning/relearning steps, max interval

2. **Assign configs to deck trees:**
   - Right-click `B737::` → Options → Set config to "B737 FSRS"
   - Right-click `UA::` → Options → Set config to "UA FSRS"
   - Right-click `Legacy::` → Options → Set config to "Legacy FSRS"

3. **Verify isolation:**
   - Anki deck config menu shows each top-level deck assigned its own config
   - Cards studied in one tree do not influence FSRS algorithm weights for others
   - Monitor actual retention rates for 2–3 weeks; adjust if needed

---

## Monitoring & Tuning

After 2–3 weeks of real study data:

1. **Check actual retention** in Anki: Deck → Study → Stats (Retention %)
2. **Compare to desired retention:**
   - If actual > desired by 5%+: You're over-reviewing; reduce desired retention by 0.02–0.03
   - If actual < desired by 5%+: You're forgetting too much; increase desired retention by 0.02–0.03
3. **Adjust incrementally;** don't swing retention targets wildly

---

## References

- FSRS Tutorial: https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md
- Expertium's Retention Guide: https://expertium.github.io/Retention.html
- Expertium's Learning Steps: https://expertium.github.io/Learning_Steps.html
