# Card schema — `v1`

> **Version:** v1 · 2026-10-26 · **Owner:** `paper-card` (this file is the single definition)
> **Consumer:** `synthesis-matrix` declares "consumes card schema v1" and does not restate fields.
>
> Changing a field name is a **breaking change**: bump to v2 and record the migration in the changelog at the bottom. Adding an optional field is not breaking; adding a required one is.

Field names are lowercase with hyphens. Every value that could be quoted carries provenance. A card that cannot fill a field writes the reason, never a placeholder.

---

## 1. Header (mandatory)

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | string | yes | `firstauthor<year>_<shorttitle>`, lowercase, ASCII. Must match the filename stem. |
| `title` | string | yes | As printed. If the running title differs from the cover title, use the cover title. |
| `venue` | string | yes | Journal / conference + year. |
| `version` | enum | yes | `preprint` \| `camera-ready` \| `formal`. Justify with one of three identifiers: DOI, running head with volume/pages, or an explicit "accepted" statement. |
| `version-evidence` | string | yes | The identifier you used. If none, write `none-as-of:YYYY-MM-DD`. |
| `topic` | string | yes | The caller's own bucket (e.g. `T1`). Free text, but stable within a library. |
| `pages` | string | yes | `body=<n>p; si=<n>p` or `body=<n>p` when no SI. When the SI is not paginated (spreadsheets, docx), write `si=<n> files (xlsx+docx)` — a file count is the honest unit there. |
| `si-state` | enum | yes | `independent` \| `inline` \| `partial` \| `none-as-of:YYYY-MM-DD`. `partial` means declared but incomplete — say what is missing in `si-note`. |
| `si-note` | string | cond. | Required when `si-state` is `partial` or `none-as-of`. Name the missing artefact, not the feeling. |
| `si-contains` | string | yes | What the supplementary **actually contains** for this card's claims. See §4 — this is a different question from `si-state`. |
| `source-trail` | list | yes | `[{kind: pdf-attachment\|local-file\|folder, ref: <id or path>, pages: n}]`, one entry per file actually opened. |

## 2. Body sections (mandatory, in this order)

| Section | Content rule |
|---|---|
| `§0 terminology` | Only terms whose meaning differs across the corpus, plus the metric definitions this paper uses. Populate once for the first card in a topic, then extend only with deltas. |
| `§1 one-liner` | One sentence: what this paper does. No evaluation. |
| `§2 question` | The question the paper poses, in its own framing. |
| `§3 prior-work` | What existed before, as the paper states it. Mark `[as-claimed]` when unverified. |
| `§4 method` | Core mechanism + hyperparameters that matter for reproduction. Each numeric hyperparameter carries a locator. |
| `§5 results` | Numbers only, each with the provenance shape in §3 below. Qualitative conclusions allowed but must be marked as such. |
| `§6 limitations` | Author-stated **and** reader-observed, kept separate. Author's own negative results go here verbatim. |
| `§7 transferable` | What a different project could reuse. Must be specific enough to act on. |
| `§8 relations` | Edges to other cards in the library: citation direction, shared baselines, conflicting claims. **One-directional claims must say which direction.** |

## 3. Provenance shape (every number in `§4` / `§5`)

```
value: 0.881
source: text-layer | table-coord | figure-transcription | derived
locator: p.4 Table 2 row "MPNN+AAC" col "CI"
note: transcribed at 600 dpi from a bitmap table panel
```

- `text-layer` — extracted from a text object. Strongest.
- `table-coord` — reconstructed from word coordinates. Nearly as strong; record the thresholds used.
- `figure-transcription` — digits printed inside a bitmap, read at ≥450 dpi with the image kept. Weaker by one tier; **must** carry `note`.
- `derived` — computed by you (difference, ratio, sum). **Must** show the arithmetic in `note`.

A value with no `locator` is not allowed in `§5`. It belongs in `§6` (as a limitation) or in the to-be-filled section (as a gap).

## 4. `si-contains` — the second question

`si-state` answers "is there supplementary material". `si-contains` answers "does it hold the table this claim needs". They routinely disagree.

| `si-state` | possible `si-contains` | what to write |
|---|---|---|
| `independent` | full result tables | `full: Tables S1–S9 incl. per-experiment results` |
| `independent` | argumentation only | `argument-only: no result table; numbers remain in body §5` |
| `inline` | appendix with tables | `inline-appendix: Tables A1–A5 (p.13–18)` |
| `none-as-of` | — | `n/a — code repository only` |

## 5. To-be-filled section

Each entry is a row, not a sentence:

| Field | Rule |
|---|---|
| `item` | The specific missing thing, named as a table/§/figure, not "details". |
| `reason` | One of: `not-in-paper` \| `not-in-si` \| `si-missing` \| `figure-only` \| `code-repo-only` \| `extraction-failed` |
| `blocker` | `blocks-citation` \| `blocks-reproduction` \| `cosmetic` |
| `next-action` | Who could close it (author request / repo read / another version). |

## 6. Extraction log (mandatory)

```
mode: layout | text | words        (per file, if two modes were used, say which page range)
failed-pages: [..]                  (pages below the char threshold, even if later recovered)
rebuilt-tables: [{page, method: coord|rotated, thresholds: {row-tol, col-gap}}, ...]
transcriptions: [{page, dpi, panel}, ...]
dual-version: yes|no                (two extractors cross-checked; which numbers required agreement)
```

## 7. Self-check line (last line of the card)

```
self-check: pages-read=<n>/<n> · failed=<n> · tables-rebuilt=<n> · transcriptions=<n> · contradictions-registered=<n>
```

A card whose `failed` count is non-zero and unlisted in the log is incomplete.

## Changelog

| Version | Date | Change |
|---|---|---|
| v1 | 2026-10-26 | First version. Derived from 24 cards; the provenance shape and `si-contains` split came from failures recorded in `pitfalls-materials.md`. |
