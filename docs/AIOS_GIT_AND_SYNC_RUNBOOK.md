# AIOS — Git & Sync Runbook (template edition, for a git newcomer)

Vault repo: `<vault path>` → `https://github.com/<your-username>/<your-vault-repo>.git`
(or your git host of choice — GitHub is used here as the concrete example).

This is the generic, placeholder-based version. The reference instance's filled-in version (real
username, repo, machine names) lives with your own instance's planning docs (or
wherever your own instance's planning docs live) — when one changes, mirror the change
to the other.

---

## 1. One-time: first push to your git host

If your agent already ran `git init`, staged everything, and made the first commit, you just need
to authenticate and push.

### a) Create an access token (used as your "password")
Most git hosts no longer accept your account password on the command line — you use a **Personal
Access Token (PAT)** instead.

1. Your git host → account settings → Developer settings → Personal access tokens → Fine-grained tokens (or equivalent).
2. **Generate new token**:
   - Repository access → *Only select repositories* → your vault repo
   - Permissions → Repository permissions → **Contents: Read and write**
   - Expiration: your call
3. Generate and **copy the token**. You won't see it again.

### b) Push (from a real terminal, not from inside your agent tool's sandbox)
```bash
cd <vault>
git push -u origin main
```
- **Username:** your git host username
- **Password:** paste the **token** (not your account password)

Set your machine to remember it (`git config --global credential.helper store`) so you only enter
it once.

### c) If the push is rejected ("fetch first" / "non-fast-forward")
That means the remote repo already has a commit (e.g. an auto-created README). Reconcile once:
```bash
git pull origin main --allow-unrelated-histories --no-edit
git push -u origin main
```

---

## 2. One-time: auto-sync with the Obsidian Git plugin

1. Obsidian → Settings → Community plugins → Browse → search **"Obsidian Git"** (by Vinzent) → Install → Enable.
2. Settings → Obsidian Git:
   - **Vault backup interval (minutes):** `10` — auto-commit + push
   - **Auto pull interval (minutes):** `10` — pull the other machine's changes
   - **Pull updates on startup:** ON
   - **Push on backup:** ON
3. Every ~10 minutes the vault commits, pushes, and pulls automatically. It uses the token stored in step 1, so do the manual push **first**.

> Repeat this setup on **every** machine that will edit the vault — each one clones and auto-syncs independently.

### Clone on a second machine
```bash
mkdir -p <parent-of-vault> && cd <parent-of-vault>
git clone https://github.com/<your-username>/<your-vault-repo>.git
```
(First `git` action there prompts for username + token once.)

---

## 3. Multi-machine sanity rules
- Let auto-pull run on startup so you don't edit a stale copy.
- Text notes rarely conflict. If you edit the **same note** on two machines while one was offline, Obsidian Git flags a merge conflict — open the file, keep the right lines, save, done.
- Don't hard-reset or force-push unless you know exactly why.

## 4. Everyday git (the plugin does most of this for you)
```bash
git status              # what changed
git add -A && git commit -m "message"   # save a snapshot
git push                # send to your git host
git pull                # get the latest
git log --oneline -10   # recent history
```

## 5. Attachments
Binaries go to **object storage behind a custom domain** (see `AIOS_SECURED_ATTACHMENTS_RUNBOOK.md`),
not into Git and not Git LFS. The repo stays text-only. Sensitive files live in `Private/` and are
never pushed at all (gitignored by default).
