# Card template

Copy this file, fill it top to bottom, delete nothing. An empty field is a claim too — if you cannot fill one, write why, in the field.

The skeleton follows `schema.md` v1 exactly; field names are a contract with `synthesis-matrix` and must not be renamed locally. What this file adds is **what to write in each slot**, and the three production notes that no schema can enforce.

---

## Skeleton

```markdown
---
id: firstauthor0000_shorttitle
title: <as printed on the cover>
venue: <journal or conference> <year>
version: preprint | camera-ready | formal
version-evidence: <DOI | "vol X, pp Y–Z" | "accepted, no DOI">  |  none-as-of:YYYY-MM-DD
topic: <your corpus bucket, stable across cards>
pages: body=<n>p; si=<n>p
si-state: independent | inline | partial | none-as-of:YYYY-MM-DD
si-note: <only when partial or none-as-of: name the missing artefact>
si-contains: <full: Tables S1–S9 | argument-only: no result table | inline-appendix: Tables A1–A5 | n/a — code repo only>
source-trail:
  - kind: pdf-attachment | local-file | folder
    ref: <attachment key / path / folder>
    pages: <n>
---

# <title>

## §0 Terminology
<only terms whose meaning differs across the corpus; metric definitions this paper uses>

## §1 One-liner
<one sentence: what this paper does. No evaluation.>

## §2 Question
<the question, in the paper's own framing>

## §3 Prior work
<what existed before, as the paper states it — mark unverified claims [as-claimed]>

## §4 Method
<core mechanism + hyperparameters that matter for reproduction; every number carries a locator>

## §5 Results
| value | unit | statistic | condition | locator | source | note |
|---|---|---|---|---|---|---|
| 0.000 | <unit> | mean \| median \| best-seed | <dataset/split/engine> | p.0 Table 0 row "" col "" | text-layer \| table-coord \| figure-transcription \| derived | <required for figure-transcription and derived> |

<qualitative conclusions are allowed here but must be prefixed `[qualitative]`>

## §6 Limitations
### Author-stated
<verbatim, including their own negative results>
### Reader-observed
<what you noticed and they did not — mark the locator that shows it>

## §7 Transferable
<what another project could reuse; specific enough to act on>

## §8 Relations
<edges to other cards: cites → / cited-by ← / shared-baseline ~ / conflicts ≠, each with the direction>

## To be filled

| item | reason | blocker | next-action |
|---|---|---|---|
| <table/§/figure> | not-in-paper \| not-in-si \| si-missing \| figure-only \| code-repo-only \| extraction-failed | blocks-citation \| blocks-reproduction \| cosmetic | <who closes it> |

## Production notes

1. **Text** — <extractor and mode; pages that failed; what was switched and why>
2. **Hand work** — <tables rebuilt by coordinate / by rotation; transcriptions and their dpi; what still lacks a visual confirmation>
3. **Identity** — <which version criterion settled it; whether the SI belongs to the same version>

## Extraction log

```
mode: layout:1-6, text:7-39
failed-pages: [7, 8, 39]
rebuilt-tables: [{page: 7, method: coord, thresholds: {row-tol: 3.0, col-gap: 12.0}}]
transcriptions: [{page: 12, dpi: 600, panel: "C"}]
dual-version: yes — Table 2 values required agreement in both extractors
```

self-check: pages-read=39/39 · failed=3 · tables-rebuilt=1 · transcriptions=1 · contradictions-registered=2
```

---

## Section by section

**`§0`** is populated once per topic and extended by deltas. If you find yourself redefining "AUROC" in every card, the definition belongs in the first card and nowhere else.

**`§1` / `§2`** carry no judgement. The moment a one-liner contains "convincingly", the card has started reviewing instead of recording.

**`§3`** exists to stop a reader from thinking the paper invented a field. `[as-claimed]` marks the parts you did not verify — which is most of it, and that is fine as long as it is marked.

**`§4`** is where reproduction lives or dies. A hyperparameter without a locator is a rumour; if the paper gives none, that is a to-be-filled entry with reason `not-in-paper`.

**`§5`** is the only section that may hold numbers, and every row has a locator. Prose conclusions sit in the same section but prefixed `[qualitative]` — that prefix is what stops a downstream matrix from treating a sentence as a value.

**`§6`** keeps the two voices apart. Author-stated limitations are evidence about the paper; reader-observed limitations are your finding. Merging them makes it impossible to tell whether the paper was honest.

**`§7`** must be actionable. "Uses contrastive learning" is not transferable; "the negative-sampling ratio schedule in §4.2 is reusable when positives are <1%" is.

**`§8`** carries direction. `A → B` (A cites B) and `A ~ B` (shared baseline) are different edges, and a matrix built from undirected edges will produce a community structure that does not exist.

---

## The three production notes (mandatory)

These are prose, one or two sentences each, and they answer the question a later reader actually has: *how much should I trust this card?*

**1 — Text.** Which extractor, which mode, which pages failed, what you switched to and why. If one sentence could be "extracted with PyMuPDF", the note is not doing its job — say what was wrong with the first attempt.

**2 — Hand work.** Which tables were rebuilt by coordinates (and with which thresholds), which were transcribed from a rendered image (and at what dpi), and — the part usually omitted — **which hand-built table has still not been confirmed visually**. An unconfirmed rebuild is `table-coord` with a note, not `text-layer`.

**3 — Identity.** Which of the three version criteria settled the version, and whether the SI is the same version as the body. A camera-ready body with a preprint SI is a real combination; the note is the only place it gets recorded.

A card can be schema-perfect and useless because these three notes say nothing. The schema validates fields, not honesty.

---

## Before you call the card done

```
python scripts/check_card.py cards/<id>.md
```

Exit 3 prints every violation with the field name: missing sections, an enum outside its set, a value with no locator, a `figure-transcription` row with no note, an estimated value carrying `≈`, or a self-check line whose counts disagree with the extraction log.

The checker does **not** check whether the notes are true — no tool can. It checks that you left the fields where a later reader will look.

---

## Filling rules that come up on nearly every card

| Situation | What to write |
|---|---|
| number appears in body and SI, different values | body as primary, SI in parentheses with its locator (`citation-rules.md` §01) |
| number appears only in a figure legend | cite the legend, mark it; if a table also has it, the table wins (`§02`) |
| number printed inside a bitmap | `figure-transcription`, note the dpi, keep the image (`pitfalls-extraction.md` §16) |
| number must be computed by you | `derived`, show the arithmetic in the note |
| no number anywhere for a claim the paper makes | to-be-filled, reason `not-in-paper`, blocker `blocks-citation` |
| SI exists but lacks the table | to-be-filled, reason `not-in-si`, and `si-contains: argument-only` in the header |
| two counting stages, difference unexplained | record both, record the failed closure test (`citation-rules.md` §05) |

## What must never appear in a card

- A value read off an axis position. `≈` in `§5` is a defect, not a hedge.
- A verdict on whether the paper is right. That is `evidence-audit`'s output, and it reads the card as input.
- A cross-paper comparison. Conditions may be recorded here; the comparison belongs to `synthesis-matrix`.
- An empty required field with no reason attached.
