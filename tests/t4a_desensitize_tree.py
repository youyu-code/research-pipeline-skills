#!/usr/bin/env python3
"""T4a — nothing private may be committed, in the working tree.

Scans every tracked file for the five classes that must never reach a public
repository, plus an optional fingerprint blacklist:

  1  Zotero credentials        API key, userID, `zotero://` deep-link URIs
  2  Zotero library names      a *named* library or collection in a config-like form
  3  the author's account name the local account name of the machine running the
                               test, derived at runtime via `getpass`; this file
                               never contains it. When no name can be derived the
                               class is skipped and the skip is printed
  4  absolute paths            drive letters, /Users/, /home/<name>
  5  session identifiers       timestamped directory names, `_scanMMDD`-style runs
  F  fingerprints              values lifted from private source material; the
                               list is *not* in the repository (see below)

The split with T4b
    This test reads what is in the tree *now*. T4b reads every line ever added,
    which is where a value that was removed but never rewritten still lives.
    Neither is sufficient alone: a clean tree over a dirty history publishes the
    history the moment anyone clones, and the history scan cannot see a file
    that was never committed.

A hit can be legitimate (documentation that quotes a path as an example). Mark
the line with `desens:allow` and a reason; the marker is honoured, counted, and
printed, so it is a visible decision rather than an invisible exception.

Requires: Python >= 3.8 (stdlib only). Uses `git ls-files` when available and
falls back to a directory walk.
Exit: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _desens import (  # noqa: E402
    BLACKLIST, ROOT, USER_TOKEN, canary, is_scanner_source, load_blacklist, read_text,
    scan_text, tracked_files,
)


def main() -> int:
    print("T4a  desensitisation scan (working tree)")

    blacklist = load_blacklist()
    if blacklist is None:
        print("  SKIP  fingerprint blacklist    tests/fingerprints.local.txt absent "
              "(maintainer-local, gitignored)")
    else:
        print("  ok    fingerprint blacklist    %d pattern(s) loaded" % len(blacklist))

    missing = canary(blacklist)
    if missing:
        print("  FAIL  scanner canary           missed class(es) %s — the scan "
              "below would be meaningless" % ",".join(sorted(missing)))
        print("T4a  FAIL")
        return 1
    if USER_TOKEN:
        print("  ok    scanner canary           planted leak detected in every class")
    else:
        print("  ok    scanner canary           planted leak detected in classes 1/4/5 "
              "and the fingerprint probe; class 3 skipped")
        print("  SKIP  account-name check       no local account name could be derived "
              "(getpass empty, USERNAME/USER unset) — class 3 not scanned")

    files, how = tracked_files()
    print("  ok    input                    %d file(s) via %s" % (len(files), how))

    problems = []
    allowed = []
    exempt = []
    for path in files:
        if path.name == BLACKLIST.name:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if is_scanner_source(rel):
            exempt.append(rel)
        for cls, label, line_no, excerpt in scan_text(read_text(path), blacklist,
                                                      not is_scanner_source(rel)):
            if cls == "*":
                allowed.append("%s:%d" % (rel, line_no))
            else:
                problems.append((cls, rel, line_no, label, excerpt))

    if exempt:
        print("  note  %d scanner source file(s) exempt from the pattern classes "
              "(they define the patterns); still scanned for fingerprints" % len(exempt))

    if allowed:
        print("  note  %d line(s) carry the allow marker: %s"
              % (len(allowed), ", ".join(allowed[:6])))

    if problems:
        for cls, rel, line_no, label, excerpt in problems:
            print("  FAIL  [%s] %-38s %s:%d  %s" % (cls, label, rel, line_no, excerpt))
        print("T4a  FAIL  (%d hit(s) in %d file(s))" % (len(problems), len(files)))
        return 1

    print("  ok    scan                     no hit in %d file(s)%s"
          % (len(files), "" if USER_TOKEN else " — class 3 was skipped"))
    print("T4a  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
