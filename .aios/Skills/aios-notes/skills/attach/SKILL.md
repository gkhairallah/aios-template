---
name: attach
description: Attach a file to the right AIOS note, routed by exposure tier. Use when the user drops or uploads a file with an instruction like "attach this to…", "add this image/pdf/doc to my note", "save this attachment", or wants to file a screenshot, document, or PDF into their vault. Two tiers only — private (local-only, never uploaded) and secured (a private R2 bucket served via a non-expiring signed URL). Never makes a file publicly guessable.
unlisted: true
---

# Attach

Route a dropped file and reference it in the right note. **Two exposure tiers: `private`
(local-only) and `secured` (private R2 via a signed URL). Nothing is ever made publicly guessable.**
Show the change and get approval before writing.

## Resolve the vault, then load config
First read `~/.aios/config.json` for `vaultPath` and use it directly — do **not** search. If it's
missing, ask (or have them run `/aios-init`) and save it. Then read the **whole**
`<vaultPath>/.aios/attachments.json` file, not just the fields below — some vaults add extra
fields describing a fallback for environments that can't run local tools (see the next section).
Core fields: `defaultDestination` (`vault` = interim in-repo | `r2` = secured), `localFolder`,
`privateFolder`, and `r2` = `{ remote, bucket (private), workerBaseUrl, keyTemplate, signSecretEnv }`.

## Two tiers (default is NOT public)
- **Private / sensitive** → `privateFolder`. Local-only, gitignored, **never synced or uploaded**. Use for anything truly sensitive.
- **Secured (default)** — the everyday tier:
  - **R2 configured** (`defaultDestination: r2` + an `r2` block) → upload to the **private** bucket and reference a **signed URL**: `<workerBaseUrl>/<key>?sig=<HMAC>`. Not publicly guessable, renders in Obsidian, portable, revocable by rotating the secret. Repo stays text-only.
  - **R2 not set up yet** (`defaultDestination: vault`) → keep the file in `localFolder` inside the private repo (interim) and tell the user it will move to secured R2 once the Worker is configured.
- **No public tier.** To share, hand someone the signed URL — it works for them. A truly-public-forever link is a rare manual one-off, not a standing option.

## Before running rclone: confirm it can actually run here
"R2 configured" in the config doesn't mean *this session* can reach it. Some environments running
this skill (e.g. a sandboxed session with file access to the vault) have no local shell tools and
no access to the machine's environment variables — `rclone` won't be on PATH and the secret named
by `signSecretEnv` won't be set, even though R2 is fully configured for the vault's owner. Don't
assume either is available — check first, then route:
1. Confirm `rclone` is actually callable, and that the `signSecretEnv` variable is actually set,
   in *this* session.
2. **Both available** → do the upload/delete directly, as described in Steps/Deleting below.
3. **Either missing** → this session can't finish the job itself, but staging is enough — most
   vault owners have already set up something (like a Folder Action) that finishes the job
   automatically the moment the file lands, with no action needed from anyone. Look through the
   rest of `attachments.json` for fields describing that fallback (commonly named something like
   `pendingFolder` / `pendingResolution` for uploads, `deleteQueueFolder` / `deleteResolution` for
   deletions) and follow them **exactly and completely** — they typically describe a poll-before-
   replying step (re-check the note/queue for resolution for a bounded stretch of time before you
   end your turn) specifically so you can often report the finished result in the same reply
   instead of a "you need to do something" message. **Telling the user to manually run a script
   that a Folder Action already runs automatically is the one thing this fallback exists to
   avoid — don't do it** unless the fallback fields explicitly say there's no such automation, or
   you have real evidence it isn't running (e.g. the same file stayed unresolved across more than
   one separate conversation). If no fallback fields exist at all, say plainly that this session
   can't complete a secured-tier attach/delete here, and ask the user to run it from a shell that
   has `rclone` and the secret — that's the one case where naming the manual step is correct.
4. Whichever path is used, never fabricate a signed URL. Signing requires the secret — if this
   session doesn't have it, it cannot produce a valid signature itself, only stage the request.

## Steps
1. **Identify the file** and the **target note** (infer or ask).
2. **Determine tier:** private if marked/sensitive; otherwise secured (default).
3. **Route:**
   - **Private** → copy into `privateFolder`; reference `![[Private/attachments/<file>]]`. Never upload.
   - **Secured + R2 configured + rclone/secret available here** → `rclone copy "<file>" <remote>:<bucket>/<key> --header-upload "Content-Disposition: inline"` (`<key>` from `keyTemplate`; the header flag matters — without it some browsers/Workers force a download regardless of Content-Type); compute `sig = HMAC-SHA256(<key>, $SIGN_SECRET)` where the secret is the env var named by `signSecretEnv`. Reference the signed URL using the format-specific embed pattern in `30 Atlas/Conventions.md § 📎 Attachments` (images → plain embed; txt → collapsed-callout iframe + a `&dl=1` download link; pdf → collapsed-callout using the `external-pdf` community plugin's code-block syntax, NOT an iframe — Obsidian's Electron shell can't render PDFs in one at all; docx/xlsx/pptx → collapsed-callout iframe via Office Online's viewer + a `&dl=1` download link; csv/other → plain link — never embed csv). Don't keep the binary in git.
   - **Secured + R2 configured but rclone/secret NOT available here** → follow the config's fallback fields (see above). **Order matters:** write the note's placeholder reference *first*, and only copy the file into the pending/fallback folder *after* the note already contains it. A local Folder Action (or similar) may start processing the instant the file lands, and if the note edit hasn't landed yet, the automation's one-shot search for the placeholder can miss it and leave the note stuck with stale text. Writing the note first removes that race entirely.
   - **Secured + R2 not set up at all** → copy into `localFolder`; reference `![[attachments/<file>]]`; note it's interim.
4. **Sanitize** the filename for keys/paths.
5. **Attach** under the note's `## 📎 Attachments` section (create if absent); show the edit, the tier, and the destination; write on approval.

## Deleting a secured attachment
1. Remove the attachment's reference from the note directly — a normal edit, no external tool needed.
2. Recover the R2 key from the existing signed URL by stripping the `workerBaseUrl` prefix and the
   `?sig=...` suffix. Reading a key back out of a URL needs no secret — only *signing* a new one does.
3. Check `rclone`/the secret exactly as above.
   - **Available** → `rclone deletefile <remote>:<bucket>/<key>` directly.
   - **Not available** → follow the config's deletion fallback fields if present (commonly
     `deleteQueueFolder` / `deleteResolution`); otherwise tell the user this session can't finish
     the deletion and it needs to run from a shell that has `rclone`.
4. Don't say the object is deleted until it actually is — a queued request isn't a completed deletion.

## Notes
- "Secured" = unguessable + revocable + shareable-by-link (anyone with the signed link can view). For truly-only-you, use the **private** tier.
- A separate scheduled reconciler removes orphaned R2 objects (parse keys, ignoring `?sig=`).
- Briefly explain the routing decision (which note; which tier; where it went).
