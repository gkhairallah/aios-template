---
type: daily-log
date: <% tp.file.title %>
week: "[[<% tp.date.now("gggg-[W]ww", 0, tp.file.title, "YYYY-MM-DD") %>]]"
energy:
tags: [daily]
---
# <% tp.date.now("dddd, MMMM Do YYYY", 0, tp.file.title, "YYYY-MM-DD") %>

<< [[<% tp.date.now("YYYY-MM-DD", -1, tp.file.title, "YYYY-MM-DD") %>|Yesterday]] | [[<% tp.date.now("YYYY-MM-DD", 1, tp.file.title, "YYYY-MM-DD") %>|Tomorrow]] >>

## 🎯 Top 3 Today
_Optional — skip on reactive days._
- [ ]
- [ ]
- [ ]

## ⏱️ Hourly Log
_Add a row only when something's worth remembering later — not a timesheet._

| Time | Activity | Project / Area | Notes |
|------|----------|-----------------|-------|
|      |          |                 |       |

## 🔗 Worked On Today
_Drop `[[links]]` to the Efforts and notes you touched — this is your permanent, historical trail (and what the Stalled Projects tracker reads)._
-

## 📥 Fleeting Notes / Inbox
-

## ✅ Tasks Captured Today
_Capture with a dated link — `- [ ] thing [[YYYY-MM-DD]]`. **Promote anything still open into the
owning note's `📌 Current Focus` before the day closes**, or it's only history. Rolling view of
everything open: [[Tasks Dashboard]] · doctrine: [[Conventions]] § ✅ Tasks._
```dataview
TASK
WHERE !completed AND length(text) > 2
  AND (contains(text, this.file.name) OR file.path = this.file.path)
```

## 🌙 Evening Review
_Optional — most days extract nothing, that's fine._
- **Wins:**
- **Blockers:**
- **Extract → PARA/Atlas:**
- **Energy (1–5):**
