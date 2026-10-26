---
description: Set a note's status (active | on-hold | done) — fast, no doctrine load
---

Fast, mechanical edit — use the **vault-ops** Fast path. Input: $ARGUMENTS

Resolve the vault from `~/.aios/config.json`. Resolve the target note: if it's already in the
conversation, use it; otherwise match the user's (possibly partial) name against note
filenames/titles — cheaply, no full-content search — and ask only if ambiguous. Exact titles aren't
required. Change **only** the `status:` frontmatter property to the
value given (`active` | `on-hold` | `done`). Do **not** load Filing Rules/Conventions, do **not**
reformat, do **not** explain. If they also say "archive" a `done` note, move it to `90 Archives/`.
Confirm in one line.
