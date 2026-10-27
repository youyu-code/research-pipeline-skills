# Audit design

An audit table is built **before** the experiment, not after. Its job is to tell you what data to collect, and its output is a verdict per claim: `supported` / `unsupported` / `undecidable`.

A table built after the fact is a summary. A table built before is a design constraint — and the difference shows up in which claims were never tested because nobody wrote down what would falsify them.

---

## One row per claim

```markdown
| # | claim | falsifier | data available | verdict | cost to close |
|---|---|---|---|---|---|
| 1 | the ranking step improves held-out recall | held-out recall ≤ baseline on ≥2 of 4 sets | none — all sets used for tuning | undecidable | one new split, ~1 week |
| 2 | the method is robust to scaffold noise | AUC drops >0.05 under 10% noise | one noise level run | unsupported | 4 noise levels |
| 3 | preprocessing reduces variance | variance unchanged with/without | ablation reported | supported | — |
```

| Column | Rule |
|---|---|
| `claim` | one sentence, falsifiable as written. "The method is better" fails this test; "better on X under Y" passes |
| `falsifier` | the observation that would make the claim false. If you cannot write it, the claim is not a claim |
| `data available` | what exists **now**, from the cards and the register |
| `verdict` | one of three words; a claim cannot be left blank |
| `cost to close` | effort to move an `undecidable` to `supported`/`unsupported` |

## The falsifier column is the whole tool

A row without a falsifier is not an audit row. Three shapes that look like falsifiers and are not:

| Written | Why it is not a falsifier |
|---|---|
| "if the results are not good enough" | no threshold, no comparison |
| "if it does not generalise" | to what? unspecified |
| "if reviewers disagree" | a fact about reviewers, not about the claim |

A usable falsifier names **an observation**, **a comparison**, and **a direction**: *"held-out recall no better than baseline on at least two of four sets."*

## The three verdicts

| Verdict | Means | What a reviewer does |
|---|---|---|
| `supported` | the data available would distinguish the claim from its negation, and it favours the claim | accepts, cites the row |
| `unsupported` | the data exists and points the other way, or the claim's own numbers do not reach its threshold | the claim is removed or rewritten |
| `undecidable` | no available data could distinguish the claim from its negation | the claim is retained **only** with its cost to close stated |

**`undecidable` is not a soft `unsupported`.** It is the most useful verdict in the table, because it is the only one that produces a work item. A table with no `undecidable` rows is usually a table whose rows were chosen to be answerable.

**Counter-example:** an audit of 22 claims with 20 `supported` and 2 `unsupported`. Reviewing the source material showed that 11 of the 20 had no data that could have contradicted them — they were tautologies written as findings ("the model performs as expected on the data it was trained on"). The audit had measured nothing and looked thorough.

## Preconditions before the first row

Three checks, all cheap:

1. **The claim is quoted from the proposal, not paraphrased.** A paraphrase drifts toward what is testable.
2. **The data source is named, not implied.** "From the matrix" is not a source; a cell with a card locator is.
3. **The claim's scope is written.** Population, condition, and comparison. A claim that silently widens its scope between the audit and the write-up has been re-scoped without a decision.

## Designing the table for the experiment you are about to run

The forward use: for each claim you *intend* to make, write the row now, with `data available: none`. The `cost to close` column becomes the experiment plan, ordered by cost.

This is why the audit belongs in the forge phase rather than the write-up phase. A claim whose closure costs three weeks and a claim whose closure costs one afternoon are different proposals, and only the table makes that visible before the work starts.

## What the table must not become

| Anti-pattern | Symptom |
|---|---|
| a list of everything the paper says | 40 rows, no priorities, no decision attached |
| a second discussion section | rows whose `falsifier` is a paragraph |
| a self-assessment | every verdict `supported`, no `undecidable` |
| a to-do list | `cost to close` filled, `falsifier` empty |

The table has one job: for each claim, say whether the evidence in hand can tell it apart from its opposite.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "supported by the literature" | no falsifier, no data named |
| "undecidable — needs more work" | cost not stated, so it cannot be planned |
| falsifier as a feeling | "if it does not hold up" |
| all rows `supported` | rows chosen for answerability |
| claim paraphrased at audit time | the audited claim is not the proposed one |
| verdict omitted on a hard row | the row that mattered is the one left blank |

## Checklist

- [ ] One row per claim, claim quoted verbatim from the proposal.
- [ ] Every row has an observation-comparison-direction falsifier.
- [ ] Verdict is one of three words, never blank.
- [ ] `undecidable` rows carry a cost to close, and become work items.
- [ ] Data sources named at card-and-locator resolution.
- [ ] At least one row admits it cannot be decided — otherwise check the rows, not the method.
