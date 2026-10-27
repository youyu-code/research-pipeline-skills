#!/usr/bin/env python3
"""Fetch one window from an Atom endpoint into a scan directory.

    scan.py --out _out/2026-01-07 --since 2026-01-01
    scan.py --out _out/2026-01-07 --since 2026-01-01 --source cs.LG --source cs.AI
    scan.py --out _out/2026-01-07 --since 2026-01-01 --config my-sources.json
    scan.py --out _out/replay --since 2026-01-01 --corpus samples/raw

Input: a window `[since, until)`, a list of sources, and optionally a config.
Output: one Atom file per source plus `_scan.json`, the run log `selfcheck.py`
reads.

**The window is half-open.** `[since, until)`: the start date is included, the
end date is not, so two consecutive runs cannot both claim the boundary date.
The end defaults to today (UTC) and is recorded in the log, because "now" means
the query time, not the time the report was written.

The API's date clause is **inclusive on both ends**, so the upper bound sent
over the wire is `until - 1 day 23:59`. The exact URL is recorded per source in
the run log: after the fact it is the only object that can tell a half-open
window from a closed one, because both look identical in a report.

**Each source carries a floor.** The floor is how far back that source was
actually walked — `since` unless the source config sets its own. It is recorded
per source, because a feed added yesterday cannot cover a window that starts last
month, and a run that reports "full coverage" over such a source has covered the
window on paper only. `selfcheck.py` compares every floor against the window
start; the earliest item date is recorded beside it as `oldest-item`, which is a
different fact (a quiet window has a late oldest item and full coverage).

**The transport lies in three ways, and this script is built around each.**

  429 — you are being limited. The wait is a measurement, not a parameter: start
        with none, wait `--retry-wait` once, and if the second attempt is also
        429 stop and report `limited`. No staircase. Each extra rung costs a
        round trip plus the wait, and a source that limits aggressively will 429
        at every one of them. A wait inherited from someone else's notes is not
        a measurement and must not be logged as one.

  000 — the connection never completed. This is *not* rate limiting, and waiting
        on it burns the full backoff and then fails again. The record says
        `unreachable` with the triage to run: check proxy variables, then test a
        second resolved address for the same host. Throttling answers; a connect
        timeout does not.

  200 — the body parsed, and it can still be short. A truncated payload has no
        error status: it has fewer items than the server reports for the same
        query. The only reliable check is count reconciliation, which is why
        every fetch here compares the parsed entry count with
        `opensearch:totalResults` and records `truncated` when they differ. A
        payload-size heuristic is a secondary signal at best; a round byte count
        proves nothing on its own.

Downloads go to a temporary file inside the output directory and are moved into
place only after they parse and reconcile. A partially written file that is
later read as complete is the exact silent failure this skill exists to prevent.

**The output directory must be empty.** A copied script that writes into last
period's directory finds existing output and reports success; refusing a
non-empty directory is what makes that failure impossible rather than unlikely.
`--allow-nonempty` exists for deliberate re-runs and forfeits that defence.

**Probes go to `_probe/`.** The directory is created on every run so the
convention is visible, and nothing else ever writes into it.

`--corpus DIR` replays Atom files already on disk instead of fetching. That is
the offline path: same reconciliation, same log, no network. Use it in tests and
in any environment where the endpoint is unreachable.

Requires: Python >= 3.8 (standard library only; `urllib` for the fetch).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ATOM = "{http://www.w3.org/2005/Atom}"
OS_NS = "{http://a9.com/-/spec/opensearch/1.1/}"
BASE_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "research-pipeline-skills/1.0 (+literature-radar)"

# Generic public arXiv categories. A real profile replaces these with its own
# sources; no topic-specific list ships in this repository.
DEFAULT_SOURCES = (
    {"name": "cs.LG", "query": "cat:cs.LG"},
    {"name": "cs.AI", "query": "cat:cs.AI"},
    {"name": "stat.ML", "query": "cat:stat.ML"},
)

EXIT_OK, EXIT_REFUSED, EXIT_PARTIAL = 0, 3, 4


def utc_today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def stamp(date_text, hhmm):
    return date_text.replace("-", "") + hhmm


def build_url(base, query, since, until_excl, max_results):
    """One constrained query: the category and the date clause, nothing else.

    Compound queries with OR groups do not reliably apply their remaining
    constraints, and the returned total then describes a different question.

    The date clause is expressed in the API's inclusive day syntax, so the
    half-open window `[since, until_excl)` becomes `[since 00:00, until_excl-1
    23:59]`. Writing `until_excl 23:59` here — which this function did once —
    asks for one extra day and quietly makes the window closed on the right.
    """
    end = datetime.strptime(until_excl, "%Y-%m-%d").date() - timedelta(days=1)
    search = "%s AND submittedDate:[%s TO %s]" % (query, stamp(since, "0000"),
                                                  stamp(end.isoformat(), "2359"))
    params = urllib.parse.urlencode(
        {"search_query": search, "start": 0, "max_results": max_results,
         "sortBy": "submittedDate", "sortOrder": "ascending"},
        quote_via=urllib.parse.quote)
    return base + "?" + params


def parse_feed(payload):
    """Return (count, expected, entries) or raise ValueError with the reason."""
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("body does not parse: %s" % exc)
    entries = root.findall(ATOM + "entry")
    total = root.find(OS_NS + "totalResults")
    expected = None
    if total is not None and (total.text or "").strip().isdigit():
        expected = int(total.text.strip())
    return len(entries), expected, entries


def deepest_date(entries):
    dates = []
    for entry in entries:
        node = entry.find(ATOM + "published")
        if node is not None and node.text:
            dates.append(node.text.strip()[:10])
    return min(dates) if dates else None


def fetch(url, max_time):
    """One request. Returns (status, http, payload, note)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=max_time) as response:
            return "ok", response.getcode(), response.read(), ""
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return "limited", 429, b"", "rate limited"
        return "failed", exc.code, b"", "HTTP %s" % exc.code
    except urllib.error.URLError as exc:
        return "unreachable", 0, b"", str(getattr(exc, "reason", exc))
    except Exception as exc:                                   # socket timeouts
        return "unreachable", 0, b"", "%s: %s" % (type(exc).__name__, exc)


