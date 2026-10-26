# AIOS — High-Level Design

Architecture and key decisions for the AIOS template. **AIOS** = the generic system; a personal
instance is a clone of it filled in with real data. Companion docs: `AIOS_PRD.md`
(requirements), `AIOS_LLD.md` (implementation detail).

Status: living document. Last updated: 2026-07-17.

---

## 1. System architecture at a glance

```
┌─────────────────────────────────────────────────────────────────────┐
│  Obsidian Vault (content — the only thing that's "AIOS" itself)     │
│                                                                       │
│   00 Calendar    10 Efforts    30 Atlas    40 Resources   90 Archives│
│   (time stream)  (project/     (authored   (collected     (lifecycle│
│                   area, split   knowledge,  reference)     end-state)│
│                   by `type`)    doctrine)                            │
│                                                                       │
│   .aios/  — local config + attachment scripts (gitignored secrets)  │
│   Private/ — local-only, gitignored, never synced or read by AI      │
└───────────────────────────┬───────────────────────────────────────────┘
                            │ read/write (Read/Edit/Write tools; native
                            │ file access, never an external file MCP)
┌───────────────────────────▼───────────────────────────────────────────┐
│  Automation layer — `aios-notes` plugin (skills + fast-path commands)│
│                                                                       │
│   capture-note   vault-ops   attach   gather                        │
│   (new notes)    (maintain,  (files,  (pull company                 │
│                   fast path) 2 tiers) context, opt-in)               │
└───────────────────────────┬───────────────────────────────────────────┘
                            │ (attach skill only, secured tier)
┌───────────────────────────▼───────────────────────────────────────────┐
│  Secured attachment subsystem (Cloudflare)                          │
│                                                                       │
│   Private R2 bucket ◄──rclone──  upload path (direct or staged)     │
│          │                                                            │
│          ▼                                                            │
│   Worker (signature-gated proxy) ── custom domain ── signed URL      │
└─────────────────────────────────────────────────────────────────────┘

Template relationship:  AIOS Template (generic, sanitized)  ──clone──▶  your instance (real data)
                         Structural changes flow back, genericized (never the reverse — no real
                         data ever flows from an instance into the template).
```

## 2. Components

### 2.1 The vault (content)

A folder of markdown + a small number of binary attachments, structured as **hybrid ACE + PARA**:
ACE's time-stream (`00 Calendar`) and knowledge-hub (`30 Atlas`) concepts, merged with PARA's
Projects/Areas/Resources/Archives. The one structural deviation from textbook PARA: **Projects and
Areas share one folder** (`10 Efforts`), distinguished only by a `type` frontmatter field — see
§3, Decision D-Efforts.

This is the only component that is version-controlled and the only one a colleague strictly needs
to clone the template. Everything else (skills, attachment infra) is optional tooling layered on
top.

### 2.2 The automation layer (`aios-notes` skills)

A set of Claude/agent skills, installed as a plugin, that encode the vault's doctrine as
executable behavior rather than leaving an agent to re-derive it every session:

| Skill | Role | Loads doctrine? |
|---|---|---|
| `capture-note` | New notes: classify → draft → interview gaps → write on approval | Yes, always (classification requires it) |
| `vault-ops` | Maintain existing notes: daily log, status, refile, link, review, audit, query | **Only for classification/refile/new-structure work.** A dedicated Fast Path skips doctrine entirely for trivial edits (status flip, to-do, one line) |
| `attach` | Route a file to the correct tier and reference it in a note | Reads `attachments.json` config; doesn't need Filing Rules/Conventions beyond the embed-pattern doctrine |
| `gather` | Pull context from connected company sources into a note | No vault doctrine; reads connector results |

**Design principle (G4 in the PRD): match the tool to the task.** Fast, mechanical commands
(`/status`, `/todo`, `/log`) exist specifically so common actions don't pay the cost of loading
and reasoning over the full doctrine every time. This is the single biggest lever for keeping the
system cheap enough to use constantly rather than occasionally.

