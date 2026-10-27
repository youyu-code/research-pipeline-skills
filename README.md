# research-pipeline-skills

Agent Skills (Anthropic format) for running a literature-driven research pipeline end to end — from daily paper tracking to an adversarially tested research proposal.

```
  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
  │literature-radar│─▶│   paper-card   │─▶│synthesis-matrix│─▶│ proposal-forge │
  │window → scored │  │PDF → card with │  │cards → matrix  │  │design → attack │
  │items + report  │  │provenance      │  │+ gap notes     │  │→ repair order  │
  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
                                                                       ╎
                                                                       ╎ planned
                                                                       ▼
                                                            paper-mill (argument
                                                            rounds, quality gates)

  ══════════════════════════════════════════════════════════════════════════════
   research-ops    state layer under all four: cursor · push log · register ·
                   TODO · three-line delivery note
  ══════════════════════════════════════════════════════════════════════════════
  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
   evidence-audit  cross-cutting: one claim → one verdict, with its evidence
                   boundary. Called by proposal-forge; usable on its own.
  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
```

`research-ops` sits under everything because each of the four stages needs somewhere to write state; it produces no research output of its own.
`evidence-audit` is cross-cutting: it rules on a single claim, so it can be called from a card, a matrix, or a proposal.

## Skills

| Skill | Use it when | Output |
|---|---|---|
| [`literature-radar`](skills/literature-radar/) | recurring tracking of new preprints for a fixed window | digest + updated cursor + self-check log |
| [`paper-card`](skills/paper-card/) | you have a paper (PDF / folder) and need one structured card | card (schema v1) + source trail + extraction log |
| [`synthesis-matrix`](skills/synthesis-matrix/) | ≥2 cards exist and the question is comparison | matrix + gap notes |
| [`proposal-forge`](skills/proposal-forge/) | you have a matrix and gaps and need a defended proposal | proposal + attack/review layers |
| [`evidence-audit`](skills/evidence-audit/) | you have one claim with numbers and need a verdict | verdict + tier + attribution |
| [`research-ops`](skills/research-ops/) | you need to update pipeline state, not produce research output | state files + three-line delivery note |

Each skill is self-contained: `SKILL.md` plus `references/`, `scripts/`, `assets/`. Install only the ones you need — but `synthesis-matrix` consumes cards, so it is not useful without `paper-card`.

**Examples.** [`examples/`](examples/) holds three cards built from public arXiv papers by these scripts — each one chosen because it broke something different — plus the record of a live radar attempt that was blocked before it reached the endpoint. No PDFs are redistributed; every card names the file it came from and the mode it was read in.

## 中文说明

本仓库把「文献雷达 → 论文卡片 → 综合矩阵 → 提案锻造」整条科研流水线拆成可独立调用的 Agent Skills。

- **`research-ops` 是底座**：只承载状态（扫描位点、推送日志、矛盾登记、TODO）与交付格式，不产出任何研究结论，其余五个 skill 都往它写。
- **`evidence-audit` 是横切能力**：对单条主张做「成立／不成立／不可判定」的裁定，并把证据边界一并写出。`proposal-forge` 引用它，不自建判据——这是本仓库唯一的跨 skill 引用。
- **`paper-card` / `literature-radar` / `research-ops` 带脚本**：分别为 5、5、1 个，全部标准库；其余三个 skill 纯文本，只读不跑代码。
- **`paper-mill` 暂不发布**：其内容（挑战轮次 + 每轮质量门）现在位于 `proposal-forge/references/challenge-mode.md`，等它在真实稿件上跑通再独立成 skill。

## Install

The only hard dependency is a Python interpreter. `paper-card`, `literature-radar` and `research-ops` ship scripts; `synthesis-matrix`, `proposal-forge` and `evidence-audit` are text only.

| Component | Version floor | Needed by | If missing |
|---|---|---|---|
| Python | 3.8 | all scripts (standard library only) | nothing runs |
| `pypdf` | 3.9 | `paper-card/scripts/pdf_text.py --mode layout` | use `--mode text` instead |
| `pymupdf` | 1.23 | `pdf_text.py --mode text\|words`, `table_coords.py`, `rotated_table.py` | text extraction falls back to layout only; table rebuild unavailable |
| `curl` | any | only the hand-run examples in `literature-radar/references/rate-limits.md`; `scan.py` fetches with `urllib` | substitute any HTTP client |

