# Attack

An attack pass has one output that matters: **which claims are still standing**, and for the rest, which sentences fall.

Everything else — the tone, the number of objections, the thoroughness of the reading — is decoration if the verdict is missing.

---

## Three identities, in order

The order is not stylistic. Each identity assumes the previous one failed; running them out of order produces a list of minor objections attached to a project that should have been stopped.

### 1 — Fatal: does the project still hold in its current form?

**Operational test.** An objection is fatal if, granting it, one of these becomes true:

- the central claim is already answered by existing work, so the project has nothing to add;
- the central claim cannot be tested with the data or methods the project can obtain;
- the effect the project predicts is smaller than the measurement's own noise, so a positive result would be uninterpretable.

**Output when fatal:** stop. Do not list majors and minors — they are irrelevant if the project does not stand. Write the fatal objection, the evidence for it, and the two available responses: re-scope, or abandon.

**Counter-example:** an attack pass listed eleven minor issues and one "major concern about novelty", for a project whose central claim had been published two years earlier under a different name. The eleven minors were accurate. The review was useless, because the ordering hid the one finding that mattered.

### 2 — Major: does the central claim survive its best counter-argument?

**Write the counter-argument in its strongest form**, not in the form the proposal already answers. A counter-argument you can defeat in one sentence was not the best one.

| Test | Question |
|---|---|
| steelman | could a competent reviewer state this objection better than I just did? |
| scope | does the claim survive if the objection holds only for part of the stated scope? |
| asymmetry | is there a version of the claim that is still worth making? |

**Output:** the claim is **rewritten**, not patched. A major objection that produces a footnote has been mis-graded.

### 3 — Minor: what would a careful reader still object to?

Collect, do not act. Minors are repaired after P-1 and P-2 are closed, and half of them will disappear when the claim is re-scoped.

## The competitor route

Ask: *if I were building the competing paper — the one that makes this work unnecessary — what two steps would end this one?*

Write both steps concretely:

1. **Step one** — the cheapest thing a competitor would do to make your result expected (a trivial baseline you did not run, a dataset where the effect vanishes).
2. **Step two** — what they would publish instead (a simpler method with the same number, a proof that the effect is an artefact).

If either step is available to a competitor at low cost, the project has a **structural** problem. Presentation cannot fix a step one that anyone can run in a week.

**Counter-example:** the competitor route's step one was "run the obvious baseline". It had not been run. Every claim in the proposal was conditional on that baseline failing, and nobody had checked — which made the whole document a bet, presented as a finding.

## Survival verdict

Per claim, exactly one of three words:

| Verdict | Means | What the document shows |
|---|---|---|
| `survives` | the claim stands as written | the strongest objection, and why it does not land |
| `survives-narrowed` | stands under a stated restriction | the old claim, the new claim, the boundary |
| `falls` | does not stand | the sentence(s) removed, and what replaces them if anything |

**A list of objections with no verdict is a reading note.** This is the single most common failure of an attack pass: it looks rigorous because it is long.

## Sentence-level bookkeeping

For every claim that does not survive intact, list the sentences that fall, quoted:

```markdown
- falls: "the method is robust across scaffold distributions" (§3.2)
  replaced by: "the method is robust to scaffold noise up to 10% (§4.3)"
- falls: "outperforms all baselines" (§5, abstract)
  replaced by: nothing — the comparison was metric-mixed
```

Two reasons this is not bureaucracy:

- A claim that falls in the abstract and survives in §4 is a document that contradicts itself, and only a quoted list catches it.
- Replaced-by-nothing is a different outcome from replaced-by-something, and both are legitimate. Recording which is which prevents a repair from silently re-introducing the claim.

## Repair grading

Four grades, executed in order. The status table is part of the output, not an afterthought.

| Grade | Definition | Test |
|---|---|---|
| **P-1** | the claim cannot stand as written | if unfixed, the central claim is false or unsupported |
| **P-2** | a definition or scope is ambiguous enough to change the verdict | two readings would be graded differently |
| **P-3** | a specific number needs a targeted re-read | the number's provenance is weak, not its claim |
| **P-4** | structural — the design's shape is wrong | the fix changes the experiment, not the text |

```markdown
| # | item | grade | status | closed by |
|---|---|---|---|---|
| 1 | held-out split not held out | P-1 | open | new split |
| 2 | "robust" undefined | P-2 | open | scope statement |
| 3 | Table 3 value from a figure legend | P-3 | done | re-read card, corrected |
| 4 | no negative control arm | P-4 | blocked | depends on #1 |
```

**Do not interleave grades.** A document with P-3 items closed and P-1 items open looks repaired and is not — and the appearance is the danger, because the next reader checks the status table rather than the claims.

## What is not an attack

| Written | Why it is not one |
|---|---|
| "the writing could be clearer" | not a claim about the work |
| "more experiments would strengthen this" | not falsifiable; which experiments, testing what |
| "the authors should discuss X" | a citation request, not a survival question |
| "I have concerns about the framing" | no claim, no verdict |
| a summary of the proposal followed by praise | a reading note |

An attack pass that produces no `falls` verdict is possible — but it should be rare, and it should be accompanied by the competitor route showing both steps unavailable. Otherwise the pass was a reread.

## Counter-examples, collected

| Symptom | Diagnosis |
|---|---|
| 11 minors, no fatal, project already published | ordering failure — the fatal was never tested |
| major objection answered in one sentence | the steelman step was skipped |
| verdicts absent | a reading note filed as an attack |
| repairs listed by topic, not by grade | execution order lost |
| P-3 closed while P-1 open | appearance of repair |
| claims fall in the abstract, survive in the body | no sentence-level list |

## Checklist

- [ ] Fatal tested first, with the three-part operational test.
- [ ] Counter-arguments written in their strongest form.
- [ ] Competitor route gives two concrete steps.
- [ ] Every claim has a verdict: survives / survives-narrowed / falls.
- [ ] Fallen sentences quoted, with replaced-by recorded.
- [ ] Repairs graded P-1..P-4, with a status table.
- [ ] No P-3 closed while a P-1 is open.
