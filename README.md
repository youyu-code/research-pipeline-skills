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

## 中文说明

本仓库把「文献雷达 → 论文卡片 → 综合矩阵 → 提案锻造」整条科研流水线拆成可独立调用的 Agent Skills。

- **`research-ops` 是底座**：只承载状态（扫描位点、推送日志、矛盾登记、TODO）与交付格式，不产出任何研究结论，其余五个 skill 都往它写。
- **`evidence-audit` 是横切能力**：对单条主张做「成立／不成立／不可判定」的裁定，并把证据边界一并写出。`proposal-forge` 引用它，不自建判据——这是本仓库唯一的跨 skill 引用。
- **`paper-card` 是唯一的硬依赖入口**：它的 `scripts/` 需要 Python；其余 skill 只读不跑代码。
- **`paper-mill` 暂不发布**：其内容（挑战轮次 + 每轮质量门）现在位于 `proposal-forge/references/challenge-mode.md`，等它在真实稿件上跑通再独立成 skill。

## Install

The only hard dependency is a Python interpreter. `paper-card` is the only skill with scripts; everything else is text.

| Component | Version floor | Needed by | If missing |
|---|---|---|---|
| Python | 3.8 | all scripts (standard library only) | nothing runs |
| `pypdf` | 3.9 | `paper-card/scripts/pdf_text.py --mode layout` | use `--mode text` instead |
| `pymupdf` | 1.23 | `pdf_text.py --mode text\|words`, `table_coords.py`, `rotated_table.py` | text extraction falls back to layout only; table rebuild unavailable |
| `curl` | any | the request examples in `literature-radar/references/rate-limits.md` | substitute any HTTP client |

No Node, no Pandoc, no LaTeX, no C toolchain.

```bash
python -m pip install "pypdf>=3.9" "pymupdf>=1.23"
```

### Cold start, three steps

**1 — Install the skills.** Copy the folders you want into your skills directory, one folder per skill (the folder name must match `name:` in the frontmatter):

```
~/.claude/skills/<name>/        or        ~/.workbuddy/skills/<name>/
```

**2 — Smoke-test the paper-card scripts, with no real paper.** The fixtures in `skills/paper-card/assets/samples/` are synthetic and exist for exactly this:

```bash
python skills/paper-card/scripts/pdf_text.py \
  --pdf skills/paper-card/assets/samples/synthetic_paper.pdf --out /tmp/t1
```

Expected: `pages=4 chars=559 verdict=partly-empty`, suspect page `[4]`. If you see that, extraction works. The full five-command self-test is in `skills/paper-card/assets/samples/README.md`.

**3 — Create your state files before the first real run.** `research-ops/references/state-files.md` defines four of them — cursor, push log, register, TODO. A first run with nowhere to write its cursor will re-scan the same window on the second run.

## Design notes

Three decisions that shape everything else:

- **One schema, one owner.** The card schema is defined once, in `paper-card/references/schema.md`, with a version number. `synthesis-matrix` declares that it consumes that version and does not restate the fields. Two copies of a schema drift within a month.
- **Record layer and adjudication layer are separate.** Cards and matrices register a problem with an ID; only a proposal or an audit rules on it. A registration is never cited as precedent for a different paper.
- **Three grading systems, no conversion.** Stopping (`B1`–`B5`), repair order (`P-1`–`P-4`), and problem type (six tags) answer different questions. Converting one into another is how a pipeline stops for a cosmetic defect and ships through a broken provenance chain.

## ROADMAP

| Item | Status |
|---|---|
| `literature-radar` | v1 — SKILL.md + 5 references; scripts planned |
| `paper-card` | v1 — SKILL.md + 6 references + 5 scripts + synthetic fixtures |
| `synthesis-matrix` | v1 — SKILL.md + 4 references |
| `proposal-forge` | v1 — SKILL.md + 5 references |
| `evidence-audit` | v1 — SKILL.md + 5 references |
| `research-ops` | v1 — SKILL.md + 4 references |
| `paper-mill` | **planned** — ships as `proposal-forge/references/challenge-mode.md` until it has been run end to end on a real manuscript |
| radar scripts (`scan` / `score` / `selfcheck` / `regress` / `miss_diag`) | planned |
| case library, expanded | planned — generalizable kernels only, private specifics stripped |

## Credits and prior art

This pipeline existed in a private form before this repository; the skills were extracted from working notes, not written to match an existing product.

**No text, code, prompt, or schema from any third-party skill is reproduced here.** A licensing audit of the skills already installed in the author's environment found **no LICENSE file in any of them** — which means default copyright applies, and nothing could be reused even if it had been useful. The audit's only lasting effect is the compatibility notes below.

Skills you may already have installed that overlap with this repository, and how to choose:

| Installed skill | Overlaps with | Guidance |
|---|---|---|
| `daily-literature-digest` | `literature-radar` | both do recurring keyword monitoring. This repo's version is stricter about coverage proof and window definitions; the other has working email delivery and more sources. Until `literature-radar` ships its scripts, that one is the more complete tool. |
| `paper-ingest-vault` | `paper-card` | that one writes reading notes into an Obsidian vault; `paper-card` writes a provenance-carrying card. Different outputs, both legitimate. |
| `zotero-cli` | nothing — it is a tool | `paper-card`'s Tier-2 path assumes a `zotero` CLI exists; `zotero-cli` is a working example of one. Named for orientation, not required. |
| `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`, `deep-research`, `sr-screener`, `paper-vault`, `speech-writing-master`, `remotion-video-toolkit` | none | different stages or different domains. This repo stops at the proposal; it deliberately does not write paper prose. |

## License

Apache-2.0
