---
type: moc
title: Daily Trends Dashboard
tags: [dashboard, moc]
---
# 📈 Daily Trends Dashboard

Trends pulled from `00 Calendar` daily logs — how much ground got covered each day, and how
energy has tracked. Bars are relative to the highest value in the window shown, not an absolute
scale (except Energy, which is fixed 1–5).

## 🔥 Efforts Touched Per Day (last 14 days)
_Counts links from each daily log to `10 Efforts` notes — a rough proxy for how much the day
touched real work, not a timesheet._
```dataviewjs
const WINDOW_DAYS = 14;
const today = dv.date("today");

const effortsSet = new Set(
  dv.pages('"10 Efforts"').where(p => p.type === "project" || p.type === "area")
    .map(p => p.file.path)
);

const fmtDate = (d) => d.toLocal().toFormat("ccc, LLL d");

const logs = dv.pages('"00 Calendar"')
  .where(p => p.type === "daily-log" && p.date)
  .array()
  .filter(p => {
    const d = dv.date(p.date);
    if (!d) return false;
    const diff = today.diff(d, "days").days;
    return diff >= 0 && diff < WINDOW_DAYS;
  })
  .sort(p => p.date, 'asc');

if (logs.length === 0) {
  dv.paragraph("No daily logs found in this window.");
} else {
  const rows = logs.map(p => {
    const count = p.file.outlinks.filter(l => effortsSet.has(l.path)).length;
    return {date: dv.date(p.date), count};
  });
  const max = Math.max(1, ...rows.map(r => r.count));

  const container = dv.el("div", "", {attr: {style: "margin-top:6px;"}});
  for (const r of rows) {
    const row = container.createEl("div", {attr: {style: "display:flex;align-items:center;margin:3px 0;font-size:0.9em;"}});
    row.createEl("div", {text: fmtDate(r.date), attr: {style: "width:100px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-right:8px;"}});
    const wrap = row.createEl("div", {attr: {style: "flex:1;background:var(--background-modifier-border);border-radius:4px;overflow:hidden;height:14px;margin:0 8px;"}});
    const pct = Math.round((r.count / max) * 100);
    wrap.createEl("div", {attr: {style: `width:${pct}%;height:100%;background:var(--color-blue);`}});
    row.createEl("div", {text: String(r.count), attr: {style: "width:20px;text-align:right;"}});
  }
}
```

## 🔋 Energy Trend (days with a recorded value)
_Sparse by design — only logged on days you filled in the Evening Review. Fixed 1–5 scale, so
bar length is directly comparable across days._
```dataviewjs
const WINDOW_DAYS = 30;
const today = dv.date("today");
const fmtDate = (d) => d.toLocal().toFormat("ccc, LLL d");

const logs = dv.pages('"00 Calendar"')
  .where(p => p.type === "daily-log" && p.date && p.energy)
  .array()
  .filter(p => {
    const d = dv.date(p.date);
    if (!d) return false;
    const diff = today.diff(d, "days").days;
    return diff >= 0 && diff < WINDOW_DAYS;
  })
  .sort(p => p.date, 'asc');

if (logs.length === 0) {
  dv.paragraph(`No energy values recorded in the last ${WINDOW_DAYS} days.`);
} else {
  const container = dv.el("div", "", {attr: {style: "margin-top:6px;"}});
  for (const p of logs) {
    const val = Number(p.energy);
    const row = container.createEl("div", {attr: {style: "display:flex;align-items:center;margin:3px 0;font-size:0.9em;"}});
    row.createEl("div", {text: fmtDate(dv.date(p.date)), attr: {style: "width:100px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-right:8px;"}});
    const wrap = row.createEl("div", {attr: {style: "flex:1;background:var(--background-modifier-border);border-radius:4px;overflow:hidden;height:14px;margin:0 8px;"}});
    const pct = Math.round((val / 5) * 100);
    const color = val <= 2 ? "var(--color-red)" : val === 3 ? "var(--color-orange)" : "var(--color-green)";
    wrap.createEl("div", {attr: {style: `width:${pct}%;height:100%;background:${color};`}});
    row.createEl("div", {text: String(val), attr: {style: "width:20px;text-align:right;"}});
  }
}
```

## 🔗 Related
- [[Efforts Dashboard]]
- [[Home]]