### 2.3 The secured attachment subsystem

The component with the most implementation detail (see `AIOS_LLD.md` for the full breakdown). At
the HLD level, three pieces:

1. **Private R2 bucket** — object storage, no public access, no `r2.dev` link, no open custom domain pointed directly at it.
2. **Cloudflare Worker** — the *only* thing allowed to read the bucket from the outside. Validates an HMAC signature on every request; on a valid signature, streams the object back with its stored metadata (and can override that metadata for an explicit-download request — see §3).
3. **Upload path** — either direct (`rclone` + local signing, when the acting session has both) or staged (a sandboxed agent session writes a placeholder into the note and stages the file in a pending folder; a machine that *does* have `rclone`/the secret finishes the job asynchronously and rewrites the placeholder in place).

### 2.4 The template relationship

`AIOS Template` is a sanitized, generic copy of the vault shape (folders, doctrine, templates,
example notes) with zero real data. A personal instance is a clone with real content
filled in. The relationship is **one-directional in practice but bidirectional in intent**:
structural/nomenclature changes discovered while living in an instance are meant to flow back to
the template (genericized), so the template never drifts stale relative to what's actually
working. This is process discipline, not automation — there is no sync tool; it's a standing rule
checked during the monthly Vault Health Audit.

## 3. Key design decisions (the "why")

| Decision | Rationale |
|---|---|
| **Projects + Areas share one folder, split by `type`** | The textbook PARA gray zone ("is this a project or an area?") becomes a one-field edit instead of a file move the moment the answer changes — removes an entire category of filing indecision. |
| **Filing is a deterministic cascade (first-YES-wins), not a rubric to weigh** | A rubric invites debate; a cascade of objective yes/no questions doesn't. This is what makes filing decisions safe to delegate to an agent — the answer is reproducible, not a judgment call. |
| **Folders are weak, `type` + `[[links]]` are strong** | Retrieval happens by search/links/Dataview, not by browsing folders — so a misfile costs nothing and doesn't need to be agonized over. This is what makes G1 (deterministic filing) actually low-stakes in practice, not just low-effort. |
| **`entity` is a list-valued frontmatter property, not folders-per-business** | One property slices every note by business (or `shared`, or blank for personal) without ever forcing a company-specific folder structure into the template. Business hubs are Areas with that `entity` set, not a parallel structure. |
| **Two attachment tiers, no public tier** | Personal vaults hold sensitive material by default. A "public" tier is an easy footgun (a signed URL that quietly outlives its usefulness, or a plugin default that uploads somewhere world-readable) — removing the option removes the failure mode entirely. |
| **Secured tier = signed URL behind a Worker, not a public bucket link** | Makes the object unguessable and revocable (rotate one secret) without needing per-user auth — the right tradeoff for a single-owner personal vault shared occasionally by link, not a multi-tenant access-control problem. |
| **A stable custom domain sits in front of R2, never a raw provider URL in markdown** | Decouples the vault's content from the storage provider — switching providers or hosts later is a DNS/Worker change, never a find-and-replace across every note that ever referenced a file. |
| **The vault repo stays text-only; binaries live in R2, not Git LFS** | R2's free tier (10 GB, zero egress) beats LFS's metered bandwidth model for this use case, and keeps clone/sync fast regardless of how many attachments accumulate. |
| **Fast Path exists as a first-class concept, not an optimization detail** | Explicitly designed in from the start (not bolted on later) because most real usage is small, frequent edits — optimizing only the "interesting" flows (capture, refile) while leaving every trivial edit expensive would have made the system slower in practice than it looks on paper. |
| **The upload pipeline must work with zero local shell access** | An agent session (e.g. a cloud sandbox) is a first-class caller of the attach flow, not an edge case — so the design had to support "stage the request now, finish it asynchronously on a machine that has the credentials" from day one, rather than treating sandboxed sessions as unsupported. |

## 4. Data flows

