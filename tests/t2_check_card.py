#!/usr/bin/env python3
"""T2 — check_card.py, both paths.

The card schema is only a contract if something enforces it. This test asserts
both directions of the enforcer:

  positive   the shipped demo card passes, and the number of values carrying
             provenance is the number the fixture claims (9)
  negative   a card with three known defects fails with exit 3, prints one line
             per violation, and yields exactly the pinned count (4: renaming the
             §5 heading breaks both the name check and the order check)

The broken card is derived from the good one by three string substitutions, not
shipped as a second fixture. A second fixture drifts: someone edits the schema,
updates the demo, forgets the broken copy, and the negative path quietly starts
testing an obsolete card. Deriving it means the negative case cannot fall out of
sync — and if a substitution stops applying, this test fails rather than passing
vacuously.

Requires: Python >= 3.8 (stdlib only).
Exit: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "paper-card" / "scripts" / "check_card.py"
CARD = ROOT / "skills" / "paper-card" / "assets" / "samples" / "demo2026_pipeline-selftest.md"

EXPECTED_VALUES = 9

# (whole line, replacement, what it breaks). Each line must occur exactly once.
# Matched on the whole line, not on a substring: the fixture also quotes
# `version: preprint` inside its own self-check paragraph, and a substring match
# would mutate the prose instead of the frontmatter.
MUTATIONS = (
    ("version: preprint", "version: draft", "version outside the enum"),
    ("si-state: independent", "si-state: maybe", "si-state outside the enum"),
    ("## §5 Results", "## §5 Result", "section heading no longer matches §5"),
)

# Pinned after the first green run; see the header for why it is pinned at all.
EXPECTED_VIOLATIONS = 4


def run(card_path):
    proc = subprocess.run([sys.executable, str(SCRIPT), str(card_path)],
                          cwd=str(ROOT),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text=True)
    return proc.returncode, proc.stdout


def main():
    print("T2  check_card.py — positive and negative path")

    if not SCRIPT.is_file():
        print("  FAIL  missing script: %s" % SCRIPT)
        return 1
    if not CARD.is_file():
        print("  FAIL  missing fixture: %s" % CARD)
        return 1

    problems = 0

    # ---- positive path -----------------------------------------------------
    code, out = run(CARD)
    if code != 0:
        print("  FAIL  demo card rejected (exit %d)" % code)
        for line in out.splitlines():
            print("        " + line)
        problems += 1
    else:
        match = re.search(r"\((\d+) value\(s\) with provenance\)", out)
        if not match:
            print("  FAIL  demo card passed but the count line is unparsable")
            problems += 1
        elif int(match.group(1)) != EXPECTED_VALUES:
            print("  FAIL  demo card reports %s provenance values, expected %d"
                  % (match.group(1), EXPECTED_VALUES))
            problems += 1
        else:
            print("  ok    demo card PASS, %d value(s) with provenance" % EXPECTED_VALUES)

    # ---- negative path ----------------------------------------------------
    lines = CARD.read_text(encoding="utf-8").splitlines(True)
    broken = list(lines)
    bad = False
    for old, new, why in MUTATIONS:
        hits = [i for i, ln in enumerate(broken) if ln.rstrip("\r\n") == old]
        if len(hits) != 1:
            print("  FAIL  mutation target %r matches %d line(s) (expected 1) — "
                  "the fixture moved under this test" % (old, len(hits)))
            problems += 1
            bad = True
            continue
        indent = ""
        broken[hits[0]] = indent + new + "\n"

    if bad:
        print("T2  FAIL  (fixture drifted; negative path not exercised)")
        return 1

    with tempfile.TemporaryDirectory(prefix="pc-t2-") as tmp:
        broken_path = Path(tmp) / CARD.name  # same stem: `id` must match it
        broken_path.write_text("".join(broken), encoding="utf-8")
        code, out = run(broken_path)

        if code != 3:
            print("  FAIL  broken card exited %d, expected 3" % code)
            for line in out.splitlines():
                print("        " + line)
            problems += 1
        else:
            violations = [ln for ln in out.splitlines() if ln.strip()]
            # The first line is the FAIL summary; the rest are violations.
            body = [ln for ln in violations if not ln.startswith("FAIL")]
            if len(body) != EXPECTED_VIOLATIONS:
                print("  FAIL  broken card yielded %d violation line(s), pinned at %d"
                      % (len(body), EXPECTED_VIOLATIONS))
                for line in body:
                    print("        " + line)
                problems += 1
            else:
                print("  ok    broken card FAIL, %d violation(s): %s"
                      % (len(body), "; ".join(m[2] for m in MUTATIONS)))

    print("T2  %s" % ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
