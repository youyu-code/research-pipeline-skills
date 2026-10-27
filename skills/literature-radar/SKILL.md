---
name: literature-radar
description: >-
  Periodic literature radar over arXiv or any OAI-PMH style scholarly API: runs a
  keyword-scored scan for a fixed time window, emits a per-day digest, and
  self-checks coverage before reporting. Use when the task is recurring new-paper
  tracking — probe the index ceiling, fetch per-category Atom feeds, score entries
  against a tiered keyword list, verify counts and coverage depth, write a daily or
  backfill report, tune the keyword list with quantified recall/noise deltas, or
  diagnose why a known paper was missed. Input: a keyword config, a scan window
  [S, E), and a scan cursor. Output: digest markdown, an updated cursor, and a
  machine-checkable self-check log. It works on abstracts only: it never reads full
  texts and never builds paper cards (use paper-card for that).
---

# literature-radar

One run answers one question: **what appeared in this window, and can I prove the window was actually covered?**

The second half is the hard half. A sweep that returns nothing looks identical to a sweep that failed, and both look identical to a sweep that was configured to find nothing.

## The run

| Step | Do | Refuse to proceed when |
|---|---|---|
| 1 — window | fix start, end, and per-source floor; write them down before querying | the window overlaps the previous run without a stated reason |
| 2 — query | one constrained query per source; page with a fixed page size | a count comes from a compound query |
| 3 — verify transport | per source: status, item count, and a payload-size sanity check | status is not `ok` — the item count then means nothing |
| 4 — score | keyword and anchor match, with word boundaries on both sides | the profile changed this run and no regression was run |
| 5 — report | items with scores, plus the empty-window evidence when the count is zero | the window was empty and no evidence was produced |
| 6 — write state | cursor, push log delta, delivery note | the cursor would be raised without a per-source floor |

→ `references/window-definitions.md` for the nine window terms, each of which changes the result when defined differently.
→ `references/rate-limits.md` for transport behaviour: rate limiting, connection failures, truncated payloads, and the two counting rules that are wrong in most implementations.
→ `references/checking.md` for the four end-of-run checks and the evidence an empty window must carry.
→ `references/tuning.md` for changing the profile without breaking the corpus it was tuned on.
→ `references/pipeline-ops.md` for long runs, request batching, probe isolation, and the copied-script trap.

## Hard rules

- **A zero-result report must carry its own proof.** "Nothing was published" requires three things: the newest item's date is older than the window start; the shallowest source was walked back past the start; a control query returns items. Without all three, write "the window was not covered", not "nothing was published". Counter-example: a zero reported because a request died at the transport layer; the control query would have shown the source was reachable the whole time.
- **Never extrapolate a rate limit from someone else's run.** A backoff value is a measurement of one client on one network at one hour. Re-measure, then use yours. Counter-example: a run inheriting a documented wait four times longer than needed, costing most of an hour per failure.
- **A count must come from a single-constraint query.** Counts returned for compound queries with OR groups are not comparable across queries. Counter-example: a "1,204 results" headline from a query that silently dropped its date clause.
- **Copying last period's script is the most expensive shortcut in this skill.** After copying, grep every path and identifier to confirm it points at the current period, and confirm the target directory was empty before the run. Counter-example: a script that wrote into the previous period's directory and printed `SKIP already-good`, producing a report that was complete and entirely from the wrong week.
- **`status` is part of the data.** An item count with no transport status cannot be interpreted, and a truncated run that reports 40 items is more dangerous than one that reports 0.

## Output contract

A run delivers, in this order:

1. **report** — items with score and reason, or the empty-window evidence triple
2. **push-log delta** — new IDs only, checked against the log before writing
3. **cursor** — `covered-through` plus a per-source `deepest` and `status`
4. **self-check** — request count reconciled, server count compared to local, per-source completion, shallowest source reaching the window start

## Routing

| Task | Go to |
|---|---|
| define what "this window" means | `references/window-definitions.md` |
| the run is being rate-limited or returns nothing | `references/rate-limits.md` |
| is this run trustworthy | `references/checking.md` |
| change the keyword profile | `references/tuning.md` |
| the run is long, or a copy of last period's script | `references/pipeline-ops.md` |
| read the papers found | `paper-card` |
| compare what was found | `synthesis-matrix` |
| record the cursor in a shared state layer | `research-ops` |
