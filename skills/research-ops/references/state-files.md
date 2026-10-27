# State files

Four artifacts, four schemas, one rule: **a fact lives in one file, and every other file points at it.**

Two copies of a cursor diverge within a week. A pointer cannot diverge. When you find yourself writing the same fact into a second file, write the path instead.

---

## 1. Scan cursor

Answers: *where did the last run stop, per source, and on what date.*

```yaml
run: 2026-01-31            # the run this position belongs to
covered-through: 2026-01-30 # the latest publication date fully covered
sources:
  - name: <source-a>
    deepest: 2026-01-28     # the oldest date this source has been walked back to
    last-run-items: 42
    status: ok              # ok | truncated | rate-limited | failed
  - name: <source-b>
    deepest: 2026-01-19
    last-run-items: 0
    status: ok
```

Three fields carry all the weight:

| Field | Why it cannot be derived |
|---|---|
| `covered-through` | the newest item seen is not the newest date covered — a source can return 40 items all older than yesterday |
| `deepest` per source | sources have different latency; one is 2 days behind and another 10, and the cursor must record both or the next run double-counts |
| `status` | a truncated run and an empty run produce the same item count. Without `status`, "0 items" is indistinguishable from "the request died" |

**Update protocol.** Read the file, modify in memory, write the whole file. Never append and never trust a partial write: an appended cursor is a cursor with two `covered-through` values and no rule for which wins.

**Conflict.** If two runs disagree, the one with the later `run` date wins for `covered-through`, but the *older* `deepest` wins per source — walking backward is monotone, and a later run that only saw recent items must not raise the floor.

## 2. Push log

Answers: *which items have already been delivered, so they are never delivered twice.*

```markdown
| date | id | title | source | score | block |
|---|---|---|---|---|---|
```

Rules that are not obvious:

- **The log is append-only.** An item is never removed because it turned out to be unimportant; importance is a later judgement and the log is a record of delivery.
- **`id` is the identity, not the title.** Titles get edited upstream; the ID does not.
- **A re-run that re-delivers an item is a bug, not a refresh.** Check the log before writing a report, and check it after a scoring change — a keyword edit can silently re-admit items already pushed.

## 3. Contradiction register

Answers: *which claims are in tension, under which ID, and who may close them.*

```markdown
| id | type | location | facts | disposition | status |
|---|---|---|---|---|---|
| M01 | numeric | card-a §5 vs card-b §5 | 0.74 vs 0.69, same metric | cite body as primary, SI in parentheses | open |
```

| Field | Rule |
|---|---|
| `id` | sequential, never reused, never renumbered when entries are deleted |
| `type` | one of the six controlled tags (see `ledger-rules.md`) |
| `location` | file + section, precise enough to open directly |
| `facts` | the two values or two statements, both quoted, neither interpreted |
| `disposition` | a **suggested** action. Suggestions are not rulings; see `ledger-rules.md` |
| `status` | `open` / `ruled:<where>` / `withdrawn` |

**The register does not close its own entries.** An entry becomes `ruled` only when the adjudication layer writes a ruling somewhere else, and the register then records *where* — the pointer, not the ruling.

## 4. Open items

Answers: *what is blocked, on whom, since when.*

```markdown
- [ ] <item> — blocked by <person/artefact> since <date> — closes when <condition>
```

Three habits keep this list usable:

- **One item per line.** Two items merged into one checkbox become one item nobody can close.
- **Every line names a closer.** "Needs more work" has no owner and therefore no next action.
- **Age is part of the item.** An item open for six weeks is a different problem from one opened yesterday, and only the date tells you which.

---

## Pointers, not copies

The failure this prevents: a matrix restates a card's number, the card is corrected, the matrix keeps the old value, and three weeks later the register is asked to reconcile two files that were never independent.

| Instead of | Write |
|---|---|
| restating a metric in the matrix cell | the value **and** the card path it came from |
| copying the cursor into a report | "cursor as of `<run>`" |
| copying an open item into the register | the register ID, and the item references it |

## Read-only sources

Some directories are inputs you must never write to. The protection is procedural, not a promise: **a manifest of relative paths and hashes, checked before and after a run.**

```bash
# manifest line, one per file
printf '%s  %s\n' "$(sha256sum "$f" | cut -c1-16)" "${f#$ROOT/}" >> sources.sha256

# verification — no output means every file matches
sha256sum -c --quiet <(awk '{print $1"  "ENVIRON["ROOT"]"/"$2}' sources.sha256)
```

Truncating to 16 hex characters is enough to catch an edit and short enough to read in a report. Store the full hash only if a file is expected to change and you need to prove *how*.

Two rules for the check:

- **Verify before you read, not after.** A hash mismatch discovered after the analysis means the analysis has no known basis.
- **A mismatch is B5-class, not a warning.** Something wrote to a read-only input; the run stops until you know what.

## Counter-examples, collected

| Written | Problem |
|---|---|
| cursor appended, not rewritten | two `covered-through` values, no rule for which wins |
| `deepest` raised by a run that only saw recent items | the floor moves up; the gap is never scanned again |
| `status` omitted on a source with 0 items | an empty run and a dead run look identical |
| push log pruned of unimportant items | importance is a later judgement; the log is a delivery record |
| register entry renumbered after a deletion | every earlier reference now points at a different problem |
| two items merged into one checkbox | one item nobody can close |
| an open item with no closer | no next action exists, so it never closes |
| a fact restated in a second file | the two copies diverge, and neither is authoritative |
| hash check run after the analysis | the analysis has no known basis |
| hash mismatch logged as a warning | something wrote to a read-only input; that is a stop |

## Checklist

- [ ] Every updated fact was written to exactly one file.
- [ ] The cursor's `status` reflects truncation, not just item count.
- [ ] New register entries have an ID, a type, a location, and both facts quoted.
- [ ] Open items each name a closer and carry a date.
- [ ] Read-only manifest verified this run, and the result recorded in the delivery note.
