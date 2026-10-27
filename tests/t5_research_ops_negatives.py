#!/usr/bin/env python3
"""T5 — the three negative fixtures for `research-ops`.

`research-ops/SKILL.md` ends with three prompts that must *not* route to
research-ops, each with the correct destination. That table is only useful if it
is checked: a description edit that makes one of these prompts plausible is
exactly the failure the table exists to prevent, and nothing about editing a
description feels risky at the time.

What is asserted, per fixture:

  1  the prompt appears verbatim in `research-ops/SKILL.md` — the fixture and the
     document cannot drift apart;
  2  the prompt's row names the expected destination (`*no skill*` for the third);
  3  the destination skill exists, and its `description` carries the capability
     keywords the prompt is about — a router can only route somewhere that
     advertises the job;
  4  `research-ops`' own description states an explicit exclusion clause.

Limitation, stated plainly: this checks the fixture table and the vocabulary of
the descriptions. It does not, and cannot, run a model to see where a prompt
actually goes. The honest claim is "the document still says what the test says it
says, and the destinations still advertise the work" — not "routing is verified".

Requires: Python >= 3.8 (stdlib only).
Exit: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OPS_SKILL = SKILLS / "research-ops" / "SKILL.md"

# (prompt, expected destination folder or None, capability keywords)
FIXTURES = (
    ("Turn this PDF into a card with provenance", "paper-card", ("pdf", "card")),
    ("Compare these six cards on one axis", "synthesis-matrix", ("card", "axis")),
    ("Keep notes on what I read this week", None, ()),
)


def read_description(skill_dir):
    """Return the folded `description` block of a SKILL.md as one string."""
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    out, inside = [], False
    for raw in lines[1:]:
        if raw.strip() == "---":
            break
        if raw.startswith("description:"):
            rest = raw[len("description:"):].strip()
            if rest in (">", ">-", "|", "|-"):
                inside = True
                continue
            return rest
        if inside:
            if raw.strip() and not raw[:1].isspace():
                break
            out.append(raw.strip())
    return " ".join(p for p in out if p) or None


def short(text, width=38):
    return text if len(text) <= width else text[:width - 3] + "..."


def row_for(text, prompt):
    for line in text.splitlines():
        if prompt in line and line.lstrip().startswith("|"):
            return line
    return None


def main():
    print("T5  research-ops negative fixtures")

    if not OPS_SKILL.is_file():
        print("  FAIL  missing %s" % OPS_SKILL)
        print("T5  FAIL")
        return 1
    text = OPS_SKILL.read_text(encoding="utf-8")
    problems = 0

    if "regression fixtures" not in text:
        print("  FAIL  the table no longer calls itself regression fixtures — "
              "this test and the document have drifted apart")
        problems += 1
    else:
        print("  ok    document labels the table as regression fixtures")

    ops_desc = read_description(SKILLS / "research-ops") or ""
    if "do not use for" in ops_desc.lower():
        print("  ok    research-ops description carries an exclusion clause")
    else:
        print("  FAIL  research-ops description has no \"Do not use for\" clause — "
              "without it, nothing keeps adjacent prompts out")
        problems += 1

    for prompt, target, keywords in FIXTURES:
        row = row_for(text, prompt)
        if row is None:
            print("  FAIL  fixture missing from SKILL.md: %r" % prompt)
            problems += 1
            continue

        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) != 3:
            print("  FAIL  row for %r has %d cells, expected 3" % (prompt, len(cells)))
            problems += 1
            continue

        route = cells[1]
        if target is None:
            if "no skill" not in route.lower():
                print("  FAIL  %r should route to *no skill*, row says %r"
                      % (prompt, route))
                problems += 1
            else:
                print("  ok    %-42s -> no skill" % short(prompt))
            continue

        if target not in route:
            print("  FAIL  %r routes to %r, expected %s" % (prompt, route, target))
            problems += 1
            continue

        skill_dir = SKILLS / target
        desc = read_description(skill_dir)
        if desc is None:
            print("  FAIL  %s has no readable description" % target)
            problems += 1
            continue

        low = desc.lower()
        missing = [k for k in keywords if k not in low]
        if missing:
            print("  FAIL  %s description does not mention %s — the destination "
                  "no longer advertises this job" % (target, missing))
            problems += 1
        else:
            print("  ok    %-42s -> %s (%s)"
                  % (short(prompt), target, ", ".join(keywords)))

    print("T5  %s" % ("FAIL" if problems else "PASS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
