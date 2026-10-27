# Delivery format

Two triples and a ledger. Both triples are cheap; the ledger is what makes them worth reading.

---

## The first triple: what changed

```
files:   <the state files you wrote, and nothing you only read>
next:    <the single next action>
new:     <newly registered items with IDs, or "none">
```

Three constraints that decide whether this is useful:

- **`files:` lists writes, not reads.** A run that read nine files and wrote one lists one. Reads belong in the extraction log of whatever artefact used them.
- **`next:` is one action, not a plan.** "Re-run the scan for source B after the rate limit clears" is an action. "Continue the pipeline" is a mood.
- **`new:` names IDs or says `none`.** An empty field is ambiguous: did nothing get registered, or did you forget?

## The second triple: what the run defends

```
defending:  <the claim this run's work stands behind>
evidence:   <what makes it checkable — file, hash, count, log line>
covered:    <what is still not covered, stated as a scope, not an apology>
```

This triple exists because "I checked" is the most common unverifiable sentence in research work. Each line has one job:

| Line | Fails when | Example of a failure |
|---|---|---|
| defending | it restates the task instead of the claim | "defending: finished the extraction" — that is an activity, not a claim |
| evidence | it names a process instead of an artefact | "evidence: verified carefully" — nothing can be re-checked |
| covered | it is blank, implying full coverage | a blank line reads as "everything", which is never true |

**Speculation never enters the second triple.** If the evidence is a guess, the row does not go in the triple — it goes into the ledger with status `unverified`, and the triple says `covered: <that item> remains unverified`.

## The ledger

The place where defended claims accumulate. One file per topic, one row per claim:

```markdown
| date | defending | evidence (artefact) | method | uncovered | status |
|---|---|---|---|---|---|
| 2026-01-31 | cursor covers both sources through 01-30 | cursor run=01-31, per-source counts in scan log | read both `deepest` fields and the run log | source A latency unmeasured | verified |
| 2026-01-31 | read-only sources untouched | `sources.sha256`, 18/18 match | sha256 prefix comparison before and after | excludes files added since the manifest | verified |
| 2026-01-31 | SI exists for item 4 | one attachment, id checked | attachment query | declaration not checked | partial |
```

| Column | Rule |
|---|---|
| `defending` | the claim, phrased so it could be false |
| `evidence` | a path, a hash, a count, a line number — something another person can open |
| `method` | how it was checked, in one clause |
| `uncovered` | the scope you did **not** cover. Never empty |
| `status` | `verified` / `partial` / `unverified` |

Why a table and not prose: the ledger gets read during an argument, and during an argument nobody reads prose. Why `uncovered` is mandatory: a row with no stated gap is a claim of exhaustiveness, and exhaustive claims are the ones that get falsified.

**The ledger is not a defence written after the fact.** A row added during the argument is worth less than a row added during the run, and the `date` column is the only thing that distinguishes them. Do not backdate, and do not add rows to a run you have already delivered.

## Change notes

When a run rewrites an existing document, it leaves a note at the top of that document:

```markdown
<!-- 2026-01-31
1. corrected the cursor date for source B (was one day ahead)
2. registered M41 (two counts for the same population)
open: whether M41 is a staging artefact or an error — needs the SI table
-->
```

- **At most three numbered items.** A change note longer than three items means the change was really a rewrite and needs a different kind of record.
- **One open point at most.** The point of the note is to tell the next reader where to look, not to reopen the discussion.
- **No rationale.** "Why" belongs in the ledger row, which has an `evidence` column. Rationale in a change note is prose that will be edited by the next run and lost.

## Counter-examples

| Written | Problem |
|---|---|
| `files: updated state` | no file named; the next reader must diff the repo |
| `next: continue` | not an action |
| `new: several items` | no IDs, so nothing can be closed |
| `defending: checked the extraction` | the task, not a claim |
| `evidence: thorough review` | nothing to open |
| `covered: (empty)` | reads as full coverage |
| ledger row with `uncovered: none` | an exhaustiveness claim nobody can support |
| a change note listing nine edits | a rewrite disguised as a note |

## Checklist

- [ ] `files:` lists only writes.
- [ ] `next:` is one action a person could start now.
- [ ] `new:` has IDs, or the literal word `none`.
- [ ] The defence triple names an artefact, not a process.
- [ ] Every ledger row states what it does not cover.
- [ ] No row was added to a run after that run was delivered.