### 4.1 Capture flow (new note)

```
Plain-language instruction
        │
        ▼
Resolve vault (~/.aios/config.json — no filesystem search)
        │
        ▼
Load Filing Rules + Conventions (authoritative; template-bundled fallback if missing)
        │
        ▼
Classify (first-YES cascade) ──▶ check for an existing home (append vs. new note)
        │
        ▼
Draft from the matching template + Conventions (frontmatter, section headers, suggested links)
        │
        ▼
Interview ONLY genuine gaps (entity? deadline? substance vs. link-out?)
        │
        ▼
Show full draft + destination + reasoning ──▶ approval ──▶ write
```

### 4.2 Attach flow (secured tier)

Two paths, chosen by whether the acting session can reach `rclone` and the signing secret
directly:

```
                    Identify file + target note + tier (private vs secured)
                                        │
                          ┌─────────────┴─────────────┐
                          ▼                             ▼
              rclone/secret available here    rclone/secret NOT available
                          │                             │
                          ▼                             ▼
        Upload directly, sign locally,        Write the note's placeholder
        write the resolved embed pattern       FIRST, then stage the file in
        into the note                          a pending folder (order matters —
                                                avoids a race with the watcher)
                          │                             │
                          │                             ▼
                          │                   A machine with rclone/the secret
                          │                   (watching the pending folder)
                          │                   uploads, signs, and rewrites the
                          │                   placeholder in place, automatically
                          │                             │
                          └─────────────┬───────────────┘
                                        ▼
                    Note now contains the correct per-format embed
                    (see AIOS_LLD.md for the exact pattern per file type)
```

### 4.3 Query / gather flow (read-only)

```
Question about the vault  ──▶  search + synthesize from vault content  ──▶  cited answer
                                (never fabricate; say so if the vault doesn't contain it)

Question needing company context  ──▶  confirm which connected source(s) to check
                                    ──▶  narrow, targeted search (never blanket)
                                    ──▶  summarize + cite  ──▶  fold into a note on approval
```

## 5. Cross-cutting concerns

- **Privacy by default.** `Private/` is excluded from sync/AI retrieval categorically. The secured tier is "unguessable + revocable," explicitly **not** "access-controlled" — that distinction is load-bearing and must stay visible to whoever attaches a file (see PRD §6).
- **Approval before write, always**, for anything touching an existing note — no silent overwrites, ever. The Fast Path shortens *doctrine loading*, never the approval step for actual content changes beyond the specific mechanical field being changed.
- **Explain-why is currently on, deliberately.** Every automated write currently states its reasoning (why this type, why this folder, why this tier). This is intentional overhead while the system is being tuned and is expected to be dialed back once the doctrine has proven itself in practice — it is a temporary transparency measure, not a permanent requirement.
- **Portability over convenience** in the attachment layer: every choice (custom domain fronting, no LFS, revocable signing) optimizes for "this still works if the storage provider or the human's machine changes," not for the shortest implementation path.

## 6. Known limitations (system-level, not implementation bugs)

- **PDF cannot render inside a plain `<iframe>` in Obsidian**, because Obsidian runs on Electron and Electron has a confirmed, long-standing bug where iframes can't render PDFs at all (blank frame, every time). This isn't a defect in AIOS's design — it's a platform limitation the design works around (a community plugin renders through Obsidian's own bundled PDF viewer instead of an iframe). Every other common format was unaffected. Full detail in `AIOS_LLD.md`.
- **CSV cannot be reliably previewed inline in a browser context at all** — Chrome and Firefox force-download CSVs even when the server sends correct "render inline" headers. AIOS treats this as a platform fact to design around (plain download link, no embed attempt) rather than a bug to chase.
- **Third-party viewer UIs' own "download" affordances are unreliable with signed/query-string URLs** (observed with Office Online's viewer). AIOS never depends on those — every embed pattern ships its own explicit download link pointed at the same signed URL with a decoration that tells the origin server to force a download.
