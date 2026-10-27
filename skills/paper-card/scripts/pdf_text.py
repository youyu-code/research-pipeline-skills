#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extract per-page text from a PDF, with a page-level health check.

Three modes, because the failure modes differ (see references/pitfalls-extraction.md):

  layout   pypdf, extraction_mode="layout" — preserves column spacing. Preferred for
           single-column tables. Silently produces 1-2 characters per page on some
           fonts (B-01) and turns digits into glyph names such as /one.onum (B-02).
  text     PyMuPDF get_text("text") — the usual fallback when layout collapses.
  words    PyMuPDF get_text("words") — one token per line with a bounding box, for
           coordinate-based table reconstruction.

Every mode writes a health report. The report is the point: a page with fewer than
--min-chars characters is marked suspect, and if more than half the pages are suspect
the process exits with code 3 telling you to switch mode. Do not read a suspect page
and conclude "the paper has no text here".

A file that cannot be opened, or that opens as zero pages, also gets a health report:
verdict "unreadable", exit 3. That case is not hypothetical — a download cut off
mid-stream leaves a PDF whose page tree is missing, and a reader that returns zero
pages without raising would otherwise score as "ok" with nothing extracted (B-17).

Requires: Python >= 3.8
  layout mode : pypdf >= 3.9   (pip install pypdf)
  text / words: pymupdf >= 1.23 (pip install pymupdf)

Examples:
  python pdf_text.py --pdf paper.pdf --out txt/ --mode layout
  python pdf_text.py --pdf paper.pdf --out txt/ --mode text --min-chars 50
