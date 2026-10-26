---
description: Capture a note into your AIOS / Obsidian vault
---

Use the **capture-note** skill to create an AIOS note from the user's input.

Input: $ARGUMENTS

If no input was provided, ask what they want to capture. Then follow the skill's workflow exactly:
1. Load the vault's `Conventions` and `Filing Rules` (or the bundled fallbacks).
2. Classify the note (Filing Rules cascade) and choose the destination folder.
3. Draft the note from the matching template — frontmatter, section headers, canonical-source links, suggested `[[links]]`.
4. Interview the user only for genuine gaps (entity, deadline, body depth, links).
5. Show the full draft + destination path, explain judgment calls, and write only after approval.
