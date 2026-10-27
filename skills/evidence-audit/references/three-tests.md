# The three tests

In order. Each test can end the audit, and a later test never overrides an earlier one.

```
1 anchoring ──fail──▶ no verdict (the claim is a paraphrase)
     │
     pass
     ▼
2 counter-evidence ──found──▶ unsupported (quote it)
     │
     none found
     ▼
3 availability ──cannot distinguish──▶ undecidable (name the artefact)
     │
     can distinguish
     ▼
supported
```

---

## Test 1 — Anchoring

**Question:** which sentence in the paper states this claim?

| Counts as an anchor | Does not |
|---|---|
| a quoted sentence with a section number | your summary of it |
| a table caption that states the claim in words | a number in a table |
| an abstract sentence **plus** the body sentence it repeats | the abstract alone, when the body says less |

**Rule:** the anchor is quoted verbatim, with its location, in the output. An audit that begins "the authors claim that performance improves" has not anchored anything.

**Why the abstract alone is not enough.** Abstracts are written under length pressure and routinely state a wider claim than the body supports. Auditing the abstract against the body is a legitimate finding — but then the finding is "the abstract overstates the body", and the anchor is the abstract sentence, not the body's.

**Failure mode:** no anchor → **no verdict**. Not `undecidable` — *no verdict*. The distinction matters: `undecidable` says the material cannot settle it; no-verdict says the claim was never located.

**Counter-example:** a claim was audited as `undecidable` for two rounds. It turned out the sentence being audited was a reviewer's paraphrase of a sentence that did support the claim. The audit had been running on a claim nobody made.

## Test 2 — Counter-evidence

**Question:** does the paper's own material refute the claim?

Search order, cheapest first:

1. the claim's own numbers, in the table it cites;
2. the neighbouring paragraph, where qualifications usually live;
3. the limitations section, where the authors often state the refutation themselves;
4. the supplement, where per-item data can contradict a summary.

**Outcome:** `unsupported`, with the refuting quote and its location. Not "contradicted by another paper" — that is a matrix comparison. This test is internal to the claimed document.

**Counter-example:** a claim of "consistent improvement across benchmarks" was passed as `supported` on the strength of the abstract, while §5's own table showed two of eight benchmarks losing. The refutation was in the same document, one section away from the anchor.

## Test 3 — Availability

**Question:** could the material in hand distinguish the claim from its negation?

Three answers, and only three:

| Answer | Condition | Verdict |
|---|---|---|
| yes, and it favours the claim | the distinguishing observation exists and is quoted | `supported` |
| yes, and it opposes | covered by test 2 | `unsupported` |
| no | name the artefact that would | `undecidable` |

**The artefact must be nameable.** "More data" is not an artefact; "the per-class breakdown for Table 3, which is not in the body or the SI" is. An `undecidable` verdict whose missing artefact cannot be named is an admission that the claim was never understood.

---

## Two rules that decide most cases

### A numeric anchor is not an anchor

The tempting move: the claim is ambiguous, but the same table reports a second number that would support a second reading, so the claim gets a second reading.

**Why it is wrong:** if a second number in the same table licenses a second reading, then every paper that reports a complete table is immune from the ambiguity test — and the ambiguity category becomes reserved for papers that report *less*. The better a paper's reporting, the less auditable its claims. That is backwards.

**The rule:** ambiguity requires **two readings anchored in the paper's own text**. A number can support a reading; only a sentence can establish that the authors meant it.

**Counter-example:** a metric was reported as a mean in the table and described as a median in the text. The audit ruled "ambiguous, both readings available" because the table's dispersion column was consistent with either. The correct verdict was `defect-self-data`: the text and the table contradict each other, and the paper's own numbers cannot be both.

### "Not discussed" is not "not claimed"

The claim "the method generalises to unseen scaffolds" was stated in §5 and never discussed in the limitations section. An audit called it ambiguous — "the authors do not say whether they mean within-family or across-family".

**Why it is wrong:** the sentence is a factual statement with a scope. If the paper's own data shows it failing across families, the claim is contradicted — a defect. Silence in the limitations section does not create a second reading; it means the authors did not qualify a claim they made.

**The rule:** ambiguity requires **two readings that are both textually anchored**. Absence of discussion is not a second reading — it is an absence.

**Counter-example, in the other direction:** a term used in two clearly different senses in §2 and §5 (`accuracy` as per-cell in one, per-molecule in the other) — that is genuine ambiguity-term-overload, because both readings have a sentence.

---

## Which test decided it — always report

The output names the deciding test. Not for ceremony: a verdict of `undecidable` from test 1 does not exist (test 1 produces no verdict), and a verdict of `unsupported` from test 3 is a category error — test 3 cannot produce `unsupported`.

| Verdict | Can be produced by |
|---|---|
| no verdict | test 1 only |
| `unsupported` | test 2 only |
| `supported` | test 3 (after tests 1 and 2 passed) |
| `undecidable` | test 3 only |

A ruling whose stated basis violates this table is internally inconsistent, and that inconsistency is visible without knowing anything about the paper.

## Counter-examples, collected

| Written | Test violated |
|---|---|
| "the authors claim X" with no quote | 1 — no anchor |
| `undecidable` on a paraphrase | 1 — should be no verdict |
| `supported` from the abstract, body unread | 2 — counter-evidence not searched |
| `unsupported` because the number was not found | 3 — search failure is not refutation |
| `undecidable` with "more data needed" | 3 — artefact not named |
| ambiguity justified by a table value | rule A — numeric anchor |
| ambiguity justified by silence | rule B — absence is not a reading |

## Checklist

- [ ] Claim quoted with a section number.
- [ ] Counter-evidence searched in four places, not one.
- [ ] Any `undecidable` names the artefact that would settle it.
- [ ] Ambiguity has two *textual* anchors, not one text plus one number.
- [ ] The stated basis is a test that can produce that verdict.