"""
from __future__ import annotations

import argparse
import json
import os
import sys


class Unreadable(Exception):
    """The file could not be opened, or opens with no pages at all."""


def _pypdf_layout(path: str) -> list:
    from pypdf import PdfReader

    try:
        reader = PdfReader(path)
        n = len(reader.pages)
    except Exception as exc:  # noqa: BLE001 - a damaged file is a verdict, not a crash
        raise Unreadable(repr(exc))
    if n == 0:
        raise Unreadable("reader reports 0 pages")
    out = []
    for i, page in enumerate(reader.pages, 1):
        try:
            txt = page.extract_text(extraction_mode="layout") or ""
        except Exception as exc:  # noqa: BLE001 - record, do not abort the batch
            txt = ""
            out.append((i, txt, repr(exc)))
            continue
        out.append((i, txt, None))
    return out


def _pymupdf(path: str, mode: str) -> list:
    import pymupdf

    try:
        doc = pymupdf.open(path)
        n = doc.page_count
    except Exception as exc:  # noqa: BLE001
        raise Unreadable(repr(exc))
    if n == 0:
        doc.close()
        raise Unreadable("reader reports 0 pages")
    out = []
    for i, page in enumerate(doc, 1):
        try:
            if mode == "words":
                rows = page.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
                txt = "\n".join(
                    "%.2f\t%.2f\t%.2f\t%.2f\t%s\t%d\t%d\t%d" % w for w in rows
                )
            else:
                txt = page.get_text("text") or ""
        except Exception as exc:  # noqa: BLE001
            txt = ""
            out.append((i, "", repr(exc)))
            continue
        out.append((i, txt, None))
    doc.close()
    return out


def _write_unreadable(args, reason: str) -> int:
    """Record a non-extraction in the same report format, then stop."""
    health = {
        "pdf": os.path.basename(args.pdf),
        "mode": args.mode,
        "pages": 0,
        "chars_total": 0,
        "chars_per_page_avg": 0,
        "min_chars_threshold": args.min_chars,
        "suspect_pages": [],
        "suspect_ratio": 0.0,
        "verdict": "unreadable",
        "errors": [{"page": 0, "error": reason}],
    }
    with open(os.path.join(args.out, "_health.json"), "w", encoding="utf-8") as fh:
        json.dump(health, fh, ensure_ascii=False, indent=1)
    if not args.quiet:
        print("mode=%-6s verdict=unreadable  %s" % (args.mode, reason), file=sys.stderr)
    print("HINT: the file is damaged or incomplete, not empty. Try --mode text (PyMuPDF "
          "repairs some structures); if the page count is still 0, fetch the file again "
          "and do not read anything from this copy (B-17).", file=sys.stderr)
    return 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="pdf_text.py",
        description="Per-page PDF text extraction with a health report.",
    )
    ap.add_argument("--pdf", required=True, help="input PDF")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--mode", choices=("layout", "text", "words"), default="layout",
                    help="layout=pypdf, text/words=pymupdf (default: layout)")
    ap.add_argument("--min-chars", type=int, default=10,
                    help="pages below this many characters are suspect (default: 10)")
    ap.add_argument("--prefix", default="p", help="per-page filename prefix (default: p)")
    ap.add_argument("--quiet", action="store_true", help="suppress the console summary")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print("ERROR: pdf not found: %s" % args.pdf, file=sys.stderr)
        return 2
    os.makedirs(args.out, exist_ok=True)

    try:
        if args.mode == "layout":
            pages = _pypdf_layout(args.pdf)
        else:
            pages = _pymupdf(args.pdf, args.mode)
    except ImportError:
        need = "pypdf" if args.mode == "layout" else "pymupdf"
        print("ERROR: mode %r needs %s (pip install %s)" % (args.mode, need, need),
              file=sys.stderr)
        return 2
    except Unreadable as exc:
        return _write_unreadable(args, str(exc))

    if not pages:
        return _write_unreadable(args, "the reader found 0 pages")

    all_chunks, suspect, errors = [], [], []
    for idx, txt, err in pages:
        path = os.path.join(args.out, "%s%03d.txt" % (args.prefix, idx))
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
        all_chunks.append("\n\n===== PAGE %d =====\n\n%s" % (idx, txt))
        if len(txt.strip()) < args.min_chars:
            suspect.append(idx)
        if err:
            errors.append({"page": idx, "error": err})

    all_path = os.path.join(args.out, "_all.txt")
    with open(all_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(all_chunks))

    total = sum(len(c) for c in all_chunks)
    n = len(pages)
    ratio = (len(suspect) / n) if n else 0.0
    if ratio > 0.5 and args.mode == "layout":
        verdict = "layout-failed"
    elif ratio > 0.5:
        verdict = "mostly-empty"
    elif suspect:
        verdict = "partly-empty"
    else:
        verdict = "ok"

    health = {
        "pdf": os.path.basename(args.pdf),
        "mode": args.mode,
        "pages": n,
        "chars_total": total,
        "chars_per_page_avg": round(total / n, 1) if n else 0,
        "min_chars_threshold": args.min_chars,
        "suspect_pages": suspect,
        "suspect_ratio": round(ratio, 3),
        "verdict": verdict,
        "errors": errors,
    }
    hpath = os.path.join(args.out, "_health.json")
    with open(hpath, "w", encoding="utf-8") as fh:
        json.dump(health, fh, ensure_ascii=False, indent=1)

    if not args.quiet:
        print("mode=%-6s pages=%-4d chars=%-8d avg=%-8s verdict=%s"
              % (args.mode, n, total, health["chars_per_page_avg"], verdict))
        if suspect:
            print("suspect pages: %s" % ",".join(str(p) for p in suspect[:20])
                  + (" ..." if len(suspect) > 20 else ""))
        if errors:
            print("errors: %d page(s) raised" % len(errors), file=sys.stderr)

    if verdict == "layout-failed":
        print("HINT: layout mode collapsed. Re-run with --mode text before reading anything.",
              file=sys.stderr)
        return 3
    if verdict == "mostly-empty":
        print("HINT: most pages are empty in this mode too. Try --mode words, then "
              "render pages and transcribe printed digits (B-16).", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
