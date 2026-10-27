#!/usr/bin/env python3
"""T3 — smoke test for every script in the repository.

Eleven product scripts in three folders, each tested in two layers:

  --help        every script must answer `--help` with exit 0 and a usage line.
                This is the cheapest possible check and it catches the most
                common breakage: an import that moved, a syntax error, a
                dependency imported at module scope instead of inside the branch
                that needs it.
  synthetic run the scripts are pointed at fixtures copied or regenerated into a
                temporary directory — never at the copy committed in
                `assets/samples/`, so a stale committed fixture cannot make a
                broken script look fine and a script that writes into its input
                cannot corrupt the repository.

Nothing here touches the network. The radar chain runs on `--corpus`, the
offline replay path, against a five-entry synthetic Atom feed; the live endpoint
is exercised by nothing in this suite, and the run log says `"mode": "corpus"`
so a reader cannot mistake the replay for a live scan.

The fixtures are synthetic by construction (Model A/B/C, a deliberately blank
page, five invented papers about widget assembly). No real paper content enters
this repository through the tests.

Expected values are pinned to fixture *shape* (rows, columns, page numbers, the
verdict word, the number of admitted entries), never to byte counts or
timestamps: character totals shift with the pymupdf version and dates move with
the clock, and a test that pins them fails on someone else's machine for no
reason.

Requires: Python >= 3.8 (stdlib only). `pymupdf` is needed for the three PDF
scripts and `pypdf` for layout mode; without them those checks are skipped and
the suite says so.
Exit: 0 = pass, 1 = fail, 77 = everything skipped.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
PC_SCRIPTS = SKILLS / "paper-card" / "scripts"
PC_SAMPLES = SKILLS / "paper-card" / "assets" / "samples"
RADAR_SCRIPTS = SKILLS / "literature-radar" / "scripts"
RADAR_SAMPLES = SKILLS / "literature-radar" / "assets" / "samples"
OPS_SCRIPTS = SKILLS / "research-ops" / "scripts"

# Eleven product scripts. The two paper-card fixture generators are checked for
# `--help` too: they are scripts in the repository, and a generator that no
# longer runs makes every PDF assertion below vacuous.
PRODUCT = {
    "paper-card": (PC_SCRIPTS, ("office_tables.py", "pdf_text.py", "table_coords.py",
                                "rotated_table.py", "check_card.py")),
    "research-ops": (OPS_SCRIPTS, ("check-sources.py",)),
    "literature-radar": (RADAR_SCRIPTS, ("scan.py", "score.py", "selfcheck.py",
                                         "regress.py", "miss_diag.py")),
}
GENERATORS = ("make_sample_pdf.py", "make_samples.py")

# A fixed window that contains the fixture feed's dates. Literal dates are safe
# here: the fixture is frozen, so this is not a timestamp that drifts.
WINDOW_SINCE, WINDOW_UNTIL = "2026-01-01", "2026-01-07"


def run(script_dir, script, args, cwd=None):
    proc = subprocess.run([sys.executable, str(Path(script_dir) / script)] + list(args),
                          cwd=str(cwd or ROOT),
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
        print("  ok    %-30s %s" % (label, detail))

    def fail(self, label, detail):
        self.checks += 1
        self.failures += 1
        print("  FAIL  %-30s %s" % (label, detail))

    def skip(self, label, why):
        self.skips += 1
        print("  SKIP  %-30s %s" % (label, why))

    def expect(self, label, cond, detail=""):
        if cond:
            self.ok(label, detail)
        else:
            self.fail(label, detail)
        return cond


def check_help(rep):
    for folder, (script_dir, scripts) in PRODUCT.items():
        for script in scripts:
            code, out = run(script_dir, script, ["--help"])
            rep.expect("--help %s" % script,
                       code == 0 and "usage" in out.lower(),
                       "" if code == 0 else "exit %d: %s" % (code, out.strip()[:120]))
    for script in GENERATORS:
        proc = subprocess.run([sys.executable, str(PC_SAMPLES / script), "--help"],
                              cwd=str(PC_SAMPLES), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True)
        rep.expect("--help %s" % script,
                   proc.returncode == 0 and "usage" in proc.stdout.lower(),
                   "" if proc.returncode == 0
                   else "exit %d: %s" % (proc.returncode, proc.stdout.strip()[:120]))


# --------------------------------------------------------------------- paper-card

def make_pdf_fixtures(rep, tmp):
    """Regenerate the synthetic fixtures into `tmp`; return their paths."""
    tmp = Path(tmp)
    paths = {}

    gen = PC_SAMPLES / "make_samples.py"
    proc = subprocess.run([sys.executable, str(gen), "--out", str(tmp)],
                          cwd=str(PC_SAMPLES), stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        rep.fail("fixtures .xlsx/.docx", proc.stdout.strip()[:200])
    else:
        paths["xlsx"] = tmp / "synthetic_si_tables.xlsx"
        paths["docx"] = tmp / "synthetic_si_methods.docx"

    if not has_module("pymupdf"):
        return paths, "pymupdf"
    gen_pdf = PC_SAMPLES / "make_sample_pdf.py"
    proc = subprocess.run([sys.executable, str(gen_pdf), "--out", str(tmp)],
                          cwd=str(PC_SAMPLES), stdout=subprocess.PIPE,
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
    code, text = run(PC_SCRIPTS, "office_tables.py",
                     ["--in", str(paths["xlsx"]), "--out", str(out)])
    ok = (code == 0 and "sheet" in text and "rows=" in text and "cols=" in text)
    rep.expect("office_tables .xlsx", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[:200]))

    code, text = run(PC_SCRIPTS, "office_tables.py",
                     ["--in", str(paths["docx"]), "--out", str(out)])
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

    if has_module("pypdf"):
        out = Path(tmp) / "t1"
        code, text = run(PC_SCRIPTS, "pdf_text.py", ["--pdf", pdf, "--out", str(out)])
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

    out = Path(tmp) / "t2"
    code, text = run(PC_SCRIPTS, "pdf_text.py",
                     ["--pdf", pdf, "--out", str(out), "--mode", "text"])
    ok = (code == 0 and "verdict=partly-empty" in text
          and (out / "p004.txt").is_file() and (out / "_all.txt").is_file())
    rep.expect("pdf_text text", ok, "" if ok else text.strip()[:200])

    out = Path(tmp) / "t3"
    code, text = run(PC_SCRIPTS, "table_coords.py",
                     ["--pdf", pdf, "--pages", "2", "--out", str(out)])
    ok = code == 0 and "rows=5" in text and "cols=3" in text
    rep.expect("table_coords p.2", ok, "" if ok else "exit %d: %s" % (code, text.strip()[:200]))

    out = Path(tmp) / "t4"
    code, text = run(PC_SCRIPTS, "rotated_table.py",
                     ["--pdf", pdf, "--page", "3", "--out", str(out)])
    ok = code == 0 and "rotated=12" in text and "rows=4" in text
    rep.expect("rotated_table p.3", ok, "" if ok else "exit %d: %s" % (code, text.strip()[:200]))


# ------------------------------------------------------------------ research-ops

def flat(text, width=160):
    """One-line tail of a command's output, for a failure detail."""
    return " ".join(text.split())[-width:]


