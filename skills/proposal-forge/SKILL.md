---
name: proposal-forge
description: >-
  Forge a research proposal from an existing matrix and gap notes, then stress-test
  it through attack and review rounds. Use when the task is to write or harden a
  research design — assemble evidence per theme, define reporting protocols and audit
  designs, run an adversarial review that lists fatal/major/minor objections with an
  explicit survival verdict, and record repair items in execution order. Input:
  matrices, gap notes, and the library's contradiction register. Output: a proposal
  document with protocol, audit table and risk/novelty-check lists, plus attack and
  review layers that never overwrite the original verdicts. Claim adjudication is
  delegated to evidence-audit, the single allowed cross-skill reference. It does not
  write paper prose and does not build cards or matrices.
---

# proposal-forge

A proposal is a claim about what should be done next, defended by evidence about what is already known. This skill builds that claim, then tries to destroy it before a reviewer does.

Two phases, and they must not be run in one pass: **forge** writes the design, **attack** tries to break it. A design written while being defended acquires the shape of its defence.

## Phase 1 — forge

| Step | Output | Refuses to proceed when |
|---|---|---|
| 1 — assemble evidence | one block per theme: the cards, the values, the register entries | a claim has no card behind it |
| 2 — state the gap | the gap this proposal closes, quoting its gap note | the gap cannot name a decision it would change |
| 3 — commit to a reporting protocol | **R1–R4**: per-experiment table, aggregation and weights, negative control arm, inference statement | any of the four is left to "we will see" |
| 4 — design the audit | one row per claim: what would falsify it, what data exists, what it would cost to close | a row has no falsifier |

**R1–R4** are commitments made *before* the experiment, not reporting conventions chosen afterwards. A proposal that cannot state its negative control arm has not decided what counts as success.

→ `references/protocol.md`
→ `references/audit-design.md`

## Phase 2 — attack

Three identities, in this order, because each one requires the previous to have failed:

| Identity | Asks | If it succeeds |
|---|---|---|
| **fatal** | does the project, in its current form, still hold? | stop — repair or abandon, no point listing minor issues |
| **major** | does the central claim survive its best counter-argument? | the claim is rewritten, not patched |
| **minor** | what would a careful reader still object to? | collect, do not act yet |

Then the competitor route: *if I were building the competing paper, what two steps would end this one?* Write both steps out. If either is available, the project has a structural problem, not a presentation problem.

**Survival verdict is mandatory.** For every claim: survives / survives narrowed / falls. A list of objections with no verdict is a reading note, not an attack.

→ `references/attack.md`

## Repair, in order

Repairs are graded **P-1 to P-4** and executed in that order:

| Grade | Meaning | Blocks |
|---|---|---|
| **P-1** | the claim cannot stand as written | everything downstream |
| **P-2** | a definition or scope is ambiguous enough to change the verdict | the claim's wording |
| **P-3** | a number needs a targeted re-read | that number's use |
| **P-4** | structural — the design's shape is wrong | nothing until P-1..P-3 are done |

Do not interleave grades: fixing a P-3 while a P-1 is open produces a document that looks repaired and is not.

**Naming note:** `R1–R4` (reporting commitments) and `P-1–P-4` (repair order) are different systems with different scopes. They are never converted into each other, and neither is a blocker level.

## Layers never overwrite

An attack pass adds a section. A review pass adds another. The earlier verdicts stay visible, and each later pass **names what it overturns and why**.

A document whose three review rounds look unanimous is usually a document where each round edited the last.

## Challenge mode

For an adversarial argument-construction mode with round thresholds instead of a single attack pass, see `references/challenge-mode.md`. It is a mode of this skill, not a separate pipeline — and it is deliberately gated, because running it on a project with fewer than three supporting papers produces confident prose about an empty foundation.

## Routing

| Task | Go to |
|---|---|
| write the reporting commitments | `references/protocol.md` |
| design the audit table | `references/audit-design.md` |
| attack a draft, grade the repairs | `references/attack.md` |
| run multi-round adversarial construction | `references/challenge-mode.md` |
| see worked cases of each failure | `references/case-studies.md` |
| rule on whether a claim holds | `evidence-audit` (the only cross-skill reference) |
| a matrix or gap note this depends on | `synthesis-matrix` |
