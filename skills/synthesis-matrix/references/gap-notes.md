# Gap notes

A gap is not "something nobody has done". That describes most of the space and predicts nothing.

A gap is **a specific piece of evidence that does not exist, whose absence is visible in the matrix, and whose production would change a decision.**

Six categories, each with its own test.

| Category | Statement shape | Test |
|---|---|---|
| `no-benchmark` | a method exists, nothing evaluates it under condition X | a card reports the method; no card reports the condition |
| `claimed-never-shown` | a claim appears in discussions but no table supports it | the claim is quoted; the table it needs is named and absent |
| `assumed-never-tested` | every paper in the group assumes Y | Y appears in ≥3 cards' methods; no card tests Y |
| `measured-only-under-Z` | the number exists only for one regime | one condition populated, the neighbouring cell empty |
| `disagreement-unresolved` | two cards report incompatible values, no third resolves it | a register entry, plus the experiment that would settle it |
| `interface-missing` | two groups do not cite each other and their methods would compose | both groups populated, the cross-edge empty |

---

## What makes a gap actionable

Four fields, and a gap without all four is a topic, not a gap:

```markdown
### G-03 — no held-out evaluation for the ranking step
category: no-benchmark
evidence: 4 cards in group-2 report ranking performance; 0 report a held-out split.
  `smith2024_x` §5 reports 3 of 4 sets; the 4th is used for tuning (§4).
  `lee2023_y` §6 states the split is random.
would-close: one evaluation on a split untouched by tuning, any of the 4 methods.
changes-decision: yes — the current ranking of group-2 depends on the tuned set.
```

| Field | Test |
|---|---|
| `evidence` | at least two cards, with sections; "the literature lacks" is not evidence |
| `would-close` | a concrete experiment or artefact, not "more work" |
| `changes-decision` | name the decision. If no decision changes, it is curiosity |
| `category` | exactly one, from the six |

**Why `changes-decision` is mandatory:** it is the field that separates a research gap from a missing citation. Most "gaps" that survive a review round do so because nobody asked which decision the gap would change.

## Deriving gaps from the matrix

Three mechanical passes, in this order:

1. **Empty cells in table A.** A row with `—` where its neighbours have numbers is `measured-only-under-Z` or `no-benchmark`, depending on whether anyone else measured that condition.
2. **Empty edges in table B.** Two populated groups with no cross-citations and compatible methods → `interface-missing`. This is the highest-yield pass and the one most often skipped, because the matrix looks complete without it.
3. **Register entries with no resolution.** An open contradiction is `disagreement-unresolved` if no card in the corpus could settle it.

Each pass produces candidates. Candidates become gaps only after the four fields are filled.

## What is not a gap

| Written | Why it is not one |
|---|---|
| "more data would help" | no condition, no decision |
| "combine method A with method B" | a suggestion, unless the combination answers a named question nobody has answered |
| "the field lacks benchmarks" | a category, not a gap; name the benchmark and the condition |
| "results are not reproducible" | too broad; name the number and the missing artefact |
| "nobody has tried X in this domain" | unless X's absence is visible in a matrix cell, it is a guess about the literature |
| "this is important" | a judgement about value, not evidence about absence |

The last row is the honest one to keep in mind: **a gap note is an evidence claim, not an importance claim.** Importance may follow; it cannot substitute.

## Cross-topic edges

A gap in one topic is sometimes closed by a method in another. Record the edge, not the solution:

```markdown
| gap | other topic | what it offers | status |
|---|---|---|---|
| G-03 | topic-B §4 | a split protocol that would serve as the held-out set | not yet applied |
```

Statuses: `not yet applied` / `applied` / `does not transfer`. The third one matters — recording that a cross-topic import failed prevents a second team from repeating it.

## Gap notes versus proposals

| Gap note | Proposal |
|---|---|
| states what evidence is missing | states what experiment to run, with a protocol |
| lives in the record layer | lives in the adjudication layer |
| may be numerous and unordered | is prioritised and defended |

A gap note that starts specifying an experimental design has become a proposal in the wrong file. Move it.

**Counter-example:** a gap note grew a four-arm experimental design with sample sizes. It was the best content in the topic, and it was invisible to the proposal process because it was filed as a gap.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "the field lacks a benchmark" | a category, not a named gap |
| one card as the sole evidence | could be that paper's omission |
| `would-close: more work` | not an artefact |
| no `changes-decision` | curiosity filed as a finding |
| gap essentially designing an experiment | a proposal in the wrong layer |
| cross-topic import recorded as success only | the failed imports disappear |

## Checklist

- [ ] Every gap has exactly one category from the six.
- [ ] Evidence cites at least two cards, with sections.
- [ ] `would-close` names an artefact or an experiment.
- [ ] `changes-decision` names a decision, or the note is downgraded.
- [ ] The empty-edge pass was run, not just the empty-cell pass.
- [ ] Cross-topic edges record failures as well as successes.
- [ ] No gap note contains an experimental protocol.
