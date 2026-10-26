---
type: area
entity:
  - company-a
review: weekly
created: 2026-01-01
tags: [area]
---
# Example Company

> 🧪 EXAMPLE — rename to your business, set `entity` to its slug (e.g. `acme`), delete this line.

## 🎯 Standard
_What "good" looks like for this business._

## 🔗 Canonical Sources
-

## 🚀 Projects
```dataview
TABLE status AS "Status", priority AS "Priority", deadline AS "Due"
FROM "10 Efforts"
WHERE type = "project" AND (contains(entity, "company-a") OR contains(entity, "shared"))
SORT status ASC, deadline ASC
```

## 🗂️ Areas & Functions
```dataview
LIST FROM "10 Efforts"
WHERE type = "area" AND file.name != this.file.name
  AND (contains(entity, "company-a") OR contains(entity, "shared"))
```

## 🧠 Decisions
```dataview
TABLE date AS "Date", status AS "Status"
FROM "30 Atlas/Decisions"
WHERE contains(entity, "company-a") OR contains(entity, "shared")
SORT date DESC
```

## 📚 Knowledge
```dataview
LIST FROM "30 Atlas"
WHERE type = "atlas" AND (contains(entity, "company-a") OR contains(entity, "shared"))
```

## 📝 Notes
-

## 🔗 Related
- [[]]
