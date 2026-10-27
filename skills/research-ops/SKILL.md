---
name: research-ops
description: >-
  Operating layer for a multi-stage research pipeline: maintains the scan cursor,
  push log, contradiction register, TODO list, and delivery format across stages.
  Use when the task is to update or reconcile pipeline state rather than to produce
  research output — record a scan position, log pushed items, register a
  contradiction under an ID, close a TODO, verify that read-only source files are
  unchanged via hash check, or report what changed in a batch. Input: existing
  state files plus one change event. Output: updated state files and a three-line
  delivery note (files touched / next step / newly registered items). It does not
  produce paper cards, matrices, proposals, or verdicts — those belong to
  paper-card, synthesis-matrix, proposal-forge, and evidence-audit respectively.
---

<!-- TODO: M3 — body: 状态文件契约 / 三行交付格式 / B1–B5 停手判据 / 登记区规则 → references/ -->
