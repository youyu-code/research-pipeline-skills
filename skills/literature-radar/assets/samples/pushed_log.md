# Push log (synthetic)

Append-only record of what was delivered. `id` is the identity; the title is a
cached label and may lag upstream edits. This fixture holds one item so the
regression can show what "a previously-pushed item disappeared" looks like.

| date | id | title | source | score | block |
|---|---|---|---|---|---|
| 2026-01-03 | 2601.00002 | A survey of widget assembly | cs.LG | 5 | daily |
