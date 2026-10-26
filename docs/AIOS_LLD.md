# AIOS — Low-Level Design

Implementation-level detail: exact schemas, file formats, script internals, and the attachment
embed pattern. **AIOS** = the generic system; your own vault is the concrete instance every example and file
path below is drawn from. Companion docs: `AIOS_PRD.md` (requirements), `AIOS_HLD.md` (architecture).

Status: living document, kept in sync with the actual scripts/config as they change.
Last updated: 2026-07-17.

---

## 1. Vault folder layout

```
<vault>/
├── 00 Calendar/<YYYY>/<YYYY-MM-DD>.md      # daily logs, dated subfolders
├── 10 Efforts/                              # projects (type: project) + areas (type: area)
│   └── Companies/                           # business hubs — Areas with entity set
├── 30 Atlas/
│   ├── Filing Rules.md                      # doctrine — the classification cascade
│   ├── Conventions.md                       # doctrine — frontmatter/headers/entity/attachments
│   ├── Dashboards/
│   ├── Decisions/                            # type: decision notes
│   ├── MOCs/                                 # type: moc notes (link hubs)
│   └── Architecture/
├── 40 Resources/                             # collected reference material
├── 90 Archives/                              # done/dormant, lifecycle end-state
├── Templates/                                 # one .md per type, Templater placeholders
├── Private/                                   # gitignored, local-only, never read by AI
├── attachments/                               # interim local attachment store (pre-R2, or if R2 unset)
└── .aios/
    ├── config.json                           # NOT vault-committed — lives at ~/.aios/config.json
    ├── attachments.json                      # gitignored — real config (secrets stay in env, not here)
    ├── attachments.example.json              # committed — sanitized template for attachments.json
    ├── upload-pending.sh                     # finishes uploads staged by a sandboxed session
    ├── resign-attachments.sh                 # re-signs every URL in the vault after secret rotation
    ├── reconcile-attachments.sh              # finds/deletes orphaned R2 objects
    └── delete-pending.sh                     # finishes deletions queued by a sandboxed session
```

`~/.aios/config.json` (note: **outside** the vault, one per machine) is what every skill reads
first to resolve the vault path without a filesystem search:
```json
{ "vaultPath": "/absolute/path/to/vault", "vaultName": "YourVault" }
```

## 2. Frontmatter schema

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
| `created` | evergreen notes | `YYYY-MM-DD` |
| `date` | time-anchored notes | `YYYY-MM-DD` |
| `source` | atlas, resource | free text / URL |
| `related` | any (esp. decision) | list of `[[links]]` |
| `tags` | every note | array; first tag = the type; **always the last frontmatter field** |

**Standard section headers by type:**

| Type | Headers |
|---|---|
| Project | 🎯 Outcome · 🔗 Canonical Sources · 📌 Current Focus · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related |
| Area | 🎯 Standard · 🔗 Canonical Sources · 🚀 Active Projects · 🧠 Decisions · 📝 Notes · 🗒️ Log · 🔗 Related |
| Atlas | 📄 Summary · 📝 Notes · 🔗 Related |
| Resource | 🔗 Source · 📝 Key Points · 🔗 Related |
| Decision | ❓ Problem · ⚖️ Options Considered · ✅ Decision · 💭 Reasoning · ⚠️ Tradeoffs · 📌 Follow-up · 🔗 Related |
| MOC | 🗂️ Notes · 🔗 Related |

Rules: every note ends with `## 🔗 Related`; `🧠 Decisions`/`🗒️ Log` are live Dataview blocks,
never hand-filled; `🔗 Canonical Sources` links to the real artifact, never duplicates it.

## 3. Filing cascade (implemented by `capture-note` / `vault-ops`)

First-YES-wins, five questions:

| # | Question | Destination |
|---|---|---|
| 0 | Just happened / just occurred to me? | `00 Calendar` (daily log) |
| 1 | WORK — can I mark it DONE and stop? | `10 Efforts`, `type: project` |
| 2 | WORK — ongoing standard, no end? | `10 Efforts`, `type: area` |
| 3 | KNOWLEDGE — I authored it? | `30 Atlas` |
| 4 | KNOWLEDGE — I collected it? | `40 Resources` |
| 5 | Done/dead/dormant? (lifecycle, not a category) | `90 Archives` |

