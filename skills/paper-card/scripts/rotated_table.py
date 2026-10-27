#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reconstruct a table that was typeset rotated 90 degrees (landscape insert).

On such a page PyMuPDF's default get_text() flattens the table into scattered words,
and get_text("words") is not directly usable either: the reading order is vertical, so
sorting by y then x produces interleaved garbage (B-05). The reliable evidence is the
line direction:

    line['dir'] == (0, -1)   rotated text, reading bottom-to-top
    line['dir'] == (1, 0)    normal text

So: keep the rotated lines, cluster them into columns by x, order within a column by
descending y, then align rows across columns by y-band. Always render the page and
check the column headers afterwards - the reconstruction tells you the cell contents,
not whether you picked the right column order.

Requires: Python >= 3.8, pymupdf >= 1.23

Examples:
  python rotated_table.py --pdf p.pdf --page 18
  python rotated_table.py --pdf p.pdf --page 18 --col-tol 10 --row-tol 4 --out tab/
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


def collect_rotated(page) -> tuple:
    """Return (rotated_lines, normal_count). Each rotated line: (x0, y1, text, extent).

    ``extent`` is the line's bbox height. For rotated text the visual width runs along
    y, so this is what --min-width filters on.
    """
    rot, normal = [], 0
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            if not text:
                continue
            dx, dy = line["dir"]
            if abs(dx) < 0.5 and abs(abs(dy) - 1.0) < 0.5:
                x0, y0, x1, y1 = line["bbox"]
                rot.append((x0, y1, text, y1 - y0))
            else:
                normal += 1
    return rot, normal


def cluster(values: list, tol: float) -> list:
    """Group 1-D values into clusters; return list of (centre, [indices])."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    groups = []
    for i in order:
        v = values[i]
        if groups and abs(v - groups[-1][0]) <= tol:
            groups[-1][1].append(i)
            n = len(groups[-1][1])
            groups[-1][0] = (groups[-1][0] * (n - 1) + v) / n
        else:
            groups.append([v, [i]])
    return [(c, idx) for c, idx in groups]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="rotated_table.py",
        description="Rebuild a 90-degree rotated table from line directions.",
    )
    ap.add_argument("--pdf", required=True, help="input PDF")
    ap.add_argument("--page", type=int, required=True, help="1-based page number")
    ap.add_argument("--col-tol", type=float, default=8.0,
                    help="x tolerance for merging lines into one column (default: 8.0)")
    ap.add_argument("--row-tol", type=float, default=6.0,
                    help="y tolerance for merging cells into one row (default: 6.0)")
    ap.add_argument("--min-width", type=float, default=0.0,
                    help="skip rotated lines taller than this in bbox height (filters page titles); 0 = keep all")
    ap.add_argument("--order", choices=("asc", "desc"), default="asc",
                    help="row order along y: asc when the header sits at the smallest y "
                         "(text rotated in place), desc when the page itself is rotated (default: asc)")
    ap.add_argument("--out", default=None, help="output directory for a TSV file")
    ap.add_argument("--quiet", action="store_true", help="write the file only")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print("ERROR: pdf not found: %s" % args.pdf, file=sys.stderr)
        return 2

    doc = pymupdf.open(args.pdf)
    if not (1 <= args.page <= len(doc)):
        print("ERROR: page %d out of range (1..%d)" % (args.page, len(doc)), file=sys.stderr)
        return 2
    page = doc[args.page - 1]
    rot, normal = collect_rotated(page)
    doc.close()

    if args.min_width > 0:
        rot = [r for r in rot if r[3] <= args.min_width]

    if not rot:
        print("ERROR: no rotated lines on page %d (dir != (0,-1)). "
              "This page is upright - use table_coords.py instead." % args.page, file=sys.stderr)
        return 3
    if normal > len(rot):
        print("WARN: %d normal lines vs %d rotated — the page is mostly upright; "
              "verify you picked the right page." % (normal, len(rot)), file=sys.stderr)

    xs = [r[0] for r in rot]
    col_groups = cluster(xs, args.col_tol)
    col_of = {}
    for ci, (_centre, idxs) in enumerate(col_groups):
        for i in idxs:
            col_of[i] = ci

    ys = [r[1] for r in rot]
    row_groups = cluster(ys, args.row_tol)
    row_groups.sort(key=lambda g: g[0] if args.order == "asc" else -g[0])
    row_of = {}
    for ri, (_centre, idxs) in enumerate(row_groups):
        for i in idxs:
            row_of[i] = ri

    n_row, n_col = len(row_groups), len(col_groups)
    grid = [["" for _ in range(n_col)] for _ in range(n_row)]
    for i, (_x0, _y1, text, _extent) in enumerate(rot):
        r, c = row_of[i], col_of[i]
        grid[r][c] = (grid[r][c] + " " + text).strip() if grid[r][c] else text

    lines = ["\t".join(r) for r in grid]

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, "p%03d_rot.tsv" % args.page)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        if not args.quiet:
            print("page %-4d rotated=%d rows=%d cols=%d -> %s"
                  % (args.page, len(rot), n_row, n_col, path))

    if not args.quiet:
        for line in lines:
            print("  " + line)
        print("REMINDER: render page %d and check the column headers before citing any cell."
              % args.page)
        print("          If the header row landed last, re-run with %s."
              % ("--order desc" if args.order == "asc" else "--order asc"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
