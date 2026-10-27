#!/usr/bin/env python3
"""Verify a hash manifest of input files, before and after a run.

    check-sources.py --manifest sources.sha256 --root ./inputs
    check-sources.py --manifest state.sha256 --root . --class state

Exit: 0 = every entry matches (clean)
      1 = at least one `readonly` mismatch — this is the B5 stop
      2 = at least one `state` mismatch — attribute, re-pin, re-verify

**Why this exists.** "I did not write to the read-only corpus" is a claim, and a
claim with no carrier is indistinguishable from a memory. The manifest is the
carrier: relative paths plus truncated hashes, checked before the analysis (so
the numbers have a known basis) and again after it (so a write during the run is
caught). Without the second check, a corpus edited mid-run produces a report
about a corpus that never existed.

**Two classes, two verdicts.** The same mismatch means different things
depending on who may write the file:

  readonly   inputs you never write — a source corpus, a borrowed directory,
             reference PDFs. A mismatch means something outside the pipeline
             wrote to an input. The run stops: the analysis that already read
             the file has no known basis. Re-pinning is allowed only after the
             change is attributed, and the new entry carries the date and the
             reason.
  state      files the pipeline itself writes — cursor, push log, profile, the
             manifest. A mismatch is expected between two checks. It is
             answered by attribution and a dated re-pin, then by re-running the
             check; it is not a stop.

A single-verdict manifest fails in one of two directions. Make every mismatch a
stop, and the first routine cursor advance teaches the operator to override the
check. Make every mismatch a warning, and a write to a read-only input is logged
and forgotten. The class is what keeps "stop" meaningful.

Manifest format, one entry per line:

    <hex digest, 16 chars typical>  <path relative to --root>  [class]

Two spaces between digest and path (the `sha256sum` shape). Blank lines and
`#` comments are ignored. An optional `class` column overrides `--class` for that
entry, so one manifest can protect both kinds of file. Prefix comparison is used,
so a full 64-character digest also works.

Counter-example, kept because it is the one that actually happens: a corpus was
checked only at the start of a run. The report was produced, and the corpus was
then found to have been rewritten by a scheduled job halfway through the run.
Every number in the report was real and none of them described the corpus the
report named. The post-run check is not redundant; it is the half that catches
this.

Requires: Python >= 3.8 (standard library only).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HASH_CHARS = 16          # enough to catch an edit, short enough to read in a report
READONLY, STATE = "readonly", "state"

ATTRIBUTION = """[attribution] this check does not decide whether the change was legitimate.
  Record all four, in the register, before re-pinning anything:
    who           who or what wrote the file (person, script, scheduled job)
    when          date and time of the write
    what          what changed, in one clause
    re-baselined  yes/no; if yes, the manifest was re-pinned on <date> for <reason>
  "unknown" is a finding, not an answer: write it down and follow up.
  Then re-run this check. A clean pass closes the loop; a second mismatch does not."""


class Entry:
    __slots__ = ("expected", "path", "cls", "line_no")

    def __init__(self, expected, path, cls, line_no):
        self.expected = expected
        self.path = path
        self.cls = cls
        self.line_no = line_no


def parse_manifest(text, default_class):
    """Return (entries, problems). A problem is a line that names no usable entry."""
    entries, problems = [], []
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            problems.append((default_class, line_no, "-", "line names no path"))
            continue
        expected, path = parts[0].lower(), parts[1]
        if path.startswith("*"):          # `sha256sum` binary-mode marker
            path = path[1:]
        cls = default_class
        if len(parts) >= 3:
            if parts[2] not in (READONLY, STATE):
                problems.append((default_class, line_no, path,
                                 "unknown class %r (expected readonly|state)" % parts[2]))
                continue
            cls = parts[2]
        if not path:
            problems.append((cls, line_no, "-", "empty path"))
            continue
        if len(expected) < 8 or any(c not in "0123456789abcdef" for c in expected):
            problems.append((cls, line_no, path,
                             "digest is not hex (or shorter than 8 characters)"))
            continue
        entries.append(Entry(expected, path, cls, line_no))
    return entries, problems


def digest_of(path, chars):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:chars]


def check(root, entry):
    """Return (status, detail) where status is 'ok' | 'mismatch' | 'missing' | 'outside'."""
    target = (root / entry.path)
    try:
        resolved = target.resolve()
        resolved.relative_to(root.resolve())
    except (ValueError, OSError):
        return "outside", "path escapes --root"
    if not resolved.is_file():
        return "missing", "listed, not found under --root"
    actual = digest_of(resolved, len(entry.expected))
    if actual == entry.expected:
        return "ok", actual
    return "mismatch", "expected %s, got %s" % (entry.expected, actual)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="check-sources.py",
        description="Verify a hash manifest of input files before and after a run. "
                    "Exit 0 clean, 1 readonly mismatch (stop), 2 state mismatch "
                    "(attribute and re-pin).")
    ap.add_argument("--manifest", required=True,
                    help="manifest file: '<hash>  <path>  [readonly|state]' per line")
    ap.add_argument("--root", required=True,
                    help="directory the manifest paths are relative to")
    ap.add_argument("--class", dest="default_class", default=READONLY,
                    choices=(READONLY, STATE),
                    help="class applied to entries with no class column "
                         "(default: readonly)")
    ap.add_argument("--quiet", action="store_true",
                    help="print mismatches only, not every matching entry")
    args = ap.parse_args(argv)

    manifest = Path(args.manifest)
    root = Path(args.root)
    print("check-sources.py — manifest verification")
    print("  manifest   %s" % manifest)
    print("  root       %s" % root)
    print("  class      %s (default for entries without a class column)" % args.default_class)

    if not manifest.is_file():
        print("  FAIL       manifest unreadable: %s" % manifest)
        print("")
        print("[B5] there is no manifest, so nothing was verified. A missing check is")
        print("     not a passing check: write the manifest, then run the analysis.")
        print("exit 1")
        return 1
    if not root.is_dir():
        print("  FAIL       --root is not a directory: %s" % root)
        print("")
        print("[B5] the manifest cannot be resolved, so nothing was verified.")
        print("exit 1")
        return 1

    entries, problems = parse_manifest(manifest.read_text(encoding="utf-8"),
                                       args.default_class)

    readonly_fail, state_fail = [], []
    width = max([len(e.path) for e in entries] + [4])
    for entry in entries:
        status, detail = check(root, entry)
        if status == "ok" and not args.quiet:
            print("  ok      %-*s  %s" % (width, entry.path, detail))
        elif status != "ok":
            print("  FAIL    %-*s  %s" % (width, entry.path, detail))
            (readonly_fail if entry.cls == READONLY else state_fail).append(entry)

    for cls, line_no, path, why in problems:
        print("  FAIL    %-*s  line %d: %s" % (width, path, line_no, why))
        readonly_fail.append(Entry("-", path, READONLY, line_no))

    total = len(entries) + len(problems)
    bad = len(readonly_fail) + len(state_fail)
    print("")
    print("  %d entr%s, %d mismatch%s" % (total, "y" if total == 1 else "ies",
                                          bad, "" if bad == 1 else "es"))

    if not bad:
        print("exit 0 — every entry matches")
        return 0

    if readonly_fail:
        print("")
        print("[B5] a read-only input changed. Stop.")
        print("     The analysis that already read it has no known basis. Name the file,")
        print("     find out what wrote it, and re-run from a known state. Re-pinning the")
        print("     hash is allowed only after the change is attributed, and the new entry")
        print("     carries the date and that reason.")
        for entry in readonly_fail:
            print("       - %s" % entry.path)

    if state_fail:
        print("")
        print(ATTRIBUTION)
        for entry in state_fail:
            print("       - %s" % entry.path)

    print("")
    print("exit %d" % (1 if readonly_fail else 2))
    return 1 if readonly_fail else 2


if __name__ == "__main__":
    sys.exit(main())
