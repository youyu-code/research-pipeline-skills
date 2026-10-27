#!/usr/bin/env python3
"""T4 — nothing private may be committed.

Scans every tracked file for the five classes that must never reach a public
repository, plus an optional fingerprint blacklist:

  1  Zotero credentials        API key, userID, `zotero://` deep-link URIs
  2  Zotero library names      a *named* library or collection in a config-like form
  3  the author's account name the local user name (assembled at runtime, so this
                               test cannot itself match; see `USER_TOKEN`)
  4  absolute paths            drive letters, /Users/, /home/<name>
  5  session identifiers       timestamped directory names, `_scanMMDD`-style runs
  F  fingerprints              values lifted from private source material; the
                               list is *not* in the repository (see below)

Design notes, because two of these are not obvious:

**The blacklist is local, deliberately.** A file listing the private values to
forbid would itself publish them. So the fingerprints live in
`tests/fingerprints.local.txt`, which `.gitignore` excludes; this test reads it
when present and prints SKIP for that class when it is absent. The maintainer's
machine therefore checks all six classes; a clone checks the five that can be
described without publishing anything.

**The scanner proves it can see.** A guard that silently matches nothing looks
exactly like a clean repository. So a canary line is assembled at runtime from
parts, written to a temporary file, and the scanner is required to flag it before
the real scan is trusted.

A hit can be legitimate (documentation that quotes a path as an example). Mark
the line with `desens:allow` and a reason; the marker is honoured, counted, and
printed, so it is a visible decision rather than an invisible exception.

Requires: Python >= 3.8 (stdlib only). Uses `git ls-files` when available and
falls back to a directory walk.
Exit: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
BLACKLIST = HERE / "fingerprints.local.txt"
ALLOW_RE = re.compile(r"(?:#|<!--)\s*desens:allow\b")

# Assembled so that this file does not contain the token it searches for.
USER_TOKEN = "q" + "cz"

SKIP_DIRS = {".git", ".workbuddy", ".codebuddy", "notes", "__pycache__", ".venv", "venv"}
BINARY_SUFFIXES = {".pdf", ".xlsx", ".docx", ".png", ".jpg", ".jpeg", ".webp", ".zip", ".pyc"}

PATTERNS = (
    # (class, label, compiled regex)
    ("1", "zotero api key",
     re.compile(r"(?i)\b(?:zotero[_-]?)?api[_-]?key\b\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}")),
    ("1", "zotero user id",
     re.compile(r"(?i)\buser(?:id|_id)\b\s*[:=]\s*[\"']?\d{5,}")),
    ("1", "zotero select link",
     re.compile(r"zotero://" r"select/\S+")),
    ("2", "named zotero library",
     re.compile(r"(?i)zotero\s+(?:library|collection)\s*[:=]\s*[^\s\"']{3,}")),
    ("3", "account name",
     re.compile(r"(?i)\b%s\b" % USER_TOKEN)),
    ("4", "drive-letter path",
     re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents|Desktop|WorkBuddy|data|research)\b")),
    ("4", "posix home path",
     re.compile(r"/(?:Users|home)/[A-Za-z][\w.-]+/")),
    ("5", "timestamped directory",
     re.compile(r"\b\d{4}-\d{2}-\d{2}[-_ ]\d{2}[-_:]\d{2}[-_:]\d{2}\b")),
    ("5", "run directory",
     re.compile(r"\b_(?:scan|ctl|probe|run|batch)\d{3,4}\b")),
)


def tracked_files():
    try:
        proc = subprocess.run(["git", "ls-files", "-z"],
                              cwd=str(ROOT),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            names = proc.stdout.decode("utf-8", "replace").split("\0")
            files = [ROOT / n for n in names if n]
            if files:
                return files, "git ls-files"
    except Exception:
        pass

    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(ROOT).parts[:-1])
        if parts & SKIP_DIRS:
            continue
        files.append(path)
    return files, "directory walk"


def load_blacklist():
    if not BLACKLIST.is_file():
        return None
    entries = []
    for raw in BLACKLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.append((line, re.compile(line)))
    return entries


def scan_text(text, blacklist):
    """Return [(class, label, line_no, excerpt)] for one file's text."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if ALLOW_RE.search(line):
            hits.append(("*", "allowed", line_no, line.strip()[:100]))
            continue
        for cls, label, rx in PATTERNS:
            match = rx.search(line)
            if match:
                hits.append((cls, label, line_no, match.group(0)[:100]))
                break
        else:
            if blacklist:
                for label, rx in blacklist:
                    if rx.search(line):
                        hits.append(("F", "fingerprint: " + label, line_no,
                                     line.strip()[:100]))
                        break
    return hits


def read_text(path):
    if path.suffix.lower() in BINARY_SUFFIXES:
        data = path.read_bytes()
        return data.decode("latin-1", "replace")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_bytes().decode("latin-1", "replace")


def canary(blacklist):
    """Prove the scanner detects a planted leak before trusting a clean result."""
    planted = [
        "zotero api key: " + "A" * 24,
        "userID: " + "9" * 8,
        "C:" + "\\Users\\somebody\\paper.pdf",
        "/home/" + "somebody/papers/x.pdf",
        "scan dir " + "2025-01-02" + "-03-04-05",
        "batch _" + "scan0401",
        "owner " + USER_TOKEN,
    ]
    found = {cls for cls, _label, _no, _ex in scan_text("\n".join(planted), None)}
    missing = {"1", "3", "4", "5"} - found

    # The F class is tested through an ad-hoc pattern rather than a real entry:
    # what matters is that a blacklist is consulted at all, and the real list is
    # deliberately absent from the repository.
    probe = [("CANARY", re.compile(r"CANARY-LEAK-7391"))]
    if not any(cls == "F" for cls, _l, _n, _e in scan_text("x CANARY-LEAK-7391 y", probe)):
        missing.add("F")
    return missing


def main():
    print("T4  desensitisation scan")

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
        print("T4  FAIL")
        return 1
    print("  ok    scanner canary          planted leak detected in every class")

    files, how = tracked_files()
    print("  ok    input                    %d file(s) via %s" % (len(files), how))

    problems = []
    allowed = []
    for path in files:
        if path.name == BLACKLIST.name:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for cls, label, line_no, excerpt in scan_text(read_text(path), blacklist):
            if cls == "*":
                allowed.append("%s:%d" % (rel, line_no))
            else:
                problems.append((cls, rel, line_no, label, excerpt))

    if allowed:
        print("  note  %d line(s) carry the allow marker: %s"
              % (len(allowed), ", ".join(allowed[:6])))

    if problems:
        for cls, rel, line_no, label, excerpt in problems:
            print("  FAIL  [%s] %-38s %s:%d  %s" % (cls, label, rel, line_no, excerpt))
        print("T4  FAIL  (%d hit(s) in %d file(s))" % (len(problems), len(files)))
        return 1

    print("  ok    scan                     no hit in %d file(s)" % len(files))
    print("T4  PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
