---
type: project
status: active
priority: medium
deadline:
milestones:
area:
created: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - project
---
# <% tp.file.title %>

## 🎯 Outcome
_What "done" looks like._

## 🔗 Canonical Sources
_Where the real artifacts live — link, don't duplicate._
-

## 📌 Current Focus
-

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
