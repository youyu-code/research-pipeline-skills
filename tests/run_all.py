#!/usr/bin/env python3
"""Run the whole suite with one command.

    python tests/run_all.py          # everything
    python tests/run_all.py -v       # echo each test's full output
    python tests/run_all.py -k t3    # subset, matched on filename

Contracts for every test in this folder:

  * it is a standalone script, runnable on its own;
  * it exits 0 on pass, 1 on failure, 77 on skip;
  * it prints one line per check, prefixed `ok` / `FAIL` / `SKIP`.

A skip means an *optional* dependency is absent (pypdf, pymupdf). Skips are
listed separately in the summary so a green run cannot quietly be a run that
checked nothing.

Nothing here is new capability. Every check is an assertion about behaviour the
skills already claim in prose — mechanised so that a change which breaks a claim
breaks the build instead of the next reader.

Release gate: this script exits 0 and prints ALL GREEN. That is the whole gate;
there is no second checklist.

Requires: Python >= 3.8 (stdlib only).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent

PASS, FAIL, SKIP = 0, 1, 77


def discover(pattern):
    found = []
    for path in sorted(TESTS.glob("t[0-9]*_*.py")):
        if pattern and pattern not in path.name:
            continue
        found.append(path)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(prog="run_all.py",
                                 description="Run every test in this folder.")
    ap.add_argument("-k", dest="pattern", default=None,
                    help="only tests whose filename contains this substring")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="echo the full output of each test")
    args = ap.parse_args(argv)

    tests = discover(args.pattern)
    if not tests:
        print("no test matched %r" % args.pattern)
        return FAIL

    print("research-pipeline-skills — test suite")
    print("root: %s" % ROOT)
    print("")

    passed, failed, skipped = [], [], []
    started = time.time()

    for path in tests:
        proc = subprocess.run([sys.executable, str(path)],
                              cwd=str(ROOT),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              text=True)
        out = proc.stdout.rstrip()
        lines = out.splitlines()
        if args.verbose or proc.returncode == FAIL:
            if out:
                print(out)
        else:
            print(lines[0] if lines else path.stem)

        if proc.returncode == PASS:
            passed.append(path.stem)
        elif proc.returncode == SKIP:
            skipped.append(path.stem)
        else:
            failed.append(path.stem)

    elapsed = time.time() - started
    total = len(tests)
    print("")
    print("%d test(s) in %.1fs — %d passed, %d skipped, %d failed"
          % (total, elapsed, len(passed), len(skipped), len(failed)))
    if skipped:
        print("SKIPPED (optional dependency absent): %s" % ", ".join(skipped))
    if failed:
        print("FAILED: %s" % ", ".join(failed))
        return FAIL
    print("ALL GREEN")
    return PASS


if __name__ == "__main__":
    sys.exit(main())
