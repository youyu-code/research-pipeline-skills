#!/usr/bin/env python3
"""Score a scan directory against a keyword profile.

    score.py --scan-dir _out/2026-01-07 --config profile.json
    score.py --scan-dir _out/2026-01-07 --config profile.json --since 2026-01-01 --top 10

Input: one or more Atom XML files written by `scan.py`, and a JSON config that
carries the profile. Output: a ranked table on stdout and, with `--out`, a JSON
file with the full match record.

**The profile is data, not code.** No vocabulary lives in this file. That is not
tidiness: a hard-coded profile means every user edits the script to change a
term, and the change then has no diff to review and no config to roll back. The
config is also the only artefact `regress.py` needs to compare two profiles.

**Two boundary tables, not one.** Terms are matched against title and abstract
with a boundary on both sides — the character before and after the term must not
be alphanumeric. A single table shared by keywords and anchors produces two
distinct bug classes: a term that is a prefix of a longer word matches it
(`gene` inside `generative`), and a short acronym matches inside an identifier
or a URL. Anchors are calibrated separately because they answer a different
question — *is this the right kind of object* — and merging the two tables is
how an anchor starts admitting papers no keyword ever matched.

**Three gates, in this order.** A term can match and still not be admitted:

  1. negative terms — any hit removes the item, whatever else matched;
  2. the C-grade rule — an anchor hit, or two distinct keyword hits. One weak
     term is a coincidence, not a topic;
  3. the score — a number below the C threshold is not reported.

The order matters for diagnosis: `miss_diag.py` reports which gate stopped an
item, and "killed by a negative term" and "below the C threshold" lead to
opposite fixes.

Counter-example, from the gate design: a profile that admitted every item with a
single weak match produced a digest where the only signal was the section
header. The fix was not a higher threshold — it was the anchor-or-two-keywords
rule, which asks a different question than the score does.

**Score only a reconciled scan.** The corpus is whatever the scan wrote. A body
cut short at HTTP 200 parses and scores perfectly well, so a transport failure
arrives here disguised as a thin week and the profile gets blamed for it. That is
why `selfcheck.py` runs before this script: when its status column says
`truncated` or `unreachable`, the table below ranks what arrived, not what was
published.

Requires: Python >= 3.8 (standard library only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ATOM = "{http://www.w3.org/2005/Atom}"
GROUP_ORDER = ("strong", "keyword", "anchor", "weak", "negative")

DEFAULTS = {
    "weights": {"strong": 3, "keyword": 2, "anchor": 2, "weak": 1, "negative": -3},
    "grades": {"A": 7, "B": 5, "C": 3},
    "c-grade": "anchor-or-two-keywords",
    "min-anchor-hits": 1,
}


# --------------------------------------------------------------------------- config

def load_config(path):
    """Read the config and fill in the documented defaults."""
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    for key, value in DEFAULTS.items():
        if key not in cfg:
            cfg[key] = value
        elif isinstance(value, dict):
            merged = dict(value)
            merged.update(cfg[key])
            cfg[key] = merged
    if "profile" not in cfg:
        raise SystemExit("config %s has no `profile` section" % path)
    return cfg


def term_regex(term):
    """A term with a boundary on both sides, case-insensitive."""
    return re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(term), re.IGNORECASE)


def compile_profile(cfg):
    """Compile the profile once; return the structure the matcher uses."""
    profile = {}
    for group in GROUP_ORDER:
        terms = cfg["profile"].get(group, [])
        profile[group] = [(term, term_regex(term)) for term in terms]
    return {
        "profile": profile,
        "weights": cfg["weights"],
        "grades": cfg["grades"],
        "rule": cfg["c-grade"],
        "min_anchor": int(cfg.get("min-anchor-hits", 1)),
    }


# --------------------------------------------------------------------------- corpus

def canonical_id(raw):
    """`http://arxiv.org/abs/2601.00001v3` -> `2601.00001`."""
    tail = raw.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"v\d+$", "", tail)


def text_of(element, tag):
    found = element.find(ATOM + tag)
    if found is None or found.text is None:
        return ""
    return " ".join(found.text.split())


def load_corpus(scan_dir):
    """Return [{id, title, summary, published, source, file}], sorted by date.

    Only `*.xml` directly inside the directory is read. `_probe/` and anything
    else starting with `_` is skipped: a probe file that gets parsed is a source
    that does not exist.
    """
    scan_dir = Path(scan_dir)
    files = sorted(p for p in scan_dir.glob("*.xml") if not p.name.startswith("_"))
    if not files:
        raise SystemExit("no *.xml in %s — point --scan-dir at a scan output directory"
                         % scan_dir)
    entries = []
    for path in files:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            print("  warn  %s does not parse (%s) — skipped" % (path.name, exc),
                  file=sys.stderr)
            continue
        for node in root.findall(ATOM + "entry"):
            raw_id = text_of(node, "id")
            entries.append({
                "id": canonical_id(raw_id) if raw_id else "(no id)",
                "title": text_of(node, "title"),
                "summary": text_of(node, "summary"),
                "published": text_of(node, "published")[:10],
                "source": path.stem,
                "file": path.name,
            })
    entries.sort(key=lambda e: (e["published"], e["id"]))
    return entries


# --------------------------------------------------------------------------- scoring

def score_entry(entry, compiled):
    """Match one entry. Returns the match record plus the gate that decided it."""
    haystack = (entry["title"] + " \n " + entry["summary"]).lower()
    matched = {group: [] for group in GROUP_ORDER}
    for group in GROUP_ORDER:
        for term, rx in compiled["profile"][group]:
            if rx.search(haystack):
                matched[group].append(term)

    weights = compiled["weights"]
    score = sum(weights[group] * len(matched[group]) for group in GROUP_ORDER)

    negative = len(matched["negative"]) > 0
    anchor_hits = len(matched["anchor"])
    keyword_hits = len(matched["keyword"])
    rule = compiled["rule"]
    if rule == "anchor-or-two-keywords":
        passes_gate = anchor_hits >= compiled["min_anchor"] or keyword_hits >= 2
    elif rule == "anchor":
        passes_gate = anchor_hits >= compiled["min_anchor"]
    elif rule == "none":
        passes_gate = True
    else:
        raise SystemExit("unknown c-grade rule %r (expected anchor-or-two-keywords|"
                         "anchor|none)" % rule)

    grades = compiled["grades"]
    grade = None
    for name in ("A", "B", "C"):
        if score >= grades[name]:
            grade = name
            break

    if negative:
        verdict, reason = "killed-negative", "negative term: " + ", ".join(matched["negative"])
    elif not passes_gate:
        verdict, reason = "below-gate", "no anchor and fewer than two keyword hits"
    elif grade is None:
        verdict, reason = "below-score", "score %d is under the C threshold (%d)" % (
            score, grades["C"])
    else:
        verdict, reason = "graded", "grade %s" % grade

    return {
        "id": entry["id"],
        "title": entry["title"],
        "published": entry["published"],
        "source": entry["source"],
        "score": score,
        "grade": grade,
        "verdict": verdict,
        "reason": reason,
        "matched": matched,
    }


def analyse(scan_dir, cfg, since=None, until=None):
    """Score a whole directory. Used by score.py, regress.py and miss_diag.py."""
    compiled = compile_profile(cfg)
    rows = []
    for entry in load_corpus(scan_dir):
        if since and entry["published"] < since:
            continue
        if until and entry["published"] > until:
            continue
        rows.append(score_entry(entry, compiled))
    return rows


# --------------------------------------------------------------------------- output

def fmt_matched(matched):
    parts = []
    for group in GROUP_ORDER:
        if matched[group]:
            parts.append("%s:%s" % (group[:2], ", ".join(matched[group])))
    return "; ".join(parts) if parts else "—"


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="score.py",
        description="Score an Atom scan directory against a JSON keyword profile.")
    ap.add_argument("--scan-dir", required=True,
                    help="directory written by scan.py (reads *.xml in it)")
    ap.add_argument("--config", required=True,
                    help="JSON config carrying the profile, weights and grades")
    ap.add_argument("--since", help="keep entries published on or after this date (YYYY-MM-DD)")
    ap.add_argument("--until", help="keep entries published on or before this date (YYYY-MM-DD)")
    ap.add_argument("--top", type=int, default=0,
                    help="show the top N by score (0 = all graded entries)")
    ap.add_argument("--out", help="write the full match record as JSON to this path")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    rows = analyse(args.scan_dir, cfg, args.since, args.until)

    graded = [r for r in rows if r["verdict"] == "graded"]
    counts = {name: sum(1 for r in graded if r["grade"] == name) for name in ("A", "B", "C")}
    killed = sum(1 for r in rows if r["verdict"] == "killed-negative")
    gated = sum(1 for r in rows if r["verdict"] == "below-gate")
    low = sum(1 for r in rows if r["verdict"] == "below-score")

    print("score.py — %s" % args.scan_dir)
    print("  entries %d · graded %d (%s) · negative %d · below gate %d · below score %d"
          % (len(rows), len(graded),
             " ".join("%s=%d" % (k, counts[k]) for k in ("A", "B", "C")),
             killed, gated, low))
    print("")
    if not graded:
        print("  no entry cleared the C threshold — the profile or the window is wrong,")
        print("  and this line is the whole report. Do not write 'nothing was published'.")
        return 0

    graded.sort(key=lambda r: (-r["score"], r["published"], r["id"]))
    shown = graded[:args.top] if args.top > 0 else graded
    print("| grade | score | id | published | source | matched | title |")
    print("|---|---|---|---|---|---|---|")
    for row in shown:
        print("| %s | %d | %s | %s | %s | %s | %s |"
              % (row["grade"], row["score"], row["id"], row["published"],
                 row["source"], fmt_matched(row["matched"]),
                 row["title"].replace("|", "\\|")))
    print("")
    print("  denominator: %d entries in the corpus, %d cleared the gate"
          % (len(rows), len(graded)))

    if args.out:
        Path(args.out).write_text(json.dumps({"entries": rows}, indent=2) + "\n",
                                  encoding="utf-8")
        print("  record %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
