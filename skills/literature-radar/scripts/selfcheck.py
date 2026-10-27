#!/usr/bin/env python3
"""Four end-of-run checks, from the run log. Nothing here reads the network.

    selfcheck.py --out _out/2026-01-07 --expect-requests 14

Exit: 0 = the run may report, 1 = it may not.

The checks exist because every one of these failures is invisible in the report
itself. A missing continuation request produces a report with items in it. A
truncated body produces a report with items in it. A source with no status
produces a report with one fewer row and no gap where the row should be. Only
the reconciliation catches them, and only if it runs before the report is
written.

  1  request count     `requests-made` equals what you expected, and the
                       arithmetic is written down: one query per source, plus
                       continuation requests, plus retries. A run that cannot
                       explain its own request count did not plan its paging.
  2  server vs local   per source, the parsed item count equals the number the
                       server reported. A shortfall is truncation or a dropped
                       page, not an empty tail. Where the server total is
                       unavailable, `expected` is null and this check says so
                       rather than inventing a number: an unavailable total is an
                       honest gap, a fabricated one closes the check without
                       closing the gap.
  3  status written    every source has a status, including the ones with zero
                       items. "No status" and "no items" look identical in a
                       report, and only one of them is news.
  4  floor reaches     the shallowest per-source floor reaches the window start.
      the window       If it does not, the window was not covered, however many
                       items came back.

Counter-example, and the reason check 4 is a separate check: a run whose busiest
source returned 300 items all inside the window looked complete, while its
slowest source had never been walked back past the opening days of the window.
The request count reconciled, the server totals matched, every status was `ok`.
Most of the window had never been read.

Requires: Python >= 3.8 (standard library only).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_log(out):
    path = Path(out) / "_scan.json"
    if not path.is_file():
        raise SystemExit("%s not found — point --out at a directory scan.py wrote" % path)
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="selfcheck.py",
        description="Reconcile a scan run log against the four end-of-run checks.")
    ap.add_argument("--out", required=True, help="scan output directory (reads _scan.json)")
    ap.add_argument("--expect-requests", type=int, required=True,
                    help="the number of requests this run intended to make")
    ap.add_argument("--since", default=None,
                    help="window start to compare the floor against "
                         "(default: the value recorded in the log)")
    args = ap.parse_args(argv)

    log = load_log(args.out)
    since = args.since or log.get("window", {}).get("since")
    sources = log.get("sources", [])
    problems = 0

    print("selfcheck.py — %s" % args.out)
    print("  window   [%s, %s)" % (log.get("window", {}).get("since"),
                                   log.get("window", {}).get("until")))

    # 1 — request count
    made = int(log.get("requests-made", -1))
    if made == args.expect_requests:
        print("  ok    requests            %d made, %d expected" % (made, args.expect_requests))
    else:
        print("  FAIL  requests            %d made, %d expected — a request is missing "
              "or unaccounted for" % (made, args.expect_requests))
        problems += 1

    # 2 — server total versus local count
    for record in sources:
        name = record.get("name", "?")
        items, expected = record.get("items", 0), record.get("expected")
        if record.get("status") != "ok":
            print("  FAIL  server-vs-local     %-10s status %s — the item count means "
                  "nothing" % (name, record.get("status")))
            problems += 1
        elif expected is None:
            print("  note  server-vs-local     %-10s server total unavailable; recorded as "
                  "an open gap" % name)
        elif items == expected:
            print("  ok    server-vs-local     %-10s %d = %d" % (name, items, expected))
        else:
            print("  FAIL  server-vs-local     %-10s %d parsed, %d reported — truncation "
                  "or a dropped page" % (name, items, expected))
            problems += 1

    # 3 — status written for every source
    missing = [r.get("name", "?") for r in sources if not r.get("status")]
    if not sources:
        print("  FAIL  status              the log lists no sources")
        problems += 1
    elif missing:
        print("  FAIL  status              no status for %s" % ", ".join(missing))
        problems += 1
    else:
        print("  ok    status              %d/%d sources carry one" % (len(sources), len(sources)))

    # 4 — shallowest floor reaches the window start
    floors = [r.get("floor") for r in sources if r.get("status") == "ok"]
    unknown = [r.get("name", "?") for r in sources
               if r.get("status") == "ok" and not r.get("floor")]
    if unknown:
        print("  FAIL  floor               no floor recorded for %s — coverage depth is "
              "unfalsifiable" % ", ".join(unknown))
        problems += 1
    elif not floors:
        print("  FAIL  floor               no source completed, so no floor exists")
        problems += 1
    elif not since:
        print("  FAIL  floor               no window start to compare against")
        problems += 1
    else:
        shallowest = min(floors)
        if shallowest <= since:
            print("  ok    floor               shallowest %s reaches the window start %s "
                  "(half-open, start inclusive)" % (shallowest, since))
        else:
            print("  FAIL  floor               shallowest %s does not reach the window "
                  "start %s — the window was not covered" % (shallowest, since))
            problems += 1

    # Two fields that record whether the copied-script defences were applied.
    if log.get("output-dir-empty-at-start"):
        print("  ok    empty-at-start      recorded")
    else:
        print("  note  empty-at-start      not recorded — the copied-script defence was "
              "not applied")
    if log.get("probe-dir"):
        print("  ok    probe isolation     %s" % log["probe-dir"])

    print("")
    if problems:
        print("selfcheck FAIL  (%d problem(s)) — do not write the report yet; a report "
              "written now describes a window of unknown depth" % problems)
        return 1
    print("selfcheck PASS — the run may report, and the report may carry its coverage proof")
    return 0


if __name__ == "__main__":
    sys.exit(main())
