# AIOS — Product Requirements Document

**AIOS** = the generic template. A personal instance is a clone of it filled in with real data —
this document was built and validated against a working instance, but every requirement below is
written for anyone cloning the template.

Status: living document. Last updated: 2026-07-17.
Related: `AIOS_HLD.md` (architecture), `AIOS_LLD.md` (implementation detail) — both in this repo.
Keep your instance's own decision log and filled-in operational runbook (real values) outside
this repo, alongside your planning docs.

---

## 1. Problem statement

Personal knowledge-management systems (Obsidian, Notion, etc.) fail in two predictable ways over
time:

1. **Filing decision fatigue.** Every new note forces a "where does this go?" decision. Left ambiguous, this either stalls capture entirely or produces inconsistent structure that erodes the system's usefulness within months.
2. **No safe way to attach real files.** Personal vaults either stay text-only (losing the ability to reference contracts, screenshots, reports) or attach files locally in a way that doesn't survive across machines, doesn't work well with an AI agent, or risks making sensitive material public the moment it's shared anywhere.

Separately, once an LLM agent (Claude, or similar) is added as a collaborator on the vault, most
existing PKM systems have no deterministic contract for *how* the agent should file, edit, or
attach things — every action becomes a fresh judgment call, which is slow, inconsistent, and
error-prone at scale.

**AIOS solves both**, with a **third goal layered on top**: be genuinely usable by an LLM agent as
a first-class collaborator, not just a human-only note app that an agent occasionally pokes at.

## 2. Goals

| # | Goal | Why it matters |
|---|---|---|
| G1 | **Deterministic filing** — any note or thought has exactly one correct destination, decidable by a short cascade of objective yes/no questions | Eliminates decision fatigue; makes an LLM agent's filing decisions reproducible and auditable |
| G2 | **LLM-native operation** — an agent can capture, maintain, query, and attach without re-deriving conventions each time | The vault is designed to be operated *by* an agent day-to-day, not just read by one occasionally |
| G3 | **Safe attachments, no public tier** — every attached file is either fully local/private or unguessable-but-shareable; nothing is ever publicly discoverable | Personal vaults routinely contain sensitive material (contracts, reviews, financials) |
| G4 | **Low overhead for trivial actions** — a status flip or a to-do add should cost near-zero tokens/latency and never require reloading doctrine | Most day-to-day interactions are small; treating every edit as a full "understand the whole system" operation doesn't scale |
| G5 | **Template portability** — the system should be cloneable by a colleague with zero of the original owner's data, secrets, or business context baked in | The whole point of a template is that it isn't bespoke to one person |
| G6 | **Vault stays text-only** — the versioned repo never grows unboundedly from binary attachments | Keeps git history light, keeps the vault fast to clone/sync |

## 3. Non-goals

- **Not a document management system.** Source-of-truth documents (contracts, SharePoint files, code) stay in their system of record and are *linked*, never duplicated into the vault.
- **Not a public-sharing platform.** There is deliberately no "public" attachment tier — see G3. Anyone wanting to publish something does so through a separate, explicit tool.
- **Not a training-data or vector-ingestion target.** Nothing in AIOS assumes or requires the vault's contents being fed into any third-party model's training set or a persistent vector store. (A separate, optional "Gateway" pattern for query-time-only retrieval by a private AI backend is a valid extension — but it is out of scope for the AIOS template itself and is not required to use AIOS.)
- **Not multi-user / real-time-collaborative.** AIOS is a personal vault pattern. Multiple people can each run their own instance; there's no shared-editing or permissions model.

## 4. Users / personas

| Persona | Description | Needs |
|---|---|---|
| **Template owner** | Power user running the full stack, may layer additional private infrastructure (a query-time AI gateway, business integrations) on top of the vault | Everything below, plus the ability to extend without forking the template's core doctrine |
| **Colleague adopter** | Clones the template fresh, uses an LLM agent (e.g. Claude Cowork or Codex) + the vault + the `aios-notes` skills, no additional private infrastructure | A working system out of the box with zero of the owner's data, a clear one-time setup path, and doctrine that's self-explanatory from the template alone |

## 5. Functional requirements

