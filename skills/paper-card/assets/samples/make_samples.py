#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate the minimal synthetic .xlsx / .docx used to smoke-test office_tables.py.

These files contain NO real paper content: one hyperparameter table, one dataset
table, one Word table with a unit suffix. They exist so the parser can be verified
without shipping any private material.

Requires: Python >= 3.8 (stdlib only)

  python make_samples.py --out .
"""
from __future__ import annotations

import argparse
import os
import zipfile
from xml.sax.saxutils import escape

CT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>"""

CT_DOCX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

RELS_DOCX = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

WORKBOOK = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Hyperparameters" sheetId="1" r:id="rId1"/>
<sheet name="Datasets" sheetId="2" r:id="rId2"/>
</sheets>
</workbook>"""

WORKBOOK_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
</Relationships>"""

# cells: ("s", shared_string_index) | ("n", numeric_literal) | (None, None)
SHEET1_ROWS = [
    [("s", 0), ("s", 1), ("s", 2)],          # Name | Value | Note
    [("s", 3), ("n", "0.001"), ("s", 4)],    # learning rate | 0.001 | tuned, not fixed
    [("s", 5), ("n", "256"), ("s", 6)],      # batch size | 256 | per GPU
    [("s", 7), ("n", "0.1"), (None, None)],  # dropout | 0.1 | (empty)
]

SHEET2_ROWS = [
    [("s", 8), ("s", 9)],                    # Dataset | Size
    [("s", 10), ("n", "4510")],              # synthetic set A | 4510
    [("s", 11), ("n", "1200")],              # synthetic set B | 1200
]

SST = [
    "Name", "Value", "Note",
    "learning rate", "tuned, not fixed",
    "batch size", "per GPU",
    "dropout",
    "Dataset", "Size",
    "synthetic set A", "synthetic set B",
]


def _cell(col: str, row: int, kind=None, val=None) -> str:
    ref = "%s%d" % (col, row)
    if kind == "s":
        return '<c r="%s" t="s"><v>%d</v></c>' % (ref, val)
    if kind == "n":
        return '<c r="%s"><v>%s</v></c>' % (ref, val)
    return '<c r="%s"/>' % ref


def _sheet(rows) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for r, cells in enumerate(rows, 1):
        parts = []
        for c, (kind, val) in enumerate(cells):
            col = chr(ord("A") + c)
            parts.append(_cell(col, r, kind, val))
        out.append('<row r="%d">%s</row>' % (r, "".join(parts)))
    out.append("</sheetData></worksheet>")
    return "".join(out)


def _w_p(text: str) -> str:
    return ("<w:p><w:r><w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % escape(text))


def _w_table(grid) -> str:
    rows = []
    for tr in grid:
        cells = "".join("<w:tc>%s</w:tc>" % _w_p(c) for c in tr)
        rows.append("<w:tr>%s</w:tr>" % cells)
    return "<w:tbl>%s</w:tbl>" % "".join(rows)


DOCX_BODY = (
    _w_p("Synthetic supplementary table (no real data).")
    + _w_table([["Metric", "Value", "Unit"],
                ["AUC", "0.881", "ratio"],
                ["RMSE", "1.374", "kcal/mol"]])
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="make_samples.py", description="Write minimal synthetic OOXML samples.")
    ap.add_argument("--out", default=".", help="output directory")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    xlsx = os.path.join(args.out, "synthetic_si_tables.xlsx")
    with zipfile.ZipFile(xlsx, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT)
        z.writestr("_rels/.rels", RELS)
        z.writestr("xl/workbook.xml", WORKBOOK)
        z.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS)
        sst = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">'
               % (len(SST), len(SST))
               + "".join("<si><t xml:space=\"preserve\">%s</t></si>" % escape(s) for s in SST)
               + "</sst>")
        z.writestr("xl/sharedStrings.xml", sst)
        z.writestr("xl/worksheets/sheet1.xml", _sheet(SHEET1_ROWS))
        z.writestr("xl/worksheets/sheet2.xml", _sheet(SHEET2_ROWS))

    docx = os.path.join(args.out, "synthetic_si_methods.docx")
    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CT_DOCX)
        z.writestr("_rels/.rels", RELS_DOCX)
        z.writestr("word/document.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   "<w:body>%s</w:body></w:document>" % DOCX_BODY)

    print("wrote %s" % xlsx)
    print("wrote %s" % docx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
