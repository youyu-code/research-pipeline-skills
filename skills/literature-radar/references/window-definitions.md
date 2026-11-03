# Window definitions

## Contents

- [1. Window start — half-open](#1-window-start--half-open)
- [2. Window end](#2-window-end)
- [3. Daily block](#3-daily-block)
- [4. File naming](#4-file-naming)
- [5. Catch-up block](#5-catch-up-block)
- [6. Hit-rate denominator](#6-hit-rate-denominator)
- [7. C-grade](#7-c-grade)
- [8. Cursor writeback](#8-cursor-writeback)
- [9. Timestamp semantics](#9-timestamp-semantics)
- [10. Announcement batch](#10-announcement-batch)
- [11. Backfill hole](#11-backfill-hole)
- [Recording the eleven](#recording-the-eleven)
- [Counter-examples, collected](#counter-examples-collected)
- [Checklist](#checklist)

Eleven terms. Each one, defined differently, changes which papers appear in the report — and none of them is self-evident.

Write all eleven down **before** the first query, in the run's own log. A window defined after the results arrive is a window fitted to the results.

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

## 10. Announcement batch

A feed is not continuous. Items are released in batches tied to working days, so an empty result for a day has two readings that look identical: **nothing was submitted**, or **the batch for that day does not exist yet**.

The readings demand opposite actions. "Nothing was submitted" advances the cursor and closes the day. "Not materialized yet" must **not** advance it, because the batch may still arrive and this window is the only thing that will ever return those items.

**Rule:** every run records `E` and the **global ceiling** `C` — the newest timestamp present in the response from any source, before filtering by your profile. Then assert:

```
C >= E - L     materialized: an empty result is a real empty
C <  E - L     not materialized: advance the cursor to C, keep [C, E) as a catch-up gap
```

`L` is the largest announcement lag observed for that feed, written down once and revised when it is exceeded. It is not a guess — it is the number the run log has been recording all along, used as a threshold instead of a footnote.

The distinction is not academic: a batch that arrives two days late is invisible to every later window, because later windows start where this one ended.

**Counter-example:** a run reported "no new submissions" for a day and advanced the cursor. That day's batch landed two days later with eight items. Every subsequent window started after that day, so re-querying never saw them; they surfaced three weeks later only because a backfill happened to overlap the old range.

**What this does not decide.** It tells you the window is not ready; it does not tell you why. A globally frozen feed and a single late batch both show an old ceiling, so record the ceiling in the log and compare it across runs rather than reasoning from one value.

## 11. Backfill hole

Items can enter a feed with a `published` timestamp **older than `S`**. A `[S, E)` window will never return them, however many times it is run.

Three mechanisms produce that symptom and need different handling:

| Mechanism | Signature | Recoverable by |
|---|---|---|
| late announcement or cross-list | `published` shortly before `S`, `updated` ≈ `published` | re-scanning `[S − W, S)` |
| revision | `updated` inside the window, `published` long before | a block filtered on `updated`, never on `published` |
| re-numbering | same work, different ID, either date | title fingerprint; no ID rule can see it |

**Rule:** each run also emits two blocks, neither counted in the new-item total:

1. **revision block** — `updated ∈ [S, E) AND published < S`. This is §9's "report revisions as revisions", given a query shape.
2. **late-arrival sweep** — `published ∈ [S − W, S)`, admitted at A/B only, labelled late arrival.

**State the bound.** The sweep covers lags up to `W` and nothing longer. An item announced three weeks late is not recovered by it; that is §10's job, at the source. A sweep is a second chance, not a guarantee — a report claiming "no losses" on the strength of a two-day sweep is claiming coverage it does not have.

**Counter-example:** five missed items were carried for a month as one number — "5 losses, one decision". They were in fact one revision, two items announced within four days, and two announced more than three weeks late. No single fix could move that number, so every proposed fix was judged against a total it could not clear, and none was adopted. Partitioning the bucket was the fix; the bucket was the defect.

---

## Recording the eleven

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
  batch-lag-max: 2d                   # L in §10, the assertion threshold
  ceiling: 2026-01-07T05:12Z          # C in §10, recorded before filtering
  revision-block: updated-in-window   # §11, reported separately
  late-arrival-sweep: 2d              # §11, W; state it, do not imply more
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
| empty result read as "nothing was submitted" | closes a day whose batch had not been generated |
| "no losses" after a 72-hour sweep | claims a coverage bound of three weeks with a three-day instrument |

## Checklist

- [ ] Interval is half-open and both endpoints are in the log.
- [ ] The timestamp field is named, and the report's wording matches it.
- [ ] Period id is derived from the window, never typed.
- [ ] Catch-up runs are labelled as catch-up.
- [ ] Hit rate carries its denominator.
- [ ] C-grade is a matching rule, not a judgement.
- [ ] Cursor writes back the window end, with per-source floors recorded separately.
- [ ] The ceiling is recorded and compared against `E − L` before the cursor moves.
- [ ] Revision and late-arrival blocks are separate, and neither is counted as new.
