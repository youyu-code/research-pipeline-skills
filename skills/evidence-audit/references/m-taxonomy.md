# M taxonomy — diagnostic use

The register tags a problem with one of six words. That is a filing decision, and the register owns the vocabulary. **This file is about the other half:** what each tag implies for the evidence you should look for, and the specific mistake each one invites.

| Tag | Look for | The mistake it invites |
|---|---|---|
| `definition` | two uses of one term, each in its own sentence | treating a term switch as sloppiness instead of a finding |
| `wording` | same fact, two sentences, different strength | grading it without reading the numbers |
| `numeric` | two values, one quantity | resolving it by preference for one source |
| `unsourced` | a claim with no locator anywhere | assuming the number does not exist |
| `version` | two documents, one title | auditing a camera-ready against an abstract written for a preprint |
| `self-contradiction` | the paper's own two statements, both checkable | filing it as ambiguity |

---

## `definition`

**What it means for evidence.** The claim cannot be audited until the term is fixed. This is the only tag that blocks the audit itself rather than the claim.

**Look for:** the definition in the methods, the usage in the results. A term defined once and used consistently is not this tag, even if the definition is vague.

**The mistake:** calling it sloppiness and moving on. A term that switches meaning between the definition and the usage usually changes the size of the effect — sometimes the sign.

**Counter-example:** `accuracy` defined per-cell and reported per-molecule. The reported value was 30 points higher under the second reading. The paper was not wrong under either meaning; the tag is what forces the reader to pick one before comparing.

## `wording`

**What it means for evidence.** The numbers agree and the sentences do not. The finding is about the summary, not the data.

**Look for:** the summary sentence in the abstract, and the same claim in the discussion. If both are stronger than the grid, it is not wording — it is `self-contradiction` or a `numeric` problem in disguise.

**The mistake:** grading the wording without reading the numbers, which produces "the authors overstate" as a conclusion with no magnitude attached.

**Counter-example:** "outperforms all baselines" against a table where it ties two and loses one. Filed as `wording`, closed with a one-sentence rewrite — which was correct. But an earlier pass had filed it as `numeric`, and the repair attempted to change the table.

## `numeric`

**What it means for evidence.** Two values exist for one quantity, both locatable. The question is which is primary, and the answer usually comes from the more formal artefact.

**Look for:** the table vs the text; the body vs the supplement; the abstract vs the results.

**The mistake:** resolving by preference. "The larger value is probably from the full run" is a guess, and a guess recorded as a disposition becomes a fact in the next revision. The honest disposition names the rule used (more formal artefact wins; body outranks supplement for headline values) and both values stay visible.

**Counter-example:** a correlation reported as 0.53 and 0.54 in two places. The register entry resolved it to 0.54 "because it appears later". Three months later the supplement was shown to carry a different subset. The disposition had been a coin flip wearing a reason.

## `unsourced`

**What it means for evidence.** The claim has no locator — not in the body, not in the supplement, not in a figure.

**Look for:** exhaustively, before tagging. The supplement is where summary numbers hide, and a number in a figure legend is still sourced.

**The mistake:** tagging `unsourced` after a search of the body only. A missing table is not a missing number, and a number that exists in a supplement the reader did not open is a search failure recorded as a finding about the paper.

**Counter-example:** a percentage tagged `unsourced`. It was in a supplement table that had been attached all along; the earlier review had checked the body PDF only.

## `version`

**What it means for evidence.** The two statements may both be correct, in different documents. Nothing is resolved until the version is fixed.

**Look for:** DOI, running head with volume and pages, pagination. Then check whether the claim and its evidence come from the same document.

**The mistake:** auditing across versions without noticing. This produces `numeric` and `self-contradiction` tags that dissolve on inspection — and each one costs a full review round before it dissolves.

**Counter-example:** a discrepancy between a preprint and its camera-ready, tagged `numeric` and investigated for two rounds. The camera-ready had added an ablation that changed the split; both numbers were right, for their own version.

## `self-contradiction`

**What it means for evidence.** The paper's own two statements, both checkable, cannot both be true. This is the strongest tag and the one that most often gets softened.

**Look for:** the two statements, both quoted, both locatable. If one of them is a number in a table and the other is a sentence, that is enough — the table is the paper speaking.

**The mistake:** filing it as `definition` or `wording` because the contradiction is expressible as a wording problem. It usually is. The difference is that a wording fix does not repair the contradiction; it hides it.

**Counter-example:** two denominators for one population, filed as `wording` and closed by rewording the sentence to match one of them. The other denominator was still in the table, and the next reader found the same contradiction six weeks later.

---

## Tag and verdict are independent

The tag describes the problem; the verdict describes the claim. Every combination is possible:

| | `supported` | `unsupported` | `undecidable` |
|---|---|---|---|
| `numeric` | two values, both consistent with the claim | the primary value contradicts it | the two values straddle the claim's threshold |
| `self-contradiction` | the contradiction is in a claim the paper does not rely on | the contradiction is in the claim being audited | the contradiction cannot be resolved from the material |
| `version` | both versions support it | the version cited does not | the version cannot be established |

**Do not derive one from the other.** A `numeric` tag does not imply `undecidable`, and an `undecidable` verdict does not imply the tag is `version`. The two columns are answered by different questions, and the temptation to align them produces audits that look coherent and are uninformative.

## Retagging

A tag may be changed, and the change is recorded, not edited:

```markdown
M07 · numeric → self-contradiction (2026-02-03): the two values are not two reports
of one run; §4 and Table 2 describe different splits. Retagged; disposition unchanged.
```

Three rules:

- **The old tag stays visible.** A tag that silently changes makes every earlier count wrong without anyone knowing which.
- **The reason is one clause.** A retag with a paragraph of reasoning is a ruling in the wrong field.
- **A retag does not move the entry's status.** If it was open, it stays open; a better label is not a resolution.

## Counter-examples, collected

| Written | Problem |
|---|---|
| `unsourced` after a body-only search | search failure as a finding |
| `numeric` across two versions | dissolves on inspection |
| `self-contradiction` filed as `wording` | the contradiction survives the wording fix |
| tag changed without recording the old one | earlier counts silently invalidated |
| verdict derived from tag | two questions answered by one |
| `definition` used for a vague term | vagueness is not a definition switch |

## Checklist

- [ ] The tag was chosen after the search, not instead of it.
- [ ] `unsourced` was ruled out by checking the supplement and figure legends.
- [ ] `version` was ruled out before any `numeric` or `self-contradiction` tag.
- [ ] `self-contradiction` was not softened to `wording` for repairability.
- [ ] Verdict and tag were answered separately.
- [ ] Any retag records the old tag, the reason, and leaves the status unchanged.
