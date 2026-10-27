#!/usr/bin/env python3
"""Validate a paper card against card schema v1.

Requires: Python >= 3.8 (stdlib only: argparse, re, sys, pathlib)

Checks the header enums, body section order, the provenance fields of every
value in the results table, the to-be-filled row shape, the three production
notes, the extraction log keys, and the self-check line — including that the
counts in the self-check agree with the log.

Exit codes: 0 = conformant, 3 = violations found, 2 = unreadable input.

Known limits: this reads the frontmatter with a deliberately small parser that
handles flat `key: value` pairs and one level of `- key: value` lists, which is
all schema v1 uses. Anchors, multi-line strings and quoting styles outside that
subset are not supported; a card that fails to parse reports the offending line.
"""

import argparse
import re
import sys
from pathlib import Path

VERSIONS = {"preprint", "camera-ready", "formal"}
SI_STATES = {"independent", "inline", "partial"}
NONE_AS_OF = "none-as-of"
SOURCE_CLASSES = {"text-layer", "table-coord", "figure-transcription", "derived"}
TBF_REASONS = {
    "not-in-paper",
    "not-in-si",
    "si-missing",
    "figure-only",
    "code-repo-only",
    "extraction-failed",
}
BLOCKERS = {"blocks-citation", "blocks-reproduction", "cosmetic"}
TRAIL_KINDS = {"pdf-attachment", "local-file", "folder"}
ESTIMATION_MARKS = ("\u2248", "~", "approx")

HEADER_REQUIRED = [
    "id",
    "title",
    "venue",
    "version",
    "version-evidence",
    "topic",
    "pages",
    "si-state",
    "si-contains",
    "source-trail",
]
BODY_SECTIONS = [
    "§0 Terminology",
    "§1 One-liner",
    "§2 Question",
    "§3 Prior work",
    "§4 Method",
    "§5 Results",
    "§6 Limitations",
    "§7 Transferable",
    "§8 Relations",
]


def split_kv(text):
    if ":" not in text:
        return text.strip(), ""
    key, _, val = text.partition(":")
    return key.strip(), val.strip()


def parse_frontmatter(lines, problems):
    """Parse the small YAML subset schema v1 uses."""
    data = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw.startswith(" "):
            problems.append(f"frontmatter: unexpected indented line {i + 1}: {raw!r}")
            i += 1
            continue
        key, val = split_kv(raw)
        if val:
            data[key] = val
            i += 1
            continue
        i += 1
        items = []
        while i < len(lines) and lines[i].lstrip().startswith("- "):
            indent = len(lines[i]) - len(lines[i].lstrip())
            item = {}
            k, v = split_kv(lines[i].strip()[2:])
            item[k] = v
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith("- "):
                if len(lines[i]) - len(lines[i].lstrip()) <= indent:
                    break
                k, v = split_kv(lines[i].strip())
                item[k] = v
                i += 1
            items.append(item)
        data[key] = items
    return data


def section_map(body):
    """Map a top-level heading to the lines underneath it."""
    sections = {}
    current = None
    for line in body:
        m = re.match(r"^##\s+(.*\S)\s*$", line)
        if m and not line.startswith("###"):
            current = m.group(1)
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def table_rows(lines):
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells):
            continue
        rows.append(cells)
    return rows


