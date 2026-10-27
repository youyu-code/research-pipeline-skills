# Citation rules — how a number earns its place in a card

A card is read *instead of* the PDF by everything downstream. So the bar is not "is this number in the paper" but **"could a reader who only has this card defend the number to someone holding the PDF"**.

That test produces four requirements, and one of them is usually skipped.

## What every citable number carries

```
<value> <unit> — <statistic> — <condition> — <locator>
```

| Slot | Why | Failure if omitted |
|---|---|---|
| statistic | mean and median can point opposite ways | the reader reports the friendlier one |
| condition | which dataset / split / engine / seed | two incomparable numbers get compared |
| locator | file › table › column › row | nobody can re-check, so the number is folklore |
| provenance | `text-layer` / `table-coord` / `figure-transcription` / `derived` | an OCR-read value is indistinguishable from a clean one |

Sample shape — no real values, this is the format:

```
0.00 (median, n = 00 targets, engine A) [Table 2 › "engine A" column, row "ours"] — table-coord
```

Anything short of this belongs in the to-be-filled section with a reason, not in the results section with a hedge.

---

## 01 — Two values for the same metric: body wins, but the other one is not deleted

**Smell** The body reports one value for a metric; the SI reports another for the same metric, same dataset, same model.
**Do** Take the body value as primary, parenthesise the SI value, and name both locators. Never cite one alone as if the other did not exist.
**Counter-example** A correlation coefficient reported as 0.612 in the body and 0.607 in the SI. A card carrying only 0.607 is not wrong about the SI — it is wrong about the paper, because it hides a discrepancy the authors never addressed.
**Where** `schema.md` §3 provenance `note` field holds the second value and its locator.

## 02 — Never cite a figure legend for a number that also appears in a table

**Smell** A legend states `38.7 ± 1.2`; the table states `38.7 (1.8)` for the same row.
**Do** Cite the table. Legends are re-typeset from memory; tables are usually generated. If only the legend carries the value, cite the legend and mark it as such.
**Counter-example** A legend that had both the model row and the dispersion wrong: it paired one model's mean with another model's SD. Reading the legend gave a number that appears nowhere in the table — and looked more precise, because it had an error bar.

## 03 — Name the statistic, or do not cite it

**Smell** "−4.86" quoted without saying whether it is a mean or a median, for a metric where the two fall on opposite sides of a baseline.
**Do** Write the statistic into the citation. When a cleaner measurement exists elsewhere in the same paper, prefer the cleaner one and say why you switched.
**Counter-example** A docking score where the mean was worse than baseline and the median was better. One paper, one dataset, two defensible sentences pointing opposite ways — decided entirely by an unstated word.
**Where** `synthesis-matrix` inherits this: a matrix cell without its statistic is not comparable to anything.

## 04 — Whose number is it: the paper's, or a re-run's?

**Smell** A model from an older paper re-implemented with a current library version; the result presented as that paper's performance.
**Do** Record it as *"`<tool>` re-run at `<version>`, our configuration"*. Never as the original authors' result. The reverse also holds: a re-run that agrees is not an independent replication.
**Counter-example** A 2018 model re-run under a 2024 toolkit and entered into a comparison table as the 2018 paper's score. Every "-points improvement over the original" computed from that cell is measuring the toolkit, not the method.

## 05 — Arithmetic closure before "typo"

**Smell** Two counts for the same population at different stages of a pipeline: 9,740 then 9,625.
**Do** Test whether the difference closes against a quantity the paper itself states (an excluded cluster, a filtered set). If it closes, it is a staged count and both numbers are correct for their stage. If it does not close, record the gap and the failed test — that is a finding, not a typo.
**Counter-example** The 115-record difference was called a typo in review. It equalled a self-declared excluded cluster exactly. Two correct numbers were nearly "corrected" into one wrong one.
**Where** Record the arithmetic in the extraction log; the card should show the reconciliation, not just the final count.

## 06 — Check the denominator before any "most / majority" sentence

**Smell** Two rows in a comparison table are numerically identical to the last digit; a count of "N combinations" is stated but not enumerable.
**Do** Suspect a duplicated row first. If the denominator cannot be established, the card must not carry "most", "majority", "consistently", or any rate — only the individual values.
**Counter-example** A table advertising seven model–dataset combinations where two rows were byte-identical; the real denominator was six or fewer. Every "won in 5 of 7" sentence built on that table was built on a denominator nobody had counted.

## 07 — The gap has a direction, and it is not always flattering

**Smell** The body understates what the authors' own data shows.
**Do** Say which way the gap runs: *body weaker than the data* versus *body stronger than the data*. Both are recordable; only the second is an overclaim.
**Counter-example** A body sentence saying a baseline was "generally exceeded", while the SI showed that baseline winning in all five subgroups. This is a **conservative** mismatch. Filing it under "exaggeration" inverts the finding, and a reviewer who checks will find the inversion before they find the claim.

---

## Handing off: what is *not* a citation rule

A card decides how one number is written. It does not decide whether two papers' numbers can be compared. These four belong to `synthesis-matrix`, and pulling them into a card is how single-paper records start making cross-paper claims:

| Question | Belongs to |
|---|---|
| two sources differ by 1.6 points — is that a difference? | `synthesis-matrix` (noise band) |
| AUPR 0.641 vs ROC-AUC 0.759 — which model is better? | `synthesis-matrix` (metric family) |
| same table mixes two docking engines, 7–9 points apart | `synthesis-matrix` (engine band) |
| "consistently outperform" vs 2 of 8 wins on the grid | `synthesis-matrix` (summary-vs-grid reconciliation) |

The card's obligation in all four cases is only to **record the condition precisely enough** that the matrix can do its job: engine name, metric name, statistic, and source. Precision here is what makes the hand-off possible; the comparison itself stays out.

## Provenance classes, and what a reader may assume

| Class | Meaning | Reader may assume |
|---|---|---|
| `text-layer` | read directly from the PDF's text | the digits are the paper's digits |
| `table-coord` | rebuilt from word coordinates | the grid was verified; a cell could still be misassigned (note which) |
| `figure-transcription` | digits read from a rendered image | correct as transcribed; the image is kept as evidence |
| `derived` | you computed it (a difference, a rate, a mean of reported values) | the formula is in the note; it is *your* number, not the paper's |

`derived` is the one that gets abused. A rate you computed from two reported counts is not something the paper claims — say so in the note, in one clause.
