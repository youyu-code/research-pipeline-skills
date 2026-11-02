#!/usr/bin/env python3
"""Shared machinery for the two desensitisation tests. Not a test itself.

T4a scans the working tree; T4b scans every line ever added in the repository's
history. They share the pattern table on purpose: two copies of a blacklist
diverge, and the copy that is not being looked at is the one that matters.

Import from a test with:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _desens import ...   # noqa: E402
"""

from __future__ import annotations

import getpass
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
BLACKLIST = HERE / "fingerprints.local.txt"
ALLOW_RE = re.compile(r"(?:#|<!--)\s*desens:allow\b")

SKIP_DIRS = {".git", ".workbuddy", ".codebuddy", "notes", "__pycache__", ".venv", "venv"}
BINARY_SUFFIXES = {".pdf", ".xlsx", ".docx", ".png", ".jpg", ".jpeg", ".webp", ".zip", ".pyc"}


def local_account_name() -> str:
    """The account name of the machine running the test, derived at runtime.

    `getpass.getuser()` first, then `USERNAME` / `USER`, and empty when none of
    the three yields a name. The value is never written into this file: a test
    that spells out the string it forbids is itself the leak, and it would also
    only work on the machine it was written on.
    """
    try:
        name = getpass.getuser()
    except Exception:
        name = ""
    if not name:
        name = os.environ.get("USERNAME") or os.environ.get("USER") or ""
    return name.strip()


USER_TOKEN = local_account_name()


def build_patterns() -> tuple:
    """The pattern table, built per run so class 3 exists only when it can."""
    table = [
        # (class, label, compiled regex)
        ("1", "zotero api key",
         re.compile(r"(?i)\b(?:zotero[_-]?)?api[_-]?key\b\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}")),
        ("1", "zotero user id",
         re.compile(r"(?i)\buser(?:id|_id)\b\s*[:=]\s*[\"']?\d{5,}")),
        ("1", "zotero select link",
         re.compile(r"zotero://" r"select/\S+")),
        ("2", "named zotero library",
         re.compile(r"(?i)zotero\s+(?:library|collection)\s*[:=]\s*[^\s\"']{3,}")),
    ]
    if USER_TOKEN:
        table.append(("3", "account name",
                      re.compile(r"(?i)\b%s\b" % re.escape(USER_TOKEN))))
    table.extend([
        ("4", "drive-letter path",
         re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents|Desktop|WorkBuddy|data|research)\b")),
        ("4", "posix home path",
         re.compile(r"/(?:Users|home)/[A-Za-z][\w.-]+/")),
        ("5", "timestamped directory",
         re.compile(r"\b\d{4}-\d{2}-\d{2}[-_ ]\d{2}[-_:]\d{2}[-_:]\d{2}\b")),
        ("5", "run directory",
         re.compile(r"\b_(?:scan|ctl|probe|run|batch)\d{3,4}\b")),
    ])
    return tuple(table)


PATTERNS = build_patterns()


def tracked_files() -> tuple:
    try:
        proc = subprocess.run(["git", "ls-files", "-z"],
                              cwd=str(ROOT),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            names = proc.stdout.decode("utf-8", "replace").split("\0")
            # `git ls-files` reads the index, which can name a file deleted in
            # the working tree but not yet staged. Scanning it would crash the
            # test instead of reporting a result; git status is where that state
            # belongs.
            files = [ROOT / n for n in names if n and (ROOT / n).is_file()]
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


# The scanner's own source necessarily contains the literals it forbids: a
# pattern for `zotero://select/...` is written as that string with a regex tail,
# and every canary has to match the class it proves. Scanning these files with
# the pattern-derived classes therefore reports the definitions themselves, and
# the only outcomes are: an exemption, or somebody deleting the test.
#
# The exemption is bounded: these paths are still scanned for class F, the
# fingerprint list, which is where private *values* live. What is exempted is
# the small set of literals the file is made of.
SELF_PATHS = ("tests/_desens.py", "tests/t4a_desensitize_tree.py",
              "tests/t4b_desensitize_history.py",
              # the retired single-file name; its history is the same role, and
              # without it T4b can never pass on any repository derived from this one
              "tests/t4_desensitize.py")


def is_scanner_source(path: str) -> bool:
    return path.replace("\\", "/").lstrip("./") in SELF_PATHS


def scan_line(line: str, blacklist, include_patterns: bool = True) -> list:
    """Hits for one line: [(class, label, excerpt)]."""
    if ALLOW_RE.search(line):
        return [("*", "allowed", line.strip()[:100])]
    hits = []
    if include_patterns:
        for cls, label, rx in PATTERNS:
            match = rx.search(line)
            if match:
                hits.append((cls, label, match.group(0)[:100]))
                break
    if not hits and blacklist:
        for label, rx in blacklist:
            if rx.search(line):
                hits.append(("F", "fingerprint: " + label, line.strip()[:100]))
                break
    return hits


def scan_text(text: str, blacklist, include_patterns: bool = True) -> list:
    """Return [(class, label, line_no, excerpt)] for one file's text."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for cls, label, excerpt in scan_line(line, blacklist, include_patterns):
            hits.append((cls, label, line_no, excerpt))
    return hits


def read_text(path: Path) -> str:
    if path.suffix.lower() in BINARY_SUFFIXES:
        data = path.read_bytes()
        return data.decode("latin-1", "replace")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_bytes().decode("latin-1", "replace")


def canary(blacklist) -> set:
    """Prove the scanner detects a planted leak before trusting a clean result."""
    planted = [
        "zotero api key: " + "A" * 24,
        "userID: " + "9" * 8,
        "C:" + "\\Users\\somebody\\paper.pdf",
        "/home/" + "somebody/papers/x.pdf",
        "scan dir " + "2025-01-02" + "-03-04-05",
        "batch _" + "scan0401",
    ]
    expected = {"1", "4", "5"}
    if USER_TOKEN:
        planted.append("owner " + USER_TOKEN)
        expected.add("3")

    found = {cls for cls, _label, _no, _ex in scan_text("\n".join(planted), None)}
    missing = expected - found

    # The F class is tested through an ad-hoc pattern rather than a real entry:
    # what matters is that a blacklist is consulted at all, and the real list is
    # deliberately absent from the repository.
    probe = [("CANARY", re.compile(r"CANARY-LEAK-7391"))]
    if not any(cls == "F" for cls, _l, _n, _e in scan_text("x CANARY-LEAK-7391 y", probe)):
        missing.add("F")
    return missing


def git(*args: str) -> tuple:
    """Run git in the repository root. Returns (code, stdout bytes)."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(ROOT),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return proc.returncode, proc.stdout
    except Exception:
        return 1, b""
