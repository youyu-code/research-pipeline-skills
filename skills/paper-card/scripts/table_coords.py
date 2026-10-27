#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reconstruct a table from word coordinates (upright pages).

Sequential text extraction merges columns whenever a table sits next to prose, and
silently mis-orders cells when two tables are typeset side by side (B-06, B-07, B-08).
Coordinates are the only reliable evidence in those cases: group words into rows by
vertical position, then split each row into cells by horizontal gaps.

Two guards are built in, because both failure modes are otherwise silent:

  1. Column-count check  - if rows disagree on how many cells they contain, the split
     is suspect and the tool says so (exit 4). A table where one row has 4 cells and
     the next has 7 is misaligned, not a 7-column table.
  2. Optional row-sum check (--sum-target) - for percentage / share tables, verify that
     numeric cells in a row add up to the expected total within a tolerance.

Requires: Python >= 3.8, pymupdf >= 1.23

Examples:
  python table_coords.py --pdf p.pdf --pages 7 --out tab/
  python table_coords.py --pdf p.pdf --pages 7,8 --row-tol 4 --col-gap 15
  python table_coords.py --pdf p.pdf --pages 12 --sum-target 100 --sum-tol 0.5
"""
from __future__ import annotations

import argparse
import os
import sys

try:
    import pymupdf
except ImportError:  # pragma: no cover
    print("ERROR: pymupdf is required (pip install pymupdf)", file=sys.stderr)
    raise SystemExit(2)


def build_rows(words: list, row_tol: float) -> list:
    """Group words into rows keyed by rounded vertical centre."""
    buckets = {}
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        if not text.strip():
            continue
        key = round(((y0 + y1) / 2.0) / row_tol)
        buckets.setdefault(key, []).append((x0, x1, text))
    return [buckets[k] for k in sorted(buckets)]


def split_cells(row: list, col_gap: float) -> list:
    row = sorted(row, key=lambda t: t[0])
    cells, cur, prev_x1 = [], [row[0][2]], row[0][1]
    for x0, x1, text in row[1:]:
        if x0 - prev_x1 > col_gap:
            cells.append(" ".join(cur))
            cur, prev_x1 = [text], x1
        else:
            cur.append(text)
            prev_x1 = max(prev_x1, x1)
    cells.append(" ".join(cur))
    return cells


def is_num(s: str) -> bool:
    t = s.replace(",", "").replace("%", "").strip()
    try:
        float(t)
        return True
    except ValueError:
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="table_coords.py",
        description="Rebuild a table from PDF word coordinates, with misalignment guards.",
    )
    ap.add_argument("--pdf", required=True, help="input PDF")
    ap.add_argument("--pages", required=True,
                    help="1-based page numbers, comma separated (e.g. 7 or 7,8,12)")
    ap.add_argument("--out", default=None, help="output directory for TSV files")
    ap.add_argument("--row-tol", type=float, default=3.0,
                    help="vertical tolerance for grouping words into one row (default: 3.0)")
    ap.add_argument("--col-gap", type=float, default=12.0,
                    help="horizontal gap that starts a new cell (default: 12.0)")
    ap.add_argument("--sum-target", type=float, default=None,
                    help="expected total of numeric cells in a row; enables the row-sum check")
    ap.add_argument("--sum-tol", type=float, default=0.5,
                    help="tolerance for --sum-target (default: 0.5)")
    ap.add_argument("--quiet", action="store_true", help="write files only")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print("ERROR: pdf not found: %s" % args.pdf, file=sys.stderr)
        return 2
    try:
        pages = [int(p) for p in args.pages.replace(" ", "").split(",") if p]
    except ValueError:
        print("ERROR: --pages must be comma-separated integers", file=sys.stderr)
        return 2

    if args.out:
        os.makedirs(args.out, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    rc = 0
    for pno in pages:
        if not (1 <= pno <= len(doc)):
            print("WARN: page %d out of range (1..%d)" % (pno, len(doc)), file=sys.stderr)
            continue
        page = doc[pno - 1]
        rows = build_rows(page.get_text("words"), args.row_tol)
        grid = [split_cells(r, args.col_gap) for r in rows]
        if not grid:
            print("WARN: page %d has no words" % pno, file=sys.stderr)
            continue

        widths = sorted({len(r) for r in grid if len(r) >= 2})
        if len(widths) > 1:
            print("WARN: page %d rows disagree on cell count %s — misalignment suspected "
                  "(tune --row-tol / --col-gap, or verify by rendering)."
                  % (pno, widths), file=sys.stderr)
            rc = 4
        elif not widths and len(grid) >= 3:
            print("WARN: page %d produced a single column for every row — --col-gap may be "
                  "too large (under-split), or the page has no table." % pno, file=sys.stderr)
            rc = 4
        elif widths and widths[-1] > 12:
            print("WARN: page %d produced up to %d cells per row — --col-gap may be too "
                  "small (over-split)." % (pno, widths[-1]), file=sys.stderr)
            rc = 4

        if args.sum_target is not None:
            for i, r in enumerate(grid, 1):
                nums = [float(c.replace(",", "").replace("%", "")) for c in r if is_num(c)]
                if len(nums) >= 2:
                    total = sum(nums)
                    if abs(total - args.sum_target) > args.sum_tol:
                        print("WARN: page %d row %d numeric sum = %.3f, expected %.3f +/- %.3f"
                              % (pno, i, total, args.sum_target, args.sum_tol), file=sys.stderr)
                        rc = 4

        out_lines = ["\t".join(r) for r in grid]
        if args.out:
            path = os.path.join(args.out, "p%03d.tsv" % pno)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(out_lines) + "\n")
            if not args.quiet:
                print("page %-4d rows=%-4d cols=%s -> %s"
                      % (pno, len(grid), widths if len(widths) > 1 else widths[0], path))
        if not args.quiet:
            for line in out_lines:
                print("  " + line)
    doc.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
