---
name: vault-ops
description: Operate on and maintain an existing AIOS/Obsidian vault. Use when the user says "log this", "add to my hourly log", "set my top 3", "mark X done", "archive X", "refile this", "fix this note", "link these notes", "build a MOC", "weekly review", "what does my vault say about…", "find in my notes", or otherwise wants to update, maintain, or query existing notes (as opposed to creating a brand-new note — use the capture-note skill for that). Always follows the vault's Filing Rules and Conventions and shows changes before writing.
unlisted: true
---

# Vault Ops

Read, update, maintain, and query an existing AIOS vault. Follow the vault's conventions, and
always show proposed changes to existing notes and get approval before writing.

## Setup (every operation)
1. **Resolve the vault fast:** read `~/.aios/config.json` → `vaultPath` and use it directly (don't search the filesystem). If it's missing, ask for the vault location (or have them run `/aios-init`) and save it there. The vault is the folder containing `30 Atlas/` and `Templates/`.
2. **Load doctrine only when needed.** For a classification / new-structure / refile task, load `30 Atlas/Conventions.md` and `30 Atlas/Filing Rules.md` (authoritative; fallback = the copies bundled with `capture-note`). For a simple edit to an already-conforming note, **skip this entirely** — see the Fast path below.
3. For any change to an EXISTING note, show the exact edit and get approval. Never silently overwrite. Preserve Dataview blocks and any frontmatter you are not changing. Never touch `Private/` unless explicitly asked.

## ⚡ Fast path (cheap, frequent edits — use this by default for updates)
Most updates are trivial and must be **cheap and fast**. For a simple change to an existing,
already-conforming note — flip a `status`, tick a checkbox, add a `- [ ]` or a line, tweak a field,
add one `[[link]]`:
- Resolve the vault from `~/.aios/config.json`. **If the note is already in the conversation, use it directly.** If the user names a note, resolve it with a quick **filename/title match** (cheap — NOT a full-content search); ask only if the name is genuinely ambiguous. The exact title is never required.
- **Do NOT load Filing Rules or Conventions** (no classification or new structure is involved).
- Open the note, make **only** the requested change, save. Don't re-read the whole file needlessly or reformat anything else.
- Confirm in one short line; **skip the reasoning explanation** for trivial edits.

Reserve the full flow (load doctrine, search, explain) for classifying, creating structure, or refiling.

## ⏳ Mutability — never retro-edit a snapshot, never let a living note go stale
Per Conventions § ⏳ Snapshots vs Living Notes. This governs **every** write, fast path included.
- **`date:` notes are snapshots** (`daily-log`, `decision`) — a fixed record of one moment. Do not
  edit them after the fact: not a generated daily brief, not an hourly log row from a past day, not
  a dated recap callout, not a decision's options or reasoning.
- **`created:` notes are living** (`project`, `area`, `atlas`, `resource`, `moc`) — they must match
  reality today.
- **Write-through is mandatory.** Never write a dated block (meeting recap, daily-log entry) without
  updating the living notes it changes **in the same pass** — frontmatter `status`/`priority`/
  `deadline`, `🎯 Outcome`, `📌 Current Focus`, `🔗 Canonical Sources`, `📝 Notes`. Superseded
  `📌 Current Focus` lines are **removed or rewritten, never stacked**.
- **Exceptions inside snapshots:** a decision's `📌 Follow-up` checkboxes and its `status`
  (`proposed → decided → superseded` + a `related` link) are living — tick and flip those freely.
  Superseding a decision = a **new** decision note.
- **Stale ≠ wrong.** Stale (accurate then, superseded now) → never touch; add new truth elsewhere.
  Wrong (misrecorded at the time — bad figure, wrong name, broken link) → fix in place **visibly**:
  `[corrected YYYY-MM-DD: was "X"]`, or a `> [!failure]- Correction — YYYY-MM-DD` callout.
- **Reading:** when a snapshot and a living note disagree, the **living note wins**. Never answer
  "what's the status of X?" from `00 Calendar` — answer from the effort note; cite the daily log only
  as evidence of timing or of what was known then.

## Daily log operations
Locate today's daily note in `00 Calendar/` by today's date (honor any `YYYY/…` subfolder format). If it doesn't exist, create it from `Templates/Daily Note.md` first.
- **Top 3:** set or replace the three checkboxes under `## 🎯 Top 3 Today`. When suggesting
  candidates, draw only from the operator's own items — open checkboxes with no `owner::`, efforts
  whose next step is theirs. Show open **👀 Watching** items (`[owner:: [[Person]]]`, or shared-mailbox
  items per the default-owner table) as a separate "raise with…" list grouped by owner, flagging any
  past the escalation threshold (5 business days, 2 customer-facing, or their own `escalate::` date).
  Never put a watch item in the Top 3 — per Conventions § 👀 Mine vs Watching.
- **Hourly log:** add the entry to the correct time row of the `## ⏱️ Hourly Log` table; put the effort in the Project/Area column as a `[[link]]`. For a range ("all morning"), fill the relevant rows.
- **Worked On Today:** append `- [[Effort]] — what I did` under `## 🔗 Worked On Today` (this feeds the Stalled Projects tracker).
- **Evening review:** fill Wins / Blockers / Extract→PARA-Atlas / Energy.
- **Day wrap (reconstruct an unlogged day):** when the ask is "wrap up my day", "fill in what I
  missed", `/aios-notes:today wrap`, or a scheduled evening run — **load
  `references/day-wrap.md` and follow it**. It sweeps the day's sources (file mtimes first, then
  sent/received mail, chat, tickets, calendar), diffs against what's already logged, and hands back a
  draft to correct rather than a blank page. Unattended runs write to a collapsed `[!todo]` draft
  callout, never into the log tables. Personal findings are logged in a collapsed `🏠 Personal`
  fold, never in the visible sections (day-wrap § 4b).
