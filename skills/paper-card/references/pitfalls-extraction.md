# Extraction pitfalls — PDF to text, PDF to table

Seventeen failure modes. The first sixteen all produce **plausible output**, none of them crashes, and most are invisible if you read the extracted text first and the health report never. The seventeenth is the opposite kind: it produces no output at all, and the only thing standing between you and a blank card is whether the report admits it.

Instances here are described by shape, not by paper. The pattern is the transferable part; the paper it happened on is not.

## The one rule

> **A page with almost no text is not an empty page. It is a failed extraction.**

Everything below is a variation on that sentence.

## How to use this file

1. Run `scripts/pdf_text.py --mode layout`. Read `_health.json` **before** any page text.
2. If `verdict` is not `ok`, switch mode. Do not read, summarise, or quote yet. Exception: if it is `unreadable`, no mode will help — the file is damaged, so fetch it again.
3. For a table, go to `scripts/table_coords.py` (upright) or `scripts/rotated_table.py` (rotated). Both exit non-zero rather than emit a silently broken grid.
4. Log every switch in the card's extraction log. A reader downstream must be able to tell a text-layer number from an OCR-read one.

---

## A. The text layer lies

### 01 — A whole run can "succeed" with no text

**Smell** Total character count in the low thousands, which reads like success; per-page counts in single digits on almost every page.
**Do** Judge per page, never in aggregate. Switch to `--mode text` (PyMuPDF).
**Counter-example** *"The total is non-zero, so extraction worked."* A full-length paper returned roughly one page's worth of characters spread across every page. The number that mattered was the per-page minimum.
**Where** `pdf_text.py --mode layout|text`, `_health.json` → `verdict: layout-failed`, exit 3.

### 02 — Digits replaced by glyph names

**Smell** Tokens like `/one.onum`, `/zero.tf`, `/five` inside what should be numeric text; a value that reads as a word.
**Do** Treat the text layer as unusable for that region. Re-extract with PyMuPDF. If the tokens survive, render and transcribe.
**Counter-example** Reading `/one.onum` as the word "one" and carrying it into the card as a value of 1.
**Where** grep `/one` `/zero` `/two` and `.onum` `.tf` over the output before reading.

### 03 — Math symbols collapse to glyph IDs

**Smell** `/uni2113`, `/uni2223`, other `/uniXXXX` runs, concentrated in formulas.
**Do** Route formula-bearing pages through PyMuPDF; assert the `/uni` count in the output is zero.
**Counter-example** *"The paper never defines the symbol."* It defined it; the glyph was lost in extraction. Reading that as an omission is a fabricated defect.

### 04 — Partially parseable encoding

**Smell** Warning `... is not required to fully parse the encoding`; exactly one character missing (a sign, a Greek letter) shown as `0:89560:002`.
**Do** Reconstruct the single missing glyph in place, keep every surrounding digit.
**Counter-example** Declaring "numbers unusable" because one `±` was missing. One lost symbol is a transcription note; a lost digit is a different problem.

---

## B. Two editions of the same paper

### 05 — Both versions defective, in different ways

**Smell** Version A truncates sentence tails; version B concatenates words (`Byanalyzingthe`); neither is clean alone.
**Do** Keep both. Read A for sentence order, patch fields from B. **A number lands only if both versions agree on it.**
**Counter-example** Preferring B's cleaner-looking token for a value that A reports differently. The cleaner version is not the more correct one; it is the more confident one.

---

## C. Geometry

### 06 — Rotated page (90°)

**Smell** Text arrives as scattered words; `--mode words` is no better; line order is arbitrary. The page looks normal in a viewer.
**Do** Detect rotation by line direction (`line['dir'] == (0, -1)`). Rebuild: cluster x into columns, walk y descending within a row. Then render at 200 dpi and confirm the header and column order visually — **coordinate rebuild and visual check are two separate confirmations, and both are required**.
**Counter-example** *"That table is corrupt in the PDF."* It was upright-but-rotated, and fully recoverable.
**Where** `rotated_table.py --page --col-tol --row-tol --order`. Exit 3 means no rotated lines were found — the table is ordinary, use `table_coords.py`.

### 07 — Two tables side by side, merged by row

**Smell** Extracted rows jump between two unrelated value sets; row count is about the sum of two tables.
**Do** Bring in a second source that preserves table structure, and require cell-by-cell agreement before any value lands.
**Counter-example** Rebuilding one merged table out of two six-row tables. Every value is real, the table is fiction.

### 08 — Wide table collapsed into uneven spaces

**Smell** Eight columns become one space-padded string; column boundaries sit at irregular widths.
**Do** Coordinate rebuild (`words` + row/column clustering), or render the whole table and read it visually. Confirm the column count before reading any cell.
**Counter-example** Splitting on runs of two or more spaces and trusting the result. The widths are unequal, so the split is silently wrong in a way that still looks like a table.
**Where** `table_coords.py --row-tol --col-gap`. Exit 4 = the grid was inconsistent, under-split, or over-split; the output was withheld on purpose.

### 09 — Header row shifted by one column

