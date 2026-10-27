---
name: research-ops
description: >-
  Operating layer for a multi-stage research pipeline: maintains the scan cursor,
  push log, contradiction register, TODO list, and delivery format across stages.
  Use when the task is to update or reconcile pipeline state rather than to produce
  research output — record a scan position, log pushed items, register a
  contradiction under an ID, close a TODO, verify that read-only source files are
  unchanged via hash check, or report what changed in a batch. Input: existing
  state files plus one change event. Output: updated state files and a three-line
  delivery note (files touched / next step / newly registered items). Do not use for
  one-off note-taking or for tasks whose output is research content; those go to
  paper-card, synthesis-matrix, proposal-forge, or evidence-audit.
---

# research-ops

The state layer of a research pipeline. Four artifacts — cursor, push log, register, TODO — plus one habit: say what changed and what it cost.

**This skill produces no research content.** No cards, no matrices, no proposals, no verdicts. It keeps the bookkeeping that makes those possible, and it is the only skill allowed to write to the state files.

## What it owns

| Artifact | Question it answers | Single owner |
|---|---|---|
| scan cursor | where did the last run stop, and on what date | `literature-radar` writes, everyone reads |
| push log | which items have already been delivered | `literature-radar` writes, everyone reads |
| contradiction register | which claims are in tension, under which ID | `synthesis-matrix` / `evidence-audit` register; nobody closes them here |
| TODO / open items | what is blocked, on whom, since when | free for all skills, one file |

The rule that makes the layer work: **each fact lives in exactly one file, and other files carry a pointer, never a copy.** Two copies of a cursor diverge within a week; a pointer cannot.

→ `references/state-files.md` for fields, update protocol, and the hash-check that proves read-only sources are untouched.

## Delivery format

Every run ends with three lines, in this order:

```
files:   <what changed, one line>
next:    <the single next action, not a plan>
new:     <items newly registered, with IDs; "none" is a valid answer>
```

And when the run defends a claim it also carries three lines of evidence — *what is being defended / what the evidence is / what remains uncovered* — with speculation excluded and unverifiable items booked into the register. This is not ceremony: it is the only place where "I checked" becomes auditable.

→ `references/delivery-format.md` for the ledger that backs the second triple, and the rule for what may not appear in either.

## Disagreement is part of the delivery

A run that only reports what it did is a run that cannot be argued with.

1. Every delivery carries a final section that names what the executor disagrees with — the instruction as given, the pipeline itself, or the last ruling — with the reason, in the same place every time.
2. **"None" is a valid answer and must be written out.** An absent section and a section saying "none" mean different things, and only one of them is trustworthy.
3. This section is a third artefact, not a fourth delivery line: it is not folded into *files / next / new*, because a disagreement about the instruction is not a fact about the files.

The failure this prevents: a pipeline where the only recorded objections are the ones that were already resolved, so every past decision looks unanimous in hindsight.

## Stopping

Five conditions stop work; everything else continues and gets registered:

| Level | Meaning | Action |
|---|---|---|
| **B1** | material missing | stop, name the file |
| **B2** | provenance broken (a number with no traceable source) | stop, name the claim |
| **B3** | a premise contradicts a known fact | stop, name both |
| **B4** | rules are mutually exclusive — cannot proceed | stop, name the pair |
| **B5** | silent error (a wrong output that looks right) | stop, name the detection |

Hit one → mark `[BLOCKER]`, stop that thread, continue the rest. **Nothing else is a blocker**; calling a preference a blocker is how a pipeline loses a day.

→ `references/blocker-levels.md` — including why B1–B5, P-1–P-4, and the M-type tags must never be converted into each other.

## Registering

Two layers, two permissions:

| Layer | May do | May not do |
|---|---|---|
| **record layer** (cards, matrix, gap notes) | register a tension with an ID, a location, a type, the facts, and a suggested disposition | decide who is right; rewrite neighbouring prose to fit |
| **adjudication layer** (proposals) | rule a claim holds / fails / is undecidable, and fix a primary value | write back into the record layer; cite a record-layer entry as precedent |

→ `references/ledger-rules.md` for the boundary cases, including the one that breaks most pipelines: a same-day ruling that starts as a registration.

## Does not trigger

Three prompts that look adjacent and must go elsewhere. These are the regression fixtures for this skill's `description`; if a change makes any of them route here, the change is wrong.

| Prompt | Correct route | Why not here |
|---|---|---|
| "Turn this PDF into a card with provenance" | `paper-card` | the output is research content; state files may also change, which is exactly the trap |
| "Compare these six cards on one axis" | `synthesis-matrix` | produces a comparative claim; registering a contradiction afterwards is a separate, smaller act |
| "Keep notes on what I read this week" | *no skill* | one-off note-taking with no state contract, no IDs, nothing to reconcile |

The last one matters most: research-ops is not a note-taking skill, and a pipeline that treats it as one ends up with state files nobody trusts.

## Routing

| Task | Go to |
|---|---|
| which file holds which fact; how to update a cursor | `references/state-files.md` |
| how to close a run; what the ledger must contain | `references/delivery-format.md` |
| should I stop; is this a blocker | `references/blocker-levels.md` |
| may I decide this, or only register it | `references/ledger-rules.md` |
| run the scan itself | `literature-radar` |
| decide whether a claim holds | `evidence-audit` |
