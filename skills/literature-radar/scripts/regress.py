#!/usr/bin/env python3
"""Replay a corpus under two profiles and report six checks.

    regress.py --config-old profile.json --config-new profile-tight.json \\
               --corpus _out/2026-01-07 --pushed-log pushed_log.md

Exit: 1 = at least one of checks 1-3 failed; 0 = otherwise.

The corpus is held constant and both profiles are applied to it. That is the
whole method: a profile change compared against a changed corpus measures two
things at once and attributes neither.

Only three of the six checks are failures on their own.

  1  previously-pushed items disappear      FAIL  the change lost recall on
                                                   items a human had already
                                                   vetted and delivered
  2  anchor leaks into unrelated matches    FAIL  the anchor side admits items
                                                   no keyword or strong term
                                                   matched — matching too loose
  3  unexplained loss                       FAIL  an item disappeared and no
                                                   removed term or added negative
                                                   accounts for it: the
                                                   attribution is incomplete
  4  coarse item count drops                note  may be precision gain or recall
                                                   loss; needs item-level reading
  5  low-evidence admissions change         note  the false-positive proxy: how
                                                   many admitted items rest on the
                                                   cheapest evidence
  6  score distribution shifts              note  expected whenever matching
                                                   changes

**Check 4 is the one people act on, and acting on it alone is how a precision
improvement gets reverted.** A count of 271 items that vanished was read as a
regression and reverted; the 271 were duplicates the change had correctly
de-duplicated, and the revert restored them. A coarse count is never a verdict.

**Check 3 is what makes the other five readable.** If an item is lost and the
config diff does not explain it, no other number in this report can be trusted
until the cause is found — so it fails even though it looks like bookkeeping.

**Defaults are behaviour.** This script compares two configs as given. When a
new key is added to the loader, the default must reproduce the old behaviour
exactly, even when the old behaviour was a bug: a default that means "never
drop" against code that dropped at a non-zero threshold silently rewrites every
existing config, and the change surfaces as a data regression days later.

Requires: Python >= 3.8 (standard library only). Imports the matcher from
`score.py` — one matcher, one definition, no second copy to drift.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from score import analyse, load_config
except ImportError:                                   # pragma: no cover
    sys.exit("regress.py needs score.py next to it (same scripts/ directory)")

ID_RE = re.compile(r"\b\d{4}\.\d{4,5}\b")


def read_pushed_log(path):
    """IDs already delivered. Tolerates the markdown table and a bare list."""
    ids = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and ID_RE.fullmatch(cells[1]):
                ids.add(cells[1])
                continue
        for token in ID_RE.findall(line):
            ids.add(token)
    return ids


def terms_of(row):
    """All matched terms of one row, flattened, with their group."""
    out = {}
    for group, terms in row["matched"].items():
        for term in terms:
            out[term] = group
    return out


def vocabulary(cfg):
    """Every term in the profile, as a set."""
    return {term for group in cfg["profile"].values() for term in group}


def anchor_only(rows):
    """Items the anchor matched with no strong or keyword hit."""
    return {row["id"] for row in rows
            if row["matched"]["anchor"]
            and not row["matched"]["strong"] and not row["matched"]["keyword"]}


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="regress.py",
        description="Replay one corpus under an old and a new profile; report six "
                    "checks with three of them fatal.")
    ap.add_argument("--config-old", required=True, help="profile in force before the change")
    ap.add_argument("--config-new", required=True, help="profile proposed or applied")
    ap.add_argument("--corpus", required=True, help="scan directory holding the frozen corpus")
    ap.add_argument("--pushed-log", default=None,
                    help="push log for check 1 (default: <corpus>/pushed_log.md if present)")
    ap.add_argument("--since", default=None, help="restrict to entries published on/after")
    ap.add_argument("--until", default=None, help="restrict to entries published on/before")
    args = ap.parse_args(argv)

    cfg_old, cfg_new = load_config(args.config_old), load_config(args.config_new)
    old = analyse(args.corpus, cfg_old, args.since, args.until)
    new = analyse(args.corpus, cfg_new, args.since, args.until)
    old_by_id = {row["id"]: row for row in old}
    new_by_id = {row["id"]: row for row in new}
    admitted_old = {row["id"] for row in old if row["verdict"] == "graded"}
    admitted_new = {row["id"] for row in new if row["verdict"] == "graded"}

    print("regress.py — %s" % args.corpus)
    print("  old  %s" % args.config_old)
    print("  new  %s" % args.config_new)
    print("  corpus %d entries, held constant across both profiles" % len(old))
    print("")

    failures = 0

    # 1 — previously-pushed items disappear
    pushed_path = args.pushed_log
    if not pushed_path:
        candidate = Path(args.corpus) / "pushed_log.md"
        pushed_path = candidate if candidate.is_file() else None
    if pushed_path:
        pushed = read_pushed_log(pushed_path)
        lost = sorted((pushed & admitted_old) - admitted_new)
        if lost:
            print("  FAIL  check 1 pushed items lost    %s" % ", ".join(lost))
            failures += 1
        else:
            print("  ok    check 1 pushed items lost    none of %d pushed items left the "
                  "admitted set" % len(pushed))
    else:
        print("  SKIP  check 1 pushed items lost    no push log (--pushed-log or "
              "<corpus>/pushed_log.md)")

    # 2 — anchor leaks into unrelated matches
    leaked = anchor_only(new) - anchor_only(old)
    if leaked:
        print("  FAIL  check 2 anchor leak          %d new item(s) admitted on an anchor "
              "alone: %s" % (len(leaked), ", ".join(sorted(leaked))))
        failures += 1
    else:
        print("  ok    check 2 anchor leak          no new anchor-only match (%d before, "
              "%d after)" % (len(anchor_only(old)), len(anchor_only(new))))

    # 3 — unexplained loss
    lost_any = (admitted_old - admitted_new)
    removed = vocabulary(cfg_old) - vocabulary(cfg_new)
    added = vocabulary(cfg_new) - vocabulary(cfg_old)
    unexplained = []
    for item in sorted(lost_any):
        matched = terms_of(old_by_id[item])
        removed_hits = [term for term in matched if term in removed]
        newly_negative = [term for term in new_by_id[item]["matched"]["negative"]
                          if term in added]
        if not removed_hits and not newly_negative:
            unexplained.append(item)
    if unexplained:
        print("  FAIL  check 3 unexplained loss     %s — no removed term and no new "
              "negative accounts for it" % ", ".join(unexplained))
        failures += 1
    else:
        print("  ok    check 3 unexplained loss     %d lost item(s), all attributable to "
              "the profile diff" % len(lost_any))

    # 4 — coarse count
    delta = len(admitted_new) - len(admitted_old)
    print("  note  check 4 coarse count         %d → %d admitted (%+d); a coarse count is "
          "not a verdict" % (len(admitted_old), len(admitted_new), delta))

    # 5 — low-evidence admissions (the false-positive proxy)
    def low_evidence(rows):
        return {row["id"] for row in rows if row["verdict"] == "graded"
                and not row["matched"]["strong"] and not row["matched"]["anchor"]}

    low_old, low_new = low_evidence(old), low_evidence(new)
    print("  note  check 5 low-evidence load    %d → %d admitted on keywords alone (%+d); "
          "act only if precision was the target" % (len(low_old), len(low_new),
                                                    len(low_new) - len(low_old)))

    # 6 — score distribution
    scores_old = [row["score"] for row in old if row["verdict"] == "graded"]
    scores_new = [row["score"] for row in new if row["verdict"] == "graded"]
    mean_old = sum(scores_old) / len(scores_old) if scores_old else 0.0
    mean_new = sum(scores_new) / len(scores_new) if scores_new else 0.0
    print("  note  check 6 score distribution   mean %.1f → %.1f over admitted items; a "
          "shift is expected whenever matching changes" % (mean_old, mean_new))

    print("")
    if failures:
        print("regress FAIL  (%d fatal check(s)) — do not ship this profile; read checks "
              "1-3 before touching 4-6" % failures)
        return 1
    print("regress PASS — no fatal check fired; 4-6 need reading, not a conclusion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
