---
name: synthesis-matrix
description: >-
  Turn a set of paper cards into a cross-paper matrix plus research-gap notes. Use
  when two or more cards already exist and the task is comparison — build the
  comparison table, group papers along an explicit functional axis with self-tests,
  write cross-topic interface edges including deliberately empty ones, and derive
  gap candidates. Input: cards conforming to paper-card schema v1, plus a grouping
  axis. Output: a matrix file with comparison tables, per-cell provenance notes and
  pending-adjudication entries, plus a gap-notes file. It consumes schema v1 and
  never redefines it. Contradictions are registered, not decided; it does not create
  cards, does not write proposals, and does not rule on whether a claim holds.
---

# synthesis-matrix

N cards become one comparison, on **one explicit axis**, with the incomparabilities written down rather than smoothed over.

The output is not "a table of results". It is a claim about how a field is organised, and that claim can be wrong in a way a table cannot: a bad grouping produces a comparison that is internally consistent and meaningless.

## The one thing to get right first

**The grouping axis is a hypothesis, and it must be testable.** A grouping is not a set of labels; it is a claim that papers in one group do the same job in the same chain, and therefore that their numbers are comparable.

Before building the table, write:

1. the axis, in one sentence;
2. **four predictions** the axis makes — what should cluster, what should be empty, which group should be smallest, which two groups should share a baseline;
3. a **counter-example** that would falsify the axis: a paper that fits the label but contradicts the predicted structure.

If you cannot state (3), the axis is a description, not a hypothesis, and the matrix will encode your taste.

→ `references/grouping-axis.md`

## Structure

| Table | Holds | Rule |
|---|---|---|
| **A — comparison** | one row per paper, columns per attribute | every numeric cell carries a source path; incomparability is written in the cell, not omitted |
| **B — relations** | citation direction, shared baselines, conflicts | only groups with real relations get an edge; an empty edge is written as empty |
| **C — gaps** | what is missing, by category | a gap needs a category, a reason, and the evidence that it is a gap and not an oversight |

→ `references/matrix-structure.md` for column design, the A-note rules, and why an empty edge must be explicit.

## Comparability

Before two numbers may share a column, the metric family, the statistic, the measurement engine, and the implementation vintage must all be compatible — or the difference must be larger than the noise band.

| Question | Verdict |
|---|---|
| same metric name, different family (AUPR vs ROC-AUC) | not comparable — different questions |
| same metric, different engines, band 7–9 points | comparable only if the gap exceeds the band |
| same metric, different runs of the same model, band 1–2 points | comparable only if the gap exceeds the band |
| a re-implementation of an old model on a new toolkit | not that model's performance — label it |
| a summary sentence vs the underlying grid | the grid wins |

→ `references/comparability.md` — the four bands, the metric-family table, and the reconciliation procedure.

## Registering, not ruling

A matrix is a **record-layer** artefact. When two cards disagree:

- register it with an ID, a type, both locations, and both quoted values;
- suggest a disposition;
- **do not** decide which is true, and do not edit either card to make them agree.

The ruling, if one is needed, belongs to `evidence-audit`. The register mechanics — including why a registration is not a precedent — belong to `research-ops`.

## Output contract

```
matrix/<topic>.md      tables A/B/C + per-cell provenance + pending-adjudication list
gaps/<topic>.md        gap candidates by category, each with its evidence
```

Both files name the axis in their header, and both list the cards consumed with their schema version. A matrix whose input set is unknown cannot be updated, only rebuilt.

## Routing

| Task | Go to |
|---|---|
| design or test the grouping axis | `references/grouping-axis.md` |
| column design, A-notes, empty edges | `references/matrix-structure.md` |
| may these two numbers sit in one column | `references/comparability.md` |
| turn the comparison into gap candidates | `references/gap-notes.md` |
| produce a card | `paper-card` |
| decide whether a claim holds | `evidence-audit` |
| register a contradiction in shared state | `research-ops` |