Tie-breakers: Work-vs-Knowledge torn → Knowledge. Atlas-vs-Resources torn → Atlas if any of your
own words are in it, else Resources. Still torn → leave it in the daily log (this is a valid
permanent state, not a deferred decision).

## 4. Attachment configuration schema

`.aios/attachments.json` (gitignored; `attachments.example.json` is the committed, sanitized
template):

```json
{
  "defaultDestination": "r2",              // "vault" (interim, local) | "r2" (secured)
  "localFolder": "attachments",
  "privateFolder": "Private/attachments",
  "pendingFolder": "Private/attachments/_pending",
  "pendingArchiveFolder": "Private/attachments/_uploaded",
  "pendingNote": "<instructions for a sandboxed session on placeholder syntax>",
  "pendingResolution": "<instructions on polling for the async upload to finish>",
  "deleteQueueFolder": "Private/attachments/_pending_delete",
  "deleteArchiveFolder": "Private/attachments/_deleted",
  "deleteResolution": "<instructions for a sandboxed session on queuing a deletion>",
  "r2": {
    "remote": "r2-vault",                  // rclone remote name
    "bucket": "<bucket-name>",
    "workerBaseUrl": "https://cdn.<domain>",
    "keyTemplate": "attachments/{yyyy}/{mm}/{filename}",
    "signSecretEnv": "AIOS_R2_SIGN_SECRET"  // env var name, never the secret itself
  }
}
```

`pendingNote`/`pendingResolution`/`deleteResolution` are the mechanism that keeps a sandboxed agent
session (no `rclone`, no secret) correctly behaved: they encode, in the config itself, exactly how
to stage a request and how to poll for it resolving, so the behavior is discoverable from the
vault rather than hardcoded into any one skill's prompt.

## 5. Two-tier attachment routing (`attach` skill)

| Tier | Where it goes | Reference syntax | Uploaded? |
|---|---|---|---|
| **Private** | `Private/attachments/` | `![[Private/attachments/<file>]]` | Never |
| **Secured** (default) | Private R2 bucket, via signed URL | Per-format pattern, §7 below | Yes, to a private bucket |

Tier selection: private if the file is marked/implied sensitive; secured otherwise. There is no
public tier — see PRD §6/G3.

### 5.1 Upload path selection

```
Can this session reach `rclone` AND the env var named by signSecretEnv?
  YES → upload directly: rclone copyto <file> <remote>:<bucket>/<key>
        --header-upload "Content-Disposition: inline"
        sig = HMAC-SHA256(key, secret); reference the resolved embed pattern immediately
  NO  → stage the request:
        1. Write the note's placeholder FIRST: a bare `PENDING:_pending/<sanitized-filename>`
           token on its own line (never wrapped in a link or image embed — the resolving script
           owns the final syntax).
        2. Copy the file into `pendingFolder`, using the identical sanitized filename.
           (Order matters: writing the note first avoids a race where a watcher on the pending
           folder fires before the placeholder exists to find.)
        3. Poll briefly (bounded loop, ~13 × 3s) for the placeholder to disappear before ending
           the turn — a Folder Action (or equivalent) on the pending folder finishes the job
           asynchronously with no human action required in the common case.
```

Filename sanitization (applied identically by the human/agent staging the file and by the
resolving script, as a safety net): strip to `[A-Za-z0-9._-]`, collapsing runs into a single `-`,
lowercase the extension. `Acme Letterhead.docx` → `Acme-Letterhead.docx`.

### 5.2 `upload-pending.sh` — resolution script

Runs on a machine with `rclone` + the secret (manually, or auto-triggered by a Folder Action
watching `pendingFolder`). For each staged file:

1. Sanitize the filename (safety net).
2. `rclone copyto <file> <remote>:<bucket>/<key> --header-upload "Content-Disposition: inline"` — the header is load-bearing: without it, uploaded objects have no disposition metadata at all, and browsers default to force-downloading regardless of Content-Type.
3. Compute `sig = HMAC-SHA256(key, $AIOS_R2_SIGN_SECRET)`; build the signed URL.
4. Generate the **format-specific embed block** (§7) and substitute it for the bare placeholder token anywhere it appears in the vault (retries for ~60s in case the note edit landed after the file did).
5. Move the original from `pendingFolder` to `pendingArchiveFolder`.