def check_sources(rep, tmp):
    """S1 in three states: clean, readonly mismatch, state mismatch.

    Two classes, two exit codes — that is the whole contract, and a fixture that
    only tests the clean path would leave the interesting half unverified.
    """
    tmp = Path(tmp) / "s1"
    inputs = tmp / "inputs"
    inputs.mkdir(parents=True)
    (inputs / "a.txt").write_text("alpha\n", encoding="utf-8")
    (inputs / "b.txt").write_text("beta\n", encoding="utf-8")

    import hashlib
    lines = []
    for name in ("a.txt", "b.txt"):
        digest = hashlib.sha256((inputs / name).read_bytes()).hexdigest()[:16]
        lines.append("%s  %s" % (digest, name))
    manifest = tmp / "sources.sha256"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    code, text = run(OPS_SCRIPTS, "check-sources.py",
                     ["--manifest", str(manifest), "--root", str(inputs)])
    ok = code == 0 and "every entry matches" in text
    rep.expect("check-sources clean", ok, "" if ok else "exit %d: %s" % (code, flat(text)))

    (inputs / "a.txt").write_text("alpha\nchanged\n", encoding="utf-8")
    code, text = run(OPS_SCRIPTS, "check-sources.py",
                     ["--manifest", str(manifest), "--root", str(inputs)])
    ok = code == 1 and "[B5]" in text
    rep.expect("check-sources readonly", ok,
               "" if ok else "exit %d (want 1 + [B5]): %s" % (code, flat(text)))

    code, text = run(OPS_SCRIPTS, "check-sources.py",
                     ["--manifest", str(manifest), "--root", str(inputs),
                      "--class", "state"])
    ok = code == 2 and "re-baselined" in text
    rep.expect("check-sources state", ok,
               "" if ok else "exit %d (want 2 + attribution): %s" % (code, flat(text)))

    # A line that names no usable entry is its own stop reason. Reporting it as
    # "a read-only input changed" would name a culprit that does not exist, so
    # the banner is asserted both ways: the new one present, the old one absent.
    bad_manifest = tmp / "broken.sha256"
    bad_manifest.write_text("zzzz  a.txt\n", encoding="utf-8")
    code, text = run(OPS_SCRIPTS, "check-sources.py",
                     ["--manifest", str(bad_manifest), "--root", str(inputs)])
    new_banner = "manifest malformed" in text
    old_banner = "a read-only input changed" in text
    ok = code == 1 and new_banner and not old_banner
    rep.expect("check-sources malformed", ok,
               "" if ok else "exit %d, malformed-banner=%s, changed-banner=%s: %s"
               % (code, new_banner, old_banner, flat(text)))


