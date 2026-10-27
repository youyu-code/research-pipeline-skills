# Reporting protocol — R1 to R4

Four commitments a proposal makes **before** the experiment. They exist because the alternative — deciding how to report after seeing the results — is indistinguishable from choosing the reporting that flatters them.

A protocol is not a style guide. Each commitment closes a specific way a result can be true and misleading at the same time.

---

## R1 — A per-experiment table, not an aggregate

**Commitment:** every experiment appears as its own row, with its own condition, before any aggregate is shown.

**What it prevents.** An aggregate is a compression, and compression is where a losing arm disappears. "Average improvement 8%" over six settings that range from −4% to +18% is arithmetically correct and hides the sign change.

**Reviewer behaviour when missing:** asks for the per-setting table. If the paper cannot produce one, the aggregate is treated as unsupported.

**Counter-example:** a proposal promised "consistent gains across benchmarks", listing a mean over eight tasks. The per-task table showed two wins, four ties, two losses. The mean was positive; the claim was false in the sense a reader would understand it.

**Minimum row set:** condition, n, metric, value, dispersion, and the arm it is compared against. Missing dispersion is acceptable only when the experiment produces a single value by construction.

## R2 — Aggregation and weights, stated in advance

**Commitment:** if results are combined, the formula and the weights are written before the run.

| Element | Must be stated |
|---|---|
| formula | the exact expression, not "we average them" |
| weights | per-term, and why those values |
| normalisation | what each term was divided by, and over what range |
| missing-data rule | what happens when a term is unavailable for one setting |

**What it prevents.** A weighted score whose weights were chosen after seeing which weighting ranks the method first. This is not usually dishonest; it is usually a researcher trying several sensible weightings and keeping the one that looks stable.

**Counter-example:** a composite score with four equally weighted terms. Three of the terms were on 0–1 scales and one was on 0–100. The composite was 96% determined by the fourth term, and the paper's "balanced evaluation" was a single metric wearing four names.

**Reviewer behaviour when missing:** recomputes the ranking under two other plausible weightings. If the ranking changes, the composite is reported as unstable rather than reported at all.

## R3 — A negative control arm

**Commitment:** at least one condition is specified in which the method **should fail**, or in which a null result is expected.

**What it prevents.** A pipeline where every arm improves has a measurement problem, not a method. The negative control is the only arm that can detect it.

| Control shape | What it tests |
|---|---|
| shuffled labels / randomised input | the metric is not measuring the label leakage |
| a known-bad baseline run through your pipeline | your pipeline can reproduce a failure |
| the method with its key component removed | the component is doing the work |
| an out-of-distribution condition | the claim's stated scope is real |

**Reviewer behaviour when missing:** treats every reported improvement as uncalibrated, and asks which arm would have shown the opposite.

**Counter-example:** a proposal with four arms, all of which beat the baseline, and no ablation. The best arm's advantage came from a preprocessing step applied to all four; removing it flattened all four. Nothing in the reported numbers indicated this, because there was no arm without the preprocessing.

## R4 — An inference statement

**Commitment:** what test will be applied, at what threshold, on what unit of analysis, and what will count as a difference.

| Element | Example of a decision that must be made early |
|---|---|
| unit of analysis | per molecule, per target, per seed — they give different p-values |
| test | paired or unpaired; parametric or not; the reason |
| threshold | α, and whether it is corrected for the number of comparisons |
| effect size | the smallest difference that would matter, stated numerically |

**What it prevents.** The two failure modes are opposite and both common: reporting a 1.6-point gap as a finding with no test, and running a test after the fact on whichever comparison looked largest.

**Counter-example:** a proposal comparing six methods across four datasets, reporting the best of 24 pairwise comparisons as significant at p < 0.05, with no correction. Under a null, one comparison in twenty is expected to clear that bar; 24 comparisons were available.

**Reviewer behaviour when missing:** re-derives the inference from the raw values. If the raw values are not reported (R1 absent), the claim is unassessable.

---

## How the four interact

They are not independent; each one protects the others.

| If this is missing | This also becomes unverifiable |
|---|---|
| R1 (per-experiment table) | R4 — you cannot re-test what you cannot see |
| R2 (weights) | R1 — a per-experiment table under an unstated weighting still hides the sign |
| R3 (control) | R1 — every row can improve for a reason outside the method |
| R4 (inference) | R2 — a composite with no error model cannot be said to differ from another composite |

That is why the protocol is four commitments and not a menu. A proposal that adopts three has adopted none of the ones that depend on the fourth.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "results will be averaged" | R2 with no formula |
| "we will use standard significance testing" | R4 with no test, no unit, no threshold |
| all arms improve | R3 absent, and the improvement is uncalibrated |
| aggregate only | R1 absent; the losing arm is invisible |
| weights chosen after a stability check | R2 violated in substance, satisfied in form |
| "differences will be discussed qualitatively" | R4 declined; the claim cannot fail |

## Checklist

- [ ] Every experiment has a row with condition, n, metric, dispersion.
- [ ] Any composite has a written formula, weights, normalisation, and missing-data rule.
- [ ] At least one arm is specified to fail, and says what its failure would mean.
- [ ] Unit of analysis, test, threshold, correction, and minimum effect size are all named.
- [ ] All four were written before the experiment ran, and the document dates them.
