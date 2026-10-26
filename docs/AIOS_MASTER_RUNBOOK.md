# AIOS — Master Operations Runbook (template edition)

The single entry point for setting up and running an AIOS instance from a fresh clone of the
template. This is the **generic, shippable** version — every instance-specific value has been
replaced with a placeholder. Step-by-step detail for each piece lives in its own runbook (linked
below); this doc is the map and the rationale.

Companion docs: `AIOS_PRD.md` (requirements), `AIOS_HLD.md` (architecture), `AIOS_LLD.md`
(implementation detail), `AIOS_SECURED_ATTACHMENTS_RUNBOOK.md`, `AIOS_GIT_AND_SYNC_RUNBOOK.md`.
If you keep a filled-in copy of these runbooks for your own instance (real domain, bucket, and
paths), treat the two sets as a pair — when either changes, mirror the change to the other,
stripped or filled in as appropriate.

Status: living document. Last updated: 2026-07-17.

---

## 1. What it is (architecture at a glance)

| Layer | What | Where |
|---|---|---|
| **Knowledge** | Obsidian vault — hybrid ACE+PARA, your authored knowledge | `<vault path>` → your own private git host |
| **Automation** | `aios-notes` plugin — capture / operate / attach via an LLM agent | Installed in your agent tool (Claude Cowork or equivalent) |
| **Attachments** | Two tiers: private (local) + secured (private object storage via a signed Worker URL) | `<your-bucket>` + Worker at `<cdn.yourdomain.com>` |
| **AI layer** | Your agent tool, with direct file access to the vault | — |
| **Template** | This repo — the generic, sanitized starting point | `AIOS Template` |

**This runbook assumes the baseline setup only** — vault + agent + skills + attachments. Anything
beyond that (a private query-time retrieval gateway, business-system integrations, multi-tenant
routing) is an optional extension layered on top by whoever adopts the template, not part of the
template's own scope.

## 2. Operational decisions baked into the template (the "why")

| Decision | Rationale |
|---|---|
| Vault lives in its own private git repo, separate from any code repos | Personal knowledge stays out of engineering/work version control; noisy auto-commits from a sync plugin don't pollute code history |
| **Hybrid ACE + PARA** folder model | Time stream (Calendar) + action (Efforts) + knowledge (Atlas) covers capture, doing, and knowing without three incompatible systems |
| **Projects + Areas merged into `10 Efforts`**, split by `type` | Kills the project↔area filing gray zone — a property change, never a folder move |
| Filing is **deterministic** (first-YES cascade); folders weak, `type` + links strong | No decision fatigue; a misfile costs nothing |
| Business axis = the `entity` frontmatter property (list; `shared` value), company hubs as Areas in `10 Efforts/Companies/` | One property slices everything by business; no company folders baked into the template |
| Attachments **2-tier**: private (local) or secured (private object storage + signed Worker URL). **No public tier.** | Nothing publicly guessable; signed URLs = unguessable + revocable + shareable-by-link; object storage beats Git LFS on cost (free tier + zero egress vs. metered bandwidth) |
| Vault and any supporting code/tooling are **separate repos** | Vault = content only; automation/skills live in the agent platform, not the vault repo |
| Any structural/nomenclature change discovered while running an instance is meant to flow back to this template, genericized | Keeps the template from drifting stale relative to what's actually working in practice |

Keep your own decision log alongside these runbooks. Doctrine (inside the vault
itself, not this planning folder): `30 Atlas/Filing Rules.md`, `30 Atlas/Conventions.md`.

## 3. One-time setup (with detailed runbooks)

| Setup | Detailed runbook | Key result |
|---|---|---|
| **Git + sync** | `AIOS_GIT_AND_SYNC_RUNBOOK.md` | Token auth, Obsidian Git auto-sync, clone on a second machine |
| **Obsidian plugins/config** | (in the git runbook) | Dataview, Templater (+ Folder Templates), Daily Notes, Calendar. **Daily notes date format `YYYY/MM/YYYY-MM-DD`** (year + month subfolders). **Files & links → new-attachment folder = `attachments`** (else drops land in the vault root). **Graph View filter `-path:Templates`** (hides template placeholder links). |
| **Bind the vault folder to your agent tool** | If using Claude Cowork (desktop app): Projects → + → "Use an existing folder" → pick the vault's parent folder. Every session then auto-mounts it — native file access, no external file MCP, the biggest latency/cost win. Equivalent step exists for other agent tools. | |
| **`aios-notes` plugin** (or equivalent skill pack) | install it; run its one-time init command | Skills become available; a local config file points at the vault so every future action resolves it instantly instead of searching the filesystem |
| **Secured attachments** | `AIOS_SECURED_ATTACHMENTS_RUNBOOK.md` | Private object-storage bucket + Worker + signed URLs; upload tool configured; vault's attachment config in "secured" mode |

