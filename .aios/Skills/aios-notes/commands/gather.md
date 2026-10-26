---
description: Pull context from connected sources (documents / email / calendar / chat / records — SharePoint, Coda, Outlook, Gmail, Teams, tickets) into a note
---

Use the **gather** skill. Input: $ARGUMENTS

Resolve sources **capability-first** — DOCS / EMAIL / CALENDAR / CHAT / RECORDS — using whatever
tools this session actually has, never a fixed tool set. If a gateway is present
(`COMPOSIO_SEARCH_TOOLS` / `COMPOSIO_MULTI_EXECUTE_TOOL`), it fronts every authorized toolkit:
discover with a plain-language `use_case`, confirm `has_active_connection`, pin the account alias,
execute reads via `COMPOSIO_MULTI_EXECUTE_TOOL` (array parameter is `tools`), and carry the
`session_id`. Never hardcode which toolkits exist.

If the user named a source + topic, search it directly; otherwise offer the available sources and
ask which to check. Search narrowly, read only what matters, summarize + cite. Then show what you'll
add, where, and why — and write on approval (link documents, including Coda pages, under Canonical
Sources; distill email/chat into the body; link records; add calendar context), applying
write-through to any living surfaces the findings supersede. Never blanket-search, and never fan out
across a gateway's whole roster.

**Read-only.** If the request needs something created, updated, sent, or deleted in an external
system, stop and hand off to the `act` intent.