The script — not whatever wrote the placeholder — owns the exact render syntax. This is a
deliberate design choice: it makes a malformed embed (e.g. a `.docx` rendered as a broken image,
or a `.csv` silently downloading instead of linking) structurally impossible regardless of what
the calling session wrote, because only one code path ever produces the final markdown.

## 6. Worker (`worker.js`) — the secured-tier gate

```js
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const key = decodeURIComponent(url.pathname.replace(/^\/+/, ""));
    const sig = url.searchParams.get("sig") || "";
    if (!key) return new Response("Not found", { status: 404 });
    const expected = await hmac(env.SIGN_SECRET, key);
    if (!safeEqual(sig, expected)) return new Response("Forbidden", { status: 403 });
    const obj = await env.BUCKET.get(key);
    if (!obj) return new Response("Not found", { status: 404 });
    const h = new Headers();
    obj.writeHttpMetadata(h);              // forwards stored Content-Type/Content-Disposition
    h.set("etag", obj.httpEtag);
    h.set("Cache-Control", "private, max-age=86400");
    if (url.searchParams.get("dl")) {       // explicit-download override
      const filename = key.split("/").pop();
      h.set("Content-Disposition", `attachment; filename="${filename}"`);
    }
    return new Response(obj.body, { headers: h });
  }
};
// hmac(secret, msg) — HMAC-SHA256 via crypto.subtle, hex-encoded
// safeEqual(a, b) — constant-time string comparison, avoids timing side-channels on the sig check
```

