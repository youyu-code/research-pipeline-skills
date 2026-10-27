# Rate limits and transport

The transport layer lies in four different ways, and three of them produce output that looks fine.

| What you see | What it usually is | What to do |
|---|---|---|
| `429` | you are being limited | measure your own wait; then wait that long |
| `000` (no status) | connection never established | triage before waiting — see below |
| `200` with a plausible body | possibly truncated | verify item count against the server's total |
| `200` with an empty list | possibly a real empty window | apply the empty-window evidence rules in `checking.md` |

---

## 429 — measure, never inherit

The only durable rule: **a backoff value is a measurement, not a parameter.** It belongs to one client, one network, one hour.

**Procedure**

1. Start with no pre-emptive wait.
2. On the first 429, wait a short interval, retry once. If it succeeds, you have a working value for this session.
3. On a second consecutive 429, do not staircase upward in small steps — **jump to a value known to work for this source**, then continue.
4. Record the value in the run log with the time it was measured.

**Why no staircase.** Each step costs a full round trip plus the wait, and a source that limits aggressively will 429 at every rung. Three failed rungs cost more than one correct jump.

**Consecutive 429s after a long wait mean the wait is not the problem** — the source may be refusing the client (user agent, IP reputation) rather than throttling it. Kill the process and restart with the diagnosis, do not keep waiting.

**Counter-example:** a run inherited a documented wait from another machine's notes. It was four times longer than needed, so each 429 cost most of an hour, and the run's own log recorded the inherited value as if it had been measured.

## `000` — triage, do not wait

`000` means the connection never completed. Treating it as rate limiting is the single most expensive misdiagnosis in this skill: it burns the full backoff and then fails again.

**Time signature is the discriminator.** Measure how long the failure takes:

| Signature | Layer | Check |
|---|---|---|
| fails in well under a second | DNS or proxy resolution | check `printenv` for proxy variables, then resolve the host |
| fails after a constant stall of roughly the same duration every time | TCP connect timeout — the address is unreachable | test the same host on another resolved IP |
| fails after a variable delay, longer under load | genuine server-side timeout | retry once, then treat as server |

A constant stall of the same duration on every attempt is the fingerprint of a connect timeout, not of throttling. Throttling answers; a connect timeout does not.

**Remedies, in order**

1. Check proxy environment variables. A misconfigured proxy produces `000` with a short, constant delay.
2. Resolve the host and try a specific address (`--resolve` style). If one address works, the failure is edge-specific, not global.
3. Rotate addresses, then retry the request unchanged.
4. Only then consider waiting.

**Counter-example:** a run spent the full backoff on a `000`, retried, and spent it again — twice — while the address it was resolving had been unreachable the whole time. A single `--resolve` to another address would have finished the run in seconds.

## `200` with a truncated payload

A truncated response has no error status. It has a body that parses, containing fewer items than it should.

**The only reliable check is count reconciliation:** compare the number of items in the body with the number the server reports for the same query. A gap is truncation, not an empty tail.

**Defences that work**

- **Fixed page size**, requested explicitly. Never let the server decide.
- **A generous client timeout** — several hundred seconds for a large page. A timeout tuned for a small response will cut a large one.
- **Download to a temporary file, verify, then move.** A partially written file that is later read as complete is the exact silent-failure shape this skill exists to prevent.
- **A payload-size sanity check** as a secondary signal: sizes that land on suspiciously round numbers, or repeat exactly across different queries, indicate a cut.

**What does not work:** trusting the status code, or trusting that XML parsed. Both succeed on a truncated body.

## Counting: two rules that are wrong in most implementations

### Count with a single constraint

A query combining groups with OR does **not** reliably apply its remaining constraints — the date clause in particular can be dropped, and the returned total then describes a different question.

**Rule:** any number you report comes from a query with one constraint. If you need a compound query to *fetch*, do not report its total.

**Counter-example:** a headline "1,204 results this week" from a query whose date clause had been dropped by the server. The real count was 87; the report was off by 14×.

### Count occurrences, not lines

```
grep -c '<entry>' file          # wrong: counts LINES containing the tag
grep -o '<entry>' file | wc -l  # right: counts occurrences
```

Atom and similar formats are frequently served as a single long line. `grep -c` then returns `1` for a 500-item document, and `1` is a number that passes a plausibility check.

**Rule:** every count that gates a decision is produced by an occurrence count, and the command used is recorded in the log.

## Recording transport state

Per source, per run:

```yaml
- source: <name>
  status: ok | limited | unreachable | truncated | empty
  http: 200 | 429 | 000
  items: <n>
  expected: <n>          # server-reported total, when obtainable
  wait-measured: <seconds, this run>   # only if a 429 was handled
  note: <one clause>
```

`status` is not decoration. An item count with no status cannot be interpreted, and every downstream check in `checking.md` depends on this field being honest.

## Counter-examples, collected

| Written | Problem |
|---|---|
| "waited 3,300 s because the docs said so" | inherited value, measured on another network |
| `000` → wait → retry → wait | misdiagnosis; the connection never existed |
| "429 on the first request, so the limit is 1/hour" | one observation, no measurement |
| staircase 60 s → 120 s → 240 s | three failures to learn what one jump would have |
| `grep -c` returning 1 | line count, not occurrence count |
| compound query total reported | the date clause may be gone |
| truncated body accepted because XML parsed | status and parsing both succeed on truncation |
| empty list accepted as an empty window | no control query, no floor check |

## Checklist

- [ ] Every 429 wait in the log was measured this session, not inherited.
- [ ] Every `000` was triaged by time signature before any waiting.
- [ ] Item count reconciled against the server's total for each source.
- [ ] All reported counts come from single-constraint queries.
- [ ] All counts were produced by occurrence counting.
- [ ] `status` recorded per source, including for empty results.
