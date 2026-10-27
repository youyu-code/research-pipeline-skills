#!/usr/bin/env python3
"""T1 — SKILL.md frontmatter conformance (Anthropic Agent Skills format).

For every folder under `skills/` that contains a `SKILL.md`:

  name          present, identical to the folder name, <= 64 characters,
                only `[a-z0-9-]`, no leading/trailing hyphen, no double hyphen
  description   present, <= 1024 characters
  structure     states a trigger ("use when"), an input, and an output — the
                M2 red line: when to call it + what goes in + what comes out
  voice         no marketing adjective (a small banned list)

The `name` rules are not stylistic: a mismatch between the frontmatter and the
folder name is how a skill silently fails to load.

Requires: Python >= 3.8 (stdlib only).
Exit: 0 = pass, 1 = at least one skill non-conformant.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESC = 1024

BANNED = (
    "powerful", "seamless", "revolutionary", "cutting-edge", "best-in-class",
    "effortless", "game-changing", "unparalleled", "unparallelled", "world-class",
    "blazing", "supercharge", "state-of-the-art",
)

TRIGGERS = ("use when", "use it when", "use this when")


def split_frontmatter(text):
    """Return the lines between the first pair of `---` fences, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def read_field(lines, key):
    """Read a scalar or a folded block (`>-`) value for a top-level key."""
    prefix = key + ":"
    for i, raw in enumerate(lines):
        if not raw.startswith(prefix):
            continue
        rest = raw[len(prefix):].strip()
        if rest in (">", ">-", "|", "|-", ">+", "|+"):
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt[:1].isspace():
                    break
                block.append(nxt.strip())
            return " ".join(part for part in block if part)
        return rest
    return None


def check_skill(folder):
    problems = []
    path = folder / "SKILL.md"
    text = path.read_text(encoding="utf-8")

    lines = split_frontmatter(text)
    if lines is None:
        return None, ["SKILL.md does not start with a `---` frontmatter fence"]

    name = read_field(lines, "name")
    desc = read_field(lines, "description")

    if not name:
        problems.append("`name` missing or empty")
    else:
        if name != folder.name:
            problems.append("name %r != folder %r" % (name, folder.name))
        if len(name) > MAX_NAME:
            problems.append("name is %d chars (max %d)" % (len(name), MAX_NAME))
        if not NAME_RE.match(name):
            problems.append("name %r is not [a-z0-9-] with single hyphens" % name)

    if not desc:
        problems.append("`description` missing or empty")
    else:
        if len(desc) > MAX_DESC:
            problems.append("description is %d chars (max %d)" % (len(desc), MAX_DESC))
        low = desc.lower()
        if not any(t in low for t in TRIGGERS):
            problems.append('description states no trigger ("Use when ...")')
        if "input:" not in low:
            problems.append('description states no "Input:" clause')
        if "output:" not in low:
            problems.append('description states no "Output:" clause')
        for word in BANNED:
            if word in low:
                problems.append("description contains marketing word %r" % word)

    return (name, len(desc or "")), problems


def main():
    print("T1  frontmatter conformance")
    if not SKILLS.is_dir():
        print("  FAIL  no skills/ directory at %s" % SKILLS)
        return 1

    folders = sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    if not folders:
        print("  FAIL  no skill folder contains a SKILL.md")
        return 1

    failed = 0
    for folder in folders:
        info, problems = check_skill(folder)
        if problems:
            failed += 1
            print("  FAIL  %-20s %s" % (folder.name, problems[0]))
            for extra in problems[1:]:
                print("        %-20s %s" % ("", extra))
        else:
            print("  ok    %-20s name=%s desc=%d chars"
                  % (folder.name, info[0], info[1]))

    print("T1  %s  (%d skill(s), %d non-conformant)"
          % ("FAIL" if failed else "PASS", len(folders), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
