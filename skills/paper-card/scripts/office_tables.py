#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read spreadsheets and Word tables with the standard library only.

Why this exists: supplementary material usually ships as .xlsx / .docx, and a
research environment often has no openpyxl / python-docx. Parsing the OOXML
container directly (zipfile + ElementTree) removes that dependency entirely.

Requires: Python >= 3.8 (stdlib only: zipfile, xml.etree.ElementTree, csv, argparse)

Outputs, written into --out:
  <stem>.<sheet>.csv   one CSV per worksheet (xlsx)
  <stem>.table<N>.csv  one CSV per table   (docx)
  <stem>.manifest.csv  inventory: file, part, rows, cols, path

Known limits (documented, not silently ignored):
  - merged cells are not expanded; the anchor cell carries the value
  - formulas are read as their cached <v> value; if absent the cell is empty
  - .xls (BIFF) and .doc are NOT supported; convert to OOXML first

Example:
  python office_tables.py --in supp_tables.xlsx --out ./csv
  python office_tables.py --in si_methods.docx --out ./csv --quiet
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS_SS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_M = "{%s}" % NS_SS
_W = "{%s}" % NS_W


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def col_index(ref: str) -> int:
    """A1 -> 0, AA1 -> 26. Returns -1 when the ref has no letters."""
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return -1
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_shared_strings(zf: zipfile.ZipFile) -> list:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    out = []
    for si in root.findall(_M + "si"):
        # rich text splits a string across several <t> nodes inside <r>
        out.append("".join(t.text or "" for t in si.iter(_M + "t")))
    return out


def read_sheet_targets(zf: zipfile.ZipFile) -> list:
    """[(sheet_name, zip_path)] in workbook order."""
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for sh in wb.find(_M + "sheets"):
        rid = sh.get("{%s}id" % NS_REL)
        tgt = relmap.get(rid, "")
        if tgt.startswith("/"):
            path = tgt.lstrip("/")
        elif tgt.startswith("xl/"):
            path = tgt
        else:
            path = "xl/" + tgt
        out.append((sh.get("name") or "sheet", path))
    return out


def read_one_sheet(zf: zipfile.ZipFile, path: str, sst: list) -> list:
    """Return rows of strings, padded to the widest row."""
    root = ET.fromstring(zf.read(path))
    grid = []
    for row in root.iter(_M + "row"):
        cells = {}
        for c in row.findall(_M + "c"):
            idx = col_index(c.get("r", ""))
            if idx < 0:
                continue
            t = c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(_M + "t"))
            else:
                v = c.find(_M + "v")
                raw = v.text if v is not None else ""
                if t == "s" and raw not in (None, ""):
                    try:
                        val = sst[int(raw)]
                    except (ValueError, IndexError):
                        val = raw
                else:
                    val = raw
            cells[idx] = (val or "").strip()
        if cells:
            width = max(cells) + 1
            grid.append([cells.get(i, "") for i in range(width)])
    if not grid:
        return []
    width = max(len(r) for r in grid)
    return [r + [""] * (width - len(r)) for r in grid]


def docx_tables(zf: zipfile.ZipFile) -> list:
    """Return [[table]] where table = list of rows of strings."""
    if "word/document.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("word/document.xml"))
    tables = []
    for tbl in root.iter(_W + "tbl"):
        rows = []
        for tr in tbl.findall(_W + "tr"):
            cells = []
            for tc in tr.findall(_W + "tc"):
                # join paragraphs with a space; keep it single-line for CSV
                paras = []
                for p in tc.findall(_W + "p"):
                    paras.append("".join(t.text or "" for t in p.iter(_W + "t")))
                cells.append(" ".join(x for x in paras if x).strip())
            rows.append(cells)
        if rows:
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            tables.append(rows)
    return tables


def write_csv(path: str, rows: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(rows)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="office_tables.py",
        description="Convert .xlsx / .docx tables to CSV using only the standard library.",
    )
    ap.add_argument("--in", dest="src", required=True, help="input .xlsx or .docx")
    ap.add_argument("--out", dest="out", required=True, help="output directory (created if absent)")
    ap.add_argument("--sheet", default=None, help="only this sheet name (xlsx only)")
    ap.add_argument("--quiet", action="store_true", help="suppress the per-part log")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.src):
        print("ERROR: input not found: %s" % args.src, file=sys.stderr)
        return 2
    ext = os.path.splitext(args.src)[1].lower()
    if ext not in (".xlsx", ".docx"):
        print("ERROR: unsupported extension %r (need .xlsx or .docx)" % ext, file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.src))[0]
    manifest = []

    with zipfile.ZipFile(args.src) as zf:
        if ext == ".xlsx":
            sst = read_shared_strings(zf)
            targets = read_sheet_targets(zf)
            if args.sheet:
                targets = [t for t in targets if t[0] == args.sheet]
                if not targets:
                    print("ERROR: sheet not found: %s" % args.sheet, file=sys.stderr)
                    return 2
            for name, path in targets:
                try:
                    rows = read_one_sheet(zf, path, sst)
                except KeyError:
                    print("WARN: sheet part missing: %s" % path, file=sys.stderr)
                    continue
                safe = re.sub(r"[^\w.\-]+", "_", name)
                dst = os.path.join(args.out, "%s.%s.csv" % (stem, safe))
                write_csv(dst, rows)
                ncol = len(rows[0]) if rows else 0
                manifest.append([os.path.basename(args.src), "sheet:" + name, len(rows), ncol, dst])
                if not args.quiet:
                    print("sheet %-24s rows=%-5d cols=%-3d -> %s" % (name, len(rows), ncol, dst))
        else:
            for i, rows in enumerate(docx_tables(zf), 1):
                dst = os.path.join(args.out, "%s.table%d.csv" % (stem, i))
                write_csv(dst, rows)
                ncol = len(rows[0]) if rows else 0
                manifest.append([os.path.basename(args.src), "table:%d" % i, len(rows), ncol, dst])
                if not args.quiet:
                    print("table %-4d                 rows=%-5d cols=%-3d -> %s" % (i, len(rows), ncol, dst))

    if not manifest:
        print("ERROR: no tables found in %s" % args.src, file=sys.stderr)
        return 1

    mpath = os.path.join(args.out, "%s.manifest.csv" % stem)
    write_csv(mpath, [["file", "part", "rows", "cols", "csv"]] + manifest)
    if not args.quiet:
        print("manifest -> %s  (%d part(s))" % (mpath, len(manifest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
