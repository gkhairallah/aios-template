---
type: moc
title: Decisions Dashboard
tags: [dashboard, moc]
---
# 🧭 Decisions Dashboard

A running log of every significant decision — the "why did I choose this?" archive.

## All Decisions (newest first)
```dataview
TABLE date AS "Date", status AS "Status", related AS "Related"
FROM "30 Atlas/Decisions" or "90 Archives"
WHERE type = "decision"
SORT date DESC
```

## ⚠️ Open / Proposed
```dataview
TABLE date AS "Date"
FROM "30 Atlas/Decisions" or "90 Archives"
WHERE type = "decision" AND status = "proposed"
SORT date DESC
```

## Superseded
```dataview
LIST
FROM "30 Atlas/Decisions" or "90 Archives"
WHERE type = "decision" AND status = "superseded"
```
