---
description: One-time setup — tell AIOS where your vault lives (so future actions are fast)
---

Set up (or update) the AIOS config so every future note/log/attach action finds the vault
**instantly**, without searching the filesystem.

0. **Connect the vault as a Cowork folder (biggest speed win).** Make sure the vault — or its
   parent (e.g. `~/REPOS`) — is a **connected Cowork folder**, so Claude uses fast **native** file
   access (Read/Write/Edit) instead of an external file MCP. If it isn't connected, ask the user to
   connect it (or use the request-directory tool). This removes the per-query "which tool / check
   access / find the vault" overhead.
1. **Determine the vault path:**
   - If the user provided a path in $ARGUMENTS, use it.
   - Otherwise, look for likely vaults — folders containing **both** `30 Atlas/` and `Templates/` —
     in common locations (the connected folder, `~/REPOS/*`, `~/Documents/*`, `~/Obsidian/*`) and
     propose the best candidate.
   - Confirm the absolute path with the user.
2. **Write `~/.aios/config.json`** (create `~/.aios/` if needed):
   ```json
   {
     "vaultPath": "<absolute path to the vault>",
     "vaultName": "<vault folder name>"
   }
   ```
3. **Confirm:** tell the user that future actions will read this and go straight to the vault. This
   only needs to be run once per machine (re-run it if the vault ever moves).
