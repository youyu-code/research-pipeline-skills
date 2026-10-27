# AGENTS.md

Repository of open-source Agent Skills (Anthropic Agent Skills format) implementing a research pipeline:
**literature radar → paper cards → synthesis matrix → proposal forging → evidence audit**.

## Layout

```
skills/<skill-name>/
  SKILL.md          # frontmatter: name + description (≤1024 chars)
  references/       # progressive-disclosure detail layer
  scripts/          # runnable helpers
  assets/           # templates, icons, static resources
```

- `name` matches the folder name: **≤64 chars, lowercase letters / digits / hyphens only**.
- `SKILL.md` stays lean: trigger conditions, inputs, outputs, routing into `references/`.
- Long tables, examples, edge cases live in `references/`.
- One cross-skill reference is allowed: `proposal-forge` → `evidence-audit`. Everything else is self-contained; do not add routing chains.

## Quality gate (before commit)

- **No private data.** No credentials, personal absolute paths, usernames, private library names, or session/timestamp directory names (`YYYY-MM-DD-HH-MM-SS` session folders, `_scanMMDD` run folders).
- **Scripts run standalone.** No dependency on a local absolute path; inputs via arguments.
- **Graceful degradation.** Without a Zotero MCP server, the manual path must still work end to end.
- **Judgment rules carry a counter-example.** Any rule that tells the agent how to *judge* (what counts as a defect, a reversal, a valid objection) must ship with at least one worked counter-example showing a plausible-but-wrong application. Definitions alone are not accepted — they get read as courtesy prose.
- **Case library ships in three tiers.** Fully generalizable cases go inline (currently ~30). Cases that only carry a generalizable *kernel* go to `references/case-studies.md` with private specifics stripped. Cases tied to one paper's numbers are not published at all.

## License

Apache-2.0.
