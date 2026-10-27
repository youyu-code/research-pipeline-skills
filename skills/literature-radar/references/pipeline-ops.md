# Pipeline operations

Four operational traps. All four are about state that survives longer than the command that created it — a process, a directory, a copy of last period's script.

---

## 1. Long jobs must be held by something that outlives the shell

A 40-minute sweep launched with `nohup ... &` is not a background job. It is a job whose parent has left, and whether it survives depends on the host, the terminal, and the OOM killer.

**What fails, and how it looks**

| Method | Failure | Symptom |
|---|---|---|
| `nohup cmd &` | parent exits, child reparented or killed | process count returns 0 while the log is incomplete |
| foreground with a large timeout | the timeout mechanism converts or kills | a run that "finished" with no tail in the log |
| `&` without `nohup` | SIGHUP on terminal close | truncated output, exit code invisible |

**What works:** let the supervisor hold the process (the agent's background task mechanism, a task queue, `systemd-run`, `tmux`). The requirement is not "run in background" — it is **something that survives the caller and can report the exit code afterwards.**

**Counter-example:** a 25-minute fetch launched with `nohup`. The log showed 18 minutes of work and stopped mid-source. The process count was zero, so the run was reported as "completed with fewer items" rather than "died", and the missing source was recorded as empty.

## 2. Batch requests, and write the limit down

A loop that issues an unbounded number of requests will eventually be rate-limited, and the failure will look like a data problem rather than a pacing problem.

**Rule:** at most eight requests per loop iteration, then persist state and start a new iteration. The state write is what makes the loop restartable.

**Why eight and not "as many as possible":** the number matters less than the existence of a number. An explicit limit produces restarts at known points; an implicit one produces a failure in the middle of a page.

**Counter-example:** a loop over 60 queries in one iteration. It was rate-limited at request 41; the cursor had not been written for 40 requests of work, and the next run repeated all of it.

## 3. Probes go in their own directory

Any run that writes test output must write it somewhere the pipeline never reads.

**Rule:** probe files go to a dedicated subdirectory (`_probe/`), and parsing only ever reads the primary output directory. If the parser globs a parent directory, a probe becomes a source.

**Counter-example:** a probe XML written into the main output directory was picked up as a sixth source. The report showed 1 extra item from a "source" that was a test fixture, and it took an hour to find because nothing about the item looked wrong — it was a real paper, fetched by a probe.

**Design rule:** the parser's input path should be a list of known files, not a wildcard over a directory. A wildcard is an invitation.

## 4. The copied-script trap

The most expensive failure in this skill, and the cheapest to prevent.

**The pattern:** last period's script is copied, the period identifier is changed in a few places, and the run starts. Some references to the old period remain. The script then writes into the old directory, finds existing output, and reports success.

**Three defences, all required**

| Defence | Check |
|---|---|
| target directory empty before the run | `ls` the output path; any existing file is a stop |
| every reference grepped after copying | the period identifier, the output path, the log path, the state file it updates |
| `SKIP` never treated as data | a "skip because output exists" message is a refusal, not a completion |

**Counter-example:** a copied script printed `SKIP already-good` for four of six sources. The report was complete, plausible, and built entirely from the previous period's files. Nothing in the output indicated a problem; the only signal was a status line nobody reads on a successful run.

**The generalisation worth keeping:** *a success message produced by a skip is not evidence of work.* Any harness that can be satisfied by pre-existing files will eventually be satisfied by the wrong files.

---

## Run log

Each run leaves one block, machine-checkable:

```yaml
run: 2026-01-07
supervisor: background-task | tmux | systemd | other
output-dir-empty-at-start: true
requests-made: 14
loops: 2
probe-dir: _probe/
copy-checked: [period-id, out-path, log-path, state-path]
exit: ok | partial | failed
```

`output-dir-empty-at-start` and `copy-checked` are the two fields that catch the trap. They cost ten seconds and they are the only record that the defences were actually applied.

## Counter-examples, collected

| Symptom | Real cause |
|---|---|
| process count 0, log truncated | `nohup` child died with the shell |
| "completed with fewer items" | the run died; nothing was completed |
| one extra item from an unknown source | a probe file in the output directory |
| report identical to last week's | copied script wrote to last week's directory |
| `SKIP already-good` in the log | refusal read as success |
| cursor unchanged after 40 requests | no state write inside the loop |

## Checklist

- [ ] The job is held by something that outlives the shell, and the exit code is retrievable.
- [ ] Requests per loop are capped at a written number, and state is written between loops.
- [ ] Probes write to their own directory, and the parser reads a file list, not a wildcard.
- [ ] Output directory verified empty before the run.
- [ ] Every period reference grepped after copying.
- [ ] `SKIP` treated as a refusal in every code path that reports success.