No Node, no Pandoc, no LaTeX, no C toolchain.

```bash
python -m pip install "pypdf>=3.9" "pymupdf>=1.23"
```

### Cold start, three steps

**1 — Install the skills.** Copy the folders you want into your skills directory, one folder per skill (the folder name must match `name:` in the frontmatter):

```
~/.claude/skills/<name>/        or        ~/.workbuddy/skills/<name>/
```

**2 — Smoke-test the scripts, with no real data.** The fixtures in `skills/*/assets/samples/` are synthetic and exist for exactly this.

```bash
python skills/paper-card/scripts/pdf_text.py \
  --pdf skills/paper-card/assets/samples/synthetic_paper.pdf --out /tmp/t1
```

Expected: `pages=4 chars=559 verdict=partly-empty`, suspect page `[4]`. If you see that, extraction works. Character totals move a little between `pymupdf` releases — the verdict word and the suspect page are the real assertion, not the count. The full five-command paper-card self-test is in `skills/paper-card/assets/samples/README.md`.

The radar chain runs the same way, against a five-entry synthetic Atom feed and with no network:

```bash
python skills/literature-radar/scripts/scan.py \
  --corpus skills/literature-radar/assets/samples/raw \
  --out /tmp/radar --since 2026-01-01 --until 2026-01-07 --source cs.LG

python skills/literature-radar/scripts/score.py \
  --scan-dir /tmp/radar --config skills/literature-radar/assets/samples/profile.json
```

Expected: `items=5 expected=5` from the scan, then three graded entries (A, B, C) from the score, plus one entry killed by a negative term and one below the gate. `selfcheck.py`, `regress.py` and `miss_diag.py` continue the chain; `tests/t3_scripts_smoke.py` runs all five.

**3 — Create your state files before the first real run.** `research-ops/references/state-files.md` defines four of them — cursor, push log, register, TODO. A first run with nowhere to write its cursor will re-scan the same window on the second run. Write the read-only manifest in the same sitting: `research-ops/scripts/check-sources.py --manifest sources.sha256 --root <input-dir>` is what turns "I did not touch the corpus" into a record.

### Cross-agent

A skill is markdown plus, in one case, Python. Nothing here is tied to a vendor: any agent that can read a file and run a shell command can use the whole set.

