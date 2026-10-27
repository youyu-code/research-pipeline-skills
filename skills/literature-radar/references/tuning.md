# Tuning the keyword profile

The profile is the recall/precision dial for the entire pipeline. Changing it is a small software change and a large data change, and the second half is what usually goes wrong.

## Four preconditions

None of them is optional, and they are cheap in the order written.

### 1 — Read the implementation, not the description

Before proposing any change, establish what the current profile actually does, from the code that runs: which fields are searched, whether matching is substring or token, whether there is stemming, which side the word boundary sits on.

**Counter-example:** a change proposed against a documented behaviour that the code had stopped implementing two versions earlier. The proposal was reasonable, the diagnosis was fiction, and the resulting regression could not be attributed to anything.

### 2 — Every proposal carries a quantified delta

"Add `protein-ligand`" is not a proposal. *"Adding `protein-ligand` on the anchor side recovers 4 previously-missed items in the last 30 days and admits 2 false positives"* is.

The measurement needs three numbers: **items recovered**, **items newly admitted (false positives)**, and **the corpus and window used**. Without all three the number is an anecdote.

### 3 — One item at a time, confirmed

Terms interact. A batch of eight additions produces a result nobody can attribute, and if the batch regresses, the only remedy is to remove all eight and lose whatever was working.

**Counter-example:** six terms added in one commit; the regression showed a 9% loss of previously-pushed items. Removing all six restored the baseline, and the three terms that were actually beneficial were lost with them.

### 4 — Regression before and after

Not "the tests pass" — the specific checks below, on a corpus that is held constant across the change.

---

## The regression, and which results are real failures

Six checks are usually run. Only three of them are failures on their own:

| # | Check | Is a failure | Reading |
|---|---|---|---|
| 1 | previously-pushed items disappear | **yes** | the change lost recall on items you had already vetted |
| 2 | an anchor leaks into unrelated matches | **yes** | matching is too loose on the anchor side |
| 3 | an unexplained loss (items gone with no rule change accounting for it) | **yes** | the attribution is incomplete; find the cause before trusting any other number |
| 4 | coarse-grained item count drops | not on its own | may be precision improvement or recall loss — needs item-level attribution |
| 5 | false-positive count changes | not on its own | depends on whether the change targeted precision |
| 6 | score distribution shifts | not on its own | a shift is expected whenever matching changes |

**The discipline:** a coarse count is never read as a verdict. Check 4 is the one people act on, and acting on it alone is how a precision improvement gets reverted because the item count fell.

**Counter-example:** a change removed 271 items from a ranking table. It was reverted as a regression. The 271 were duplicates the change had correctly de-duplicated; the revert restored them and the "regression" was the fix.

## Defaults are behaviour

When a new option is added to a config loader, **the default must reproduce the old behaviour exactly**, even when the old behaviour was a bug.

| Situation | Wrong default | Right default |
|---|---|---|
| new `min-anchor-strength`, old code dropped weak anchors | `0` (never drop) | the old effective threshold |
| new `max-items`, old code had no cap | `100` | unlimited |
| new `dedupe`, old code emitted duplicates | `true` | `false` |

**Why:** existing configs are not edited. A new default that changes behaviour means every existing config silently changes meaning, and the change will be discovered as a regression in data, not as an error in code.

**Counter-example:** a new threshold defaulted to `0`, which meant "never drop". The old hard-coded behaviour dropped weak anchors at a non-zero value. Every config without the new key suddenly admitted 271 extra items, and the "regression" was diagnosed as data drift for two days before anyone read the loader.

## Word boundaries, on both sides

Matching happens between **profile terms** and **candidate text**, and each side has its own boundary requirements. One list shared by both is a source of two distinct bugs.

| Bug | Example shape | Direction |
|---|---|---|
| false positive by prefix | `gene` matching `generative` | term is a prefix of a longer word |
| false positive by substring | a short acronym appearing inside a URL or an identifier | term is buried in a token |
| false negative by suffix | dropping plurals | term needs `s`/`es` variants |

**Rules**

- Keep two boundary tables — one for keyword terms, one for anchors. They are calibrated differently and merge badly.
- Preserve plural forms explicitly; do not rely on a stemmer you did not verify.
- When a term is short (≤4 characters), require an exact token match rather than a boundary rule.
- Record every historical false positive you find, with the text that triggered it. That list is the only durable defence against re-adding the same term.

**Counter-example:** an acronym matched inside a repository URL, adding a paper that had nothing to do with the topic, four times, because the term was matched as a substring and the URL happened to contain it.

## Replaying the last corpus

After a change, replay it against the most recent period's raw results:

- **Use it to validate the change**, not to draw conclusions about that period.
- Do not update that period's report. It was already delivered, and rewriting a delivered report destroys the record of what was delivered when.
- Record the replay result in the change note: items recovered, items admitted, items lost.

**Counter-example:** a replay that improved the ranking was used to rewrite the previous week's digest. The digest was better and no longer described the week it was named after.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "added 8 terms, recall should improve" | no delta, no attribution |
| "count dropped 12%, revert" | coarse count read as a verdict |
| new option defaults to the modern behaviour | every existing config changes meaning |
| one boundary table for terms and anchors | two bug classes, one fix |
| plurals delegated to an unverified stemmer | silent recall loss |
| replay used to rewrite a delivered report | the record stops being a record |

## Checklist

- [ ] Current behaviour read from the code, not the docs.
- [ ] Each proposal carries recovered / admitted / corpus / window.
- [ ] Terms added one at a time, each confirmed.
- [ ] Regression run before and after, with the six checks attributed line by line.
- [ ] New config defaults reproduce the old effective behaviour.
- [ ] Two boundary tables, plurals handled explicitly.
- [ ] Replay validated the change only; no delivered report was rewritten.
