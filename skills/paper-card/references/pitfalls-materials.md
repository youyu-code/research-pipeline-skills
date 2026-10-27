# Material pitfalls — supplementary material, version identity, metadata

Every question about supplementary material is really **three** questions, and they are asked in this order:

| # | Question | Answer shape | Where it lives |
|---|---|---|---|
| 1 | What material exists? | a state, time-stamped | card header, `si-state` |
| 2 | Is it the same version as the claim? | an identity judgement | card header, version fields |
| 3 | Does it contain *the specific number*? | a locator, or a gap | card body, provenance + to-be-filled |

Collapsing them is the root cause of nine of the ten pitfalls below. "The paper has an SI" answers question 1 and says nothing about 3; "the number is not in the SI" answers 3 and says nothing about 1.

---

## 1. What exists

### 01 — One attachment proves nothing about the rest

**Smell** An attachment query returns exactly one file, so the paper "has no SI".
**Do** Write the observation with its date and its scope: **as of `YYYY-MM-DD`, this item has no supplementary attachment.** Re-query on every review. Never carry a previous conclusion forward.
**Counter-example** *"Checked — no SI."* In one corpus this conclusion was reversed four separate occasions (papers that later gained attachments), and one paper was reversed a second time on the same day. None of the earlier judgements were dishonest; all of them were stated as permanent facts when they were observations.
**Where** `schema.md` §4, `si-state: none-as-of:YYYY-MM-DD`.

### 02 — "One attachment" also cannot prove "no SI declared"

**Smell** You checked the attachment list, concluded "no SI", and never checked whether the text announces one.
**Do** Ask two separate questions: *how many attachments* and *does the text declare supplementary material*. An item can be `declared-but-absent` — and that is a different fact from `none`.
**Counter-example** Three items moved from `none` to `declared-but-absent` as soon as the sentence-level check was added. The attachment count had been correct the whole time; the conclusion drawn from it was not.

### 03 — Non-PDF files count

**Smell** The attachment is not a PDF, so it gets skipped in the count; or the item is called "no SI" while fifteen spreadsheets sit next to it.
**Do** Judge material completeness by **content**, not by file format or file count. Route `.xlsx` / `.docx` through `scripts/office_tables.py`.
**Counter-example** Fifteen spreadsheets *were* the complete SI. Counting PDFs only produced "not attached" for a paper whose tables were all present.

### 04 — Inline extended data is not inline SI

**Smell** A long page range at the back of the body PDF, assumed to be supplementary material.
**Do** Before asserting "SI is inline", check for embedded files and look for an actual supplementary section heading. Extended-data figures, references, and figure legends bound at the back are **not** an SI.
**Counter-example** Thirty pages of extended-data figures plus references plus main-figure legends were recorded as "supplementary material inline". The material existed; the classification was wrong, and every downstream "the SI has X" inherited the error.

### 05 — "No appendix in the body" ≠ "no SI on record"

**Smell** One sentence covering both facts: "the paper has no appendix."
**Do** Keep the two statements separate: *body PDF contains no supplementary section* / *the record has no SI attached*. Either can be true while the other is false.
**Counter-example** A paper whose body carried no appendix and whose SI was a separate second attachment. The single sentence was wrong in the direction that loses material.

---

## 2. Is it the same version

### 06 — Preprint, camera-ready, published version

**Smell** The record is an arXiv entry; the attached PDF is a conference camera-ready without a DOI; the same item holds several files.
**Do** Apply the three version criteria in order — **DOI present / running head with venue and year / page numbering scheme**. If you cite the published version, verify *its* DOI separately. Never present a preprint DOI as the venue version's DOI.
**Counter-example** A card citing "the ICLR version, DOI 10.48550/arXiv.…". The DOI resolves to the preprint; the numbers came from the camera-ready. The citation and the number point at different documents.

### 07 — Metadata key one character short

**Smell** A lookup by key returns nothing, and the key was pasted from an index rather than a record.
**Do** Verify every key with one lookup before using it. Treat keys in any index or overview table as unverified by default.
**Counter-example** A key missing its final character, carried through a whole review round, producing "this item has no attachment" for an item that simply was not found.

---

## 3. Does it contain the number

### 08 — "Has SI" ≠ "SI contains the table you need"

**Smell** Question 1 answered yes, so the claim is treated as supported.
**Do** Ask about the **table**, not the attachment: *is the table that carries this claim present?* A three-page SI can be entirely methodological.
**Counter-example** A three-page SI that argued the method and contained no result table at all. Every "the SI confirms it" statement about that paper was unsupported, while being literally true about the file's existence.

### 09 — "SI is complete" ≠ "the number is verifiable"

**Smell** All supplementary tables located, so the result is treated as citable.
**Do** The only question that licenses citing a number is: **which file, which sheet, which cell.** If you cannot answer at that resolution, the number goes into the to-be-filled section.
**Counter-example** A paper with fifteen supplementary tables but no summary table for the headline metric; another with a complete SI whose figure had no printed values. Both had "complete material" and neither had a citable number.

### 10 — Completeness reveals contradictions, it does not close them

**Smell** The tables arrived, so the review moves on.
**Do** Reconcile the summary sentence against the cell-by-cell data **after** the tables arrive. New material creates new inconsistencies; it does not retire old ones.
**Counter-example** A paper that looked clean until its SI landed, at which point the denominators, counting units, and category axes all turned out to be unstated or non-reproducible. "Material complete" was recorded before the reconciliation, and the record never caught up.

---

## Recording the three answers

```yaml
si-state: attached | inline-in-body | none-as-of:YYYY-MM-DD
si-contains:
  needed: "<the table or figure the claim requires>"
  found: yes | partial | no
  locator: "<file> › <sheet/table> › <row/col>"
version:
  identity: preprint | camera-ready | published
  criteria: [doi, running-head, pagination]   # which of the three you checked
  doi-verified: yes | no
```

Two rules for this block:

- **`si-contains` never inherits from `si-state`.** A `yes` in one and an `attached` in the other are independent facts.
- **A missing capability is `unknown`, never `none`.** If the tooling cannot list attachments, the state is not "no attachment" — it is "not observable, here is the probe I ran". See `zotero-manual.md`.

## Checklist before leaving step 3

- [ ] State written with a date, if the state is absence.
- [ ] Declaration checked separately from attachment count.
- [ ] Non-PDF files counted as material.
- [ ] Inline claim verified by section heading, not by page count.
- [ ] Version identity settled by all three criteria that apply.
- [ ] Every cited number has a file-level locator, or a to-be-filled entry.
- [ ] Summary sentences reconciled against the cells after the material arrived.
