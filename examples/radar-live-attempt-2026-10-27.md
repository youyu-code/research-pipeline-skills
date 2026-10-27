# First live radar run — attempt on 2026-10-27, blocked at the proxy

`literature-radar`'s live path was pointed at `https://export.arxiv.org/api/query` for the first time. **No query reached arXiv.** The blocker is at the local forward proxy, not at the endpoint, and the distinction decides what to do next: a 429 says wait, a refused tunnel says the waiting is pointless.

Consequence: no digest, no cursor, no `radar-<date>/` directory. Everything the offline path proves remains true; nothing about the live path has been measured, and `README.md` still calls it unproven.

## What was attempted

Window `[2026-10-26, 2026-10-27)`, three sources (`cs.LG`, `cs.AI`, `stat.ML`), one constrained query per source, `max_results=200`, sorted ascending by submission date. That is the run table's step 1 and step 2, written down before querying.

## Measurements, in order

| # | Probe | Result | Reading |
|---|---|---|---|
| 1 | `curl https://arxiv.org/abs/1706.03762` | `http=200`, 44 KB, 1.10 s | the main site is reachable through the proxy |
| 2 | `curl https://arxiv.org/pdf/1706.03762v7` | `http=200`, 2.21 MB, 64.0 s | PDF transfer works; large files are slow |
| 3 | `curl https://arxiv.org/pdf/1810.04805v2` | `http=200`, 775 KB, 17.8 s | throughput varies by about 4x between requests |
| 4 | API query, `cat:cs.LG` + one-day date clause | `http=000`, 0 bytes, **10.04 s** | no response at all |
| 5 | API control query, `all:electron`, no date clause | `http=000`, 0 bytes, **10.03 s** | the date clause is not the cause |
| 6 | API control query again, after 75 s of silence | `http=000`, 0 bytes, **10.03 s** | waiting does not change it |
| 7 | `curl -sv` on the same URL | `CONNECT export.arxiv.org:443` → `HTTP/1.1 502 Bad Gateway` | the proxy refuses the tunnel |
| 8 | direct connection, `--noproxy '*'` | `http=000`, 0 bytes, **21.06 s** | no direct egress either; TCP connects time out |
| 9 | `getaddrinfo` for both hosts | `export.arxiv.org` → 146.75.115.42, `arxiv.org` → 151.101.67.42 | DNS is fine; both resolve to Fastly addresses |

Probes 4-6 have the same duration to two decimal places, which is a timeout constant, not a server response. Probe 7 names it: the proxy answers the `CONNECT` itself.

## Triage, per `references/rate-limits.md`

- **Not a rate limit.** A rate limit is `429` with a body; the endpoint returned nothing. Nothing about backoff or `--retry-wait` can fix a refused tunnel, and inventing a wait would have produced a run that looked patient and stayed broken.
- **Not DNS.** Probe 9.
- **Not the date clause.** Probe 5 is the control: the same host, no constraint, same result.
- **Not the endpoint being down.** `arxiv.org` is the same CDN and answers in under a second; only the API host is refused.

An earlier measurement on the same day, before the proxy started refusing the host, did get `429 Rate exceeded.` from the API (14 bytes) and was still `429` after 75 s of silence. That is the behaviour `rate-limits.md` describes for this endpoint, and it is recorded here so the two failure modes are not confused later.

## What would close this

1. A network where `export.arxiv.org:443` can be reached (proxy rule change, or a host with direct egress). Then rerun the same window and expect either items or an empty-window triple.
2. If the run still returns `429`, treat it as the first real measurement of the endpoint's current limit — one retry after a measured wait, no staircase — and record the wait that was actually used.
3. Only after a successful live run does `README.md`'s "the live path is unproven" sentence change, and only then does a `radar-<date>/` directory belong in this folder.

## The rule this run was following

> **A zero-result report must carry its own proof.** "Nothing was published" requires three things: the newest item's date is older than the window start; the shallowest source was walked back past the start; a control query returns items.

This run produced zero results and **none** of the three. So the report is not "nothing was published" and not "the window was empty" — it is "the window was not covered", with the measurements above as the reason.
