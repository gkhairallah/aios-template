# aios-notes

Run your **AIOS / Obsidian vault** through an LLM — capture, maintain, and query it in plain
language, with the structure and rules doing the work. Everything follows your vault's Filing
Rules and Conventions, and every change to an existing note is shown to you before it's written.

## What it can do

**Capture (create new notes)** — the `capture-note` skill / `/note`
- Classifies a note (project / area / atlas / resource / decision / moc / daily log), drafts it
  per your Conventions, links to sources instead of duplicating them, suggests `[[links]]`,
  interviews you for the genuine gaps, and writes on approval.

**Operate & maintain** — the `vault-ops` skill + commands
- **`/log`** — log an entry into today's hourly log with a `[[link]]` + a Worked-On bullet.
- **`/today`** — set your 🎯 Top 3, or run the 🌙 Evening Review.
- **`/review`** — weekly rollup: active/stalled projects, overdue/due-soon, decisions this week, fleeting notes to promote.
- **`/audit`** — monthly structural health check: PARA-quadrant balance, doctrine drift, dead/orphan links, entity-stub sprawl, lifecycle hygiene, AIOS Template sync.
- **`/find`** — ask a question answered from your vault (read-only, cited).
- Plus, by natural language: change a project's status, archive it, refile a misfiled note, fix a
  note to match the conventions, stamp `entity`, insert links, and build/extend MOCs.

**Reach outside the vault** — the `gather` and `act` skills
- **`/gather`** *(read-only)* — pull real context into a note from whatever this session can
  actually reach. Sources resolve **capability-first** (DOCS / EMAIL / CALENDAR / CHAT / RECORDS)
  rather than by a fixed tool list, so the same skill works under Claude, Codex/ChatGPT Work, or
  anything else. Where a host exposes a **gateway** — Composio today — the whole authorized roster
  comes with it (Coda / "Superhuman Docs", Zoho Desk, Notion, Linear, Slack, GitHub…), discovered at
  runtime and never hardcoded, so a newly-connected toolkit is reachable the moment it's authorized.
- **`/act`** *(the outward write path)* — the only workflow allowed to change a system outside the
  vault: add a Coda row, update a ticket, file an issue, post a message, draft or send mail. Works
  through either a first-party connector or a gateway. Every write is shown first as a full approval
  card — tool, account alias, target id, the exact JSON payload, what changes, who it reaches,
  whether it's reversible — and runs only after you say yes. Irreversible, customer-facing, or
  financial actions take a second confirmation.
- The split is structural: `gather` can never write outward, so it's always safe to run. Anything
  that would change the world hands off to `act` with a fresh card.

**Live project dashboards** — the `live-dashboard-ops` skill / `/dashboard`
- Stands up an auto-syncing dashboard for a project — a self-contained HTML page mirroring its
  vault note's status/KPIs, timeline and risks, with self-service Export HTML / Export PDF buttons —
  or adds a new data source to a dashboard that already exists. One dashboards folder
  (`registry.json` + one `<id>.html` per project + a rendered `index.html`) plus one shared
  scheduled sync task cover every dashboard in the vault, so adding a project is a two-step edit,
  never new infrastructure. Host-agnostic since v0.15.0: runs under Codex/ChatGPT, Claude or any
  host with file access and a real scheduler.

## How to use
Just talk to it — "make a note about…", "log that I spent the morning on…", "mark the pricing
calc done", "what does my vault say about Azure?", "what does the team wiki say about
licensing?", "add a row to the Projects table", "add a live dashboard for the Acme project" — or use
the `/note`, `/log`, `/today`, `/review`, `/find`, `/gather`, `/act`, `/dashboard` commands. It
shows proposed changes and writes only after you approve.

## Requirements
- **An AIOS vault** (folder with `30 Atlas/`, `10 Efforts/`, `Templates/`, and ideally
  `30 Atlas/Conventions.md` + `Filing Rules.md` — read as the source of truth; bundled fallbacks used if absent).
- **Claude Cowork with access to the vault folder** — reads for links/queries, writes notes directly.
  No gateway or middleware needed; this is the standalone, single-person setup.
- **Optional, for `/gather` and `/act`** — any first-party connectors you want (Microsoft 365,
  Gmail, Calendar) and/or a tool gateway such as Composio, which fronts everything else. Nothing is
  required: both skills resolve capability-first and degrade gracefully to whatever this session
  actually has.
- **For `/dashboard` specifically** — read/write access to the dashboards folder, `python3`, and
  the host's scheduled-task mechanism (Codex scheduled tasks, Claude scheduled tasks, …) for the
  one shared sync task.

## Design notes
- **Tool-agnostic** — references "your vault," nothing company-specific; drops onto any AIOS instance.
- **Host-agnostic** — `gather` and `act` resolve tools by *capability*, not by model or product, so
  the same files work under Claude, Codex/ChatGPT Work, or any host, with or without a gateway.
- **DRY** — behavior is driven by your vault's live Conventions/Filing Rules; update those and the
  plugin follows. Bundled `references/` are fallbacks only.
- **Safe by default** — existing notes are never overwritten silently; Dataview blocks are
  preserved; `Private/` is left alone unless you ask.
