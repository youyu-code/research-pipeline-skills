# Ledger rules — who may decide what

Two layers exist because the same person is usually both the one who notices a problem and the one who resolves it, and mixing the two roles in one document makes both unusable.

| | Record layer | Adjudication layer |
|---|---|---|
| **Files** | cards, matrix, gap notes, overview | proposals, rulings, review passes |
| **Permission** | register only | may rule |
| **Output** | ID + tag + location + quoted facts + suggested disposition | holds / fails / undecidable, with a reason |
| **Forbidden** | deciding which value is true; rewriting neighbouring prose to fit | writing back into a record-layer file; citing a registration as precedent |

The asymmetry is deliberate: **registering is cheap and reversible; ruling is expensive and binding.** A pipeline that lets registrations drift into rulings ends up with cards that argue, and a register that no longer records anything.

---

## What a registration must contain

```markdown
| id | type | location | facts | disposition | status |
|---|---|---|---|---|---|
| M07 | numeric | card-a §5 Table 1 · card-b §4 | body 0.74 vs SI 0.69, same metric, same dataset | cite body as primary, SI parenthetical | open |
```

| Field | Test |
|---|---|
| `type` | exactly one of the six tags below |
| `location` | precise enough that a reader can open the file and land on the line |
| `facts` | **both** statements quoted, neither interpreted, no adjective |
| `disposition` | phrased as a suggestion ("cite X as primary"), never as a finding ("X is correct") |
| `status` | `open` until someone rules it elsewhere |

Two things a registration must never do:

- **Restate the surrounding prose to make the tension disappear.** A card edited to remove the tension has destroyed the evidence.
- **Defend itself.** No "this is probably a typo" — that is a ruling drafted in the wrong layer.

## The six tags

| Tag | Question it answers | Example shape |
|---|---|---|
| `definition` | do the two sides mean the same thing by this word | "accuracy" = per-cell vs per-molecule |
| `wording` | same fact, two different sentences, one of them stronger | "outperforms" vs "comparable" |
| `numeric` | same metric, different value | 0.74 vs 0.69 |
| `unsourced` | a claim with no locator anywhere | a percentage with no table |
| `version` | the two statements describe different documents | preprint vs camera-ready |
| `self-contradiction` | the paper contradicts itself internally | two denominators for one population |

The tag is a filing decision, not a severity. A `numeric` entry can be trivial; a `wording` entry can invalidate a whole comparison.

A conflict **between two papers** uses these same six tags — there is no seventh tag for cross-paper tension, and adding one would only postpone the question of which of the six it actually is. What differs is scope, and scope is already carried by `location`: two card paths in one field (`card-a §5 Table 1 · card-b §4`) say that the entry spans two documents, and a single path says it does not. The entry still registers both statements without deciding which paper is right; that decision belongs to the adjudication layer and binds only what it names.

## What a ruling must contain

A ruling lives in the adjudication layer and answers exactly one question:

```
claim: <the claim being ruled on>
verdict: holds | fails | undecidable
basis: <the test applied, and its outcome>
scope: <the file this ruling binds — and nothing else>
```

- **`undecidable` is a real verdict** and is used more often than the other two. A claim that cannot be settled with the available material is not a failure of the claim; it is a fact about the material.
- **`scope` is not optional.** A ruling binds the document it sits in. It does not travel to other cards, and it does not become policy.
- **No write-back.** The ruling does not edit the card. If the card needs changing, that is a separate edit in the record layer, and it must be possible to see that the card changed *after* the ruling.

## Multi-round review: append, never overwrite

When a second review pass disagrees with the first, the first verdict stays on the page. Rounds are named `pass 1`, `pass 2` — never `R1`, which already means a reporting commitment in a proposal.

```markdown
**pass 1** holds — the claim survives because the SI reports the same value (…)
**pass 2** fails — pass 1's basis is the SI, but the SI's table is a different ablation (…)
```

Rules:

- The later pass adds a paragraph; it does not edit the earlier one.
- The later pass **names what it is overturning** and why. "pass 1 is wrong" is not a review.
- The final state of a document with three passes is three visible positions plus a current one. A reader can see the argument; that is the point.

The failure this prevents: a review chain that looks unanimous because each pass quietly rewrote the last, and a claim that survived three rounds only because the third round never saw the first round's objection.

## The boundary case: same-day adjudication

A registration is made in the morning and ruled on in the afternoon. Is that allowed?

**Yes — but only if the ruling is in the adjudication layer and the registration stays as written.** What is not allowed is editing the morning entry to read as if it had always been a ruling.

Three signals that the boundary has been crossed:

| Signal | What happened |
|---|---|
| the register entry now contains a verdict verb ("is", "should be", "the true value is") | a ruling was written into the record layer |
| the neighbouring prose was adjusted to match the disposition | the evidence was edited, not the decision made |
| a later entry cites `M07` as precedent for a different paper | a registration was used as a ruling |

The third is the subtlest and the most damaging: it turns one paper's local resolution into a rule nobody voted for. **A registration is evidence about one document, not a precedent for another.**

## Counter-examples

| Written | Layer error |
|---|---|
| "M07: the correct PCC is 0.74" | a verdict in the record layer |
| "M07: probably a typo, ignore" | a ruling disguised as a disposition |
| "the card was reworded so the two values now agree" | evidence destroyed |
| "per M07, all body values outrank SI values" | a registration used as precedent |
| "pass 2 supersedes pass 1 (details omitted)" | a review that hides what it overturned |
| ruling without `scope` | binds everything, therefore nothing |

## Checklist

- [ ] Every register entry has one tag from the six, and both facts quoted.
- [ ] No register entry contains a verdict verb.
- [ ] Every ruling states its basis and its scope.
- [ ] No ruling edited a record-layer file.
- [ ] Review passes are appended, and each names what it overturns.
- [ ] No entry was cited as precedent for a different document.