def resolve_sources(args, cfg):
    if args.source:
        out = []
        for item in args.source:
            if "=" in item:
                name, query = item.split("=", 1)
            else:
                name, query = item, "cat:" + item
            out.append({"name": name.strip(), "query": query.strip()})
        return out
    if cfg and cfg.get("sources"):
        return [dict(s) for s in cfg["sources"]]
    return [dict(s) for s in DEFAULT_SOURCES]


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="scan.py",
        description="Fetch a half-open date window from an Atom endpoint into an "
                    "output directory, with count reconciliation and a run log.")
    ap.add_argument("--out", required=True,
                    help="output directory; must be empty unless --allow-nonempty")
    ap.add_argument("--since", required=True,
                    help="window start, inclusive (YYYY-MM-DD)")
    ap.add_argument("--until", default=None,
                    help="window end, exclusive (YYYY-MM-DD); default is today (UTC)")
    ap.add_argument("--source", action="append", metavar="CATEGORY|=QUERY",
                    help="source to fetch, repeatable; `cs.LG` means `cat:cs.LG`, "
                         "or pass `name=query`")
    ap.add_argument("--max-results", type=int, default=None,
                    help="fixed page size, requested explicitly (default 200)")
    ap.add_argument("--max-time", type=int, default=None,
                    help="per-request timeout in seconds (default 500)")
    ap.add_argument("--init-wait", type=int, default=None,
                    help="seconds to wait before the first request (default 0)")
    ap.add_argument("--retry-wait", type=int, default=None,
                    help="seconds to wait before the single retry after a 429 (default 60)")
    ap.add_argument("--config", help="JSON config with `sources` and `request` sections")
    ap.add_argument("--corpus", help="offline mode: replay Atom files from this directory, "
                                     "one <source>.xml per source; no network")
    ap.add_argument("--base-url", default=BASE_URL, help="Atom endpoint (default: arXiv)")
    ap.add_argument("--allow-nonempty", action="store_true",
                    help="write into a non-empty directory; forfeits the copied-script defence")
    args = ap.parse_args(argv)

    cfg = {}
    if args.config:
        cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    request_cfg = cfg.get("request", {})
    max_results = args.max_results or int(request_cfg.get("max-results", 200))
    max_time = args.max_time or int(request_cfg.get("max-time", 500))
    init_wait = args.init_wait if args.init_wait is not None else int(request_cfg.get("init-wait", 0))
    retry_wait = args.retry_wait if args.retry_wait is not None else int(request_cfg.get("retry-wait", 60))
    until = args.until or utc_today()
    if until <= args.since:
        ap.error("--until (%s) must be after --since (%s): the window is half-open "
                 "[since, until), so an empty window has no query to make"
                 % (until, args.since))

    out = Path(args.out)
    if out.exists() and any(out.iterdir()) and not args.allow_nonempty:
        print("scan.py — refusing to write into a non-empty directory")
        print("  %s" % out)
        print("  A run that finds existing output and calls it success is the failure this")
        print("  check exists for. Use a new directory, or --allow-nonempty if you mean it.")
        return EXIT_REFUSED

    out.mkdir(parents=True, exist_ok=True)
    (out / "_probe").mkdir(exist_ok=True)

    sources = resolve_sources(args, cfg)
    print("scan.py — %s" % out)
    print("  window   [%s, %s)" % (args.since, until))
    print("  mode     %s" % ("offline replay from " + args.corpus if args.corpus
                             else args.base_url))
    print("  sources  %s" % ", ".join(s["name"] for s in sources))

    if init_wait:
        print("  wait     %ds before the first request (measured for this client, not inherited)"
              % init_wait)
        time.sleep(init_wait)

    records, requests_made = [], 0
    for source in sources:
        name = source["name"]
        # A source may carry its own floor: a feed added yesterday cannot reach a
        # window that starts last month, and pretending otherwise is how a run
        # reports full coverage over a source it has only read for two days.
        floor = source.get("floor") or args.since
        status, http, payload, note = "failed", 0, b"", ""
        tries = 0
        waited = 0
        url = build_url(args.base_url, source["query"], floor, until, max_results)

        if args.corpus:
            origin = Path(args.corpus) / (name + ".xml")
            requests_made += 1
            tries = 1
            if not origin.is_file():
                print("  FAIL  %-10s not in corpus: %s" % (name, origin))
                records.append({"name": name, "status": "unreachable", "http": 0,
                                "items": 0, "expected": None, "requests": 1,
                                "waited": 0, "floor": floor, "oldest-item": None,
                                "bytes": 0, "file": None, "url": url,
                                "note": "corpus file missing"})
                continue
            payload = origin.read_bytes()
            status, http = "ok", 200
        else:
            status, http, payload, note = fetch(url, max_time)
            requests_made += 1
            tries = 1
            if status == "limited":
                print("  wait  %-10s 429; one retry after %ds (no staircase)" % (name, retry_wait))
                time.sleep(retry_wait)
                waited = retry_wait
                status, http, payload, note = fetch(url, max_time)
                requests_made += 1
                tries = 2
                if status == "limited":
                    note = "429 twice — stop, do not staircase; the limit is not the problem"

        items, expected, entries = 0, None, []
        if status == "ok":
            try:
                items, expected, entries = parse_feed(payload)
            except ValueError as exc:
                status, note = "truncated", str(exc)
            else:
                if expected is not None and items < expected:
                    status = "truncated"
                    note = "%d of %d entries — count reconciliation failed" % (items, expected)

        target = None
        if status == "ok":
            target = out / (name + ".xml")
            part = out / (".part-" + name)
            part.write_bytes(payload)
            os.replace(part, target)

        oldest = deepest_date(entries) if entries else None
        records.append({
            "name": name, "status": status, "http": http, "items": items,
            "expected": expected, "requests": tries, "waited": waited,
            "floor": floor, "oldest-item": oldest, "bytes": len(payload),
            "file": target.name if target else None, "url": url, "note": note,
        })
        print("  %-5s %-10s http=%-3s items=%-4s expected=%-4s floor=%s oldest=%s%s"
              % ("ok" if status == "ok" else "FAIL", name, http or "000", items,
                 expected if expected is not None else "-", floor, oldest or "-",
                 "" if not note else "  (" + note + ")"))

    log = {
        "window": {"since": args.since, "until": until, "interval": "half-open [since, until)"},
        "mode": "corpus" if args.corpus else "network",
        "sources": records,
        "requests-made": requests_made,
        "loops": 1,
        "output-dir-empty-at-start": not args.allow_nonempty,
        "probe-dir": "_probe/",
        "max-results": max_results,
        "max-time": max_time,
    }
    (out / "_scan.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")

    bad = [r for r in records if r["status"] != "ok"]
    print("")
    print("  requests %d · sources ok %d/%d · log %s"
          % (requests_made, len(records) - len(bad), len(records), out / "_scan.json"))
    if bad:
        print("  next: run selfcheck.py --out %s --expect-requests %d, then read the"
              % (out, requests_made))
        print("        per-source status before writing any report line.")
        return EXIT_PARTIAL
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