| Agent | Where the instructions go | Note |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` (or `.claude/skills/` inside a project) | reads `SKILL.md` frontmatter natively |
| Codex and other AGENTS.md readers | repository root | `AGENTS.md` holds the quality gates; `CLAUDE.md` is a one-line pointer to it so the two cannot diverge |
| Anything else (a chat UI, a local script, a different CLI) | anywhere readable | point it at `skills/<name>/SKILL.md` and treat the body as instructions |

Two mechanical requirements survive any translation: the folder name must equal `name:` in the frontmatter, and the `scripts/` folders must be reachable from a Python interpreter. There is no server, no build step, and no index to regenerate.

## Verification

One command, and it is the only release gate:

```bash
python tests/run_all.py
```

Expected last line: `ALL GREEN`. Five tests, all standard library:

| Test | Asserts |
|---|---|
| `t1_frontmatter` | six `SKILL.md` files: `name` matches the folder and the character rules, `description` ≤ 1024 chars, and states trigger + input + output |
| `t2_check_card` | the demo card passes with 9 provenance values; a card broken in three places fails with exactly 4 violations |
| `t3_scripts_smoke` | eleven product scripts answer `--help`; the paper-card five run on regenerated fixtures, the radar five on an offline Atom feed, `check-sources` on a two-class hash fixture |
| `t4_desensitize` | no credentials, account names, absolute paths, session IDs or private numeric fingerprints in any tracked file |
| `t5_research_ops_negatives` | the three "does not trigger" prompts still route away from `research-ops` |

`pypdf` and `pymupdf` are optional here: without them the PDF checks report `SKIP` instead of failing, and the summary counts the skips rather than hiding them.

One skip you should expect on a fresh clone: `t4` also checks a numeric fingerprint blacklist, and **that list is deliberately not in the repository** — a file naming the values to forbid would publish them. It lives in `tests/fingerprints.local.txt`, which is gitignored; when it is absent, `t4` reports `SKIP` for that class and still checks the five that can be described without publishing anything.

## Design notes

Three decisions that shape everything else:

- **One schema, one owner.** The card schema is defined once, in `paper-card/references/schema.md`, with a version number. `synthesis-matrix` declares that it consumes that version and does not restate the fields. Two copies of a schema drift within a month.
- **Record layer and adjudication layer are separate.** Cards and matrices register a problem with an ID; only a proposal or an audit rules on it. A registration is never cited as precedent for a different paper.
- **Three grading systems, no conversion.** Stopping (`B1`–`B5`), repair order (`P-1`–`P-4`), and problem type (six tags) answer different questions. Converting one into another is how a pipeline stops for a cosmetic defect and ships through a broken provenance chain.

## ROADMAP

| Item | Status |
|---|---|
| `literature-radar` | v1 — SKILL.md + 5 references + 5 scripts |
| `paper-card` | v1 — SKILL.md + 6 references + 5 scripts + synthetic fixtures · **live-proven 2026-10-27** on three public arXiv papers ([`examples/cards/`](examples/cards/)) |
| `synthesis-matrix` | v1 — SKILL.md + 4 references |
| `proposal-forge` | v1 — SKILL.md + 5 references |
| `evidence-audit` | v1 — SKILL.md + 5 references |
| `research-ops` | v1 — SKILL.md + 4 references + 1 script |
| `paper-mill` | **planned** — ships as `proposal-forge/references/challenge-mode.md` until it has been run end to end on a real manuscript |
| radar scripts (`scan` / `score` / `selfcheck` / `regress` / `miss_diag`) | **scripts shipped (v1)** — offline replay and run-log reconciliation tested; the live endpoint is first exercised in v1.1. First live attempt 2026-10-27 never reached the endpoint: the local proxy answers `CONNECT export.arxiv.org:443` with `502`, measured in [`examples/radar-live-attempt-2026-10-27.md`](examples/radar-live-attempt-2026-10-27.md) |
| case library, expanded | planned — generalizable kernels only, private specifics stripped |

Two rows above set expectations, so read them before installing:

- **`paper-mill` is not a folder.** The challenge rounds and the per-round quality gate live in `proposal-forge/references/challenge-mode.md`. It becomes a skill after it has been run end to end on a real manuscript — not before, because a quality gate that has never failed anything is a claim, not a gate.
- **`literature-radar` ships scripts whose live path is unproven.** The five scripts run end to end against an offline Atom fixture, and `selfcheck.py` reconciles the run log they leave. Nothing here has yet been pointed at the live endpoint in anger: the rate-limit handling is implemented to the written rules, not measured against the endpoint's current behaviour. Treat your first real run as the measurement, and expect to tune `--retry-wait` for your own network. The offline path (`scan.py --corpus`) is the one this repository tests.

## Credits and prior art

This pipeline existed in a private form before this repository; the skills were extracted from working notes, not written to match an existing product.

**No text, code, prompt, or schema from any third-party skill is reproduced here.** Eleven skills already installed in the author's environment were audited. **None of them carries a LICENSE file** — two carry marketplace metadata with no license field and no repository link — so default copyright applies and nothing could be reused even where it overlapped. The audit produced no reuse and no removals: ten coexist with this repository because they solve the same job differently, and one (`zotero-cli`) is an ordinary tool rather than a competing skill. Names are the only thing carried over, and only so you can tell which is which.

Skills you may already have installed that overlap with this repository, and how to choose:

| Installed skill | Overlaps with | Guidance |
|---|---|---|
| `daily-literature-digest` | `literature-radar` | both do recurring keyword monitoring, and both are complete — choose on what you need. This repository's version is stricter about coverage proof and window definitions (a run must be able to show the window was actually read); the other has working delivery channels and more sources wired up. |
| `paper-ingest-vault` | `paper-card` | that one writes reading notes into an Obsidian vault; `paper-card` writes a provenance-carrying card. Different outputs, both legitimate. |
| `zotero-cli` | nothing — it is a tool | `paper-card`'s Tier-2 path assumes a `zotero` CLI exists; `zotero-cli` is a working example of one. Named for orientation, not required. |
| `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `deep-research`, `sr-screener`, `paper-vault`, `speech-writing-master`, `remotion-video-toolkit` | none | different stages or different domains. This repo stops at the proposal; it deliberately does not write paper prose. |

## License

Apache-2.0