**Smell** Header has a different cell count from the body; two adjacent headers are identical (`LR` over `LR`) while their value magnitudes differ by an order of magnitude.
**Do** Restore by magnitude and in-table semantics, then write the restoration basis into the card.
**Counter-example** Accepting `LR / LR` literally when the table only makes sense as `P@L / P@L/5`. The literal reading is self-contradictory, which is the signal.

### 10 — Body text crosses the table, cutting the header

**Smell** A prose line sits between two header lines; header cells are split across the interruption.
**Do** Restore column correspondence from value semantics, then verify with a column-sum self-check.
**Counter-example** Treating the intruding paragraph as a header cell and shifting every column by one.

---

## D. Layout noise

### 11 — Multi-column bleed

**Smell** Lines from the right column interleave with the left; caption fragments like "See next page".
**Do** Assign paragraphs by page-top heading plus semantics; merge split captions before quoting.
**Counter-example** Reading a two-column paper as one column and reporting a sentence that never existed in that order.

### 12 — Figure text swamps the body

**Smell** Hundreds of short tokens (labels inside a figure) mixed with prose; no table on the page.
**Do** Filter by line length into a `_prose.txt`, keep figure text in a separate file.
**Counter-example** Quoting a label from inside a figure as if it were a claim in the text.

### 13 — "Rotated text discovered" is usually noise

**Smell** pypdf warns `Rotated text discovered. Output will be incomplete`.
**Do** Locate the affected pages. If only bitmaps and axis labels are affected while the table's text layer is complete, keep the path and record the warning.
**Counter-example** Switching pipelines on every occurrence. The warning fires on rotated axis labels, which are not text you need.

---

## E. Emphasis and pixels

### 14 — Bold does not reach the text layer

**Smell** You need emphasis to know which row is "ours" or "best"; the extracted text carries none.
**Do** Render the page, read it visually, and mark the field `visual confirmation`.
**Counter-example** Inferring the best row from its position in the table.

### 15 — No Excel library in the environment

**Smell** The supplementary material is `.xlsx` / `.docx`, and `openpyxl` / `python-docx` are absent.
**Do** `scripts/office_tables.py` — standard library only (`zipfile` + `ElementTree`), CSV intermediate you can read line by line.
**Counter-example** Declaring the SI unreadable or unattached when fifteen spreadsheets *were* the SI. See `pitfalls-materials.md` §03.

### 16 — Printed digits versus axis estimation

**Smell** A figure carries values, but `get_text` and `words` return zero tokens in that region; the figure is a bitmap.
**Do** Render the panel at 450–1200 dpi, transcribe the digits character by character, mark provenance `figure-transcription`, and keep the rendered image as evidence.
**Counter-example** `≈0.72` read off a bar height. Even with an axis, a gridline, and a label on the bar, that is estimation, not transcription. The card must not contain it.

---

## F. The file itself

### 17 — A truncated download is not an empty paper

**Smell** A reader refuses the file (`Stream has ended unexpectedly`, `EOF marker not found`) or, worse, opens it and reports **zero pages** without raising — and a run that extracted nothing is scored `verdict: ok`, because zero suspect pages out of zero pages is a perfect ratio.
**Do** Treat a zero-page read as a failed extraction, exactly like a page under ten characters: `pdf_text.py` now writes `verdict: unreadable` with the reader's own error and exits 3. Then re-fetch the file. PyMuPDF can repair some structural damage, so `--mode text` is still worth one try before declaring the file unusable.
**Counter-example** *"The extractor returned no error, so the PDF is probably blank."* A 10.3 MB paper cut off at 8.4 MB had lost its cross-reference table; the tolerant reader returned a document with no pages and no exception. A blank card would have been written from it.
**Where** `pdf_text.py` → `_health.json` `verdict: unreadable`, exit 3; the `errors` list carries the reader's message. Checksum the file against the source's stated size before blaming the extractor.

---

## Which tool for which symptom

| Symptom | Tool | Refusal signal |
|---|---|---|
| whole run, near-zero text per page | `pdf_text.py --mode text` | `_health.json` verdict ≠ `ok`, exit 3 |
| reader refuses the file, or reports 0 pages | re-fetch; one `--mode text` try first | `_health.json` verdict `unreadable`, exit 3 |
| `/one.onum`, `/uni2113` | `pdf_text.py --mode text`, then render | `/uni` or `.onum` still present |
| upright table, columns misaligned | `table_coords.py` | exit 4 (inconsistent / under-split / over-split) |
| rotated table | `rotated_table.py` | exit 3 (no rotated lines) |
| `.xlsx` / `.docx` tables | `office_tables.py` | manifest lists unreadable parts |
| digits inside a bitmap | render + transcribe by hand | no digits readable at 450 dpi → record as unavailable |

## What to write into the extraction log

For every page that needed a switch:

- the mode used, and the one-line reason it was switched to
- which pages failed the health check, and their character counts
- which tables were rebuilt by coordinate, which by rotation, which transcribed from a rendered image
- warnings kept on purpose, and why they were judged harmless

A card whose extraction log says only "extracted with PyMuPDF" has thrown away the part a later reader needs.
