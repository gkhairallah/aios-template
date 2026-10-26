# AIOS — a Knowledge Operating System (Obsidian template)

A hybrid **ACE + PARA** Obsidian vault template. Clone it, connect an LLM (Claude Cowork works
well), and capture knowledge with almost no manual filing — the structure and rules do the work.

This repo is the **generic template.** A personal instance is a copy of this with your own data
filled in.

> ### 👉 New here? Start with **[docs/AIOS_GETTING_STARTED.md](docs/AIOS_GETTING_STARTED.md)**
>
> The complete guide, written for someone who has never used Obsidian, git, or an AI assistant: the concepts behind the design, step-by-step setup on **Mac and Windows**, dependencies and keys, connecting an AI layer (Claude *or* Codex/ChatGPT — this template is model-agnostic), connecting external services, syncing across computers, attachments and whether you need the secured tier at all, an always-on setup, voice access, and the security decisions worth understanding before you make them.

## Quick start
The abbreviated version. Full detail and the Windows path are in the
[Getting Started guide](docs/AIOS_GETTING_STARTED.md).

1. Open this folder as an Obsidian vault → **Trust author and enable plugins**. `.obsidian/` is tracked, so **the settings arrive with the clone** — daily notes (`00 Calendar`, format `YYYY/MM/YYYY-MM-DD`, template `Templates/Daily Note.md`) and the `attachments` folder default. Plugin *code* isn't bundled: install the six once (Dataview, Templater, Obsidian Git, Calendar, BRAT, external-pdf), then set Templater → Template folder = `Templates`, "Trigger on new file creation" ON, and Folder Templates `10 Efforts`→`Project`, `30 Atlas`→`Atlas Note`, `30 Atlas/Decisions`→`Decision`, `40 Resources`→`Resource`. Commit `.obsidian/plugins/` afterwards and every later machine needs none of this.
2. **Per machine, once:** `cp .obsidian/graph.json.example .obsidian/graph.json` (graph state is gitignored — it churns), then restart Obsidian. This carries the `-Path: Templates` filter so the templates' Templater placeholders don't appear as unresolved nodes.
3. **Connect an AI layer** — see [Part 3](docs/AIOS_GETTING_STARTED.md#part-3--connect-the-ai-layer). Claude reads `CLAUDE.md`; Codex/ChatGPT reads `AGENTS.md` and `.codex/`. Both route to the same plain-Markdown skills in `.aios/Skills/aios-notes/`. Run the one-time init so it remembers the vault path.
4. Delete the 🧪 EXAMPLE notes; create a hub per business in `10 Efforts/Companies/`.
5. Read [[Filing Rules]] and [[Conventions]] — that's the whole system.

Native drag = local attachment; use the attach skill for the secured tier
([Part 6](docs/AIOS_GETTING_STARTED.md#part-6--attachments-and-whether-you-need-r2-at-all) — it is
optional, and starts out off).

## Folder map
| Folder | Purpose |
|--------|---------|
| `00 Calendar` | Daily/weekly/hourly logs + capture inbox |
| `10 Efforts` | Projects (`type: project`) + Areas (`type: area`); business hubs in `Companies/` |
| `30 Atlas` | Knowledge: `Dashboards/`, `Decisions/`, `MOCs/`, `Architecture/` |
| `40 Resources` | Collected reference material |
| `90 Archives` | Completed / inactive |
| `Templates` | Note templates |
| `attachments` | Binaries (offload to object storage; keep the repo text-only) |
| `Private` | Local-only, gitignored, excluded from AI retrieval |

## Model-agnostic by design

The instructions that make this work are plain Markdown in `.aios/Skills/aios-notes/` — not code.
Two thin routers point at them, so you can switch assistants without changing the system:

| Assistant | Router | Invocation |
|---|---|---|
| Claude (desktop / Cowork / Code) | `CLAUDE.md` + the `aios-notes` plugin | `/note`, `/log`, `/find`… or plain English |
| Codex / ChatGPT | `AGENTS.md` → `.codex/workflows/`, `.codex/commands/` | Plain English |
| Anything else that reads files | Point it at `AGENTS.md` | Plain English |

## Doctrine
- Filing is deterministic — see [[Filing Rules]].
- Structure & nomenclature — see [[Conventions]].
- **Obsidian holds your *thinking*, not your *documents*:** original knowledge lives here; source documents stay in their system of record (Git, SharePoint, etc.) and are linked, not copied.
