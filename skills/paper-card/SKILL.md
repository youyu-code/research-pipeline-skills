---
name: paper-card
description: >-
  Build one structured paper card from one paper: extract full text from a PDF,
  classify supplementary-material status, transcribe tables with coordinate-based
  verification, and record which numbers are citable versus which are not. Use when
  the task is to turn one paper into one card. Input: a paper — a single PDF, a
  Zotero attachment, or a folder of PDFs. Output: one card following the card schema,
  carrying a source trail, an extraction-failure log, and a to-be-filled section.
  Folder-driven by default: point it at a directory and it processes every PDF
  inside; a Zotero MCP server only accelerates lookup and is never a prerequisite.
  It does not compare papers across a corpus (use synthesis-matrix), and it does not
  adjudicate whether a claim is true or exaggerated (use evidence-audit).
---

# paper-card

A card is a **terminal record of what one paper says and what can be cited from it**. It is not a summary, not a review, and not a verdict. Everything downstream (matrix, proposal) reads cards instead of PDFs, so a card's job is to make that substitution safe.

## Five steps

**1 — Pair.** Decide which PDF is the main text and which are supplementary, before opening anything. If the directory holds more than one PDF per paper, run the pairing heuristic and **print the pairing list**. Any pair below the confidence bar is a stop-and-ask, never a silent guess. → `references/zotero-manual.md`

**2 — Extract.** Run `scripts/pdf_text.py` in `layout` mode first. Read `_health.json` before reading text: a page under ten characters is not an empty page, it is a failed extraction. Switch mode, do not conclude. One verdict is not a mode problem: `unreadable` means the file itself is damaged (a download cut off mid-stream is the usual cause), so re-fetch it instead of cycling modes. Tables go through `scripts/table_coords.py` (upright) or `scripts/rotated_table.py` (rotated); both refuse silently-broken output by exit code. → `references/pitfalls-extraction.md`

**3 — Classify supplementary material.** Three states only, each with a date: *independent SI attached* / *inline in the body PDF* / *none as of YYYY-MM-DD*. That last state is a time-stamped observation, never a permanent fact. Then answer the second, separate question: does the material contain **the specific table** the claim needs? → `references/pitfalls-materials.md`

**4 — Fill the card.** Follow `references/schema.md` v1 exactly — field names are a contract with `synthesis-matrix`. Every number carries its provenance and its citation form. A number you cannot cite goes in the to-be-filled section with the reason, not in the results section with a hedge. → `references/card-template.md`, `references/citation-rules.md`

**5 — Trace, then check.** Write the extraction log: which mode, which pages failed, which tables were rebuilt by coordinate, which figures were transcribed from print. A later reader must be able to tell an OCR-read number from a text-layer number. Then run `scripts/check_card.py` on the card — exit 0 or the card is not finished. → `references/card-template.md`

## Hard rules

- **A folder run never stops on a broken page; it stops on a broken pairing.** Page-level failures are logged and continued; a main/SI mismatch contaminates every number downstream.
- **`children == 1` proves nothing about the paper's claims.** It is a fact about the attachment list at query time. Counter-example: a paper declaring three supplementary tables with one PDF attachment — the tables are absent, not the declaration. → `references/pitfalls-materials.md`
- **"SI is here" ≠ "the number is here".** Counter-example: a 3-page SI that argues the method and contains zero result tables; the number lives in the formal version's Table 2.
- **Never estimate a value from a plot axis.** Printed digits inside a figure may be transcribed (≥450 dpi, rendered image kept as evidence); positions on an axis may not. Counter-example: "≈0.72" read off a bar height is not a transcription, even if the bar carries a label.
- **Do not rule on whether the paper is right.** "Author says X, Table 3 says Y" is in scope; deciding which is true belongs to `evidence-audit`.

## Routing

| Task | Go to |
|---|---|
| extract text / rebuild a table / read .xlsx-.docx tables | `scripts/` (5 files) + `pitfalls-extraction.md` |
| check a finished card against the schema | `scripts/check_card.py <card.md>` |
| see a filled card | `assets/samples/demo2026_pipeline-selftest.md` |
| decide SI status or version identity | `pitfalls-materials.md` |
| decide how to write a number into the card | `citation-rules.md` |
| decide what a card field means | `schema.md` |
| no MCP, no CLI, folder of loose PDFs | `zotero-manual.md` |
| compare this card with others | hand off to `synthesis-matrix` |
| decide whether a claim holds | hand off to `evidence-audit` |

## Output contract

`cards/<firstauthor><year>_<shorttitle>.md`, schema `v1`, six mandatory sections: header (identity + version + SI state), body (§0–§8, with provenance on every number), to-be-filled (with reasons), production notes (text / hand work / identity), extraction log, and a self-check line (pages read / pages failed / tables rebuilt / transcriptions). `check_card.py` enforces all six.
