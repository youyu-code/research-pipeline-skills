# Examples — three real papers, one blocked live run

Demonstration material produced by running this repository's skills on real inputs, not fixtures. Nothing here is required to use the skills; it exists so a reader can see what their output looks like, and so the repository's claims about itself have at least one artifact behind them.

## `cards/` — three cards from public arXiv papers

| Card | Paper | arXiv | `si-state` | Extraction mode used | Tables rebuilt | Contradictions registered | Values with provenance |
|---|---|---|---|---|---|---|---|
| [`vaswani2017_attention.md`](cards/vaswani2017_attention.md) | Attention Is All You Need (NeurIPS 2017) | 1706.03762v7 | `inline` | `layout` (clean) | 1 (p.8) | 1 | 16 |
| [`ho2020_ddpm.md`](cards/ho2020_ddpm.md) | Denoising Diffusion Probabilistic Models (NeurIPS 2020) | 2006.11239v2 | `inline` | `layout` (clean) | 1 (p.13) | 1 | 22 |
| [`devlin2019_bert.md`](cards/devlin2019_bert.md) | BERT (arXiv v2) | 1810.04805v2 | `inline` | `layout` rejected, `text` used | 1 (p.6) | 0 | 12 |

All three pass `check_card.py` with exit 0. The PDFs themselves are **not** redistributed — each card records which file it was built from, in `version-evidence` and `source-trail`. To rebuild one:

```bash
curl -L -o paper.pdf https://arxiv.org/pdf/1706.03762v7
python skills/paper-card/scripts/pdf_text.py --pdf paper.pdf --out txt/ --mode layout
cat txt/_health.json                      # read this before any page text
python skills/paper-card/scripts/table_coords.py --pdf paper.pdf --pages 8 --out tables/
python skills/paper-card/scripts/check_card.py cards/vaswani2017_attention.md
```

### What each card is here to show

- **`vaswani2017_attention`** — the clean case: text layer reads, one table rebuilt by coordinate, and a paper-internal contradiction found by reading two locators on the same page (§6.1 says 41.0 for EN-FR; Table 2 and the abstract print 41.8). The card records both and rules on neither. Verified against the PDF text on 2026-10-27 with two independent extractors (`layout`/pypdf and `text`/PyMuPDF): the p.8 sentence reads "achieves a BLEU score of 41.0", Table 2 on the same page prints 41.8, and the abstract on p.1 prints 41.8 — the contradiction is in the paper, not in the extraction.
- **`ho2020_ddpm`** — the side-by-side case: Tables 1 and 2 are printed next to each other on p.5, and the coordinate rebuild merges them into one grid whose rows interleave two unrelated value sets. The script's cell-count guard **did not fire**, so the merge was caught by reading the rebuild, and those values were attributed to `text-layer` instead. The card also registers a claim its own table contradicts (abstract: "state-of-the-art FID" at 3.17; Table 1: `Sparse Transformer` at 2.80). Verified against the PDF text on 2026-10-27 with two independent extractors (`layout`/pypdf and `text`/PyMuPDF): p.1 reads "a state-of-the-art FID score of 3.17", and Table 1 on p.5 carries `Sparse Transformer [7]` at 2.80 in the FID column (the two readers agree; in `text` mode the value sits on the line below its row label, which is how that reader orders a sparse row) — both locators hold, in the paper and in the extraction.
- **`devlin2019_bert`** — the health-report case: `layout` mode returns `verdict: ok` on all 16 pages and the text is unusable, because the page is two columns and the extractor concatenates the columns line by line. A per-page character count cannot see this. The switch to `--mode text` was triggered by reading page 1, and the card records both modes — the rejected one included.

Two of the three `si-state: inline` cards were also the reason the `si-contains` question exists: in BERT the complete pre-training hyperparameters live **only** in Appendix A, so "the SI is present" and "the number you need is present" have different answers for different sections of the same appendix.

## `radar-live-attempt-2026-10-27.md` — a live run that could not be made

The first attempt to point `literature-radar` at the live endpoint is recorded there with its measurements. It failed at the transport layer, before any query reached arXiv, so no digest was produced and no `radar-<date>/` directory exists. The offline path is what the test suite exercises; the live path remains unproven, and the record says exactly why rather than substituting an offline replay for it.

## Status of these examples

- Produced on 2026-10-27 by this repository's scripts, following `skills/paper-card/SKILL.md` step by step.
- Numbers were not re-checked by a second reader. A card is a record of what one reader extracted and where; it is not a second opinion.
- Cards describe public papers; the interpretation in each `§6 Limitations` is the extracting reader's, and each such line names its locator so it can be checked.