- **Personal entries (any log operation):** a personal log entry (health, energy, feelings, family,
  home, personal errands) goes into the day's collapsed `> [!quote]- 🏠 Personal` callout directly
  below the Hourly Log table, not into the table itself. Create the fold if the day has none.

## Note lifecycle
- **Status:** change a project's `status` (`active` ↔ `on-hold` ↔ `done`). Confirm which note.
- **Archive:** when done or dormant, set `status: done` and move the file to `90 Archives/` (confirm the move).
- **Deadline / priority:** update those fields on request.

## Refile & fix
- **Refile:** if a note is misfiled, run the Filing Rules cascade, propose the correct folder + `type`, and move it on approval.
- **Fix to conventions:** align a note's frontmatter and section headers to `Conventions.md` (add a missing `type`/`tags`/`created`, correct header names). Show the diff.
- **Stamp entity:** add or adjust the `entity` list to tie a note to a business.

## Linking & MOCs
- **Insert links:** search the vault for related notes and insert `[[links]]` in the right section (usually `🔗 Related`). Propose before inserting.
- **Build / extend a MOC:** create or update a `type: moc` note in `30 Atlas/MOCs/` that links a set of related notes — the right tool for a topic that would otherwise tempt a subfolder.
- **Connect to a company:** set `entity` and/or link the relevant company hub in `10 Efforts/Companies/`.

## Weekly review
Produce a rollup from the vault (read-only unless asked to act):
- Active projects and status; **stalled** ones (no daily-log mention recently).
- **Overdue / due-soon** by `deadline`.
- **Currency check (drift patrol).** For every `status: active` project, compare `📌 Current Focus`
  and the frontmatter against the most recent evidence in `00 Calendar` and the note's own dated
  blocks. Flag any project whose Current Focus names a blocker, owner, date or dependency that later
  entries contradict or resolve — that's a write-through miss, and it is the failure mode the
  mutability rule exists to prevent. Offer to rewrite the stale lines (never the dated blocks).
- **Decisions** logged this week; flag any `status: decided` decision whose `📌 Follow-up` items are
  all complete, or that a later decision has superseded without the `status` being flipped.
- **Fleeting notes** in recent daily logs worth promoting to real notes.
Offer to act on any item (promote a note, change a status) — with approval.

## Vault Health Audit (monthly-ish; heavier than the weekly review)
Run this on a slower cadence than the weekly review — it looks at vault *structure*, not this
week's activity.
- **PARA balance:** is `40 Resources` and `90 Archives` actually being used, or sitting empty while
  everything lands in Atlas/Efforts? Is `30 Atlas/MOCs` and `Architecture/` still empty — fine
  early on, worth naming once volume builds and it hasn't changed.
- **Doctrine drift:** scan frontmatter for invalid `type` / `status` / `priority` values against
  `Conventions.md` (e.g. a project `status` outside `active/on-hold/done`, a `type` not in the
  enum). Flag notes sitting in the wrong folder for their `type`.
- **Dead / orphan links:** find `[[links]]` that don't resolve to a note, and notes with zero
  inbound links. Recommend a stub, a real note, or removal per the Filing Rules tie-breakers.
- **Entity-stub sprawl:** count lightweight `type: atlas` stubs standing in for people/orgs (the
  doctrine gap where no `person`/`partner` type exists). If it's grown past a handful, flag that
  it may be time to formalize a real type instead of continuing to patch around it.
- **Mutability drift:** spot-check for retro-edited snapshots (a dated block whose content references events later than its own date, with no `[corrected …]` marker) and for living notes whose newest `📝 Notes` bullet is materially newer than their `📌 Current Focus`.
- **Lifecycle hygiene:** projects that are done/dormant but still sitting in `10 Efforts` instead
  of `90 Archives`.
- **Template sync:** per Conventions' "Template sync" rule, check whether structural changes made
  here (new frontmatter fields, folders, doctrine edits) have been mirrored to
  `~/REPOS/AIOS Template`; flag drift.
- **Capture trend:** a rough read on whether daily-log habits (Top 3, Evening Review, Fleeting
  Notes) are being used consistently or trailing off.
Report as a prioritized punch list, same format as the weekly review; offer to act on any item
with approval.

## Query the vault (read-only)
Answer questions by searching the vault and synthesizing, citing the notes used as `[[links]]`.
Never fabricate — if the vault doesn't contain it, say so plainly. Do not modify anything in this mode.
**Personal boundary (Conventions § 🔒 Personal stays personal):** a work question gets a work
answer. Leave out blank-`entity` notes, rows inside a `🏠 Personal` fold, and personal calendar or
inbox content unless the operator explicitly asks to include them. When unsure, leave it out.

## Safety
- Show proposed edits, moves, and deletes; get approval first.
- **Explain your reasoning** for each change (why this note/section, why this status/move/link). Intentional while the workflow is being tuned; can be dialed down later by editing this line.
- Preserve Dataview blocks and untouched frontmatter.
- Never read or write `Private/` unless explicitly asked.

## References
- The vault's live `30 Atlas/Conventions.md` + `Filing Rules.md` are authoritative.
- `references/day-wrap.md` — end-of-day reconstruction procedure. Load only when wrapping a day.
- Fallback copies are bundled with the `capture-note` skill (`../capture-note/references/`).
