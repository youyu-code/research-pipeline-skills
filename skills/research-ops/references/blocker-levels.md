# Blocker levels

One question: **do I stop now?** Five conditions say yes. Everything else continues and gets registered.

A blocker is not a severity label. It is an instruction to stop one thread, and it is only useful if it names the thing that stopped it.

| Level | Condition | Detection | Required output |
|---|---|---|---|
| **B1** | material missing | the artefact a step depends on is absent — not "thin", absent | the artefact, by name and location |
| **B2** | provenance broken | a value or claim has no traceable source | the claim, and where the trace ends |
| **B3** | premise contradicts a known fact | two records disagree on a fact that both treat as settled | both statements, both locations |
| **B4** | rules mutually exclusive | two rules require opposite actions in the same situation | the pair of rules |
| **B5** | silent error | an output that looks correct and is not | the detection that caught it |

## Each level, with the failure it prevents

### B1 — material missing

Stop because continuing means inventing. The common form is not a missing file; it is a file that exists and does not contain the thing — a supplementary PDF with no result table is B1 for a step that needs that table.

**Output shape:** `[BLOCKER] B1 — Table S3 absent from <file>; the claim in §5 needs its per-class breakdown.`

**Not B1:** a source that is slower than usual, a page that failed extraction but was recovered by a second mode, a table that needed a coordinate rebuild. All three are work, not absence.

### B2 — provenance broken

A number with no locator, a claim with no citation, a file with no hash. The break is *in the chain*, not in the value — the value may well be right.

**Output shape:** `[BLOCKER] B2 — 0.881 in card §5 has no locator; the row was transcribed but the page was not recorded.`

**Not B2:** a value whose provenance is weak but stated (`figure-transcription` at 450 dpi with no kept image is a defect to register, not a stop).

### B3 — premise contradicts a known fact

Two of your own records disagree about something both treat as settled. This is the most expensive level, because every step downstream of the disagreement is now uncertain.

**Output shape:** `[BLOCKER] B3 — cursor says source B covered through 01-30; the run log shows its last successful request on 01-22.`

**Not B3:** two sources reporting different values for the same metric. That is a *finding* — it goes in the register. B3 requires that one of the two be your own record of what happened, not the literature's record of what it found.

### B4 — rules mutually exclusive

Two rules cannot both be obeyed here. Do not pick one silently; that is how a pipeline acquires an unwritten exception.

**Output shape:** `[BLOCKER] B4 — state-files says the later run wins for covered-through; the same file says a later run must not raise a per-source floor. A run that saw only recent items triggers both.`

**Not B4:** a rule that is inconvenient, or a rule whose exception you would prefer. B4 needs two rules that *cannot* be satisfied together, in this instance.

### B5 — silent error

The output passes every check you designed and is still wrong. This is the level that justifies the whole scheme: B5 errors do not announce themselves, so the only defence is a detection you built in advance.

**Output shape:** `[BLOCKER] B5 — the report claims 42 items new; the push log shows 12 of them were delivered on 01-19. The scoring change re-admitted them and nothing flagged it.`

**Not B5:** an error you noticed. That is a repair. B5 means the pipeline reported success and was wrong — the detection is the valuable artefact, so record it.

## What is not a blocker

| Looks like a blocker | What it actually is |
|---|---|
| the source is rate-limited | a wait; log the status and continue with another source |
| one page failed extraction | a switch of mode, or a logged gap |
| a value is imprecise | a provenance weakness; register it |
| a claim is probably false | an adjudication task, not a stop |
| the work is bigger than expected | scope, not a state |
| I am unsure how to proceed | a question, which is allowed without a blocker label |

The last row matters most: **"I don't know" is not B-something.** Asking is cheap and does not require a label. Reserving `[BLOCKER]` for the five conditions is what keeps the label meaningful.

## Three grading systems, no conversion

Three scales coexist in a mature pipeline. They answer different questions, live in different layers, and are never converted into one another.

| System | Question | Works on | Output form |
|---|---|---|---|
| **B1–B5** | do I stop now | an action, right now | `[BLOCKER]` + halt |
| **P-1–P-4** | what do I fix first | a repair plan's execution order | grouped list + status table |
| **M-type tags** | what kind of problem is this | a register entry's classification | ID + tag + disposition |

**Why conversion is forbidden.** A conversion implies a mapping, and a mapping implies that the three scales measure one quantity. They do not: a numeric M-type entry (two sources disagree on a value) can be a registered finding with no stop at all, or it can sit behind a B2 if the disagreement reveals broken provenance. The tag describes the problem; the blocker describes your next action. Same object, two independent judgements.

Three conversions that are always wrong:

| Wrong | Why it breaks |
|---|---|
| "it is an M-numeric entry, so it is B3" | B3 requires a contradiction between your records about *what happened*, not between two papers about *what they found* |
| "it is P-1, so we stop everything" | P-1 orders a repair; the pipeline can keep producing elsewhere while P-1 waits |
| "it is only cosmetic, so it cannot be B5" | a cosmetic-looking defect that propagates silently is exactly B5 |

**Worked case.** A pipeline found two counts for the same population (9,740 and 9,625), registered it as a numeric entry, and a reviewer re-labelled it P-1 because "numbers must be fixed before anything else". Both labels were defensible and neither was a blocker — the correct record was: *register as numeric, do not stop, and close it only after an arithmetic test.* A conversion to B3 would have stopped a pipeline that had no reason to stop.

## Counter-examples

| Called a blocker | Correct handling |
|---|---|
| "the SI is thin" | not a level; either it lacks the needed table (B1) or it does not (register it) |
| "the number looks wrong" | a suspicion; test it, then register the outcome |
| "two papers disagree" | a finding — register with both locators |
| "the rule is inconvenient" | follow it, or propose changing it; not B4 |
| "I cannot decide" | a question, asked plainly |
| "the deadline is close" | not a pipeline state |

## Checklist

- [ ] Every `[BLOCKER]` names its level and the specific thing that stopped it.
- [ ] The stop is scoped to one thread; other work continued.
- [ ] No P-level or M-tag was converted into a B-level.
- [ ] Non-blockers were registered rather than escalated.
- [ ] A B5 records the detection, not just the error.
