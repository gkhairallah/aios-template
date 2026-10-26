---
type: moc
title: Home
tags: [moc, home]
---
# 🏠 AIOS Home

## 📂 Filing Rules — first YES wins
1. Just happened / just occurred to me → **`00 Calendar`** (log it — no decision)
2. WORK — can I mark it **DONE** and stop? → **`10 Efforts`** · `type: project`
3. WORK — ongoing **standard I maintain**, no end? → **`10 Efforts`** · `type: area`
4. KNOWLEDGE — I **authored** it? → **`30 Atlas`**
5. KNOWLEDGE — I **collected** it? → **`40 Resources`**
6. Done / dead / dormant? → **`90 Archives`**

> Torn → it's Knowledge. Still torn → leave it in the log. Folders are weak; `type` + `[[links]]` are strong — a misfile costs nothing. Full guides: [[Filing Rules]] · [[Conventions]]

## 📊 Dashboards
- [[Efforts Dashboard]] — projects, deadlines, areas, stalled work
- [[Decisions Dashboard]] — every significant decision
- [[Daily Trends Dashboard]] — efforts touched per day, energy trend

## 🏢 Companies
- _Add one hub per business in `10 Efforts/Companies/` — see [[Example Company]]._

## Active Efforts (projects)
```dataview
LIST FROM "10 Efforts"
WHERE type = "project" AND status = "active"
```

## Recent Decisions
```dataview
TABLE date AS "Date", status AS "Status"
FROM "30 Atlas/Decisions"
WHERE type = "decision"
SORT date DESC
LIMIT 5
```
