---
type: moc
title: Efforts Dashboard
tags: [dashboard, moc]
---
# 📊 Efforts Dashboard

**Efforts** = Projects (have a done-state) + Areas (ongoing). One folder, split by `type`.

## 📊 Status & Priority Breakdown
```dataviewjs
function barRow(container, label, value, max, color) {
  const row = container.createEl("div", {attr: {style: "display:flex;align-items:center;margin:4px 0;font-size:0.9em;"}});
  row.createEl("div", {text: label, attr: {style: "width:90px;flex-shrink:0;text-transform:capitalize;"}});
  const wrap = row.createEl("div", {attr: {style: "flex:1;background:var(--background-modifier-border);border-radius:4px;overflow:hidden;height:16px;margin:0 8px;"}});
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  wrap.createEl("div", {attr: {style: `width:${pct}%;height:100%;background:${color};`}});
  row.createEl("div", {text: String(value), attr: {style: "width:24px;text-align:right;"}});
}

// Projects live in 10 Efforts while active/on-hold, and move to 90 Archives once
// done/dead — both are scanned so lifecycle (a folder move) never skews the counts.
const efforts = dv.pages('"10 Efforts" or "90 Archives"').where(p => p.type === "project");
const statusCounts = {active: 0, "on-hold": 0, done: 0};
const priorityCounts = {high: 0, medium: 0, low: 0};
for (const p of efforts) {
  if (p.status in statusCounts) statusCounts[p.status]++;
  if (p.priority in priorityCounts) priorityCounts[p.priority]++;
}

// Decisions are a separate `type` with their own status vocabulary
// (proposed/decided/superseded) — kept in their own column, not folded into "Done".
const decisions = dv.pages('"30 Atlas/Decisions" or "90 Archives"').where(p => p.type === "decision");
const decisionCounts = {proposed: 0, decided: 0, superseded: 0};
for (const p of decisions) {
  if (p.status in decisionCounts) decisionCounts[p.status]++;
}

// Grid (not flex-wrap) so wrapped columns land on the same left edge as the first row
// instead of re-centering/re-justifying when the container is too narrow for 3 columns.
const wrapper = dv.el("div", "", {attr: {style: "display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:8px 32px;align-items:start;"}});
const statusCol = wrapper.createEl("div", {attr: {style: "min-width:220px;"}});
statusCol.createEl("div", {text: "Project Status", attr: {style: "font-weight:bold;margin-bottom:4px;"}});
const maxStatus = Math.max(1, ...Object.values(statusCounts));
barRow(statusCol, "Active", statusCounts.active, maxStatus, "var(--color-green)");
barRow(statusCol, "On-hold", statusCounts["on-hold"], maxStatus, "var(--color-orange)");
barRow(statusCol, "Done", statusCounts.done, maxStatus, "var(--color-base-40)");

const priorityCol = wrapper.createEl("div", {attr: {style: "min-width:220px;"}});
priorityCol.createEl("div", {text: "Priority", attr: {style: "font-weight:bold;margin-bottom:4px;"}});
const maxPriority = Math.max(1, ...Object.values(priorityCounts));
barRow(priorityCol, "High", priorityCounts.high, maxPriority, "var(--color-red)");
barRow(priorityCol, "Medium", priorityCounts.medium, maxPriority, "var(--color-orange)");
barRow(priorityCol, "Low", priorityCounts.low, maxPriority, "var(--color-blue)");

const decisionCol = wrapper.createEl("div", {attr: {style: "min-width:220px;"}});
decisionCol.createEl("div", {text: "Decisions", attr: {style: "font-weight:bold;margin-bottom:4px;"}});
const maxDecision = Math.max(1, ...Object.values(decisionCounts));
barRow(decisionCol, "Proposed", decisionCounts.proposed, maxDecision, "var(--color-orange)");
barRow(decisionCol, "Decided", decisionCounts.decided, maxDecision, "var(--color-green)");
barRow(decisionCol, "Superseded", decisionCounts.superseded, maxDecision, "var(--color-base-40)");
```

