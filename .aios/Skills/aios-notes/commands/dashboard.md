---
description: Create or extend an auto-syncing project dashboard (HTML file + registry.json + one shared sync task)
---

Use the **live-dashboard-ops** skill.

Input: $ARGUMENTS

If no input was provided, ask whether this is a new project dashboard, a change to an existing
one's sources, or a look at what's registered. Then follow the skill's workflow exactly:
bootstrap the dashboards folder and sync task if this vault doesn't have them yet, build or update
the dashboard HTML file, update `registry.json` and re-render `index.html`, teach the sync task any
new source type, write through to the anchoring vault note, and write nothing until the combined
summary is approved.
