# Comparability

Two numbers may share a column only if they answer the same question the same way. Four gates, in this order; failing any of them means the cells go in different columns, or the comparison is written as "not comparable" in the cell itself.

| Gate | Question | Fails when |
|---|---|---|
| 1 — metric family | is this the same metric | AUPR vs ROC-AUC |
| 2 — statistic | same summary of the same distribution | mean vs median; single seed vs best-of-5 |
| 3 — measurement engine | same tool, same version class | two docking engines; two library versions |
| 4 — provenance of the run | same party, same protocol | original authors vs a re-implementation |

Only after all four pass does the size of the difference matter.

---

## Gate 1 — metric family

| Metric pair | Comparable | Why |
|---|---|---|
| AUROC vs AUPR | **no** | different question: ranking over all thresholds vs precision at recall |
| accuracy vs balanced accuracy | **no** | class-prior dependent |
| RMSE vs MAE | **no** | different loss; RMSE penalises tails |
| Pearson vs Spearman | **no** | linear vs monotone |
| R² vs Pearson r | **no** | one is variance explained, the other is correlation |

**Counter-example:** a matrix row read "zero-shot performance 0.641", compared against another paper's 0.759, concluding a capability gap. One number was AUPR and the other ROC-AUC. The gap measured the metric, not the model — and because both numbers were plausible for either metric, nothing in the table looked wrong.

**Rule:** the metric name goes in the column header **and** in the cell's source note. A column titled "performance" is a column that will eventually mix families.

## Gate 2 — statistic

Same metric, different summary, opposite conclusions.

| Situation | Comparable |
|---|---|
| mean over 5 seeds vs best of 5 | no — the best-seed number is an order statistic, not a central one |
| mean vs median on a skewed distribution | no |
| mean ± SD vs median (IQR) | no |
| mean over targets, unweighted, vs mean over molecules | no — different denominator |

**Counter-example:** one paper reported a mean that lost to baseline; another reported a median that beat it, on the same benchmark with the same metric. Both numbers were correct. A matrix that put them in one column produced a trend that reversed depending on which paper was read first.

**Rule:** if the statistic is not stated in the source, the cell carries `statistic: unknown` and the column is not used for ranking.

## Gate 3 — measurement engine

Two tools measuring "the same thing" rarely agree to the precision being compared.

Observed shapes worth knowing — **these are examples of magnitude, not constants; measure your own**:

- The same model scored by different engines in the same paper: differences of several percentage points, in a consistent direction.
- The same model re-run on a later library version: differences of a fraction of a point to a couple of points.

| Rule | Reason |
|---|---|
| name the engine in the cell | a value without its engine is not attributable |
| never mix engines within a column | the column becomes a comparison of tools |
| when the gap is smaller than the observed engine disagreement, write "within engine band" | the difference is not evidence |

**Counter-example:** a table mixed two docking engines and reported a 7-point improvement for one method. Re-scored on a single engine, the improvement was inside the engine disagreement. The table was internally consistent and the ranking it supported did not exist.

## Gate 4 — provenance of the run

| Case | How to label it |
|---|---|
| the authors' own reported number | `as-reported` |
| a re-implementation by a later paper | `re-implemented by <paper>` |
| your own re-run | `re-run by us on <tool> <version>` |

**A re-implementation is not the original's performance.** It measures the method *plus* the re-implementer's choices, and the difference is often larger than the effect being claimed.

**And the reverse is not true either:** a re-run that reproduces the original within noise does not count as an independent replication unless it was run independently. Label it, do not promote it.

**Counter-example:** a model from an older paper re-implemented on a modern toolkit and entered into a comparison as that paper's score. Every "improvement over the original" computed from that cell was measuring a five-year toolkit gap, not a method.

## Noise bands, and how to get one

A band is the size of a difference you should expect **when nothing is different**. It cannot be borrowed; it is a property of the metric, the benchmarks, and the field's reporting habits.

Three ways to get one, in order of preference:

1. **Repeated runs of the same model** in the source material (same protocol, different seeds) — the spread is the band.
2. **Cross-source agreement**: the same model reported by three papers — the range is the band.
3. **Published variance** if the paper reports SD or CIs — the interval is the band.

If none is available, say so: `band: unestimated`. A cell marked that way may be displayed but not used to rank.

**What a band is for:** to convert "0.912 vs 0.896" from a finding into a non-finding. When the difference is inside the band, the honest cell reads `within band` — not "slightly better".

**Counter-example:** three sources reported the same model at 0.912, 0.908, and 0.896 — a 1.6-point range, all with no significance test. Two matrix revisions ranked those three sources against each other. The ranking was reading source variance as method quality.

## Summary sentences versus the grid

Papers summarise themselves favourably, sometimes by accident. The grid is authoritative.

**Procedure**

1. Take the summary sentence and write down what it claims numerically ("consistently outperforms", "5–10% improvement").
2. Go to the table and count the cells that support it.
3. Record both.

| Summary says | Grid shows | Cell value |
|---|---|---|
| "consistently outperforms" | wins 2 of 8 tasks | grid: 2/8; note the summary discrepancy |
| "5–10% improvement" | 3% and 12%, neither endpoint in range | grid, plus the interval that is actually supported |
| "comparable to the state of the art" | loses on 3 of 4 | grid |

**Why record both:** a summary sentence is evidence about the authors' reading of their own work, which is itself interesting — and sometimes it is more conservative than the grid, which is a different finding and must not be filed as an overclaim. Erasing either one loses information.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "performance improved from 0.641 to 0.759" | AUPR vs ROC-AUC |
| mean compared against best-seed | order statistic read as a central one |
| two engines in one column | the column compares tools |
| re-implementation entered as the original | measures the toolkit gap |
| "slightly better" inside the band | noise read as signal |
| summary sentence used as the cell value | the grid disagrees and is authoritative |
| band borrowed from another paper's corpus | a band is local |

## Checklist

- [ ] Metric family matches across the column, and the family is named.
- [ ] Statistic stated per cell; unknown statistics are not ranked.
- [ ] Engine named per cell; no column mixes engines.
- [ ] Run provenance labelled (`as-reported` / `re-implemented` / `re-run`).
- [ ] Band estimated locally, or marked `unestimated`.
- [ ] Differences inside the band written as "within band".
- [ ] Summary sentences reconciled against the grid, both recorded.