def check_header(fm, stem, problems):
    for field in HEADER_REQUIRED:
        if field not in fm:
            problems.append(f"header: missing required field `{field}`")
        elif not fm[field]:
            problems.append(f"header: `{field}` is empty — write the reason, not a blank")

    if fm.get("id") and fm["id"] != stem:
        problems.append(f"header: `id` ({fm['id']}) does not match the filename stem ({stem})")

    version = fm.get("version", "")
    if version and version not in VERSIONS:
        problems.append(f"header: `version` must be one of {sorted(VERSIONS)}, got {version!r}")

    state = fm.get("si-state", "")
    if state:
        if state.startswith(NONE_AS_OF + ":"):
            date = state.split(":", 1)[1]
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                problems.append("header: `none-as-of` needs a YYYY-MM-DD date")
        elif state not in SI_STATES:
            problems.append(f"header: `si-state` must be one of {sorted(SI_STATES)} or none-as-of:<date>, got {state!r}")
        if (state == "partial" or state.startswith(NONE_AS_OF)) and not fm.get("si-note"):
            problems.append("header: `si-note` is required when si-state is partial or none-as-of")

    pages = fm.get("pages", "")
    if pages and not re.search(r"body=\d+p", pages):
        problems.append("header: `pages` must start with body=<n>p")

    trail = fm.get("source-trail")
    if isinstance(trail, list):
        if not trail:
            problems.append("header: `source-trail` is empty — at least one file must be listed")
        for entry in trail:
            kind = entry.get("kind", "")
            if kind not in TRAIL_KINDS:
                problems.append(f"header: source-trail kind {kind!r} not in {sorted(TRAIL_KINDS)}")
            if not entry.get("ref"):
                problems.append("header: source-trail entry has no `ref`")
    elif "source-trail" in fm:
        problems.append("header: `source-trail` must be a list of entries")


def check_body_order(sections, problems):
    present = [name for name in sections if name.startswith("§")]
    order = [n for n in BODY_SECTIONS if n in present]
    if len(order) != len(BODY_SECTIONS):
        missing = [n for n in BODY_SECTIONS if n not in present]
        problems.append(f"body: missing section(s) {missing}")
    if present != order:
        problems.append(f"body: sections out of order — expected {BODY_SECTIONS}, got {present}")


def check_results(sections, problems):
    names = [n for n in sections if n.startswith("§5")]
    if not names:
        return 0
    rows = table_rows(sections[names[0]])
    if not rows:
        problems.append("§5: no results table found")
        return 0
    header = [c.lower() for c in rows[0]]
    needed = ["value", "locator", "source"]
    for col in needed:
        if col not in header:
            problems.append(f"§5: results table needs a `{col}` column (found {rows[0]})")
            return 0
    idx = {col: header.index(col) for col in needed}
    note_idx = header.index("note") if "note" in header else None

    count = 0
    for cells in rows[1:]:
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        value = cells[idx["value"]]
        locator = cells[idx["locator"]]
        source = cells[idx["source"]]
        note = cells[note_idx] if note_idx is not None and note_idx < len(cells) else ""
        count += 1
        if not value:
            problems.append("§5: a results row has an empty value")
        for mark in ESTIMATION_MARKS:
            if mark in value:
                problems.append(f"§5: value {value!r} carries an estimation mark — read from an axis, not the page")
        if not locator:
            problems.append(f"§5: value {value!r} has no locator — it belongs in §6 or the to-be-filled section")
        if source not in SOURCE_CLASSES:
            problems.append(f"§5: value {value!r} has source {source!r}, not one of {sorted(SOURCE_CLASSES)}")
        elif source in {"figure-transcription", "derived"} and not note:
            problems.append(f"§5: value {value!r} is {source} and needs a `note`")
    return count


def check_to_be_filled(sections, problems):
    names = [n for n in sections if n.lower().startswith("to be filled")]
    if not names:
        problems.append("body: missing `## To be filled` section")
        return
    rows = table_rows(sections[names[0]])
    if not rows:
        problems.append("to-be-filled: needs a table, even when empty")
        return
    header = [c.lower() for c in rows[0]]
    for col in ("item", "reason", "blocker", "next-action"):
        if col not in header:
            problems.append(f"to-be-filled: missing `{col}` column")
            return
    idx = {col: header.index(col) for col in ("item", "reason", "blocker", "next-action")}
    for cells in rows[1:]:
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        if not cells[idx["item"]]:
            problems.append("to-be-filled: a row has no `item`")
        if cells[idx["reason"]] not in TBF_REASONS:
            problems.append(f"to-be-filled: reason {cells[idx['reason']]!r} not in {sorted(TBF_REASONS)}")
        if cells[idx["blocker"]] not in BLOCKERS:
            problems.append(f"to-be-filled: blocker {cells[idx['blocker']]!r} not in {sorted(BLOCKERS)}")
        if not cells[idx["next-action"]]:
            problems.append("to-be-filled: a row has no `next-action`")


