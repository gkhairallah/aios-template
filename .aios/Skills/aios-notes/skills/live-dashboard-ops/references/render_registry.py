#!/usr/bin/env python3
"""Render the Live Dashboard Registry as a static index.html from registry.json.

Replaces the Claude artifact's live `db` capability. Run from this folder:
    python3 render_registry.py
Reads ./registry.json, writes ./index.html. No dependencies beyond the stdlib.
"""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = {"vault_note": "Vault note", "email": "Email", "teams": "Teams", "coda": "Coda", "crm": "CRM"}


def rel_time(iso, now):
    if not iso:
        return "never"
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return "never"
    mins = round((now - d).total_seconds() / 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hrs = round(mins / 60)
    if hrs < 48:
        return f"{hrs}h ago"
    return f"{round(hrs / 24)}d ago"


def card(pid, p, now):
    e = html.escape
    counts, order = {}, []
    for s in p.get("sources") or []:
        t = (s or {}).get("type") or "source"
        if t not in counts:
            counts[t] = 0
            order.append(t)
        counts[t] += 1
    badges = "".join(
        f'<span class="badge {"b-grey" if t == "vault_note" else "b-blue"}">'
        f'{e(LABELS.get(t, t))}{" ×" + str(counts[t]) if counts[t] > 1 else ""}</span>'
        for t in order
    )
    status = p.get("status") or "pending"
    pill = {"ok": "pill-ok", "error": "pill-error"}.get(status, "pill-pending")
    name = e(p.get("name") or pid)
    local = p.get("localFile")
    name_html = f'<a href="{e(local)}">{name}</a>' if local else name
    err = f'<div class="meta err">{e(p["lastError"])}</div>' if p.get("lastError") else ""
    synced = p.get("lastSyncedAt") or ""
    return (
        '<div class="card"><div class="row"><div>'
        f'<div class="name">{name_html}</div>'
        + (f'<div class="meta">{e(p["vaultNote"])}</div>' if p.get("vaultNote") else "")
        + f'<div class="badges">{badges}</div>{err}</div>'
        f'<div class="status"><div class="statusline"><span class="pill {pill}">{e(status)}</span>'
        f'<span class="synced" title="{e(synced)}">synced {e(rel_time(synced, now))}</span></div></div>'
        "</div></div>"
    )


def main():
    reg = json.loads((HERE / "registry.json").read_text(encoding="utf-8"))
    projects = reg.get("projects", {})
    now = datetime.now(timezone.utc)
    cards = "".join(card(k, v, now) for k, v in sorted(projects.items(), key=lambda kv: kv[1].get("name") or kv[0]))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Live Dashboard Registry</title>
<style>
:root{{color-scheme:light;--bg:#fff;--panel:#f7f8fa;--line:#e3e6ea;--ink:#14181d;--mut:#5f6874;--dim:#8a929d;
--blue:#1f5fd6;--blueBg:#eaf1fd;--green:#1a7f4b;--greenBg:#e7f5ed;--red:#b3261e;--redBg:#fdecea}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:20px 16px 64px}}h1{{font-size:20px;margin:0 0 4px}}
.sub{{color:var(--mut);font-size:13px;margin:0 0 20px}}header{{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:20px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:12px}}
.row{{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}}
.name{{font-size:15px;font-weight:650;margin:0 0 4px}}.name a{{color:var(--ink);text-decoration:none}}.name a:hover{{text-decoration:underline}}
.meta{{color:var(--mut);font-size:12.5px}}.err{{color:var(--red)}}.badges{{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}}
.badge{{padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600}}.b-blue{{background:var(--blueBg);color:var(--blue)}}.b-grey{{background:#eef0f3;color:var(--mut)}}
.statusline{{display:flex;align-items:center;gap:6px;white-space:nowrap}}.pill{{padding:3px 10px;border-radius:20px;font-size:11.5px;font-weight:650}}
.pill-ok{{background:var(--greenBg);color:var(--green)}}.pill-error{{background:var(--redBg);color:var(--red)}}.pill-pending{{background:#eef0f3;color:var(--mut)}}
.synced{{font-size:11.5px;color:var(--dim)}}.foot{{border-top:1px solid var(--line);padding-top:12px;margin-top:8px;color:var(--dim);font-size:11.5px}}
</style></head><body><div class="wrap">
<header><h1>Live Dashboard Registry</h1><p class="sub">Projects with an auto-refreshed dashboard, and what each one pulls from.</p></header>
{cards or '<div class="meta">No projects registered yet.</div>'}
<div class="foot">Static page rendered {html.escape(now.strftime('%Y-%m-%d %H:%M UTC'))} from registry.json by render_registry.py. "synced" ages are as of render time.</div>
</div></body></html>
"""
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html written ({len(projects)} projects)")


if __name__ == "__main__":
    main()
