---
type: area
review: weekly
created: <% tp.date.now("YYYY-MM-DD") %>
tags: [area]
---
# <% tp.file.title %>

## 🎯 Standard
_What "good" looks like for this ongoing responsibility._

## 🔗 Canonical Sources
_Key systems and authoritative homes for this area — link, don't duplicate._
-

## 🚀 Active Projects
```dataview
LIST FROM "10 Efforts"
WHERE type = "project" AND status = "active" AND contains(area, this.file.link)
```

## 🧠 Decisions
```dataview
LIST FROM "30 Atlas/Decisions"
WHERE type = "decision" AND contains(related, this.file.link)
```

## 📝 Notes
-

## 🗒️ Log
```dataview
LIST FROM "00 Calendar"
WHERE type = "daily-log" AND contains(file.outlinks, this.file.link)
SORT file.name DESC
```

## 🔗 Related
- [[]]
