---
name: paper-card
description: >-
  Build one structured paper card from one paper: extract full text from a PDF,
  classify supplementary-material status, transcribe tables with coordinate-based
  verification, and record which numbers are citable versus which are not. Use when
  the input is a paper — a single PDF, a Zotero attachment, or a folder of PDFs —
  and the output should be one card following the card schema, carrying a source
  trail, an extraction-failure log, and a to-be-filled section. Folder-driven by
  default: point it at a directory and it processes every PDF inside; a Zotero MCP
  server only accelerates lookup and is never a prerequisite. It does not compare
  papers across a corpus (use synthesis-matrix), and it does not adjudicate whether
  a claim is true or exaggerated (use evidence-audit).
---

<!-- TODO: M3 — body: schema v1 / 抽取决策树 / SI 三档判据 / 引用规则 B-27..B-37 前半 / 手动降级动作序列 → references/ -->
