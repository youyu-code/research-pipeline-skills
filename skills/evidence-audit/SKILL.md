---
name: evidence-audit
description: >-
  Adjudicate one specific claim: is it supported, unsupported, or undecidable given
  the numbers actually available. Use when the input is a claim rather than a paper —
  a quoted sentence plus its reported figures — and the answer must be a verdict with
  a stated evidence boundary. Applies three ordered tests (claim anchoring,
  counter-evidence, availability), a four-tier reversal scale (rank flip / strength
  collapse / scope narrowing / not a reversal), and the rule that a second number in
  the same table does not by itself license a second reading. Input: claim text,
  available numbers with provenance, and the material boundary stating what was and
  was not read. Output: verdict, tier, attribution as defect versus ambiguity, and
  the exact citation form allowed. It does not build cards, matrices or proposals;
  given a whole paper to document rather than a claim to rule on, use paper-card.
---

# evidence-audit

One claim in, one verdict out, with the boundary of the evidence stated in the same breath.

The discipline is entirely in **refusing to rule** on the cases where the material does not permit it. A verdict of `undecidable` is a success, not a failure to try.

## The three tests, in this order

| Order | Test | Question | If it fails |
|---|---|---|---|
| 1 | **anchoring** | which sentence, in the paper, states this claim | no verdict — the claim is your paraphrase |
| 2 | **counter-evidence** | does the paper itself contain something that refutes it | `unsupported`, with the quote |
| 3 | **availability** | could the available material distinguish the claim from its negation | `undecidable`, with the missing artefact named |

The order matters: a claim with no anchor cannot be audited at all, and a claim with an anchor plus a direct refutation does not need the availability test.

→ `references/three-tests.md`

## Two rules that decide most cases

- **A numeric anchor is not an anchor.** If the same table reports another number that would support a second reading, the claim is still a claim: only the paper's own sentence counts as the anchor. Otherwise every paper that reports a full table is automatically immune, and the `undecidable` category becomes structurally empty.
- **"Not discussed" is not "not claimed".** An absence of discussion is not ambiguity. A factual statement that the paper can be seen to contradict is a defect, not an ambiguity, no matter how little the authors say about it.

→ `references/counter-examples.md` for the eight rulings that look correct and are not.

## Reversal tiers

When later evidence changes a claim's standing, the change has a **tier**, and the tier is not a matter of emphasis:

| Tier | Name | Test |
|---|---|---|
| **T1** | rank flip | the ordering of two methods reverses |
| **T2** | strength collapse | the direction holds, the effect goes to zero |
| **T3** | scope narrowing | holds inside a stated boundary, fails outside |
| **T0** | not a reversal | restated, re-measured, or re-scoped without changing the claim |

Count after defining, never before. A count of "reversals" produced before the tiers exist overstates: in the one corpus where this has been checked, five of twelve findings moved out of the reversal column (12 → 7).

→ `references/reversal-tiers.md`

## Attribution

Every non-trivial ruling also says **what kind of problem it is**. Four names, used verbatim:

| Name | Means |
|---|---|
| `defect-self-data` | the paper contradicts its own reported data |
| `defect-external-fact` | the paper contradicts a checkable outside fact |
| `ambiguity-two-readings` | one sentence supports two anchored readings |
| `ambiguity-term-overload` | one term carries two meanings |

The first word decides who fixes it: a defect needs new data or a correction, an ambiguity needs one sentence. Confusing them sends a defect to the authors as a wording question, and an ambiguity back as an error.

→ `references/attribution.md`

## What this skill refuses

- **Refuses to rule on a paper.** That is `paper-card`: a card documents, this rules on one claim.
- **Refuses to rule without an anchor.** A paraphrase is not auditable, and rewriting the claim until it is auditable is how audits produce their own answers.
- **Refuses to convert its output into a blocker level or a repair priority.** Verdicts live here; stopping decisions and repair order belong to the pipeline's operating layer.

## Output contract

```markdown
claim:     "<quoted, with §>"
anchor:    "<the sentence that states it, with §>"
verdict:   supported | unsupported | undecidable
basis:     <the test that decided it, and its result>
tier:      T1 | T2 | T3 | T0 | n/a
attribution: defect-self-data | defect-external-fact | ambiguity-two-readings | ambiguity-term-overload | n/a
boundary:  <material read, and what was not>
allowed:   "<the exact citation form this verdict permits>"
```

The `boundary` line is not optional: a verdict without its evidence boundary reads as absolute.

## Routing

| Task | Go to |
|---|---|
| run the three tests on a claim | `references/three-tests.md` |
| classify how a claim's standing changed | `references/reversal-tiers.md` |
| decide defect versus ambiguity | `references/attribution.md` |
| tag the problem for the register | `references/m-taxonomy.md` |
| check a ruling against known failure shapes | `references/counter-examples.md` |
| document a whole paper | `paper-card` |
| compare several papers | `synthesis-matrix` |
| act on a verdict inside a proposal | `proposal-forge` |
