# The grouping axis

A matrix is organised by an axis, and the axis is the only part of the matrix that cannot be checked by looking at a cell.

Two matrices can contain identical numbers and support opposite conclusions, purely because they group differently. So the axis gets designed before the table, and tested before the conclusions.

---

## What an axis is not

| Tempting axis | Why it fails |
|---|---|
| the topic | every paper in the corpus has it; a grouping that includes everything groups nothing |
| the method family | papers using the same method often solve different problems, and papers solving one problem use different methods |
| the publication year | a timeline, not a grouping; it organises by when, which explains nothing |
| the dataset | a benchmark table, not a structure; it tells you who ran what, not what the work is for |
| the venue tier | a quality proxy that correlates with nothing you can act on |

A usable axis answers: **what job does this paper do in a chain that ends somewhere?**

## Designing one

Write the axis as a sentence with a direction:

> *"Papers are grouped by which step of the discovery loop they remove: candidate generation, candidate ranking, or candidate validation."*

Then derive **four predictions**. They are what makes the axis a hypothesis rather than a filing system:

| Prediction | What it constrains |
|---|---|
| **P1 — what should cluster** | two papers that never cite each other should land in the same group for a stated reason |
| **P2 — what should be empty** | at least one cell of the group × attribute grid should be empty, and you should be able to say why |
| **P3 — which group is smallest** | a chain usually has one bottleneck and therefore one thin group |
| **P4 — which groups share a baseline** | adjacent steps in a chain tend to be evaluated on the same benchmark; non-adjacent ones do not |

Then the counter-example — and this is the step people skip:

> **State one paper that fits a group's label but would contradict P2 or P4.** If no such paper could exist, the predictions are tautologies.

## The counter-example check

A grouping survives when a **swap test** fails: take two members from different groups and ask whether exchanging their labels would produce an equally coherent matrix.

- If exchanging labels produces nonsense — the axis is doing work.
- If exchanging labels produces something equally plausible — the axis is decorative, and the groups are your vocabulary rather than the field's structure.

**Counter-example (the failure this prevents):** a corpus grouped into "structure-based" and "ligand-based" methods. Every paper could be described either way depending on which figure you emphasised, so both labels fit almost every paper. The resulting matrix showed two well-populated groups and a clean comparison, and the groups did not correspond to anything — the "difference" between them was the reviewer's attention, not the work.

## Mixed axes

A grouping is sometimes legitimately two-dimensional: *what job it does* × *what it assumes is available*. That is fine, and it is not the same as mixing two axes in one column.

| Acceptable | Not acceptable |
|---|---|
| two orthogonal dimensions, each with its own column | one column whose values come from two different dimensions |
| a stated priority when the dimensions conflict | silent resolution of conflicts per paper |

If two dimensions conflict for a paper — it does the ranking job but assumes validation-grade data — say so in the cell. The conflict is a finding about the field, and flattening it destroys the finding.

## Axes change; matrices do not survive the change

When the axis changes, the matrix is rebuilt. Do not migrate cells: a cell's content depends on which group it sits in, and moving it carries the old axis's assumptions into the new one.

**Counter-example:** an axis refined from three groups to four. The matrix was edited in place, and two rows kept values that had been normalised against the old three-group structure. Every cross-group comparison involving those rows was wrong by the normalisation factor, and nothing in the file showed it.

## What belongs in the axis header

```markdown
axis: <one sentence, with direction>
dimensions: [<primary>, <secondary if any>]
predictions:
  P1: <what clusters, and why>
  P2: <which cell is empty, and why>
  P3: <which group is thinnest, and why>
  P4: <which groups share a baseline>
falsifier: <a paper that would break P2 or P4>
built-from: <card ids + schema version>
```

A matrix without this header is a table. It may be a correct table; it cannot be a synthesis.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "grouped by approach" | a label, no direction, no predictions |
| four groups, all equally populated | suspicious; a real chain has a bottleneck |
| no empty cell anywhere | the grid is too coarse to be informative |
| labels swappable between groups | decorative axis |
| axis changed, cells migrated | old normalisation carried into a new structure |
| falsifier omitted | the predictions cannot fail, so they say nothing |

## Checklist

- [ ] Axis written as one sentence with a direction.
- [ ] Four predictions, each specific enough to be wrong.
- [ ] A named falsifier exists, and the axis survives it.
- [ ] The swap test fails for at least one pair of groups.
- [ ] At least one deliberately empty cell, with a reason.
- [ ] The header records the cards and schema version the axis was built from.
