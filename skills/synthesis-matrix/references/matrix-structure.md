# Matrix structure

Three tables, one file. Each answers a different question, and mixing them is how a matrix becomes a document nobody can update.

| Table | Question | Failure if merged with another |
|---|---|---|
| **A — comparison** | what did each paper report | relations become columns, and every new paper adds columns |
| **B — relations** | how do the papers connect | citation edges get read as performance claims |
| **C — gaps** | what is missing | a gap gets counted as a row, and the matrix grows to fill itself |

---

## Table A — comparison

One row per card. Columns are **attributes**, chosen so that each column answers exactly one question.

```markdown
| card | group | claim (one line) | metric | value | verifiability | source |
|---|---|---|---|---|---|---|
| `smith2024_x` | ranking | beats baseline on 3 of 4 sets | AUROC | 0.81 | verifiable | card §5 Table 2 |
| `lee2023_y` | generation | reports no held-out metric | — | — | no-performance-data | card §6 |
```

**Column rules**

- **One question per column.** "Performance (AUROC/AUPR, mean/best)" is three questions in one cell and will be read as one number.
- **The metric column is mandatory** and is never blank when a value exists. A value without its metric name is not comparable to anything, including itself in a later revision.
- **`—` and `0` are different.** `—` means "not reported"; `0` means "reported as zero". A matrix that conflates them reports absences as failures.
- **Every numeric cell carries a `source`**, at file-and-locator resolution. "Table 2" without the card path breaks when the card is revised.

## Verifiability tiers

Every row gets one of three tiers, and the tier is part of the finding:

| Tier | Meaning | What a reader may do |
|---|---|---|
| `verifiable` | the number can be checked against a table in the paper or its SI | cite it, and re-check it |
| `method-verifiable` | the method is reproducible from the description; the reported precision is not checkable | reproduce the method, not the number |
| `no-performance-data` | no performance number is reported anywhere | use the paper for method or framing only |

**Why a tier and not a footnote.** A column of numbers with no tiers implies uniform reliability, and a comparison built on it inherits that implication. The tiers let a reader see, at a glance, that a promising gap between two rows may be a gap between one number and no number.

**Counter-example:** a matrix where a "20% improvement" row was compared against a row whose cell came from a figure legend, with no tier recorded. The comparison was arithmetically correct and evidentially empty.

## A-notes — per-cell provenance

Below table A, a note block keyed by card and column:

```markdown
<!-- A-notes
smith2024_x / value: table-level value, restated from the paper's own table;
  no recomputation. Source: card §5, provenance table-coord.
lee2023_y / claim: the "3 of 4" is the paper's summary sentence; the grid in
  card §5 shows 2 of 4. Both recorded; the grid is authoritative for the cell.
-->
```

Rules:

- **Only restate values the paper itself reports.** A number you computed belongs in the cell only if marked `derived` with the arithmetic in the note.
- **"Not verifiable" is written, not omitted.** A blank note reads as "nothing to say", which is a different claim.
- **Disagreements between a summary sentence and a grid are recorded here**, and the grid wins for the cell value.

## Table B — relations

Rows are edges, not papers.

```markdown
| from | to | kind | evidence | direction |
|---|---|---|---|---|
| `smith2024_x` | `lee2023_y` | cites | card §8 | → |
| `smith2024_x` | `okafor2022_z` | shared-baseline | card §5 Table 2 | ~ |
| `lee2023_y` | `okafor2022_z` | conflicts | card §6 vs card §5 | ≠ |
```

- **`cites` is directional and must say which way.** "Related to" is not an edge.
- **`shared-baseline` is symmetric**, but write it once and mark it `~` so it is not counted twice.
- **`conflicts` is not an adjudication.** It records that two cards disagree; who is right is elsewhere.

### Empty edges must be written

If group 1 and group 3 have no citations between them, write that down:

```markdown
| group-1 | group-3 | none observed | 14 papers, 0 citations across | — |
```

An empty edge is a finding about a field — two sub-communities that do not read each other — and it is the most common source of gap candidates. Omitting it makes the matrix look denser than the field is.

**Counter-example:** a matrix built from 14 papers showed a well-connected graph. The three edges actually present were all within one group; the connectivity was an artefact of omitting the empty cells.

## Table C — gaps

Pointer table only. The substantive work belongs in `gap-notes.md`; here the matrix records which cell motivated each gap.

```markdown
| gap id | category | motivated by | points to |
|---|---|---|---|
| G-03 | claimed-never-shown | `smith2024_x` §6, `lee2023_y` §7 | gaps/topic.md#G-03 |
```

## Updating

| Change | Action |
|---|---|
| a new card arrives | add one row, re-run the tier assignment, do not touch existing rows |
| a card is revised | update that row, and record the date in the A-note |
| the axis changes | **rebuild** — see `grouping-axis.md` |
| a contradiction is ruled | change `conflicts` → nothing; the edge stays, its status moves to the register |

The rule behind all four: **a cell's meaning depends on the axis and the tier, so neither can change quietly.**

## Counter-examples, collected

| Written | Problem |
|---|---|
| `0.81 / 0.79 / 0.77` in one cell | three values, no statistic, no seed count |
| metric column omitted | the value cannot be compared even with itself |
| `0` where the paper reported nothing | absence recorded as failure |
| tier column omitted | uniform reliability implied |
| "related work" as an edge | no direction, no kind |
| empty edges omitted | connectivity fabricated |
| rows migrated across an axis change | old normalisation in a new structure |

## Checklist

- [ ] One question per column, and the metric column is never blank where a value exists.
- [ ] `—` for not reported, `0` for reported zero.
- [ ] Every numeric cell has a card-level locator.
- [ ] Every row has a verifiability tier.
- [ ] A-notes exist for every cell whose value needed a decision.
- [ ] All edges carry a kind and a direction.
- [ ] At least one empty edge, stated.
- [ ] The axis and the card set are named in the header.
