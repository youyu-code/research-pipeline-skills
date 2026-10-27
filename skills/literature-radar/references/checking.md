# Checking a run

Four checks decide whether a run may report. They are cheap, they are mechanical, and skipping them is how a pipeline produces confident reports about weeks it never read.

```yaml
selfcheck:
  requests-expected: 14
  requests-made: 14
  per-source: {source-a: ok, source-b: ok, source-c: limited}
  server-total: 87
  local-count: 87
  shallowest-floor: 2025-12-28      # must be earlier than the window start
  window-start: 2026-01-01
  verdict: pass
```

---

## 1. Request count reconciliation

`requests-made` must equal `requests-expected`, and both must be explainable: one query per source, plus `ceil(items / page-size)` continuation requests, plus retries.

**Why it matters.** A missing continuation request is invisible in the output — the report contains items, just not all of them. This check is the only place where "I asked for everything I intended to ask for" is verified rather than assumed.

**Counter-example:** a source returned 500 items; the run fetched one page of 100 and reported 100 as the week's total, with no error anywhere.

## 2. Server total versus local count

For each source, the number of items the server reports for the query should equal the number you parsed. A shortfall is truncation or a dropped page.

**Counter-example:** a payload cut at a round byte boundary. XML parsed, item count was 412 against a reported 500, and only this check caught it.

Where the server's total is unavailable or unreliable (compound queries — see `rate-limits.md`), record `expected: unavailable` rather than guessing. An unavailable total is an honest gap; a fabricated one closes the check without closing the gap.

## 3. Per-source status written

Every source, including the ones with zero items, gets a status. A source with no status is a source whose silence cannot be interpreted.

**Counter-example:** three sources omitted from the state block because they returned nothing. One of them had been rate-limited for six consecutive runs; nobody noticed, because "no status" and "no items" looked the same in every report.

## 4. Shallowest source reaches the window start

The floor — the oldest date any source has been walked back to — must be earlier than the window start. If it is not, the window was not covered, no matter how many items came back.

**Counter-example:** a run whose busiest source returned 300 items all dated inside the window, while its slowest source had only ever been walked back to three days before the window end. The report was 300 items long and described a period it had read only in part.

---

## The empty-window evidence triple

When a run returns zero items, the report must carry all three of these, or it must not say "nothing was published":

| # | Evidence | What it rules out |
|---|---|---|
| 1 | the newest item available from the source is dated **before** the window start | the source has newer content that the query failed to return |
| 2 | the shallowest source was walked back **earlier** than the window start | the window sits outside the covered range |
| 3 | a control query — a different window, a broader constraint — **returns items** | the source or transport is dead |

All three, every time. Two of three is not a weaker claim; it is a different claim.

| Evidence present | Honest sentence |
|---|---|
| all three | "No items were submitted in this window." |
| 1 and 2, no control | "No items were found in this window; the source's reachability was not independently confirmed." |
| 3 only | "The query returned nothing in this window; coverage depth was not verified." |
| none | "The window was not covered." |

**Counter-example:** a zero reported with the sentence "no new papers this week". The source had been rate-limited; the control query would have returned items immediately, and the report would have said so.

## Prediction, if you make one

Any statement about how much work the next run will be — hours, item counts, cursor movement — is a **prediction** and needs an interval plus the condition it depends on.

```
next run: 3–6 h, assuming the largest source responds in under 5 min per page
```

**Counter-example:** a single-point estimate of "about 96 hours of work" delivered as fact, against an actual of roughly 31. The estimate was not wrong about the pipeline; it was wrong about being a number. A range with a condition would have been correct the whole time.

The rule generalises: **a point estimate presented without a condition is a claim that cannot fail, and therefore cannot be trusted.**

## Counter-examples, collected

| Written | Problem |
|---|---|
| "14 requests made" with no expected count | reconciliation is impossible |
| "count: 100" from a 500-item source | continuation requests missing |
| status omitted for empty sources | silence became indistinguishable from failure |
| "coverage: full" with no floor recorded | unfalsifiable |
| "nothing published this week" | no evidence triple |
| "next run ≈ 96 h" | point estimate, no condition |
| `expected: 0` when the total was unavailable | fabricated to close a check |

## Checklist

- [ ] `requests-made` equals `requests-expected`, and the arithmetic is written down.
- [ ] Every source has a status, including the empty ones.
- [ ] Server total compared to local count, or recorded as unavailable.
- [ ] Shallowest floor is earlier than the window start.
- [ ] Zero items triggered the evidence triple, and the sentence matches the evidence present.
- [ ] Any forward-looking number carries an interval and a condition.