# ------------------------------------------------------------------ literature-radar

def check_radar(rep, tmp):
    """S2-S6 in one chain, entirely offline.

    scan -> score -> selfcheck -> regress -> miss_diag. Each step consumes what
    the previous one wrote, so a break anywhere in the chain shows up here rather
    than in a user's first run.
    """
    base = Path(tmp) / "radar"
    base.mkdir(parents=True)
    corpus = base / "raw"
    shutil.copytree(RADAR_SAMPLES / "raw", corpus)
    profile = base / "profile.json"
    profile.write_bytes((RADAR_SAMPLES / "profile.json").read_bytes())
    tight = base / "profile-tight.json"
    tight.write_bytes((RADAR_SAMPLES / "profile-tight.json").read_bytes())
    pushed = base / "pushed_log.md"
    pushed.write_bytes((RADAR_SAMPLES / "pushed_log.md").read_bytes())
    scan_out = base / "scan"

    code, text = run(RADAR_SCRIPTS, "scan.py",
                     ["--corpus", str(corpus), "--out", str(scan_out),
                      "--since", WINDOW_SINCE, "--until", WINDOW_UNTIL,
                      "--source", "cs.LG"])
    ok = (code == 0 and "items=6" in text and "expected=6" in text
          and (scan_out / "cs.LG.xml").is_file() and (scan_out / "_scan.json").is_file())
    rep.expect("scan.py offline replay", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[:200]))

    if ok:
        log = json.loads((scan_out / "_scan.json").read_text(encoding="utf-8"))
        ok2 = (log.get("mode") == "corpus" and log.get("requests-made") == 1
               and log["sources"][0].get("floor") == WINDOW_SINCE)
        rep.expect("scan.py run log", ok2,
                   "" if ok2 else "mode/requests/floor = %s/%s/%s"
                   % (log.get("mode"), log.get("requests-made"),
                      log["sources"][0].get("floor")))

        # Half-open window: the date clause sent to the API is inclusive on both
        # ends, so an exclusive `until` must reach the wire as until-1 23:59.
        url = urllib.parse.unquote(log["sources"][0].get("url", ""))
        ok3 = "submittedDate:[202601010000 TO 202601062359]" in url
        rep.expect("scan.py window clause", ok3,
                   "" if ok3 else "url does not carry the half-open upper bound: %s" % url)

    code, text = run(RADAR_SCRIPTS, "score.py",
                     ["--scan-dir", str(scan_out), "--config", str(profile),
                      "--since", WINDOW_SINCE, "--until", WINDOW_UNTIL])
    ok = code == 0 and "graded 3" in text and "| A | 9 | 2601.00001" in text
    rep.expect("score.py profile", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[:240]))

    # The boundary item is in the corpus and would be graded if admitted. It is
    # published on the window end date, so the half-open window must drop it.
    ok = "2601.00006" not in text
    rep.expect("score.py half-open end", ok,
               "" if ok else "an entry published on --until was admitted: %s"
               % flat(text, 240))

    code, text = run(RADAR_SCRIPTS, "selfcheck.py",
                     ["--out", str(scan_out), "--expect-requests", "1"])
    ok = code == 0 and "selfcheck PASS" in text
    rep.expect("selfcheck.py pass", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[-240:]))

    code, text = run(RADAR_SCRIPTS, "selfcheck.py",
                     ["--out", str(scan_out), "--expect-requests", "2"])
    ok = code == 1 and "FAIL  requests" in text
    rep.expect("selfcheck.py count", ok,
               "" if ok else "exit %d (want 1 + request FAIL): %s"
               % (code, text.strip()[-200:]))

    code, text = run(RADAR_SCRIPTS, "regress.py",
                     ["--config-old", str(profile), "--config-new", str(tight),
                      "--corpus", str(scan_out), "--pushed-log", str(pushed)])
    ok = (code == 1 and "check 1 pushed items lost" in text
          and "2601.00002" in text and "check 3 unexplained loss" in text)
    rep.expect("regress.py six checks", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[-300:]))

    code, text = run(RADAR_SCRIPTS, "miss_diag.py",
                     ["--scan-dir", str(scan_out), "--item-id", "2601.00004",
                      "--config", str(profile)])
    ok = code == 0 and "verdict below-gate" in text
    rep.expect("miss_diag.py no-match", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[-200:]))

    code, text = run(RADAR_SCRIPTS, "miss_diag.py",
                     ["--scan-dir", str(scan_out), "--item-id", "2601.00003",
                      "--config", str(profile)])
    ok = code == 0 and "verdict killed-negative" in text
    rep.expect("miss_diag.py negative", ok,
               "" if ok else "exit %d: %s" % (code, text.strip()[-200:]))


def main():
    print("T3  script smoke test")
    missing = []
    for folder, (script_dir, scripts) in PRODUCT.items():
        for script in scripts:
            if not (script_dir / script).is_file():
                missing.append("%s/%s" % (folder, script))
    if missing:
        for name in missing:
            print("  FAIL  missing script: %s" % name)
        print("T3  FAIL")
        return 1

    rep = Report()
    check_help(rep)

    with tempfile.TemporaryDirectory(prefix="pc-t3-") as tmp:
        paths, why = make_pdf_fixtures(rep, tmp)
        check_office(rep, paths, tmp)
        check_pdf(rep, paths, tmp, why)
        check_sources(rep, tmp)
        check_radar(rep, tmp)

    if rep.failures:
        print("T3  FAIL  (%d check(s), %d skipped, %d failure(s))"
              % (rep.checks, rep.skips, rep.failures))
        return 1
    print("T3  PASS  (%d check(s), %d skipped)" % (rep.checks, rep.skips))
    return 0


if __name__ == "__main__":
    sys.exit(main())