**Gotchas learned (baked into the runbooks so you don't rediscover them):**
- Object-storage scoped API tokens often can't run bucket-level ops — the upload tool needs a "don't check the bucket exists" flag or it 403s on every upload.
- The custom domain must attach to the **Worker**, not directly to the bucket, or it serves the bucket publicly.
- Quote URLs containing `?` in zsh, or the shell mangles them.
- Pipe secrets into whatever "set secret" command your platform provides rather than pasting interactively — avoids transcription mismatches.
- Uploads need an explicit "render inline" disposition header — without it, objects default to force-downloading in the browser regardless of file type.
- Forcing an actual download (as opposed to another inline-render attempt) needs the Worker to support an explicit override parameter on the URL — see the attachments runbook §11 for exactly how and why.
- **The vault app's rendering engine may not support `<iframe>`-embedded PDFs at all** if it's Electron-based (a confirmed, long-standing Electron bug — blank frame, every time, not fixable via headers). Every other common format renders fine in an iframe; plan for a PDF-specific fallback (a dedicated viewer plugin) rather than assuming iframes work universally.
- Multiple attachments in one note need a genuinely blank line between each attachment's embed block, or consecutive blockquote-prefixed lines merge into a single callout and everything after the first one breaks.

## 4. Daily operations (how you use it)

| Want to… | Do this |
|---|---|
| Capture a note | "make a note about…" — classifies, drafts, interviews for gaps, writes on approval |
| Log your day | Daily-log commands: hourly + worked-on links; Top 3 / evening review |
| Maintain notes | Plain language: change status, archive, refile, link, build a MOC — routed through the fast path for trivial edits |
| Weekly review | Stalled work, overdue items, decisions logged, fleeting notes to promote |
| Ask your vault | Read-only, cited answers from vault content only |
| Attach a file | Drop it + "attach to [note]" — private → local; else secured → signed URL, embedded per the format-specific pattern |

Every write is shown for **approval** first; the skill explains its reasoning (tunable once the
doctrine has proven itself — see `AIOS_HLD.md` §5).

## 5. Maintenance

### 5a. Run the attachment reconciler (remove orphaned objects)
The reconciler finds objects in storage no longer referenced by any note and (optionally) deletes
them. Dry-run by default:
```bash
<vault>/.aios/reconcile-attachments.sh              # preview — lists orphans, deletes nothing
<vault>/.aios/reconcile-attachments.sh --delete     # act — deletes the orphans it listed
```
Run dry-run for a couple of weeks before trusting `--delete`.

### 5b. Schedule it (cron, or your platform's scheduler)
```bash
crontab -e
```
```
0 9 * * 1 <vault>/.aios/reconcile-attachments.sh --delete >> /tmp/aios-reconcile.log 2>&1
```
On macOS: cron may not have the upload tool on `PATH` — hardcode its path or add it to the
crontab's `PATH` line. Grant cron/Terminal Full Disk Access so it can read the vault.

**Where to run it:** interim = your laptop's cron (fine — a missed weekly run only defers
cleanup). Better = an always-on machine, if you have one. Best (optional, more code) = a
serverless scheduled function that lists the bucket and diffs against referenced keys directly,
no machine dependency at all.

### 5c. Rotate the signing secret
Rotating invalidates **every** existing signed URL, so re-sign the vault in the same pass:
```bash
# 1) New secret
NEW=$(openssl rand -hex 32); echo "$NEW"

# 2) Update the Worker's secret (from the worker's own directory)
printf %s "$NEW" | npx wrangler secret put SIGN_SECRET

# 3) Update your local env var, then:
source ~/.zshrc   # or your shell's equivalent

# 4) Re-sign every attachment URL in the vault with the new secret:
<vault>/.aios/resign-attachments.sh

# 5) Commit so every clone gets the new URLs:
cd <vault> && git add -A && git commit -m "Re-sign attachment URLs" && git push
```
Verify: one attachment loads with its new signature; any old copy of the URL now returns 403
immediately (the check isn't cached).

### 5d. Other
- **Template sync** — any structural/nomenclature change made while running a real instance should be mirrored back into this template, genericized, in the same pass — not deferred.
- **Backups** — your git host is your history; a sync plugin auto-commits; consider a periodic snapshot regardless.
- **Second machine** — clone the vault, run the init command, install the same plugins; set the signing secret + upload-tool remote there too if it will attach files.

## 6. Component & config map

| Thing | Location |
|---|---|
| Vault (content) | `<vault path>` → your private git host |
| Generic template | `AIOS Template` (this repo) |
| Skill pack (installed) | `aios-notes` or equivalent |
| Planning / design / runbooks | wherever you keep pre-vault planning docs |
| Vault pointer (per machine) | a local config file outside the vault, e.g. `~/.aios/config.json` |
| Attachment config (gitignored — never commit this) | `<vault>/.aios/attachments.json` |
| Upload-tool credentials | a named remote in the upload tool's own config, outside the vault |
| Signing secret | a local env var + the Worker's own secret store — never in vault-committed config |
| Attachment Worker | your own deployment, behind your own custom domain |
| PDF preview plugin | Obsidian community plugin `external-pdf`, installed via BRAT — the one plugin dependency in the whole attachment pipeline, needed only because Obsidian's Electron shell can't render PDFs in an iframe |

## 7. Open / next (template-level, not instance-specific)

- **Multi-instance rollout patterns** — how a team standardizes on this template while each person keeps their own private vault and their own attachment infrastructure (nothing shared).
- **Optional extensions** (query-time retrieval gateway, business-system connectors) are explicitly out of the template's own scope — see `AIOS_PRD.md` §9 — but worth documenting as a recognized extension pattern once a reference implementation exists.
