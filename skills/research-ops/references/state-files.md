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
- **A mismatch on a read-only input is B5-class, not a warning.** Something wrote to an input you do not own; the run stops until you know what.

### Two classes of entry, two verdicts

A manifest is only useful if it distinguishes what it is protecting. The same mismatch means opposite things depending on who is allowed to write the file, so every entry carries a class — `readonly` or `state` — and the class, not the mismatch, selects the response.

| Class | What it holds | A mismatch means | Response |
|---|---|---|---|
| `readonly` | inputs you never write: a source corpus, a collaborator's directory, reference PDFs | something outside the pipeline wrote to an input | **B5 — stop.** Attribute before continuing; the analysis that already read the file has no known basis |
| `state` | files the pipeline itself writes: cursor, push log, keyword profile, this manifest | the pipeline (or a person) advanced state between two checks | **attribute → re-baseline with a date and a reason → re-verify.** Not a stop |

**`readonly`, applied correctly.** The check runs before the analysis, a source hash does not match, and the run stops with the file named. The attribution comes back "the upstream maintainer published a new revision" — a legitimate external change. The manifest is re-pinned to the new hash **with the date and that reason**, and the analysis is re-run from the new baseline. The run never continues on numbers computed against a file it no longer has.

**`readonly`, applied wrongly.** The same mismatch is noticed after the analysis, re-pinned on the spot, and the report ships. Nothing in the record says what changed or when; six weeks later the re-pin is indistinguishable from a tampered input, and the report's numbers cannot be traced to any version of the corpus.

**`state`, applied correctly.** The cursor's hash differs from the manifest. The check reports which file, which field moved, and the run that moved it (`run: 2026-01-07`, `covered-through` advanced one day). The entry is re-pinned with that date and reason, then the check is re-run and comes back clean. Two lines of attribution, and the manifest stays trustworthy.

**`state`, applied wrongly.** Every state mismatch is re-pinned silently, because "it changes every run anyway". That is true until a truncated write or a hand edit lands — and it lands in the same bucket as routine advancement, so the one mismatch that mattered is now indistinguishable from the ones that did not. The mirror error is as bad: treating a cursor mismatch as B5 stops the pipeline every morning until people learn to skip the check.

**Why one class is not enough.** A single-verdict manifest fails in one of two directions. If every mismatch stops the run, the first legitimate cursor advance trains the operator to override the check. If every mismatch is a warning, a write to a read-only input is logged and forgotten. The class is what keeps "stop" meaningful.

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
| a `state` mismatch re-pinned with no date and no reason | the baseline becomes "whatever it was last time" |
| every mismatch treated as a stop | the first routine cursor advance teaches people to override the check |
| a `readonly` change re-pinned after the analysis | the report's numbers belong to no traceable version of the corpus |

## Checklist

- [ ] Every updated fact was written to exactly one file.
- [ ] The cursor's `status` reflects truncation, not just item count.
- [ ] New register entries have an ID, a type, a location, and both facts quoted.
- [ ] Open items each name a closer and carry a date.
- [ ] Read-only manifest verified this run, and the result recorded in the delivery note.
- [ ] Every manifest entry carries a class, and a mismatch was answered by its class rather than by habit.
- [ ] Every re-pinned `state` entry carries a date and a one-clause reason.
