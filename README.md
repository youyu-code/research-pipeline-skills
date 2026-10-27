# research-pipeline-skills

Agent Skills (Anthropic format) for running a literature-driven research pipeline end to end — from daily paper tracking to an adversarially tested research proposal.

```
  literature-radar        paper-card          synthesis-matrix        proposal-forge
  ┌──────────────┐      ┌────────────┐      ┌────────────────┐      ┌───────────────┐
  │ arXiv scan   │ ───▶ │ one PDF    │ ───▶ │ cross-paper    │ ───▶ │ protocol +    │
  │ keyword score│      │ → one card │      │ matrix + gaps  │      │ attack rounds │
  └──────────────┘      └────────────┘      └────────────────┘      └───────────────┘
         │                    │                      │                      │
         └────────────────────┴──────────┬───────────┴──────────────────────┘
                                         ▼
                              ┌────────────────────┐        ┌──────────────┐
                              │   evidence-audit   │◀───────│ research-ops │
                              │ claim → verdict    │        │ state, logs  │
                              └────────────────────┘        └──────────────┘
```

`evidence-audit` is cross-cutting: it rules on single claims and is invoked by `proposal-forge`.
`research-ops` carries state (scan cursor, push log, contradiction register) so the other skills stay stateless.

## Skills

| Skill | Use it when | Output |
|---|---|---|
| [`literature-radar`](skills/literature-radar/) | recurring tracking of new preprints for a fixed window | digest + updated cursor + self-check log |
| [`paper-card`](skills/paper-card/) | you have a paper (PDF / folder) and need one structured card | card (schema v1) + source trail + extraction log |
| [`synthesis-matrix`](skills/synthesis-matrix/) | ≥2 cards exist and the question is comparison | matrix + gap notes |
| [`proposal-forge`](skills/proposal-forge/) | you have a matrix and gaps and need a defended proposal | proposal + attack/review layers |
| [`evidence-audit`](skills/evidence-audit/) | you have one claim with numbers and need a verdict | verdict + tier + attribution |
| [`research-ops`](skills/research-ops/) | you need to update pipeline state, not produce research output | state files + three-line delivery note |

## 中文说明

本仓库把「文献雷达 → 论文卡片 → 综合矩阵 → 提案锻造」整条科研流水线拆成可独立调用的 Agent Skills。
`evidence-audit` 是横切能力：对单条主张做「成立／不成立／不可判定」的裁定，`proposal-forge` 引用它而不自建判据。
`research-ops` 只承载状态（扫描位点、推送日志、矛盾登记），保证其余 skill 无状态、可重入。

## Install

<!-- TODO: M3 — per-skill dependency list, folder conventions, cold start sequence -->

## ROADMAP

| Item | Status |
|---|---|
| `literature-radar` | v1 |
| `paper-card` | v1 |
| `synthesis-matrix` | v1 |
| `proposal-forge` | v1 |
| `evidence-audit` | v1 |
| `research-ops` | v1 |
| `paper-mill` | **planned** — challenge-mode content currently ships inside `proposal-forge/references/challenge-mode.md`; it becomes a standalone skill once it has been run end to end on a real manuscript |
| case library (`references/case-studies.md`) | planned — generalizable kernels only, private specifics stripped |

## License

Apache-2.0
