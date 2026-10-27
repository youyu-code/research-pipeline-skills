# Counter-examples — rulings that look right

Ten rulings that a careful auditor can produce, each defensible in the moment and wrong in the light.

Read this before signing a verdict. Every item below has passed an internal review at least once.

---

## 1 — `undecidable` because the authors never discussed it

**Looks right.** The paper states a general claim and says nothing about the boundary case. The authors did not discuss it, so the material cannot settle it.
**Why wrong.** Silence is not a second reading. If the paper's own data shows the claim failing in that case, the claim is contradicted — a defect, not an ambiguity.
**The tell.** Your justification contains "they do not say whether".
**Correct.** Test 2: search the paper's own numbers. If they refute, `unsupported` + `defect-self-data`.

## 2 — `supported` because the number is in the paper

**Looks right.** The claimed value exists, in a table, with a locator.
**Why wrong.** The number's existence says nothing about whether it supports the claim's *scope*. A value measured on the tuning set does not support a claim about held-out performance.
**The tell.** You checked the value and never wrote down the claim's condition.
**Correct.** Restate the claim's scope, then check the number's condition against it. Mismatch → `unsupported`, with the condition quoted.

## 3 — Ambiguous because another number allows the reading

**Looks right.** The sentence could mean X. The table also contains a value consistent with X. Two readings are available.
**Why wrong.** That is a numeric anchor. Only a sentence can establish that the authors meant a reading; otherwise every well-reported paper becomes immune to the ambiguity test.
**The tell.** Your second reading is supported by a table cell, not a quotation.
**Correct.** Ambiguity needs two textual anchors. One text plus one number is a defect-self-data candidate, or nothing.

## 4 — `unsupported` because the number could not be found

**Looks right.** The claim needs a value; you searched the body and the supplement; it is not there.
**Why wrong.** A search failure is a fact about the search. The claim is not refuted by its evidence being absent — it becomes `undecidable`, with the missing artefact named.
**The tell.** Your basis says "no data found" rather than "data shows otherwise".
**Correct.** `undecidable`, with the artefact named and the search scope recorded. If the artefact should exist, that gap is itself a register entry.

## 5 — Ruling on a paraphrase

**Looks right.** The claim is clearly what the paper means; the exact sentence is a formality.
**Why wrong.** Every audit that produced a surprising verdict and was later withdrawn had drifted from the sentence to a paraphrase of it. The paraphrase moves toward what is testable.
**The tell.** Your claim line has no quotation marks.
**Correct.** No anchor → no verdict. Quote the sentence, then decide whether the quoted claim is worth auditing.

## 6 — Defect, where the two statements are from two versions

**Looks right.** Two numbers for one quantity, both in the document set, irreconcilable.
**Why wrong.** If one is from a preprint and the other from a camera-ready, both are correct and nothing is contradicted. This is the `version` tag, and it dissolves on inspection — after costing a review round.
**The tell.** The two locators have different page-numbering schemes.
**Correct.** Establish version identity first (DOI / running head / pagination) for every document in the set, before comparing anything across them.

## 7 — Ambiguity, where the paper follows one field convention

**Looks right.** Two communities use the term differently, so the sentence has two readings.
**Why wrong.** If the paper uses one convention consistently, the paper is unambiguous. The ambiguity lives in the reader's background, not in the text.
**The tell.** Your two readings come from two textbooks, not two sentences.
**Correct.** No ambiguity finding. Optionally note the convention the paper follows — that is a card-level terminology note, not an audit verdict.

## 8 — T1 asserted with no band field

**Looks right.** A later result puts a different method ahead. The ordering reversed, so the claim goes in the count as a rank flip.
**Why wrong.** The tier is not the question here — the *citation* is. Without a `band` annotation the reader cannot tell a settled reversal from one whose margin is smaller than the measurement's own disagreement, and both get quoted with the same confidence. The reversal is real; the warrant for relying on it is missing.
**The tell.** Your row has `tier: T1` and nothing on the `band` line.
**Correct.** Keep the tier, fill the annotation: `outside-band` (citable as settled), `in-band` (recorded, not relied on), or `unestimated` (a claim about the reporting, not the field). A missing band does not demote T1 to T2 — a strength collapse is a different event, and conflating the two inflates one while hiding the other.

## 9 — A conservative mismatch filed as an overclaim

**Looks right.** The body sentence is weaker than the data, so the paper misrepresents its own result. Mismatch found, filed with the exaggerations.
**Why wrong.** The direction is inverted. A body that understates its result is not exaggerating; merging it with overclaims inverts the finding, and a reviewer who checks will find the inversion before the claim.
**The tell.** Your summary says "the paper overstates" while your quote shows it understating.
**Correct.** Record the direction explicitly: body weaker than data, or body stronger. Only the second is an overclaim.

## 10 — Ruling on "all X" from one instance

**Looks right.** The claim says all cases behave a certain way; one case clearly does. Claim supported.
**Why wrong.** A universal claim is refuted by one instance and supported by none. One confirming case supports "some", which is a different claim.
**The tell.** The claim contains "all", "every", "consistently", and your evidence is a single row.
**Correct.** Either narrow the claim to what one case supports (and say so), or mark `undecidable` for the universal, naming the coverage that would settle it.

---

## Pre-flight check

Before a verdict leaves the file:

- [ ] The claim line contains a quotation and a section number.
- [ ] The basis names a test, and that test can produce that verdict.
- [ ] Every "could not find" is `undecidable`, never `unsupported`.
- [ ] Every ambiguity has two quotations.
- [ ] Version identity checked before any cross-document comparison.
- [ ] Direction of any mismatch stated in words.
- [ ] Universal claims checked against their quantifier, not against an example.
- [ ] The `would-flip-if` line is filled.

Eight boxes, two minutes. The alternative is a verdict that survives until someone reads the paper.
