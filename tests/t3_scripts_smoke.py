#!/usr/bin/env python3
"""T3 — smoke test for every script in the repository.

Two layers per script:

  --help        every script must answer `--help` with exit 0 and a usage line.
                This is the cheapest possible check and it catches the most
                common breakage: an import that moved, a syntax error, a
                dependency imported at module scope instead of inside the branch
                that needs it.
  synthetic run the scripts are pointed at fixtures regenerated into a temporary
                directory — never at the copy committed in `assets/samples/`, so a
                stale committed fixture cannot make a broken script look fine.

The fixtures are synthetic by construction (Model A/B/C, a deliberately blank
page). No real paper content enters this repository through the tests.

Expected values are pinned to fixture *shape* (rows, columns, page numbers, the
verdict word), never to byte counts: character totals shift with the pymupdf
version, and a test that pins them would fail on someone else's machine for no
reason.

Requires: Python >= 3.8 (stdlib only). `pymupdf` is needed for the three PDF
scripts and `pypdf` for layout mode; without them those checks are skipped and
the suite says so.
Exit: 0 = pass, 1 = fail, 77 = everything skipped.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "paper-card" / "scripts"
SAMPLES = ROOT / "skills" / "paper-card" / "assets" / "samples"

# Five product scripts. The two fixture generators are checked for `--help` too:
# they are scripts in the repository, and a generator that no longer runs makes
# every PDF assertion below vacuous.
ALL_SCRIPTS = (
    "office_tables.py",
    "pdf_text.py",
    "table_coords.py",
    "rotated_table.py",
    "check_card.py",
)
GENERATORS = ("make_sample_pdf.py", "make_samples.py")


def run(script, args):
    proc = subprocess.run([sys.executable, str(SCRIPTS / script)] + list(args),
                          cwd=str(ROOT),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True)
    return proc.returncode, proc.stdout


def has_module(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False


class Report:
    def __init__(self):
        self.failures = 0
        self.checks = 0
        self.skips = 0

    def ok(self, label, detail=""):
        self.checks += 1
        print("  ok    %-28s %s" % (label, detail))

    def fail(self, label, detail):
        self.checks += 1
        self.failures += 1
        print("  FAIL  %-28s %s" % (label, detail))

    def skip(self, label, why):
        self.skips += 1
        print("  SKIP  %-28s %s" % (label, why))

    def expect(self, label, cond, detail=""):
        if cond:
            self.ok(label, detail)
        else:
            self.fail(label, detail)
        return cond


def check_help(rep):
    for script in ALL_SCRIPTS:
        code, out = run(script, ["--help"])
        rep.expect("--help %s" % script,
                   code == 0 and "usage" in out.lower(),
                   "" if code == 0 else "exit %d: %s" % (code, out.strip()[:120]))
    for script in GENERATORS:
        proc = subprocess.run([sys.executable, str(SAMPLES / script), "--help"],
                              cwd=str(SAMPLES), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True)
        rep.expect("--help %s" % script,
                   proc.returncode == 0 and "usage" in proc.stdout.lower(),
                   "" if proc.returncode == 0
                   else "exit %d: %s" % (proc.returncode, proc.stdout.strip()[:120]))


def make_fixtures(rep, tmp):
    """Regenerate the synthetic fixtures into `tmp`; return their paths."""
    tmp = Path(tmp)
    paths = {}

    gen = SAMPLES / "make_samples.py"
    proc = subprocess.run([sys.executable, str(gen), "--out", str(tmp)],
                          cwd=str(SAMPLES), stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        rep.fail("fixtures .xlsx/.docx", proc.stdout.strip()[:200])
    else:
        paths["xlsx"] = tmp / "synthetic_si_tables.xlsx"
        paths["docx"] = tmp / "synthetic_si_methods.docx"

    if not has_module("pymupdf"):
        return paths, "pymupdf"
    gen_pdf = SAMPLES / "make_sample_pdf.py"
    proc = subprocess.run([sys.executable, str(gen_pdf), "--out", str(tmp)],
                          cwd=str(SAMPLES), stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        rep.fail("fixtures .pdf", proc.stdout.strip()[:200])
    else:
        paths["pdf"] = tmp / "synthetic_paper.pdf"
    return paths, None


def check_office(rep, paths, tmp):
    if "xlsx" not in paths:
        rep.skip("office_tables .xlsx", "fixture generation failed earlier")
        return
    out = Path(tmp) / "office"
    code, text = run("office_tables.py", ["--in", str(paths["xlsx"]), "--out", str(out)])
    ok = (code == 0 and "sheet" in text and "rows=" in text and "cols=" in text)
    rep.expect("office_tables .xlsx", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[:200]))

    code, text = run("office_tables.py", ["--in", str(paths["docx"]), "--out", str(out)])
    ok = code == 0 and "table" in text and "rows=" in text
    rep.expect("office_tables .docx", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[:200]))


def check_pdf(rep, paths, tmp, why_skip):
    if "pdf" not in paths:
        for label in ("pdf_text layout", "pdf_text text", "table_coords p.2",
                      "rotated_table p.3"):
            rep.skip(label, why_skip or "fixture generation failed earlier")
        return
    pdf = str(paths["pdf"])

    # layout mode (pypdf)
    if has_module("pypdf"):
        out = Path(tmp) / "t1"
        code, text = run("pdf_text.py", ["--pdf", pdf, "--out", str(out)])
        health = out / "_health.json"
        ok = (code == 0 and "verdict=partly-empty" in text and health.is_file())
        detail = ""
        if ok:
            data = json.loads(health.read_text(encoding="utf-8"))
            ok = data.get("suspect_pages") == [4] and data.get("verdict") == "partly-empty"
            detail = "verdict=%s suspect_pages=%s" % (
                data.get("verdict"), data.get("suspect_pages"))
        rep.expect("pdf_text layout", ok, detail or text.strip()[:200])
    else:
        rep.skip("pdf_text layout", "pypdf not installed")

    # text mode (pymupdf)
    out = Path(tmp) / "t2"
    code, text = run("pdf_text.py", ["--pdf", pdf, "--out", str(out), "--mode", "text"])
    ok = (code == 0 and "verdict=partly-empty" in text
          and (out / "p004.txt").is_file() and (out / "_all.txt").is_file())
    rep.expect("pdf_text text", ok, "" if ok else text.strip()[:200])

    # upright table
    out = Path(tmp) / "t3"
    code, text = run("table_coords.py", ["--pdf", pdf, "--pages", "2", "--out", str(out)])
    ok = code == 0 and "rows=5" in text and "cols=3" in text
    rep.expect("table_coords p.2", ok, "" if ok else "exit %d: %s" % (code, text.strip()[:200]))

    # rotated table
    out = Path(tmp) / "t4"
    code, text = run("rotated_table.py", ["--pdf", pdf, "--page", "3", "--out", str(out)])
    ok = code == 0 and "rotated=12" in text and "rows=4" in text
    rep.expect("rotated_table p.3", ok, "" if ok else "exit %d: %s" % (code, text.strip()[:200]))


def main():
    print("T3  script smoke test")
    for script in ALL_SCRIPTS:
        if not (SCRIPTS / script).is_file():
            print("  FAIL  missing script: %s" % script)
            print("T3  FAIL")
            return 1

    rep = Report()
    check_help(rep)

    with tempfile.TemporaryDirectory(prefix="pc-t3-") as tmp:
        paths, why = make_fixtures(rep, tmp)
        check_office(rep, paths, tmp)
        check_pdf(rep, paths, tmp, why)

    if rep.failures:
        print("T3  FAIL  (%d check(s), %d skipped, %d failure(s))"
              % (rep.checks, rep.skips, rep.failures))
        return 1
    print("T3  PASS  (%d check(s), %d skipped)" % (rep.checks, rep.skips))
    return 0


if __name__ == "__main__":
    sys.exit(main())