| # | Requirement | Covered by |
|---|---|---|
| F1 | Capture a plain-language instruction into a correctly-typed, correctly-filed note, asking the user only about genuine gaps | `capture-note` skill |
| F2 | Maintain existing notes — status changes, to-dos, refiling, linking, MOC-building — via a **fast path** that skips doctrine loading entirely for trivial edits | `vault-ops` skill, its Fast Path |
| F3 | Log a daily stream (Top 3, hourly log, worked-on, evening review) as the default capture inbox | `vault-ops` (daily log ops), `Templates/Daily Note.md` |
| F4 | Produce a weekly review (stalled work, overdue items, recent decisions, promotable fleeting notes) | `vault-ops` (weekly review) |
| F5 | Produce a monthly structural health audit (doctrine drift, dead links, PARA balance, template-sync drift) | `vault-ops` (Vault Health Audit) |
| F6 | Answer questions from the vault's own content, read-only, with citations, never fabricating | `vault-ops` (query mode) / `find` command |
| F7 | Attach a file to a note, routed to exactly one of two tiers (private-local or secured-remote), never public | `attach` skill — see §6 below and `AIOS_HLD.md` |
| F8 | Pull supporting context from connected company knowledge sources (SharePoint, email, calendar, chat) into a note, opt-in and cited, never blanket-searched | `gather` skill |
| F9 | One-time setup that lets every subsequent action resolve the vault instantly, without a filesystem search | `aios-init` / `~/.aios/config.json` |

## 6. The attachments requirement, in detail (F7)

This is the most-implemented, most-tested part of the system as of this document's last update,
so its requirements are stated explicitly:

- **Exactly two tiers, no third.** Private (local-only, never leaves the machine/repo) or Secured (uploaded to private object storage, reachable only via a non-expiring, revocable signed URL). There is no public tier by design — see G3.
- **Renders inline in the vault app**, not just as a link, for every common file type a user is likely to attach (images, PDF, plain text, Office documents) — a link-only fallback is acceptable only for formats that cannot reliably preview in-app for reasons outside the system's control (see `AIOS_LLD.md` for the one documented exception: PDF, and why).
- **Explicit, reliable download**, independent of whatever the inline viewer's own UI offers (third-party viewer UIs have proven unreliable with signed/query-string URLs).
- **Revocable**: rotating one secret invalidates every previously-issued signed URL at once.
- **Portable**: switching storage providers or hosts should never require touching vault content — the indirection point (a stable domain in front of the storage) absorbs that change.
- **Must work from an agent session with no local shell/secret access** (e.g. a cloud sandbox), not just from the owner's own machine — the agent stages the request, and a machine that *does* have the credentials finishes the job asynchronously, with no manual "please run this script" step required of the human in the common case.

## 7. Non-functional requirements

| # | Requirement |
|---|---|
| N1 | A trivial edit (status flip, to-do add, one-line log entry) must not load `Filing Rules.md` or `Conventions.md`, must not do a full-vault search, and must confirm in one line. |
| N2 | Any change to an existing note must be shown (what / where / why) before writing — no silent overwrites. |
| N3 | `Private/` is never read or written unless the user explicitly asks. |
| N4 | Dataview blocks and untouched frontmatter are preserved exactly across any automated edit. |
| N5 | The template repo contains zero real personal data, secrets, or business-specific values — every business-specific slot is a clearly-marked placeholder. |
| N6 | Structural or doctrine changes made in a personal instance are mirrored back to the generic template in the same pass, genericized (strip real data, keep the shape) — not deferred indefinitely. |

## 8. Success criteria

- A new note, of any recognized type, can be filed correctly by an agent without the human ever being asked "where should this go?" in the common case.
- A colleague can clone the template, run one setup command, and have working capture/maintain/ attach/query behavior with no code changes.
- A file of any of the five common types (image, pdf, txt, Office doc, csv) attached to a note renders as designed (inline preview or, for the one documented exception, a working download) without the human needing to know which storage tier or embed mechanism was used.
- Rotating the attachment signing secret and re-running the resign pass leaves zero broken links in the vault.

## 9. Out of scope for this document

- The specific query-time AI gateway pattern an instance may layer on top (privacy-preserving retrieval by a separate AI backend) — that is an instance-specific extension project with its own design docs and decision log, not a requirement of the AIOS template itself.
- Business-integration connectors (Zoho, Quickbase, M365, etc.) — those belong to whatever agent platform sits on top of the vault, not to the vault/template itself.