def check_production_notes(sections, problems):
    names = [n for n in sections if n.lower().startswith("production notes")]
    if not names:
        problems.append("body: missing `## Production notes` section")
        return
    lines = sections[names[0]]
    items = [ln.strip() for ln in lines if re.match(r"^\s*\d+\.\s+\*\*", ln)]
    if len(items) < 3:
        problems.append(f"production notes: {len(items)} numbered item(s), three are required (text / hand work / identity)")
    for item in items:
        body = re.sub(r"^\d+\.\s+\*\*[^*]+\*\*\s*[\u2014-]?\s*", "", item)
        if len(body) < 40:
            problems.append(f"production notes: item {item[:40]!r} says nothing substantial")


def check_extraction_log(body, problems):
    text = "\n".join(body)
    m = re.search(r"^##\s+Extraction log\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        problems.append("body: missing `## Extraction log` section")
        return {}
    block = m.group(1)
    found = {}
    for key in ("mode", "failed-pages", "rebuilt-tables", "transcriptions", "dual-version"):
        hit = re.search(rf"^{key}:[ \t]*(.*(?:\n(?![A-Za-z][-\w]*:)[ \t]+\S.*)*)", block, re.M)
        if not hit:
            problems.append(f"extraction log: missing key `{key}`")
        else:
            found[key] = " ".join(hit.group(1).split())
    return found


def check_self_check(body, log, problems):
    lines = [ln for ln in body if ln.strip()]
    if not lines:
        problems.append("self-check: card has no content")
        return
    last = lines[-1].strip()
    pattern = (
        r"^self-check:\s*pages-read=(\d+)/(\d+)\s*·\s*failed=(\d+)\s*·\s*"
        r"tables-rebuilt=(\d+)\s*·\s*transcriptions=(\d+)\s*·\s*contradictions-registered=(\d+)$"
    )
    m = re.fullmatch(pattern, last)
    if not m:
        problems.append(f"self-check: last non-empty line is not a conformant self-check line: {last[:80]!r}")
        return
    read, total, failed, rebuilt, transcriptions, _ = (int(g) for g in m.groups())
    if read > total:
        problems.append("self-check: pages-read numerator exceeds the denominator")
    if failed > total:
        problems.append("self-check: failed pages exceed total pages")

    if log.get("failed-pages") is not None:
        listed = len(re.findall(r"\d+", log["failed-pages"]))
        if listed != failed:
            problems.append(f"self-check: failed={failed} but failed-pages lists {listed} page(s)")
    if log.get("rebuilt-tables") is not None:
        listed = len(re.findall(r"\bpage\s*:", log["rebuilt-tables"]))
        if listed != rebuilt:
            problems.append(f"self-check: tables-rebuilt={rebuilt} but the log lists {listed}")
    if log.get("transcriptions") is not None:
        listed = len(re.findall(r"\bpage\s*:", log["transcriptions"]))
        if listed != transcriptions:
            problems.append(f"self-check: transcriptions={transcriptions} but the log lists {listed}")


def validate(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    problems = []

    if not lines or lines[0].strip() != "---":
        return ["frontmatter: card must open with a `---` line"], 0
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return ["frontmatter: no closing `---` found"], 0

    fm = parse_frontmatter(lines[1:close], problems)
    body = lines[close + 1 :]
    sections = section_map(body)

    check_header(fm, Path(path).stem, problems)
    check_body_order(sections, problems)
    values = check_results(sections, problems)
    check_to_be_filled(sections, problems)
    check_production_notes(sections, problems)
    log = check_extraction_log(body, problems)
    check_self_check(body, log, problems)
    return problems, values


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate a paper card against schema v1.")
    ap.add_argument("card", help="path to the card .md file")
    ap.add_argument("--quiet", action="store_true", help="print violations only")
    args = ap.parse_args(argv)

    try:
        problems, values = validate(args.card)
    except FileNotFoundError:
        print(f"error: no such file: {args.card}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"error: card is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    if problems:
        print(f"FAIL  {args.card}  ({len(problems)} violation(s))", file=sys.stderr)
        for item in problems:
            print(f"  - {item}", file=sys.stderr)
        return 3

    if not args.quiet:
        print(f"PASS  {args.card}  ({values} value(s) with provenance)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
