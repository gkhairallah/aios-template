# `.aios/` — setup guide

> **New to AIOS?** Read **[../docs/AIOS_GETTING_STARTED.md](../docs/AIOS_GETTING_STARTED.md)** first — it explains the whole system end to end and tells you whether you need anything in this folder at all. (Short answer: only if you turn on the secured attachment tier.) The relevant section is [Part 6 — Attachments](../docs/AIOS_GETTING_STARTED.md#part-6--attachments-and-whether-you-need-r2-at-all).

This folder holds AIOS's local automation: config and shell scripts that support the
`aios-notes` skill pack. Everything here that could contain your personal values (vault
path, bucket name, domain, lock-file names) ships as a `.example` file and is gitignored
once you create the real one — so cloning this template never leaks, and never requires,
anyone else's setup.

**You only need any of this if you're turning on the secured (R2) attachment tier.** If
you're fine with attachments living in the vault itself (`defaultDestination: "vault"`,
the default in `attachments.example.json`), skip this folder entirely — the `attach`
skill works with zero setup.

## What's here

| File | Ships as | Purpose |
|---|---|---|
| `attachments.json` | `attachments.example.json` | Tells the `attach` skill where files go: vault-local vs. object storage, and (if the latter) which bucket/domain/remote to use, plus the staged-upload fallback fields for agent sessions with no local shell. |
| `config.json` | `config.example.json` | Shape reference only. The **real** per-machine vault pointer lives outside the vault at `~/.aios/config.json` and is written by the skill pack's one-time init command — it holds an absolute path that differs per machine, so it must never travel with the repo. A stray `.aios/config.json` inside the vault is gitignored as a safety net. |
| `upload-pending.sh` | `upload-pending.sh.example` | Finishes uploads staged by a sandboxed agent session that has no local `rclone`/secret — uploads to R2, signs the URL, rewrites the note. |
| `resign-attachments.sh` | `resign-attachments.sh.example` | Re-signs every attachment URL in the vault after you rotate your signing secret. |
| `reconcile-attachments.sh` | `reconcile-attachments.sh.example` | Finds (and optionally deletes) R2 objects no longer referenced by any note. |
| `delete-pending.sh` | `delete-pending.sh.example` | Finishes deletions queued by an agent session that has no `rclone`/secret. |
| `Skills/` | (committed as-is) | Vendored, editable mirror of the installed `aios-notes` plugin skill pack — lets you read/tweak the skill instructions without digging into the plugin cache. |

## Setup — the `.example` → real workflow

1. **Decide if you need R2 at all.** Most people don't, at least not on day one. The
   vault-local tier just writes files into the vault's `attachments/` folder and commits
   them with everything else. Come back to this section when you outgrow that.
2. **Stand up the R2 bucket + Worker + signing secret.** Full walkthrough, including the
   exact `worker.js` to deploy, is in
   [`../docs/AIOS_SECURED_ATTACHMENTS_RUNBOOK.md`](../docs/AIOS_SECURED_ATTACHMENTS_RUNBOOK.md).
   Do that first — the scripts below assume the bucket/Worker/secret already exist.
3. **Copy each `.example` file, dropping the suffix**, and fill in your own values:
   ```bash
   cd .aios
   cp attachments.example.json attachments.json
   cp upload-pending.sh.example upload-pending.sh
   cp resign-attachments.sh.example resign-attachments.sh
   cp reconcile-attachments.sh.example reconcile-attachments.sh
   cp delete-pending.sh.example delete-pending.sh
   chmod +x *.sh
   ```
4. **Edit each new file's `CONFIG` block** (the `.sh` files have one clearly marked near
   the top; `attachments.json` just needs its placeholder strings replaced):
   - `VAULT` → the real path to your vault, e.g. `$HOME/REPOS/MyVault` (use `$HOME`, never a
     hard-coded `/Users/<name>` — usernames differ between machines and the failure is silent)
   - `REMOTE` → the rclone remote name you chose when you ran `rclone config create`
   - `BUCKET` → your R2 bucket name
   - `BASE` → your Worker's custom domain, e.g. `https://cdn.yourdomain.com`

   `resign-attachments.sh` is the exception — it only needs `VAULT` and `BASE`, since re-signing
   rewrites URLs in your notes and never touches storage.
5. **Put the signing secret somewhere the scripts can read it.** Either export it in your
   shell profile (`~/.zshrc`) as `AIOS_R2_SIGN_SECRET`, or — since GUI automations
   (Automator/Alfred/Shortcuts/Folder Actions) don't source your shell profile — drop it
   in `~/.aios/secrets.env` as `export AIOS_R2_SIGN_SECRET="..."`. Every script checks
   both.
6. **Never commit the real files.** They're already covered by `.gitignore`
   (`.aios/attachments.json`, `.aios/*.sh`) — only the `.example` versions and this
   README are tracked.

## `Skills/`

This is a plain copy of the `aios-notes` plugin's skill instructions, kept here so you
can read or adjust them without hunting through the plugin cache. It's committed as-is —
nothing personal lives in it. If you edit it, note that it won't automatically re-sync
with future plugin updates; treat it as a local override/reference copy.

## More detail

- **Start here:** `../docs/AIOS_GETTING_STARTED.md`
- End-to-end architecture and rationale: `../docs/AIOS_HLD.md`, `../docs/AIOS_LLD.md`
- Full R2 setup + embed-syntax doctrine: `../docs/AIOS_SECURED_ATTACHMENTS_RUNBOOK.md`
- Git/sync setup: `../docs/AIOS_GIT_AND_SYNC_RUNBOOK.md`
