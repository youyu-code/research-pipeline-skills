# Challenge mode

An adversarial mode for building an argument over several rounds, by repeatedly trying to break it. It is a **mode of proposal-forge, not a writing pipeline**, and it stops before prose.

> **Status:** the gate, the milestones, and the per-round quality gate below are settled. Worked examples are thin — this mode has not been run against a real paper draft in public yet, and the README marks it `planned` for that reason.

---

## Entry gate

**At least three papers must carry the argument before the mode starts.**

If fewer than three support the central claim, stop and say so:

> *"The foundation supports one paper and two adjacent results. An argument built on this would be confident prose over an empty base."*

The gate exists because the failure mode of this mode is fluency: with no supporting literature, rounds still produce text, and the text reads the same as when the foundation is solid. The only thing that distinguishes them is a check made at the start.

**Counter-example:** a challenge run began with one supporting paper and a strong intuition. By round 4 the argument had grown to nine claims, six of which cited the same single paper in different words. Nothing in the document indicated that it was one source wearing nine hats.

## Milestones

The rounds have fixed output obligations, not fixed lengths:

| By round | Must exist | If missing |
|---|---|---|
| **3** | the research question, fixed, one sentence, falsifiable | the run has not converged on a question; stop adding claims |
| **5** | an argument map: claims, the evidence for each, and the dependency edges | the argument is a list, not a structure |
| **8** | forced convergence — the current state is declared final and the open items are closed or dropped | stop round 8; a ninth round has never produced a new claim |

**Why round 8 forces convergence.** Rounds 9+ reliably produce restatements. The signal that the argument is done is that new rounds start paraphrasing old ones, and that signal is indistinguishable from progress unless the calendar decides.

**Final state** is declared by the author explicitly ("the outline is final"), not inferred by the absence of objections. Silence is not agreement.

## The per-round quality gate

Every round must produce four things. A round that produces only text has not happened.

| # | Output | Test |
|---|---|---|
| 1 | **claim list with verdicts** | each claim: survives / survives-narrowed / falls, as in `attack.md` |
| 2 | **delta since the previous round** | what changed, in at most three lines |
| 3 | **drops** | which claims were removed, and the objection that removed them |
| 4 | **the open question for the next round** | one question, phrased as answerable |

Why all four:

- Without (1) the round is a discussion.
- Without (2) the document cannot be read as a history, only as a snapshot.
- Without (3) claims quietly reappear two rounds later, having never been refuted — only unmentioned.
- Without (4) the next round starts by re-deciding what to work on.

**Counter-example:** a challenge run of eleven rounds with no drops recorded. The final document contained two claims that had been refuted in round 3 and one that had been refuted twice. Both refutations were in the transcripts; neither reached the document, because there was no step that required them to.

## What this mode does not do

| Not in scope | Where it goes |
|---|---|
| writing paper prose | nowhere in this pipeline — prose is the author's |
| producing new experimental results | the author's lab |
| deciding whether a cited claim holds | `evidence-audit` |
| comparing papers | `synthesis-matrix` |
| judging whether the paper is publishable | no skill can; that is a reviewer's judgement |

The boundary is deliberate: an argument map is a research artefact, and a paper is a rhetorical one. Crossing that boundary turns a tool that sharpens thinking into a tool that generates confident text about work that may not exist.

## Counter-examples, collected

| Symptom | Diagnosis |
|---|---|
| nine claims, one source | entry gate skipped |
| no RQ by round 4 | claims accumulating without a question |
| argument map that is a list | no dependency edges; nothing depends on anything |
| round 9, 10, 11 | convergence not forced |
| "no objections, so it is final" | finality inferred from silence |
| refutations in transcripts but not in the document | no drops record |

## Checklist

- [ ] Three or more supporting papers, or the mode did not start.
- [ ] RQ fixed by round 3, one sentence, falsifiable.
- [ ] Argument map with dependency edges by round 5.
- [ ] Convergence forced at round 8.
- [ ] Every round produced verdicts, a delta, drops, and one open question.
- [ ] Finality declared explicitly, never inferred.