## 🔥 Active Projects
```dataview
TABLE status AS "Status", area AS "Area", priority AS "Priority",
  deadline AS "Due",
  choice(deadline, (date(deadline) - date(today)).day, "—") AS "Days Left"
FROM "10 Efforts"
WHERE type = "project" AND status = "active"
SORT deadline ASC
```

## ⏳ Due in Next 14 Days
```dataview
TABLE deadline AS "Due", (date(deadline) - date(today)).day AS "Days Left"
FROM "10 Efforts"
WHERE type = "project" AND status = "active" AND deadline
  AND date(deadline) <= date(today) + dur(14 days)
SORT deadline ASC
```

## 🪜 Upcoming Milestones (next 90 days)
```dataviewjs
// Reads the `milestones` frontmatter list: plain strings with a leading ISO date.
// `deadline` stays the single-valued alarm; this is the ladder behind it.
const today = dv.date("today");
const rows = [];
for (const p of dv.pages('"10 Efforts"').where(p => p.type === "project" && p.status !== "done")) {
  for (const m of (p.milestones ?? [])) {
    const str = String(m);
    const hit = str.match(/(\d{4}-\d{2}-\d{2})/);
    if (!hit) continue;
    const d = dv.date(hit[1]);
    const days = Math.floor(d.diff(today, "days").days);
    if (days < 0 || days > 90) continue;
    const label = str.replace(hit[1], "").replace(/^[\s—–-]+/, "").trim();
    rows.push([d.toFormat("yyyy-LL-dd"), days, p.file.link, label, /🔴/.test(str) ? "🔴" : ""]);
  }
}
rows.sort((a, b) => a[1] - b[1]);
if (rows.length) dv.table(["Date", "Days", "Project", "Milestone", "Hard"], rows);
else dv.paragraph("_No milestones in the next 90 days._");
```

## 🚨 Overdue
```dataview
TABLE deadline AS "Was Due", (date(today) - date(deadline)).day AS "Days Over"
FROM "10 Efforts"
WHERE type = "project" AND status != "done" AND deadline
  AND date(deadline) < date(today)
SORT deadline ASC
```

## ⏸️ On Hold
```dataview
TABLE area AS "Area", priority AS "Priority"
FROM "10 Efforts"
WHERE type = "project" AND status = "on-hold"
SORT priority ASC
```

## 🗂️ Areas (ongoing responsibilities)
```dataview
TABLE review AS "Review Cadence", file.mtime AS "Last Touched"
FROM "10 Efforts"
WHERE type = "area" AND (contains(entity, "shared") OR !entity)
SORT file.name ASC
```

## 💤 Stalled Projects (no daily-log mention lately)
```dataviewjs
const today = dv.date("today");
const projects = dv.pages('"10 Efforts"')
  .where(p => p.type === "project" && p.status === "active");

const rows = projects.map(p => {
  const inbound = dv.pages('"00 Calendar"')
    .where(d => d.type === "daily-log"
      && d.file.outlinks.some(l => l.path === p.file.path));
  let last = null;
  for (const d of inbound) {
    const dt = d.date ? dv.date(d.date) : null;
    if (dt && (!last || dt > last)) last = dt;
  }
  const idle = last ? Math.floor(today.diff(last, "days").days) : 9999;
  return [p.file.link, last ? last.toFormat("yyyy-LL-dd") : "never", idle];
});

rows.sort((a, b) => b[2] - a[2]);
dv.table(["Project", "Last Touched", "Days Idle"],
  rows.map(r => [r[0], r[1], r[2] === 9999 ? "never" : r[2]]));
```

## 🏢 Companies
```dataview
TABLE review AS "Review Cadence"
FROM "10 Efforts/Companies"
WHERE type = "area"
SORT file.name ASC
```