Key properties:
- **Signature covers only `key`** (the path), not the full query string — so `&dl=1` can be appended to any already-signed URL without invalidating it. This is intentional: `dl` is a display preference, not an authorization grant.
- **`writeHttpMetadata()` is a faithful passthrough** — the Worker never hardcodes a disposition itself. Every rendering behavior is controlled entirely by what was set at upload time (§5.2) plus the optional `dl` override at request time.
- Deploy: `wrangler deploy` (picks up `worker.js` + `wrangler.toml`'s R2 binding). Re-running `wrangler deploy` alone is sufficient for a code-only change — no need to redo the secret or custom-domain steps.

## 7. Attachment embed pattern, by file type (secured tier)

This is the actual rendering contract — get this wrong and a file uploads successfully but never
previews. Implemented by `upload-pending.sh` (§5.2); this table is what it computes.

| Extension(s) | Embed as | Rendering mechanism |
|---|---|---|
| `.png .jpg .jpeg .gif .webp .svg .bmp .avif` | `![filename](url)` | Native Obsidian image embed. No callout needed — already compact. |
| `.txt` | Collapsed callout, `<iframe src="url">` | Browser renders `text/plain` natively — no viewer service needed. |
| `.pdf` | Collapsed callout, **`external-pdf` plugin's fenced code block** (see §8 — NOT an iframe) | Obsidian's own bundled PDF viewer, invoked via the plugin. |
| `.docx .xlsx .pptx` | Collapsed callout, `<iframe src="...view.officeapps.live.com/op/embed.aspx?src=<url-encoded signed URL>">` | Office Online's JS/canvas viewer — browsers can't render Office formats natively at all. |
| `.csv` | Plain link, `[filename](url)` — **never embedded** | Chrome/Firefox force-download csv even with correct inline headers; there's no reliable in-browser render path, so no embed is attempted. |
| anything else | Plain link, `[filename](url)` | Unknown format — safe fallback. |

**The collapsed-callout shape** (every iframe/plugin case):
```markdown
> [!doc]- 📎 filename.ext
> <iframe src="<signed URL>" width="100%" height="600"></iframe>
>
> [⬇ Download original](<signed URL>&dl=1)
```
`[!doc]-` is stock Obsidian callout syntax, not a custom type the vault defines — Obsidian doesn't
ship a built-in `doc` callout type, it falls back to a generic style for any unrecognized one. The
`-` immediately after the type is what makes it **foldable, collapsed by default** (`+` would be
foldable-and-expanded; no marker = not foldable at all). This is a core Obsidian feature, not
plugin-dependent.

### 7.1 Two mandatory spacing rules

Both discovered from a real broken render (two attachments in one note, no separators):

1. **A bare `>` line between the embedded block and the download link, inside one callout.** `<iframe>` (and the `external-pdf` fenced block) is block-level content, and CommonMark's HTML-block rule keeps consuming every following line until a blank line. Skip the separator and the download link gets swallowed as literal text instead of parsing as a clickable markdown link.
2. **A genuinely blank line (no `>` at all) between one attachment's callout and the next.** Skip it and consecutive `>`-prefixed lines merge into a single blockquote — the second attachment's `[!doc]-` header renders as inert text *inside* the first one's callout instead of starting its own, and everything below the first embed in that merged block breaks for the same reason as rule 1, compounded.

`upload-pending.sh` bakes both rules into its generated output unconditionally (a leading `\n`
before every resolved block, and a bare `>` line before every download link), so this can't
regress as long as the script — not a human hand-writing markdown — owns the final syntax.

### 7.2 The download button

Objects are stored `Content-Disposition: inline` by default (§5.2) so they render instead of
force-downloading. Appending `&dl=1` to the *same* signed URL (no re-signing needed — see §6)
tells the Worker to override that to `attachment` for that one request. This exists because
Office Online's own built-in "Download a copy" UI proved unreliable with signed/query-string
URLs — rather than depend on a third party's viewer chrome, every embed carries its own explicit,
Worker-backed download link.

## 8. Known limitation: PDF cannot render in a plain iframe

**Root cause:** Obsidian runs on Electron, and Electron has a confirmed, long-standing bug —
`<iframe>` elements cannot render PDF content at all (blank frame, every time), regardless of
headers, CORS, or Content-Type. This is a platform limitation, not something fixable from the
Worker or the upload script (see Chromium/Electron issue tracker: electron/electron#33094,
#33907, #33519 for the underlying reports).

**Fix:** the `external-pdf` community plugin (`tenebrisnox/external-PDF-plugin`) renders through
Obsidian's own bundled PDF viewer component instead of an iframe, sidestepping the bug entirely.
It explicitly documents support for direct HTTPS URLs carrying query strings (its own docs cite
Paperless-NGX-style authenticated links as a supported case) — so a signed URL is a documented
use case, not a workaround being asked of the plugin.

**Install** (not yet in Obsidian's official Community Plugins directory, so BRAT is required):
1. Settings → Community plugins → Browse → install and enable **BRAT**.
2. BRAT settings → "Add Beta plugin" → repo `tenebrisnox/external-PDF-plugin` → Add.
3. Enable **External PDF** under Community plugins.

**Syntax used inside the callout:**
```markdown
> [!doc]- 📎 filename.pdf
> ```external-pdf
> <signed URL>
> title: filename.pdf
> height: 600px
> ```
>
> [⬇ Download original](<signed URL>&dl=1)
```

This is the **only** plugin dependency anywhere in the attachment pipeline. Every other format in
§7 needs zero plugins.

## 9. Maintenance scripts

| Script | Purpose | Cadence |
|---|---|---|
| `resign-attachments.sh` | Recomputes every `?sig=` in the vault after `SIGN_SECRET` rotation | On demand, immediately after rotating |
| `reconcile-attachments.sh` | Diffs referenced object keys (grepped from the vault) against the bucket's actual contents; deletes orphans with `--delete` (dry-run by default) | Weekly cron; dry-run for a few weeks before trusting `--delete` |
| `delete-pending.sh` | Finishes a deletion queued by a sandboxed session (a `*.delete` file containing just the R2 key) | Auto-triggered by a Folder Action watching the delete-queue folder |

Rotation procedure: generate a new secret → `wrangler secret put SIGN_SECRET` on the Worker →
update the local env var → run `resign-attachments.sh` → commit. Old links die immediately (the
signature check isn't cached).

## 10. Verification record

Confirmed end-to-end, 2026-07-17, against a live test note in `40 Resources/`: docx via Office Online viewer (preview +
download), pdf via `external-pdf` plugin (preview + download) after the two spacing-rule fixes
and the Worker's `dl=1` addition were deployed. xlsx/pptx share docx's code path and are expected
to behave identically (untested directly as of this writing). txt shares the direct-iframe path
and needs no viewer service. csv is deliberately link-only, never embedded.
