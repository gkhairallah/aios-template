---
description: Run a monthly structural health audit across your vault
---

Use the **vault-ops** skill (Vault Health Audit). This is heavier than `/review` — meant for a
monthly cadence, not weekly. Check: PARA-quadrant balance (is `40 Resources` / `90 Archives`
actually being used), doctrine drift (invalid `type`/`status`/`priority` values, notes in the
wrong folder for their `type`), dead or orphaned `[[links]]`, entity-stub sprawl (lightweight
`type: atlas` stubs standing in for people/orgs that have no real type yet), lifecycle hygiene
(done/dormant projects still in `10 Efforts`), whether structural changes have been mirrored to
`~/REPOS/AIOS Template` per the Conventions' template-sync rule, and whether daily-log habits
(Top 3, Evening Review, Fleeting Notes) are holding up. Report as a prioritized punch list; offer
to act on any item with approval.
