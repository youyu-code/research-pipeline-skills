# Case studies — twelve kernels

Cases where a careful reader reached a defensible conclusion that was wrong, and a specific test showed it.

All twelve are desensitized: no paper is identifiable, values are rounded, and in several the direction of the mistake has been changed so the case cannot be matched back to its source. **The transferable part is the test, not the story.**

The full failure modes with their mechanics live in the skill that owns them; these are the shapes worth recognising at a glance.

---

## 1 — The supplement that arrived after the conclusion

**Situation.** An item had one attachment, so the review concluded it had no supplementary material. Six weeks later a supplement appeared.
**Wrong conclusion.** "No SI exists."
**Test.** Ask what the statement is a statement *about*: the attachment list, at a moment. Write the date and the scope.
**Generalizes to.** Any absence claim about a mutable external record — attachments, repositories, database entries, web pages.

## 2 — The supplementary file with nothing in it

**Situation.** A three-page supplement, present and attached.
**Wrong conclusion.** "The SI supports the result."
**Test.** Ask for the table. Not the file — the table that carries the specific number.
**Generalizes to.** Every "we have data on that" claim. Presence of a container is not presence of the content.

## 3 — Two counts for one population

**Situation.** The same cohort reported as 9,740 and 9,625 at different pipeline stages.
**Wrong conclusion.** A typographical error; one number "corrected" into the other.
**Test.** Arithmetic closure: does the difference equal a quantity the paper itself states elsewhere? Here it equalled a declared excluded cluster exactly.
**Generalizes to.** Any staged count. Two correct numbers are frequently "fixed" into one wrong one.

## 4 — The legend that swapped two rows

**Situation.** A figure legend gave `38.7 ± 1.2`; the table gave `38.7 (1.8)` for the same model and a different dispersion for its neighbour.
**Wrong conclusion.** The legend is more precise because it has an error bar.
**Test.** Prefer the generated artefact over the re-typeset one. Table over legend, always.
**Generalizes to.** Any two representations of one number: the one produced by the analysis pipeline wins over the one typed by hand.

## 5 — The mean that lost and the median that won

**Situation.** One paper's mean score was worse than baseline; another's median, on the same benchmark and metric, was better.
**Wrong conclusion.** A trend, in whichever direction the reader encountered first.
**Test.** Name the statistic before comparing. If it is unstated, the number cannot be ranked.
**Generalizes to.** Every comparison of summary statistics — and every cell in a matrix.

## 6 — Two metrics, one model

**Situation.** 0.67 and 0.77 reported for the same model in the same paper.
**Wrong conclusion.** A capability gap of ten points.
**Test.** Read the metric names: AUPR and ROC-AUC answer different questions. The gap measured the metric.
**Generalizes to.** Any comparison where the metric name lives in a column header rather than in the cell.

## 7 — Seven combinations, six rows

**Situation.** A table advertised seven model–dataset combinations; two rows were identical to the last digit.
**Wrong conclusion.** "Won in five of seven."
**Test.** Count the denominator. Identical rows suggest a duplicated configuration, and the real count was six or fewer.
**Generalizes to.** Every rate, fraction, or majority claim. An uncounted denominator invalidates the sentence, not just the number.

## 8 — The re-implementation entered as the original

**Situation.** A 2018 model re-run on a 2024 toolkit, entered into a comparison as that model's score.
**Wrong conclusion.** A large improvement over the original method.
**Test.** Ask who ran it, on what, and when. Label `re-implemented` or `re-run`; never `as-reported`.
**Generalizes to.** Every benchmark table that spans more than a couple of years of tooling.

## 9 — Twelve reversals that were seven

**Situation.** A review counted twelve claims as "reversed" by later evidence.
**Wrong conclusion.** A reversal rate well above the field's, reported as a finding — the gap was the definition, not the evidence.
**Test.** Define the tiers before counting: full flip, falls inside the noise band, narrowed, not reversed at all. Recount.
**Generalizes to.** Any count of a qualitative category. The count is a function of the definition, and the definition is usually written after the count.

## 10 — "Consistently outperforms", two of eight

**Situation.** A summary sentence claimed consistent improvement; the grid showed two wins, four ties, two losses.
**Wrong conclusion.** Consistent improvement, because the sentence said so.
**Test.** Reconcile the sentence against the grid, cell by cell. Record both; the grid is the value.
**Generalizes to.** Every abstract. The abstract is a claim about the paper's own reading, and it is checkable.

## 11 — The preprint DOI on a camera-ready

**Situation.** An arXiv DOI cited for numbers taken from a conference camera-ready PDF.
**Wrong conclusion.** The citation resolves, so the numbers are sourced.
**Test.** Version identity by three criteria — DOI, running head with volume/pages, pagination. Cite the document the numbers came from.
**Generalizes to.** Any work with more than one public version, which is now most work.

## 12 — The paper that understated itself

**Situation.** A body sentence said a baseline was "generally exceeded"; the supplement showed it winning in all five subgroups.
**Wrong conclusion.** An overclaim, filed with the exaggerations.
**Test.** State the direction of the gap: body weaker than the data, or body stronger. Only the second is an overclaim.
**Generalizes to.** Every audit that collects "mismatches". A conservative mismatch and an inflationary one are opposite findings, and merging them inverts one of them.

---

## How to use these

| If you are | Read |
|---|---|
| building a card | 1, 2, 3, 4, 11 |
| building a matrix | 5, 6, 7, 8, 10 |
| auditing a claim | 3, 9, 10, 12 |
| writing a proposal | 3, 7, 9 — the three that turn a number into a sentence nobody can defend |

A case you cannot map to a test you could run is a story. The test column is the only part worth memorising.
