# Getting the PDFs — three tiers, declared before use

> **Report your tier first.** Every card run starts with a three-line declaration:
> `tier: 1|2|3 · implementation: <name@version> · capabilities-probed: <list>`
> If any of those three cannot be filled from evidence, write `[BLOCKER-waiting-for-user]` and stop.
> **Guessing an implementation name or a tool signature is worse than having no tier at all** — a wrong signature produces a plausible-looking empty result that reads like "the paper has no SI".

---

## Tier 1 — MCP server (preferred)

### 1.1 Self-report, before touching a paper

1. Locate the config actually in force. Check, in order: project-level `.mcp.json`, user-level `~/.workbuddy/mcp.json`, then whatever the host exposes as its connector list.
2. From that file (not from memory), read the `zotero` entry: server name, `command`/`args` or `url`, and any pinned version.
3. Probe the live tool list and record the **exact tool names and required arguments** you will use.
4. Write the declaration line. Example shape (values must come from your own config):

```
tier: 1
implementation: zotero-mcp@<version from config>  (server name: <name>)
capabilities-probed: search_items · get_item_children · get_attachment_path · get_item_fulltext
```

### 1.2 What to probe, and what each answer means

| Capability | Why the card needs it | If absent |
|---|---|---|
| list children of an item | the only way to answer `si-state` | `si-state` becomes `unknown` — not `none` |
| resolve an attachment to a local path | the only way to open the PDF | fall back to tier 3 |
| fetch item metadata (DOI, venue, pages) | decides `version` | read the PDF's first page and mark `version-evidence: from-pdf` |
| fetch annotations / notes | optional convenience | proceed without |

**Rule:** capability absent ⇒ the field becomes `unknown`/`unverified`. It never becomes `none`, and it never becomes a guess.

### 1.3 Signature drift

MCP tool names are not a stable standard. Two implementations may both offer "get children" under different names and different return shapes. Record the signature you actually called:

```
call: <tool_name>(<arg>=<value>) -> {n_children: 2, items: [{key, filename, pages}]}
```

If a later run sees a different shape, re-declare the tier. Do not silently coerce.

---

## Tier 2 — `zotero` CLI

### 2.1 Self-report

```
tier: 2
implementation: zotero-cli@<version from `zotero --version`>
auth: <how the credential is supplied — env var name, config file, or "not required">
capabilities-probed: <fill from the table below>
```

### 2.2 Capability probe

Run the CLI's own help output and map it against this table. **Do not paste a command you have not seen in that help text** — the point of the probe is to discover the real flag names.

| Capability | What you need to be able to do | Reproducible command (fill with the real flags) |
|---|---|---|
| search items | find an item by title/DOI | `<cli> search --query "<title>"` |
| list children | enumerate attachments of an item | `<cli> children <item-key>` |
| resolve path | print the local file path of an attachment | `<cli> path <attachment-key>` |
| export metadata | dump DOI / venue / pages | `<cli> item <item-key> --format json` |

Record the actual output of each probe in the card's extraction log (one line per capability: `ok` / `absent` / `errored`).

### 2.3 Failure handling

- CLI present but unauthenticated ⇒ tier 2 unusable, drop to tier 3, and say so in `si-note`.
- CLI returns partial data (e.g. children listed but no paths) ⇒ tier 2 for enumeration + tier 3 for opening files. Declare the **mixed** tier: `tier: 2+3`.

---

## Tier 3 — plain files (always available)

### 3.1 Folder convention

```
papers/<paper-id>/
  00-main.pdf            # body text, always present
  01-si.pdf              # independent supplementary, optional
  02-si-tables.xlsx      # non-PDF supplementary, optional, any count
  03-si-methods.docx
```

`<paper-id>` = `firstauthor<year>_<shorttitle>`, the same stem the card uses. Multiple supplementary files are allowed and expected — **counting only PDFs is the mistake that makes a complete SI look absent**.

### 3.2 Pairing heuristic (run on every multi-PDF directory)

Score each candidate (main, other) pair. Print the table. Do not skip the print — the point is that a human can see a wrong row.

| Signal | Points | How to compute |
|---|---|---|
| filename stem similarity | 0–2 | strip extensions and the tokens `main/supp/supplementary/si/sm/appendix`; compare the remaining prefix. 2 = identical prefix, 1 = one is a prefix of the other, 0 = unrelated |
| page-count asymmetry | 0–1 | SI usually ≥ body. 1 if `pages(si) > pages(main)`, else 0 |
| first-page self-declaration | 0–2 | does page 1 of the candidate say Supplementary / Supporting Information / Electronic Supplementary Material / Appendix? 2 = explicit, 1 = contains "supplement" anywhere on page 1, 0 = no |
| shared parent / adjacency | 0–2 | same directory + adjacent ordering, or an explicit parent-child relation in metadata. 2 = explicit relation, 1 = same directory only |

**Thresholds**

| Score | Action |
|---|---|
| ≥ 4 | pair, mark `confidence: high` |
| 2–3 | **stop and ask the user.** Print both candidates, both first-page heads, and the score breakdown. Never resolve this yourself. |
| < 2 | do not pair. Treat as separate papers. |

**Forbidden:** assigning an SI to a body because it is "the only other PDF in the folder". That single heuristic is responsible for cross-paper contamination, and it is silent — every number still parses.

### 3.3 D-06 action sequence (manual path, end to end)

1. Ask the user for a directory, or create `papers/<paper-id>/` yourself and tell them where to drop files.
2. Enumerate `*.pdf`, `*.xlsx`, `*.docx`, `*.csv` — **all four**, not just PDFs.
3. Run the pairing heuristic; print the table; stop on any medium-confidence row.
4. Extract each body PDF: `python scripts/pdf_text.py --pdf <path> --out txt/<paper-id>/ --mode layout`, then read `_health.json`.
5. If `verdict` is `layout-failed`, re-run with `--mode text`; if still `mostly-empty`, `--mode words` and fall back to rendering + transcription for the specific pages that hold results.
6. Extract non-PDF supplementary: `python scripts/office_tables.py --in <file> --out csv/<paper-id>/`, then read `<stem>.manifest.csv` to confirm row/column counts before trusting a cell.
7. Record every path, mode, threshold and failure in the card's extraction log.
8. If a table cannot be recovered by any of the above, put the specific cell in the to-be-filled section with `reason: extraction-failed` and `blocker: blocks-citation`. Do not write an approximate number.

### 3.4 What tier 3 cannot do

- It cannot answer "does this paper have an SI that is not in my folder". That answer is `unknown`, not `none`.
- It cannot verify the version (preprint vs formal) unless the PDF itself carries a DOI, a running head with volume/pages, or an acceptance statement.
- It cannot discover that a newer supplementary file exists. `si-state` must therefore carry a date.
