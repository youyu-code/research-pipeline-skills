# Reversal tiers

When later evidence changes a claim's standing, the change has a magnitude. Four tiers, and the tier is a definition, not a judgement of importance.

Define the tiers **before** counting. A count produced first is a count of the word "reversed", not of the thing.

| Tier | Name | Operational test |
|---|---|---|
| **T1** | rank flip | two methods' ordering reverses on the same metric |
| **T2** | strength collapse | the direction holds, the effect drops inside the noise band |
| **T3** | scope narrowing | holds inside a boundary, fails outside it |
| **T0** | not a reversal | restated, re-measured, re-scoped, or refined without changing the claim |

---

## T1 — rank flip

**Test:** `A > B` becomes `B > A`, on a comparable metric.

Requirements, all three:

1. the same metric family (a flip between AUPR and ROC-AUC is a metric change, not a reversal);
2. both orderings measurable from reported values — not from a figure, not from an axis;
3. the flip carries a **band annotation**: `band: in-band | outside-band | unestimated`.

The band annotation is **mandatory and never decides the tier**. A flip that reversed is T1 whether or not its margin is measurable; what the annotation decides is the *citation form*:

| `band` | May be cited as |
|---|---|
| `outside-band` | "the ordering reversed" — a settled reversal |
| `in-band` | "the ordering reversed, within the noise band" — recorded, not relied on |
| `unestimated` | "an ordering was reported to reverse; no band was available" — a claim about the reporting, not about the field |

`in-band` is the state `synthesis-matrix` calls **within band**, and the two mean the same thing: the difference is smaller than the measurement's own disagreement. Neither file may drop the annotation and neither may upgrade it into a verdict.

**Fails the test when:** the methods were never compared under the same condition, so no ordering existed to reverse.

**Counter-example:** a "reversal" recorded because a later paper reported a different method winning — on a different dataset, with a different engine, on a metric of a different family. Nothing reversed; two incomparable measurements were compared.

## T2 — strength collapse

**Test:** the direction holds, but the effect falls inside the noise band, so the original claim's magnitude no longer exists.

This is the tier people skip, because it looks like "no change": A is still ahead of B. But a claim that said "substantially better" is dead even when the ranking survives.

| Before | After | Tier |
|---|---|---|
| +12 points, significant | +1.5 points, **within band** | **T2** |
| +12 points | +11 points, same band | T0 |

**Requirements:** a band. Without one, a collapse cannot be distinguished from noise in either direction. If no band is available the effect is `unestimated`: record T0 with the annotation, not T2 by impression. `within band` here is the same phrase and the same threshold as `synthesis-matrix` uses for a matrix cell — one number, one definition.

## T3 — scope narrowing

**Test:** the claim still holds inside a boundary that later evidence establishes, and fails outside it.

The output must state the boundary, in the terms the later evidence uses:

> *holds for within-family scaffolds; fails for cross-family* — not *holds in general but weaker*.

**Why this is a reversal and not a refinement:** the original claim, as a reader would have understood it, is false in the region outside the boundary. The tier records that the claim has a smaller domain than it asserted.

**Counter-example:** a "narrowing" was recorded for a method that still worked everywhere, just less well on one subgroup. That is T0 — a weaker effect, not a smaller domain. The distinction is whether the claim is *false* outside the boundary or merely *smaller*.

## T0 — not a reversal

Four shapes, all commonly counted as reversals:

| Shape | Why it is T0 |
|---|---|
| restated in different words | no change in standing |
| re-measured on a new sample, same conclusion | replication, not reversal |
| refined (a sub-claim added) | the original claim still holds |
| a correction of a number inside the band | not a change in standing |

**Rule of doubt:** when a claim sits between T3 and T0, choose T0 and record why. Tier inflation is systematic in one direction — reviewers classify ambiguous cases upward, because an upward classification sounds like a finding.

## Counting rules

1. **Count per claim, not per sentence.** A claim restated in an abstract and in §5 is one claim. Counting sentences inflates the denominator.
2. **One tier per claim.** A claim cannot be both T1 and T3 in one count; if both occurred at different times, it is two events with two tiers.
3. **Report the breakdown, never the bare total.** "7 reversals" is not a number anyone can use. "3 T1, 2 T2, 2 T3" is.
4. **The denominator is the population of claims examined**, not the population of reversals found.

**The effect of getting this wrong:** in the corpus where these tiers were introduced, an existing count of reversals was reclassified. **Two of twelve** claims moved out of the reversal column, and the headline rate fell by roughly a sixth. Nothing about the evidence had changed — only the definition.

## What a tier is not

| Not a tier | Because |
|---|---|
| severity | T1 is not "worse" than T3 for a project; they break different things |
| a blocker level | a T1 does not stop work; it changes what a claim may say |
| a repair priority | what to fix first is a different scale, and converting between them is an error |
| a judgement about the authors | every tier here is consistent with careful work |

## Output shape

```markdown
claim:     "<the claim, quoted>"
tier:      T1 | T2 | T3 | T0
before:    <the earlier standing, with locator>
after:     <the later standing, with locator>
band:      in-band | outside-band | unestimated   (mandatory for T1; decides citation form, not tier)
boundary:  <for T3 only: the region where the claim fails>
basis:     <why not the neighbouring tier>
```

The `basis` line is the discipline: every tier decision has a neighbouring tier it could be confused with, and naming why it is not that one is what makes the count reproducible.

## Counter-examples, collected

| Written | Problem |
|---|---|
| count of 12, no tiers defined | a count of a word |
| T1 across metric families | a metric change, not an ordering flip |
| T1 with no `band` field | the reversal is asserted without saying whether it is measurable |
| T2 with no band | a collapse asserted by impression |
| T3 for a uniformly weaker effect | that is T0; the domain did not shrink |
| claim counted twice (abstract + body) | denominator inflated |
| "8 reversals (67%)" with no breakdown | unusable, and hides that most are T3 |
| T1 treated as a blocker | a tier converted into a stop |

## Checklist

- [ ] Tiers defined before counting.
- [ ] Every reversal has before/after with locators.
- [ ] T1 requires a comparable metric, both orderings measurable, and a `band` annotation.
- [ ] T2 requires a band; without one, T0 with a note.
- [ ] T3 states the boundary where the claim fails.
- [ ] Counted per claim; breakdown reported; denominator stated.
- [ ] No tier converted into a blocker or a repair grade.
