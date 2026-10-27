# Attribution — defect or ambiguity

A verdict says whether a claim stands. Attribution says **why**, and the why determines who can fix it.

| | defect | ambiguity |
|---|---|---|
| **What is wrong** | the paper is wrong | the paper is unclear |
| **Who fixes it** | the authors, with new data or a correction | the authors, with one sentence |
| **Checkable by** | comparing against a fact | comparing against a stated reading |
| **Fails when** | the contradiction is not produced | the second reading is not produced |

Four names, each a single unbreakable token so that no shorthand can drift between files:

| Name | Means | Checkable against |
|---|---|---|
| `defect-self-data` | contradicts its own reported data | the paper's other statements |
| `defect-external-fact` | contradicts an external fact | the cited fact or identity |
| `ambiguity-two-readings` | one sentence supports two readings | two textual anchors |
| `ambiguity-term-overload` | one term carries two meanings | both usages, quoted |

The first word is the family (it decides who fixes it), the rest is the cell. Never abbreviate them back to a letter: a two-letter label is exactly the shorthand that gets misread across files.

---

## The judging order

```
1. Is there a contradiction with something checkable?
      yes, inside the paper   → defect-self-data
      yes, outside the paper  → defect-external-fact
      no                      → step 2
2. Are there two readings, each anchored in the paper's own text?
      yes                     → ambiguity-two-readings, or
                                ambiguity-term-overload if the switch is in a term
      no                      → no verdict / undecidable
```

**The order is not negotiable.** Ambiguity is the escape hatch, and taking it first converts errors into wording problems. A paper that states two incompatible numbers has a defect even if its sentences are also vague — the defect is the finding, the vagueness is a second finding.

**Why step 1 is cheap:** a defect needs one comparison. An ambiguity needs two quotations that genuinely diverge. If you cannot produce the two quotations, you were not looking at an ambiguity.

## `defect-self-data` — contradicts its own data

The most common and the most consequential. Forms:

| Form | Shape |
|---|---|
| summary vs grid | "consistently outperforms" against a 2-of-8 grid |
| two numbers, one quantity | the same cohort counted twice |
| text vs table on the statistic | text says median, table reports a mean |
| method vs result | the described protocol could not produce the reported split |

**Requirement:** both sides quoted, with locators, in the same row.

**Counter-example:** a claim of "state-of-the-art on all four benchmarks" audited as `unsupported` with no attribution. The table showed losses on two. The finding was `defect-self-data`, and saying so is what made the correction possible — the fix was to the sentence, not to the experiment.

## `defect-external-fact` — contradicts an external fact

The paper contradicts something true outside it: a physical constant, an arithmetic identity, a defined term used against its definition.

**Requirement:** the external fact must be cited too, or it is opinion. "The reported sum does not equal the reported total" is checkable; "the effect size is implausibly large" is not, unless a bound is given.

**Counter-example:** a table's percentages summed to 104%. Audited as "rounding", which is T0-ish and generous. The correct attribution was `defect-external-fact` — an arithmetic identity, violated, with no rounding convention that could explain four points.

## `ambiguity-two-readings` — two readings of one sentence

**Requirement:** two quotations, or one quotation that genuinely parses two ways, **plus** a statement of what changes under each reading.

| Weak ambiguity | Strong ambiguity |
|---|---|
| "improves performance" — on what? | "improves performance on the held-out sets" where §4 says the sets were used for tuning |
| a term without a definition | the definition given in §2 and the usage in §5 diverge |

The first is vagueness, which is a quality complaint and not an audit finding. The second is ambiguity: two anchored readings with different consequences.

**Test:** if both readings lead to the same verdict, it is not an ambiguity worth ruling on. State that, and rule.

## `ambiguity-term-overload` — a term with two meanings

The highest-value cell, and the rarest. A term used in two senses, where the switch is not flagged:

- `accuracy` = per-cell in §2, per-molecule in §5;
- `baseline` = the paper's own ablation in one table, the field's standard method in another;
- `zero-shot` = unseen target in one section, unseen scaffold in another.

**Requirement:** both usages quoted. The finding is the switch, not the term.

## Three trace fields, every row

A ruling that cannot be re-derived is a ruling nobody can overturn, which is not the same as being right.

```markdown
| claim | attribution | compared | where | would-flip-if |
|---|---|---|---|---|
| C-04 | defect-self-data | text "median" vs Table 2 header "mean" | §4 ¶2 vs Table 2 | the table's header were a footnote to a different column |
```

| Field | Rule |
|---|---|
| `compared` | both sides, named as objects, not as conclusions |
| `where` | two locators; one locator means one side was not found |
| `would-flip-if` | the observation that would change this attribution. If nothing would, the attribution is an opinion |

`would-flip-if` is the field that makes an audit an audit rather than a review. It is also the field most often left empty, and an empty one is visible.

## Counter-examples, collected

| Written | Problem |
|---|---|
| ambiguity claimed with one quotation | only one reading anchored |
| "vague" filed as ambiguity | vagueness is not an audit finding |
| defect asserted with no locator for the other side | unfalsifiable |
| summary vs grid filed as ambiguity | it is a defect; the grid is unambiguous |
| term switch not noticed because both usages are in the same section | the finding was skipped, not absent |
| `would-flip-if` empty | opinion, not attribution |
| defect-external-fact with no citation for the external fact | opinion about plausibility |

## Checklist

- [ ] Step 1 (contradiction) tested before step 2 (two readings).
- [ ] Every defect carries both sides with locators.
- [ ] Every ambiguity carries two anchored readings and says what changes under each.
- [ ] Term switches (§2 vs §5) checked explicitly.
- [ ] `compared`, `where`, `would-flip-if` filled on every row.
- [ ] Vagueness noted as a quality remark, not filed as ambiguity.
