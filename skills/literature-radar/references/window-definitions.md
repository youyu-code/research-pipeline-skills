# Window definitions

Nine terms. Each one, defined differently, changes which papers appear in the report — and none of them is self-evident.

Write all nine down **before** the first query, in the run's own log. A window defined after the results arrive is a window fitted to the results.

---

## 1. Window start — half-open

`[S, E)` — start inclusive, end exclusive.

**Why not `[S, E]`.** Adjacent runs share a boundary date. Closed intervals count the boundary twice, so a paper published at `E` appears in two consecutive reports and the push log has to de-duplicate something that should never have been duplicated.

**Counter-example:** a run with `[01-01, 01-31]` followed by `[01-31, 02-28]` delivered 14 items twice. Both reports were internally correct; the window was not.

## 2. Window end

Usually "now", but state which now: the time the query was sent, or the time the report was written. The gap matters when a run takes an hour and a paper appears inside it.

**Rule:** the end is the query time, and the report says so. A report whose end is the writing time claims coverage it did not have.

## 3. Daily block

Which items belong to which day's report, when a run covers several days.

Two defensible rules — *by publication date* or *by ingestion order* — and they disagree for items with a lag. Pick one, write it in the log, never mix. Mixing produces a report where day 3 contains an item published on day 1 that was fetched on day 2.

## 4. File naming

The period identifier must be derivable from the window, not typed by hand. `YYYY-MM-DD` for a single-day report, `YYYY-MM-DD..YYYY-MM-DD` for a range.

**Counter-example:** a hand-typed filename one day off from the window it contains. The report is right, the index is wrong, and the index is what later runs read.

## 5. Catch-up block

When a run is missed, the next run covers a wider window **and says so as its own block**, rather than silently widening the normal block.

Why: a 7-day block labelled as a 1-day block corrupts every per-day rate computed from the report series. A catch-up block is a different object with a different label.

## 6. Hit-rate denominator

"Hit rate" needs a denominator, and there are three candidates:

| Denominator | Answers |
|---|---|
| items returned by the query | how selective is the keyword profile |
| items after de-duplication against the push log | how much new signal per run |
| items published in the window (server total) | how much of the field the profile sees |

They differ by an order of magnitude and are routinely reported as one number. **Name the denominator in the same line as the rate**, or the rate is not interpretable.

## 7. C-grade

The lowest tier that still gets reported. If C means "matched one weak keyword", the report fills with noise; if C means "matched an anchor plus a keyword", the report is short and the profile looks precise.

**Rule:** C-grade is defined by the matching rule, not by a reviewer's judgement after reading. A grade assigned by reading is a grade that cannot be recomputed.

## 8. Cursor writeback

Which date gets written back after a run: the window end, or the latest publication date seen?

**Write the window end**, and separately record the per-source deepest date reached. The latest publication date is often older than the window end (a quiet week), and writing it back silently re-scans the gap every run.

**Counter-example:** a run that wrote back the newest item's date instead of the window end; the following run re-scanned four days and re-delivered nine items.

## 9. Timestamp semantics

Which timestamp the window filters on: **submitted**, **published**, or **updated**.

- `submitted` — when the author sent it; stable.
- `published` — when the venue released it; can be much later.
- `updated` — when it was last revised; **an old paper updated today enters today's window.**

**Counter-example:** filtering on `updated` to catch revisions, then reporting the results as "new papers this week". Most of the items were years old, and the report's headline count was wrong by that factor.

If revisions are the goal, report them as revisions — a separate block, with the original submission date beside the revision date.

---

## Recording the nine

```yaml
window:
  interval: half-open [S, E)          # S inclusive, E exclusive
  start: 2026-01-01
  end: 2026-01-07                     # query time, recorded
  timestamp-field: submitted          # submitted | published | updated
  daily-block: by-publication-date
  period-id: 2026-01-01..2026-01-07
  catch-up: false
  hit-rate-denominator: after-dedup
  c-grade: anchor-or-two-keywords
  cursor-writeback: window-end
```

A run that cannot fill this block has not defined its window; it has only picked two dates.

## Counter-examples, collected

| Written | What it silently does |
|---|---|
| "this week" | no boundary, no timestamp field |
| `[S, E]` | double-counts the boundary date |
| window end = writing time | claims coverage of the writing interval |
| latest-date writeback | re-scans the quiet gap every run |
| "hit rate 12%" | three possible denominators, one unstated |
| filtering on `updated`, reporting as new | counts revisions as discoveries |
| catch-up run labelled as a normal day | corrupts every per-day series computed from it |

## Checklist

- [ ] Interval is half-open and both endpoints are in the log.
- [ ] The timestamp field is named, and the report's wording matches it.
- [ ] Period id is derived from the window, never typed.
- [ ] Catch-up runs are labelled as catch-up.
- [ ] Hit rate carries its denominator.
- [ ] C-grade is a matching rule, not a judgement.
- [ ] Cursor writes back the window end, with per-source floors recorded separately.
