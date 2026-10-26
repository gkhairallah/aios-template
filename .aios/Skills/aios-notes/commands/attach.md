---
description: Attach a dropped file to the right note (private → local, else per config)
---

Use the **attach** skill. Input: $ARGUMENTS

Identify the dropped file and the target note, check privacy, and route per `.aios/attachments.json`:
private → `Private/attachments/` (local, never uploaded); `local` mode → `attachments/`; `r2` mode →
upload with the configured tool and reference the custom-domain URL. Add it under the note's
`📎 Attachments` section and write on approval.
