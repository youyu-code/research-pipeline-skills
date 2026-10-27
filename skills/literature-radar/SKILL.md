---
name: literature-radar
description: >-
  Periodic literature radar over arXiv: runs a keyword-scored scan for a fixed time
  window, emits a per-day digest, and self-checks coverage before reporting. Use
  when the task is recurring new-paper tracking — probe the index ceiling, fetch
  per-category Atom feeds, score entries against a tiered keyword list, verify
  counts and coverage depth, write a daily or backfill report, tune the keyword
  list with quantified recall/noise deltas, or diagnose why a known paper was
  missed. Input: a keyword config, a scan window [S, E), and a scan cursor.
  Output: digest markdown, an updated cursor, and a machine-checkable self-check
  log. It works on abstracts only: it never reads full texts and never builds
  paper cards (use paper-card for that).
---

<!-- TODO: M3 — body: 窗口口径 / 限流分诊 / 原子下载 / selfcheck 四校验 / 词表调参四前置 → references/ -->
