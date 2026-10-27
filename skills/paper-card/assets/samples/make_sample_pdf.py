#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate the synthetic PDF used to smoke-test pdf_text.py / table_coords.py /
rotated_table.py.

Content is deliberately fake (Model A/B/C, 0.1xx numbers) so that no real paper
material enters the repository. Four pages:

  p1  prose only                     - text-mode sanity
  p2  upright 3-column table         - coordinate reconstruction target
  p3  the same table rotated 90 deg  - rotated-table reconstruction target
  p4  blank page                     - health-check must flag it as suspect

Requires: Python >= 3.8, pymupdf >= 1.23

  python make_sample_pdf.py --out .
"""
from __future__ import annotations

import argparse
import os

import pymupdf

COLS = [50, 170, 290]
HEADER = ["Model", "MSE", "CI"]
ROWS = [["Model A", "0.242", "0.881"],
        ["Model B", "0.178", "0.872"],
        ["Model C", "0.310", "0.804"]]


def _draw_table(page, x0: float, y0: float, rotate: int = 0) -> None:
    dy = 22
    for c, text in enumerate(HEADER):
        page.insert_text((x0 + COLS[c], y0), text, fontsize=10, rotate=rotate)
    for r, row in enumerate(ROWS, 1):
        for c, text in enumerate(row):
            page.insert_text((x0 + COLS[c], y0 + r * dy), text, fontsize=10, rotate=rotate)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="make_sample_pdf.py",
                                 description="Write a 4-page synthetic PDF for smoke tests.")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--name", default="synthetic_paper.pdf", help="output filename")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    doc = pymupdf.open()

    p1 = doc.new_page()
    p1.insert_text((50, 70), "Synthetic methods note (no real data)", fontsize=14)
    p1.insert_text((50, 100),
                   "This page exists so that text extraction has something to read. "
                   "It contains two sentences and nothing numeric.", fontsize=10)

    p2 = doc.new_page()
    p2.insert_text((50, 70), "Table 1. Synthetic results", fontsize=11)
    _draw_table(p2, 0, 100)

    p3 = doc.new_page()
    p3.insert_text((70, 70), "Table 2. Same synthetic rows, rotated", fontsize=11)
    _draw_table(p3, 0, 120, rotate=90)

    doc.new_page()  # deliberately blank

    out = os.path.join(args.out, args.name)
    doc.save(out)
    doc.close()
    print("wrote %s (4 pages)" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
