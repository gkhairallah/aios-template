# Conventions — the AIOS nomenclature standard (fallback copy)

> Prefer the vault's own `30 Atlas/Conventions.md` when present. This is the fallback.

## Frontmatter fields
| Field | Applies to | Values |
|---|---|---|
| `type` | every note | `daily-log` · `project` · `area` · `atlas` · `resource` · `decision` · `moc` |
| `status` | project | `active` · `on-hold` · `done` |
| `status` | decision | `proposed` · `decided` · `superseded` |
| `priority` | project | `high` · `medium` · `low` |
| `deadline` | project | `YYYY-MM-DD` |
| `area` | project | `"[[Area]]"` (optional functional grouping) |
| `review` | area | `weekly` · `monthly` · `quarterly` |
| `entity` | any note (optional) | **list** of business slugs + `shared`. Presence = business; absence = personal. |
| `created` | evergreen notes | `YYYY-MM-DD` (project, area, atlas, resource, moc) |
| `date` | time-anchored notes | `YYYY-MM-DD` (daily-log, decision) |
| `source` | atlas, resource | free text / URL |
| `related` | any (esp. decision) | list of `[[links]]` |
| `tags` | every note | array; first tag = the type; **always the last field** |

`entity` is a list: one business → `[company-a]`; two → `[company-a, company-b]`; company-wide → `[shared]`; personal → blank.

## Standard section headers
- **Project:** 🎯 Outcome · 🔗 Canonical Sources · 📌 Current Focus · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related
- **Area:** 🎯 Standard · 🔗 Canonical Sources · 🚀 Active Projects · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related
- **Business hub (area):** 🎯 Standard · 🔗 Canonical Sources · 🚀 Projects · 🗂️ Areas & Functions · 🧠 Decisions · 📚 Knowledge · 📝 Notes · 🔗 Related
- **Atlas:** 📄 Summary · 📝 Notes · 🔗 Related
- **Resource:** 🔗 Source · 📝 Key Points · 🔗 Related
- **Decision:** ❓ Problem · ⚖️ Options Considered · ✅ Decision · 💭 Reasoning · ⚠️ Tradeoffs · 📌 Follow-up · 🔗 Related
- **MOC:** 🗂️ Notes · 🔗 Related

## Rules
- Every note ends with `## 🔗 Related` (bulleted `[[links]]`).
- `🔗 Canonical Sources` = link to where the real artifact lives; never paste a duplicate.
- `🧠 Decisions` and `🗒️ Log` are live Dataview — self-populate; don't hand-fill.
- Emoji headers everywhere, one per header.
- Obsidian holds your *thinking*, not your *documents*: authored knowledge lives in the vault; source documents stay in their system of record and are linked.

## Mutability — snapshots vs living notes
The `date:` / `created:` split above is the **mutability flag**.
- **`date:`** (`daily-log`, `decision`) = **snapshot** — a fixed record of one moment. **Never
  retro-edit it.** Not a generated daily brief, not an hourly log row, not a dated recap callout,
  not a decision's reasoning.
- **`created:`** (`project`, `area`, `atlas`, `resource`, `moc`) = **living note** — a projection of
  now. **Never let it go stale.** Status, dates, deadlines, owners, blockers must match reality today.

**Write-through (load-bearing):** a snapshot and the living notes it affects are written in the
**same pass**. Every capture = two writes — the dated block, *and* the living surfaces it changes
(frontmatter `status`/`priority`/`deadline`, `🎯 Outcome`, `📌 Current Focus`, `🔗 Canonical
Sources`, `📝 Notes`). Superseded `📌 Current Focus` lines are **removed or rewritten, never
stacked** — that section holds no history.

**Mixed cases:** dated `### YYYY-MM-DD — …` sections and dated callouts *inside* a living note are
snapshots (append, never revise). Conversely, a decision's `📌 Follow-up` checkboxes and its
`status` (`proposed → decided → superseded` + a `related` link) are **living** — superseding a
decision means a **new** decision note, never a rewrite of the old one's options or reasoning.

**Stale ≠ wrong.** *Stale* = accurately recorded, since superseded → never touch it; new truth goes
in a new dated block plus the living surfaces. *Wrong* = misrecorded what was true at the time (bad
figure, wrong name, broken link) → correct in place, **visibly**: inline `[corrected YYYY-MM-DD: was
"X"]`, or a `> [!failure]- Correction — YYYY-MM-DD` callout for anything substantial.

**When they disagree, the living note wins** — the snapshot isn't wrong, it's old. Never answer
"what's the status of X?" from the daily logs; answer from the effort note and cite the log only as
evidence of timing or of what was known then.

**Supersede and fold — never delete.** Superseded tracks, plans and decisions are *moved and
marked*, not removed: fold them into a dated `📝 Notes` heading (`### Retired tracks`,
`### Delivery timeline`) verbatim, and flip a decision's `status:` to `superseded` with a
`> [!info] ⛔ Superseded YYYY-MM-DD by [[...]]` callout rather than rewriting it. **Rationale is
evidentiary, not cosmetic:** what was believed and when — and what changed it — is the argument in
any commercial or legal dispute. Where a chain of decisions exists, index it in the effort note as
a decision timeline (date · status · one line · link).
