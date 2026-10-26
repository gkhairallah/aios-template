---
type: moc
title: Tasks Dashboard
tags: [dashboard, moc]
---
# ✅ Tasks Dashboard

The **live rolling view** of open work. Doctrine: [[Conventions]] § ✅ Tasks.

**The split this dashboard exists to enforce:** a daily note *captures* a task; the owning effort
note *tracks* it. A checkbox still sitting in a daily note is **captured but unowned** — which is
the most common way a vault quietly loses track of work. The first panel below is the one that
matters most, because it is the leak detector.

---

## 🚨 Orphans — open tasks still sitting in daily notes
**Every line here is unowned work.** It was raised on a date and never promoted into a project,
area or decision. Promote each into the owning note's `📌 Current Focus`, then leave the daily line
as history — or, if it's dead, strike it with a dated disposition (never tick a box to silence it).

> [!note]- Why `length(text) > 2` is in every query here
> The `🎯 Top 3 Today` scaffold is three **empty** `- [ ]` boxes, and Dataview parses each one as a task. In a vault with a few months of daily notes that is typically **five times more blank placeholders than real tasks** — without the filter this panel is mostly noise and recreates the exact problem it was built to fix. Keep the filter on any task query that reads `00 Calendar`.

### Last 30 days — act on these
```dataview
TASK FROM "00 Calendar"
WHERE !completed AND length(text) > 2 AND file.day >= date(today) - dur(30 days)
GROUP BY file.link
SORT file.name DESC
```

### Older backlog — triage, don't action blindly
Anything here has survived a month without being promoted, which usually means it was quietly done,
quietly abandoned, or genuinely dropped. **Check before treating one as live.**
```dataview
TASK FROM "00 Calendar"
WHERE !completed AND length(text) > 2 AND file.day < date(today) - dur(30 days)
GROUP BY file.link
SORT file.name DESC
```

---

## 📌 Open by effort — projects and areas
The tracked copies. This is where tasks are *supposed* to live, and what a weekly review walks.

```dataview
TASK FROM "10 Efforts"
WHERE !completed AND length(text) > 2 AND !owner
GROUP BY file.link
SORT file.name ASC
```

---

## 👀 Watching: raise with the owner, don't do it
Grouped by person: each group is that person's agenda for the next 1:1. Doctrine: [[Conventions]] § 👀 Mine vs Watching.
```dataview
TASK FROM "10 Efforts" OR "00 Calendar"
WHERE !completed AND length(text) > 2 AND owner
GROUP BY owner
```

---

## 🧠 Decision follow-ups
A decision's `📌 Follow-up` boxes are the one live checkbox allowed inside a `date:` note, because
the follow-up belongs to that decision and nowhere else.

> [!warning]- ⚠️ Known: these have historically gone untouched
> Decision follow-up boxes are easy to write and easy to never look at again. If a batch has gone untouched for months, that is evidence the boxes were not being read — not evidence the work is open. **Treat a long-untouched follow-up as needing verification, not as a to-do to action blindly**, and walk them during `/review`.

```dataview
TASK FROM "30 Atlas/Decisions"
WHERE !completed AND length(text) > 2
GROUP BY file.link
SORT file.name ASC
```

---

## 📊 Counts

```dataviewjs
const buckets = [
  ["Daily notes (unowned)", '"00 Calendar"'],
  ["Efforts (tracked)",     '"10 Efforts"'],
  ["Decisions (follow-up)", '"30 Atlas/Decisions"'],
];

const rows = [];
for (const [label, src] of buckets) {
  let open = 0, done = 0, blank = 0;
  for (const p of dv.pages(src)) {
    for (const t of (p.file.tasks ?? [])) {
      if ((t.text ?? "").trim().length <= 2) { blank++; continue; }   // Top 3 scaffold
      t.completed ? done++ : open++;
    }
  }
  rows.push([label, open, done, open + done, blank || "—"]);
}

dv.table(["Where", "Open", "Done", "Total", "Blank scaffold"], rows);

const orphans = rows[0][1];
dv.paragraph(
  orphans === 0
    ? "**✅ No orphaned tasks — everything captured has been promoted or closed.**"
    : `**⚠️ ${orphans} task${orphans === 1 ? "" : "s"} sitting unowned in daily notes.** Promote or close them; see the first panel.`
);
```

---

## 🗒️ Tasks captured in the last 14 days
Captures carrying a dated link, newest first — the recent flow, whether or not they were promoted.
Useful for spotting a day whose captures never got picked up.

```dataviewjs
const days = [];
for (let i = 0; i < 14; i++) {
  const d = new Date();
  d.setDate(d.getDate() - i);
  days.push(d.toISOString().slice(0, 10));
}

// A task "belongs" to a date if it carries that date as a link, wherever the task lives.
const rows = [];
for (const p of dv.pages()) {
  for (const t of (p.file.tasks ?? [])) {
    if ((t.text ?? "").trim().length <= 2) continue;
    const hit = days.find(d => t.text.includes(d));
    if (hit) rows.push([hit, t.completed ? "✅" : "⬜", t.text.replace(/\[\[\d{4}-\d{2}-\d{2}\]\]/g, "").trim(), p.file.link]);
  }
}
rows.sort((a, b) => b[0].localeCompare(a[0]));

if (rows.length) dv.table(["Captured", "", "Task", "Lives in"], rows);
else dv.paragraph("_No dated task captures in the last 14 days. This fills in as the convention gets used._");
```

## 🔗 Related
- [[Conventions]]
- [[Filing Rules]]
- [[Efforts Dashboard]]
- [[Decisions Dashboard]]
- [[Daily Trends Dashboard]]
