#!/usr/bin/env python3
"""Explain why one known item is not in the digest.

    miss_diag.py --scan-dir _out/2026-01-07 --item-id 2601.00004
    miss_diag.py --scan-dir _out/2026-01-07 --item-id 2601.00004 --config profile.json

Input: the scan directory the run produced, one item id, and optionally the
profile. Output: one block naming the gate that stopped the item, or the fact
that the corpus never contained it.

The distinction the report must make is between **not fetched** and **filtered**.
They look identical downstream — the item is absent either way — and they have
opposite fixes: one is a window or a paging problem, the other is a vocabulary
problem. A diagnosis that says "missed" without saying which is a diagnosis that
cannot be acted on.

Order of causes, and why the order is fixed:

  1  not in the corpus at all          the scan never saw it: window, source
                                       list, or a dropped page
  2  outside the window                present in the corpus, dated outside the
                                       run's own window — usually a backfill
                                       item that arrived in the same feed
  3  killed by a negative term         the profile removed it on purpose
  4  below the C gate                  no anchor and fewer than two keywords: the
                                       term is too rare to clear the gate alone
  5  below the score threshold         cleared the gate, too few terms to reach C
  6  graded                            not a miss; the digest cut it downstream

Only 1 and 4 are normally worth changing the profile for. 2 and 3 are correct
behaviour, and "fixing" them re-admits items the run deliberately excluded.

Counter-example: a known paper was diagnosed as "keyword missing" and a term was
added. The term was already there; the paper had been filtered by a negative
term that matched the word "retraction" in an unrelated sentence. The profile
grew a redundant keyword, the paper stayed out, and the negative term stayed
unexamined for another month.

Requires: Python >= 3.8 (standard library only). Imports the matcher from
`score.py`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from score import compile_profile, load_config, load_corpus, score_entry
except ImportError:                                   # pragma: no cover
    sys.exit("miss_diag.py needs score.py next to it (same scripts/ directory)")

NEXT = {
    "absent": "the scan never fetched this item: check the window, the source list, "
              "and whether a continuation request was dropped",
    "out-of-window": "present in the corpus but outside the run's window — a backfill "
                     "item, not a miss",
    "killed-negative": "removed by design; read the negative term before changing it",
    "below-gate": "the text needs a term it actually uses, or the item stays out",
    "below-score": "cleared the gate but scored under C — add evidence or lower the "
                   "threshold deliberately",
    "graded": "not a miss: it was scored and the digest cut it downstream",
}


def find_item(scan_dir, item_id):
    for entry in load_corpus(scan_dir):
        if entry["id"] == item_id:
            return entry
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="miss_diag.py",
        description="Diagnose why one item id is absent from a radar digest.")
    ap.add_argument("--scan-dir", required=True, help="the scan directory the run produced")
    ap.add_argument("--item-id", required=True, help="canonical id, e.g. 2601.00004")
    ap.add_argument("--config", default=None,
                    help="profile to diagnose against (default: <scan-dir>/../profile.json, "
                         "then the sample profile next to this script)")
    ap.add_argument("--since", default=None, help="the run's window start, inclusive (YYYY-MM-DD)")
    ap.add_argument("--until", default=None,
                    help="the run's window end, exclusive (YYYY-MM-DD)")
    args = ap.parse_args(argv)

    item_id = args.item_id.strip()
    print("miss_diag.py — %s" % item_id)
    print("  corpus  %s" % args.scan_dir)

    entry = find_item(args.scan_dir, item_id)
    if entry is None:
        print("  found   no — the id appears in no *.xml of this directory")
        print("  verdict absent")
        print("  next    %s" % NEXT["absent"])
        return 0

    print("  found   yes — %s, published %s, source %s"
          % (entry["file"], entry["published"], entry["source"]))

    if args.since and entry["published"] < args.since:
        print("  verdict out-of-window — published %s, before the window start %s"
              % (entry["published"], args.since))
        print("  next    %s" % NEXT["out-of-window"])
        return 0
    if args.until and entry["published"] >= args.until:
        print("  verdict out-of-window — published %s, on or after the window end %s"
              % (entry["published"], args.until))
        print("  next    %s" % NEXT["out-of-window"])
        return 0

    config_path = args.config
    if not config_path:
        for candidate in (Path(args.scan_dir).parent / "profile.json",
                          Path(__file__).resolve().parent.parent
                          / "assets" / "samples" / "profile.json"):
            if candidate.is_file():
                config_path = str(candidate)
                break
    if not config_path:
        print("  verdict undetermined — no profile given, so no term trace is possible")
        print("  next    re-run with --config; presence alone does not explain a miss")
        return 0

    cfg = load_config(config_path)
    row = score_entry(entry, compile_profile(cfg))
    matched = row["matched"]
    if any(matched.values()):
        for group in ("strong", "keyword", "anchor", "weak", "negative"):
            if matched[group]:
                print("  match   %-9s %s" % (group, ", ".join(matched[group])))
    else:
        print("  match   none — no term in the profile appears in the title or abstract")

    print("  score   %d (C threshold %d)" % (row["score"], cfg["grades"]["C"]))
    print("  verdict %s — %s" % (row["verdict"], row["reason"]))
    print("  next    %s" % NEXT.get(row["verdict"], "read the match record above"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
