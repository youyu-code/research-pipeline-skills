#!/usr/bin/env python3
"""T4b — nothing private may remain in the repository's history.

`git log --all -p` every commit and scan the lines that were **added**. A value
that was committed once and deleted later is still published: cloning the
repository and running `git log -p` prints it. T4a cannot see it, because T4a
reads the working tree.

Same pattern table as T4a, from `_desens.py`, because two copies of a blacklist
diverge and the copy nobody reads is the one that matters.

Three properties worth stating, since each was a way this test could lie:

  1  **Unique commits.** `--all -p` prints a commit once per path that reaches
     it, so the same patch can appear many times. Commits are filtered by hash
     before scanning, and the count of unique commits is printed.
  2  **Nothing scanned is not a pass.** If the diff yields zero added lines the
     test fails rather than passing quietly: an empty scan looks exactly like a
     clean repository.
  3  **The canary runs here too.** The scanner is proven on planted values
     before the history is trusted.

Exit: 0 = pass, 1 = fail, 77 = skip (no git, or an empty history).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _desens import (  # noqa: E402
    BLACKLIST, USER_TOKEN, canary, git, is_scanner_source, load_blacklist, scan_line,
)

MAX_REPORT = 40


def history_patch() -> tuple:
    code, out = git("log", "--all", "-p", "--no-color", "--unified=0",
                    "--format=commit %H %h %ad %s", "--date=short")
    return code, out.decode("utf-8", "replace")


def main() -> int:
    print("T4b  desensitisation scan (history)")

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
        print("T4b  FAIL")
        return 1
    print("  ok    scanner canary           planted leak detected%s"
          % ("" if USER_TOKEN else " (class 3 skipped: no account name derivable)"))

    code, patch = history_patch()
    if code != 0:
        print("  SKIP  history                  git log unavailable — history not scanned")
        print("T4b  SKIP")
        return 77

    commits_seen = set()
    added = 0
    current_commit = ("", "")
    current_file = ""
    problems = []
    allowed = 0

    for line in patch.splitlines():
        if line.startswith("commit "):
            match = re.match(r"^commit ([0-9a-f]{40}) ([0-9a-f]{7,})", line)
            if match:
                current_commit = (match.group(1), match.group(2))
                commits_seen.add(current_commit[1])
            continue
        if line.startswith("+++ "):
            target = line[4:].strip()
            current_file = target[2:] if target.startswith("b/") else target
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added += 1
        body = line[1:]
        for cls, label, excerpt in scan_line(body, blacklist,
                                             not is_scanner_source(current_file)):
            if cls == "*":
                allowed += 1
                continue
            problems.append((current_commit[1], current_file, cls, label, excerpt))

    print("  ok    history                  %d unique commit(s), %d added line(s)"
          % (len(commits_seen), added))

    if added == 0:
        print("  FAIL  history                  no added line was scanned; an empty "
              "scan is indistinguishable from a clean one")
        print("T4b  FAIL")
        return 1

    if allowed:
        print("  note  %d added line(s) carry the allow marker" % allowed)

    if problems:
        for short, path, cls, label, excerpt in problems[:MAX_REPORT]:
            print("  FAIL  [%s] %-34s %s %s  %s" % (cls, label, short, path, excerpt))
        if len(problems) > MAX_REPORT:
            print("  ...   %d more hit(s) not printed" % (len(problems) - MAX_REPORT))
        print("T4b  FAIL  (%d hit(s) across %d unique commit(s))"
              % (len(problems), len(commits_seen)))
        return 1

    print("  ok    scan                     no hit in %d added line(s) across %d commit(s)"
          % (added, len(commits_seen)))
    print("T4b  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
